from llmos_core.Prompts import PromptMainBoard,parse_response
from openai import OpenAI
import yaml
import os
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

deepseek_key = config["deepseek"]["key"]

def call_openai_api(prompt: str) -> str:
    client = OpenAI(api_key=deepseek_key, base_url="https://api.deepseek.com")
    resp = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        stream = False
    )
    return resp.choices[0].message.content

class ContextProgram:
    def __init__(self,code_file=None):
        self.promptMainBoard = PromptMainBoard(code_file=code_file)

    def run(self):
        full_prompt = self.promptMainBoard.assemble_prompt()
        response = call_openai_api(full_prompt)
        # 3. 解析结果并更新内存
        try:
            result = parse_response(response)
            for call in result:
                call_type = call["call_type"]
                func_name = call["func_name"]
                kwargs = call["kwargs"]
                if call_type.lower() == "prompt":
                    self.promptMainBoard.handle_call(func_name,**kwargs)
            return self.promptMainBoard.get_snap_shot()
        except Exception as e:
            print("解析错误:", e, "原始输出:", response)
            return {

            }
