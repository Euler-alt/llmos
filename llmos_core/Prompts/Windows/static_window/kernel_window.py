import pathlib

from llmos_core.Prompts.Windows import BasePromptWindow
from llmos_core.Prompts.Windows.static_window.static_window import StaticPromptWindow

TEXT_DIR = pathlib.Path(__file__).parent
KERNEL_FILE = TEXT_DIR / 'kernel_description.md'

class KernelPromptWindow(StaticPromptWindow):
    def __init__(self, window_title="Kernel", file_path=KERNEL_FILE):
        super().__init__(window_title=window_title, file_path=file_path)

    def export_meta_prompt(self) ->str:
        return self.content
