from enum import Enum
from .BaseWindow import BasePromptWindow, NullSystemWindow

# 导入必要的底层实现类，以确保它们在被调用前注册到 BasePromptWindow
from  .static_window import KernelPromptWindow,CodePromptWindow
from  .stack_window import StackPromptWindow,FlowStackPromptWindow
from  .heap_window import HeapPromptWindow
from  .system_window import SystemPromptWindow

from  .chat_window import ChatWindow,AsyChatPromptWindow
from  .ALFworldWindow import ALFworldWindow
from  .think_window import ThinkWindow

class PromptWindow(Enum):
    KernelPromptWindow = 'kernel'
    CodePromptWindow = 'code'

    StackPromptWindow = 'stack'
    FlowStackPromptWindow = 'flowStack'

    HeapPromptWindow = 'heap'
    SystemPromptWindow = 'system'

    ChatPromptWindow = 'ChatWindow'
    ALFWorldWindow = 'alfworld'
    AsyChatPromptWindow = 'AsyChatPromptWindow'
    ThinkingPromptWindow = 'think_window'
    
    NullWindow = 'NullWindow'

    def __str__(self):
        """让 Enum 成员被 str() 转换时，返回其内部的字符串值"""
        return self.value

    def create(self, **kwargs):
        """通过 PromptWindow.MEMBER.create() 方式创建窗口实例"""
        cls = _WINDOW_MAPPING.get(self)
        if not cls:
            raise ValueError(f"Window class for {self} not found in mapping.")
        
        # 自动根据枚举成员名称设置标题
        if 'window_title' not in kwargs:
            kwargs['window_title'] = self.name
            
        return cls(**kwargs)

    @classmethod
    def from_name(cls, name, **kwargs):
        """
        统一的窗口创建入口。
        接受字符串或 Enum 成员作为输入。
        """
        window_cls = _get_window_class(name)
        if not window_cls:
            raise ValueError(f"Window '{name}' not found in registry.")
        
        # 确定 window_title
        if isinstance(name, cls):
            window_title = name.name
        else:
            window_title = str(name)
            
        if 'window_title' not in kwargs:
            kwargs['window_title'] = window_title
            
        return window_cls(**kwargs)

# 建立 Enum 到 类的映射表
_WINDOW_MAPPING = {
    PromptWindow.KernelPromptWindow: KernelPromptWindow,
    PromptWindow.CodePromptWindow: CodePromptWindow,
    PromptWindow.StackPromptWindow: StackPromptWindow,
    PromptWindow.FlowStackPromptWindow: FlowStackPromptWindow,
    PromptWindow.HeapPromptWindow: HeapPromptWindow,
    PromptWindow.SystemPromptWindow: SystemPromptWindow,
    PromptWindow.ChatPromptWindow: ChatWindow,
    PromptWindow.ALFWorldWindow: ALFworldWindow,
    PromptWindow.AsyChatPromptWindow: AsyChatPromptWindow,
    PromptWindow.ThinkingPromptWindow: ThinkWindow,
    PromptWindow.NullWindow: NullSystemWindow,
}

# 辅助函数：根据名称（Enum 或 字符串）获取类
def _get_window_class(name):
    if isinstance(name, PromptWindow):
        return _WINDOW_MAPPING.get(name)
    
    if isinstance(name, str):
        # 尝试通过 value 匹配 Enum
        for member in PromptWindow:
            if member.value == name:
                return _WINDOW_MAPPING.get(member)
        # 尝试通过 name 匹配 Enum
        for member in PromptWindow:
            if member.name == name:
                return _WINDOW_MAPPING.get(member)
                
    return None

# 辅助函数：根据类或实例获取其注册的类型字符串
def get_window_type(window_obj_or_cls):
    """根据类或实例获取其注册的类型字符串"""
    cls = window_obj_or_cls if isinstance(window_obj_or_cls, type) else window_obj_or_cls.__class__
    
    for member, mapped_cls in _WINDOW_MAPPING.items():
        if mapped_cls == cls:
            return member.value
    return "text" # 默认 fallback