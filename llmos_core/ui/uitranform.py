from llmos_core.Program import BaseProgram
from llmos_core.Prompts.Windows import PromptWindow
from llmos_core.ui import WindowConfig

WINDOW_CONFIGS = {
    # 精确匹配的窗口
    PromptWindow.KernelPromptWindow.value: {"ui_type": "KernelWindow", "theme": "blue"},
    PromptWindow.CodePromptWindow.value: {"ui_type": "CodeWindow", "theme": "purple"},
    PromptWindow.ChatPromptWindow.value: {"ui_type": "ChatWindow", "theme": "orange"},
    PromptWindow.FlowStackPromptWindow.value : {"ui_type": "StackWindow", "theme": "yellow"},
    PromptWindow.HeapPromptWindow.value: {"ui_type": "HeapWindow", "theme": "green"},
    PromptWindow.AsyChatPromptWindow.value: {"ui_type": "ChatWindow", "theme": "blue"},
    PromptWindow.StackPromptWindow.value: {"ui_type": "StackWindow", "theme": "purple"},
    # 业务逻辑不同，但 UI 组件共用的窗口
    PromptWindow.ALFWorldWindow.value: {"ui_type": "TextWindow", "theme": "cyan"},  # 业务是ALF，UI用text
    PromptWindow.ThinkingPromptWindow.value: {"ui_type": "TextWindow", "theme": "gray"},  # 业务是思考，UI用text
    PromptWindow.SystemPromptWindow.value: {"ui_type": "TextWindow", "theme": "red"},  # 系统窗口借用kernel UI

    # 兜底配置
    "DEFAULT": {"ui_type": "TextWindow", "theme": "blue"}
}

# 2. 自动检查覆盖率
def check_coverage():
    for member in PromptWindow:
        if member.value not in WINDOW_CONFIGS and member != PromptWindow.NullWindow:
            print(f"⚠️ 警告: {member} 未配置 UI 属性")

check_coverage()


def update_backend_state_from_program(program:BaseProgram=None):
    if program is None: return []

    ui_configs = program.get_ui_configs()

    for config_item in ui_configs:
        # 获取当前的 Enum 成员
        w_enum = config_item.windowType

        # 从注册表获取 UI 映射
        # 如果 Enum 没在 WINDOW_CONFIGS 里定义，则使用 DEFAULT
        config = WINDOW_CONFIGS.get(w_enum, WINDOW_CONFIGS["DEFAULT"])

        # --- 关键步骤：重写发往前端的字段 ---
        # 1. 告诉前端用哪个组件 (chat/text/kernel...)
        config_item.windowType = config['ui_type']

        # 2. 注入后端定义的皮肤颜色
        config_item.windowTheme = config['theme']
    return ui_configs