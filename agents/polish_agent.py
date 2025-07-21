"""
润色智能体
负责对生成的内容进行语言优化和质量提升
"""
import re
from typing import Dict, List
from utils.llm_client import LLMClient

class PolishAgent:
    """
    润色智能体
    
    设计理念：
    1. 质量提升：提高文本的语言质量和可读性
    2. 风格统一：确保整个报告的写作风格一致
    3. 逻辑优化：改善内容的逻辑结构和表达
    4. 专业化：提升文本的专业性和准确性
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        初始化润色智能体
        
        Args:
            llm_client: 大语言模型客户端
        """
        self.llm_client = llm_client
        self.agent_name = "PolishAgent"
        self.polish_aspects = [
            "语言流畅性",
            "逻辑清晰性", 
            "专业术语规范",
            "句式多样性",
            "表达准确性"
        ]
    
    def polish_content(self, content: str, section_title: str = None) -> str:
        """
        润色单个章节内容
        
        Args:
            content: 原始内容
            section_title: 章节标题（用于上下文）
            
        Returns:
            润色后的内容
            
        为什么需要润色：
        1. 质量保证：LLM生成的内容可能存在语言问题
        2. 专业性：提升内容的专业水准
        3. 可读性：让内容更易于理解和阅读
        4. 一致性：保持整个报告的风格统一
        """
        
        if not content.strip():
            return content
        
        try:
            # 基本文本清理
            cleaned_content = self._basic_text_cleaning(content)
            
            # LLM润色
            polished_content = self._llm_polish(cleaned_content, section_title)
            
            # 后处理
            final_content = self._post_polish_processing(polished_content)
            
            print(f"[{self.agent_name}] 已润色内容 ({len(content)} -> {len(final_content)} 字符)")
            return final_content
            
        except Exception as e:
            print(f"[{self.agent_name}] 润色失败: {e}")
            return self._basic_text_cleaning(content)  # 至少进行基本清理
    
    def polish_full_report(self, sections_content: Dict[str, str]) -> Dict[str, str]:
        """
        润色整个报告
        
        Args:
            sections_content: 包含所有章节内容的字典
            
        Returns:
            润色后的章节内容字典
            
        为什么需要整体润色：
        1. 全局一致性：确保整个报告的风格一致
        2. 章节衔接：优化章节间的过渡和衔接
        3. 重复检查：避免内容重复
        4. 整体优化：从整体角度优化报告质量
        """
        
        polished_sections = {}
        total_sections = len(sections_content)
        
        for i, (section_title, content) in enumerate(sections_content.items()):
            print(f"[{self.agent_name}] 正在润色第 {i+1}/{total_sections} 个章节: {section_title}")
            
            # 提供上下文信息
            context = {
                "all_sections": list(sections_content.keys()),
                "current_index": i,
                "previous_content": list(polished_sections.values())
            }
            
            polished_content = self._polish_with_context(content, section_title, context)
            polished_sections[section_title] = polished_content
        
        return polished_sections
    
    def _basic_text_cleaning(self, text: str) -> str:
        """
        基本文本清理
        
        为什么需要基本清理：
        1. 格式规范：统一基本格式
        2. 错误修正：修正明显的格式错误
        3. 预处理：为LLM润色做准备
        """
        
        # 规范化空白字符
        text = re.sub(r'\s+', ' ', text)
        
        # 规范化标点符号
        text = re.sub(r'[，,]\s*', '，', text)
        text = re.sub(r'[。.]\s*', '。', text)
        text = re.sub(r'[；;]\s*', '；', text)
        text = re.sub(r'[：:]\s*', '：', text)
        
        # 规范化段落分隔
        text = re.sub(r'。\s*', '。\n\n', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        # 移除首尾空白
        text = text.strip()
        
        return text
    
    def _llm_polish(self, content: str, section_title: str = None) -> str:
        """
        使用LLM进行内容润色
        
        为什么使用LLM润色：
        1. 智能化：理解语义，进行智能优化
        2. 全面性：同时处理多个润色维度
        3. 上下文感知：考虑上下文进行优化
        4. 专业性：提升专业表达水准
        """
        
        context_info = f"（章节：{section_title}）" if section_title else ""
        
        prompt = f"""
请对以下文本进行专业润色{context_info}：

原始文本：
{content}

润色要求：
1. 语言流畅性：确保语句通顺、表达自然
2. 逻辑清晰性：优化逻辑结构，增强条理性
3. 专业术语：使用准确的专业术语
4. 句式多样性：避免句式单调，增加表达层次
5. 表达准确性：确保意思准确，避免歧义

请保持原有的主要观点和信息不变，只优化表达方式。

润色后的文本：
"""
        
        polished_text = self.llm_client.generate_text(prompt, max_tokens=1500)
        return polished_text
    
    def _polish_with_context(self, content: str, section_title: str, context: Dict) -> str:
        """
        基于上下文进行润色
        
        为什么需要上下文润色：
        1. 一致性：确保风格与前面章节一致
        2. 衔接性：优化与其他章节的衔接
        3. 避免重复：检查并避免内容重复
        """
        
        previous_sections = context.get("previous_content", [])
        context_summary = ""
        
        if previous_sections:
            # 生成前面章节的简要概述
            recent_content = " ".join(previous_sections[-2:])[:300]  # 最近两个章节的前300字符
            context_summary = f"\n\n前面章节的风格参考：\n{recent_content}..."
        
        prompt = f"""
请润色以下章节内容，确保与整个报告的风格保持一致：

章节标题：{section_title}
{context_summary}

待润色内容：
{content}

润色要求：
1. 保持与前面章节的风格一致
2. 确保章节间的过渡自然
3. 避免与前面内容重复
4. 提升语言的专业性和可读性
5. 保持逻辑结构清晰

润色后的内容：
"""
        
        polished_text = self.llm_client.generate_text(prompt, max_tokens=1500)
        return polished_text
    
    def _post_polish_processing(self, text: str) -> str:
        """
        润色后的后处理
        
        为什么需要后处理：
        1. 质量检查：检查润色后的质量
        2. 格式规范：确保最终格式正确
        3. 错误修正：修正可能的润色错误
        """
        
        # 再次进行基本清理
        text = self._basic_text_cleaning(text)
        
        # 检查段落长度，避免过长的段落
        paragraphs = text.split('\n\n')
        processed_paragraphs = []
        
        for paragraph in paragraphs:
            if len(paragraph) > 500:  # 如果段落太长，尝试分割
                sentences = paragraph.split('。')
                current_para = ""
                
                for sentence in sentences:
                    if len(current_para + sentence) > 300 and current_para:
                        processed_paragraphs.append(current_para.strip() + '。')
                        current_para = sentence
                    else:
                        current_para += sentence + '。'
                
                if current_para.strip():
                    processed_paragraphs.append(current_para.strip())
            else:
                processed_paragraphs.append(paragraph)
        
        return '\n\n'.join(processed_paragraphs)
    
    def check_text_quality(self, text: str) -> Dict[str, any]:
        """
        检查文本质量
        
        为什么需要质量检查：
        1. 质量评估：评估润色效果
        2. 问题发现：发现可能的问题
        3. 改进建议：提供改进方向
        """
        
        quality_metrics = {
            "length": len(text),
            "paragraph_count": len(text.split('\n\n')),
            "avg_paragraph_length": 0,
            "sentence_count": len(re.findall(r'[。！？]', text)),
            "issues": []
        }
        
        paragraphs = [p for p in text.split('\n\n') if p.strip()]
        if paragraphs:
            quality_metrics["avg_paragraph_length"] = sum(len(p) for p in paragraphs) / len(paragraphs)
        
        # 检查潜在问题
        if quality_metrics["length"] < 200:
            quality_metrics["issues"].append("内容过短")
        
        if quality_metrics["avg_paragraph_length"] > 400:
            quality_metrics["issues"].append("段落过长")
        
        if quality_metrics["sentence_count"] < 5:
            quality_metrics["issues"].append("句子数量过少")
        
        return quality_metrics
    
    def generate_polish_summary(self, original_length: int, polished_length: int) -> str:
        """
        生成润色总结
        
        为什么需要润色总结：
        1. 透明度：让用户了解润色过程
        2. 质量反馈：提供质量改进信息
        3. 调试帮助：帮助系统调优
        """
        
        length_change = polished_length - original_length
        change_rate = (length_change / original_length) * 100 if original_length > 0 else 0
        
        summary = f"""
润色完成总结：
- 原始长度：{original_length} 字符
- 润色后长度：{polished_length} 字符
- 长度变化：{length_change:+d} 字符 ({change_rate:+.1f}%)
- 润色维度：{', '.join(self.polish_aspects)}
"""
        
        return summary
