import json
import re
from collections.abc import Iterable
from typing import List

from llmos_core.Prompts.Windows import BasePromptWindow
from llmos_core.Prompts.Windows.BaseWindow import NullSystemWindow


def parse_response(response_text: str):
    """
    解析大模型返回的 JSON-only 调用结果。
    支持单个调用或数组。
    返回：list[dict] 格式，每个 dict 包含 call_type、func_name、kwargs。
    """
    response_text = response_text.strip()

    # 尝试提取纯 JSON（防御模型输出中混入前后空白或格式符）
    try:
        data = json.loads(response_text)
    except json.JSONDecodeError as e:
        raise ValueError(f"模型输出不是合法 JSON：{e}\n输出内容:\n{response_text[:500]}")

    # 标准化为列表
    if isinstance(data, dict):
        data = [data]
    elif not isinstance(data, list):
        raise TypeError(f"顶层结构必须是对象或数组，收到：{type(data)}")

    calls = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"第 {idx} 个调用不是对象类型")
        for key in item.keys():
            if key not in ("call_type", "func_name", "kwargs"):
                raise ValueError(f"非法字段: {key}")
        if "call_type" not in item or "func_name" not in item:
            raise ValueError(f"缺少必要字段: call_type 或 func_name")
        if item["call_type"] != "prompt":
            raise ValueError(f"不支持的 call_type: {item['call_type']}")
        kwargs = item.get("kwargs", {})
        if not isinstance(kwargs, dict):
            raise ValueError("kwargs 必须为字典类型")
        calls.append({
            "call_type": item["call_type"],
            "func_name": item["func_name"],
            "kwargs": kwargs
        })
    return calls


class PromptMainBoard:
    def __init__(self):

        self.windows:List[BasePromptWindow] = []
        self.system_window:BasePromptWindow | None = None
        self.handlers = {}

    def assemble_prompt(self):
        """
        拼接所有模块的 forward() 输出
        """
        ret_message = {
            "system": self.system_window.forward(),
            "user":"\n".join(m.forward() for m in self.windows)
        }
        return ret_message

    def register_windows(self, windows: List[BasePromptWindow] | BasePromptWindow=NullSystemWindow(),system_window:BasePromptWindow=NullSystemWindow()):
        """注册模块"""
        """
                注册模块。可以接受单个模块实例，也可以接受模块实例列表。
                """
        if windows:
            # 1. 检查是否为可迭代对象（列表、元组等）
            if isinstance(windows, Iterable):
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

            if system_window:
                self.register_system_window(system_window)

    def register_system_window(self, system_window):
        self.system_window = system_window
        self.handlers.update(system_window.export_handlers() or {})

    def handle_call(self, func_name: str, **kwargs):
        """统一分发到对应窗口的 handler"""
        if func_name in self.handlers:
            return self.handlers[func_name](**kwargs)
        else:
            return {"status": "error", "reason": f"handler not found: {func_name}"}

    def get_divided_snapshot(self):
        divided_snap_shot = {}
        divided_snap_shot.update(self.system_window.get_divided_snapshot())
        for window in self.windows:
            divided_snap_shot.update(window.get_divided_snapshot())
        return divided_snap_shot


