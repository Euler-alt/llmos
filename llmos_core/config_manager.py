from pathlib import Path
import os
import yaml
import json
class ConfigManager:
    """统一的配置管理器"""

    def __init__(self , spec_path=None):
        """

        :param spec_path:存放配置的路径
        """
        self.base_paths = self._get_base_paths(spec_path)

    def _get_base_paths(self,spec_path=None):
        """获取配置文件的搜索路径优先级"""
        paths = []

        # 1. 环境变量指定
        if spec_path is not None:
            paths.append(Path(spec_path))

        if env_path := os.getenv('LLMDEV_CONFIG_DIR'):
            paths.append(Path(env_path))

        return paths


    def load_json_config(self, config_name: str):
        """加载json配置文件"""

        config_path = self._find_config_file(config_name)

        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)

        return config

    def load_yaml_config(self, config_name: str):
        """加载yaml配置文件"""

        config_path = self._find_config_file(config_name)

        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)

        return config

    def _find_config_file(self, config_name: str):
        """在搜索路径中查找配置文件"""
        for base_path in self.base_paths:
            config_path = base_path / config_name
            if config_path.exists():
                return config_path

        raise FileNotFoundError(
            f"配置文件 {config_name} 在以下路径中都不存在:\n" +
            "\n".join(f"  - {path / config_name}" for path in self.base_paths)
        )

    def get_config_path(self, config_name: str):
        """获取配置文件的实际路径"""
        return self._find_config_file(config_name)