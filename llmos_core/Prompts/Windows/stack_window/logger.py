import datetime
from typing import Any, Dict


class LogEvent:
    _templates = {}

    @classmethod
    def register(cls, name: str, template: str):
        cls._templates[name] = template

    def __init__(self, level: str, event_type: str, **data):
        self.timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.level = level.upper()
        self.event_type = event_type
        self.data = data

    def render(self) -> str:
        template = self._templates.get(self.event_type)
        if template:
            try:
                return f"[{self.timestamp}] [{self.level}] " + template.format(**self.data)
            except KeyError:
                return f"[{self.timestamp}] [{self.level}] {self.event_type}: {self.data}"
        else:
            return f"[{self.timestamp}] [{self.level}] {self.event_type}: {self.data}"

LogEvent.register("prompt", "调用 {func_name},reasoning:{reasoning} → {result}")
LogEvent.register("error", "raw_response:{raw_response} →❌ {error}")
LogEvent.register("tool", "调用 {func_name},reasoning:{reasoning} → {result}")
LogEvent.register("event_call", "调用 {func_name}")


