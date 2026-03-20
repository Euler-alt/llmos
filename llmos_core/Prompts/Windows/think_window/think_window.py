import json
from llmos_core.Prompts.Windows.BaseWindow import BasePromptWindow
from llmos_core.schema import ToolDefinition
from pathlib import Path
from typing import List

Meta_dir = Path(__file__).parent
Meta_file = Meta_dir / "think_description.json"

class ThinkWindow(BasePromptWindow):
    def __init__(self, window_title='think_window'):
        super().__init__(window_title=window_title, meta_file=Meta_file)
        self.think_content = None

    def reset(self):
        """清空思考内容"""
        self.think_content = None
        print(f"Think Window Reset.")

    # export_meta_prompt 已经由基类实现

    def get_tool_definitions(self) -> List[ToolDefinition]:
        return []

    def export_state_prompt(self) -> str:
        if self.think_content:
            return f"#last_thinks#:{self.think_content}"
        else:
            return "#No last think"

    def new_think(self, *args, **kwargs):
        content = kwargs.get('content', '')
        self.think_content = content
        return {
            "status": "ok", 
            "message": "Think updated.",
            "__summary__": f"Updated internal thought: {content[:40]}..."
        }

    def export_handlers(self):
        return {
            "new_think": self.new_think,
        }
