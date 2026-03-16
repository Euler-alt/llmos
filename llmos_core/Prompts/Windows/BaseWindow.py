from abc import ABC, abstractmethod
from typing import List, Dict, Any, Callable
from llmos_core.schema import WindowSnapshot, ToolDefinition


class BasePromptWindow(ABC):
    """
    BasePromptWindow
    -----------------
    所有提示词窗口（模块）的抽象基类。

    ✅ 每个窗口负责维护自身的提示词片段，以及内部状态。
    ✅ 支持将自身注册到一个全局注册表（registered_windows），便于通过名称创建实例。
    ✅ 提供 forward() 来序列化本模块的最终提示词文本。
    ✅ 提供 handler 分发机制，使模型的 function call 能调用该模块的能力。
    """

    def __init__(self, window_title=""):
        """
        :param window_title: 窗口标题，对应前端展示的名称
        """
        self.handlers: Dict[str, Callable] = {}  # 各模块暴露给 LLM 的处理方法，例如 function call 的入口
        if window_title is None or window_title == "":
            window_title = "undefined_window"
        self.window_title = window_title

    def forward(self, *args, **kwargs) -> str:
        """
        将当前模块的提示内容序列化为字符串。
        默认行为是输出 meta prompt + state prompt 的组合。
        """
        meta_prompt = self.export_meta_prompt()
        state_prompt = self.export_state_prompt()

        # 仅当 meta 或 state 有内容时才生成窗口
        if not meta_prompt and not state_prompt:
            return ""

        return (f"\n"
                f"<WINDOW START: {self.window_title}>\n"
                f"META:\n"
                f"{meta_prompt}\n"
                f"STATE:\n"
                f"{state_prompt}\n"
                f"<WINDOW END: {self.window_title}>\n")

    def handle_call(self, module_call: str, *args, **kwargs):
        """
        模型/系统调用接口。
        当大模型触发工具调用（function call）时，
        名称 module_call 用来查找该窗口是否提供对应的处理方法。

        :param module_call: 函数名（字符串），应注册在 self.handlers 字典中
        :return: 调用处理结果（通常是 Any，用于返回给模型）
        """
        if module_call in self.handlers:
            return self.handlers[module_call](*args, **kwargs)
        else:
            raise NotImplementedError(
                f"Handler for {module_call} not found in {self.__class__.__name__}"
            )

    def get_tool_definitions(self) -> List[ToolDefinition]:
        """
        返回该窗口提供的所有外部工具定义，用于 LLM API 的 tools 参数。
        默认不提供任何工具。仅需要调用外部环境的窗口需要重写此方法。
        """
        return []

    def export_meta_prompt(self) -> str:
        """
        返回模块的“元提示词”部分，用于描述模块目的、功能、使用规范等。
        对于内部调用（JSON Syscall），函数定义应在此处说明。
        可以为空；子类可覆盖。
        """
        return ""

    def export_state_prompt(self) -> str:
        """
        返回模块的“状态提示词”部分，用于描述当前内部状态。
        例如记忆模块会输出当前记忆、任务模块输出当前计划等。
        可以为空；子类可覆盖。
        """
        return ""

    def export_handlers(self) -> Dict[str, Callable]:
        """
        返回该窗口提供的 function call 可调用表。
        默认返回 self.handlers。
        """
        return self.handlers

    def get_divided_snapshot(self) -> WindowSnapshot:
        """
        拿到更结构化的快照：meta 与 state 分别展示。
        用于可视化、存储、调试或 Web UI 显示。
        """
        # 将 tool definitions 格式化为 meta 描述
        tools = self.get_tool_definitions()
        meta_desc = "\n".join([f"- {t.name}: {t.description}" for t in tools]) if tools else self.export_meta_prompt()
        return WindowSnapshot(
            meta=meta_desc,
            state=self.export_state_prompt(),
        )

    def get_snapshot(self) -> Dict[str, str]:
        """
        返回合并后的提示词快照（单一字符串形式）。
        一般用于展示最终拼接内容。

        :return: { "window_title": "full_forward_text" }
        """
        return {
            self.window_title: self.forward()
        }

class NullSystemWindow(BasePromptWindow):
    def __init__(self, window_title="null_window"):
        super().__init__(window_title=window_title)

    def forward(self, *args, **kwargs) -> str:
        return ""  # 明确返回空内容

    def export_meta_prompt(self) -> str:
        return ""

    def export_state_prompt(self) -> str:
        return ""

    def get_divided_snapshot(self) -> WindowSnapshot:
        return WindowSnapshot(meta="", state="")

