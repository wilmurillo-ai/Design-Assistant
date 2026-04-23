# -*- coding: utf-8 -*-
"""
HMAC-SHA256 签名策略

使用方式（与现有 Signer 相同）：
- 请求头包含 Authorization, X-Timestamp, X-Nonce, X-Signature
- 请求体不加密
- 响应不加密
"""

from typing import Dict, Any, Optional

from ..security_strategy import SecurityStrategy


class HmacSha256Strategy(SecurityStrategy):
    """
    HMAC-SHA256 签名策略
    
    使用方式（与现有 Signer 相同）：
    - 请求头包含 Authorization, X-Timestamp, X-Nonce, X-Signature
    - 请求体不加密
    - 响应不加密
    """
    
    def __init__(self, api_key: str):
        """
        初始化策略
        
        Args:
            api_key: API Key，用于签名
        """
        self.api_key = api_key
    
    def build_request_headers(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """构造 HMAC-SHA256 请求头"""
        from ..hmac.signer import Signer
        
        signer = Signer(self.api_key)
        return signer.build_headers(params=params, body=body)
    
    def build_request_body(
        self,
        body: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """HMAC 策略不加密请求体，直接返回"""
        return body
    
    def process_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """HMAC 策略不处理响应，直接返回"""
        return response_data
