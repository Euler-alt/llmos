from pathlib import Path
import json


class CacheManager:
    """
    管理缓存加载、迭代和写入。
    提供：
        - next_record()       获取下一条缓存
        - append_record()     追加新的缓存记录
        - reset()             重置迭代器
    """

    def __init__(self, cache_file: Path,clear_cache_file: bool = True):
        self.cache_file = cache_file
        self._iter = None
        self._index = -1
        if clear_cache_file:
            self.clear()

    def clear(self):
        """真正执行清空缓存的动作"""
        self.cache_file.parent.mkdir(exist_ok=True)
        with open(self.cache_file, "w", encoding="utf8") as f:
            json.dump([], f, indent=2, ensure_ascii=False)
        self.reset()

    # === 内部方法 ===
    def _load_cache(self):
        """加载整个缓存文件为列表"""
        if not self.cache_file.exists():
            return []

        try:
            with open(self.cache_file, "r", encoding="utf8") as f:
                data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                print(f"[cache] 非列表格式缓存，忽略 {self.cache_file}")
                return []
        except json.JSONDecodeError:
            print(f"[cache] 缓存损坏 {self.cache_file}")
            return []

    # === 对外的方法 ===
    def reset(self):
        """重置缓存迭代器"""
        self._iter = None
        self._index = -1

    def next_record(self):
        """
        生成器形式读取缓存，返回：
        {
            "index": i,
            "prompt": {...},
            "response": {...},
            "meta": {}
        }
        或 None（没有更多缓存）
        """
        # 初始化迭代器
        if self._iter is None:
            data = self._load_cache()
            self._iter = iter(data)

        try:
            raw = next(self._iter)
        except StopIteration:
            return None

        self._index += 1
        return {
            "index": self._index,
            "prompt": raw.get("prompt"),
            "response": raw.get("response"),
        }

    def append_record(self, prompt, response):
        """将一次交互追加到缓存文件中"""
        data = self._load_cache()

        data.append({
            "prompt": prompt,
            "response": response,
        })

        self.cache_file.parent.mkdir(exist_ok=True)
        with open(self.cache_file, "w", encoding="utf8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
