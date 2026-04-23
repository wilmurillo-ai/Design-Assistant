# -*- coding: utf-8 -*-
"""
钱包服务模块
"""

import json
from typing import Dict, Any, Optional

from ..config import Config
from ..core.secure_client import SecureClient
from ..log_manager import get_logger

logger = get_logger(__name__)


class WalletService:
    """钱包服务 - 处理钱包相关业务逻辑"""
    
    def __init__(self, skill, memory):
        """
        初始化钱包服务
        
        Args:
            skill: ZLPaySkill 实例，用于调用 api_call
            memory: 记忆管理器
        """
        self.skill = skill
        self.memory = memory
    
    def bind_sub_wallet(self, session_id=None, interface_id=None, params=None, body=None):
        # type: (Optional[str], Optional[str], Optional[Dict], Optional[Dict]) -> Dict[str, Any]
        """
        绑定子钱包（开户）
        
        使用 SecureClient 发送国密加密请求。
        在绑定之前 skill 尚未配置 sub_wallet_id 和 api_key，
        因此需要传入 api_key 并通过 lazy_init 模式创建 SecureClient。
        
        Args:
            session_id: 会话ID
            interface_id: 接口编码（如 C00003）
            params: URL参数
            body: 请求体，包含 apiKey, subWalletName 等业务参数
            
        Returns:
            绑定结果（包含 subWalletId 等）
            
        Raises:
            ValueError: 如果参数为空
            requests.RequestException: 如果 HTTP 请求失败
        """
        if body is None:
            body = {}
        
        # 从 body 提取参数（支持驼峰和下划线两种命名）
        api_key = body.get('apiKey') or body.get('api_key')
        sub_wallet_name = body.get('subWalletName') or body.get('sub_wallet_name')

        # 删除 subWalletName 中的空格
        if sub_wallet_name:
            sub_wallet_name = sub_wallet_name.replace(" ", "")

        # 参数校验
        if not api_key:
            raise ValueError(u"api_key 不能为空")

        # 构造业务数据
        body = {
            "apiKey": api_key,
            "subWalletName": sub_wallet_name
        }

        # 打印请求日志（脱敏）
        logger.info(f"[WalletService] 绑定子钱包请求")
        safe_body = body.copy()
        for key in ['apiKey', 'api_key', 'password', 'token']:
            if key in safe_body:
                safe_body[key] = '***'
        logger.info(f"[WalletService] 请求体: {json.dumps(safe_body, ensure_ascii=False)}")
        
        # 创建 SecureClient（延迟初始化，绑定前场景）
        client = SecureClient(lazy_init=True)
        
        # 动态设置 API Key 并发送国密加密请求
        result = client.with_api_key(api_key).secure_request(
            method="POST",
            endpoint="/post/claw/bind-sub-wallet",
            interface_id=interface_id,
            body=body
        )
        
        # 从响应中获取 sub_wallet_id 并持久化
        res_data = result.get("resData") or {}
        
        # 如果响应表示失败，直接返回结果（F开头:业务错误，P开头:平台错误，E开头:系统错误）
        res_code = result.get("resCode", "")
        if res_code and not res_code.startswith(Config.SUCCESS_CODE_PREFIX):
            return result
        
        if not res_data:
            raise ValueError(u"绑定失败,解析响应数据失败")

        # 打印响应日志
        logger.info(f"[WalletService] 绑定成功，响应: {json.dumps(res_data, ensure_ascii=False)[:500]}")

        response_sub_wallet_id = res_data.get("subWalletId")
        if response_sub_wallet_id:
            logger.info(f"[WalletService] 子钱包ID: {response_sub_wallet_id}")
            self.memory.remember_wallet(response_sub_wallet_id)
        self.memory.remember_api_key(api_key)
        
        return result
    
    def unbind_sub_wallet(self, session_id=None, interface_id=None, params=None, body=None):
        # type: (Optional[str], Optional[str], Optional[Dict], Optional[Dict]) -> Dict[str, Any]
        """
        解绑子钱包
        
        Args:
            session_id: 会话ID
            interface_id: 接口编码（如 L00002）
            params: URL参数
            body: 请求体
            
        Returns:
            解绑结果
        """
        if body is None:
            body = {}
        
        # 获取当前绑定的钱包ID
        sub_wallet_id = self.memory.get_wallet()
        
        if not sub_wallet_id:
            return {
                "resCode": "F010001",
                "resMsg": u"未绑定子钱包，无需解绑",
                "unbindStatus": "解绑失败"
            }
        
        # 清除本地绑定
        self.memory.forget_wallet()
        self.memory.forget_api_key()
        
        logger.info(f"[WalletService] 解绑子钱包: {sub_wallet_id}")
        
        return {
            "resCode": "S010000",
            "resMsg": u"解绑成功",
            "subWalletId": sub_wallet_id,
            "unbindStatus": "已解绑"
        }
    
    def query_wallet(self, session_id=None, interface_id=None, params=None, body=None):
        # type: (Optional[str], Optional[str], Optional[Dict], Optional[Dict]) -> Dict[str, Any]
        """
        查询子钱包信息（本地接口 L00001）
        
        Args:
            session_id: 会话ID
            interface_id: 接口编码（如 L00001）
            params: URL参数
            body: 请求体
            
        Returns:
            本地记忆存储的钱包信息（sub_wallet_id, api_key）
        """
        # 从 memory 读取子钱包信息
        sub_wallet_id = self.memory.get_wallet()
        
        # 判断是否已绑定
        if sub_wallet_id:
            return {
                "resCode": "S010000",
                "resMsg": u"查询成功",
                "subWalletId": sub_wallet_id,
                "bindStatus": u"已绑定"
            }
        else:
            return {
                "resCode": "S010000",
                "resMsg": u"未绑定",
                "subWalletId": None,
                "bindStatus": u"未绑定"
            }
    