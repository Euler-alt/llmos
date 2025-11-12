from pathlib import Path
import json
from platform import system

from llmos_core.Program.BaseProgram import BaseProgram
from llmos_core.Prompts import PromptMainBoard, parse_response
from llmos_core.cache import append_cache_record, load_cache_result
from llmos_core.llmos_util import LLMClient
from llmos_core.Prompts.Windows import PromptWindow


CACHE_DIR = Path(__file__).parent / 'cache_result'
CACHE_FILE = CACHE_DIR / "chat.json"

class ChatProgram(BaseProgram):
    def __init__(self):

        # 注册四个核心窗口
        windows = [
            PromptWindow.from_name(PromptWindow.FlowStackPromptWindow),
            PromptWindow.from_name(PromptWindow.HeapPromptWindow),
            PromptWindow.from_name(PromptWindow.ALFWorldWindow),
            PromptWindow.from_name(PromptWindow.ChatPromptWindow),
            PromptWindow.from_name(PromptWindow.ThinkingPromptWindow),
        ]

        system_window = PromptWindow.from_name(PromptWindow.KernelPromptWindow)
        # === 初始化系统结构 ===
        super().__init__(windows=windows,system_window=system_window)
        self.llm_client = LLMClient()
        # === 缓存生成器状态 ===
        self._cache_iter = None
        self._cache_index = -1  # 当前缓存帧索引

    def _next_cache(self):
        """尝试获取下一条缓存记录"""
        if self._cache_iter is None:
            self._cache_iter = load_cache_result()
        try:
            record = next(self._cache_iter)
            self._cache_index = record["index"]
            return record
        except StopIteration:
            self._cache_iter = None
            return None

    def set_client_model(self, model_name):
        self.llm_client.set_model(model_name)

    # === 核心任务1：模型回合 ===
    def run(self, use_cache=True):
        """一次模型回合，可能来自缓存或实时API"""
        if use_cache:
            record = self._next_cache()
            if record:
                print(f"[cache replay] 使用第 {record['index']} 轮缓存")
                response = record["response"]
                calls=self.apply_response(response)
                return {
                    "snapshot": self.promptMainBoard.get_divided_snapshot(),
                    "raw_response": response,
                    "parsed_calls": calls,
                    "cache_index": self._cache_index,
                }

        # === 实时运行 ===
        prompt = self.promptMainBoard.assemble_prompt()
        system_prompt = prompt.get("system")
        user_prompt = prompt.get("user")
        response = self.llm_client.chat(user_prompt=user_prompt,system_prompt=system_prompt)
        calls = self.apply_response(response)
        # === 缓存记录 ===
        append_cache_record(CACHE_FILE,prompt, response)
        return {
            "snapshot": self.promptMainBoard.get_divided_snapshot(),
            "raw_response": response,
            "parsed_calls": calls,
            "cache_index": None,
        }


    def apply_response(self, response:str):
        """解析模型回复，并执行其中的prompt调用"""
        try:
            calls = parse_response(response)
            for call in calls:
                self.promptMainBoard.handle_call(call)
        except Exception as e:
            self.promptMainBoard.record_execution("error", raw_response=response, error_message =  str(e))
        return calls

    def env_event(self, args,kwargs):
        self.promptMainBoard.handle_call(args,**kwargs)

    def get_prompt_snapshot(self):
        return self.promptMainBoard.get_divided_snapshot()