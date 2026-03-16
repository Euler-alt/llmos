from llmos_core.Program.BaseProgram import BaseProgram
from llmos_core.Program.cache import load_cache_result
from llmos_core.Prompts.PromptMainBoard import PromptMainBoard, parse_response
from llmos_core.llmos_util.api_client import LLMClient
from llmos_core.Prompts.Windows import PromptWindow
from llmos_core.schema import ProgramRunResult, LLMOSCall
import json

class ALFworldProgram(BaseProgram):
    def __init__(self):
        super().__init__()
        self.llm_client = LLMClient()
        self.promptMainBoard = PromptMainBoard()
        code_window = PromptWindow.from_name(PromptWindow.CodePromptWindow)
        heap_window = PromptWindow.from_name(PromptWindow.HeapPromptWindow)
        stack_window = PromptWindow.from_name(PromptWindow.StackPromptWindow)
        alfworld_window = PromptWindow.from_name(PromptWindow.ALFWorldWindow)
        chat_window = PromptWindow.from_name(PromptWindow.ChatPromptWindow)
        kernel_window = PromptWindow.from_name(PromptWindow.KernelPromptWindow)
        self.promptMainBoard.register_windows(
            user_windows=[code_window, heap_window, stack_window, alfworld_window, chat_window],
            system_windows=kernel_window
        )

    def run(self, use_cache=False) -> ProgramRunResult:
        if use_cache:
            response_text = load_cache_result()
            calls = parse_response(response_text)
        else:
            messages = self.promptMainBoard.assemble_messages()
            # 调用 LLM，传入收集到的 tools (如果存在)
            tools = self.promptMainBoard.get_all_tools()
            kwargs = {"messages": messages}
            if tools:
                kwargs["tools"] = tools
            
            response_msg = self.llm_client.chat(**kwargs)
            response_text = response_msg.content or ""
            
            # 优先处理 tool_calls
            if hasattr(response_msg, 'tool_calls') and response_msg.tool_calls:
                calls = []
                for tc in response_msg.tool_calls:
                    call_data = LLMOSCall(
                        call_type="tool",
                        func_name=tc.function.name,
                        kwargs=json.loads(tc.function.arguments)
                    )
                    result = self.promptMainBoard.handle_call(call_data)
                    calls.append(result)
            else:
                # 如果没有 tool_calls，则尝试解析 content 中的 JSON Syscall
                calls = self.promptMainBoard.apply_response(response_text)

        return ProgramRunResult(
            raw_response=response_text,
            parsed_calls=calls
        )
