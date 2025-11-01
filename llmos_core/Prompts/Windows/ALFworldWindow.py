from .BaseWindow import BasePromptWindow
from alfworld.agents.environment import get_environment
import alfworld.agents.modules.generic as generic
import yaml
import os
import traceback  # 引入 traceback 模块用于更详细的错误报告

# 假设 ALFWORLD_DATA_ROOT 已经设置好
ALFWORLD_DATA_ROOT = "/root/PycharmProjects/alfworld/data"
os.environ['ALFWORLD_DATA'] = ALFWORLD_DATA_ROOT


@BasePromptWindow.register("alfworld")
class ALFworldWindow(BasePromptWindow):
    def __init__(self, window_name='ALFWorld'):
        super().__init__(window_name=window_name)

        # 1. 加载配置
        config_path = os.path.join("/root/PycharmProjects/alfworld/configs", "base_config.yaml")
        try:
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)
        except Exception as e:
            print(f"Error loading config file: {e}")
            self.config = {}  # 使用空配置作为回退

        # 2. 初始化环境
        EnvClass = get_environment('AlfredTWEnv')
        uninitialized_env = EnvClass(self.config, train_eval='train')
        self.env = uninitialized_env.init_env(batch_size=1)

        # 3. 首次重置环境
        self.obs, self.info = self.env.reset()

        # 4. 初始化状态变量
        self.admissible_cmds = self.info.get("admissible_commands", [])
        self.last_action = None
        self.last_reward = 0
        self.done = False

    def forward(self, *args, **kwargs):
        """主入口，返回完整的 Meta 和 State Prompt。"""
        return f"{self.export_meta_prompt()}\n{self.export_state_prompt()}"

    def export_meta_prompt(self) -> str:
        """定义大模型的角色和工具调用说明。"""
        return (
            "[ENV MODULE: ALFWorld]\n"
            "You are an embodied agent operating in a text-based environment.\n"
            "You can perform actions by calling 'ALF_step(action=...)', where the action must be one of the available commands listed in the current state.\n"
            "Each step returns a new observation, a reward, and whether the task is done.\n"
            "Think carefully about the environment and plan your next move.\n"
        )

    def export_state_prompt(self) -> str:
        """将当前环境状态格式化为 Prompt 文本。"""
        # 确保在出错时也能安全访问 info
        self.admissible_cmds = self.info.get("admissible_commands", [])
        task_desc = self.info.get("task_desc", "Unknown task")
        inventory = self.info.get("inv_objs", [])
        progress = self.info.get("goal_progress", None)
        won = self.info.get("won", False)
        failed = self.info.get("failed", False)

        # 检查 progress 是否为 None，避免格式化错误
        progress_line = f"Goal Progress: {progress:.2f}\n" if progress is not None else ""

        # 检查是否有错误发生，并加入到状态报告中
        error_status = ""
        if self.info.get("error", False):
            error_status = f"CRITICAL ERROR OCCURRED: {self.info.get('error_type', 'Unknown')}\n"

        return (
            "[ENV STATE]\n"
            f"{error_status}"
            f"Task: {task_desc}\n"
            f"Observation: {self.obs}\n"
            f"Inventory: {inventory}\n"
            f"Available Actions: {self.admissible_cmds}\n"
            f"Last Action: {self.last_action}\n"
            f"Last Reward: {self.last_reward}\n"
            f"Done: {self.done}, Won: {won}, Failed: {failed}\n"
            f"{progress_line}"
            "[ACTION GUIDE] The Observation above is your current environment feedback. If it contains '[CRITICAL TOOL ERROR]', you must read the error and correct your next ALF_step call.\n"
            "[END STATE]\n"
        )

    def step(self, action):
        """
        执行 ALFWorld 环境中的一个动作。

        已修复两个问题：
        1. 确保 action 被封装成列表 (batch_size=1 的环境要求)。
        2. 添加 try-except 块以捕获错误，并将错误信息作为新的 Observation 返回给 LLM。
        """
        self.last_action = action
        try:
            # FIX 1: TextWorld Batch Env requires a list of commands, even for batch_size=1.
            # FIX 2: Correctly unpacks the batch returns (obs_batch, reward_batch, ...)
            obs_batch, reward_batch, done_batch, info_batch = self.env.step([action])

            # Unpack the single item from the batch
            self.obs = obs_batch[0]
            self.last_reward = reward_batch[0]
            self.done = done_batch[0]

            # FIX 2 UPDATE: Addressing KeyError: 0 on info_batch.
            # This suggests info_batch is the dictionary itself, not a list of dictionaries.
            # We assign it directly.
            if isinstance(info_batch, (list, tuple)) and len(info_batch) > 0 and isinstance(info_batch[0], dict):
                # 优先按列表处理 (最标准的做法)
                self.info = info_batch[0]
            elif isinstance(info_batch, dict):
                # 如果它直接就是字典 (您的错误指向的情况)
                self.info = info_batch
            else:
                # 捕获意外格式
                raise TypeError(f"Unexpected info batch format: {type(info_batch)}")

            self.info["error"] = False  # 标记成功执行

        except AssertionError as e:
            # 捕获因输入格式错误（如非 list）导致的断言错误
            error_msg = f"Assertion Error: The environment execution failed due to incorrect input format. Details: {e}"
            self.obs = f"[CRITICAL TOOL ERROR] {error_msg}. LLM must re-evaluate the action format. Last Attempted Action: '{action}'"
            self.last_reward = -0.05  # 可以给一个轻微惩罚
            self.done = False
            self.info = {"error": True, "error_type": "AssertionError", "original_action": action,
                         "admissible_commands": []}
            print(f"Assertion Error during ALF_step: {traceback.format_exc()}")

        except Exception as e:
            # 捕获其他运行时错误（如环境内部错误、无效的命令字符串等）
            error_msg = f"Environment Execution Error: Details: {e}"
            self.obs = f"[CRITICAL TOOL ERROR] {error_msg}. LLM must review the 'Available Actions' and try again. Last Attempted Action: '{action}'"
            self.last_reward = -0.1  # 可以给一个惩罚
            self.done = False
            self.info = {"error": True, "error_type": "GenericError", "original_action": action,
                         "admissible_commands": []}
            print(f"Generic Error during ALF_step: {traceback.format_exc()}")

        return self.obs, self.last_reward, self.done, self.info

    def reset(self):
        """重置环境并清除状态。"""
        self.obs, self.info = self.env.reset()
        self.last_action, self.last_reward, self.done = None, 0, False
        self.info["error"] = False
        return self.obs

    def export_handlers(self):
        """暴露给大模型调用的 API 接口。"""
        return {
            "ALF_step": self.step,
            "ALF_reset": self.reset
        }
