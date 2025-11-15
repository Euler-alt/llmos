# 导入必要的底层实现类，以确保它们在被调用前注册到 BasePromptWindow
from llmos_core.Prompts.Windows.BaseWindow import BasePromptWindow
from  .static_window import KernelPromptWindow,CodePromptWindow
from  .stack_window import stack_window,FlowStackPromptWindow
from  .heap_window import heap_window
from  .system_window import SystemPromptWindow

from  .chat_window import ChatWindow,AsyChatPromptWindow
from  .ALFworldWindow import ALFworldWindow
from  .think_window import ThinkWindow

from .Prompt_register import PromptWindow


