from abc import ABC, abstractmethod

from abc import ABC, abstractmethod


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

    # 用于存储已注册的窗口名 -> 窗口类
    registered_windows = {}

    def __init__(self, window_name=""):
        """
        :param window_name: 模块名称，用于识别模块、打印状态或从快照中区分
        """
        self.handlers = {}  # 各模块暴露给 LLM 的处理方法，例如 function call 的入口
        if window_name is None or window_name == "":
            window_name = "undefined_windowName"
        self.window_name = window_name

    @abstractmethod
    def forward(self, *args, **kwargs):
        """
        将当前模块的提示内容序列化为字符串。
        子类需要实现自己的提示词输出逻辑。
        默认行为是输出 meta prompt + state prompt 的组合。

        :return: str，最终用于拼接到大模型输入的提示词片段
        """
        return (f"\n"
                f"<WINDOW START: {self.window_name}>\n"
                f"META:\n"
                f"{self.export_meta_prompt()}\n"
                f"STATE:\n"
                f"{self.export_state_prompt()}]\n"
                f"<WINDOW START: {self.window_name}>\n")

    @classmethod
    def register(cls, *window_names):
        """
        装饰器：将子类绑定到指定窗口名。
        使用示例：

            @BasePromptWindow.register("memory", "记忆模块")
            class MemoryWindow(BasePromptWindow):
                ...

        :param window_names: 一个或多个用于标识该窗口的名称（字符串或 Enum）
        :return: 装饰器函数
        """

        def decorator(subclass):
            for name in window_names:
                normalized_name = str(name)  # 支持 Enum / 字符串统一处理
                cls.registered_windows[normalized_name] = subclass
            return subclass

        return decorator

    @classmethod
    def from_name(cls, name, **kwargs):
        """
        根据名称实例化已注册的窗口类。
        允许动态构建模块，例如从配置或 JSON 加载。

        :param name: 注册过的窗口名称（字符串或 Enum）
        :param kwargs: 传给子类构造函数的参数
        :return: 对应窗口类的实例
        """
        normalized_name = str(name)
        if normalized_name not in cls.registered_windows:
            raise ValueError(f"Window '{normalized_name}' not registered.")
        return cls.registered_windows[normalized_name](**kwargs)

    def handle_call(self, module_call: str, *args, **kwargs):
        """
        模型/系统调用接口。
        当大模型触发工具调用（function call）时，
        名称 module_call 用来查找该窗口是否提供对应的处理方法。

        :param module_call: 函数名（字符串），应注册在 self.handlers 字典中
        :return: 调用处理结果（通常是dict，用于返回给模型）
        """
        if module_call in self.handlers:
            return self.handlers[module_call](*args, **kwargs)
        else:
            raise NotImplementedError(
                f"Handler for {module_call} not found in {self.__class__.__name__}"
            )

    def export_meta_prompt(self) -> str:
        """
        返回模块的“元提示词”部分，用于描述模块目的、功能、使用规范等。
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

    def export_handlers(self):
        """
        返回该窗口提供的 function call 可调用表。
        默认空字典，子类需要返回类似：
            {
                "update_memory": self.update_memory,
                "reset": self.reset_state
            }
        """
        return {}

    def get_divided_snapshot(self) -> dict[str, dict[str, str]]:
        """
        拿到更结构化的快照：meta 与 state 分别展示。
        用于可视化、存储、调试或 Web UI 显示。

        :return: {
            "window_name": {
                "meta": "...",
                "state": "..."
            }
        }
        """
        return {
            self.window_name: {
                "meta": self.export_meta_prompt(),
                "state": self.export_state_prompt(),
            }
        }

    def get_snapshot(self) -> dict[str, str]:
        """
        返回合并后的提示词快照（单一字符串形式）。
        一般用于展示最终拼接内容。

        :return: { "window_name": "full_forward_text" }
        """
        return {
            self.window_name: self.forward()
        }

@BasePromptWindow.register("NullWindow")
class NullSystemWindow(BasePromptWindow):
    def __init__(self):
        super().__init__(window_name="null_window")

    def forward(self):
        return super().forward()  # 明确返回空内容

    def export_meta_prompt(self):
        return ""

    def export_state_prompt(self):
        return ""

    def get_divided_snapshot(self):
        return {
            self.window_name: {
                "meta": "",
                "state": "",
            }
        }

