from .BaseModules import BasePromptModule
from .heap_module import HeapPromptModule
from .stack_module import StackPromptModule
from .static_module import KernelPromptModule,CodePromptModule

class SystemPromptModule(BasePromptModule):

    def __init__(self, kernel_file=None,heap_file=None,stack_file=None,code_file=None):
        super().__init__()
        self.kernelModule = KernelPromptModule(kernel_file)
        self.heapModule = HeapPromptModule(heap_file)
        self.stackModule = StackPromptModule(stack_file)
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