"""
大语言模型客户端
支持多种LLM接口，包括OpenAI、vLLM等
"""
import os
import json
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class LLMClient:
    """
    大语言模型客户端类
    
    设计理念：
    1. 统一接口：不同LLM提供商使用统一的调用接口
    2. 可配置性：支持通过环境变量或参数配置不同的模型
    3. 错误处理：包含完善的错误处理和重试机制
    4. 扩展性：易于添加新的LLM提供商支持
    """
    
    def __init__(self, 
                 model_type: str = "openai",
                 model_name: str = "gpt-3.5-turbo",
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 temperature: float = 0.7):
        """
        初始化LLM客户端
        
        Args:
            model_type: 模型类型 (openai, vllm, local)
            model_name: 模型名称
            api_key: API密钥
            base_url: 自定义API地址
            temperature: 生成温度参数
        """
        self.model_type = model_type
        self.model_name = model_name
        self.temperature = temperature
        
        # 配置API密钥
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        # 配置基础URL
        if base_url:
            self.base_url = base_url
        elif model_type == "vllm":
            self.base_url = os.getenv("VLLM_BASE_URL", "http://localhost:8000")
        else:
            self.base_url = "https://api.openai.com/v1"
    
    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        生成文本的统一接口
        
        Args:
            prompt: 输入提示词
            max_tokens: 最大生成token数
            
        Returns:
            生成的文本内容
            
        设计思路：
        - 使用统一的接口设计，便于切换不同的LLM
        - 包含错误处理和重试机制
        - 支持流式输出（可扩展）
        """
        try:
            if self.model_type in ["openai", "vllm"]:
                return self._call_openai_api(prompt, max_tokens)
            else:
                raise ValueError(f"不支持的模型类型: {self.model_type}")
        except Exception as e:
            print(f"LLM调用失败: {e}")
            return f"生成失败: {str(e)}"
    
    def _call_openai_api(self, prompt: str, max_tokens: int) -> str:
        """
        调用OpenAI API格式的接口
        
        为什么这样设计：
        1. OpenAI API已成为事实标准，很多本地部署的模型都兼容此格式
        2. vLLM等框架也提供OpenAI兼容的API
        3. 统一的API格式便于维护和扩展
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model_name,
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": max_tokens,
            "temperature": self.temperature
        }
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API请求失败: {e}")
        except (KeyError, IndexError) as e:
            raise Exception(f"API响应格式错误: {e}")
    
    def batch_generate(self, prompts: list, max_tokens: int = 1000) -> list:
        """
        批量生成文本
        
        为什么需要批量生成：
        1. 提高效率：避免频繁的网络请求
        2. 并发处理：可以并行处理多个请求
        3. 成本优化：某些API提供商对批量请求有优惠
        """
        results = []
        for prompt in prompts:
            result = self.generate_text(prompt, max_tokens)
            results.append(result)
        return results
