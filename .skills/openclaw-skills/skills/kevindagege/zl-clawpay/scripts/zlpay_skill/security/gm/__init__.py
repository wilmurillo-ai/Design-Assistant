# -*- coding: utf-8 -*-
"""
国密加密包 (GM - Guo Mi)

提供 SM2/SM4 国密算法实现：
- crypto: SM2/SM4 基础加密工具
- processor: 报文处理器（加密、解密、签名、验签）
"""

from .crypto import SM2Util, SM4Util, CryptoError
from .processor import MessageProcessor, parse_request_message, build_response_message

__all__ = [
    'SM2Util',
    'SM4Util',
    'CryptoError',
    'MessageProcessor',
    'parse_request_message',
    'build_response_message'
]
