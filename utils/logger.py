# 日志管理器 - 统一的日志记录

import os
import logging
from datetime import datetime
from typing import Optional

class LogManager:
    """日志管理器"""
    
    def __init__(self, 
                 log_dir: str = "logs",
                 log_level: str = "INFO",
                 enable_file_logging: bool = True,
                 enable_console_logging: bool = True):
        """
        初始化日志管理器
        
        Args:
            log_dir: 日志目录
            log_level: 日志级别
            enable_file_logging: 是否启用文件日志
            enable_console_logging: 是否启用控制台日志
        """
        self.log_dir = log_dir
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.enable_file_logging = enable_file_logging
        self.enable_console_logging = enable_console_logging
        
        # 创建日志目录
        if self.enable_file_logging:
            os.makedirs(self.log_dir, exist_ok=True)
        
        # 设置日志格式
        self.formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 配置根日志器
        self._setup_root_logger()
    
    def _setup_root_logger(self):
        """设置根日志器"""
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # 清除现有的处理器
        root_logger.handlers.clear()
        
        # 添加控制台处理器
        if self.enable_console_logging:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(self.formatter)
            root_logger.addHandler(console_handler)
        
        # 添加文件处理器
        if self.enable_file_logging:
            log_file = os.path.join(
                self.log_dir, 
                f"report_system_{datetime.now().strftime('%Y%m%d')}.log"
            )
            file_handler = logging.FileHandler(log_file, encoding='utf-8')
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(self.formatter)
            root_logger.addHandler(file_handler)
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        获取指定名称的日志器
        
        Args:
            name: 日志器名称
            
        Returns:
            日志器实例
        """
        return logging.getLogger(name)
    
    def log_agent_activity(self, agent_name: str, activity: str, status: str = "INFO"):
        """
        记录智能体活动
        
        Args:
            agent_name: 智能体名称
            activity: 活动描述
            status: 状态级别
        """
        logger = self.get_logger(f"Agent.{agent_name}")
        
        if status.upper() == "ERROR":
            logger.error(f"[{agent_name}] {activity}")
        elif status.upper() == "WARNING":
            logger.warning(f"[{agent_name}] {activity}")
        else:
            logger.info(f"[{agent_name}] {activity}")
    
    def log_user_action(self, action: str, details: Optional[str] = None):
        """
        记录用户操作
        
        Args:
            action: 操作类型
            details: 操作详情
        """
        logger = self.get_logger("UserAction")
        message = f"用户操作: {action}"
        if details:
            message += f" - {details}"
        logger.info(message)
    
    def log_performance(self, operation: str, duration: float, details: Optional[str] = None):
        """
        记录性能数据
        
        Args:
            operation: 操作名称
            duration: 耗时（秒）
            details: 附加信息
        """
        logger = self.get_logger("Performance")
        message = f"性能统计: {operation} 耗时 {duration:.2f}s"
        if details:
            message += f" - {details}"
        logger.info(message)

# 全局日志管理器实例
log_manager = LogManager()
