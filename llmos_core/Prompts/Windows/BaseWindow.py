from abc import ABC, abstractmethod


class BasePromptWindow(ABC):

    def __init__(self):
        self.handlers = {}

    @abstractmethod
    def forward(self, *args, **kwargs):
        """根据当前状态，将提示词内容序列化为可用的字符串。"""
        return ""

    def handle_call(self, module_call:str, *args, **kwargs):
        """更新提示词模块的内容（比如由 LLM 生成的新规则）。"""
        if module_call in self.handlers:
            return self.handlers[module_call](*args, **kwargs)
        else:
            raise NotImplementedError(f"Handler for {module_call} not found in {self.__class__.__name__}")

    def export_meta_prompt(self)->str:
        return ""

    def export_state_prompt(self)->str:
        return ""

    def export_handlers(self):
        return {}