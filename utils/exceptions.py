# 多智能体报告生成系统 - 异常处理模块

class ReportGenerationError(Exception):
    """报告生成相关错误基类"""
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code

class LLMConnectionError(ReportGenerationError):
    """LLM连接错误"""
    def __init__(self, message: str = "无法连接到大语言模型服务"):
        super().__init__(message, "LLM_CONNECTION_ERROR")

class ConfigurationError(ReportGenerationError):
    """配置错误"""
    def __init__(self, message: str = "配置参数错误"):
        super().__init__(message, "CONFIGURATION_ERROR")

class ValidationError(ReportGenerationError):
    """数据验证错误"""
    def __init__(self, message: str = "输入数据验证失败"):
        super().__init__(message, "VALIDATION_ERROR")

class GenerationTimeoutError(ReportGenerationError):
    """生成超时错误"""
    def __init__(self, message: str = "报告生成超时"):
        super().__init__(message, "GENERATION_TIMEOUT")

class FileProcessingError(ReportGenerationError):
    """文件处理错误"""
    def __init__(self, message: str = "文件处理失败"):
        super().__init__(message, "FILE_PROCESSING_ERROR")
