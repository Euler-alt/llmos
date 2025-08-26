class Module:
    """所有模块的基类"""
    def __init__(self, name):
        self.name = name

    def handle(self, call):
        raise NotImplementedError


class HardwareMainBoard:
    def __init__(self):
        self.modules = {}

    def attach(self, module: Module):
        self.modules[module.name] = module
        print(f"[MainBoard] Module '{module.name}' attached.")

    def detach(self, name: str):
        if name in self.modules:
            del self.modules[name]
            print(f"[MainBoard] Module '{name}' detached.")

    def syscall(self, call: dict):
        # call 必须指定目标模块
        module_name = call.get("module")
        if module_name not in self.modules:
            return f"Error: module '{module_name}' not found"

        return self.modules[module_name].handle(call)


class IOModule(Module):
    def __init__(self):
        super().__init__("io")

    def handle(self, call):
        op = call.get("op")
        if op == "print":
            print("[IO]:", call.get("message"))
            return "ok"
        elif op == "input":
            return input(call.get("prompt", "> "))
        else:
            return f"Unknown IO op: {op}"


class MemoryModule(Module):
    def __init__(self):
        super().__init__("memory")
        self.store = {}

    def handle(self, call):
        op = call.get("op")
        if op == "read":
            return self.store.get(call["addr"], None)
        elif op == "write":
            self.store[call["addr"]] = call["value"]
            return "ok"
        else:
            return f"Unknown Memory op: {op}"
