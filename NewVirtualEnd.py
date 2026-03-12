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
context_code = Path(__file__).parent / 'tests' / 'prompt_code' / 'engage_agent.txt'
program = ALFworldProgram()

# 新式后端状态管理
class WindowConfig(BaseModel):
    """窗口配置模型"""
    windowId: str
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
                windowId="kernel-1",
                windowType="kernel",
                windowTitle="Kernel",
                description="系统规则和工作流程",
                order=0,
                windowTheme="blue",
                icon="kernel"
            ),
            WindowConfig(
                windowId="heap-2",
                windowType="heap",
                windowTitle="Heap",
                description="持久化存储区域",
                order=1,
                windowTheme="green",
                icon="heap"
            ),
            WindowConfig(
                windowId="stack-3",
                windowType="stack",
                windowTitle="Stack",
                description="临时工作区域",
                order=2,
                windowTheme="yellow",
                icon="stack"
            ),
            WindowConfig(
                windowId="text-4",
                windowType="text",
                windowTitle="ALFWorld",
                description="alfworld信息",
                order=4,
                windowTheme="red",
                icon="code"
            )
        ]
        
        # 模块数据存储
        self.module_data: Dict[str, Any] = {
            "Kernel": {
                "meta": "系统核心规则与工作流配置",
                "state": {
                    "rules": ["始终优先调用工具函数", "使用栈模块管理多步任务"],
                    "status": "running"
                }
            },
            "Heap": {
                "meta": "持久化存储与上下文信息",
                "state": {
                    "current_user": "Alex",
                    "objective": "查找最新的AI新闻",
                    "last_sync": "2026-03-11 22:38"
                }
            },
            "Stack": {
                "meta": "任务执行栈控制",
                "state": {
                    "steps": [
                        {"id": 1, "task": "调用搜索工具", "status": "done"},
                        {"id": 2, "task": "汇总搜索结果", "status": "pending"}
                    ],
                    "depth": 2
                }
            },
            "ALFWorld": {
                "meta": "环境观察与交互文本",
                "state": {
                    "observation": "你正站在客厅中心，面前有一个茶几。",
                    "inventory": []
                }
            }
        }
        
        # SSE 客户端队列
        self.subscribers: List[asyncio.Queue] = []
    
    def validate_window_type(self, window_type: str) -> bool:
        """验证窗口类型是否有效（与前端注册表匹配）"""
        valid_types = {"kernel", "heap", "stack", "code","text"}
        return window_type in valid_types

    def get_full_state(self) -> Dict[str, Any]:
        """将数据直接嵌入到配置中，形成自包含的列表"""
        integrated_windows = []
        for config in self.window_configs:
            # 获取该窗口对应的业务数据
            data = self.module_data.get(config.windowTitle, {})

            # 这里的 dict() 转换后，直接把 data 塞进去
            window_item = config.dict()
            window_item["data"] = data  # 关键：数据跟配置走
            integrated_windows.append(window_item)

        return {
            "windows": integrated_windows
        }
    
    def get_legacy_state(self) -> Dict[str, Any]:
        """获取传统格式的状态数据（向后兼容）"""
        return self.module_data.copy()
    
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
@app.get("/api/modules")
async def get_modules():
    return JSONResponse(content=backend_state.get_legacy_state())

# POST 接口：更新模块数据
@app.post("/api/modules/update")
async def update_module(request: Request):
    data = await request.json()
    module_name = data.get("moduleName")
    new_data = data.get("newData")

    if module_name in backend_state.module_data:
        backend_state.module_data[module_name] = new_data
        await backend_state.broadcast_update()
        return {"message": "Data updated successfully"}
    else:
        return JSONResponse(content={"message": "Invalid module name"}, status_code=400)

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
                windowId=config_data.get("id", f"{config_data.get('type')}-{len(validated_configs)}"),
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

@app.post("/api/llm/call")
async def call_llm(data: LLMPrompt):
    """LLM 调用接口"""
    prompt = data.prompt
    print("收到 LLM 调用请求！Prompt 内容前50字符：")
    print(prompt[:50])
    
    # 调用上下文程序
    result = program.run(use_cache=True)
    
    # 更新模块数据
    for key in backend_state.module_data:
        if key in result.get("snapshot", {}):
            backend_state.module_data[key] = result["snapshot"][key]
    
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