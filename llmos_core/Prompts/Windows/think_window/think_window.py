from llmos_core.Prompts.Windows.BaseWindow.BaseWindow import BasePromptWindow
from pathlib import Path
import json
Meta_dir = Path(__file__).parent
Meta_file = Meta_dir / "think_description.json"

@BasePromptWindow.register("think_window")
class ThinkWindow(BasePromptWindow):
    def __init__(self, window_name = 'think_window'):
        super().__init__(window_name=window_name)
        with open(Meta_file) as f:
            self.meta_data = json.load(f)
        self.think_content = None

    def forward(self):
        return f"{self.export_meta_prompt()}{self.export_state_prompt()}"


    def export_meta_prompt(self) ->str:
        return self.meta_data

    def export_state_prompt(self) ->str:
        if self.think_content:
            return f"#last_thinks#:{self.think_content}"
        else:
            return "#No last think"

    def new_think(self,*args,**kwargs):
        self.think_content = kwargs.get('content')

    def export_handlers(self):
        return {
            "new_think": self.new_think,
        }