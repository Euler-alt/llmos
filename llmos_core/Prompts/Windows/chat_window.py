from BaseWindow import BasePromptWindow
from pathlib import Path
class ChatWindow(BasePromptWindow):
    def __init__(self,code_file=None):
        super().__init__()
        default_path = Path(__file__).parent / 'texts' / 'user_instruction.json'
        self.code_file = code_file if code_file else default_path
        with open(self.code_file,'r') as f:
            self.meta_prompt = f.read()
        self.prompt = ''

    def export_meta_prompt(self):
        return f"\n{self.meta_prompt}"

    def export_state_prompt(self):
        if self.prompt == '':
            return '\nNO USER instruction'
        else:
            return f"\n{self.prompt}"

    def forward(self):
        return f"{self.export_meta_prompt()}{self.export_state_prompt()}"

    def handle_call(self, module_call:str, *args, **kwargs):
        pass

    def export_handlers(self):
        pass