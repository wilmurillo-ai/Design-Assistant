"""
SSE SDK 异常定义
"""


class SSEError(Exception):
    """SSE基础异常"""
    
    def __init__(self, message: str, code: str = None):
        super().__init__(message)
        self.message = message
        self.code = code
    
    def __str__(self):
        if self.code:
            return f"[{self.code}] {self.message}"
        return self.message


class AuthenticationError(SSEError):
    """认证错误"""
    pass


class RateLimitError(SSEError):
    """频率限制错误"""
    pass


class ValidationError(SSEError):
    """参数验证错误"""
    pass


class NotFoundError(SSEError):
    """资源不存在"""
    pass
