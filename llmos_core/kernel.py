# kernel.py
import time
import uuid
from collections import deque

class Logger:
    def __init__(self):
        self.logs = []

    def write(self, level, msg):
        entry = {"ts": time.time(), "level": level, "msg": msg}
        self.logs.append(entry)
        print(f"[{level}] {msg}")

    def dump(self):
        return list(self.logs)

class MemoryPage:
    def __init__(self, page_id, process_id=None, content="", status="active"):
        self.page_id = page_id
        self.process_id = process_id
        self.content = content
        self.status = status
        self.ts = time.time()
        self.usage_count = 0

    def summary(self, maxlen=120):
        s = self.content or ""
        return (s[:maxlen] + "...") if len(s) > maxlen else s

class MemoryManager:
    def __init__(self, logger, max_pages=10):
        self.pages = {}  # page_id -> MemoryPage
        self.index = []  # LRU-ish order, front is oldest
        self.max_pages = max_pages
        self.logger = logger

    def new_page(self, process_id, content):
        pid = str(uuid.uuid4())[:8]
        p = MemoryPage(pid, process_id, content, status="active")
        self.pages[pid] = p
        self.index.append(pid)
        self.logger.write("INFO", f"Created page {pid} for process {process_id}")
        self._ensure_limit()
        return pid

    def touch(self, page_id):
        if page_id in self.index:
            self.index.remove(page_id)
            self.index.append(page_id)
            self.pages[page_id].usage_count += 1
            self.pages[page_id].ts = time.time()

    def get_page(self, page_id):
        return self.pages.get(page_id)

    def swap_out(self, page_id):
        p = self.pages.get(page_id)
        if p and p.status == "active":
            p.status = "swapped"
            self.logger.write("INFO", f"Swapped out page {page_id}")
            return True
        return False

    def swap_in(self, page_id):
        p = self.pages.get(page_id)
        if p and p.status == "swapped":
            p.status = "active"
            self.logger.write("INFO", f"Swapped in page {page_id}")
            return True
        return False

    def _ensure_limit(self):
        while len(self.index) > self.max_pages:
            oldest = self.index.pop(0)
            self.swap_out(oldest)

    def list_pages(self):
        return {pid: {"process_id": p.process_id, "status": p.status, "summary": p.summary()} for pid,p in self.pages.items()}

class Task:
    def __init__(self, task_id, payload, metadata=None):
        self.task_id = task_id
        self.payload = payload
        self.metadata = metadata or {}
        self.status = "pending"

class TaskScheduler:
    def __init__(self, logger):
        self.queue = deque()
        self.logger = logger

    def submit(self, task):
        self.queue.append(task)
        self.logger.write("INFO", f"Task {task.task_id} submitted")

    def fetch(self):
        if self.queue:
            t = self.queue.popleft()
            self.logger.write("INFO", f"Task {t.task_id} fetched")
            return t
        return None

    def qsize(self):
        return len(self.queue)

class ModuleManager:
    def __init__(self, logger):
        self.modules = {}
        self.logger = logger

    def register(self, name, handler, description=""):
        self.modules[name] = {"handler": handler, "description": description}
        self.logger.write("INFO", f"Module '{name}' registered")

    def unregister(self, name):
        if name in self.modules:
            del self.modules[name]
            self.logger.write("INFO", f"Module '{name}' unregistered")

    def call(self, name, *args, **kwargs):
        if name not in self.modules:
            raise Exception(f"Module {name} not registered")
        return self.modules[name]["handler"](*args, **kwargs)

class Kernel:
    def __init__(self, max_pages=10):
        self.logger = Logger()
        self.mem = MemoryManager(self.logger, max_pages=max_pages)
        self.scheduler = TaskScheduler(self.logger)
        self.modules = ModuleManager(self.logger)
        self.state = {
            "modules": [],
            "task_queue": [],
            "memory_pages": [],
            "logs": []
        }

        # syscall table maps syscall name to kernel-internal handler (module call or kernel function)
        self.syscall_table = {
            "register_module": self._sys_register_module,
            "submit_task": self._sys_submit_task,
            "fetch_task": self._sys_fetch_task,
            "write_log": self._sys_write_log,
            "get_summary": self._sys_get_summary
        }

    # Public kernel syscall entry — emulate "trap into kernel"
    def syscall(self, name, *args, **kwargs):
        self.logger.write("DEBUG", f"Kernel received syscall: {name} args={args} kwargs={kwargs}")
        if name not in self.syscall_table:
            raise Exception(f"Invalid syscall: {name}")
        handler = self.syscall_table[name]
        return handler(*args, **kwargs)

    # Kernel internal handlers
    def _sys_register_module(self, name, handler, description=""):
        self.modules.register(name, handler, description)
        self.state["modules"] = list(self.modules.modules.keys())
        return {"status":"ok", "module": name}

    def _sys_submit_task(self, payload, metadata=None):
        tid = str(uuid.uuid4())[:8]
        task = Task(tid, payload, metadata)
        self.scheduler.submit(task)
        self.state["task_queue"] = self.scheduler.qsize()
        return {"status":"ok", "task_id": tid}

    def _sys_fetch_task(self):
        t = self.scheduler.fetch()
        if t is None:
            return None
        self.state["task_queue"] = self.scheduler.qsize()
        return {"task_id": t.task_id, "payload": t.payload, "metadata": t.metadata}

    def _sys_write_log(self, level, msg):
        self.logger.write(level, msg)
        self.state["logs"] = len(self.logger.logs)
        return {"status":"ok"}

    def _sys_get_summary(self):
        # produce a tiny summary from pages and logs
        pages = self.mem.list_pages()
        logs = self.logger.dump()[-10:]
        summary = {
            "pages": pages,
            "recent_logs": logs
        }
        return summary

    # convenience helper to create context pages
    def new_context_page(self, process_id, content):
        pid = self.mem.new_page(process_id, content)
        self.state["memory_pages"] = self.mem.list_pages()
        return pid
