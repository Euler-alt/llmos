import json
from collections.abc import Iterable
from typing import List

from llmos_core.Prompts.Windows import BasePromptWindow,FlowStackPromptWindow
from llmos_core.Prompts.Windows.BaseWindow import NullSystemWindow
from typing import List, Union
import json
import re

from llmos_core.logger import LogEvent,RecordType
ALLOWEDKEYS = ["call_type", "func_name", "kwargs", 'reasoning']
NEEDKEYS = ["call_type", "func_name"]

from enum import Enum



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
        self.system_window:List[BasePromptWindow] = []
        self.handlers = {}

    def assemble_prompt(self):
        user_prompts = "".join([window.forward() for window in self.windows])
        systemMessage = "".join([window.forward() for window in self.system_window])

        return {
            "system": systemMessage,
            "user": user_prompts  # ← 不加分隔符自然拼接
        }

    def register_windows(
            self,
            windows: Union[List[BasePromptWindow], BasePromptWindow, None] = None,
            system_windows: Union[List[BasePromptWindow], BasePromptWindow, None] = None
    ):
        """注册模块，可接受单个实例或实例列表"""

        def _register(target_list, win):
            target_list.append(win)
            self.handlers.update(win.export_handlers() or {})

        def _ensure_list(obj):
            if obj is None:
                return []
            if isinstance(obj, Iterable) and not isinstance(obj, (str, bytes)):
                return list(obj)
            return [obj]

        for window in _ensure_list(windows):
            _register(self.windows, window)

        for sys_win in _ensure_list(system_windows):
            _register(self.system_window, sys_win)

    def handle_call(self, call, auto_record=True):
        """统一分发到对应窗口的 handler"""
        func_name = call["func_name"]

        # call["call_type"] 是字符串，例如 "tool" 或 "prompt"
        call_type_str = call["call_type"]

        kwargs = call["kwargs"]
        reasoning = call.get("reasoning", '')

        # 🚀 关键步骤：将字符串转换为 RecordType 实例
        try:
            # 使用枚举的构造函数，根据值查找对应的成员
            # 例如 RecordType("tool") 会返回 RecordType.tool_call
            event_type = RecordType(call_type_str)
        except ValueError:
            # 如果字符串不在 RecordType 的值中，则使用错误类型或默认类型
            event_type = RecordType.error  # 或者 RecordType.event_call，取决于您的定义
            # 记录一个额外的错误信息，表示调用类型不匹配

        if func_name in self.handlers:
            try:
                result = self.handlers[func_name](**kwargs)

                if auto_record:
                    record_data = {
                        "func_name": func_name,
                        "reasoning": reasoning,
                        "result": result,
                        "call_kwargs": kwargs,
                        "status": "success",
                    }
                    # 传入的是 RecordType 实例
                    event_log = LogEvent(event_type, **record_data)
                    # 提交 log_event 对象（假设有 _submit_event 方法）
                    self._submit_event(event_log)

                return result

            except Exception as e:
                if auto_record:
                    # 发生异常时，强制使用 RecordType.error 实例
                    error_data = {
                        "func_name": func_name,
                        "reasoning": reasoning,
                        "error": str(e),  # 对应 LogEvent.register 中 error 模板的键
                        "raw_response": f"Execution failed for {func_name}",
                        "call_kwargs": kwargs,
                        "status": "error",
                    }
                    # 传入 RecordType.error 实例
                    event_log = LogEvent(RecordType.error, **error_data)
                    self._submit_event(event_log)

                return {"status": "error", "reason": f"execution failed: {str(e)}"}
        else:
            # handler not found 时的错误处理...
            if auto_record:
                # 可以使用 RecordType.error 或 RecordType.event_call 来记录
                not_found_data = {
                    "func_name": func_name,
                    "reasoning": reasoning,
                    "error": f"Handler not found: {func_name}",
                    "raw_response": f"Call type: {call_type_str}",
                    "call_kwargs": kwargs,
                    "status": "error_not_found",
                }
                event_log = LogEvent(RecordType.error, **not_found_data)
                self._submit_event(event_log)

            return {"status": "error", "reason": f"handler not found: {func_name}"}

    def apply_response(self, response:str,auto_record=True):
        """解析模型回复，并执行其中的prompt调用"""
        calls = []
        try:
            calls = parse_response(response)
            for call in calls:
                self.handle_call(call,auto_record)
        except Exception as e:
            if auto_record:
                record_data = {
                    "response": response,
                    "error": str(e),
                }
                log_event = LogEvent(RecordType.error, **record_data)
                self._submit_event(log_event)
        return calls

    def _submit_event(self, log_event:LogEvent):
        """
        记录一次正常调用
        :type log_event: LogEvent
        :return:
        """
        for window in self.windows:
            if isinstance(window, FlowStackPromptWindow):
                window.record_event(log_event)
                break

    def get_divided_snapshot(self):
        divided_snap_shot = {}
        for window in self.windows:
            divided_snap_shot.update(window.get_divided_snapshot())
        for sys_win in self.system_window:
            divided_snap_shot.update(sys_win.get_divided_snapshot())
        return divided_snap_shot


