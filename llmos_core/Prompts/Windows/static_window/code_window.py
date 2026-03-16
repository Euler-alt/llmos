import pathlib

from llmos_core.Prompts.Windows import BasePromptWindow
from llmos_core.Prompts.Windows.static_window.static_window import StaticPromptWindow
TEXT_DIR = pathlib.Path(__file__).parent
CODE_FILE = TEXT_DIR / 'code_description.md'

class CodePromptWindow(StaticPromptWindow):
    def __init__(self, window_title="Code", file_path=CODE_FILE):
        super().__init__(window_title=window_title, file_path=file_path)

    def export_state_prompt(self) ->str:
        return self.content
