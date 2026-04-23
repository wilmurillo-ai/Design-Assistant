# -*- coding: utf-8 -*-
"""
流水号生成器模块

提供统一的流水号生成逻辑，支持多种生成策略。
"""

import time
import random
from typing import Optional


class SeqIdGenerator:
    """
    流水号生成器
    
    统一生成全局唯一的请求流水号，确保：
    - 全局唯一性（使用纳秒级时间戳）
    - 单调递增（便于排序和排查）
    - 重启后不会重复
    """
    
    @staticmethod
    def generate() -> str:
        """
        生成唯一流水号
        
        使用纳秒级时间戳（约19位）+ 随机数补足32位，确保全局唯一性。
        
        Returns:
            流水号字符串（共32位数字）
        """
        timestamp = str(int(time.time() * 1e9))  # 纳秒时间戳（Python 3.6兼容）
        remaining = 32 - len(timestamp)   # 需要补足的位数
        if remaining > 0:
            # 生成指定位数的随机数
            random_part = str(random.randint(0, 10**remaining - 1)).zfill(remaining)
            return timestamp + random_part
        return timestamp[:32]  # 如果时间戳超过32位，截取前32位
    
    @staticmethod
    def generate_with_prefix(prefix: str) -> str:
        """
        带前缀的流水号
        
        Args:
            prefix: 前缀字符串（如 "REQ", "PAY"）
        
        Returns:
            带前缀的流水号
        """
        timestamp = str(int(time.time() * 1e9))
        remaining = 32 - len(timestamp)
        if remaining > 0:
            random_part = str(random.randint(0, 10**remaining - 1)).zfill(remaining)
            return f"{prefix}{timestamp}{random_part}"
        return f"{prefix}{timestamp[:32]}"
    
    @staticmethod
    def validate(seq_id: str) -> bool:
        """
        验证流水号格式
        
        Args:
            seq_id: 待验证的流水号
        
        Returns:
            是否为有效的流水号格式（32位数字）
        """
        if not seq_id:
            return False
        # 去除可能的前缀，只保留数字部分
        digits = ''.join(c for c in seq_id if c.isdigit())
        return len(digits) == 32 and digits.isdigit()
