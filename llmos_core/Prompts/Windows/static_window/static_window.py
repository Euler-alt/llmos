import pathlib

from llmos_core.Prompts.Windows.BaseWindow import BasePromptWindow

TEXT_DIR = pathlib.Path(__file__).parent
KERNEL_FILE = TEXT_DIR / 'kernel_description.md'

class StaticPromptWindow(BasePromptWindow):

    def __init__(self, window_title="", file_path=None):
        super().__init__(window_title=window_title)
        self.file_path = file_path or KERNEL_FILE
        with open(self.file_path) as f:
            self.content = f.read()

    def load(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.content = f.read()

    def export_state_prompt(self) -> str:
        """对于静态窗口，其内容作为状态（规则/说明）始终保留在 system prompt 中"""
        return self.content

    def forward(self, *args, **kwargs):
        if self.content is None:
            self.load()
        return super().forward()

    def export_handlers(self):
        return {}

