import json
from pathlib import Path
from typing import List, Dict, Any

from llmos_core.Prompts.Windows.BaseWindow import BasePromptWindow
from llmos_core.logger import LogEvent, RecordType
from llmos_core.schema import ToolDefinition

META_DIR = Path(__file__).parent
META_FILE = META_DIR / 'flowStack_description.json'


# =========================================================
# 🧱 FrameLogger：封装执行历史记录
# =========================================================
class FrameLogger:
    def __init__(self, name: str = None, maxlen: int = 20):
        self.frameName = name or "UnnamedFrame"
        self.records: List[LogEvent] = []
        self.maxlen = maxlen

    def log(self, log_event: LogEvent):
        """记录一次事件"""
        self.records.append(log_event)
        if len(self.records) > self.maxlen:
            self.records.pop(0)
        # print(log_event.render())  # 你也可以换成写文件、消息总线等
        return log_event

    def render_recent(self, n=3):
        """渲染最近几条记录"""
        return "\n".join(e.render() for e in self.records[-n:])

    def __len__(self):
        return len(self.records)

    def clear(self):
        self.records.clear()


# =========================================================
# 🧩 Frame：栈帧对象（包含自己的 StackLogger）
# =========================================================
class Frame:
    def __init__(self, name: str, description: str, variables: Dict[str, Any] = None, instruction: str = None, ret_key=None):
        self.name = name
        self.description = description
        self.variables = variables or {}
        self.instruction = instruction
        self.ret_key = ret_key
        self.fail_reason = None
        self.step_counter = 0

        # ✅ 每个帧都自带日志记录器
        self.logger = FrameLogger(name=self.name)

    def record_event(self, log_event: LogEvent):
        """在当前帧内记录事件"""
        self.step_counter += 1
        log_event.append_data({"step": self.step_counter})
        return self.logger.log(log_event)

    def render_text(self):
        """渲染当前帧的简短状态描述"""
        lines = [f"Function {self.name}: {self.description}"]
        if self.variables:
            lines.append(f"Variables: {self.variables}")
        if self.instruction:
            lines.append(f"-> INSTRUCTION: {self.instruction}")
        if len(self.logger):
            lines.append("[Execution History]")
            lines.append(self.logger.render_recent(3))
        if self.fail_reason:
            lines.append(f"[Fail reason: {self.fail_reason}]")
        return "\n".join(lines)

    def set_variables(self, **kwargs):
        self.variables.update(kwargs)

    def set_instruction(self, instruction='', **kwargs):
        self.instruction = instruction

# ========== 【主窗口类：FlowStackPromptWindow】 ==========
from .stack_window import StackPromptWindow

class FlowStackPromptWindow(StackPromptWindow):

    def __init__(self, window_title='FlowStackWindow'):
        super().__init__(window_title=window_title)
        self.file_path = META_FILE
        with open(self.file_path, 'r') as f:
            self.meta_data = json.load(f)
        self.stack: List[Frame] = []
        self._init_root_frame()

    def export_state_prompt(self):
        """覆盖基类的状态输出，使用 Frame 的 render_text"""
        if not self.stack:
            return "### STACK EMPTY ###\n"

        parts = [frame.render_text() for frame in self.stack]
        return "### FLOW STACK DATA ###\n" + "\n".join(parts)

    def record_event(self, log_event: LogEvent):
        """在当前栈帧记录事件"""
        if self.stack:
            self.stack[-1].record_event(log_event)

    def forward(self, *args, **kwargs):
        return super().forward(*args, **kwargs)

    def _init_root_frame(self):
        root = Frame("ROOT", "主任务根帧（永不弹出）")
        self.stack.append(root)

    def _stack_push(self, *args, **kwargs):
        frame = Frame(
            name=kwargs.get("name", f"func_{len(self.stack)}"),
            description=kwargs.get("description", ""),
            variables=kwargs.get("variables", {}),
            instruction=kwargs.get("instruction", ""),
            ret_key=kwargs.get("ret_key", None)
        )
        self.stack.append(frame)
        return {"status": "ok", "stack_size": len(self.stack)}

    def _stack_pop(self, *args, **kwargs):
        if len(self.stack) <= 1:
            return {"status": "error", "reason": "cannot pop root frame"}
        frame = self.stack.pop()
        result = kwargs.get("result", None)
        # 如果有 ret_key，尝试把结果写回前一帧的 variables
        if frame.ret_key and self.stack:
            self.stack[-1].variables[frame.ret_key] = result
        return {
            "status": "ok",
            "popped": frame.name,
            "result": result,
            "stack_size": len(self.stack),
        }

    def _stack_setvar(self, *args, **kwargs):
        new_vars = kwargs.get("variables", {})
        if not self.stack:
            return {"status": "error", "reason": "stack empty"}
        self.stack[-1].set_variables(**new_vars)
        return {"status": "ok", "updated": list(new_vars.keys())}

    def _stack_setinstruction(self, *args, **kwargs):
        instruction = kwargs.get("instruction", "")
        if not self.stack:
            return {"status": "error", "reason": "stack empty"}
        self.stack[-1].set_instruction(instruction)
        return {"status": "ok", "instruction": instruction}

    def export_handlers(self):
        handlers = super().export_handlers()
        handlers.update({
            "stack_setinstruction": self._stack_setinstruction,
        })
        return handlers
