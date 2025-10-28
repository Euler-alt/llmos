from .BaseWindow import BasePromptWindow
from alfworld.agents.environment import get_environment
import alfworld.agents.modules.generic as generic
import yaml
import os
ALFWORLD_DATA_ROOT = "/root/PycharmProjects/alfworld/data"
os.environ['ALFWORLD_DATA'] = ALFWORLD_DATA_ROOT
@BasePromptWindow.register("alfworld")
class ALFworldWindow(BasePromptWindow):
    def __init__(self,window_name='ALFWorld'):
        super().__init__(window_name=window_name)
        # 修正：使用 generic.load_config()/root/PycharmProjects/alfworld/configs/base_config.yaml
        config_path = os.path.join("/root/PycharmProjects/alfworld/configs", "base_config.yaml")
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # 注意：这里我们假设你的配置中 'env']['type'] 是 'AlfredTWEnv'，
        # 如果不是，你可能需要从 config 中动态获取 env type。
        EnvClass = get_environment('AlfredTWEnv')
        uninitialized_env= EnvClass(self.config, train_eval='train')
        self.env = uninitialized_env.init_env(batch_size=1)

        # 5. 首次重置（现在 self.env 具备 reset() 方法了）
        self.obs, self.info = self.env.reset()
        self.admissible_cmds = None
        self.last_action = None
        self.last_reward = 0
        self.done = False

    # ... (其他方法保持不变)
    def forward(self, *args, **kwargs):
        return f"{self.export_meta_prompt()}\n{self.export_state_prompt()}"

    def export_meta_prompt(self) -> str:
        return (
            "[ENV MODULE: ALFWorld]\n"
            "You are an embodied agent operating in a text-based environment.\n"
            "You can perform actions by calling 'ALF_step(action=...)', where the action must be one of the available commands listed in the current state.\n"
            "Each step returns a new observation, a reward, and whether the task is done.\n"
            "Think carefully about the environment and plan your next move.\n"
        )

    def export_state_prompt(self) -> str:
        self.admissible_cmds = self.info.get("admissible_commands", [])
        task_desc = self.info.get("task_desc", "Unknown task")
        inventory = self.info.get("inv_objs", [])
        progress = self.info.get("goal_progress", None)
        won = self.info.get("won", False)
        failed = self.info.get("failed", False)

        progress_line = f"Goal Progress: {progress:.2f}\n" if progress is not None else ""

        return (
            "[ENV STATE]\n"
            f"Task: {task_desc}\n"
            f"Observation: {self.obs}\n"
            f"Inventory: {inventory}\n"
            f"Available Actions: {self.admissible_cmds}\n"
            f"Last Action: {self.last_action}\n"
            f"Last Reward: {self.last_reward}\n"
            f"Done: {self.done}, Won: {won}, Failed: {failed}\n"
            f"{progress_line}"
            "[/ENV STATE]\n"
        )

    def step(self, action):
        self.last_action = action
        self.obs, self.last_reward, self.done, self.info = self.env.step(action)
        return self.obs, self.last_reward, self.done, self.info

    def reset(self):
        self.obs, self.info = self.env.reset()
        self.last_action, self.last_reward, self.done = None, 0, False
        return self.obs

    def export_handlers(self):
        return {
            "ALF_step": self.step,
            "ALF_reset": self.reset
        }