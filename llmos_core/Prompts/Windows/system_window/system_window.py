from llmos_core.Prompts.Windows.BaseWindow.BaseWindow import BasePromptWindow
from llmos_core.Prompts.Windows.heap_window.heap_window import HeapPromptWindow
from llmos_core.Prompts.Windows.stack_window.stack_window import StackPromptWindow
from llmos_core.Prompts.Windows.static_window.static_window import KernelPromptWindow,CodePromptWindow

@BasePromptWindow.register('system_window')
class SystemPromptWindow(BasePromptWindow):

    def __init__(self, kernel_file=None,heap_file=None,stack_file=None,code_file=None):
        super().__init__()
        self.kernelPromptWindow = KernelPromptWindow(kernel_file)
        self.heapPromptWindow = HeapPromptWindow(heap_file)
        self.stackPromptWindow = StackPromptWindow(stack_file)
        self.codePromptWindow = CodePromptWindow(code_file)
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

    def get_divided_snapshot(self):
        divided_snap_shot = {}
        for window in self.Windows:
            divided_snap_shot.update(window.get_divided_snapshot())
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