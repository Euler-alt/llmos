import asyncio
import json
from typing import Dict, List
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import random
from pathlib import Path
from llmos_core.Program.context_program import ContextProgram
# 初始化 FastAPI 应用
app = FastAPI()

# 允许所有来源的跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟数据库中的数据
module_data: Dict[str, str] = {
    "kernel": "系统规则和工作流：\n- 始终优先调用工具函数来完成任务。\n- 使用栈模块管理多步任务。",
    "heap": "持久化存储：\n- 当前用户：Alex\n- 任务目标：查找最新的AI新闻",
    "stack": "任务执行：\n- [step 1] 调用搜索工具\n- [step 2] 汇总搜索结果",
    "code": "可执行代码: \n"
}

# 用于存储所有 SSE 客户端的引用，使用异步队列实现
clients: List[asyncio.Queue] = []


# Pydantic 模型，用于验证 POST 请求的输入
class UpdateModule(BaseModel):
    moduleName: str
    newData: str


# 新增一个异步任务来模拟后台程序的运行
async def simulate_ai_process():
    context_code = Path(__file__).parent / 'tests'/'prompt_code' / 'engage_agent.txt'
    program = ContextProgram(context_code)
    while True:
        await asyncio.sleep(random.uniform(1, 1.5))  # 随机等待

        data = program.run()
        for key in module_data:
            if key in data:
                module_data[key] = data[key]
        # 将最新的数据推送到所有客户端
        await send_sse_update(module_data)


# 在应用启动时创建并运行后台任务
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(simulate_ai_process())
    print("后台模拟程序已启动。")


# GET 接口：用于前端获取所有模块数据
@app.get("/api/modules")
async def get_modules():
    return module_data


# POST 接口：用于前端更新特定模块数据 (此功能仍然保留)
@app.post("/api/modules/update")
async def update_module(update_data: UpdateModule):
    module_name = update_data.moduleName
    new_data = update_data.newData

    if module_name in module_data:
        module_data[module_name] = new_data

        # 数据更新后，立即通过 SSE 推送给所有客户端
        await send_sse_update(module_data)

        return {"message": "Data updated successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid module name")


# 新增函数：向所有客户端的队列中推送数据
async def send_sse_update(data: Dict):
    # 核心改动：将字典转换为 JSON 字符串，确保前端能正确解析
    json_data = json.dumps(data)
    payload = f"data: {json_data}\n\n"
    for client_queue in clients:
        await client_queue.put(payload)
    print('Pushed update to all connected clients.')


# 新增 SSE 接口，使用 StreamingResponse 和异步生成器
@app.get("/api/sse")
async def sse_endpoint(request: Request):
    # 为新连接的客户端创建一个独立的队列
    client_queue = asyncio.Queue()
    clients.append(client_queue)
    print('New SSE client connected.')

    # 立即发送一次完整的数据，确保新连接的客户端能获取当前状态
    initial_data = json.dumps(module_data)
    await client_queue.put(f"data: {initial_data}\n\n")

    async def event_generator():
        try:
            while True:
                # 从队列中获取数据并发送
                data = await client_queue.get()
                yield data
        except asyncio.CancelledError:
            # 客户端断开连接时，从列表中移除
            clients.remove(client_queue)
            print('SSE client disconnected.')

    # 返回流式响应
    return StreamingResponse(event_generator(), media_type="text/event-stream")


if __name__ == "__main__":
    import uvicorn

    # 要运行此文件，请在终端中执行: uvicorn main:app --reload
    uvicorn.run(app, host="0.0.0.0", port=3001)

