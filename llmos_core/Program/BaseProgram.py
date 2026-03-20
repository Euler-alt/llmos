from abc import ABC, abstractmethod
from typing import List, Any

from llmos_core.llmos_util import LLMClient
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
        self.llm_client = LLMClient()

    def set_model(self, model_name: str):
        if self.llm_client:
            self.llm_client.set_model(model_name)

    def get_available_models(self):
        if self.llm_client:
            return self.llm_client.get_available_models()
        return []

    @abstractmethod
    def run(self, *args, **kwargs) -> ProgramRunResult:
        pass

    def env_event(self, func_name, **kwargs):
        """
        处理来自环境或用户的事件调用。
        :param func_name: 处理函数名称 (str)
        :param kwargs: 调用参数
        """
        call = {
            "call_type": "event_call",
            "func_name": func_name,
            "kwargs": kwargs
        }
        return self.promptMainBoard.handle_call(call)

    def get_ui_configs(self)->List[WindowConfig]:
        return self.promptMainBoard.get_ui_configs()

    def get_window_snapshots(self):
        return self.promptMainBoard.get_divided_snapshot()

    def reset(self):
        """
        重置程序状态。基类默认清空所有窗口的状态。
        子类可以覆盖此方法以实现特定的重置逻辑（如环境重置）。
        """
        for window in self.promptMainBoard.user_windows + self.promptMainBoard.system_windows:
            if hasattr(window, 'reset'):
                window.reset()
            else:
                # 默认回退：尝试清除 state_prompt 相关的内部状态
                # 这里可以根据具体窗口实现来完善
                pass

