from abc import ABC, abstractmethod

from llmos_core.Prompts.Windows import BasePromptWindow
from llmos_core.Prompts.PromptMainBoard import PromptMainBoard,parse_response

class BaseProgram(ABC):
    def __init__(self, windows=None):
        if windows is None:
            windows = []
        self.promptMainBoard = PromptMainBoard()
        self.promptMainBoard.register_windows(windows)
        self.llm_client = None

    @abstractmethod
    def run(self):
        pass

    def env_event(self,*args, **kwargs):
        self.promptMainBoard.handle_call(*args,**kwargs)



