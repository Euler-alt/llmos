from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import asyncio
import json
from pathlib import Path
from llmos_core.Program.context_program import ContextProgram
from llmos_core.Program.ALFworldProgram import ALFworldProgram
from llmos_core.Program.chatProgram import ChatProgram
app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 加载上下文程序
program = ChatProgram()


# 新式后端状态管理
class WindowConfig(BaseModel):
    """窗口配置模型"""
    WindowId: str
    windowType: str  # 必须与前端组件注册表匹配：kernel, heap, stack, code
    windowTitle: str
    description: Optional[str] = None
    order: int = 0
    windowTheme: Optional[str] = None
    icon: Optional[str] = None


class BackendState:
    """后端状态管理器"""

    def __init__(self):
        self.window_configs: List[WindowConfig] = [
            WindowConfig(
                WindowId="kernel-1",
                windowType="kernel",
                windowTitle="Kernel",
                description="系统规则和工作流程",
                order=0,
                windowTheme="blue",
                icon="kernel"
            ),
            WindowConfig(
                WindowId="heap-2",
                windowType="heap",
                windowTitle="Heap",
                description="持久化存储区域",
                order=1,
                windowTheme="gray",
                icon="heap"
            ),
            WindowConfig(
                WindowId="stack-3",
                windowType="stack",
                windowTitle="FlowStackWindow",
                description="临时工作区域",
                order=2,
                windowTheme="green",
                icon="stack"
            ),
            WindowConfig(
                WindowId="text-4",
                windowType="text",
                windowTitle="ALFWorld",
                description="alfworld信息",
                order=4,
                windowTheme="purple",
                icon="code"
            ),
            WindowConfig(
                WindowId="text-4",
                windowType="text",
                windowTitle="think_window",
                description="大模型思考信息",
                order=4,
                windowTheme="yellow",
                icon="code"
            ),
            WindowConfig(
                WindowId="chat-5",
                windowType="chat",
                windowTitle="ChatWindow",
                description="对话交互",
                order=5,
                windowTheme="orange",
                icon="code"
            )
        ]

        # 模块数据存储
        self.window_data: Dict[str, Any] = {
            "Kernel": "系统规则和工作流：\n- 始终优先调用工具函数来完成任务。\n- 使用栈模块管理多步任务。",
            "Heap": "持久化存储：\n- 当前用户：Alex\n- 任务目标：查找最新的AI新闻",
            "FlowStackWindow": "任务执行栈：\n- [step 1] 调用搜索工具\n- [step 2] 汇总搜索结果",
            "ALFWorld": "文本",
            "ChatWindow":"聊天消息展示",
            "think_window":"思考信息"
        }

        # SSE 客户端队列
        self.subscribers: List[asyncio.Queue] = []

    def update_snapshot(self):
        snapshot = program.get_prompt_snapshot()
        for key in self.window_data:
            if key in snapshot.keys():
                self.window_data[key] = snapshot[key]

    def validate_window_type(self, window_type: str) -> bool:
        """验证窗口类型是否有效（与前端注册表匹配）"""
        valid_types = {"kernel", "heap", "stack", "code", "text"}
        return window_type in valid_types

    def get_full_state(self) -> Dict[str, Any]:
        """获取完整的状态数据（新式格式）"""
        return {
            "windows": [config.dict() for config in self.window_configs],
            **self.window_data
        }

    def get_legacy_state(self) -> Dict[str, Any]:
        """获取传统格式的状态数据（向后兼容）"""
        return self.window_data.copy()

    async def broadcast_update(self):
        """广播状态更新给所有客户端"""
        full_state = self.get_full_state()
        for queue in self.subscribers:
            await queue.put(full_state)


# 全局状态实例
backend_state = BackendState()

# 用于存储 SSE 客户端队列
subscribers = []




# GET 接口：获取所有模块数据（向后兼容）
@app.get("/api/windows")
async def get_windows():
    return JSONResponse(content=backend_state.get_legacy_state())


# POST 接口：按照api更新模块数据
@app.post("/api/windows/update")
async def update_window(request: Request):
    data = await request.json()
    args = data.get("args")
    kwargs = data.get("kwargs")
    program.env_event(args, kwargs)
    backend_state.update_snapshot()
    await backend_state.broadcast_update()

# 新式窗口配置管理接口
@app.get("/api/windows/config")
async def get_window_configs():
    """获取窗口配置列表"""
    return JSONResponse(content={
        "windows": [config.dict() for config in backend_state.window_configs]
    })


@app.post("/api/windows/config")
async def update_window_configs(request: Request):
    """更新窗口配置"""
    try:
        data = await request.json()
        new_configs = data.get("windows", [])

        # 验证配置
        validated_configs = []
        for config_data in new_configs:
            if not backend_state.validate_window_type(config_data.get("type", "")):
                return JSONResponse(
                    content={"message": f"无效的窗口类型: {config_data.get('type')}"},
                    status_code=400
                )

            # 创建窗口配置对象
            config = WindowConfig(
                WindowId=config_data.get("id", f"{config_data.get('type')}-{len(validated_configs)}"),
                windowType=config_data.get("type"),
                windowTitle=config_data.get("title", config_data.get('type')),
                description=config_data.get("description"),
                order=config_data.get("order", len(validated_configs)),
                windowTheme=config_data.get("color"),
                icon=config_data.get("icon")
            )
            validated_configs.append(config)

        # 更新配置
        backend_state.window_configs = validated_configs
        await backend_state.broadcast_update()

        return {"message": "Window configs updated successfully"}

    except Exception as e:
        return JSONResponse(
            content={"message": f"配置更新失败: {str(e)}"},
            status_code=500
        )


# SSE 接口（新式格式）
@app.get("/api/sse")
async def sse_endpoint():
    async def event_generator():
        # 新客户端连接时立即推送完整状态
        backend_state.update_snapshot()
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
class LLMPrompt(BaseModel):
    prompt: str

class LLMresponse(BaseModel):
    response:str

@app.post("/api/llm/setModel")
async def set_model(request: Request):
    body = await request.json()
    model_name = body.get("model")
    program.set_client_model(model_name)

@app.post("/api/llm/manual-response")
async def manual_response(manual_request: LLMresponse):
    response =manual_request.response
    print("手动接受回复")
    parsed_calls=program.apply_response(response)
    backend_state.update_snapshot()
    # 广播更新
    await backend_state.broadcast_update()
    return {
        "parsed_calls": parsed_calls
    }
@app.post("/api/llm/call")
async def call_llm(data: LLMPrompt):
    """LLM 调用接口"""
    prompt = data.prompt
    print("收到 LLM 调用请求！Prompt 内容前50字符：")
    print(prompt[:50])

    # 调用上下文程序
    result = program.run(use_cache=False)

    # 更新模块数据
    for key in backend_state.window_data:
        if key in result.get("snapshot", {}):
            backend_state.window_data[key] = result["snapshot"][key]

    # 广播更新
    await backend_state.broadcast_update()

    answer = f"这是模拟 LLM 的响应，收到的 prompt 长度: {len(prompt)}"
    print("finish a call")

    return {
        "answer": answer,
        "raw_response": result.get("raw_response", ""),
        "parsed_calls": result.get("parsed_calls", [])
    }


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
        "supported_window_types": ["kernel", "heap", "stack", "code", "text"]
    }


if __name__ == "__main__":
    import uvicorn

    print("启动新式后端服务器...")
    print("支持的窗口类型: kernel, heap, stack, code")
    print("SSE 端点: /api/sse")
    print("窗口配置管理: /api/windows/config")
    print("传统API兼容: /api/windows, /api/windows/update")

    uvicorn.run(app, host="0.0.0.0", port=3001)