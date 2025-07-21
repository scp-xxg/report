# 配置管理器 - 统一的配置管理

import json
import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class ConfigurationError(Exception):
    """配置错误"""
    pass

class ConfigManager:
    """统一配置管理器"""
    
    def __init__(self, config_file: str = "config.json"):
        """
        初始化配置管理器
        
        Args:
            config_file: 配置文件路径
        """
        self.config_file = config_file
        self.config = self._load_config()
        self._validate_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_config()
        except json.JSONDecodeError as e:
            raise ConfigurationError(f"配置文件格式错误: {e}")
        except Exception as e:
            raise ConfigurationError(f"加载配置文件失败: {e}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "project": {
                "name": "multi-agent-report-generator",
                "version": "1.0.0",
                "description": "多智能体协作的自动化报告生成系统"
            },
            "system": {
                "default_model_type": "demo",
                "default_model_name": "demo-model",
                "default_output_dir": "./output",
                "max_retry_attempts": 3,
                "request_timeout": 60
            },
            "agents": {
                "outline_agent": {
                    "max_sections": 10,
                    "min_sections": 3
                },
                "content_agent": {
                    "target_words_per_section": 500,
                    "writing_style": "professional"
                },
                "polish_agent": {
                    "polish_aspects": ["语言流畅性", "逻辑清晰性", "专业术语规范"]
                },
                "chart_agent": {
                    "chart_types": ["bar", "line", "pie", "scatter"],
                    "max_charts_per_report": 5
                }
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点分割的键路径
        
        Args:
            key: 配置键，支持 'system.default_model_type' 格式
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key.split('.')
        value = self.config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        keys = key.split('.')
        config = self.config
        
        # 导航到最后一级
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # 设置值
        config[keys[-1]] = value
    
    def _validate_config(self) -> None:
        """验证配置完整性"""
        required_keys = [
            "system.default_model_type",
            "system.default_output_dir",
            "agents.outline_agent",
            "agents.content_agent"
        ]
        
        for key in required_keys:
            if self.get(key) is None:
                raise ConfigurationError(f"缺少必需的配置项: {key}")
    
    def get_model_config(self) -> Dict[str, Any]:
        """获取模型配置"""
        model_type = self.get("system.default_model_type", "demo")
        
        if model_type == "openai":
            return {
                "model_type": "openai",
                "model_name": self.get("system.default_model_name", "gpt-3.5-turbo"),
                "api_key": os.getenv("OPENAI_API_KEY"),
                "base_url": os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
            }
        elif model_type == "vllm":
            return {
                "model_type": "vllm",
                "model_name": self.get("system.default_model_name", "Qwen/Qwen2-7B-Instruct"),
                "api_key": "dummy",
                "base_url": os.getenv("VLLM_BASE_URL", "http://localhost:8000")
            }
        else:  # demo模式
            return {
                "model_type": "demo",
                "model_name": "demo-model",
                "api_key": None,
                "base_url": None
            }
    
    def save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ConfigurationError(f"保存配置文件失败: {e}")
    
    def reload_config(self) -> None:
        """重新加载配置"""
        self.config = self._load_config()
        self._validate_config()

# 全局配置实例
config_manager = ConfigManager()
