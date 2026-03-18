import json
from llmos_core.Prompts.Windows.BaseWindow import BasePromptWindow
from llmos_core.schema import ToolDefinition
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

META_DIR = Path(__file__).parent
META_FILE = META_DIR / 'stack_description.json'


@dataclass
class StackFrame:
    name: str
    description: str
    variables: Dict[str, Any] = field(default_factory=dict)
    fail_reason: Optional[str] = None

class StackPromptWindow(BasePromptWindow):

    def __init__(self, window_title='Stack'):
        super().__init__(window_title=window_title)
        self.file_path = META_FILE
        with open(self.file_path, 'r') as f:
            self.meta_data = json.load(f)
        self.stack: List[StackFrame] = []

    def export_meta_prompt(self):
        """栈描述部分"""
        return json.dumps(self.meta_data, indent=2, ensure_ascii=False)

    def export_state_prompt(self):
        """栈帧数据部分"""
        if not self.stack:
            return "### STACK EMPTY ###\n"

        def export_frame(frame: StackFrame):
            """单帧 → 文本"""
            desc_lines = [f"Function {frame.name}: {frame.description}"]
            if frame.variables:
                desc_lines.append(f"Variables: {frame.variables}")
            if frame.fail_reason:
                desc_lines.append(f"[Previous failure: {frame.fail_reason}]")
            return "\n".join(desc_lines)

        parts = [export_frame(frame) for frame in self.stack]
        return "### STACK DATA ###\n" + "\n".join(parts)

    def forward(self, context=None):
        """组合完整提示词"""
        return super().forward()

    def _stack_push(self, *args, **kwargs):
        frame = StackFrame(
            name=kwargs.get("name", f"func_{len(self.stack)}"),
            description=kwargs.get("description", ""),
            variables=kwargs.get("variables", {}),
            fail_reason=None,
        )
        self.stack.append(frame)
        return {"status": "ok", "stack_size": len(self.stack)}

    def _stack_pop(self, *args, **kwargs):
        if not self.stack:
            return {"status": "error", "reason": "stack empty"}
        frame = self.stack.pop()
        result = kwargs.get("result", None)
        return {
            "status": "ok",
            "popped": frame.name,
            "result": result,
            "stack_size": len(self.stack),
        }

    def _stack_setvar(self, *args, **kwargs):
        new_vars = kwargs.get("variables", {})
        if not isinstance(new_vars, dict) or not new_vars:
            return {"status": "error", "reason": "variables argument must be a non-empty dictionary"}
        if not self.stack:
            return {"status": "error", "reason": "no active frame to update variables in"}
        
        frame = self.stack[-1]
        frame.variables.update(new_vars)
        return {"status": "ok", "updated_keys": list(new_vars.keys()), "stack_size": len(self.stack)}

    def _stack_replace(self, *args, **kwargs):
        if not self.stack:
            return {"status": "error", "reason": "stack empty"}
        fail_reason = kwargs.get("fail_reason", "unknown failure")
        desc = kwargs.get("description", "")
        variables = kwargs.get("variables", {})
        
        frame = self.stack[-1]
        frame.description = desc
        frame.variables = variables
        frame.fail_reason = fail_reason
        return {"status": "ok", "replaced": frame.name}

    def export_handlers(self):
        return {
            "stack_push": self._stack_push,
            "stack_pop": self._stack_pop,
            "stack_setvar": self._stack_setvar,
            "stack_replace": self._stack_replace,
        }
