import datetime
import string

from enum import Enum

class RecordType(Enum):
    event_call = 'event_call'
    prompt_call = 'prompt'
    tool_call = 'tool'
    error = 'error'

class SafeFormatter(string.Formatter):
    """
    一个安全的格式化器，缺失的键会显示为空字符串或指定的默认值。
    """
    def get_field(self, field_name, args, kwargs):
        try:
            return super().get_field(field_name, args, kwargs)
        except KeyError:
            # 键不存在时，返回一个空字符串 '' 作为值
            return '', field_name

class LogEvent:
    _templates = {}
    _formatter = SafeFormatter()  # 使用安全格式化器
    @classmethod
    def register(cls, name: str, template: str):
        cls._templates[name] = template

    def __init__(self, event_type: str, **data):
        self.timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.event_type = event_type
        self.data = data

    def render(self) -> str:
        template = self._templates.get(self.event_type)
        if template:
            # 使用 SafeFormatter 进行格式化
            formatted_message = self._formatter.format(template, **self.data)
            return f"[{self.timestamp}] [{self.event_type}] {formatted_message}"
        else:
            return f"[{self.timestamp}] [{self.event_type}] {self.event_type}: {self.data}"

LogEvent.register(f"{RecordType.prompt_call}", "调用 {func_name},reasoning:{reasoning} → {result}")
LogEvent.register(f"{RecordType.error}", "raw_response:{raw_response} →❌ {error}")
LogEvent.register(f"{RecordType.tool_call}", "调用 {func_name},reasoning:{reasoning} → {result}")
LogEvent.register(f"{RecordType.event_call}", "外部环境产生了调用 {func_name}")


