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
    reasoning: str = ""
    call_kwargs: Dict[str, Any] = field(default_factory=dict)
    status: str = "success"

@dataclass
class LLMOSCall:
    call_type: str
    func_name: str
    kwargs: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""

@dataclass
class ProgramRunResult:
    raw_response: str
    parsed_calls: List[Any]

@dataclass
class StackFrame:
    name: str
    description: str
    variables: Dict[str, Any] = field(default_factory=dict)
    fail_reason: Optional[str] = None
