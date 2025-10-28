from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import asyncio
import json

from pathlib import Path
from pydantic import BaseModel

from llmos_core.Program.context_program import ContextProgram

app = FastAPI()

# 允许跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 可以指定前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
context_code = Path(__file__).parent / 'tests'/'prompt_code' / 'engage_agent.txt'
program = ContextProgram(context_code)
# 模拟数据库中的数据
module_data = {
    "kernel": "系统规则和工作流：\n- 始终优先调用工具函数来完成任务。\n- 使用栈模块管理多步任务。",
    "heap": "持久化存储：\n- 当前用户：Alex\n- 任务目标：查找最新的AI新闻",
    "stack": "任务执行栈：\n- [step 1] 调用搜索工具\n- [step 2] 汇总搜索结果",
    "code": "可执行代码: \n```python\ndef get_latest_news(topic):\n    # 调用外部API...\n    pass\n```"
}

# 用于存储 SSE 客户端队列
subscribers = []


# GET 接口：获取所有模块数据
@app.get("/api/modules")
async def get_modules():
    return JSONResponse(content=module_data)


# POST 接口：更新模块数据
@app.post("/api/modules/update")
async def update_module(request: Request):
    data = await request.json()
    module_name = data.get("moduleName")
    new_data = data.get("newData")

    if module_name in module_data:
        module_data[module_name] = new_data
        await send_sse_update(module_data)
        return {"message": "Data updated successfully"}
    else:
        return JSONResponse(content={"message": "Invalid module name"}, status_code=400)


# SSE 接口
@app.get("/api/sse")
async def sse_endpoint():
    async def event_generator():
        # 新客户端：立即推送一次全量数据
        yield f"data: {json.dumps(module_data, ensure_ascii=False)}\n\n"
        queue = asyncio.Queue()
        subscribers.append(queue)
        try:
            while True:
                data = await queue.get()
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        except asyncio.CancelledError:
            # 客户端断开时清理
            subscribers.remove(queue)
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
    prompt = data.prompt
    # 模拟调用大模型，实际可替换成你的 API
    print("收到 LLM 调用请求！Prompt 内容前50字符：")
    print(prompt[:50])  # 只打印前50个字符，避免太长
    result=program.run(use_cache=True)
    for key in module_data:
        if key in result["snapshot"]:
            module_data[key] = result["snapshot"][key]
    await send_sse_update(module_data)
    answer = f"这是模拟 LLM 的响应，收到的 prompt 长度: {len(prompt)}"
    print("finish a call")
    return {
        "answer": answer,
        "raw_response": result["raw_response"],
        "parsed_calls": result["parsed_calls"]
    }

if __name__ == "__main__":
    import uvicorn

    # 要运行此文件，请在终端中执行: uvicorn main:app --reload
    uvicorn.run(app, host="0.0.0.0", port=3001)