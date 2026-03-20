import json
from typing import List
from llmos_core.Prompts.Windows.BaseWindow import BasePromptWindow
from llmos_core.schema import ToolDefinition
from alfworld.agents.environment import get_environment
import yaml
import os
import traceback
from pathlib import Path
from collections import deque

ALFWORLD_DATA_ROOT = "/root/PycharmProjects/alfworld/data"
os.environ['ALFWORLD_DATA'] = ALFWORLD_DATA_ROOT

META_DIR = Path(__file__).parent
META_FILE = META_DIR / 'alfworld_description.json'

# 最多保留最近 N 步的历史（防止 prompt 无限增长）
OBS_HISTORY_MAXLEN = 10


class ALFworldWindow(BasePromptWindow):
    def __init__(self, window_title='ALFWorld'):
        super().__init__(window_title=window_title, meta_file=META_FILE)

        # 加载配置
        config_path = os.path.join("/root/PycharmProjects/alfworld/configs", "base_config.yaml")
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config file: {e}")
            self.config = {}

        # 初始化环境
        EnvClass = get_environment('AlfredTWEnv')
        uninitialized_env = EnvClass(self.config, train_eval='train')
        self.env = uninitialized_env.init_env(batch_size=1)

        # 首次重置
        obs_batch, self.info = self.env.reset()
        self.obs = obs_batch[0] if isinstance(obs_batch, (list, tuple)) else obs_batch

        # 状态变量
        self.admissible_cmds = self.info.get("admissible_commands", [])
        self.last_action = None
        self.last_reward = 0
        self.done = False

        # 观察历史：每条记录为 (action, obs, reward)
        # action=None 表示初始观察
        self._obs_history: deque = deque(maxlen=OBS_HISTORY_MAXLEN)
        self._obs_history.append((None, self.obs, 0))

    def export_meta_prompt(self) -> str:
        return super().export_meta_prompt()

    def get_tool_definitions(self) -> List[ToolDefinition]:
        tools = []
        for func in self.meta_data.get("functions", []):
            properties = {}
            required = []
            for param_name, param_desc in func.get("parameters", {}).items():
                properties[param_name] = {"type": "string", "description": param_desc}
                required.append(param_name)
            tools.append(ToolDefinition(
                name=func["name"],
                description=func["description"],
                parameters={
                    "type": "object",
                    "properties": properties,
                    "required": required
                }
            ))
        return tools

    def forward(self, *args, **kwargs):
        return super().forward()

    def _render_obs_history(self) -> str:
        """将观察历史渲染为易读的累加格式。"""
        lines = []
        for i, (action, obs, reward) in enumerate(self._obs_history):
            clean_obs = obs.strip().replace('\n', ' ')
            if i == 0 and action is None:
                # 初始观察
                lines.append(f"  [INIT] {clean_obs}")
            else:
                reward_tag = f"+{reward:.2f}" if reward > 0 else f"{reward:.2f}"
                lines.append(f"  [Step {i}] Action: {action}")
                lines.append(f"           Obs:    {clean_obs}  (reward: {reward_tag})")
        return "\n".join(lines)

    def export_state_prompt(self) -> str:
        cmds = self.info.get("admissible_commands")[0]
        self.admissible_cmds = cmds
        won = self.info.get("won")[0]
        status_line = f"Status: {'WON' if won else  'IN PROGRESS'}\n"
        
        return f"""
{status_line}
### RECENT OBSERVATION HISTORY ###
{self._render_obs_history()}

### ADMISSIBLE COMMANDS ###
{", ".join(self.admissible_cmds)}
"""

    def step(self, action):
        self.last_action = action
        try:
            obs_batch, reward_batch, done_batch, info_batch = self.env.step([action])

            self.obs = obs_batch[0]
            self.last_reward = reward_batch[0]
            self.done = done_batch[0]

            if isinstance(info_batch, (list, tuple)) and len(info_batch) > 0 and isinstance(info_batch[0], dict):
                self.info = info_batch[0]
            elif isinstance(info_batch, dict):
                self.info = info_batch
            else:
                raise TypeError(f"Unexpected info batch format: {type(info_batch)}")

            self.info["error"] = False

            # 成功执行，追加历史
            self._obs_history.append((action, self.obs, self.last_reward))

        except AssertionError as e:
            error_msg = f"Assertion Error: incorrect input format. Details: {e}"
            self.obs = f"[CRITICAL TOOL ERROR] {error_msg}. Last Attempted Action: '{action}'"
            self.last_reward = -0.05
            self.done = False
            self.info = {"error": True, "error_type": "AssertionError", "original_action": action,
                         "admissible_commands": []}
            self._obs_history.append((action, self.obs, self.last_reward))
            print(f"Assertion Error during ALF:step: {traceback.format_exc()}")

        except Exception as e:
            error_msg = f"Environment Execution Error: {e}"
            self.obs = f"[CRITICAL TOOL ERROR] {error_msg}. Review 'Available Actions' and try again. Last Attempted Action: '{action}'"
            self.last_reward = -0.1
            self.done = False
            self.info = {"error": True, "error_type": "GenericError", "original_action": action,
                         "admissible_commands": []}
            self._obs_history.append((action, self.obs, self.last_reward))
            print(f"Generic Error during ALF:step: {traceback.format_exc()}")

        if self.info.get("error"):
            summary = f"❌ 动作执行失败: {self.obs}"
        else:
            clean_obs = self.obs.strip().replace('\n', ' ')
            if len(clean_obs) > 150:
                clean_obs = clean_obs[:147] + "..."
            summary = f"执行动作 '{action}' -> 观察到: {clean_obs}"

        return {
            'execute_action': action,
            'reward': self.last_reward,
            'done': self.done,
            '__summary__': summary
        }

    def reset(self):
        """重置 ALFWorld 环境和内部状态"""
        obs_batch, self.info = self.env.reset()
        self.obs = obs_batch[0] if isinstance(obs_batch, (list, tuple)) else obs_batch
        self.admissible_cmds = self.info.get("admissible_commands", [])
        self.last_action = None
        self.last_reward = 0
        self.done = False
        self._obs_history.clear()
        self._obs_history.append((None, self.obs, 0))
        print(f"ALFWorld Environment Reset.")

    def export_handlers(self):
        return {
            "ALF_step": self.step,
            "ALF_reset": self.reset
        }