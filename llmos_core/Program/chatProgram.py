import asyncio
from pathlib import Path
import yaml

from llmos_core.Program.BaseProgram import BaseProgram
from llmos_core.Prompts import PromptMainBoard, parse_response
from llmos_core.llmos_util import LLMClient
from llmos_core.Prompts.Windows import PromptWindow


CACHE_FILE = Path('./cache') / "cache.yaml"


def load_cache_result(result_path=None) -> str:
    result_path = Path(result_path) if result_path else Path(CACHE_FILE)
    with open(result_path, "r") as f:
        result = yaml.safe_load(f)
    return result.get("result")


class ChatProgram(BaseProgram):
    def __init__(self):

        # 注册四个核心窗口
        windows = [
            PromptWindow.from_name(PromptWindow.KernelPromptWindow),
            PromptWindow.from_name(PromptWindow.CodePromptWindow),
            PromptWindow.from_name(PromptWindow.StackPromptWindow),
            PromptWindow.from_name(PromptWindow.HeapPromptWindow),
            PromptWindow.from_name(PromptWindow.ALFworldWindow),
            PromptWindow.from_name(PromptWindow.ChatPromptWindow)
        ]

        # === 初始化系统结构 ===
        super().__init__(windows)
        self.llm_client = LLMClient()
    # === 核心任务1：模型回合 ===
    def run(self, use_cache=True):
        """持续运行的大模型回合"""
        if use_cache:
            response = load_cache_result()
        else:
            prompt = self.promptMainBoard.assemble_prompt()
            response = self.llm_client.chat(prompt)  # 假设异步接口
        calls = parse_response(response)
        for call in calls:
            call_type = call["call_type"]
            func_name = call["func_name"]
            kwargs = call["kwargs"]
            if call_type.lower() == "prompt":
                self.promptMainBoard.handle_call(func_name,**kwargs)
        return {
            "snapshot": self.promptMainBoard.get_divided_snapshot(),
            "raw_response": response,
            "parsed_calls": calls
        }

    def env_event(self, args,kwargs):
        self.promptMainBoard.handle_call(args,**kwargs)

    def get_prompt_snapshot(self):
        return self.promptMainBoard.get_divided_snapshot()