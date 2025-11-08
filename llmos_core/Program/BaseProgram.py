from abc import ABC, abstractmethod

from llmos_core.Prompts.Windows import BasePromptWindow
from llmos_core.Prompts.PromptMainBoard import PromptMainBoard,parse_response
from llmos_core.Prompts.Windows.BaseWindow import NullSystemWindow


class BaseProgram(ABC):
    def __init__(self, windows=None,system_window=None):
        if windows is None:
            windows = []
        if system_window is None:
            system_window = NullSystemWindow()
        self.promptMainBoard = PromptMainBoard()
        self.promptMainBoard.register_windows(windows=windows,system_window=system_window)
        self.llm_client = None

    @abstractmethod
    def run(self):
        pass

    def env_event(self,*args, **kwargs):
        self.promptMainBoard.handle_call(*args,**kwargs)



