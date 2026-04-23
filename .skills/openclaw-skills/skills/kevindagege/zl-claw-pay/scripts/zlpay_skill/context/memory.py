"""
记忆管理模块
"""

from typing import Optional, Dict, Any
from .session_manager import SessionManager
from .state_store import StateStore

# 存储键常量
sub_wallet_id_KEY = "sub_wallet_id"
API_KEY = "api_key"


class Memory:
    """记忆管理器 - 管理会话内记忆和非敏感缓存"""
    
    def __init__(self, session_manager, state_store):
        # type: (SessionManager, StateStore) -> None
        """
        初始化记忆管理器
        
        Args:
            session_manager: 会话管理器（会话内记忆）
            state_store: 状态存储器（非敏感缓存）
        """
        self.session_manager = session_manager
        self.state_store = state_store
    
    def remember_wallet(self, sub_wallet_id):
        # type: (str) -> None
        """
        记住钱包 ID（持久化到 state.json）

        Args:
            sub_wallet_id: 钱包 ID
        """
        self.state_store.save_preference(sub_wallet_id_KEY, sub_wallet_id)

    def recall_wallet(self):
        # type: () -> Optional[str]
        """
        回忆钱包 ID（从持久化存储获取）

        Returns:
            钱包 ID 或 None
        """
        return self.state_store.get_preference(sub_wallet_id_KEY)

    def forget_wallet(self):
        # type: () -> None
        """
        忘记/清除钱包 ID（从持久化存储删除）
        """
        self.state_store.delete_preference(sub_wallet_id_KEY)

    def get_wallet(self):
        # type: () -> Optional[str]
        """
        获取钱包 ID（recall_wallet 的别名）

        Returns:
            钱包 ID 或 None
        """
        return self.recall_wallet()

    def remember_api_key(self, api_key):
        # type: (str) -> None
        """
        记住 API Key（持久化到 state.json）

        Args:
            api_key: API Key
        """
        self.state_store.save_preference(API_KEY, api_key)

    def recall_api_key(self):
        # type: () -> Optional[str]
        """
        回忆 API Key（从持久化存储获取）

        Returns:
            API Key 或 None
        """
        return self.state_store.get_preference(API_KEY)
    
    def forget_api_key(self):
        # type: () -> None
        """
        忘记/清除 API Key（从持久化存储删除）
        """
        self.state_store.delete_preference(API_KEY)
    
    def set_preference(self, session_id, key, value):
        # type: (str, str, Any) -> None
        """
        设置用户偏好（会话内）
        
        Args:
            session_id: 会话 ID
            key: 偏好键
            value: 偏好值
        """
        self.session_manager.set_preference(session_id, key, value)
    
    def get_preference(self, session_id, key, default=None):
        # type: (str, str, Optional[Any]) -> Optional[Any]
        """
        获取用户偏好（从会话内获取）
        
        Args:
            session_id: 会话 ID
            key: 偏好键
            default: 默认值
            
        Returns:
            偏好值或默认值
        """
        return self.session_manager.get_preference(session_id, key, default)
    
    def save_api_response_cache(self, key, data, ttl=3600):
        # type: (str, Any, int) -> None
        """
        保存 API 响应缓存（非敏感）
        
        Args:
            key: 缓存键
            data: 缓存数据
            ttl: 缓存有效期（秒）
        """
        self.state_store.save_api_response(key, data, ttl)
    
    def get_api_response_cache(self, key):
        # type: (str) -> Optional[Any]
        """
        获取 API 响应缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存数据或 None
        """
        return self.state_store.get_api_response(key)
    
    def add_operation_history(self, action, result, metadata=None):
        # type: (str, str, Optional[Dict[str, Any]]) -> None
        """
        添加操作历史记录
        
        Args:
            action: 操作名称
            result: 操作结果（success/failure）
            metadata: 操作元数据
        """
        self.state_store.add_operation_history(action, result, metadata)
    
    def clear_session(self, session_id):
        # type: (str) -> None
        """
        清除会话记忆
        
        Args:
            session_id: 会话 ID
        """
        self.session_manager.clear_session(session_id)
    
    def cleanup(self):
        # type: () -> Dict[str, int]
        """
        清理过期数据
        
        Returns:
            清理统计信息
        """
        expired_sessions = self.session_manager.clear_expired_sessions()
        expired_caches = self.state_store.clean_expired_data()
        
        return {
            "expired_sessions": expired_sessions,
            "expired_caches": expired_caches
        }
