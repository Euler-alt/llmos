from llmos_core.config_manager import ConfigManager
from openai import OpenAI
from pathlib import Path

class LLMClient:
    def __init__(self, model_name: str=None, specific_api_config_path=None):
        """
        初始化大模型客户端。会加载配置并绑定指定模型的密钥和 API 地址。
        """
        api_config_path = Path(specific_api_config_path).parent if specific_api_config_path else Path(__file__).parent / 'api_configure'
        config_manager = ConfigManager(api_config_path)
        config_name = specific_api_config_path.name if specific_api_config_path else "api_config.yaml"
        self.api_configs  = config_manager.load_yaml_config(config_name)
        self.model_name = None
        self.api_key = None
        self.base_url = None
        self.client = None

        self.set_model(model_name)

    def set_model(self, model_name: str):
        # 先设定默认
        self.model_name = self.api_configs['default']['name']

        # 如果指定模型有效则覆盖
        if model_name and model_name != "default" and model_name in self.api_configs:
            self.model_name = model_name

        api_config = self.api_configs[self.model_name]
        self.api_key = api_config["api_key"]
        self.base_url = api_config["base_url"]
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def chat(self, user_prompt: str='', system_prompt: str = "", temperature=1.5, max_tokens=2048) -> str:
        """
        执行一次聊天调用，使用初始化时设定的模型与连接信息。
        """
        response = self.client.chat.completions.create(
            model=self.model_name,
            frequency_penalty=1,
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
