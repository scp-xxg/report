"""
协调智能体 - 多智能体报告生成系统的核心调度器
负责协调各个智能体的工作，管理整个报告生成流程
"""
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
from agents import OutlineAgent, ContentAgent, PolishAgent, ChartAgent
from utils import LLMClient, ReportFormatter

class ReportCoordinator:
    """
    报告协调器
    
    设计理念：
    1. 中央调度：统一管理各个智能体的工作流程
    2. 流程控制：控制生成流程的顺序和依赖关系
    3. 质量管理：监控和保证最终报告的质量
    4. 资源管理：合理分配和使用系统资源
    5. 用户接口：提供简洁的用户调用接口
    """
    
    def __init__(self, 
                 model_type: str = "openai",
                 model_name: str = "gpt-3.5-turbo",
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 output_dir: str = "output"):
        """
        初始化报告协调器
        
        Args:
            model_type: 模型类型
            model_name: 模型名称  
            api_key: API密钥
            base_url: API基础URL
            output_dir: 输出目录
        """
        
        # 初始化LLM客户端
        self.llm_client = LLMClient(
            model_type=model_type,
            model_name=model_name,
            api_key=api_key,
            base_url=base_url
        )
        
        # 初始化各个智能体
        self.outline_agent = OutlineAgent(self.llm_client)
        self.content_agent = ContentAgent(self.llm_client)
        self.polish_agent = PolishAgent(self.llm_client)
        self.chart_agent = ChartAgent(self.llm_client, os.path.join(output_dir, "charts"))
        
        # 初始化报告格式化器
        self.formatter = ReportFormatter()
        
        # 设置输出目录
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # 工作流程状态
        self.workflow_status = {
            "outline_generated": False,
            "content_generated": False,
            "content_polished": False,
            "charts_generated": False,
            "report_formatted": False
        }
        
        self.generation_log = []
        
        print(f"[ReportCoordinator] 系统初始化完成")
        print(f"[ReportCoordinator] 模型: {model_type}/{model_name}")
        print(f"[ReportCoordinator] 输出目录: {output_dir}")
    
    def generate_report(self, 
                       topic: str, 
                       report_type: str = "research",
                       enable_charts: bool = True,
                       enable_polish: bool = True,
                       output_formats: List[str] = ["markdown", "docx"]) -> Dict:
        """
        生成完整报告
        
        Args:
            topic: 报告主题
            report_type: 报告类型 (research, business, technical, academic)
            enable_charts: 是否生成图表
            enable_polish: 是否进行润色
            output_formats: 输出格式列表
            
        Returns:
            包含报告内容和元数据的字典
            
        为什么这样设计工作流程：
        1. 分步骤：将复杂任务分解为可管理的步骤
        2. 依赖管理：确保步骤间的正确依赖关系
        3. 可配置：用户可以选择启用/禁用某些功能
        4. 可追踪：记录每个步骤的执行状态
        5. 容错性：单个步骤失败不会影响整个流程
        """
        
        start_time = time.time()
        self._log(f"开始生成报告: {topic}")
        
        try:
            # 步骤1: 生成大纲
            self._log("步骤1: 生成报告大纲")
            outline = self._generate_outline(topic, report_type)
            
            # 步骤2: 生成内容
            self._log("步骤2: 生成章节内容")
            sections_content = self._generate_content(outline, topic)
            
            # 步骤3: 润色内容（可选）
            if enable_polish:
                self._log("步骤3: 润色报告内容")
                sections_content = self._polish_content(sections_content)
            else:
                self._log("步骤3: 跳过润色（用户选择）")
            
            # 步骤4: 生成图表（可选）
            charts = {}
            if enable_charts:
                self._log("步骤4: 分析和生成图表")
                charts = self._generate_charts(sections_content)
            else:
                self._log("步骤4: 跳过图表生成（用户选择）")
            
            # 步骤5: 格式化和输出
            self._log("步骤5: 格式化和输出报告")
            report_data = {
                "title": topic,
                "type": report_type,
                "outline": outline,
                "sections": sections_content,
                "charts": charts,
                "generation_time": datetime.now().isoformat(),
                "processing_time": time.time() - start_time
            }
            
            output_files = self._format_and_save_report(report_data, output_formats)
            
            # 生成最终报告
            final_report = {
                "status": "success",
                "topic": topic,
                "report_type": report_type,
                "data": report_data,
                "output_files": output_files,
                "workflow_status": self.workflow_status,
                "generation_log": self.generation_log,
                "processing_time": time.time() - start_time
            }
            
            self._log(f"报告生成完成，耗时 {final_report['processing_time']:.2f} 秒")
            return final_report
            
        except Exception as e:
            error_report = {
                "status": "error",
                "topic": topic,
                "error": str(e),
                "workflow_status": self.workflow_status,
                "generation_log": self.generation_log,
                "processing_time": time.time() - start_time
            }
            
            self._log(f"报告生成失败: {e}")
            return error_report
    
    def _generate_outline(self, topic: str, report_type: str) -> List[str]:
        """
        生成报告大纲
        
        为什么独立封装：
        1. 可测试：独立测试大纲生成功能
        2. 可重用：可以单独调用生成大纲
        3. 状态管理：更新工作流程状态
        """
        try:
            outline = self.outline_agent.generate_outline(topic, report_type)
            self.workflow_status["outline_generated"] = True
            self._log(f"大纲生成成功，包含 {len(outline)} 个章节")
            return outline
        except Exception as e:
            self._log(f"大纲生成失败: {e}")
            raise Exception(f"大纲生成失败: {e}")
    
    def _generate_content(self, outline: List[str], topic: str) -> Dict[str, str]:
        """
        生成所有章节内容
        
        为什么需要协调：
        1. 进度跟踪：跟踪内容生成进度
        2. 资源管理：合理分配生成资源
        3. 错误处理：处理单个章节的生成错误
        """
        try:
            sections_content = self.content_agent.generate_all_sections(outline, topic)
            self.workflow_status["content_generated"] = True
            self._log(f"内容生成成功，共 {len(sections_content)} 个章节")
            return sections_content
        except Exception as e:
            self._log(f"内容生成失败: {e}")
            raise Exception(f"内容生成失败: {e}")
    
    def _polish_content(self, sections_content: Dict[str, str]) -> Dict[str, str]:
        """
        润色报告内容
        
        为什么需要润色协调：
        1. 质量控制：确保润色质量
        2. 进度管理：管理润色进度
        3. 一致性：保持整体润色风格一致
        """
        try:
            polished_content = self.polish_agent.polish_full_report(sections_content)
            self.workflow_status["content_polished"] = True
            self._log("内容润色完成")
            return polished_content
        except Exception as e:
            self._log(f"内容润色失败: {e}")
            # 润色失败时返回原始内容
            return sections_content
    
    def _generate_charts(self, sections_content: Dict[str, str]) -> Dict[str, str]:
        """
        生成图表
        
        为什么需要图表协调：
        1. 需求分析：分析内容的图表需求
        2. 生成管理：管理图表生成过程
        3. 质量控制：确保图表质量和相关性
        """
        try:
            # 分析图表需求
            chart_requirements = self.chart_agent.analyze_content_for_charts(sections_content)
            
            # 生成图表
            if chart_requirements:
                charts = self.chart_agent.generate_charts(chart_requirements)
                self.workflow_status["charts_generated"] = True
                self._log(f"图表生成成功，共 {len(charts)} 个图表")
                return charts
            else:
                self._log("未发现图表需求")
                return {}
                
        except Exception as e:
            self._log(f"图表生成失败: {e}")
            return {}
    
    def _format_and_save_report(self, report_data: Dict, output_formats: List[str]) -> Dict[str, str]:
        """
        格式化和保存报告
        
        为什么需要多格式输出：
        1. 用户需求：不同用户偏好不同格式
        2. 用途不同：不同格式适合不同用途
        3. 兼容性：确保在不同环境下的兼容性
        """
        output_files = {}
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_filename = f"report_{timestamp}"
        
        try:
            for format_type in output_formats:
                if format_type == "markdown":
                    content = self.formatter.format_markdown(report_data)
                    filepath = os.path.join(self.output_dir, f"{base_filename}.md")
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    output_files["markdown"] = filepath
                    
                elif format_type == "json":
                    content = self.formatter.format_json(report_data)
                    filepath = os.path.join(self.output_dir, f"{base_filename}.json")
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    output_files["json"] = filepath
                    
                elif format_type == "docx":
                    filepath = os.path.join(self.output_dir, f"{base_filename}.docx")
                    try:
                        self.formatter.format_docx(report_data, filepath)
                        output_files["docx"] = filepath
                    except ImportError:
                        self._log("警告：python-docx未安装，跳过Word格式输出")
                    except Exception as e:
                        self._log(f"Word格式输出失败: {e}")
            
            self.workflow_status["report_formatted"] = True
            self._log(f"报告已保存为 {len(output_files)} 种格式")
            return output_files
            
        except Exception as e:
            self._log(f"报告格式化失败: {e}")
            raise Exception(f"报告格式化失败: {e}")
    
    def _log(self, message: str):
        """
        记录日志
        
        为什么需要日志：
        1. 调试：帮助调试和问题排查
        2. 监控：监控系统运行状态
        3. 用户反馈：向用户提供进度信息
        4. 审计：记录系统操作历史
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.generation_log.append(log_entry)
        print(f"[ReportCoordinator] {message}")
    
    def get_system_status(self) -> Dict:
        """
        获取系统状态
        
        为什么需要状态查询：
        1. 监控：实时监控系统状态
        2. 调试：帮助问题诊断
        3. 用户反馈：向用户展示系统状态
        """
        return {
            "workflow_status": self.workflow_status,
            "recent_logs": self.generation_log[-10:],  # 最近10条日志
            "agents_status": {
                "outline_agent": self.outline_agent.agent_name,
                "content_agent": self.content_agent.agent_name,
                "polish_agent": self.polish_agent.agent_name,
                "chart_agent": self.chart_agent.agent_name
            },
            "output_directory": self.output_dir
        }
    
    def reset_workflow(self):
        """
        重置工作流程状态
        
        为什么需要重置：
        1. 清理：清理上次生成的状态
        2. 准备：为新的生成任务做准备
        3. 隔离：避免不同任务间的状态干扰
        """
        self.workflow_status = {
            "outline_generated": False,
            "content_generated": False,
            "content_polished": False,
            "charts_generated": False,
            "report_formatted": False
        }
        self.generation_log = []
        self._log("工作流程状态已重置")
