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
        self._init_root_frame()

    def _init_root_frame(self):
        root_frame = {
            "name": "ROOT",
            "description": "主任务根帧（永不弹出）",
            "variables": {},
            "instruction": None,
            "ret_key": None,
            "fail_reason": None,
            "action_history": [],
            "step_counter": 0,
            "is_root": True
        }
        self.stack.append(root_frame)

    def _stack_pop(self, *args, **kwargs):
        if not self.stack:
            return {"status": "error", "reason": "stack empty"}

        if len(self.stack) == 1:  # ✅ 根帧禁止弹出
            return {
                "status": "warning",
                "reason": "cannot pop root frame",
                "stack_size": 1
            }

        frame = self.stack.pop()
        result = kwargs.get("result")
        ret_key = kwargs.get("ret_key") or frame.get("ret_key")
        self._ret_frame(ret_key, result)

        return {
            "status": "ok",
            "stack_size": len(self.stack),
            "message": f"Task '{frame['name']}' completed with {frame['step_counter']} steps"
        }


    def _ret_frame(self, ret_key, ret_value):
        """
        将子任务的返回值 ret_value 写入新的栈顶帧（父帧）的 ret_key 变量中。
        """
        if len(self.stack) >= 1:
            parent_frame = self.stack[-1]
            if ret_key and ret_value is not None:
                parent_frame['variables'][ret_key] = ret_value

    # ========== 【新增】自动记录接口 ==========
    def auto_record_action(self, instruction,call_type,func_name, result, reasoning=None, source="external",**kwargs):
        """
        供外部系统（Dispatcher/其他窗口）调用，自动记录动作到栈历史

        Args:
            instruction: 执行的动作指令（如 "go to bed 1"）
            result: 执行结果（如 "You are now at bed 1..."）
            reasoning: 可选的推理说明（如 "寻找 desklamp"）
            source: 来源标识（如 "ALF_step", "env_step"）
            call_type:
            func_name:

        Returns:
            dict: {"status": "ok/warning", "step": N} 或错误信息
        """
        if not self.stack:
            return {
                "status": "error",
                "reason": "no active frame to record action in"
            }

        frame = self.stack[-1]

        # 更新步骤计数
        frame['step_counter'] += 1

        # 准备推理说明
        if reasoning:
            final_reasoning = reasoning
        else:
            final_reasoning = f"(系统自动记录 from {source})"

        # 添加历史记录
        if 'action_history' not in frame:
            frame['action_history'] = []

        # 截断过长的结果（避免 prompt 爆炸）
        truncated_result = result[:200] if isinstance(result, str) and len(result) > 200 else result

        history_entry = {
            "step": frame['step_counter'],
            "instruction": instruction | 'no_instruction',
            "call_type": call_type,
            "func_name": func_name,
            "result": str(truncated_result),
            "reasoning": final_reasoning,
            "auto_recorded": True,
            "source": source,
            **kwargs  # 自动覆盖同名键
        }

        frame['action_history'].append(history_entry)

        # 保持历史长度限制（存储最近10步,用于循环检测）
        if len(frame['action_history']) > 10:
            frame['action_history'].pop(0)

        return {
            "step": frame['step_counter'],
            "recorded": True
        }

    # ========== 【新增】批量记录接口（可选） ==========
    def record_action_batch(self, actions: List[Dict[str, Any]]):
        """
        批量记录多个动作（用于一次调用执行多步的情况）

        Args:
            actions: [{"instruction": "...", "result": "...", "reasoning": "..."}, ...]

        Returns:
            list of results
        """
        results = []
        for action in actions:
            result = self.auto_record_action(
                instruction=action.get('instruction'),
                result=action.get('result'),
                reasoning=action.get('reasoning'),
                source=action.get('source', 'batch')
            )
            results.append(result)

        return results

    # ========== 原有代码保持不变 ==========

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

            if frame.get("instruction"):
                lines.append(f"-> INSTRUCTION: {frame['instruction']}")

            # 【关键】显示执行历史（注意这里用的是 action_history）
            history = frame.get("action_history", [])
            if history:
                lines.append("\n[Execution History - 在当前栈帧环境下的行动记录]")
                # 只显示最近3步
                recent = history[-3:]
                for h in recent:
                    # 标记自动记录的条目
                    auto_mark = " [自动记录]" if h.get('auto_recorded') else ""
                    lines.append(f"  Step #{h['step']}: {h['instruction']} → {h['result']}{auto_mark}")
                    lines.append(f"           Reasoning: {h['reasoning']}")

                if len(history) > 3:
                    lines.append(f"  (共 {len(history)} 步，仅显示最近 3 步)")
                else:
                    lines.append("  (当前 INSTRUCTION 是基于以上历史做出的下一步决策)")

            # 显示失败路径摘要
            if history:
                failed_instructions = set()
                for h in history:
                    if h.get('result') and ('fail' in str(h['result']).lower() or 'locked' in str(h['result']).lower()):
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
        return super().forward()

    def _stack_push(self, *args, **kwargs):
        """启动新的子任务，初始化执行历史"""
        name = kwargs.get("name")
        description = kwargs.get("description")
        instruction = kwargs.get("instruction")

        if not description:
            return {"status": "error", "reason": "stack_push requires 'description'"}

        if not instruction:
            return {"status": "error", "reason": "stack_push requires 'instruction'"}

        frame = {
            "name": name or f"task_{len(self.stack)}",
            "description": description,
            "variables": kwargs.get("variables", {}),
            "instruction": instruction,
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
            "step": 1
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

        if "description" in kwargs:
            frame["description"] = kwargs["description"]
        if "variables" in kwargs:
            frame["variables"] = kwargs["variables"]
        if "instruction" in kwargs:
            frame["instruction"] = kwargs["instruction"]

        frame["fail_reason"] = fail_reason

        # 【关键】清空执行历史
        frame["action_history"] = []
        frame["step_counter"] = 0

        return {
            "status": "ok",
            "replaced": frame["name"],
            "fail_reason": fail_reason,
            "history_cleared": True
        }

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

        # 保存当前指令到历史
        current_instruction = frame.get("instruction")
        if current_instruction:
            frame["step_counter"] += 1

            history_entry = {
                "step": frame["step_counter"],
                "instruction": current_instruction,
                "result": last_result,
                "reasoning": reason,
                "auto_recorded": False  # 标记为手动记录
            }

            if "action_history" not in frame:
                frame["action_history"] = []

            frame["action_history"].append(history_entry)

            if len(frame["action_history"]) > 10:
                frame["action_history"].pop(0)

        # 更新新指令
        frame["instruction"] = new_instruction

        return {
            "status": "ok",
            "new_instruction": new_instruction,
            "step": frame["step_counter"] + 1,
            "stack_size": len(self.stack)
        }

    def export_handlers(self):
        return {
            'stack_push': self._stack_push,
            'stack_pop': self._stack_pop,
            'stack_set_instruction': self._stack_set_instruction,
            'stack_setvar': self._stack_setvar,
            'stack_replace': self._stack_replace,
            # 【注意】auto_record_action 不暴露给 LLM，只供内部系统调用
        }