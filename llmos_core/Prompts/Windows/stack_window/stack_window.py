from llmos_core.Prompts.Windows.BaseWindow.BaseWindow import BasePromptWindow
from pathlib import Path
from typing import List,Dict,Any

META_DIR = Path(__file__).parent
META_FILE = META_DIR / 'stack_description.json'

@BasePromptWindow.register('stack','Stack')
class StackPromptWindow(BasePromptWindow):

    def __init__(self, window_name='Stack'):
        super().__init__(window_name=window_name)
        self.file_path = META_FILE
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
            return "\n".join(desc_lines)

        parts = [export_frame(frame, i) for i, frame in enumerate(self.stack)]
        return "### STACK DATA ###\n" + "\n".join(parts)

    def export_meta_prompt(self):
        """栈描述部分"""
        return f"{self.description}\n"

    def forward(self, context=None):
        """组合完整提示词"""
        return super().forward()

    def _stack_push(self,*args,**kwargs):
        frame = {
            "name": kwargs.get("name", f"func_{len(self.stack)}"),
            "description": kwargs.get("description", ""),
            "variables": kwargs.get("variables", {}),
            "fail_reason": None,
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

    def _stack_setvar(self, *args, **kwargs):
        # 接收一个字典作为变量更新
        new_vars = kwargs.get("variables", {})

        if not isinstance(new_vars, dict) or not new_vars:
            return {"status": "error", "reason": "variables argument must be a non-empty dictionary"}

        if not self.stack:
            return {"status": "error", "reason": "no active frame to update variables in"}

        frame = self.stack[-1]

        updated_keys = []

        # 原子性地更新当前栈帧的 variables 字典
        current_vars = frame.get("variables", {})
        for key, value in new_vars.items():
            current_vars[key] = value  # 覆盖或新增键
            updated_keys.append(key)

        frame["variables"] = current_vars  # 确保更新回 frame

        # 我们应该在返回结果中告知更新了哪些键
        return {"status": "ok", "updated_keys": updated_keys, "stack_size": len(self.stack)}

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
            'stack_setvar': self._stack_setvar,  # <--- 替换 stack_append
            'stack_replace': self._stack_replace,
        }