# -*- coding: utf-8 -*-
"""
统一日志管理模块

提供项目统一的日志配置和管理，包括：
- 统一的日志格式
- 统一的日志级别控制
- 自动脱敏敏感信息
- 文件和控制台双输出
"""

import logging
import os
import time
from logging.handlers import RotatingFileHandler
from pathlib import Path

from .config import Config
from .security.log_filter import SensitiveDataFilter


class LogManager:
    """日志管理器 - 统一配置项目日志"""
    
    # 日志格式
    CONSOLE_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    FILE_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
    
    # 日志文件配置
    MAX_BYTES = 10 * 1024 * 1024  # 10MB
    BACKUP_COUNT = 5
    
    # 日志清理配置（保留天数）
    LOG_RETENTION_DAYS = 30
    
    _initialized = False
    
    @classmethod
    def setup(cls, log_dir=None, log_level=None):
        """
        初始化项目日志配置
        
        Args:
            log_dir: 日志目录，默认使用 Config.LOG_DIR
            log_level: 日志级别，默认使用 Config.get_log_level()
        """
        if cls._initialized:
            return
        
        log_dir = log_dir or Config.LOG_DIR
        log_level = log_level or Config.get_log_level()
        
        # 确保日志目录存在
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        
        # 清理过期日志
        cls._cleanup_old_logs(log_dir)
        
        # 获取根日志器
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # 清除现有处理器（避免重复添加）
        root_logger.handlers.clear()
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(logging.Formatter(cls.CONSOLE_FORMAT))
        
        # 创建文件处理器
        log_file = os.path.join(log_dir, 'zlpay.log')
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=cls.MAX_BYTES,
            backupCount=cls.BACKUP_COUNT,
            encoding='utf-8'
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(logging.Formatter(cls.FILE_FORMAT))
        
        # 添加脱敏过滤器
        sensitive_filter = SensitiveDataFilter()
        console_handler.addFilter(sensitive_filter)
        file_handler.addFilter(sensitive_filter)
        
        # 添加到根日志器
        root_logger.addHandler(console_handler)
        root_logger.addHandler(file_handler)
        
        cls._initialized = True
        root_logger.info(f"[LogManager] 日志初始化完成，级别: {log_level}，目录: {log_dir}")
    
    @classmethod
    def _cleanup_old_logs(cls, log_dir):
        """
        清理超过保留天数的日志文件
        
        Args:
            log_dir: 日志目录路径
        """
        if cls.LOG_RETENTION_DAYS <= 0:
            return
        
        cutoff_time = time.time() - (cls.LOG_RETENTION_DAYS * 24 * 60 * 60)
        removed_count = 0
        
        try:
            for filename in os.listdir(log_dir):
                if not filename.endswith('.log'):
                    continue
                
                file_path = os.path.join(log_dir, filename)
                if not os.path.isfile(file_path):
                    continue
                
                # 检查文件修改时间
                file_mtime = os.path.getmtime(file_path)
                if file_mtime < cutoff_time:
                    try:
                        os.remove(file_path)
                        removed_count += 1
                    except OSError:
                        pass
            
            if removed_count > 0:
                logging.getLogger().info(f"[LogManager] 清理日志文件: {removed_count}个")
        except OSError:
            pass

    @classmethod
    def get_logger(cls, name):
        """
        获取日志器
        
        Args:
            name: 日志器名称（通常使用 __name__）
            
        Returns:
            配置好的日志器
        """
        if not cls._initialized:
            cls.setup()
        return logging.getLogger(name)


def get_logger(name):
    """
    便捷函数：获取日志器
    
    Args:
        name: 日志器名称
        
    Returns:
        配置好的日志器
    """
    return LogManager.get_logger(name)
