from pathlib import Path
import json

def load_cache_result(result_path=None):
    """逐条加载缓存结果（生成器版）"""
    result_path = Path(result_path) if result_path else Path(CACHE_FILE)
    if not result_path.exists():
        print(f"[cache] 缓存文件 {result_path} 不存在，返回空生成器。")
        return
    with open(result_path, "r") as f:
        try:
            result = json.load(f)
        except json.JSONDecodeError:
            print(f"[cache] 文件损坏或格式错误：{result_path}")
            return
    if not isinstance(result, list):
        print(f"[cache] 非列表格式缓存，忽略。")
        return
    for i, record in enumerate(result):
        yield {
            "index": i,
            "prompt": record.get("prompt"),
            "response": record.get("response"),
            "meta": record.get("meta", {}),
        }


def append_cache_record(cache_file, prompt, response):
    """把一次交互追加到缓存文件"""
    cache_file.parent.mkdir(exist_ok=True)
    try:
        if cache_file.exists():
            with open(cache_file, "r") as f:
                data = json.load(f)
        else:
            data = []
    except json.JSONDecodeError:
        data = []

    data.append({
        "prompt": prompt,
        "response": response,
    })

    with open(cache_file, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)