#!/usr/bin/env python3
"""
配置管理模块，集中处理配置相关的功能
"""

import json
import os
import sys
from typing import Dict, Optional


def expand_user(path: str) -> str:
    """安全地扩展用户路径，防止路径遍历攻击"""
    # 扩展用户路径
    expanded = os.path.expanduser(path)
    # 规范化路径，去除路径遍历字符
    normalized = os.path.normpath(expanded)
    # 确保路径在用户主目录下（防止路径遍历）
    home_dir = os.path.expanduser("~")
    # 处理Windows路径
    if os.name == 'nt':
        home_dir = home_dir.lower()
        normalized = normalized.lower()
    if not normalized.startswith(home_dir):
        # 如果路径不在用户主目录下，将其限制在主目录内
        normalized = os.path.join(home_dir, os.path.basename(normalized))
    return normalized


class ConfigManager:
    """配置管理器，负责读取、写入和管理配置
    
    功能：
    - 读取配置文件
    - 从环境变量获取API密钥
    - 自动创建默认配置
    - 保存配置到文件
    - 提供配置访问接口
    """
    
    def __init__(self, config_path: str = None):
        """初始化配置管理器
        
        Args:
            config_path: 配置文件路径，默认为 ~/.openclaw/workspace/data/simple-schedule/config.json
        """
        if config_path:
            self.config_path = expand_user(config_path)
        else:
            self.config_path = expand_user("~/.openclaw/workspace/data/simple-schedule/config.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """加载配置文件
        
        Returns:
            Dict: 配置字典
        """
        default_config = {
            "amap_api_key": "",  # 高德地图API密钥
            "default_start_address": "家",  # 默认出发地址
            "buffer_minutes": 10,  # 路程额外缓冲时间
            "same_location_remind_before_minutes": 10,  # 同地点提前提醒时间
            "default_transit_mode": "driving",  # 出行方式：driving(驾车)、walking(步行)、riding(骑行)、bus(公交)
            "ddl_remind_1day_before": True,  # DDL是否提前一天提醒
            "ddl_remind_1hour_before": True,  # DDL是否提前一小时提醒
            "data_path": "~/.openclaw/workspace/data/simple-schedule/schedule.json"  # 日程数据存储路径
        }
        
        
        # 配置文件不存在，创建默认配置
        if not os.path.exists(self.config_path):
            self._ensure_dir_exists()
            self._save_config(default_config)
            return default_config
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            # 从环境变量读取API密钥（优先级高于配置文件）
            if 'AMAP_API_KEY' in os.environ:
                config['amap_api_key'] = os.environ['AMAP_API_KEY']
            # 确保所有必要的配置项都存在
            for key, value in default_config.items():
                if key not in config:
                    config[key] = value
            return config
        except json.JSONDecodeError:
            # 如果文件损坏，返回默认配置
            print("配置文件损坏，使用默认配置", file=sys.stderr)
            return default_config
        except Exception as e:
            # 其他错误，返回默认配置
            print(f"加载配置文件失败: {e}", file=sys.stderr)
            return default_config
    
    def _ensure_dir_exists(self):
        """确保配置文件所在目录存在
        
        创建目录时设置权限为仅当前用户可访问
        """
        dir_path = os.path.dirname(self.config_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path, mode=0o700)  # 设置目录权限为仅当前用户可访问
    
    def _save_config(self, config: Dict):
        """保存配置文件
        
        Args:
            config: 配置字典
        """
        try:
            # 保存前确保目录存在
            self._ensure_dir_exists()
            # 写入文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
            # 在Windows上设置文件属性为隐藏
            if os.name == 'nt':
                try:
                    import ctypes
                    FILE_ATTRIBUTE_HIDDEN = 0x02
                    kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
                    file_attr = kernel32.GetFileAttributesW(self.config_path)
                    if file_attr != -1:
                        kernel32.SetFileAttributesW(self.config_path, file_attr | FILE_ATTRIBUTE_HIDDEN)
                except Exception:
                    pass
        except Exception as e:
            print(f"保存配置文件失败: {e}", file=sys.stderr)
    
    def get(self, key: str, default: any = None) -> any:
        """获取配置项
        
        Args:
            key: 配置键名
            default: 默认值
        
        Returns:
            any: 配置值
        """
        return self.config.get(key, default)
    
    def set(self, key: str, value: any):
        """设置配置项
        
        Args:
            key: 配置键名
            value: 配置值
        """
        self.config[key] = value
        self._save_config(self.config)
    
    def get_all(self) -> Dict:
        """获取所有配置
        
        Returns:
            Dict: 配置字典
        """
        return self.config


# 全局配置管理器实例
_config_manager = None


def get_config() -> Dict:
    """获取配置
    
    Returns:
        Dict: 配置字典
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.get_all()


def get_config_value(key: str, default: any = None) -> any:
    """获取特定配置值
    
    Args:
        key: 配置键名
        default: 默认值
    
    Returns:
        any: 配置值
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager.get(key, default)


def set_config_value(key: str, value: any):
    """设置特定配置值
    
    Args:
        key: 配置键名
        value: 配置值
    """
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    _config_manager.set(key, value)


if __name__ == "__main__":
    import sys
    # 修复Windows中文输出乱码：强制stdout用utf-8
    if sys.stdout.encoding and 'utf' not in sys.stdout.encoding.lower():
        sys.stdout.reconfigure(encoding='utf-8')
    config = get_config()
    print(f"Config: {json.dumps(config, ensure_ascii=False)}")
