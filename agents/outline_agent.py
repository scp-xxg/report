"""
目录生成智能体
负责根据主题生成报告的大纲结构
"""
from typing import List, Dict
from utils.llm_client import LLMClient

class OutlineAgent:
    """
    目录生成智能体
    
    设计理念：
    1. 专业性：基于领域知识生成结构化的目录
    2. 逻辑性：确保目录的逻辑顺序和层次结构
    3. 完整性：涵盖主题的各个重要方面
    4. 可定制：支持不同类型报告的目录模板
    """
    
    def __init__(self, llm_client: LLMClient):
        """
        初始化目录生成智能体
        
        Args:
            llm_client: 大语言模型客户端
        """
        self.llm_client = llm_client
        self.agent_name = "OutlineAgent"
    
    def generate_outline(self, topic: str, report_type: str = "research") -> List[str]:
        """
        生成报告大纲
        
        Args:
            topic: 报告主题
            report_type: 报告类型 (research, business, technical, academic)
            
        Returns:
            大纲列表
            
        为什么这样设计：
        1. 结构化思维：先搭建框架再填充内容，符合人类写作习惯
        2. 质量保证：好的大纲是高质量报告的基础
        3. 效率提升：其他智能体可以并行工作于不同章节
        4. 一致性：确保报告的逻辑一致性和完整性
        """
        
        # 根据报告类型选择不同的提示模板
        prompt_template = self._get_prompt_template(report_type)
        prompt = prompt_template.format(topic=topic)
        
        try:
            # 调用LLM生成大纲
            response = self.llm_client.generate_text(prompt, max_tokens=800)
            
            # 解析和清理大纲
            outline = self._parse_outline(response)
            
            # 验证大纲质量
            validated_outline = self._validate_outline(outline, topic)
            
            print(f"[{self.agent_name}] 已为主题 '{topic}' 生成 {len(validated_outline)} 个章节的大纲")
            return validated_outline
            
        except Exception as e:
            print(f"[{self.agent_name}] 大纲生成失败: {e}")
            # 返回默认大纲作为备选方案
            return self._get_default_outline(topic)
    
    def _get_prompt_template(self, report_type: str) -> str:
        """
        获取不同类型报告的提示模板
        
        为什么需要不同模板：
        1. 专业性：不同类型的报告有不同的结构要求
        2. 针对性：提高生成内容的相关性和专业性
        3. 标准化：符合行业标准和读者期望
        """
        templates = {
            "research": """
请为研究报告主题 "{topic}" 生成一个详细的大纲。
报告应包含以下几个部分，请生成具体的章节标题：

要求：
1. 包含引言、文献综述、方法论、分析、结论等部分
2. 每个章节标题要具体明确
3. 逻辑结构清晰，层次分明
4. 适合学术研究报告的风格

请以数字列表的形式输出，每行一个章节标题。
""",
            
            "business": """
请为商业报告主题 "{topic}" 生成一个专业的大纲。
报告应适合商业环境，包含以下方面：

要求：
1. 包含执行摘要、市场分析、竞争分析、策略建议等
2. 每个章节要对决策者有价值
3. 结构要便于快速阅读和理解
4. 包含数据分析和可行性分析

请以数字列表的形式输出，每行一个章节标题。
""",
            
            "technical": """
请为技术报告主题 "{topic}" 生成一个详细的大纲。
报告应适合技术人员阅读：

要求：
1. 包含技术背景、架构设计、实现方案、测试验证等
2. 每个章节要有技术深度
3. 包含技术细节和最佳实践
4. 便于技术团队理解和实施

请以数字列表的形式输出，每行一个章节标题。
""",
            
            "academic": """
请为学术论文主题 "{topic}" 生成一个规范的大纲。
论文应符合学术写作标准：

要求：
1. 包含摘要、引言、相关工作、方法、实验、结论等
2. 符合学术论文的标准结构
3. 每个部分要有学术价值
4. 适合期刊或会议发表

请以数字列表的形式输出，每行一个章节标题。
"""
        }
        
        return templates.get(report_type, templates["research"])
    
    def _parse_outline(self, response: str) -> List[str]:
        """
        解析LLM生成的大纲文本
        
        为什么需要解析：
        1. 格式统一：LLM的输出格式可能不一致
        2. 数据清理：移除无关内容和格式字符
        3. 结构化：转换为程序可处理的数据结构
        """
        lines = response.strip().split('\n')
        outline = []
        
        for line in lines:
            line = line.strip()
            # 移除编号和特殊字符
            line = line.lstrip('0123456789.- ')
            
            # 过滤空行和无效内容
            if line and len(line) > 3:
                outline.append(line)
        
        return outline[:10]  # 限制章节数量，避免过长
    
    def _validate_outline(self, outline: List[str], topic: str) -> List[str]:
        """
        验证大纲的质量和相关性
        
        为什么需要验证：
        1. 质量控制：确保生成的大纲符合要求
        2. 相关性：检查章节是否与主题相关
        3. 完整性：确保包含必要的部分
        4. 逻辑性：检查章节的逻辑顺序
        """
        # 基本验证
        if len(outline) < 3:
            print(f"[{self.agent_name}] 警告：大纲章节过少，补充默认章节")
            return self._get_default_outline(topic)
        
        # 检查是否包含基本部分
        has_intro = any('引言' in section or '概述' in section or '导论' in section 
                       for section in outline)
        has_conclusion = any('结论' in section or '总结' in section or '展望' in section 
                           for section in outline)
        
        if not has_intro:
            outline.insert(0, f"{topic}概述")
        if not has_conclusion:
            outline.append("结论与展望")
        
        return outline
    
    def _get_default_outline(self, topic: str) -> List[str]:
        """
        获取默认大纲作为备选方案
        
        为什么需要默认大纲：
        1. 容错性：当LLM生成失败时的备选方案
        2. 基础结构：提供最基本的报告结构
        3. 可靠性：确保系统的鲁棒性
        """
        return [
            f"{topic}概述",
            f"{topic}的背景与意义",
            f"{topic}的现状分析",
            f"{topic}的关键技术/方法",
            f"{topic}的应用案例",
            f"{topic}面临的挑战",
            f"{topic}的发展趋势",
            "结论与建议"
        ]
    
    def refine_outline(self, outline: List[str], feedback: str) -> List[str]:
        """
        根据反馈优化大纲
        
        为什么需要优化功能：
        1. 迭代改进：支持多轮优化
        2. 用户参与：允许用户提供反馈
        3. 质量提升：通过反馈提高大纲质量
        """
        prompt = f"""
请根据以下反馈优化报告大纲：

原始大纲：
{chr(10).join(f"{i+1}. {section}" for i, section in enumerate(outline))}

反馈意见：
{feedback}

请提供优化后的大纲，以数字列表形式输出：
"""
        
        try:
            response = self.llm_client.generate_text(prompt, max_tokens=600)
            refined_outline = self._parse_outline(response)
            print(f"[{self.agent_name}] 已根据反馈优化大纲")
            return refined_outline
        except Exception as e:
            print(f"[{self.agent_name}] 大纲优化失败: {e}")
            return outline  # 返回原始大纲
