from abc import ABC, abstractmethod


class BasePromptWindow(ABC):
    registered_windows = {}
    def __init__(self, window_name=""):
        self.handlers = {}
        self.window_name = window_name

    @abstractmethod
    def forward(self, *args, **kwargs):
        """根据当前状态，将提示词内容序列化为可用的字符串。"""
        return ""

    @classmethod
    def register(cls, *window_names):
        def decorator(subclass):
            for name in window_names:
                # 无论是字符串还是 Enum 成员，str(name) 都能得到所需的字符串键
                normalized_name = str(name)
                cls.registered_windows[normalized_name] = subclass
            return subclass
        return decorator

    @classmethod
    def from_name(cls, name, **kwargs):
        normalized_name = str(name)
        if normalized_name not in cls.registered_windows:
            raise ValueError(f"Window '{normalized_name}' not registered.")
        return cls.registered_windows[normalized_name](**kwargs)

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

    def get_divide_snapshot(self)->dict[str,dict[str,str]]:
        return {
            self.window_name:{
                "meta":self.export_meta_prompt(),
                "state":self.export_state_prompt(),
            }
        }

    def get_snapshot(self)->dict[str,str]:
        return {
            self.window_name:self.forward()
        }