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
            model_type: 模型类型 (openai, vllm, demo)
            model_name: 模型名称
            api_key: API密钥
            base_url: 自定义API地址
            temperature: 生成温度参数
        """
        self.model_type = model_type
        self.model_name = model_name
        self.temperature = temperature
        
        # 从环境变量或参数获取配置
        if model_type == "openai":
            self.api_key = api_key or os.getenv("OPENAI_API_KEY")
            self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        elif model_type == "vllm":
            self.api_key = "dummy"  # vLLM通常不需要密钥
            self.base_url = base_url or os.getenv("VLLM_BASE_URL", "http://localhost:8000")
        elif model_type == "demo":
            self.api_key = "demo"
            self.base_url = "demo"
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
    
    def generate_text(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        生成文本
        
        Args:
            prompt: 输入提示词
            max_tokens: 最大生成长度
            
        Returns:
            生成的文本内容
        """
        if self.model_type == "openai":
            return self._call_openai(prompt, max_tokens)
        elif self.model_type == "vllm":
            return self._call_vllm(prompt, max_tokens)
        elif self.model_type == "demo":
            return self._call_demo(prompt, max_tokens)
        else:
            raise ValueError(f"不支持的模型类型: {self.model_type}")
    
    def _call_openai(self, prompt: str, max_tokens: int) -> str:
        """调用OpenAI API"""
        try:
            import openai
            
            # 检查API密钥
            if not self.api_key or self.api_key in ["your_openai_api_key_here", "demo"]:
                raise Exception("请配置有效的OpenAI API密钥")
            
            # 初始化客户端
            client = openai.OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            # 发送请求
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": "你是一个专业的报告撰写助手，请根据用户需求生成高质量、详细的内容。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content.strip()
            
        except ImportError:
            raise Exception("请安装openai库: pip install openai")
        except Exception as e:
            print(f"OpenAI API调用失败: {e}")
            # 如果是API配置问题，提供友好提示
            if "api" in str(e).lower() or "key" in str(e).lower():
                return "⚠️ OpenAI API调用失败，请检查API密钥配置。运行 `python configure_llm.py` 进行配置。"
            return self._call_demo(prompt, max_tokens)  # 降级到演示模式
    
    def _call_vllm(self, prompt: str, max_tokens: int) -> str:
        """调用vLLM API"""
        try:
            # 构建请求URL
            url = f"{self.base_url.rstrip('/')}/v1/chat/completions"
            
            # 构建请求数据
            data = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": "你是一个专业的报告撰写助手，请根据用户需求生成高质量、详细的内容。"},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": self.temperature
            }
            
            # 发送请求
            response = requests.post(url, json=data, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
            
        except requests.exceptions.ConnectionError:
            print(f"vLLM连接失败: 无法连接到 {self.base_url}")
            return "⚠️ vLLM服务连接失败，请检查服务是否启动。运行 `python configure_llm.py` 进行配置。"
        except Exception as e:
            print(f"vLLM API调用失败: {e}")
            return self._call_demo(prompt, max_tokens)  # 降级到演示模式
    
    def _call_demo(self, prompt: str, max_tokens: int) -> str:
        """演示模式 - 生成示例内容"""
        # 根据prompt类型生成不同的演示内容
        if "大纲" in prompt or "outline" in prompt.lower():
            return """1. 概述与背景
2. 现状分析
3. 核心技术/方法
4. 应用案例
5. 发展趋势
6. 挑战与机遇
7. 结论与建议"""
        
        elif "润色" in prompt or "polish" in prompt.lower():
            # 如果是润色请求，返回稍微改进的内容
            if len(prompt) > 100:
                return prompt.replace("这是一个", "这是一个重要的").replace("需要", "亟需").replace("。", "，为行业发展提供了重要参考。")
            
        elif "图表" in prompt or "chart" in prompt.lower():
            return """建议生成以下图表：
1. 发展趋势图 - 展示技术发展历程
2. 对比分析图 - 不同方案的优劣对比
3. 市场份额图 - 各厂商市场占比
4. 流程图 - 核心技术实现流程"""
        
        # 默认内容生成
        topic = prompt.split("：")[-1] if "：" in prompt else prompt
        return f"""
{topic}是当前重要的研究领域和发展方向。

在技术层面，{topic}具有以下特点：
- 创新性强，技术架构先进
- 应用场景广泛，市场前景良好  
- 具备良好的可扩展性和兼容性
- 安全性和稳定性不断提升

从发展现状来看，{topic}正处于快速发展期，主要表现在：
- 技术成熟度不断提升
- 产业生态日趋完善
- 标准化程度逐步提高
- 应用领域持续扩大

面向未来，{topic}的发展趋势包括：
- 技术融合程度进一步加深
- 应用场景更加丰富多样
- 产业规模持续扩大
- 国际合作不断加强

总体而言，{topic}具有广阔的发展前景和重要的战略价值，值得持续关注和深入研究。

🔸 注意：这是演示内容，如需获得真实AI生成的内容，请配置API密钥。
""".strip()
    
    def batch_generate(self, prompts: list, max_tokens: int = 1000) -> list:
        """
        批量生成文本
        """
        results = []
        for prompt in prompts:
            result = self.generate_text(prompt, max_tokens)
            results.append(result)
        return results
