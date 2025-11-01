from pathlib import Path
import json

from llmos_core.Program.BaseProgram import BaseProgram
from llmos_core.Prompts import PromptMainBoard, parse_response
from llmos_core.llmos_util import LLMClient
from llmos_core.Prompts.Windows import PromptWindow


CACHE_DIR = Path('./cache_result')
CACHE_FILE = CACHE_DIR / "chat.json"

from pathlib import Path
import json

def load_cache_result(result_path=None):
    """逐条加载缓存结果（生成器版）"""
    result_path = Path(result_path) if result_path else Path(CACHE_FILE)
    if not result_path.exists():
        print(f"[cache] 缓存文件 {result_path} 不存在，返回空生成器。")
        return
    with open(result_path, "r") as f:
        try:
            result = json.load(f)
        except json.JSONDecodeError:
            print(f"[cache] 文件损坏或格式错误：{result_path}")
            return
    if not isinstance(result, list):
        print(f"[cache] 非列表格式缓存，忽略。")
        return
    for i, record in enumerate(result):
        yield {
            "index": i,
            "prompt": record.get("prompt"),
            "response": record.get("response"),
            "meta": record.get("meta", {}),
        }


def append_cache_record(prompt, response):
    """把一次交互追加到缓存文件"""
    CACHE_FILE.parent.mkdir(exist_ok=True)
    try:
        if CACHE_FILE.exists():
            with open(CACHE_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []
    except json.JSONDecodeError:
        data = []

    data.append({
        "prompt": prompt,
        "response": response,
    })

    with open(CACHE_FILE, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


class ChatProgram(BaseProgram):
    def __init__(self):

        # 注册四个核心窗口
        windows = [
            PromptWindow.from_name(PromptWindow.KernelPromptWindow),
            PromptWindow.from_name(PromptWindow.CodePromptWindow),
            PromptWindow.from_name(PromptWindow.StackPromptWindow),
            PromptWindow.from_name(PromptWindow.HeapPromptWindow),
            PromptWindow.from_name(PromptWindow.ALFworldWindow),
            PromptWindow.from_name(PromptWindow.ChatPromptWindow),
            PromptWindow.from_name(PromptWindow.ThinkingPromptWindow),
        ]

        # === 初始化系统结构 ===
        super().__init__(windows)
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

    # === 核心任务1：模型回合 ===
    def run(self, use_cache=True):
        """一次模型回合，可能来自缓存或实时API"""
        if use_cache:
            record = self._next_cache()
            if record:
                print(f"[cache replay] 使用第 {record['index']} 轮缓存")
                response = record["response"]
                calls = parse_response(response)
                for call in calls:
                    if call["call_type"].lower() == "prompt":
                        self.promptMainBoard.handle_call(
                            call["func_name"], **call["kwargs"]
                        )
                return {
                    "snapshot": self.promptMainBoard.get_divided_snapshot(),
                    "raw_response": response,
                    "parsed_calls": calls,
                    "cache_index": self._cache_index,
                }

        # === 实时运行 ===
        prompt = self.promptMainBoard.assemble_prompt()
        response = self.llm_client.chat(prompt)
        calls = parse_response(response)
        for call in calls:
            if call["call_type"].lower() == "prompt":
                self.promptMainBoard.handle_call(
                    call["func_name"], **call["kwargs"]
                )

        # === 缓存记录 ===
        append_cache_record(prompt, response)

        return {
            "snapshot": self.promptMainBoard.get_divided_snapshot(),
            "raw_response": response,
            "parsed_calls": calls,
            "cache_index": None,
        }

    def env_event(self, args,kwargs):
        self.promptMainBoard.handle_call(args,**kwargs)

    def get_prompt_snapshot(self):
        return self.promptMainBoard.get_divided_snapshot()