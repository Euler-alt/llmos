from .BaseModules import BasePromptModule
from pathlib import Path
from typing import List,Dict,Any


class StackPromptModule(BasePromptModule):

    def __init__(self,name='stack'):
        super().__init__()
        self.name = name
        self.file_path = Path(__file__).parent / 'texts' / 'stack_description.txt'
        with open(self.file_path,'r') as f:
            self.description = f.read()
        self.stack:List[Dict[str, Any]] = []

    def forward(self, context=None):
        """将栈帧序列化成提示词字符串，供 LLM 使用"""
        parts = []

        for i, frame in enumerate(self.stack):
            desc_lines = [f"Function {frame['name']}: {frame['description']}"]
            if frame.get("variables"):
                desc_lines.append(f"Variables: {frame['variables']}")
            if frame.get("fail_reason"):
                desc_lines.append(f"[Previous failure: {frame['fail_reason']}]")
            if frame.get("content"):
                desc_lines.append(frame['content'])
            # 每帧使用统一分隔符拼接
            frame_str = "\n".join(desc_lines)
            parts.append(frame_str)

        # 如果栈为空，返回描述 + 提示
        if not parts:
            return f"\n{self.description}\n### STACK EMPTY ###\n"

        # 栈非空时，把每帧用分隔符拼接
        return f"\n{self.description}\n".join(parts)

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