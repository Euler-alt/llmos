import json
import re

def parse_response(response:str):
    """
    :param response:
    :return:
    """

    try:
        parsed = json.loads(response)
        if isinstance(parsed,dict) and "call_type" in parsed:
            return [parsed]
        elif isinstance(parsed,list) and "call_type" in parsed:
            return parsed

    except json.JSONDecodeError:
        pass

    matches = re.finditer(r"\[(\w+):(\w+)\((.*?)\)\]", response)
    calls = []
    for match in matches:
        call_type, func_name, args = match.groups()
        kwargs = {kv.split("=")[0]: kv.split("=")[1]
                  for kv in args.split(",") if "=" in kv}
        calls.append({
            "call_type": call_type,
            "func_name": func_name,
            "kwargs": kwargs
        })
    return calls



class PromptMainBoard:
    def __init__(self):

        self.windows = []
        self.handlers = {}

    def assemble_prompt(self):
        """
        拼接所有模块的 forward() 输出
        """
        return "\n".join(m.forward() for m in self.windows)

    def register_module(self, module):
        """注册模块"""
        self.windows.append(module)
        self.handlers.update(module.export_handlers() or {})


    def handle_call(self, func_name: str, **kwargs):
        """统一分发到对应窗口的 handler"""
        if func_name in self.handlers:
            return self.handlers[func_name](**kwargs)
        else:
            return {"status": "error", "reason": f"handler not found: {func_name}"}

    def show_state(self):
        """
        打印或返回提示词的当前状态
        """
        return self.assemble_prompt()

    def get_divide_snapshot(self):
        divided_snap_shot = {}
        for window in self.windows:
            divided_snap_shot.update(window.get_divide_snapshot())
        return divided_snap_shot

    def get_snapshot(self):
        snapshot = {}
        for window in self.windows:
            snapshot.update(window.get_snapshot())
        return snapshot

