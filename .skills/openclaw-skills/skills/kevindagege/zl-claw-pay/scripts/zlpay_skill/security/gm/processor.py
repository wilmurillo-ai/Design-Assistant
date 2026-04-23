# -*- coding: utf-8 -*-
"""
报文加密加签处理模块

兼容 Java 版本的报文处理逻辑：
- 请求报文解析（解密、验签）
- 响应报文组装（加密、加签）
"""

import base64
import json
from typing import Any, Dict, Optional

from .crypto import SM2Util, SM4Util, CryptoError


# 配置常量（从上层 config 导入）
JSON_COMPACT_SEPARATORS = (',', ':')


class MessageProcessor:
    """
    报文处理器
    
    对应 Java 中的 sm2 类，提供：
    - parse_client_message: 解析请求报文（解密、验签）
    - build_client_message: 组装响应报文（加密、加签）
    """
    
    def __init__(self, client_private_key: str, server_public_key: str):
        """
        初始化报文处理器
        
        Args:
            client_private_key: 客户端私钥（16 进制字符串），用于签名请求
            server_public_key: 服务端公钥（16 进制字符串），用于加密请求密钥/验签响应
        """
        self.client_private_key = client_private_key
        self.server_public_key = server_public_key
    
    def parse_client_message(
        self,
        app_id: str,
        version: str,
        seq_id: str,
        timestamp: str,
        interface_id: str,
        encrypted_data: str,
        signature: str,
        encrypted_sm4_key: str,
        session_token: Optional[str] = None,
        trx_devc_inf: Optional[str] = None,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        解析客户端请求报文（对应 Java parseClientMessage）
        
        流程：
        1. SM2 解密获取 SM4 密钥
        2. 构造验签原文（verify_bo JSON + sm4_key）
        3. SM2 验签
        4. SM4 解密报文数据
        
        Args:
            app_id: 应用 ID
            version: 版本号
            seq_id: 流水号
            timestamp: 时间戳
            interface_id: 接口 ID
            encrypted_data: SM4 加密的报文数据（Base64）
            signature: 签名（Base64）
            encrypted_sm4_key: SM2 加密的 SM4 密钥（Base64）
            session_token: 会话令牌（可选）
            trx_devc_inf: 交易设备信息（可选）
            source: 来源（可选）
            
        Returns:
            解密后的业务数据字典
            
        Raises:
            CryptoError: 解密或验签失败
        """
        try:
            # 1. SM2 解密获取 SM4 密钥（使用客户端私钥解密服务端用客户端公钥加密的响应）
            sm4_key = SM2Util.de_code(
                private_key_hex=self.client_private_key,
                encrypted_data=encrypted_sm4_key
            )
            
            # 2. 构造验签原文
            verify_bo = self._build_verify_bo(
                app_id=app_id,
                version=version,
                seq_id=seq_id,
                timestamp=timestamp,
                interface_id=interface_id,
                encrypted_sm4_key=encrypted_sm4_key,
                encrypted_data=encrypted_data,
                session_token=session_token,
                trx_devc_inf=trx_devc_inf,
                source=source
            )
            
            # 根据是否有 source 字段选择字段列表
            if source:
                verify_fields = [
                    "appId", "version", "seqId", "timeStamp",
                    "interfaceId", "secret", "data",
                    "sessionToken", "trxDevcInf", "source"
                ]
            else:
                verify_fields = [
                    "appId", "version", "seqId", "timeStamp",
                    "interfaceId", "secret", "data",
                    "sessionToken", "trxDevcInf"
                ]
            
            # 过滤字段并序列化
            filtered_bo = {k: v for k, v in verify_bo.items() if k in verify_fields}
            json_data = json.dumps(
                filtered_bo,
                separators=(',', ':'),
                ensure_ascii=False,
                sort_keys=False
            )
            
            # 追加 sm4Key
            sign_data = json_data + sm4_key
            
            # 3. SM2 验签（使用服务端公钥验证服务端签名）
            is_valid = SM2Util.verify(
                public_key_hex=self.server_public_key,
                data=sign_data,
                signature=signature
            )
            
            if not is_valid:
                raise CryptoError("摘要验签失败")
            
            # 4. SM4 解密报文数据
            decrypted_data = SM4Util.decrypt_ecb(
                key_hex=sm4_key,
                encrypted_data=encrypted_data
            )
            
            # 解析为字典返回
            return json.loads(decrypted_data)
            
        except CryptoError:
            raise
        except Exception as e:
            raise CryptoError(f"解析请求报文失败: {e}")
    
    def build_client_message(
        self,
        app_id: str,
        version: str,
        seq_id: str,
        interface_id: str,
        response_data: Dict[str, Any],
        session_token: Optional[str] = None,
        trx_devc_inf: Optional[str] = None,
        source: Optional[str] = None
    ) -> Dict[str, str]:
        """
        组装客户端响应报文（对应 Java buildClientMessage）
        
        流程：
        1. 生成随机 SM4 密钥
        2. SM4 加密响应数据
        3. SM2 加密 SM4 密钥
        4. 构造签名原文并 SM2 签名
        
        Args:
            app_id: 应用 ID
            version: 版本号
            seq_id: 流水号
            interface_id: 接口 ID
            response_data: 响应业务数据字典
            session_token: 会话令牌（可选）
            trx_devc_inf: 交易设备信息（可选）
            source: 来源（可选）
            
        Returns:
            包含加密数据和签名的响应报文字典
            {
                "appId": ...,
                "version": ...,
                "seqId": ...,
                "timeStamp": ...,
                "interfaceId": ...,
                "secret": "SM2 加密的 SM4 密钥",
                "data": "SM4 加密的响应数据",
                "sign": "SM2 签名",
                "sessionToken": ...,
                "trxDevcInf": ...,
                "source": ...
            }
        """
        try:
            # 1. 生成随机 SM4 密钥
            sm4_key = SM4Util.generate_key()
            
            # 2. SM4 加密响应数据
            response_json = json.dumps(
                response_data,
                separators=JSON_COMPACT_SEPARATORS,
                ensure_ascii=False
            )
            encrypted_data = SM4Util.encrypt_ecb(
                key_hex=sm4_key,
                data=response_json
            )
            
            # 3. SM2 加密 SM4 密钥（使用服务端公钥加密）
            encrypted_sm4_key = SM2Util.en_code(
                public_key_hex=self.server_public_key,
                data=sm4_key
            )
            
            # 4. 构造签名原文
            verify_bo = self._build_verify_bo(
                app_id=app_id,
                version=version,
                seq_id=seq_id,
                timestamp=self._get_timestamp(),
                interface_id=interface_id,
                encrypted_sm4_key=encrypted_sm4_key,
                encrypted_data=encrypted_data,
                session_token=session_token,
                trx_devc_inf=trx_devc_inf,
                source=source
            )
            
            # 根据是否有 source 字段选择字段列表
            if source:
                verify_fields = [
                    "appId", "version", "seqId", "timeStamp",
                    "interfaceId", "secret", "data",
                    "sessionToken", "trxDevcInf", "source"
                ]
            else:
                verify_fields = [
                    "appId", "version", "seqId", "timeStamp",
                    "interfaceId", "secret", "data",
                    "sessionToken", "trxDevcInf"
                ]
            
            # 过滤字段并序列化（空字符串写为 ""）
            filtered_bo = {}
            for k in verify_fields:
                v = verify_bo.get(k)
                # 空值转为空字符串
                if v is None:
                    v = ""
                filtered_bo[k] = v
            
            json_data = json.dumps(
                filtered_bo,
                separators=(',', ':'),
                ensure_ascii=False,
                sort_keys=False
            )
            
            # 追加 sm4Key
            sign_data = json_data + sm4_key
            
            # 5. SM2 签名（使用客户端私钥签名请求）
            signature = SM2Util.sign(
                private_key_hex=self.client_private_key,
                data=sign_data
            )
            
            # 6. 组装响应报文
            result = {
                "appId": app_id,
                "version": version,
                "seqId": seq_id,
                "timeStamp": verify_bo["timeStamp"],
                "interfaceId": interface_id,
                "secret": encrypted_sm4_key,
                "data": encrypted_data,
                "sign": signature
            }
            
            # 添加可选字段
            if session_token is not None:
                result["sessionToken"] = session_token
            if trx_devc_inf is not None:
                result["trxDevcInf"] = trx_devc_inf
            if source is not None:
                result["source"] = source
            
            return result
            
        except Exception as e:
            raise CryptoError(f"组装响应报文失败: {e}")
    
    def _build_verify_bo(
        self,
        app_id: str,
        version: str,
        seq_id: str,
        timestamp: str,
        interface_id: str,
        encrypted_sm4_key: str,
        encrypted_data: str,
        session_token: Optional[str] = None,
        trx_devc_inf: Optional[str] = None,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """构造验签 BO 对象"""
        bo = {
            "appId": app_id,
            "version": version,
            "seqId": seq_id,
            "timeStamp": timestamp,
            "interfaceId": interface_id,
            "secret": encrypted_sm4_key,
            "data": encrypted_data
        }
        
        if session_token is not None:
            bo["sessionToken"] = session_token
        if trx_devc_inf is not None:
            bo["trxDevcInf"] = trx_devc_inf
        if source is not None:
            bo["source"] = source
            
        return bo
    
    def _get_timestamp(self) -> str:
        """获取当前时间戳字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y%m%d%H%M%S")


# 便捷函数

def parse_request_message(
    client_private_key: str,
    server_public_key: str,
    request_message: Dict[str, Any]
) -> Dict[str, Any]:
    """
    便捷函数：解析请求报文
    
    Args:
        client_private_key: 客户端私钥
        server_public_key: 服务端公钥
        request_message: 请求报文字典
        
    Returns:
        解密后的业务数据
    """
    processor = MessageProcessor(client_private_key, server_public_key)
    
    return processor.parse_client_message(
        app_id=request_message.get("appId", ""),
        version=request_message.get("version", ""),
        seq_id=request_message.get("seqId", ""),
        timestamp=request_message.get("timeStamp", ""),
        interface_id=request_message.get("interfaceId", ""),
        encrypted_data=request_message.get("data", ""),
        signature=request_message.get("sign", ""),
        encrypted_sm4_key=request_message.get("secret", ""),
        session_token=request_message.get("sessionToken"),
        trx_devc_inf=request_message.get("trxDevcInf"),
        source=request_message.get("source")
    )


def build_response_message(
    client_private_key: str,
    server_public_key: str,
    request_message: Dict[str, Any],
    response_data: Dict[str, Any]
) -> Dict[str, str]:
    """
    便捷函数：组装响应报文
    
    Args:
        client_private_key: 客户端私钥
        server_public_key: 服务端公钥
        request_message: 原始请求报文（用于复制部分字段）
        response_data: 响应业务数据
        
    Returns:
        加密加签后的响应报文
    """
    processor = MessageProcessor(client_private_key, server_public_key)
    
    return processor.build_client_message(
        app_id=request_message.get("appId", ""),
        version=request_message.get("version", ""),
        seq_id=request_message.get("seqId", ""),
        interface_id=request_message.get("interfaceId", ""),
        response_data=response_data,
        session_token=request_message.get("sessionToken"),
        trx_devc_inf=request_message.get("trxDevcInf"),
        source=request_message.get("source")
    )
