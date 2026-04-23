# -*- coding: utf-8 -*-
"""
签名器 - HMAC-SHA256 请求签名

提供请求签名生成功能，用于 API 请求认证和防篡改。
"""

import hmac
import hashlib
import json
import time
import uuid
from typing import Optional, Dict, Any

from ..config import Config


class Signer:
    """签名器 - 生成 HMAC-SHA256 签名"""
    
    def __init__(self, api_key: str):
        """
        初始化签名器
        
        Args:
            api_key: API Key，用于生成签名
            
        Raises:
            ValueError: 如果 api_key 为空
        """
        if not api_key:
            raise ValueError("API Key 不能为空")
        
        self.api_key = api_key
    
    def build_headers(
        self,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        构造认证请求头
        
        生成包含认证信息和签名的 HTTP 请求头，用于 API 请求。
        
        Args:
            params: 查询参数（GET 请求）
            body: 请求体（POST 请求）
        
        Returns:
            请求头字典，包含以下字段：
            - Authorization: Bearer Token
            - Content-Type: application/json
            - X-Timestamp: 时间戳（毫秒）
            - X-Nonce: 随机值（UUID）
            - X-Signature: HMAC-SHA256 签名
        """
        # 生成防重放参数
        timestamp = int(time.time() * Config.HMAC_TIMESTAMP_MULTIPLIER)  # 毫秒级时间戳
        nonce = uuid.uuid4().hex  # {HMAC_NONCE_LENGTH}位随机字符串
        
        # 计算签名
        signature = self._calculate_signature(params, body, timestamp, nonce)
        
        # 构造请求头
        headers = {
            "Authorization": f"{Config.HMAC_AUTH_BEARER_PREFIX}{self.api_key}",
            "Content-Type": "application/json",
            "X-Timestamp": str(timestamp),
            "X-Nonce": nonce,
            "X-Signature": signature
        }
        
        return headers
    
    def _calculate_signature(
        self,
        params: Optional[Dict[str, Any]],
        body: Optional[Dict[str, Any]],
        timestamp: int,
        nonce: str
    ) -> str:
        """
        计算 HMAC-SHA256 签名
        
        签名范围：参数（字典序）+ Body Hash + 时间戳 + Nonce
        
        签名字符串格式：
        - 如果有 params: key1=value1&key2=value2&body_hash=xxx&timestamp=xxx&nonce=xxx
        - 如果没有 params: body_hash=xxx&timestamp=xxx&nonce=xxx
        
        Args:
            params: 查询参数
            body: 请求体
            timestamp: 时间戳（毫秒）
            nonce: 随机值
        
        Returns:
            HMAC-SHA256 签名（十六进制字符串）
        """
        # 1. 参数字典序排序并拼接
        param_str = "&".join(f"{k}={v}" for k, v in sorted(params.items())) if params else ""
        
        # 2. 计算 Body Hash
        body_hash = ""
        if body:
            # 将 body 序列化为 JSON（键按字典序排序，无空格）
            body_json = json.dumps(body, separators=Config.JSON_COMPACT_SEPARATORS, sort_keys=True, ensure_ascii=False)
            # 计算 SHA256 Hash
            body_hash = hashlib.sha256(body_json.encode('utf-8')).hexdigest()
        
        # 3. 构造签名字符串
        sign_parts = []
        if param_str:
            sign_parts.append(param_str)
        if body_hash:
            sign_parts.append(f"body_hash={body_hash}")
        sign_parts.append(f"timestamp={timestamp}")
        sign_parts.append(f"nonce={nonce}")
        
        sign_str = '&'.join(sign_parts)
        
        # 4. 生成 HMAC-SHA256 签名
        signature = hmac.new(
            self.api_key.encode('utf-8'),
            sign_str.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
