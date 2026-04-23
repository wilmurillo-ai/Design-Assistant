#!/usr/bin/env python3
"""
适配器基类 - 支持多平台技能接入

所有平台适配器必须继承此类
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from pathlib import Path


class SkillAdapter(ABC):
    """
    技能适配器基类
    
    支持的平台：
    - OpenClaw
    - GPTs / GPT Store
    - 钉钉
    - 飞书
    - 腾讯
    - 智谱
    - 文心
    - 自定义框架
    """
    
    def __init__(self, platform_name: str, config: Optional[Dict] = None):
        self.platform_name = platform_name
        self.config = config or {}
        self._connected = False
    
    @abstractmethod
    def connect(self) -> bool:
        """
        连接到平台
        
        Returns:
            bool: 连接是否成功
        """
        pass
    
    @abstractmethod
    def get_skill_list(self) -> list:
        """
        获取平台上的技能列表
        
        Returns:
            list: 技能列表
        """
        pass
    
    @abstractmethod
    def get_skill_metadata(self, skill_id: str) -> Dict:
        """
        获取技能元数据
        
        Args:
            skill_id: 技能ID
            
        Returns:
            Dict: 技能元数据
        """
        pass
    
    @abstractmethod
    def track_skill_usage(self, skill_id: str, metrics: Dict) -> Dict:
        """
        追踪技能使用（拦截调用）
        
        Args:
            skill_id: 技能ID
            metrics: 使用指标
            
        Returns:
            Dict: 追踪结果
        """
        pass
    
    @abstractmethod
    def update_skill(self, skill_id: str, updates: Dict) -> bool:
        """
        更新技能
        
        Args:
            skill_id: 技能ID
            updates: 更新内容
            
        Returns:
            bool: 更新是否成功
        """
        pass
    
    def is_connected(self) -> bool:
        """检查是否已连接"""
        return self._connected


class AdapterRegistry:
    """适配器注册表"""
    
    _adapters: Dict[str, SkillAdapter] = {}
    
    @classmethod
    def register(cls, name: str, adapter: SkillAdapter):
        """注册适配器"""
        cls._adapters[name] = adapter
    
    @classmethod
    def get(cls, name: str) -> Optional[SkillAdapter]:
        """获取适配器"""
        return cls._adapters.get(name)
    
    @classmethod
    def list_adapters(cls) -> list:
        """列出所有适配器"""
        return list(cls._adapters.keys())
