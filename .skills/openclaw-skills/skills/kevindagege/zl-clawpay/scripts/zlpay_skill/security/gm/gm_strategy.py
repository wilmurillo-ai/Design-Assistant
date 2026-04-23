# -*- coding: utf-8 -*-
"""
国密 SM2/SM4 加密加签策略

客户端加密流程：
- 使用服务端公钥加密 SM4 会话密钥
- 使用 SM4 加密请求体数据
- 使用客户端私钥签名请求

客户端解密流程：
- 使用客户端私钥解密 SM4 会话密钥
- 使用 SM4 解密响应数据
- 使用服务端公钥验证响应签名

需要配置：
- client_private_key: 客户端私钥（用于签名请求/解密响应）
- server_public_key: 服务端公钥（用于加密请求/验签响应）
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json
import time

from ..security_strategy import SecurityStrategy
from ...config import Config


class GmSecurityStrategy(SecurityStrategy):
    """
    国密 SM2/SM4 加密加签策略
    
    客户端加密流程：
    - 使用服务端公钥加密 SM4 会话密钥
    - 使用 SM4 加密请求体数据
    - 使用客户端私钥签名请求
    
    客户端解密流程：
    - 使用客户端私钥解密 SM4 会话密钥
    - 使用 SM4 解密响应数据
    - 使用服务端公钥验证响应签名
    
    需要配置：
    - client_private_key: 客户端私钥（用于签名请求/解密响应）
    - server_public_key: 服务端公钥（用于加密请求/验签响应）
    """
    
    def __init__(
        self,
        client_private_key: str,
        server_public_key: str,
        version: str = Config.VERSION
    ):
        """
        初始化策略
        
        Args:
            client_private_key: 客户端 SM2 私钥（16 进制），用于签名
            server_public_key: 服务端 SM2 公钥（16 进制），用于加密 SM4 密钥
            version: 版本号
        """
        self.client_private_key = client_private_key
        self.server_public_key = server_public_key
        self.version = version
        self.app_id = Config.get_app_id()
    
    def _generate_seq_id(self) -> str:
        """
        生成唯一流水号
        
        使用纳秒级时间戳确保全局唯一性，避免重启后重复
        """
        return str(int(time.time() * 1e9))  # Python 3.6兼容
    
    def _build_common_fields(
        self,
        seq_id: str,
        interface_id: str
    ) -> Dict[str, Any]:
        """
        构建报文公共字段（报文头）
        
        组装后端系统公共数据域的基础字段：
        - appId: 商户号
        - version: 版本号
        - seqId: 请求流水号
        - timeStamp: 时间戳
        - interfaceId: 接口编码
        
        Args:
            seq_id: 请求流水号
            interface_id: 接口编码
            
        Returns:
            公共字段字典
        """
        time_stamp = datetime.now().strftime(Config.GM_TIMESTAMP_FORMAT)
        
        return {
            "appId": self.app_id,
            "version": self.version,
            "seqId": seq_id,
            "timeStamp": time_stamp,
            "interfaceId": interface_id,
        }
    
    def _build_optional_fields(
        self,
        extra_fields: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        构建可选扩展字段
        
        从 extra_fields 中提取可选字段：
        - sessionToken: APP会话token
        - trxDevcInf: 交易设备信息
        - source: 前端请求来源系统
        
        这些字段参与加签，但不属于核心报文头
        
        Args:
            extra_fields: 可选字段字典
            
        Returns:
            过滤后的可选字段字典
        """
        result = {}
        if extra_fields:
            for key in ['sessionToken', 'trxDevcInf', 'source']:
                if key in extra_fields and extra_fields[key]:
                    result[key] = extra_fields[key]
        return result
    
    def build_request_headers(
        self,
        endpoint: str,
        interface_id: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        """
        构造国密请求头
        
        返回标准 HTTP 头，实际加密逻辑在 build_request_body 中处理
        interfaceId 作为请求头传递
        """
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "X-Encryption-Type": "SM2/SM4",
            "X-Interface-Id": interface_id
        }
        
        return headers
    
    def build_request_body(
        self,
        body: Optional[Dict[str, Any]] = None,
        endpoint: Optional[str] = None,
        seq_id: Optional[str] = None,
        interface_id: Optional[str] = None,
        extra_fields: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        构建请求体
        
        根据 GM_ENABLE_ENCRYPTION 配置决定是否加密：
        - 启用加密（默认）：使用 SM2/SM4 加密，包含 secret 和 sign
        - 关闭加密：data 使用明文，不包含 secret 和 sign
        
        Args:
            body: 原始请求体
            endpoint: API 端点
            seq_id: 请求流水号
            interface_id: 接口编码
            extra_fields: 可选字段字典（sessionToken, trxDevcInf, source）
            
        Returns:
            报文结构（加密或明文，符合后端系统公共数据域标准）
        """
        if body is None:
            body = {}
        
        # 使用传入的 seq_id 或自动生成
        if seq_id is None:
            seq_id = self._generate_seq_id()
        
        # 检查 interface_id，优先从 body 中获取驼峰命名的 interfaceId
        if interface_id is None:
            interface_id = body.get("interfaceId") if body else None
        
        if not interface_id:
            raise ValueError("interfaceId 参数不能为空")
        
        # 构建报文三层结构
        # 第1层：报文头（公共字段）
        header_fields = self._build_common_fields(seq_id, interface_id)
        
        # 第2层：可选扩展字段（参与加签但不属于核心报文头）
        optional_fields = self._build_optional_fields(extra_fields)
        
        # 合并基础字段
        base_fields = {**header_fields, **optional_fields}
        
        if Config.is_encryption_enabled():
            # 启用加密：使用 SM2/SM4 加密
            from . import SM2Util, SM4Util
            
            sm4_key = SM4Util.generate_key()
            encrypted_data = SM4Util.encrypt_ecb(sm4_key, json.dumps(body, separators=(',', ':'), ensure_ascii=False))
            encrypted_sm4_key = SM2Util.en_code(self.server_public_key, sm4_key)
            
            request_data = {
                **base_fields,
                "secret": encrypted_sm4_key,
                "data": encrypted_data
            }
            
            # 生成 SM2 签名
            # 构造与服务端一致的摘要明文：JSON序列化 + 追加sm4key
            sign_dict = {
                "appId": request_data["appId"],
                "version": request_data["version"],
                "seqId": request_data["seqId"],
                "timeStamp": request_data["timeStamp"],
                "interfaceId": request_data["interfaceId"],
                "secret": request_data["secret"],
                "data": request_data["data"]
            }
            # 添加可选字段（如果存在）
            for key in ['sessionToken', 'trxDevcInf', 'source']:
                if key in request_data:
                    sign_dict[key] = request_data[key]
            
            # JSON序列化后追加sm4key（与服务端VerifyBO逻辑一致）
            sign_content = json.dumps(sign_dict, separators=(',', ':'), ensure_ascii=False)
            sign_content = sign_content + sm4_key
            
            request_data["sign"] = SM2Util.sign(self.client_private_key, sign_content)
        else:
            # 关闭加密：body序列化为JSON字符串放入data字段（明文，不加密）
            request_data = {
                **base_fields,
                "data": json.dumps(body, separators=(',', ':'), ensure_ascii=False) if body else "{}"
            }
        
        return request_data
    
    def process_response(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理响应数据
        
        根据 GM_ENABLE_ENCRYPTION 配置决定处理方式：
        - 启用加密（默认）：验签并解密响应
        - 关闭加密：从data字段解析明文JSON
        
        Args:
            response_data: 响应数据（可能是加密或明文）
            
        Returns:
            处理后的业务数据
        """
        # 关闭加密模式：从data字段解析明文JSON，再解析resData
        if not Config.is_encryption_enabled():
            data_str = response_data.get('data', '')
            if data_str:
                try:
                    inner_data = json.loads(data_str)
                    # 解析resData中的嵌套JSON
                    res_data = inner_data.get('resData')
                    if res_data and isinstance(res_data, str):
                        try:
                            inner_data['resData'] = json.loads(res_data)
                        except (ValueError, json.JSONDecodeError):
                            pass
                    return inner_data
                except (ValueError, json.JSONDecodeError):
                    return {"data": data_str}
            return response_data
        
        # 启用加密模式：验签并解密
        from . import SM2Util
        
        # 检查是否包含加密数据字段
        if not response_data.get('secret') or not response_data.get('data'):
            # 没有加密字段，直接返回
            return response_data
        
        # 验证响应签名（如果存在）
        sign = response_data.get('sign')
        if sign:
            # 构建验签内容（与服务端SimplePropertyPreFilter格式一致）
            # 字段顺序：appId, version, seqId, timeStamp, interfaceId, secret, data, sessionToken, trxDevcInf, source
            # 注意：服务端使用驼峰 timeStamp
            verify_dict = {
                "appId": response_data.get("appId", ""),
                "version": response_data.get("version", ""),
                "seqId": response_data.get("seqId", ""),
                "timeStamp": response_data.get("timeStamp") or response_data.get("timeStamp", ""),
                "interfaceId": response_data.get("interfaceId", ""),
                "secret": response_data.get("secret", ""),
                "data": response_data.get("data", ""),
            }
            
            # 添加可选字段
            for key in ['sessionToken', 'trxDevcInf', 'source']:
                if key in response_data:
                    verify_dict[key] = response_data[key]
            
            # 序列化为JSON（不加空格，保持紧凑）
            verify_content = json.dumps(verify_dict, separators=(',', ':'), ensure_ascii=False)
            
            # 使用服务端公钥验签
            try:
                is_valid = SM2Util.verify(self.server_public_key, verify_content, sign)
                if not is_valid:
                    raise ValueError(u"响应签名验证失败")
            except Exception as e:
                raise ValueError(u"响应签名验证失败: {}".format(str(e)))
        
        from . import MessageProcessor
        
        processor = MessageProcessor(
            client_private_key=self.client_private_key,
            server_public_key=self.server_public_key
        )
        
        # 调用解析方法解密响应
        return processor.parse_client_message(
            app_id=response_data.get("appId", ""),
            version=response_data.get("version", ""),
            seq_id=response_data.get("seqId", ""),
            timestamp=response_data.get("timeStamp", ""),
            interface_id=response_data.get("interfaceId", ""),
            encrypted_data=response_data.get("data", ""),
            signature=sign or "",
            encrypted_sm4_key=response_data.get("secret", "")
        )
