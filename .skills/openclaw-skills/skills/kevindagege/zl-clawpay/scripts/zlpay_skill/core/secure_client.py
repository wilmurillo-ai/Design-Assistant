# -*- coding: utf-8 -*-
"""
安全请求客户端 - 统一加签请求方法

提供统一的 API 请求接口，封装加签、请求、验签逻辑。
支持两种安全策略（代码硬编码切换）：
- HmacSha256Strategy: HMAC-SHA256 签名
- GmSecurityStrategy: 国密 SM2/SM4 加密加签

切换方式：修改下面 SECURITY_STRATEGY 常量的值
"""

import requests
import json
import logging
from typing import Optional, Dict, Any

from ..config import Config
from ..log_manager import get_logger
from ..exceptions import APIError, SecurityError

logger = get_logger(__name__)

# 使用 Config 中的安全策略配置
SECURITY_STRATEGY = Config.SECURITY_STRATEGY


def _mask_sensitive_data(data: Any) -> Any:
    """
    脱敏敏感数据
    
    对敏感字段（api_key, secret, private_key, sub_wallet_id 等）进行脱敏处理，
    显示前8位 + **** + 后4位，其他内容保持不变。
    
    Args:
        data: 需要脱敏的数据（字符串、字典、列表或其他类型）
        
    Returns:
        脱敏后的数据
    """
    sensitive_keys = {'api_key', 'secret', 'private_key', 'sub_wallet_id', 'wallet_id', 
                      'gm_client_private_key', 'gm_server_public_key', 'authorization'}
    
    if isinstance(data, str):
        # 如果字符串较短，直接返回前8位+****
        if len(data) <= 12:
            return data[:8] + '****' if len(data) > 8 else '****'
        return data[:8] + '****' + data[-4:]
    elif isinstance(data, dict):
        masked = {}
        for key, value in data.items():
            if key.lower() in sensitive_keys or any(s in key.lower() for s in sensitive_keys):
                masked[key] = _mask_sensitive_data(value) if isinstance(value, str) else value
            elif isinstance(value, (dict, list)):
                masked[key] = _mask_sensitive_data(value)
            else:
                masked[key] = value
        return masked
    elif isinstance(data, list):
        return [_mask_sensitive_data(item) for item in data]
    else:
        return data


class SecureClient:
    """安全请求客户端 - 封装加签、请求、验签逻辑
    
    设计说明：
    - 配置在初始化时固定，避免每次请求重复读取
    - 支持外部传入配置（便于测试），不传则从 Config 读取
    - 安全策略通过 SECURITY_STRATEGY 常量硬编码切换
    """
    
    def __init__(self, api_key: str = None, base_url: str = None, lazy_init: bool = False):
        """
        初始化安全请求客户端
        
        Args:
            api_key: API Key，不传则从 Config 读取（绑定前场景可传 None）
            base_url: API 基础 URL，不传则从 Config 读取
            lazy_init: 是否延迟初始化策略（用于绑定前场景，后续通过 with_api_key 设置）
            
        Raises:
            ValueError: 如果 base_url 未设置
        """
        # 加载配置（外部传入优先，否则从 Config 读取）
        if api_key:
            self.api_key = api_key
        else:
            self.api_key = Config.get_api_key(memory=None)
        self.base_url = base_url or Config.get_api_url()
        
        if not self.base_url:
            raise ValueError("API URL 不能为空，请通过参数传入或配置 Config")
        
        # 根据延迟初始化参数决定是否立即初始化策略
        if not lazy_init and self.api_key:
            # 立即初始化策略（正常场景）
            self.strategy = self._init_strategy()
        else:
            # 延迟初始化（绑定前场景）
            self.strategy = None
        
        # 初始化 HTTP 会话
        self.session = requests.Session()
        
        # 配置重试机制（指数退避）
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry
        import urllib3
        
        # 检测 urllib3 版本，兼容新旧版本参数名
        # urllib3 2.x 使用 allowed_methods，1.x 使用 method_whitelist
        retry_kwargs = {
            "total": 3,  # 最多重试3次
            "backoff_factor": 1,  # 指数退避基数：1s, 2s, 4s
            "status_forcelist": [500, 502, 503, 504],  # 这些HTTP状态码触发重试
        }
        
        # 根据 urllib3 版本选择正确的参数名
        if urllib3.__version__.startswith("1."):
            retry_kwargs["method_whitelist"] = ["HEAD", "GET", "OPTIONS", "POST"]
        else:
            retry_kwargs["allowed_methods"] = ["HEAD", "GET", "OPTIONS", "POST"]
        
        retry_strategy = Retry(**retry_kwargs)
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
    
    def with_api_key(self, api_key: str):
        """
        动态设置 API Key（用于绑定前场景）
        
        Args:
            api_key: API Key
            
        Returns:
            self（支持链式调用）
        """
        self.api_key = api_key
        if self.strategy is None:
            self.strategy = self._init_strategy()
        return self
    
    def with_base_url(self, base_url: str):
        """
        动态设置基础 URL
        
        Args:
            base_url: API 基础 URL
            
        Returns:
            self（支持链式调用）
        """
        self.base_url = base_url.rstrip('/')
        return self
    
    def _init_strategy(self):
        """
        初始化安全策略（硬编码切换）
        
        Returns:
            SecurityStrategy 实例
        """
        if SECURITY_STRATEGY == "hmac":
            # HMAC-SHA256 策略
            from ..security.hmac.hmac_strategy import HmacSha256Strategy
            return HmacSha256Strategy(api_key=self.api_key)
            
        elif SECURITY_STRATEGY == "gm":
            # 国密 SM2/SM4 策略（不依赖 api_key）
            from ..security.gm.gm_strategy import GmSecurityStrategy
            
            # 使用 Config 类读取 GM 密钥（支持环境变量或文件路径）
            client_private_key = Config.get_gm_client_private_key()
            server_public_key = Config.get_gm_server_public_key()
            
            return GmSecurityStrategy(
                client_private_key=client_private_key,
                server_public_key=server_public_key
            )
        else:
            raise ValueError(f"未知的安全策略: {SECURITY_STRATEGY}")
    
    def build_request(
        self,
        method: str,
        endpoint: str,
        interface_id: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        extra_fields: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        组装请求报文（不发送请求）
        
        执行报文组装流程：
        1. 构造完整 URL
        2. 生成流水号
        3. 使用策略构建请求头
        4. 使用策略处理请求体（加密/加签）
        
        Args:
            method: HTTP 方法（GET/POST）
            endpoint: API 端点路径
            interface_id: 接口编码
            params: 查询参数
            body: 请求体
            extra_fields: 可选字段（sessionToken, trxDevcInf, source）
            
        Returns:
            请求信息字典：
            {
                'url': str,           # 完整 URL
                'headers': dict,      # 请求头
                'body': dict,         # 处理后请求体（加密/加签后）
                'seq_id': str,        # 流水号
                'raw_body': dict,     # 原始请求体
                'method': str         # HTTP 方法
            }
        """
        if self.strategy is None:
            raise ValueError("安全策略未初始化，请先调用 with_api_key() 或在构造函数中提供 api_key")
        
        # 1. 构造完整 URL
        base_url = self.base_url.rstrip('/')
        endpoint_clean = endpoint.lstrip('/')
        url = f"{base_url}/{endpoint_clean}"
        
        # 2. 生成流水号
        from ..security.seq_id_generator import SeqIdGenerator
        seq_id = SeqIdGenerator.generate()
        logger.debug(f"[SecureClient] 生成请求流水号: {seq_id}, endpoint: {endpoint}")
        
        # 3. 构建请求头
        headers = self.strategy.build_request_headers(
            endpoint=endpoint_clean,
            interface_id=interface_id,
            params=params,
            body=body
        )
        
        # 4. 处理请求体（加密/加签）
        processed_body = self.strategy.build_request_body(
            body=body,
            endpoint=endpoint_clean,
            seq_id=seq_id,
            interface_id=interface_id,
            extra_fields=extra_fields
        )
        
        # 5. 打印请求日志
        if logger.isEnabledFor(logging.DEBUG):
            safe_body = _mask_sensitive_data(processed_body.copy() if processed_body else {})
            logger.debug(f"[SecureClient] 组装请求: {method.upper()} {url}")
            logger.debug(f"[SecureClient] 请求头: {json.dumps(dict(headers), ensure_ascii=False)}")
            logger.debug(f"[SecureClient] 请求体: {json.dumps(safe_body, ensure_ascii=False, indent=2)}")
        
        return {
            'url': url,
            'headers': headers,
            'body': processed_body,
            'seq_id': seq_id,
            'raw_body': body,
            'method': method.upper(),
            'endpoint': endpoint
        }
    
    def send(
        self,
        url: str,
        method: str,
        headers: Dict[str, Any],
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        timeout: int = None
    ) -> requests.Response:
        """
        发送 HTTP 请求
        
        Args:
            url: 完整 URL
            method: HTTP 方法
            headers: 请求头
            body: 请求体
            params: 查询参数
            timeout: 超时时间（秒）
            
        Returns:
            requests.Response 对象
            
        Raises:
            requests.Timeout: 请求超时
            requests.RequestException: 其他网络错误
        """
        timeout = timeout or Config.REQUEST_TIMEOUT
        
        try:
            # 手动序列化 JSON 并设置 ensure_ascii=False，避免中文字符被转义
            json_body = json.dumps(body, ensure_ascii=False) if body else None
            
            # 调试：打印实际发送的 JSON
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"[SecureClient] 实际发送的 JSON: {json_body[:1000] if json_body else 'None'}")
            
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                data=json_body.encode('utf-8') if json_body else None,
                headers=headers,
                timeout=timeout
            )
        except requests.Timeout:
            raise requests.Timeout(f"请求超时（{timeout}秒）")
        except requests.RequestException as e:
            raise requests.RequestException(f"网络请求失败: {e}")
        
        return response
    
    def parse_response(
        self,
        response_data: Dict[str, Any],
        seq_id: str = None
    ) -> Dict[str, Any]:
        """
        处理响应数据（解密/验签）
        
        Args:
            response_data: 原始响应数据
            seq_id: 流水号（用于追踪）
            
        Returns:
            解析后的业务数据，包含 seq_id
        """
        if self.strategy is None:
            raise ValueError("安全策略未初始化")
        
        # 使用策略处理响应数据
        result_data = self.strategy.process_response(response_data)
        
        # 添加 seq_id 用于追踪
        if seq_id and isinstance(result_data, dict):
            result_data['seq_id'] = seq_id
            
        return result_data
    
    def secure_request(
        self,
        method: str,
        endpoint: str,
        interface_id: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
        extra_fields: Optional[Dict[str, Any]] = None,
        timeout: int = Config.REQUEST_TIMEOUT
    ) -> Dict[str, Any]:
        """
        统一加签请求方法
        
        执行完整的 API 请求流程：
        1. 构造完整 URL
        2. 使用策略构建请求头和处理请求体
        3. 发送 HTTP 请求
        4. 检查 HTTP 状态码
        5. 使用策略处理响应数据
        6. 返回纯净的业务数据
        
        Args:
            method: HTTP 方法（GET/POST）
            endpoint: API 端点路径（如 /skill/wallet/balance）
            interface_id: 接口编码（如 C00003、A00063）
            params: 查询参数（GET 请求）
            body: 请求体（POST 请求）
            extra_fields: 可选字段字典（sessionToken, trxDevcInf, source）
            timeout: 超时时间（秒），默认 30 秒
        
        Returns:
            响应数据字典（纯净的业务数据，不包含签名和认证信息）
        
        Raises:
            APIError: API 错误（非 200 状态码）
            SecurityError: 签名验证失败
            requests.Timeout: 请求超时
            requests.RequestException: 其他网络错误
        """
        # 1. 组装请求
        req = self.build_request(
            method=method,
            endpoint=endpoint,
            interface_id=interface_id,
            params=params,
            body=body,
            extra_fields=extra_fields
        )
        
        # 2. 发送 HTTP 请求
        response = self.send(
            url=req['url'],
            method=req['method'],
            headers=req['headers'],
            body=req['body'],
            params=params,
            timeout=timeout
        )
        
        # 4. 打印完整响应日志（debug级别）
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"[SecureClient] 响应状态: HTTP {response.status_code}")
            try:
                resp_text = response.text
                # 尝试解析为JSON并脱敏
                resp_json = json.loads(resp_text)
                safe_resp = _mask_sensitive_data(resp_json)
                logger.debug(f"[SecureClient] 响应体: {json.dumps(safe_resp, ensure_ascii=False, indent=2)}")
            except (ValueError, json.JSONDecodeError):
                # 非JSON响应，直接打印前500字符
                logger.debug(f"[SecureClient] 响应体（原始）: {resp_text[:500]}")
        
        # 5. 检查 HTTP 状态码
        if response.status_code != Config.HTTP_OK:
            try:
                error_data = response.json()
                message = error_data.get("message", "请求失败")
            except:
                message = response.text or "请求失败"
            
            raise APIError(
                status_code=response.status_code,
                message=message
            )
        
        # 6. 解析响应数据
        try:
            response_data = response.json()
        except ValueError:
            raise APIError(
                status_code=response.status_code,
                message="响应数据格式错误（非 JSON）"
            )
        
        # 7. 处理响应数据（解密/验签）并返回
        return self.parse_response(response_data, req['seq_id'])
    
    def close(self):
        """关闭 HTTP 会话，释放资源"""
        if self.session:
            self.session.close()
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
