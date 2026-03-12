from abc import ABC, abstractmethod

from llmos_core.Prompts.Windows import BasePromptWindow
from llmos_core.Prompts.PromptMainBoard import PromptMainBoard,parse_response
from llmos_core.Prompts.Windows.BaseWindow import NullSystemWindow


class BaseProgram(ABC):
    def __init__(self, windows=None,system_windows=None):
        if windows is None:
            windows = []
        if system_windows is None:
            system_windows = NullSystemWindow()
        self.promptMainBoard = PromptMainBoard()
        self.promptMainBoard.register_windows(windows=windows,system_windows=system_windows)
        self.llm_client = None

    @abstractmethod
    def run(self):
        pass

    def env_event(self,*args, **kwargs):
        self.promptMainBoard.handle_call(*args,**kwargs)



