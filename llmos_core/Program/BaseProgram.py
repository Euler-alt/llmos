from abc import ABC, abstractmethod
from typing import List, Any
from llmos_core.schema import ProgramRunResult
from llmos_core.Prompts.PromptMainBoard import PromptMainBoard, parse_response
from llmos_core.Prompts.Windows.BaseWindow import NullSystemWindow
from llmos_core.ui import WindowConfig


class BaseProgram(ABC):
    def __init__(self, windows=None,system_windows=None):
        if windows is None:
            windows = []
        if system_windows is None:
            system_windows = NullSystemWindow()
        self.promptMainBoard = PromptMainBoard()
        self.promptMainBoard.register_windows(user_windows=windows, system_windows=system_windows)
        self.llm_client = None

    @abstractmethod
    def run(self, *args, **kwargs) -> ProgramRunResult:
        pass

    def env_event(self,*args, **kwargs):
        self.promptMainBoard.handle_call(*args,**kwargs)

    def get_ui_configs(self)->List[WindowConfig]:
        return self.promptMainBoard.get_ui_configs()

    def get_window_snapshots(self):
        return self.promptMainBoard.get_divided_snapshot()

