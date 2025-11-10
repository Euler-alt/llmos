from llmos_core.Prompts.Windows.BaseWindow.BaseWindow import BasePromptWindow
from pathlib import Path
import json

Meta_dir = Path(__file__).parent
Meta_file = Meta_dir / 'heap_description.json'
@BasePromptWindow.register('heap','Heap')
class HeapPromptWindow(BasePromptWindow):

    def __init__(self, window_name="Heap"):
        super().__init__(window_name=window_name)
        self.file_path = Meta_file
        with open(self.file_path,'r') as f:
            self.description = f.read()
        # 堆的核心数据结构，一个全局字典
        self.data = {}

    def export_state_prompt(self):
        heap_data_str = json.dumps(self.data, indent=2, ensure_ascii=False)
        if heap_data_str:
            return f"### HEAP DATA ###\n{heap_data_str}\n"
        else:
            return "### HEAP Empty ###\n"

    def export_meta_prompt(self):
        return f'{self.description}\n'

    def forward(self, context=None):
        """将堆数据序列化成提示词，供 LLM 使用"""
        return super().forward()

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