from .Modules import  HardwareMainBoard,IOModule,MemoryModule

import importlib
def load_external_module(board: HardwareMainBoard, module_path: str, class_name: str):
    spec = importlib.import_module(module_path)
    cls = getattr(spec, class_name)
    instance = cls()
    board.attach(instance)
