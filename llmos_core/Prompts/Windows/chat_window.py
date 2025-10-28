from .BaseWindow import BasePromptWindow
from pathlib import Path

@BasePromptWindow.register('ChatWindow', 'chatWindow')
class ChatWindow(BasePromptWindow):
    def __init__(self,code_file=None,window_name="ChatWindow"):
        super().__init__(window_name=window_name)
        default_path = Path(__file__).parent / 'texts' / 'user_instruction.json'
        self.code_file = code_file if code_file else default_path
        with open(self.code_file,'r') as f:
            self.meta_prompt = f.read()
        self.prompt = ''
        self.messages = [] # 历史对话记录 [{role: 'user'/'assistant', text: str}]

    def export_meta_prompt(self):
        return f"\n{self.meta_prompt}"

    def export_state_prompt(self):
        if not self.messages:
            return '\nNO USER instruction'
        joined = "\n".join([f"{m['role'].upper()}: {m['text']}" for m in self.messages])
        return f"\n{joined}"

    def forward(self):
        return f"{self.export_meta_prompt()}{self.export_state_prompt()}"

    # === 处理大模型回调 ===
    def llm_response(self, text = ""):
        """当模型主动调用 chat 窗口时（如反问）"""
        self.messages.append({"role": "assistant", "text": text})

    # === 环境事件入口 ===
    def user_response(self, text=""):
        """来自用户的新输入"""
        self.messages.append({"role": "user", "text": text})

    # === 可导出状态 ===
    def export_handlers(self):
        return {
            "user_response": self.user_response,
            "llm_response": self.llm_response,
        }



import asyncio
from collections import deque

import asyncio
from threading import Thread
from collections import deque
from datetime import datetime


@BasePromptWindow.register('AsychatWindow', 'AsyChatWindow')
class AsyChatPromptWindow(BasePromptWindow):
    def forward(self, *args, **kwargs):
        pass

    def __init__(self, window_name="Chat"):
        super().__init__(window_name=window_name)
        self.chat_history = []
        self.input_buffer = deque()
        self.streaming_message = {"active": False, "content": ""}

        # 🔥 关键：启动内部异步事件循环（在后台线程）
        self._loop = asyncio.new_event_loop()
        self._thread = Thread(target=self._run_event_loop, daemon=True)
        self._thread.start()

        # 启动用户输入监听器（模拟）
        asyncio.run_coroutine_threadsafe(
            self._user_input_listener(),
            self._loop
        )

    def _run_event_loop(self):
        """后台线程运行事件循环"""
        asyncio.set_event_loop(self._loop)
        self._loop.run_forever()

    async def _user_input_listener(self):
        """
        窗口内部的异步任务：持续监听用户输入
        （实际项目中可以是 WebSocket 连接、stdin 监听等）
        """
        while True:
            # 模拟：从某个输入源获取用户消息
            # 真实场景可能是：
            # message = await websocket.recv()
            # message = await asyncio.to_thread(input, "User: ")

            await asyncio.sleep(0.1)  # 避免空转

            # 这里可以通过共享队列从外部注入消息
            # 例如：self._external_input_queue

    def inject_user_message_sync(self, message):
        """
        🔥 外部同步调用接口（主循环可以调用）
        内部通过事件循环异步处理
        """
        future = asyncio.run_coroutine_threadsafe(
            self._handle_user_input(message),
            self._loop
        )
        # 不等待结果，立即返回（非阻塞）
        return {"status": "queued"}

    async def _handle_user_input(self, message):
        """内部异步处理用户输入"""
        msg_obj = {
            "role": "user",
            "content": message,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }

        if self.streaming_message["active"]:
            # LLM正在说话，缓存输入
            self.input_buffer.append(msg_obj)
        else:
            # 直接加入历史
            self.chat_history.append(msg_obj)

    # ============ 对外同步接口（主循环调用）============

    def export_state_prompt(self):
        """同步接口：返回当前状态快照"""
        history_str = ""

        # 历史消息
        for msg in self.chat_history[-5:]:
            history_str += f"[{msg['role'].upper()} {msg['timestamp']}]:\n"
            history_str += f"{msg['content']}\n\n"

        # 流式生成中的消息
        if self.streaming_message["active"]:
            history_str += f"[ASSISTANT streaming]:\n"
            history_str += f"{self.streaming_message['content']}▌\n\n"

        # 缓冲区
        if self.input_buffer:
            history_str += "--- USER INPUT BUFFER ---\n"
            for buffered in self.input_buffer:
                history_str += f"[{buffered['timestamp']}] {buffered['content']}\n"

        return f"### CHAT WINDOW STATE ###\n{history_str}"

    def export_meta_prompt(self):
        return """
### CHAT WINDOW FUNCTIONS ###
- chat_reply(message="..."): Send message to user
- chat_start_streaming(): Mark that you're about to send a long message
- chat_end_streaming(): Finish streaming and process buffered user inputs
- chat_check_buffer(): Check if user sent messages while you were speaking
"""

    # ============ 函数调用处理（同步接口）============

    def _chat_reply(self, *args, **kwargs):
        """LLM调用：发送消息"""
        message = kwargs.get("message", "")

        # 如果正在streaming，追加内容
        if self.streaming_message["active"]:
            self.streaming_message["content"] += message
        else:
            # 直接发送
            self.chat_history.append({
                "role": "assistant",
                "content": message,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })

        return {"status": "ok", "message": message}

    def _chat_start_streaming(self, *args, **kwargs):
        """LLM调用：开始流式输出"""
        self.streaming_message = {"active": True, "content": ""}
        return {"status": "streaming_started"}

    def _chat_end_streaming(self, *args, **kwargs):
        """LLM调用：结束流式输出"""
        if self.streaming_message["active"]:
            # 将流式消息加入历史
            self.chat_history.append({
                "role": "assistant",
                "content": self.streaming_message["content"],
                "timestamp": datetime.now().strftime("%H:%M:%S")
            })
            self.streaming_message = {"active": False, "content": ""}

            # 处理缓冲区
            while self.input_buffer:
                self.chat_history.append(self.input_buffer.popleft())

        return {"status": "streaming_ended", "buffered_processed": len(self.input_buffer)}

    def _chat_check_buffer(self, *args, **kwargs):
        """LLM调用：检查缓冲区"""
        return {
            "status": "ok",
            "buffer_count": len(self.input_buffer),
            "messages": [msg["content"] for msg in self.input_buffer]
        }

    def export_handlers(self):
        return {
            'chat_reply': self._chat_reply,
            'chat_start_streaming': self._chat_start_streaming,
            'chat_end_streaming': self._chat_end_streaming,
            'chat_check_buffer': self._chat_check_buffer
        }