"""
图表生成智能体
负责生成报告中需要的图表、表格和数据可视化
"""
import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any, Optional
from utils.llm_client import LLMClient

# 设置中文字体（避免中文显示问题）
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

class ChartAgent:
    """
    图表生成智能体
    
    设计理念：
    1. 数据驱动：基于内容自动识别可视化需求
    2. 多样性：支持多种类型的图表和可视化
    3. 美观性：生成专业、美观的图表
    4. 智能化：自动选择最适合的图表类型
    """
    
    def __init__(self, llm_client: LLMClient, output_dir: str = "output/charts"):
        """
        初始化图表生成智能体
        
        Args:
            llm_client: 大语言模型客户端
            output_dir: 图表输出目录
        """
        self.llm_client = llm_client
        self.agent_name = "ChartAgent"
        self.output_dir = output_dir
        self.chart_counter = 0
        
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 支持的图表类型
        self.chart_types = {
            "bar": "柱状图",
            "line": "折线图", 
            "pie": "饼图",
            "scatter": "散点图",
            "histogram": "直方图",
            "box": "箱线图",
            "heatmap": "热力图",
            "table": "表格"
        }
    
    def analyze_content_for_charts(self, sections_content: Dict[str, str]) -> List[Dict]:
        """
        分析内容并识别图表需求
        
        Args:
            sections_content: 章节内容字典
            
        Returns:
            图表需求列表
            
        为什么需要内容分析：
        1. 智能化：自动识别哪些内容适合可视化
        2. 相关性：确保图表与内容高度相关
        3. 价值最大化：选择最有价值的数据进行可视化
        4. 用户体验：减少用户手动指定的工作量
        """
        
        chart_requirements = []
        
        for section_title, content in sections_content.items():
            # 使用LLM分析内容的可视化需求
            requirements = self._analyze_section_for_visualization(section_title, content)
            chart_requirements.extend(requirements)
        
        print(f"[{self.agent_name}] 识别出 {len(chart_requirements)} 个图表需求")
        return chart_requirements
    
    def _analyze_section_for_visualization(self, section_title: str, content: str) -> List[Dict]:
        """
        分析单个章节的可视化需求
        
        为什么需要章节级分析：
        1. 精确性：针对具体内容进行分析
        2. 上下文：考虑章节的特定上下文
        3. 适配性：根据不同类型的内容选择合适的可视化
        """
        
        prompt = f"""
请分析以下章节内容，识别可以用图表可视化的数据和概念：

章节标题：{section_title}
章节内容：
{content}

请识别以下类型的可视化需求：
1. 数值比较（适合柱状图、折线图）
2. 占比关系（适合饼图）
3. 趋势变化（适合折线图）
4. 分类统计（适合柱状图）
5. 相关关系（适合散点图）
6. 流程步骤（适合流程图）
7. 层次结构（适合树形图）
8. 对比表格（适合表格）

请以JSON格式返回，包含以下字段：
- chart_type: 图表类型（bar/line/pie/scatter/table/flow等）
- title: 图表标题
- description: 图表描述
- data_concept: 数据概念描述
- priority: 优先级（1-5，5最高）

如果没有明显的可视化需求，请返回空数组 []。

返回格式：
[
  {{
    "chart_type": "bar",
    "title": "示例图表标题",
    "description": "图表描述",
    "data_concept": "数据概念",
    "priority": 3
  }}
]
"""
        
        try:
            response = self.llm_client.generate_text(prompt, max_tokens=800)
            
            # 尝试解析JSON响应
            requirements = self._parse_chart_requirements(response)
            
            # 添加章节信息
            for req in requirements:
                req["section_title"] = section_title
                req["section_content"] = content[:200] + "..."  # 保存部分内容作为参考
            
            return requirements
            
        except Exception as e:
            print(f"[{self.agent_name}] 章节 '{section_title}' 可视化分析失败: {e}")
            return []
    
    def _parse_chart_requirements(self, response: str) -> List[Dict]:
        """
        解析LLM返回的图表需求
        
        为什么需要解析：
        1. 结构化：将文本转换为结构化数据
        2. 验证：验证数据格式的正确性
        3. 清理：清理和标准化数据
        """
        
        try:
            # 尝试直接解析JSON
            requirements = json.loads(response)
            
            # 验证和清理数据
            validated_requirements = []
            for req in requirements:
                if self._validate_chart_requirement(req):
                    validated_requirements.append(req)
            
            return validated_requirements
            
        except json.JSONDecodeError:
            # 如果JSON解析失败，尝试从文本中提取信息
            return self._extract_requirements_from_text(response)
    
    def _validate_chart_requirement(self, requirement: Dict) -> bool:
        """
        验证图表需求的有效性
        
        为什么需要验证：
        1. 质量控制：确保生成的需求是有效的
        2. 错误预防：避免无效数据导致后续错误
        3. 标准化：确保数据格式符合标准
        """
        
        required_fields = ["chart_type", "title", "description"]
        
        for field in required_fields:
            if field not in requirement or not requirement[field]:
                return False
        
        # 检查图表类型是否支持
        if requirement["chart_type"] not in self.chart_types:
            return False
        
        return True
    
    def generate_charts(self, chart_requirements: List[Dict]) -> Dict[str, str]:
        """
        根据需求生成图表
        
        Args:
            chart_requirements: 图表需求列表
            
        Returns:
            图表文件路径字典
        """
        
        generated_charts = {}
        
        for requirement in chart_requirements:
            try:
                chart_path = self._generate_single_chart(requirement)
                if chart_path:
                    generated_charts[requirement["title"]] = chart_path
                    print(f"[{self.agent_name}] 已生成图表: {requirement['title']}")
                
            except Exception as e:
                print(f"[{self.agent_name}] 图表生成失败 '{requirement['title']}': {e}")
        
        return generated_charts
    
    def _generate_single_chart(self, requirement: Dict) -> Optional[str]:
        """
        生成单个图表
        
        为什么需要单独生成：
        1. 模块化：每个图表独立生成，便于调试
        2. 容错性：单个图表失败不影响其他图表
        3. 可扩展：易于添加新的图表类型
        """
        
        chart_type = requirement["chart_type"]
        title = requirement["title"]
        
        # 生成模拟数据（实际项目中可能从数据库或API获取）
        data = self._generate_mock_data(requirement)
        
        # 生成文件名
        self.chart_counter += 1
        filename = f"chart_{self.chart_counter:03d}_{chart_type}_{title[:20]}.png"
        filepath = os.path.join(self.output_dir, filename)
        
        # 根据图表类型生成图表
        if chart_type == "bar":
            self._create_bar_chart(data, title, filepath)
        elif chart_type == "line":
            self._create_line_chart(data, title, filepath)
        elif chart_type == "pie":
            self._create_pie_chart(data, title, filepath)
        elif chart_type == "scatter":
            self._create_scatter_chart(data, title, filepath)
        elif chart_type == "table":
            self._create_table_chart(data, title, filepath)
        else:
            print(f"[{self.agent_name}] 不支持的图表类型: {chart_type}")
            return None
        
        return filepath
    
    def _generate_mock_data(self, requirement: Dict) -> Dict:
        """
        生成模拟数据
        
        为什么需要模拟数据：
        1. 演示效果：在没有真实数据时展示图表效果
        2. 原型开发：快速原型开发和测试
        3. 模板作用：为用户提供数据格式参考
        4. 完整性：确保系统功能的完整性
        
        在实际应用中，这个函数应该：
        1. 从数据库查询相关数据
        2. 调用外部API获取数据
        3. 分析文本内容提取数据
        4. 让用户提供真实数据
        """
        
        chart_type = requirement["chart_type"]
        
        # 根据不同图表类型生成相应的模拟数据
        if chart_type == "bar":
            return {
                "categories": ["类别A", "类别B", "类别C", "类别D", "类别E"],
                "values": [23, 45, 56, 78, 32]
            }
        elif chart_type == "line":
            return {
                "x_values": ["2019", "2020", "2021", "2022", "2023"],
                "y_values": [10, 15, 23, 28, 35]
            }
        elif chart_type == "pie":
            return {
                "labels": ["部分1", "部分2", "部分3", "部分4"],
                "values": [30, 25, 25, 20]
            }
        elif chart_type == "scatter":
            return {
                "x_values": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
                "y_values": [2, 5, 3, 8, 7, 10, 9, 12, 15, 14]
            }
        elif chart_type == "table":
            return {
                "headers": ["项目", "数值1", "数值2", "比例"],
                "rows": [
                    ["项目A", "100", "80", "80%"],
                    ["项目B", "120", "100", "83%"],
                    ["项目C", "90", "85", "94%"],
                    ["项目D", "110", "95", "86%"]
                ]
            }
        else:
            return {}
    
    def _create_bar_chart(self, data: Dict, title: str, filepath: str):
        """创建柱状图"""
        plt.figure(figsize=(10, 6))
        plt.bar(data["categories"], data["values"], color='skyblue', edgecolor='navy', alpha=0.7)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('类别', fontsize=12)
        plt.ylabel('数值', fontsize=12)
        plt.xticks(rotation=45)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_line_chart(self, data: Dict, title: str, filepath: str):
        """创建折线图"""
        plt.figure(figsize=(10, 6))
        plt.plot(data["x_values"], data["y_values"], marker='o', linewidth=2, markersize=8)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('时间', fontsize=12)
        plt.ylabel('数值', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_pie_chart(self, data: Dict, title: str, filepath: str):
        """创建饼图"""
        plt.figure(figsize=(8, 8))
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        plt.pie(data["values"], labels=data["labels"], autopct='%1.1f%%', 
                colors=colors, startangle=90)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_scatter_chart(self, data: Dict, title: str, filepath: str):
        """创建散点图"""
        plt.figure(figsize=(10, 6))
        plt.scatter(data["x_values"], data["y_values"], alpha=0.7, s=100)
        plt.title(title, fontsize=16, fontweight='bold')
        plt.xlabel('X值', fontsize=12)
        plt.ylabel('Y值', fontsize=12)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _create_table_chart(self, data: Dict, title: str, filepath: str):
        """创建表格图"""
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.axis('tight')
        ax.axis('off')
        
        table = ax.table(cellText=data["rows"], colLabels=data["headers"],
                        cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1.2, 1.5)
        
        # 设置表格样式
        for i in range(len(data["headers"])):
            table[(0, i)].set_facecolor('#4CAF50')
            table[(0, i)].set_text_props(weight='bold', color='white')
        
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
    
    def _extract_requirements_from_text(self, text: str) -> List[Dict]:
        """
        从文本中提取图表需求（当JSON解析失败时的备选方案）
        
        为什么需要备选方案：
        1. 鲁棒性：确保系统在LLM输出格式不标准时仍能工作
        2. 容错性：提高系统的容错能力
        3. 用户体验：避免因格式问题导致功能失效
        """
        
        # 这是一个简化的实现，实际项目中可以使用更复杂的文本解析
        requirements = []
        
        # 查找常见的图表类型关键词
        chart_keywords = {
            "柱状图": "bar",
            "条形图": "bar", 
            "折线图": "line",
            "饼图": "pie",
            "散点图": "scatter",
            "表格": "table"
        }
        
        for keyword, chart_type in chart_keywords.items():
            if keyword in text:
                requirements.append({
                    "chart_type": chart_type,
                    "title": f"{keyword}示例",
                    "description": f"基于内容生成的{keyword}",
                    "priority": 3
                })
        
        return requirements[:3]  # 最多返回3个需求
