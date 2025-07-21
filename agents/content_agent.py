"""
内容生成智能体
负责根据大纲章节生成具体的报告内容
"""
from typing import Dict, List
from utils.llm_client import LLMClient

class ContentAgent:
    """
    内容生成智能体
    
    设计理念：
    1. 专业性：生成高质量、专业的内容
    2. 一致性：保持整个报告的风格和语调一致
    3. 深度：根据主题提供有深度的分析和见解
    4. 可读性：确保内容易于理解和阅读
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        初始化内容生成智能体
        
        Args:
            llm_client: 大语言模型客户端
        """
        self.llm_client = llm_client
        self.agent_name = "ContentAgent"
        self.writing_style = "professional"  # 写作风格
        self.target_length = 500  # 每个章节的目标字数
    
    def generate_section_content(self, 
                                section_title: str, 
                                topic: str, 
                                context: Dict = None) -> str:
        """
        生成单个章节的内容
        
        Args:
            section_title: 章节标题
            topic: 报告主题
            context: 上下文信息（包括其他章节的信息）
            
        Returns:
            生成的章节内容
            
        为什么这样设计：
        1. 模块化：每个章节独立生成，便于并行处理
        2. 上下文感知：考虑其他章节的内容，保持一致性
        3. 质量控制：针对每个章节进行专门优化
        4. 灵活性：可以单独重新生成某个章节
        """
        
        # 构建生成提示
        prompt = self._build_content_prompt(section_title, topic, context)
        
        try:
            # 生成内容
            content = self.llm_client.generate_text(prompt, max_tokens=1200)
            
            # 后处理内容
            processed_content = self._post_process_content(content, section_title)
            
            print(f"[{self.agent_name}] 已生成章节 '{section_title}' 的内容 ({len(processed_content)}字符)")
            return processed_content
            
        except Exception as e:
            print(f"[{self.agent_name}] 章节 '{section_title}' 内容生成失败: {e}")
            return self._generate_fallback_content(section_title, topic)
    
    def generate_all_sections(self, 
                            outline: List[str], 
                            topic: str) -> Dict[str, str]:
        """
        生成所有章节的内容
        
        Args:
            outline: 报告大纲
            topic: 报告主题
            
        Returns:
            包含所有章节内容的字典
            
        为什么需要批量生成：
        1. 效率：减少重复的上下文建立
        2. 一致性：在同一个会话中生成，保持风格一致
        3. 优化：可以考虑章节间的关联性
        """
        sections_content = {}
        context = {"topic": topic, "outline": outline, "generated_sections": {}}
        
        for i, section_title in enumerate(outline):
            print(f"[{self.agent_name}] 正在生成第 {i+1}/{len(outline)} 个章节: {section_title}")
            
            # 更新上下文
            context["current_section_index"] = i
            context["generated_sections"] = sections_content
            
            # 生成内容
            content = self.generate_section_content(section_title, topic, context)
            sections_content[section_title] = content
        
        return sections_content
    
    def _build_content_prompt(self, 
                            section_title: str, 
                            topic: str, 
                            context: Dict = None) -> str:
        """
        构建内容生成的提示词
        
        为什么需要精心设计提示词：
        1. 质量控制：好的提示词能生成更高质量的内容
        2. 一致性：确保不同章节的风格一致
        3. 相关性：确保内容与主题和章节标题相关
        4. 结构化：生成结构清晰的内容
        """
        
        base_prompt = f"""
请为报告主题 "{topic}" 撰写章节 "{section_title}" 的详细内容。

要求：
1. 内容要专业、准确、有深度
2. 字数控制在 {self.target_length} 字左右
3. 结构清晰，逻辑严密
4. 包含具体的分析和见解
5. 适合 {self.writing_style} 的写作风格

"""
        
        # 添加上下文信息
        if context:
            outline = context.get("outline", [])
            current_index = context.get("current_section_index", 0)
            
            if outline:
                base_prompt += f"\n整个报告的大纲结构：\n"
                for i, section in enumerate(outline):
                    marker = " (当前章节)" if i == current_index else ""
                    base_prompt += f"{i+1}. {section}{marker}\n"
            
            # 添加已生成章节的信息
            generated_sections = context.get("generated_sections", {})
            if generated_sections:
                base_prompt += f"\n已生成的章节概要：\n"
                for title, content in generated_sections.items():
                    summary = content[:100] + "..." if len(content) > 100 else content
                    base_prompt += f"- {title}: {summary}\n"
        
        # 添加特定的写作指导
        base_prompt += f"""
请确保这个章节与整个报告的主题和其他章节保持一致。
内容应该有理有据，如果涉及数据或统计，请说明数据来源的重要性。
请用中文撰写，语言要专业但易懂。

章节内容：
"""
        
        return base_prompt
    
    def _post_process_content(self, content: str, section_title: str) -> str:
        """
        后处理生成的内容
        
        为什么需要后处理：
        1. 格式规范：统一内容格式
        2. 质量提升：修正明显的错误
        3. 结构优化：改善内容结构
        4. 长度控制：确保内容长度适中
        """
        
        # 移除多余的空白字符
        content = ' '.join(content.split())
        
        # 确保段落分隔
        content = content.replace('。', '。\n\n')
        content = '\n\n'.join(paragraph.strip() for paragraph in content.split('\n\n') if paragraph.strip())
        
        # 添加章节标识（如果需要）
        if not content.startswith(section_title):
            pass  # 暂时不添加标题，由格式化器处理
        
        # 长度检查和调整
        if len(content) < self.target_length * 0.5:
            print(f"[{self.agent_name}] 警告：章节 '{section_title}' 内容较短")
        elif len(content) > self.target_length * 2:
            print(f"[{self.agent_name}] 警告：章节 '{section_title}' 内容较长")
        
        return content
    
    def _generate_fallback_content(self, section_title: str, topic: str) -> str:
        """
        生成备用内容（当正常生成失败时）
        
        为什么需要备用方案：
        1. 鲁棒性：确保系统在异常情况下仍能工作
        2. 用户体验：避免返回空白内容
        3. 调试帮助：提供调试信息
        """
        return f"""
这里是关于 "{section_title}" 的内容。

在这个章节中，我们将深入探讨与 "{topic}" 相关的 "{section_title}" 方面的重要内容。

本章节将从以下几个角度进行分析：
- 基本概念和定义
- 现状和发展趋势
- 关键技术和方法
- 实际应用和案例
- 存在的挑战和问题
- 未来的发展方向

通过本章节的学习，读者将能够全面了解 "{section_title}" 在 "{topic}" 领域中的重要作用和价值。

注：此内容为系统自动生成的备用内容，建议进一步完善和补充具体信息。
"""
    
    def enhance_content_with_examples(self, content: str, section_title: str) -> str:
        """
        为内容添加实例和案例
        
        为什么需要添加实例：
        1. 可理解性：实例帮助读者理解抽象概念
        2. 说服力：具体案例增强论证效果
        3. 实用性：提供可参考的实际应用
        """
        
        prompt = f"""
请为以下内容添加相关的实例、案例或具体数据来支撑观点：

原始内容：
{content}

要求：
1. 添加 2-3 个相关的实例或案例
2. 保持原有内容的结构和逻辑
3. 实例要具体、可信
4. 与 "{section_title}" 主题密切相关

增强后的内容：
"""
        
        try:
            enhanced_content = self.llm_client.generate_text(prompt, max_tokens=1500)
            return enhanced_content
        except Exception as e:
            print(f"[{self.agent_name}] 内容增强失败: {e}")
            return content  # 返回原始内容
    
    def generate_content(self, section_title: str, report_type: str = "research") -> str:
        """
        生成内容的兼容方法
        
        Args:
            section_title: 章节标题或主题
            report_type: 报告类型
            
        Returns:
            生成的内容
        """
        return self.generate_section_content(section_title, section_title, {})
