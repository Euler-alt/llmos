from .BaseModules import BasePromptModule
from pathlib import Path

class StaticPromptModule(BasePromptModule):
    def __init__(self, file_path=None):
        super().__init__()
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
class KernelPromptModule(StaticPromptModule):
    def __init__(self, file_path=None):
        super().__init__(file_path)

class CodePromptModule(StaticPromptModule):
    def __init__(self, file_path=None):
        super().__init__(file_path)