# -*- coding: utf-8 -*-
"""
统一异常模块

定义项目中所有自定义异常类，提供统一的异常处理体系。
"""


class ZLPayError(Exception):
    """
    ZLPay Skill 基础异常类
    
    所有自定义异常的基类，提供统一的错误信息格式。
    """
    
    def __init__(self, message: str, error_code: str = None):
        """
        初始化异常
        
        Args:
            message: 错误消息
            error_code: 错误代码（可选）
        """
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class APIError(ZLPayError):
    """
    API 错误异常
    
    调用 API 时发生的错误，包括 HTTP 错误和业务逻辑错误。
    
    Attributes:
        status_code: HTTP 状态码
        message: 错误消息
        response_data: 原始响应数据
    """
    
    def __init__(self, status_code: int, message: str, response_data: dict = None):
        """
        初始化 API 错误
        
        Args:
            status_code: HTTP 状态码
            message: 错误消息
            response_data: 原始响应数据（可选）
        """
        self.status_code = status_code
        self.response_data = response_data
        error_code = f"HTTP_{status_code}"
        super().__init__(message, error_code)
    
    def __str__(self):
        return f"API Error {self.status_code}: {self.message}"


class SecurityError(ZLPayError):
    """
    安全错误异常
    
    签名验证失败、加密解密错误等安全问题。
    """
    
    def __init__(self, message: str):
        """
        初始化安全错误
        
        Args:
            message: 错误消息
        """
        super().__init__(message, "SECURITY_ERROR")


class ConfigError(ZLPayError):
    """
    配置错误异常
    
    缺少必需配置、配置格式错误等问题。
    """
    
    def __init__(self, message: str):
        """
        初始化配置错误
        
        Args:
            message: 错误消息
        """
        super().__init__(message, "CONFIG_ERROR")


class ValidationError(ZLPayError):
    """
    数据验证错误异常
    
    参数验证失败、数据格式错误等。
    """
    
    def __init__(self, message: str, field: str = None):
        """
        初始化验证错误
        
        Args:
            message: 错误消息
            field: 相关字段名（可选）
        """
        self.field = field
        error_code = f"VALIDATION_ERROR_{field.upper()}" if field else "VALIDATION_ERROR"
        super().__init__(message, error_code)


class NetworkError(ZLPayError):
    """
    网络错误异常
    
    网络连接失败、超时等问题。
    """
    
    def __init__(self, message: str, original_error: Exception = None):
        """
        初始化网络错误
        
        Args:
            message: 错误消息
            original_error: 原始异常（可选）
        """
        self.original_error = original_error
        super().__init__(message, "NETWORK_ERROR")


class CryptoError(ZLPayError):
    """
    加密错误异常
    
    加密、解密、签名、验签过程中的错误。
    """
    
    def __init__(self, message: str):
        """
        初始化加密错误
        
        Args:
            message: 错误消息
        """
        super().__init__(message, "CRYPTO_ERROR")


class BusinessError(ZLPayError):
    """
    业务逻辑错误异常
    
    业务规则验证失败、状态不正确等。
    """
    
    def __init__(self, message: str, business_code: str = None):
        """
        初始化业务错误
        
        Args:
            message: 错误消息
            business_code: 业务错误代码（可选）
        """
        self.business_code = business_code
        error_code = business_code or "BUSINESS_ERROR"
        super().__init__(message, error_code)
