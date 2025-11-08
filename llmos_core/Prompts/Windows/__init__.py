# 导入必要的底层实现类，以确保它们在被调用前注册到 BasePromptWindow
from  .BaseWindow.BaseWindow import BasePromptWindow
from  .static_window import KernelPromptWindow,CodePromptWindow
from  .stack_window import stack_window,flowStackWindow
from  .heap_window import heap_window
from  .system_window import SystemPromptWindow

from  .chat_window import ChatWindow,AsyChatPromptWindow
from  .ALFworldWindow import ALFworldWindow
from  .think_window import ThinkWindow

from enum import Enum


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

    # 关键修改：重写 __str__
    def __str__(self):
        """让 Enum 成员被 str() 转换时，返回其内部的字符串值"""
        return self.value

    # 新增：作为 Enum 成员的辅助创建方法
    def create(self, **kwargs):
        """允许通过 PromptWindow.MEMBER.create() 方式创建"""
        # 直接调用底层的 from_name，并传递自身（Enum 成员）
        return BasePromptWindow.from_name(self, **kwargs)

    # 核心目标：作为统一的工厂入口
    @classmethod
    def from_name(cls, name, **kwargs):
        """
        统一的窗口创建入口。
        接受字符串或 Enum 成员作为输入。
        """
        # 1. 检查输入是否是自身的 Enum 成员
        if isinstance(name, cls):
            # 如果是 Enum 成员，直接传递给底层方法
            final_name = name

        # 2. 检查输入是否是字符串
        elif isinstance(name, str):
            # 如果是字符串，尝试将其解析为 Enum 成员
            # 注意：这里我们使用 .value 来匹配，而非 .name
            try:
                final_name = cls(name)  # cls('stack') 会返回 PromptWindow.StackPromptWindow
            except ValueError:
                # 如果字符串无效，则直接使用字符串（让 BasePromptWindow 去抛出未注册的错误）
                final_name = name
        else:
            final_name = name  # 保持其他类型不变

        # 转发给底层的 BasePromptWindow.from_name
        return BasePromptWindow.from_name(final_name, **kwargs)