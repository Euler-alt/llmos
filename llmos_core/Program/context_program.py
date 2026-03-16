from llmos_core.Prompts.PromptMainBoard import PromptMainBoard, parse_response
from llmos_core.llmos_util.api_client import LLMClient
from llmos_core.Prompts.Windows import PromptWindow
from llmos_core.schema import ProgramRunResult, LLMOSCall
import yaml
import json
from pathlib import Path

CACHE_FILE = Path('./cache') / "cache.yaml"


def load_cache_result(result_path=None) -> str:
    result_path = Path(result_path) if result_path else Path(CACHE_FILE)
    with open(result_path, "r") as f:
        result = yaml.safe_load(f)
    return result.get("result")


class ContextProgram:
    def __init__(self, code_file=None):
        self.promptMainBoard = PromptMainBoard()
        kernelPromptWindow = PromptWindow.from_name(PromptWindow.KernelPromptWindow)
        codePromptWindow = PromptWindow.from_name(PromptWindow.StackPromptWindow)
        stackPromptWindow = PromptWindow.from_name(PromptWindow.StackPromptWindow)
        heapPromptWindow = PromptWindow.from_name(PromptWindow.HeapPromptWindow)
        windows = [kernelPromptWindow, codePromptWindow, stackPromptWindow, heapPromptWindow]
        self.promptMainBoard.register_windows(windows)
        self.llm_client = LLMClient()

    def run(self, use_cache=True) -> ProgramRunResult:
        if use_cache:
            response_text = load_cache_result()
            calls = parse_response(response_text)
        else:
            messages = self.promptMainBoard.assemble_messages()
            tools = self.promptMainBoard.get_all_tools()
            response_msg = self.llm_client.chat(messages, tools=tools)
            response_text = response_msg.content or ""
            
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
                calls = self.promptMainBoard.apply_response(response_text)

        return ProgramRunResult(
            snapshot=self.promptMainBoard.get_divided_snapshot(),
            raw_response=response_text,
            parsed_calls=calls
        )
