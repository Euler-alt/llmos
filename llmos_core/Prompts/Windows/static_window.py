from shellingham.nt import kernel32

from .BaseWindow import BasePromptWindow
from pathlib import Path

class StaticPromptWindow(BasePromptWindow):

    def __init__(self, window_name="",file_path=None):
        super().__init__(window_name=window_name)
        self.file_path = file_path or Path(__file__).parent / 'texts' / 'kernel_description.json'
        with open(self.file_path) as f:
            self.content = f.read()

    def load(self):
        with open(self.file_path, 'r', encoding='utf-8') as f:
            self.content = f.read()

    def forward(self, *args, **kwargs):
        if self.content is None:
            self.load()
        return self.content

    def export_handlers(self):
        return None

# 示例：一个具体的提示词模块实现
@BasePromptWindow.register('kernel','Kernel')
class KernelPromptModule(StaticPromptWindow):
    def __init__(self, window_name="Kernel",file_path=None):
        super().__init__(window_name=window_name,file_path=file_path)

    def export_meta_prompt(self) ->str:
        return self.content

@BasePromptWindow.register('code','Code')
class CodePromptModule(StaticPromptWindow):
    def __init__(self, window_name="Code",file_path=None):
        super().__init__(window_name=window_name,file_path=file_path)

    def export_state_prompt(self) ->str:
        return self.content