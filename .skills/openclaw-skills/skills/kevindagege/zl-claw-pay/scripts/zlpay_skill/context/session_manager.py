# -*- coding: utf-8 -*-
"""
会话管理模块
"""

import time
from typing import Optional, Dict, Any


class SessionManager:
    """会话管理器 - 管理会话内 sub_wallet_id 记忆"""
    
    # 会话超时时间（秒）
    SESSION_TIMEOUT = 1800  # 30 分钟
    
    def __init__(self):
        """初始化会话管理器"""
        self._sessions = {}  # type: Dict[str, Dict[str, Any]]
    
    def remember_sub_wallet_id(self, session_id, sub_wallet_id):
        # type: (str, str) -> None
        """
        记住钱包 ID
        
        Args:
            session_id: 会话 ID
            sub_wallet_id: 钱包 ID
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = {}
        
        self._sessions[session_id]["sub_wallet_id"] = sub_wallet_id
        self._sessions[session_id]["last_access_time"] = time.time()
    
    def get_sub_wallet_id(self, session_id):
        # type: (str) -> Optional[str]
        """
        获取钱包 ID
        
        Args:
            session_id: 会话 ID
            
        Returns:
            钱包 ID 或 None
        """
        session = self._sessions.get(session_id)
        if not session:
            return None
        
        # 检查会话是否过期
        last_access = session.get("last_access_time", 0)
        if time.time() - last_access > self.SESSION_TIMEOUT:
            self.clear_session(session_id)
            return None
        
        # 更新最后访问时间
        session["last_access_time"] = time.time()
        
        return session.get("sub_wallet_id")
    
    def set_preference(self, session_id, key, value):
        # type: (str, str, Any) -> None
        """
        设置用户偏好
        
        Args:
            session_id: 会话 ID
            key: 偏好键
            value: 偏好值
        """
        if session_id not in self._sessions:
            self._sessions[session_id] = {}
        
        if "preferences" not in self._sessions[session_id]:
            self._sessions[session_id]["preferences"] = {}
        
        self._sessions[session_id]["preferences"][key] = value
        self._sessions[session_id]["last_access_time"] = time.time()
    
    def get_preference(self, session_id, key, default=None):
        # type: (str, str, Optional[Any]) -> Optional[Any]
        """
        获取用户偏好
        
        Args:
            session_id: 会话 ID
            key: 偏好键
            default: 默认值
            
        Returns:
            偏好值或默认值
        """
        session = self._sessions.get(session_id)
        if not session:
            return default
        
        preferences = session.get("preferences", {})
        return preferences.get(key, default)
    
    def clear_session(self, session_id):
        # type: (str) -> None
        """
        清除会话
        
        Args:
            session_id: 会话 ID
        """
        if session_id in self._sessions:
            del self._sessions[session_id]
    
    def clear_expired_sessions(self):
        # type: () -> int
        """
        清除过期会话
        
        Returns:
            清除的会话数量
        """
        current_time = time.time()
        expired_sessions = []
        
        for session_id, session in self._sessions.items():
            last_access = session.get("last_access_time", 0)
            if current_time - last_access > self.SESSION_TIMEOUT:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self._sessions[session_id]
        
        return len(expired_sessions)
