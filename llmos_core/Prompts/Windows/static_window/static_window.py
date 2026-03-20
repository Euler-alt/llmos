import pathlib

from llmos_core.Prompts.Windows.BaseWindow import BasePromptWindow

TEXT_DIR = pathlib.Path(__file__).parent
KERNEL_FILE = TEXT_DIR / 'kernel_description.md'

class StaticPromptWindow(BasePromptWindow):

    def __init__(self, window_title="", file_path=None):
        self.file_path = file_path or KERNEL_FILE
        super().__init__(window_title=window_title, meta_file=self.file_path)




