import json
from collections.abc import Iterable
from typing import List

from llmos_core.Prompts.Windows import BasePromptWindow,FlowStackPromptWindow
from llmos_core.Prompts.Windows.BaseWindow import NullSystemWindow

import json
import re

ALLOWEDKEYS = ["call_type", "func_name", "kwargs", 'reasoning']
NEEDKEYS = ["call_type", "func_name"]

import datetime
from typing import Any, Dict



def parse_response(response_text: str):
    """
    尝试从任意包含 JSON 的字符串中提取并解析第一个合法的 JSON 结构。

    1. 移除 Markdown 代码块标记（如 ```json...```）。
    2. 遍历字符串，使用括号计数法找到最有可能的 JSON 结构的结束位置。
    3. 解析提取的 JSON，并应用原始的结构验证（NEEDKEYS, ALLOWEDKEYS）。

    返回：list[dict] 格式，每个 dict 包含 call_type、func_name、kwargs。
    """
    cleaned_text = response_text.strip()

    # 1. 尝试移除 Markdown 代码块标记，使查找起始字符更容易
    match_md = re.search(r"```json\s*([\s\S]*?)\s*```", cleaned_text)
    if match_md:
        cleaned_text = match_md.group(1).strip()

    # 2. 找到第一个 JSON 结构的起始位置
    start_index = -1
    for char in ['{', '[']:
        idx = cleaned_text.find(char)
        if idx != -1 and (start_index == -1 or idx < start_index):
            start_index = idx

    if start_index == -1:
        raise ValueError("输入字符串中未找到 JSON 起始字符 '{' 或 '['。")

    # 3. 使用栈/计数法找到 JSON 结构的结束位置

    # 存储找到的 JSON 片段
    json_candidates = []

    for start_char in ['{', '[']:
        try:
            # 找到所有可能的起始位置
            for match in re.finditer(re.escape(start_char), cleaned_text):
                start_pos = match.start()
                if start_pos < start_index:  # 只从第一个找到的起始符开始
                    continue

                open_char = start_char
                close_char = '}' if start_char == '{' else ']'
                balance = 0

                # 从起始字符开始遍历，找到平衡的结束字符
                for i in range(start_pos, len(cleaned_text)):
                    char = cleaned_text[i]
                    if char == open_char:
                        balance += 1
                    elif char == close_char:
                        balance -= 1

                    if balance == 0:
                        # 找到平衡点，提取并尝试解析这个片段
                        json_str = cleaned_text[start_pos: i + 1]

                        # 尝试解析
                        try:
                            parsed_data = json.loads(json_str)
                            # 如果解析成功，存储它
                            json_candidates.append(parsed_data)
                            # 找到第一个合法的 JSON 就立即退出外层循环
                            raise StopIteration  # 使用异常跳出多层循环
                        except json.JSONDecodeError:
                            # 可能是非法的 JSON，或 JSON 内部有未转义的引号等，继续查找
                            pass
        except StopIteration:
            break  # 成功找到并解析，跳出循环

    if not json_candidates:
        raise ValueError(f"字符串中未找到合法的 JSON 结构。尝试从位置 {start_index} 开始。")

    # 优先使用第一个成功解析的候选
    data = json_candidates[0]

    # --- 4. 应用原有的结构验证逻辑 ---

    # 标准化为列表
    if isinstance(data, dict):
        data = [data]
    elif not isinstance(data, list):
        raise TypeError(f"顶层结构必须是对象或数组，收到：{type(data)}")

    calls = []
    for idx, item in enumerate(data):
        if not isinstance(item, dict):
            raise ValueError(f"第 {idx} 个调用不是对象类型")

        illegal = set(item) - set(ALLOWEDKEYS)
        if illegal:
            raise ValueError(f"非法字段: {', '.join(illegal)}")

        missing = [k for k in NEEDKEYS if k not in item]
        if missing:
            raise ValueError(f"缺少必要字段: {', '.join(missing)}")

        kwargs = item.get("kwargs", {})
        if not isinstance(kwargs, dict):
            raise ValueError("kwargs 必须为字典类型")

        call = {
            "call_type": item["call_type"],
            "func_name": item["func_name"],
            "kwargs": kwargs
        }
        if reasoning := item.get("reasoning"):
            call["reasoning"] = reasoning

        calls.append(call)

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

    def handle_call(self, call, auto_record=True):
        """统一分发到对应窗口的 handler"""
        func_name = call["func_name"]
        call_type = call["call_type"]
        kwargs = call["kwargs"]
        reasoning = call.get("reasoning", '')
        if func_name in self.handlers:
            result = self.handlers[func_name](**kwargs)
            if auto_record:
                self.record_execution(call_type, func_name=func_name, result=result, reasoning=reasoning, **kwargs)
            return result
        else:
            return {"status": "error", "reason": f"handler not found: {func_name}"}

    def record_execution(self, event_type,**kwargs):
        """
        记录一次正常调用
        :param event_type:
        :param kwargs:
        :return:
        """
        for window in self.windows:
            if isinstance(window, FlowStackPromptWindow):
                window.record_event(event_type=event_type, **kwargs)

    def get_divided_snapshot(self):
        divided_snap_shot = {}
        divided_snap_shot.update(self.system_window.get_divided_snapshot())
        for window in self.windows:
            divided_snap_shot.update(window.get_divided_snapshot())
        return divided_snap_shot


