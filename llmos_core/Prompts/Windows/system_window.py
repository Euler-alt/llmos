from .BaseWindow import BasePromptWindow
from .heap_window import HeapPromptWindow
from .stack_window import StackPromptWindow
from .static_window import KernelPromptModule,CodePromptModule

@BasePromptWindow.register('system_window')
class SystemPromptWindow(BasePromptWindow):

    def __init__(self, kernel_file=None,heap_file=None,stack_file=None,code_file=None):
        super().__init__()
        self.kernelPromptWindow = KernelPromptModule(kernel_file)
        self.heapPromptWindow = HeapPromptWindow(heap_file)
        self.stackPromptWindow = StackPromptWindow(stack_file)
        self.codePromptWindow = CodePromptModule(code_file)
        self.Windows = [self.kernelPromptWindow, self.heapPromptWindow, self.stackPromptWindow, self.codePromptWindow]
        for window in self.Windows:
            self.handlers.update(window.export_handlers() or {})

    def forward(self, *args, **kwargs):
        desc =''
        for module in self.Windows:
            desc += module.forward(*args, **kwargs)
        return desc

    def export_handlers(self):
        handlers = {}
        for window in self.Windows:
            handlers.update(window.export_handlers() or {})
        return handlers

    def get_divide_snapshot(self):
        divided_snap_shot = {}
        for window in self.Windows:
            divided_snap_shot.update(window.get_divide_snapshot())
        return divided_snap_shot

    def get_snapshot(self):
        snapshot = {}
        for window in self.Windows:
            snapshot.update({window.window_name:window.get_snapshot()})
        return snapshot

    def get_descriptions(self):
        descriptions = {}
        for window in self.Windows:
            descriptions.update({window.window_name:window.export_meta_prompt()})
        return descriptions

    def get_state_snapshot(self):
        state_snapshot = {}
        for window in self.Windows:
            state_snapshot.update({window.window_name:window.export_state_prompt()})
        return state_snapshot