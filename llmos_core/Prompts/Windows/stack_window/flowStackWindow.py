from pathlib import Path
from typing import List, Dict, Any

from llmos_core.Prompts.Windows.BaseWindow import BasePromptWindow
from llmos_core.logger import LogEvent, RecordType

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

    def log(self, log_event:LogEvent):
        """记录一次事件"""
        self.records.append(log_event)
        if len(self.records) > self.maxlen:
            self.records.pop(0)
        print(log_event.render())  # 你也可以换成写文件、消息总线等
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

    def set_instruction(self, instruction='',**kwargs):
        self.instruction = instruction

# ========== 【主窗口类：FlowStackPromptWindow】 ==========
@BasePromptWindow.register('flowStack', 'stack')
class FlowStackPromptWindow(BasePromptWindow):

    def __init__(self, window_name='FlowStackWindow'):
        super().__init__(window_name=window_name)
        self.file_path = META_FILE
        with open(self.file_path, 'r') as f:
            self.description = f.read()
        self.stack: List[Frame] = []
        self._init_root_frame()

    def forward(self, *args, **kwargs):
        return super().forward(*args, **kwargs)

    def _init_root_frame(self):
        root = Frame("ROOT", "主任务根帧（永不弹出）")
        self.stack.append(root)

    # === 栈操作 ===
    def _stack_push(self, *args, **kwargs):
        name = kwargs.get("name")
        desc = kwargs.get("description")
        inst = kwargs.get("instruction")
        ret_key = kwargs.get("ret_key")
        if not desc or not inst:
            return {"status": "error", "reason": "stack_push requires 'description' and 'instruction'"}

        frame = Frame(name or f"task_{len(self.stack)}", desc, kwargs.get("variables", {}),inst,ret_key=ret_key)
        #记录到当前帧
        logData = {'func_name':'stack_push','subframename':name or 'not set','mission':desc}
        log_event = LogEvent(RecordType.prompt_call, data=logData)
        self.stack.append(frame)
        return {"status": "ok", "stack_size": len(self.stack)}

    def _stack_pop(self, *args, **kwargs):
        if len(self.stack) <= 1:
            return {"status": "warning", "reason": "cannot pop root frame"}
        popped = self.stack.pop()
        result = kwargs.get("result")
        ret_key = kwargs.get("ret_key")
        if not ret_key:
            ret_key = popped.ret_key or None
        if ret_key and result is not None and self.stack:
            self.stack[-1].variables[ret_key] = result
        else:
            self.stack[-1].variables[f'子帧{popped.name} pop with:'] = None
        return {'subframename':popped.name,'mission':popped.description,"status": "ok", "message": f"Frame '{popped.name}' completed"}

    # === 调用记录接口（代理给 Frame） ===
    def record_event(self, log_event:LogEvent):
        if not self.stack:
            return {"status": "error", "reason": "no active frame"}
        return self.stack[-1].record_event(log_event)

    # === 状态导出 ===
    def export_state_prompt(self):
        return "### STACK DATA ###\n" + "\n".join(f.render_text() for f in self.stack)

    def export_meta_prompt(self):
        return f"{self.description}\n"

    def export_handlers(self):
        return {
            'stack_push': self._stack_push,
            'stack_pop': self._stack_pop,
            'stack_set_instruction': lambda *a, **kw: self.stack[-1].set_instruction(**kw),
            'stack_setvar': lambda *a, **kw: self.stack[-1].set_variables(instuction=kw.get("variables", {})),
        }
