
from llmos_core.Prompts import PromptMainBoard, parse_response
from llmos_core.llmos_util import LLMClient
from llmos_core.Prompts.Windows import PromptWindow

from llmos_core.cache import load_cache_result



class ALFworldProgram:
    def __init__(self):
        self.llm_client = LLMClient()
        self.promptMainBoard = PromptMainBoard()
        code_window = PromptWindow.from_name(PromptWindow.CodePromptWindow)
        heap_window = PromptWindow.from_name(PromptWindow.HeapPromptWindow)
        stack_window = PromptWindow.from_name(PromptWindow.StackPromptWindow)
        alfworld_window = PromptWindow.from_name(PromptWindow.ALFWorldWindow)
        kernel_window = PromptWindow.from_name(PromptWindow.KernelPromptWindow)
        self.promptMainBoard.register_windows([kernel_window, code_window, heap_window, stack_window, alfworld_window])

    def run(self, use_cache=False):
        if use_cache:
            response = load_cache_result()
        else:
            full_prompt = self.promptMainBoard.assemble_prompt()
            response = self.llm_client.chat(full_prompt)
        # 3. 解析结果并更新内存
        try:
            calls = parse_response(response)
            for call in calls:
                call_type = call["call_type"]
                func_name = call["func_name"]
                kwargs = call["kwargs"]
                if call_type.lower() == "prompt":
                    self.promptMainBoard.handle_call(func_name, **kwargs)

            return {
                "snapshot": self.promptMainBoard.get_divided_snapshot(),
                "raw_response": response,
                "parsed_calls": calls
            }

        except Exception as e:
            print("解析错误:", e, "原始输出:", response)
            return {
                "snapshot": {},
                "raw_response": response,
                "parsed_calls": []
            }

