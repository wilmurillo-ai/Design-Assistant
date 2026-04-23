#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单的插件管理器
用于眠小兔睡眠健康技能
"""

import importlib
from typing import Dict, Any, List, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, Any
from enum import Enum

class PluginType(Enum):
    """插件类型枚举"""
    ANALYZER = "analyzer"
    STRESS = "stress"
    MEDITATION = "meditation"
    REPORT = "report"
    UTILITY = "utility"

@dataclass
class PluginInfo:
    """插件信息"""
    name: str
    version: str
    description: str
    author: str = ""
    config: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'version': self.version,
            'description': self.description,
            'author': self.author,
            'config': self.config or {}
        }

class BasePlugin(ABC):
    """插件基类"""
    
    @abstractmethod
    def execute(self, *args, **kwargs) -> Any:
        """执行插件功能"""
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """获取插件名称"""
        pass
    
    @abstractmethod
    def get_info(self) -> PluginInfo:
        """获取插件信息"""
        pass

class PluginManager:
    """插件管理器"""
    
    def __init__(self):
        self.plugins = {}
        self.initialized = False
    
    def register_plugin(self, name: str, plugin_class):
        """注册插件"""
        self.plugins[name] = plugin_class
        print(f"[INFO] 注册插件: {name}")
    
    def get_plugin(self, name: str):
        """获取插件实例"""
        if name in self.plugins:
            plugin_class = self.plugins[name]
            return plugin_class()
        return None
    
    def list_plugins(self) -> List[str]:
        """列出所有插件"""
        return list(self.plugins.keys())
    
    def has_plugin(self, name: str) -> bool:
        """检查是否有指定插件"""
        return name in self.plugins
    
    def initialize(self):
        """初始化所有插件"""
        if self.initialized:
            return
        
        print("[INFO] 初始化插件管理器")
        self.initialized = True
    
    def shutdown(self):
        """关闭插件管理器"""
        print("[INFO] 关闭插件管理器")
        self.plugins.clear()
        self.initialized = False