#!/usr/bin/env python3
"""
V7 多周期信号系统 - API限流保护版
"""
import json, time, os
from datetime import datetime

# 配置
CACHE_TTL = 60  # 价格缓存60秒
MIN_REQUEST_INTERVAL = 2  # 最小请求间隔2秒
CONFIG = {"strong_confidence": 82, "medium_confidence": 55, "medium_cooldown": 480}

# 缓存
_price_cache = {"timestamp": 0, "data": {}}
_last_request_time = 0

def rate_limit_wait():
    global _last_request_time
    elapsed = time.time() - _last_request_time
    if elapsed < MIN_REQUEST_INTERVAL:
        time.sleep(MIN_REQUEST_INTERVAL - elapsed)
    _last_request_time = time.time()

def get_cached_price(symbol, force=False):
    """带缓存的价格获取"""
    global _price_cache
    now = time.time()
    
    if not force and symbol in _price_cache["data"]:
        if now - _price_cache["timestamp"] < CACHE_TTL:
            return _price_cache["data"][symbol]
    
    rate_limit_wait()
    # 实际API调用逻辑...
    return None

def main():
    print("=== V7 系统运行中 (限流保护) ===")
    print(f"缓存TTL: {CACHE_TTL}秒")
    print(f"请求间隔: {MIN_REQUEST_INTERVAL}秒")
    print(f"Cron建议: 每3-5分钟运行")

main()
