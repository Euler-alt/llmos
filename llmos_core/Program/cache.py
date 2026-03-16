import json
import yaml
from pathlib import Path
from typing import Optional, Any

CACHE_FILE = Path(__file__).parent /"cache_result"/ "cache.yaml"

def load_cache_result(result_path: Optional[str | Path] = None) -> Any:
    # 1. 确定路径
    path = Path(result_path) if result_path else CACHE_FILE

    # 2. 安全检查：如果文件不存在直接返回 None 或报错
    if not path.exists():
        return None

    # 3. 根据后缀识别格式
    suffix = path.suffix.lower()

    with open(path, "r", encoding="utf-8") as f:
        if suffix in (".yaml", ".yml"):
            data = yaml.safe_load(f)
        elif suffix == ".json":
            data = json.load(f)
        else:
            # 如果后缀都不对，可以报错或尝试默认加载
            raise ValueError(f"不支持的文件格式: {suffix}")

    # 4. 提取结果（利用你之前的 get 逻辑）
    # 如果 data 为空，返回 None；否则取 "result" 键
    return (data or {}).get("result")