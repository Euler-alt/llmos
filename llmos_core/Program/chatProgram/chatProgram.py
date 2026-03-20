from pathlib import Path

from llmos_core.Program.BaseProgram import BaseProgram
from llmos_core.cache import CacheManager
from llmos_core.llmos_util import LLMClient
from llmos_core.Prompts.Windows import PromptWindow


CACHE_DIR = Path(__file__).parent / 'cache_result'
CACHE_FILE = CACHE_DIR / "chat.json"
Code_file = Path(__file__).parent / "chatCode.md"
class ChatProgram(BaseProgram):
    def __init__(self,use_cache=True):

        # 注册窗口
        windows = [
            PromptWindow.from_name(PromptWindow.FlowStackPromptWindow),
            PromptWindow.from_name(PromptWindow.HeapPromptWindow),
            PromptWindow.from_name(PromptWindow.ALFWorldWindow),
            PromptWindow.from_name(PromptWindow.ChatPromptWindow),
            PromptWindow.from_name(PromptWindow.ThinkingPromptWindow),
        ]

        system_window = [PromptWindow.from_name(PromptWindow.KernelPromptWindow),PromptWindow.from_name(PromptWindow.CodePromptWindow,file_path=Code_file),]
        # === 初始化系统结构 ===
        super().__init__(windows=windows,system_windows=system_window)
        self.llm_client = LLMClient()
        self.use_cache = use_cache
        # === 缓存生成器状态 ===
        self.cache_manager = CacheManager(CACHE_FILE,clear_cache_file=not use_cache)

    def set_client_model(self, model_name):
        self.llm_client.set_model(model_name)

    # === 核心任务1：模型回合 ===
    def run(self,auto_record = True):
        """一次模型回合，可能来自缓存或实时API"""
        if self.use_cache:
            record = self.cache_manager.next_record()
            if record:
                print(f"[cache replay] 使用第 {record['index']} 轮缓存")
                response = record["response"]
                calls=self.promptMainBoard.apply_response(response)
                return {
                    "snapshot": self.promptMainBoard.get_divided_snapshot(),
                    "raw_response": response,
                    "parsed_calls": calls
                }

        # === 实时运行 ===
        messages = self.promptMainBoard.assemble_messages()

        # This logic is derived from the intended replacement, but adapted to be a complete and valid code block.
        # It introduces tool calling and handles both tool calls and regular text responses.
        import json
        from llmos_core.llmos_util import LLMOSCall

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
                result = self.promptMainBoard.handle_call(call_data, auto_record=auto_record)
                calls.append(result)
        else:
            # 如果没有 tool_calls，则尝试解析 content 中的 JSON Syscall
            calls = self.apply_response(response_text)

        # === 缓存记录 ===
        # NOTE: Caching `response_text` will not preserve tool calls on replay.
        # The cache replay logic might need a separate update to handle structured `response_msg`.
        serializable_messages = [m.model_dump() for m in messages]
        self.cache_manager.append_record(serializable_messages, response_text)

        return {
            "snapshot": self.promptMainBoard.get_divided_snapshot(),
            "raw_response": response_text, # Use response_text instead of the old `response`
            "parsed_calls": calls
        }

    def apply_response(self, response):
        return self.promptMainBoard.apply_response(response)

    def get_prompt_divided_snapshot(self):
        return self.promptMainBoard.get_divided_snapshot()