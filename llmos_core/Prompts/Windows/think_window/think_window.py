import json
from llmos_core.Prompts.Windows.BaseWindow import BasePromptWindow
from llmos_core.schema import ToolDefinition
from pathlib import Path
from typing import List

Meta_dir = Path(__file__).parent
Meta_file = Meta_dir / "think_description.json"

class ThinkWindow(BasePromptWindow):
    def __init__(self, window_title='think_window'):
        super().__init__(window_title=window_title)
        with open(Meta_file) as f:
            self.meta_data = json.load(f)
        self.think_content = None

    def export_meta_prompt(self) -> str:
        return json.dumps(self.meta_data, indent=2, ensure_ascii=False)

    def get_tool_definitions(self) -> List[ToolDefinition]:
        return []

    def export_state_prompt(self) -> str:
        if self.think_content:
            return f"#last_thinks#:{self.think_content}"
        else:
            return "#No last think"

    def new_think(self, *args, **kwargs):
        self.think_content = kwargs.get('content')
        return {"status": "ok", "message": "Think updated."}

    def export_handlers(self):
        return {
            "new_think": self.new_think,
        }
