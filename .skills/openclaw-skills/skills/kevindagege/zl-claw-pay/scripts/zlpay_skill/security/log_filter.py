# -*- coding: utf-8 -*-
"""
日志脱敏过滤器 - 强制脱敏敏感信息
"""

import re
import logging


class SensitiveDataFilter(logging.Filter):
    """日志脱敏过滤器 - 自动脱敏敏感信息"""
    
    # 脱敏规则（正则表达式 + 替换函数）
    PATTERNS = [
        # 手机号（中国大陆）：保留前3位和后4位
        (
            re.compile(r'1[3-9]\d{9}'),
            lambda m: m.group(0)[:3] + '****' + m.group(0)[-4:]
        ),
        
        # Bearer Token：保留前8位
        (
            re.compile(r'Bearer\s+([A-Za-z0-9_-]{20,})'),
            lambda m: 'Bearer ' + m.group(1)[:8] + '****'
        ),
        
        # API Key（带前缀 ak_/sk_/key_ 等，32位以上）：保留前8位
        (
            re.compile(r'\b((?:ak_|sk_|key_|api_|secret_|token_)[A-Za-z0-9_-]{28,})\b', re.IGNORECASE),
            lambda m: m.group(1)[:8] + '****'
        ),
        
        # 身份证号（18位）：保留前6位和后4位
        (
            re.compile(r'\b(\d{6})\d{8}([\dXx]{4})\b'),
            lambda m: m.group(1) + '****' + m.group(2)
        ),
        
        # 银行卡号（16-19位）：保留前6位和后4位
        (
            re.compile(r'\b(\d{6})\d{6,9}(\d{4})\b'),
            lambda m: m.group(1) + '****' + m.group(2)
        ),
    ]
    
    def filter(self, record):
        # type: (logging.LogRecord) -> bool
        """
        过滤日志记录，脱敏敏感信息
        
        Args:
            record: 日志记录
            
        Returns:
            True（始终返回 True，不过滤日志）
        """
        # 脱敏日志消息
        if hasattr(record, 'msg') and isinstance(record.msg, str):
            record.msg = self._mask_sensitive_data(record.msg)
        
        # 脱敏日志参数
        if hasattr(record, 'args') and record.args:
            if isinstance(record.args, dict):
                record.args = {
                    k: self._mask_sensitive_data(str(v)) if isinstance(v, str) else v
                    for k, v in record.args.items()
                }
            elif isinstance(record.args, (list, tuple)):
                record.args = tuple(
                    self._mask_sensitive_data(str(arg)) if isinstance(arg, str) else arg
                    for arg in record.args
                )
        
        return True
    
    def _mask_sensitive_data(self, text):
        # type: (str) -> str
        """
        脱敏敏感数据
        
        Args:
            text: 原始文本
            
        Returns:
            脱敏后的文本
        """
        for pattern, replacer in self.PATTERNS:
            text = pattern.sub(replacer, text)
        
        return text


def setup_logging_with_filter(logger=None):
    # type: (logging.Logger) -> None
    """
    为日志器添加脱敏过滤器
    
    Args:
        logger: 日志器（默认为根日志器）
    """
    if logger is None:
        logger = logging.getLogger()
    
    # 创建脱敏过滤器
    sensitive_filter = SensitiveDataFilter()
    
    # 添加到所有处理器
    for handler in logger.handlers:
        handler.addFilter(sensitive_filter)
    
    # 如果没有处理器，添加到日志器本身
    if not logger.handlers:
        logger.addFilter(sensitive_filter)
