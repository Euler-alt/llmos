from pathlib import Path
import yaml


CACHE_FILE = Path('./cache') / "cache.yaml"


def load_cache_result(result_path=None) -> str:
    result_path = Path(result_path) if result_path else Path(CACHE_FILE)
    with open(result_path, "r") as f:
        result = yaml.safe_load(f)
    return result.get("result")