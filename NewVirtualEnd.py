from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import json

from llmos_core.Program import BaseProgram
from llmos_core.Program.context_program import ContextProgram
from llmos_core.Program.ALFworldProgram import ALFworldProgram
from llmos_core.Program.chatProgram import ChatProgram
from llmos_core.ui import WindowConfig
from llmos_core.ui.uitranform import update_backend_state_from_program

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局程序实例
# 默认启动 ALFworld
program: BaseProgram | None = ALFworldProgram()
update_backend_state_from_program(program)

class BackendState:
    """后端状态管理器"""
    def __init__(self):
        self.window_configs: List[WindowConfig] = []
        self.subscribers: List[asyncio.Queue] = []
        self.cache: Dict[str, Any] = {}
        self.use_cache: bool = True

    def get_full_state(self) -> Dict[str, Any]:
        self.update_windowConfig()
        return {"windows": [config.model_dump() for config in self.window_configs]}

    async def broadcast_update(self):
        full_state = self.get_full_state()
        for queue in self.subscribers:
            await queue.put(full_state)

    def update_windowConfig(self):
        self.window_configs = update_backend_state_from_program(program)

# 全局状态实例
backend_state = BackendState()


# 程序映射
PROGRAM_CLASSES = {
    "ALFworld": ALFworldProgram,
    "Context": ContextProgram,
    "Chat": ChatProgram
}

class ProgramSetRequest(BaseModel):
    program_name: str

@app.post("/api/program/set")
async def set_program(request: ProgramSetRequest):
    global program
    prog_class = PROGRAM_CLASSES.get(request.program_name)
    if not prog_class:
        return JSONResponse(content={"message": "Invalid program name"}, status_code=400)
    
    program = prog_class()
    update_backend_state_from_program(program)
    await backend_state.broadcast_update()
    return {"message": f"Program set to {request.program_name}"}


# 用于存储 SSE 客户端队列
subscribers = []
# 新式窗口配置管理接口
@app.get("/api/windows/config")
async def get_window_configs():
    """获取窗口配置列表"""
    return JSONResponse(content={
        "windows": [config.model_dump() for config in backend_state.window_configs]
    })

# SSE 接口（新式格式）
@app.get("/api/sse")
async def sse_endpoint():
    async def event_generator():
        # 新客户端连接时立即推送完整状态
        initial_data = backend_state.get_full_state()
        yield f"data: {json.dumps(initial_data, ensure_ascii=False)}\n\n"

        # 添加到订阅者队列
        queue = asyncio.Queue()
        backend_state.subscribers.append(queue)

        try:
            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        except asyncio.CancelledError:
            # 客户端断开时清理
            if queue in backend_state.subscribers:
                backend_state.subscribers.remove(queue)
            raise

    return StreamingResponse(event_generator(), media_type="text/event-stream")

# 广播函数：推送给所有 SSE 客户端
async def send_sse_update(data):
    for queue in subscribers:
        await queue.put(data)

# 请求体模型
class LLMCallRequest(BaseModel):
    prompt: str

@app.post("/api/llm/call")
async def call_llm(data: LLMCallRequest):
    """LLM 调用接口"""
    prompt = data.prompt
    print("收到 LLM 调用请求！Prompt 内容前50字符：")
    print(prompt[:50])
    
    # 调用上下文程序
    if backend_state.use_cache and "last_result" in backend_state.cache:
        result = backend_state.cache["last_result"]
    else:
        result = program.run(use_cache=backend_state.use_cache)
        backend_state.cache["last_result"] = result

    backend_state.update_windowConfig()
    # 广播更新
    await backend_state.broadcast_update()
    
    # 💡 提取第一个行动记录的摘要作为简短回答，如果没有则显示执行成功
    answer = "执行成功"
    if result.parsed_calls and len(result.parsed_calls) > 0:
        first_call = result.parsed_calls[0]
        # 如果是 ToolCallResult 对象或字典
        if hasattr(first_call, 'summary'):
            answer = first_call.summary
        elif isinstance(first_call, dict) and 'summary' in first_call:
            answer = first_call['summary']
        elif isinstance(first_call, dict) and 'result' in first_call:
            answer = str(first_call['result'])

    print(f"Finish a call. Result summary: {answer[:30]}...")
    
    return {
        "answer": answer,
        "raw_response": result.raw_response,
        "parsed_calls": result.parsed_calls,
    }

class LLMConfig(BaseModel):
    use_cache: bool

@app.post("/api/llm/config")
async def config_llm(config: LLMConfig):
    backend_state.use_cache = config.use_cache
    return {"message": f"Cache usage set to {backend_state.use_cache}"}

@app.get("/")
async def root():
    """根路径，显示后端信息"""
    return {
        "message": "LLM OS 新式后端启动器",
        "version": "1.0.0",
        "features": [
            "动态窗口配置管理",
            "SSE 实时数据推送",
            "向后兼容的API接口",
            "前端组件类型验证"
        ],
        "supported_window_types": ["kernel", "heap", "stack", "code","text"]
    }

if __name__ == "__main__":
    import uvicorn
    print("启动新式后端服务器...")
    print("支持的窗口类型: kernel, heap, stack, code")
    print("SSE 端点: /api/sse")
    print("窗口配置管理: /api/windows/config")
    print("传统API兼容: /api/modules, /api/modules/update")
    
    uvicorn.run(app, host="0.0.0.0", port=3001)