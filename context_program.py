from llmos_core.Prompts import PromptMainBoard,parse_response
import openai
import json

async def call_openai_api(prompt: str) -> str:
    # 假设你用 gpt-4o-mini
    import openai
    client = openai.AsyncOpenAI(api_key="YOUR_KEY")
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return resp.choices[0].message.content

class ContextProgram:
    def __init__(self):
        self.promptMainBoard = PromptMainBoard()

    async def run(self):
        full_prompt = self.promptMainBoard.assemble_prompt()
        response = await call_openai_api(full_prompt)
        # 3. 解析结果并更新内存
        try:
            syscall = json.loads(response)
            result = parse_response(syscall)
            call_type = result["call_type"]
            func_name = result["func_name"]
            kwargs = result["kwargs"]
            if call_type.lower() == "prompt":
                self.promptMainBoard.handle_call(func_name,**kwargs)
            return self.promptMainBoard.get_snap_shot()
        except Exception as e:
            print("解析错误:", e, "原始输出:", response)
            return {

            }
