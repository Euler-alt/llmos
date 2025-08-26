from .BaseModules import BasePromptModule
from pathlib import Path
import json

class HeapPromptModule(BasePromptModule):

    def __init__(self, name="heap"):
        super().__init__()
        self.name = name
        self.file_path = Path(__file__).parent / 'texts' / 'heap_description.txt'
        with open(self.file_path,'r') as f:
            self.description = f.read()
        # 堆的核心数据结构，一个全局字典
        self.data = {}

    def forward(self, context=None):
        """将堆数据序列化成提示词，供 LLM 使用"""
        if not self.data:
            return f'\n{self.description}\n### HEAP DATA ###\n'

        # 序列化为可读的 JSON 格式
        heap_data_str = json.dumps(self.data, indent=2, ensure_ascii=False)
        return f"\n{self.description}\n### HEAP DATA ###\n{heap_data_str}\n"

    def _heap_set(self,*args,**kwargs):
        key = kwargs.get("key")
        value = kwargs.get("value")
        if key is None or value is None:
            return {"status": "error", "reason": "key or value missing"}
        self.data[key] = value
        return {"status": "ok", "key": key, "value": value}

    def _heap_get(self,*args,**kwargs):
        key = kwargs.get("key")
        if key is None:
            return {"status": "error", "reason": "key missing"}
        value = self.data.get(key)
        return {"status": "ok", "key": key, "value": value}

    def _heap_delete(self,*args,**kwargs):
        key = kwargs.get("key")
        if key is None:
            return {"status": "error", "reason": "key missing"}
        if key in self.data:
            del self.data[key]
            return {"status": "ok", "key": key}
        else:
            return {"status": "error", "reason": f"key '{key}' not found"}

    def export_handlers(self):
        return {
                'heap_set':self._heap_set,
                'heap_get':self._heap_get,
                'heap_delete':self._heap_delete
                }