# -*- coding: utf-8 -*-
"""
状态存储模块 - 跨会话非敏感缓存存储
"""

import os
import json
import time
from typing import Optional, List, Dict, Any

from ..log_manager import get_logger

logger = get_logger(__name__)


class StateStore:
    """状态存储器 - 持久化非敏感缓存到本地文件"""
    
    def __init__(self, state_file_path, retention_days=90):
        # type: (str, int) -> None
        """
        初始化状态存储器
        
        Args:
            state_file_path: 状态文件路径
            retention_days: 数据保留天数
        """
        self.state_file_path = state_file_path
        self.retention_days = retention_days
        self._memory_cache = None  # type: Optional[Dict[str, Any]]
        self._cache_timestamp = 0
        self._cache_ttl = 30  # 内存缓存有效期（秒）
        self._ensure_state_dir()
    
    def _ensure_state_dir(self):
        # type: () -> None
        """确保状态文件目录存在"""
        state_dir = os.path.dirname(self.state_file_path)
        if not os.path.exists(state_dir):
            os.makedirs(state_dir)
    
    def _is_cache_valid(self):
        # type: () -> bool
        """检查内存缓存是否有效"""
        if self._memory_cache is None:
            return False
        return time.time() - self._cache_timestamp < self._cache_ttl
    
    def _check_file_permission(self):
        # type: () -> None
        """检查状态文件权限，如果权限过于宽松则警告"""
        try:
            file_stat = os.stat(self.state_file_path)
            file_mode = file_stat.st_mode & 0o777
            # 检查是否仅所有者可读写（0o600）
            if file_mode != 0o600:
                logger.warning(
                    u"状态文件 {} 权限为 {:o}，建议设置为 600（仅所有者可读写）".format(
                        self.state_file_path, file_mode
                    )
                )
        except Exception:
            pass
    
    def _load_state(self):
        # type: () -> Dict[str, Any]
        """
        加载状态文件
        
        Returns:
            状态数据字典
        """
        # 优先使用内存缓存
        if self._is_cache_valid():
            return self._memory_cache
        
        if not os.path.exists(self.state_file_path):
            self._memory_cache = self._init_state()
            self._cache_timestamp = time.time()
            return self._memory_cache
        
        try:
            with open(self.state_file_path, "r", encoding="utf-8") as f:
                self._memory_cache = json.load(f)
                self._cache_timestamp = time.time()
                # 检查文件权限
                self._check_file_permission()
                return self._memory_cache
        except json.JSONDecodeError as e:
            logger.warning(u"状态文件 JSON 格式错误，使用初始状态: {}".format(str(e)))
            self._memory_cache = self._init_state()
            self._cache_timestamp = time.time()
            return self._memory_cache
        except Exception as e:
            logger.warning(u"读取状态文件失败，使用初始状态: {}".format(str(e)))
            self._memory_cache = self._init_state()
            self._cache_timestamp = time.time()
            return self._memory_cache
    
    def _save_state(self, state):
        # type: (Dict[str, Any]) -> None
        """
        保存状态文件
        
        Args:
            state: 状态数据字典
        """
        # 更新内存缓存
        self._memory_cache = state
        self._cache_timestamp = time.time()
        
        with open(self.state_file_path, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        
        # 设置文件权限为仅所有者可读写 (600)
        os.chmod(self.state_file_path, 0o600)
    
    def _init_state(self):
        # type: () -> Dict[str, Any]
        """
        初始化状态结构
        
        Returns:
            初始状态字典
        """
        return {
            "version": "1.0.0",
            "cache": {
                "api_responses": {},
                "user_preferences": {},
                "operation_history": []
            }
        }
    
    def save_api_response(self, key, data, ttl=3600):
        # type: (str, Any, int) -> None
        """
        保存 API 响应缓存
        
        Args:
            key: 缓存键
            data: 缓存数据
            ttl: 缓存有效期（秒，默认 1 小时）
        """
        state = self._load_state()
        
        state["cache"]["api_responses"][key] = {
            "data": data,
            "timestamp": time.time(),
            "ttl": ttl
        }
        
        self._save_state(state)
    
    def get_api_response(self, key):
        # type: (str) -> Optional[Any]
        """
        获取 API 响应缓存
        
        Args:
            key: 缓存键
            
        Returns:
            缓存数据或 None（如果过期或不存在）
        """
        state = self._load_state()
        
        if key not in state["cache"]["api_responses"]:
            return None
        
        cache_entry = state["cache"]["api_responses"][key]
        timestamp = cache_entry.get("timestamp", 0)
        ttl = cache_entry.get("ttl", 3600)
        
        # 检查缓存是否过期
        if time.time() - timestamp > ttl:
            del state["cache"]["api_responses"][key]
            self._save_state(state)
            return None
        
        return cache_entry.get("data")
    
    def save_preference(self, key, value):
        # type: (str, Any) -> None
        """
        保存用户偏好
        
        Args:
            key: 偏好键
            value: 偏好值
        """
        state = self._load_state()
        state["cache"]["user_preferences"][key] = value
        self._save_state(state)
    
    def get_preference(self, key, default=None):
        # type: (str, Optional[Any]) -> Optional[Any]
        """
        获取用户偏好
        
        Args:
            key: 偏好键
            default: 默认值
            
        Returns:
            偏好值或默认值
        """
        state = self._load_state()
        return state["cache"]["user_preferences"].get(key, default)
    
    def delete_preference(self, key):
        # type: (str) -> None
        """
        删除用户偏好
        
        Args:
            key: 偏好键
        """
        state = self._load_state()
        if key in state["cache"]["user_preferences"]:
            del state["cache"]["user_preferences"][key]
            self._save_state(state)
    
    def add_operation_history(self, action, result, metadata=None):
        # type: (str, str, Optional[Dict[str, Any]]) -> None
        """
        添加操作历史记录
        
        Args:
            action: 操作名称
            result: 操作结果（success/failure）
            metadata: 操作元数据
        """
        state = self._load_state()
        
        history_entry = {
            "action": action,
            "result": result,
            "timestamp": time.time(),
            "metadata": metadata or {}
        }
        
        # 保留最近 100 条记录
        state["cache"]["operation_history"].append(history_entry)
        if len(state["cache"]["operation_history"]) > 100:
            state["cache"]["operation_history"] = state["cache"]["operation_history"][-100:]
        
        self._save_state(state)
    
    def get_operation_history(self, limit=10):
        # type: (int) -> List[Dict[str, Any]]
        """
        获取操作历史记录
        
        Args:
            limit: 返回的最大记录数
            
        Returns:
            操作历史列表
        """
        state = self._load_state()
        history = state["cache"]["operation_history"]
        return history[-limit:] if history else []
    
    def clean_expired_data(self):
        # type: () -> int
        """
        清理过期数据
        
        Returns:
            清理的缓存条数
        """
        state = self._load_state()
        current_time = time.time()
        cleaned_count = 0
        
        # 清理过期的 API 响应缓存
        expired_keys = []
        for key, cache_entry in state["cache"]["api_responses"].items():
            timestamp = cache_entry.get("timestamp", 0)
            ttl = cache_entry.get("ttl", 3600)
            if current_time - timestamp > ttl:
                expired_keys.append(key)
        
        for key in expired_keys:
            del state["cache"]["api_responses"][key]
            cleaned_count += 1
        
        # 清理超过保留天数的操作历史
        retention_seconds = self.retention_days * 24 * 3600
        history = state["cache"]["operation_history"]
        new_history = [
            entry for entry in history
            if current_time - entry.get("timestamp", 0) <= retention_seconds
        ]
        
        if len(new_history) < len(history):
            cleaned_count += len(history) - len(new_history)
            state["cache"]["operation_history"] = new_history
        
        if cleaned_count > 0:
            self._save_state(state)
        
        return cleaned_count
