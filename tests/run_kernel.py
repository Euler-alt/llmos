# run_demo.py
from llmos_core.kernel import Kernel
import time

# simple module that "executes" tasks by echoing and creating a context page
def echo_module(handler_input):
    # handler_input expected to be dict or str
    text = handler_input if isinstance(handler_input, str) else str(handler_input)
    return {"result": "ECHO: " + text}

def run_demo():
    k = Kernel(max_pages=3)

    # register a simple module
    k.syscall("register_module", "echo", echo_module, "Echo back module for demo")

    # submit a few tasks
    for i in range(5):
        payload = f"task_payload_{i}"
        res = k.syscall("submit_task", payload, {"priority": "low"})
        k.syscall("write_log", "INFO", f"submitted {payload} -> {res['task_id']}")

    # kernel main loop: fetch tasks and dispatch to module manager
    for _ in range(6):
        t = k.syscall("fetch_task")
        if not t:
            k.syscall("write_log", "INFO", "no more tasks")
            break
        task_id = t["task_id"]
        payload = t["payload"]
        k.syscall("write_log", "INFO", f"dispatching {task_id}")
        # dispatch to module 'echo'
        out = k.modules.call("echo", payload)
        k.syscall("write_log", "INFO", f"module output: {out}")
        # create a context page from output
        page_id = k.new_context_page(task_id, str(out))
        k.syscall("write_log", "INFO", f"created context page {page_id} for task {task_id}")
        time.sleep(0.1)  # simulate work

    # ask for summary
    summary = k.syscall("get_summary")
    print("\n--- SUMMARY ---")
    import json
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    run_demo()
