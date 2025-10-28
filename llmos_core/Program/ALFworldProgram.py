
from llmos_core.Prompts import PromptMainBoard, parse_response
from llmos_core.llmos_util import LLMClient
from llmos_core.Prompts.Windows import PromptWindow

from .cache import load_cache_result



class ALFworldProgram:
    def __init__(self):
        self.llm_client = LLMClient()
        self.promptMainBoard = PromptMainBoard()
        codeWindow = PromptWindow.from_name(PromptWindow.CodePromptWindow)
        heapWindow = PromptWindow.from_name(PromptWindow.HeapPromptWindow)
        stackWindow = PromptWindow.from_name(PromptWindow.StackPromptWindow)
        ALFworldWindow = PromptWindow.from_name(PromptWindow.ALFworldWindow)
        kernelWindow = PromptWindow.from_name(PromptWindow.KernelPromptWindow)
        self.promptMainBoard.register_windows([kernelWindow, codeWindow, heapWindow, stackWindow, ALFworldWindow])

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
                "snapshot": self.promptMainBoard.get_divide_snapshot(),
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

