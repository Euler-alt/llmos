import json
import re

from llmos_core.llmos_util import LLMClient
from pathlib import Path
from llmos_core.Prompts import parse_response


# 测试你的原始输入
textfile = Path(__file__).parent / "res.json"

with open(textfile) as f:
    raw_data = f.read()
# 使用示例
parsed = parse_response(raw_data)
print(parsed["kwargs"]["variables"]["current_phase"])