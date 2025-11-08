from llmos_core.Prompts.Windows.BaseWindow.BaseWindow import BasePromptWindow
from pathlib import Path
from typing import List, Dict, Any

META_DIR = Path(__file__).parent
META_FILE = META_DIR / 'flowStack_description.json'


@BasePromptWindow.register('flowStack', 'stack')
class FlowStackPromptWindow(BasePromptWindow):

    def __init__(self, window_name='FlowStackWindow'):
        super().__init__(window_name=window_name)
        self.file_path = META_FILE
        with open(self.file_path, 'r') as f:
            self.description = f.read()
        self.stack: List[Dict[str, Any]] = []

    def _ret_frame(self, ret_key, ret_value):
        """
        将子任务的返回值 ret_value 写入新的栈顶帧（父帧）的 ret_key 变量中。
        """
        if len(self.stack) >= 1:  # 子帧已经 pop，现在栈顶是父帧
            parent_frame = self.stack[-1]
            if ret_key and ret_value is not None:
                parent_frame['variables'][ret_key] = ret_value

    def export_state_prompt(self):
        """栈帧数据部分 - 重点显示执行历史"""
        if not self.stack:
            return "### STACK EMPTY ###\n"

        def export_frame(frame, index=None):
            """单帧 → 文本，包含执行历史"""
            lines = []

            # 基本信息
            lines.append(f"Function {frame['name']}: {frame['description']}")

            if frame.get("variables"):
                lines.append(f"Variables: {frame['variables']}")

            if frame.get("next_instruction"):
                lines.append(f"-> INSTRUCTION: {frame['next_instruction']}")

            # 【关键】显示执行历史
            history = frame.get("action_history", [])
            if history:
                lines.append("\n[Execution History - 你是如何走到这一步的]")
                # 只显示最近3步
                recent = history[-3:]
                for h in recent:
                    lines.append(f"  Step #{h['step']}: {h['instruction']} → {h['result']}")
                    lines.append(f"           Reasoning: {h['reasoning']}")
                lines.append("  (当前 INSTRUCTION 是基于以上历史做出的下一步决策)")

            # 显示失败路径摘要
            if history:
                failed_instructions = set()
                for h in history:
                    if h['result'] and 'fail' in h['result'].lower() or 'locked' in h['result'].lower():
                        failed_instructions.add(h['instruction'])

                if failed_instructions:
                    lines.append("\n[Tried and Failed - 已知无效的路径]")
                    for instr in failed_instructions:
                        # 找到最近的失败记录
                        fail_record = next((h for h in reversed(history) if h['instruction'] == instr), None)
                        if fail_record:
                            lines.append(f"  - {instr}: {fail_record['result']} (步骤 #{fail_record['step']})")

            # 显示回溯原因（如果有）
            if frame.get("fail_reason"):
                lines.append(f"\n[Previous failure reason: {frame['fail_reason']}]")

            return "\n".join(lines)

        parts = [export_frame(frame, i) for i, frame in enumerate(self.stack)]
        return "### STACK DATA ###\n" + "\n".join(parts)

    def export_meta_prompt(self):
        """栈描述部分"""
        return f"{self.description}\n"

    def forward(self, context=None):
        """组合完整提示词"""
        return f"\n{self.export_meta_prompt()}{self.export_state_prompt()}"

    def _stack_push(self, *args, **kwargs):
        """启动新的子任务，初始化执行历史"""
        # 强制检查必需参数
        name = kwargs.get("name")
        description = kwargs.get("description")
        next_instruction = kwargs.get("next_instruction")

        if not description:
            return {"status": "error", "reason": "stack_push requires 'description'"}

        if not next_instruction:
            return {"status": "error", "reason": "stack_push requires 'next_instruction'"}

        frame = {
            "name": name or f"task_{len(self.stack)}",
            "description": description,
            "variables": kwargs.get("variables", {}),
            "next_instruction": next_instruction,
            "ret_key": kwargs.get("ret_key"),
            "fail_reason": None,

            # 【新增】执行历史追踪
            "action_history": [],  # 存储历史动作
            "step_counter": 0,  # 当前步骤计数
        }

        self.stack.append(frame)

        return {
            "status": "ok",
            "stack_size": len(self.stack),
            "step": 1  # 新任务从步骤1开始
        }

    def _stack_pop(self, *args, **kwargs):
        """结束当前任务并返回结果"""
        if not self.stack:
            return {"status": "error", "reason": "stack empty"}

        frame = self.stack.pop()

        # 将结果写回父帧
        result = kwargs.get("result")
        ret_key = kwargs.get("ret_key") or frame.get("ret_key")
        self._ret_frame(ret_key, result)

        return {
            "status": "ok",
            "stack_size": len(self.stack),
            "message": f"Task '{frame['name']}' completed with {frame['step_counter']} steps"
        }

    def _stack_setvar(self, *args, **kwargs):
        """更新栈顶帧的变量"""
        new_vars = kwargs.get("variables", {})

        if not isinstance(new_vars, dict) or not new_vars:
            return {"status": "error", "reason": "variables argument must be a non-empty dictionary"}

        if not self.stack:
            return {"status": "error", "reason": "no active frame to update variables in"}

        frame = self.stack[-1]
        updated_keys = []

        # 原子性更新
        current_vars = frame.get("variables", {})
        for key, value in new_vars.items():
            current_vars[key] = value
            updated_keys.append(key)

        frame["variables"] = current_vars

        return {
            "status": "ok",
            "updated_keys": updated_keys,
            "stack_size": len(self.stack)
        }

    def _stack_replace(self, *args, **kwargs):
        """回溯修正：重写当前栈帧并清空历史"""
        if not self.stack:
            return {"status": "error", "reason": "stack empty"}

        fail_reason = kwargs.get("fail_reason")
        if not fail_reason:
            return {"status": "error", "reason": "fail_reason is required for stack_replace"}

        frame = self.stack[-1]

        # 更新字段
        if "description" in kwargs:
            frame["description"] = kwargs["description"]
        if "variables" in kwargs:
            frame["variables"] = kwargs["variables"]
        if "next_instruction" in kwargs:
            frame["next_instruction"] = kwargs["next_instruction"]

        frame["fail_reason"] = fail_reason

        # 【关键】清空执行历史，相当于重新开始
        frame["action_history"] = []
        frame["step_counter"] = 0

        return {
            "status": "ok",
            "replaced": frame["name"],
            "fail_reason": fail_reason,
            "history_cleared": True
        }

    def _is_loop_detected(self, frame, new_instruction):
        """
        检测是否在重复最近的指令
        返回: (is_loop, error_message)
        """
        history = frame.get("action_history", [])

        # 检查最近5步
        recent_instructions = [h['instruction'] for h in history[-5:]]

        if new_instruction in recent_instructions:
            # 找到之前的执行记录
            prev_record = next(
                (h for h in reversed(history) if h['instruction'] == new_instruction),
                None
            )

            if prev_record:
                error_msg = (
                    f"检测到循环: 指令 '{new_instruction}' 在步骤 #{prev_record['step']} "
                    f"已尝试过，结果为 '{prev_record['result']}'。"
                    f"你必须尝试不同的方法，或使用 stack_replace/stack_pop 改变策略。"
                )
                return True, error_msg

        return False, None

    def _stack_set_instruction(self, *args, **kwargs):
        """
        更新栈顶帧的下一条执行指令，并自动记录历史
        """
        new_instruction = kwargs.get("instruction")
        reason = kwargs.get("reason")
        last_result = kwargs.get("last_result")

        # 参数校验
        if not new_instruction or not isinstance(new_instruction, str):
            return {"status": "error", "reason": "instruction argument must be a non-empty string"}

        if not reason:
            return {
                "status": "error",
                "reason": "reason is required: 你必须解释为什么要执行这个指令，以及它与上一步有何不同"
            }

        if not last_result:
            return {
                "status": "error",
                "reason": "last_result is required: 你必须说明上一步的执行结果是什么"
            }

        if not self.stack:
            return {"status": "error", "reason": "no active frame to update instruction in"}

        frame = self.stack[-1]

        # 【关键】循环检测
        is_loop, error_msg = self._is_loop_detected(frame, new_instruction)
        if is_loop:
            return {"status": "error", "reason": error_msg}

        # 【关键】保存当前指令到历史
        current_instruction = frame.get("next_instruction")
        if current_instruction:  # 如果有旧指令（不是第一步）
            frame["step_counter"] += 1

            history_entry = {
                "step": frame["step_counter"],
                "instruction": current_instruction,
                "result": last_result,
                "reasoning": reason
            }

            if "action_history" not in frame:
                frame["action_history"] = []

            frame["action_history"].append(history_entry)

            # 【优化】只保留最近10步的完整历史（用于循环检测）
            # 但显示时只显示最近3步（在 export_state_prompt 中控制）
            if len(frame["action_history"]) > 10:
                frame["action_history"].pop(0)

        # 更新新指令
        frame["next_instruction"] = new_instruction

        return {
            "status": "ok",
            "new_instruction": new_instruction,
            "step": frame["step_counter"] + 1,  # 下一步的步骤号
            "stack_size": len(self.stack)
        }

    def export_handlers(self):
        return {
            'stack_push': self._stack_push,
            'stack_pop': self._stack_pop,
            'stack_set_instruction': self._stack_set_instruction,
            'stack_setvar': self._stack_setvar,
            'stack_replace': self._stack_replace,
        }