#!/usr/bin/env python3
"""
统一数据获取 - 解决多Agent API调用问题
"""
import json, time, os

CACHE_FILE = "~/.openclaw/skills/crypto-monitor-team/data_cache.json"
CACHE_TTL = 120  # 2分钟缓存

def load_cache():
    try:
        with open(os.path.expanduser(CACHE_FILE), 'r') as f:
            return json.load(f)
    except:
        return {"timestamp": 0, "data": {}}

def save_cache(data):
    with open(os.path.expanduser(CACHE_FILE), 'w') as f:
        json.dump(data, f)

def get_all_prices(force=False):
    """统一获取所有价格数据"""
    cache = load_cache()
    now = time.time()
    
    if not force and now - cache["timestamp"] < CACHE_TTL:
        return cache["data"]
    
    # 实际API调用 - 这里只做演示
    # 真实实现需要合并所有API调用
    cache["timestamp"] = now
    cache["data"] = {
        "BTC": {"price": 67100, "change": -0.5},
        "ETH": {"price": 2070, "change": 0.3},
        "XAU": {"price": 4580, "change": 0.2},
        "XAG": {"price": 73, "change": 1.5}
    }
    save_cache(cache)
    return cache["data"]

if __name__ == "__main__":
    data = get_all_prices()
    print(json.dumps(data, indent=2))
