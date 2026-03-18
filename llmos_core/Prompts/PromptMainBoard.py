import json
from dataclasses import asdict
from collections.abc import Iterable
from typing import List

from llmos_core.Prompts.Windows import BasePromptWindow,FlowStackPromptWindow
from llmos_core.Prompts.Windows.BaseWindow import NullSystemWindow
from typing import List, Union

from llmos_core.Prompts.Windows.stack_window import StackPromptWindow
from llmos_core.logger import LogEvent, RecordType
from llmos_core.ui import WindowConfig
from llmos_core.schema import LLMOSCall, ToolCallResult, ToolDefinition

ALLOWEDKEYS = ["call_type", "func_name", "kwargs", 'reasoning']
NEEDKEYS = ["call_type", "func_name"]

from llmos_core.llmos_util.api_client import LLMMessage, LLMClient
from llmos_core.Prompts.Windows.Window_register import get_window_type

import re
import json

def repair_json_with_llm(bad_json_str: str, error_msg: str = "", retry_count: int = 1) -> str:
    """
    使用大模型修复损坏的 JSON 字符串。
    """
    client = LLMClient()
    system_prompt = f"""
    You are a strict JSON repair engine.

    Your task is to repair the user's malformed JSON so that it becomes valid JSON that can be parsed directly by json.loads() in Python.

    {"The specific error reported by the parser is: " + error_msg if error_msg else ""}

    CRITICAL RULES:

    1. Output ONLY the repaired JSON.
    2. Do NOT output explanations, comments, or markdown.
    3. The output must start with {{ or [ and end with }} or ].

    JSON FORMAT REQUIREMENTS:

    - All strings MUST use double quotes ".
    - Single quotes ' are NOT allowed in JSON strings.
    - If a string contains internal double quotes, they MUST be escaped using \\".
    - Remove trailing commas.
    - Remove comments (// or /* */).
    - Ensure all brackets and braces are balanced.
    - Ensure keys are enclosed in double quotes.
    - Ensure arrays use [ ] and objects use {{ }} correctly.

    COMMON ERRORS TO FIX:

    - Replace single quotes with double quotes.
    - Escape internal quotes inside strings.
    - Remove invalid escape characters.
    - Remove trailing commas in objects and arrays.
    - Fix unclosed brackets or braces.
    - Remove markdown formatting such as ```json.
    - Remove text before or after the JSON.
    - Ensure the output is a single valid JSON object or array.

    VALIDATION RULE:

    The result MUST be valid for:

    json.loads(output)

    If the JSON cannot be confidently repaired, return the closest valid JSON structure.

    Remember:
    Output ONLY the repaired JSON.
    No explanations.
    """
    
    current_str = bad_json_str
    for _ in range(retry_count):
        try:
            # 在用户消息中也加入错误信息
            user_msg = f"MALFORMED JSON:\n{current_str}\n\nERROR MESSAGE:\n{error_msg}" if error_msg else current_str
            repaired_resp = client.chat(messages=user_msg, system_prompt=system_prompt)
            
            # 这里的 client.chat 返回的是消息对象，需要取 content
            repaired = repaired_resp.content if hasattr(repaired_resp, 'content') else str(repaired_resp)
            
            # 尝试解析一次以验证
            json.loads(repaired.strip())
            return repaired.strip()
        except Exception:
            current_str = repaired if 'repaired' in locals() else bad_json_str
            continue
    return bad_json_str

def parse_response(response_text: str, retry_fix: int = 1):
    """
    最稳妥的解析策略：
    1. 尝试原始字符串。
    2. 尝试去除 Markdown 标记后解析。
    3. 如果都失败，尝试使用 LLM 修复。
    """
    cleaned_text = response_text.strip()
    last_error = ""

    # 辅助函数：尝试解析
    def _try_parse(text):
        nonlocal last_error
        try:
            # 尝试移除可能的 markdown 代码块标记
            if text.startswith("```"):
                text = re.sub(r'^```(?:json)?\s*|\s*```$', '', text, flags=re.MULTILINE).strip()
            return json.loads(text)
        except json.JSONDecodeError as e:
            last_error = str(e)
            return None

    # 第一步：直接尝试
    data = _try_parse(cleaned_text)

    # 第二步：如果失败，尝试使用 LLM 修复
    if data is None and retry_fix > 0:
        repaired_text = repair_json_with_llm(cleaned_text, error_msg=last_error, retry_count=retry_fix)
        data = _try_parse(repaired_text)

    # 第三步：如果依然失败，报错
    if data is None:
        raise ValueError(f"JSON 解析失败: {last_error}。原始文本片段: {response_text[:100]}...")

    if isinstance(data, dict):
        data = [data]
    return data



class PromptMainBoard:
    def __init__(self):

        self.user_windows:List[BasePromptWindow] = []
        self.system_windows:List[BasePromptWindow] = []
        self.handlers = {}

    def assemble_messages(self) -> List[LLMMessage]:
        """将窗口转化为消息列表格式"""
        messages = []
        # 系统窗口
        system_content = "".join([window.forward() for window in self.system_windows])
        if system_content:
            messages.append(LLMMessage(role="system", content=system_content))

        # 用户窗口
        for window in self.user_windows:
            content = window.forward()
            if content:
                messages.append(LLMMessage(role="user", content=content))
        return messages

    def get_all_tools(self) -> List[dict]:
        """收集所有窗口提供的外部工具定义"""
        all_tools = []
        # 遍历所有窗口，收集工具
        for win in self.system_windows + self.user_windows:
            for tool_def in win.get_tool_definitions():
                all_tools.append(tool_def.to_openai_tool())
        return all_tools

    def apply_response(self, response: str, auto_record=True):
        """解析模型在 content 中生成的 JSON Syscall"""
        calls = []
        try:
            calls = parse_response(response)
            for call in calls:
                self.handle_call(call, auto_record)
        except Exception as e:
            if auto_record:
                log_event = LogEvent(
                    event_type=RecordType.error,
                    error=str(e),
                    raw_response=response
                )
                self._submit_event(log_event)
        return calls

    def register_windows(
            self,
            user_windows: Union[List[BasePromptWindow], BasePromptWindow, None] = None,
            system_windows: Union[List[BasePromptWindow], BasePromptWindow, None] = None
    ):
        """注册模块，可接受单个实例或实例列表
        :param user_windows:
        :param system_windows:
        :return:
        """

        def _register(target_list, win):
            target_list.append(win)
            self.handlers.update(win.export_handlers() or {})

        def _ensure_list(obj):
            if obj is None:
                return []
            if isinstance(obj, Iterable) and not isinstance(obj, (str, bytes)):
                return list(obj)
            return [obj]

        for user_win in _ensure_list(user_windows):
            _register(self.user_windows, user_win)

        for sys_win in _ensure_list(system_windows):
            _register(self.system_windows, sys_win)

    def handle_call(self, call_data: Union[dict, LLMOSCall], auto_record=True) -> ToolCallResult:
        """统一分发到对应窗口的 handler"""
        # 如果输入是字典，转换为 LLMOSCall dataclass
        if isinstance(call_data, dict):
            call = LLMOSCall(
                call_type=call_data.get("call_type", "tool"),
                func_name=call_data.get("func_name", ""),
                kwargs=call_data.get("kwargs", {}),
                reasoning=call_data.get("reasoning", "")
            )
        else:
            call = call_data

        func_name = call.func_name
        call_type_str = call.call_type
        kwargs = call.kwargs
        reasoning = call.reasoning

        # 🚀 关键步骤：将字符串转换为 RecordType 实例
        try:
            event_type = RecordType(call_type_str)
        except ValueError:
            event_type = RecordType.error

        if func_name in self.handlers:
            try:
                result = self.handlers[func_name](**kwargs)

                # 💡 提取语义摘要 (优先从返回值中获取)
                summary = ""
                if isinstance(result, dict) and "__summary__" in result:
                    summary = result.pop("__summary__") # 移除摘要字段，保留核心结果
                else:
                    summary = str(result)

                call_result = ToolCallResult(
                    func_name=func_name,
                    reasoning=reasoning,
                    result=result,
                    summary=summary,
                    call_kwargs=kwargs,
                    status="success"
                )

                if auto_record:
                    # 记录事件到系统（保持原有逻辑，但使用 dataclass 属性）
                    event_log = LogEvent(
                        event_type=event_type,
                        func_name=call_result.func_name,
                        reasoning=call_result.reasoning,
                        result=call_result.summary, # 使用摘要作为 Outcome 展示
                        call_kwargs=call_result.call_kwargs,
                        status=call_result.status
                    )
                    self._submit_event(event_log)
                return call_result

            except Exception as e:
                error_result = ToolCallResult(
                    func_name=func_name,
                    reasoning=reasoning,
                    result=str(e),
                    call_kwargs=kwargs,
                    status="error"
                )
                if auto_record:
                    error_log = LogEvent(
                        event_type=RecordType.error,
                        func_name=func_name,
                        reasoning=reasoning,
                        error=str(e),
                        raw_response=f"Execution failed for {func_name}",
                        call_kwargs=kwargs,
                        status="error"
                    )
                    self._submit_event(error_log)
                return error_result
        else:
            msg = f"Handler for {func_name} not found."
            if auto_record:
                not_found_log = LogEvent(
                    event_type=RecordType.error,
                    func_name=func_name,
                    error=msg,
                    status="error_not_found"
                )
                self._submit_event(not_found_log)
            return ToolCallResult(func_name=func_name, result=msg, status="error")

    def _submit_event(self, log_event:LogEvent):
        """
        记录一次调用结果
        :type log_event: LogEvent
        :return:
        """
        for window in self.user_windows:
            if isinstance(window, FlowStackPromptWindow):
                window.record_event(log_event)
                break

    def get_divided_snapshot(self):
        divided_snap_shot = {}
        for sys_win in self.system_windows:
            # sys_win.get_divided_snapshot() 返回 WindowSnapshot dataclass
            divided_snap_shot[sys_win.window_title] = asdict(sys_win.get_divided_snapshot())
        for window in self.user_windows:
            divided_snap_shot[window.window_title] = asdict(window.get_divided_snapshot())
        return divided_snap_shot

    def get_ui_configs(self)->List[WindowConfig]:
        """
        获取所有窗口的 UI 配置信息（包含类型、标题和数据快照）。
        后端通过调用该接口获取前端展示所需的一切信息。
        """
        configs :List[WindowConfig]= []
        all_windows = self.system_windows + self.user_windows
        
        for index, window in enumerate(all_windows):
            window_title = window.window_title
            window_type = get_window_type(window)
            
            # 获取窗口快照数据 (WindowSnapshot dataclass)
            snapshot_data = window.get_divided_snapshot()
            
            # 🚀 修复点：将 dataclass 转换为 dict 以适配 Pydantic 校验
            snapshot_dict = asdict(snapshot_data)
            
            window_config = WindowConfig(
                        windowId=window_title,
                        windowType=window_type,
                        windowTitle = window_title,
                        order= index,
                        windowTheme = None,
                        data=snapshot_dict
            )

            configs.append(window_config)
        return configs


