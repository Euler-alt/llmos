from .BaseWindow import BasePromptWindow
from pathlib import Path
from typing import List,Dict,Any

@BasePromptWindow.register('stack','Stack')
class StackPromptWindow(BasePromptWindow):

    def __init__(self, window_name='Stack'):
        super().__init__(window_name=window_name)
        self.file_path = Path(__file__).parent / 'texts' / 'stack_description.json'
        with open(self.file_path,'r') as f:
            self.description = f.read()
        self.stack:List[Dict[str, Any]] = []


    def export_state_prompt(self):
        """栈帧数据部分"""

        if not self.stack:
            return "### STACK EMPTY ###\n"

        def export_frame(frame, index=None):
            """单帧 → 文本"""
            desc_lines = [f"Function {frame['name']}: {frame['description']}"]
            if frame.get("variables"):
                desc_lines.append(f"Variables: {frame['variables']}")
            if frame.get("fail_reason"):
                desc_lines.append(f"[Previous failure: {frame['fail_reason']}]")
            if frame.get("content"):
                desc_lines.append(frame['content'])
            return "\n".join(desc_lines)

        parts = [export_frame(frame, i) for i, frame in enumerate(self.stack)]
        return "### STACK DATA ###\n" + "\n".join(parts)

    def export_meta_prompt(self):
        """栈描述部分"""
        return f"{self.description}\n"

    def forward(self, context=None):
        """组合完整提示词"""
        return f"\n{self.export_meta_prompt()}{self.export_state_prompt()}"

    def _stack_push(self,*args,**kwargs):
        frame = {
            "name": kwargs.get("name", f"func_{len(self.stack)}"),
            "description": kwargs.get("description", ""),
            "variables": kwargs.get("variables", {}),
            "fail_reason": None,
            "content": None,
        }
        self.stack.append(frame)
        return {"status": "ok", "stack_size": len(self.stack)}

    def _stack_pop(self,*args,**kwargs):
        if not self.stack:
            return {"status": "error", "reason": "stack empty"}
        frame = self.stack.pop()
        result = kwargs.get("result", None)
        return {
            "status": "ok",
            "popped": frame["name"],
            "result": result,
            "stack_size": len(self.stack),
        }

    def _stack_append(self,*args,**kwargs):
        content = kwargs.get("content", None)
        frame = self.stack[-1]
        if frame["content"] is None:
            frame["content"] = content
        else:
            frame["content"] += content
        return {"status": "ok", "new_content": "new_content"}

    def _stack_replace(self,*args,**kwargs):
        if not self.stack:
            return {"status": "error", "reason": "stack empty"}
        fail_reason = kwargs.get("fail_reason", "unknown failure")
        desc = kwargs.get("description", "")
        variables = kwargs.get("variables", {})
        # 重置当前栈帧
        frame = self.stack[-1]
        frame["description"] = desc
        frame["variables"] = variables
        frame["fail_reason"] = fail_reason
        return {
            "status": "ok",
            "replaced": frame["name"],
            "fail_reason": fail_reason,
        }

    def export_handlers(self):
        return {
        'stack_push': self._stack_push,
        'stack_pop': self._stack_pop,
        'stack_append': self._stack_append,
        'stack_replace': self._stack_replace,}