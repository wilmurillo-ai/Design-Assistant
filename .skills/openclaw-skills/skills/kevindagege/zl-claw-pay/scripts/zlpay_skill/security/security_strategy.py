# -*- coding: utf-8 -*-
"""
安全策略基类模块

提供安全策略基类，具体策略实现见：
- hmac_strategy.py: HmacSha256Strategy - HMAC-SHA256 签名
- gm_strategy.py: GmSecurityStrategy - 国密 SM2/SM4 加密加签
"""

from typing import Dict, Any, Optional


class SecurityStrategy:
    """
    安全策略基类
    
    定义统一的加密加签接口，具体策略实现此接口
    """
    
    def build_request_headers(
        self,
        endpoint: str,
        interface_id: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        构造请求头（包含认证信息）
        
        Args:
            endpoint: API 端点
            interface_id: 接口编码
            params: 查询参数
            body: 请求体
            
        Returns:
            请求头字典
        """
        raise NotImplementedError
    
    def build_request_body(
        self,
        body: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
        seq_id: Optional[str] = None,
        interface_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        处理请求体（加密等）
        
        Args:
            body: 原始请求体
            endpoint: API 端点
            seq_id: 请求流水号
            interface_id: 接口编码
            
        Returns:
            处理后的请求体
        """
        raise NotImplementedError
    
    def process_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理响应数据（解密、验签等）
        
        Args:
            response_data: 原始响应数据
            
        Returns:
            处理后的业务数据
        """
        raise NotImplementedError

