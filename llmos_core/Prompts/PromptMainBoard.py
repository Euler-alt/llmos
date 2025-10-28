import json
import re
from collections.abc import Iterable

def parse_response(response: str):
    """
    :param response:
    :return:
    """

    try:
        parsed = json.loads(response)
        if isinstance(parsed, dict) and "call_type" in parsed:
            return [parsed]
        elif isinstance(parsed, list) and "call_type" in parsed:
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

    def register_windows(self, windows):
        """注册模块"""
        """
                注册模块。可以接受单个模块实例，也可以接受模块实例列表。
                """
        # 确定要处理的模块列表
        modules_to_register = []

        # 1. 检查是否为可迭代对象（列表、元组等），但排除字符串
        if isinstance(windows, Iterable) and not isinstance(windows, str):
            modules_to_register = windows
        else:
            # 2. 否则，视为单个模块实例
            modules_to_register = [windows]

        # 遍历所有需要注册的模块
        for module in modules_to_register:
            # 简化类型检查：可以添加更严格的检查，确保是 BasePromptWindow 的子类
            # if not isinstance(module, BasePromptWindow):
            #     raise TypeError("Registered item must be a Prompt Window module.")

            self.windows.append(module)

            # 尝试更新 handlers
            # 假设每个 module 都有 export_handlers 方法
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

    def get_divided_snapshot(self):
        divided_snap_shot = {}
        for window in self.windows:
            divided_snap_shot.update(window.get_divide_snapshot())
        return divided_snap_shot


