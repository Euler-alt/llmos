from llmos_core.config_manager import ConfigManager
from openai import OpenAI
from pathlib import Path
import asyncio

class LLMClient:
    def __init__(self, model_name: str=None, specific_api_config_path=None):
        """
        初始化大模型客户端。会加载配置并绑定指定模型的密钥和 API 地址。
        """
        api_config_path = Path(specific_api_config_path).parent if specific_api_config_path else Path(__file__).parent / 'api_configure'
        config_manager = ConfigManager(api_config_path)
        config_name = specific_api_config_path.name if specific_api_config_path else "api_config.yaml"
        self.api_configs  = config_manager.load_yaml_config(config_name)

        if model_name is not None and not 'default':
            self.model_name = model_name
            if model_name not in self.api_configs:
                raise ValueError(f"模型 '{model_name}' 未在配置中注册")
        else:
            self.model_name = self.api_configs['default']['name']

        api_config = self.api_configs[self.model_name]
        self.api_key = api_config["api_key"]
        self.base_url = api_config["base_url"]

        # 初始化 OpenAI 兼容客户端
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(self, user_prompt: str, system_prompt: str = "", temperature=0.7, max_tokens=2048) -> str:
        """
        执行一次聊天调用，使用初始化时设定的模型与连接信息。
        """
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content


    async def achat(self, user_prompt: str, system_prompt: str = "", temperature=0.7,
             max_tokens=2048) -> str:
        """
        执行一次聊天调用，使用初始化时设定的模型与连接信息。
        """
        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content
