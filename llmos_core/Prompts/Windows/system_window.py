from .BaseWindow import BasePromptWindow
from .heap_window import HeapPromptWindow
from .stack_window import StackPromptWindow
from .static_window import KernelPromptModule,CodePromptModule

class SystemPromptWindow(BasePromptWindow):

    def __init__(self, kernel_file=None,heap_file=None,stack_file=None,code_file=None):
        super().__init__()
        self.kernelModule = KernelPromptModule(kernel_file)
        self.heapModule = HeapPromptWindow(heap_file)
        self.stackModule = StackPromptWindow(stack_file)
        self.codeModule = CodePromptModule(code_file)
        self.Modules = [self.kernelModule, self.heapModule, self.stackModule,self.codeModule]
        for module in self.Modules:
            self.handlers.update(module.export_handlers() or {})

    def forward(self, *args, **kwargs):
        desc =''
        for module in self.Modules:
            desc += module.forward(*args, **kwargs)
        return desc

    def export_handlers(self):
        handlers = {}
        for module in self.Modules:
            handlers.update(module.export_handlers() or {})
        return handlers

    def get_descriptions(self):
        return {
            "stack": self.stackModule.export_meta_prompt(),
            "heap": self.heapModule.export_meta_prompt(),
            "kernel": self.kernelModule.export_meta_prompt(),
        }

    def get_state_snapshot(self):
        return {
            "stack": self.stackModule.export_state_prompt(),
            "heap": self.heapModule.export_state_prompt(),
            "code": self.codeModule.export_state_prompt(),
        }

    def get_divide_snapshot(self):
        return {
            "stack": {
                "meta": self.stackModule.export_meta_prompt(),
                "state": self.stackModule.export_state_prompt(),
            },
            "heap": {
                "meta": self.heapModule.export_meta_prompt(),
                "state": self.heapModule.export_state_prompt(),
            },
            "code": {
                "meta": self.codeModule.export_meta_prompt(),
                "state": self.codeModule.export_state_prompt(),
            },
            "kernel": {
                "meta": self.kernelModule.export_meta_prompt(),
                "state": self.kernelModule.export_state_prompt(),
            },
        }

    def get_snapshot(self):
        return {
            "stack": str(self.stackModule.forward()),
            "heap": str(self.heapModule.forward()),
            "code": self.codeModule.forward(),
            "kernel": self.kernelModule.forward(),
        }