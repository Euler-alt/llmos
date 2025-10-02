from llmos_core.Prompts import PromptMainBoard,parse_response
from llmos_core.llmos_util import LLMClient
import yaml
from pathlib import Path

CACHE_FILE = Path('cache') / "cache.yaml"
def load_cache_result(result_path=None)->str:
    result_path = Path(result_path) if result_path else Path(CACHE_FILE)
    with open(result_path, "r") as f:
        result = yaml.safe_load(f)
    return result.get("result")

class ContextProgram:
    def __init__(self,code_file=None):
        self.promptMainBoard = PromptMainBoard(code_file=code_file)
        self.llm_client = LLMClient()

    def run(self, use_cache=True)->dict:
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
                    self.promptMainBoard.handle_call(func_name,**kwargs)

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
