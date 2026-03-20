from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass
class WindowSnapshot:
    meta: str
    state: str

@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=lambda: {
        "type": "object",
        "properties": {},
        "required": []
    })

    def to_openai_tool(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters
            }
        }

@dataclass
class ToolCallResult:
    func_name: str
    result: Any
    summary: str = "" # 新增语义摘要字段
    reasoning: str = ""
    call_kwargs: Dict[str, Any] = field(default_factory=dict)
    status: str = "success"

    def get_summary(self) -> str:
        """获取执行结果摘要"""
        return self.summary or str(self.result) or "执行成功"

@dataclass
class LLMOSCall:
    call_type: str
    func_name: str
    kwargs: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""

    def get_summary(self) -> str:
        """获取调用请求摘要"""
        return f"调用 {self.func_name}"

@dataclass
class ProgramRunResult:
    raw_response: str
    parsed_calls: List[Any]

    def get_first_summary(self) -> str:
        """获取第一个解析出来的调用的摘要"""
        if not self.parsed_calls:
            return "执行成功"
        
        first = self.parsed_calls[0]
        if isinstance(first, (ToolCallResult, LLMOSCall)):
            return first.get_summary()
        elif isinstance(first, dict):
            return str(first.get('summary') or first.get('result') or "执行成功")
        return str(first)

