#!/usr/bin/env python3
"""
对接已安装的高德地图技能，获取路线耗时
兼容 smart-map-guide 和 amap-lbs-skill
"""

import json
import os
import sys
import subprocess
import time
from datetime import datetime, timedelta
from typing import Optional, Tuple, Dict

def expand_user(path: str) -> str:
    return os.path.expanduser(path)

# 尝试相对导入，如果失败则使用绝对导入
try:
    from .config_manager import get_config
except ImportError:
    # 直接运行脚本时的导入方式
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from config_manager import get_config

def check_map_skill_installed() -> Tuple[bool, str]:
    """检查是否有高德地图技能安装"""
    # 检查 smart-map-guide
    skill_paths = [
        os.path.expanduser("~/AppData/Roaming/npm/node_modules/openclaw/skills/smart-map-guide"),
        os.path.expanduser("~/.openclaw/workspace/skills/smart-map-guide"),
        os.path.expanduser("~/AppData/Roaming/npm/node_modules/openclaw/skills/amap-lbs-skill"),
        os.path.expanduser("~/.openclaw/workspace/skills/amap-lbs-skill"),
    ]
    for path in skill_paths:
        if os.path.exists(path):
            skill_name = os.path.basename(path)
            return True, skill_name
    return False, ""

# 全局缓存
_GEOCODE_CACHE = {}
_DURATION_CACHE = {}
_CACHE_EXPIRY = 3600  # 缓存过期时间（秒）


def calculate_duration(from_address: str, to_address: str, api_key: str = None, mode: str = None) -> Optional[int]:
    """
    计算路程耗时（分钟）
    mode: driving/walking/riding/bus，默认使用配置中的default_transit_mode
    返回 None 表示计算失败
    """
    # 验证输入参数
    if not from_address or not isinstance(from_address, str):
        print("ERROR: Invalid from_address", file=sys.stderr)
        return None
    if not to_address or not isinstance(to_address, str):
        print("ERROR: Invalid to_address", file=sys.stderr)
        return None
    if mode and not isinstance(mode, str):
        print("ERROR: Invalid mode", file=sys.stderr)
        return None
    
    # 先看有没有已安装的地图技能
    has_skill, skill_name = check_map_skill_installed()
    
    config = get_config()
    if not api_key:
        api_key = config.get("amap_api_key", "")
    if not mode:
        mode = config.get("default_transit_mode", "driving")
    
    # 验证API密钥
    if not api_key:
        print("WARN: No amap_api_key configured, can't calculate duration", file=sys.stderr)
        return None
    if not isinstance(api_key, str) or len(api_key) < 10:
        print("WARN: Invalid amap_api_key format", file=sys.stderr)
        return None
    
    # 检查缓存
    cache_key = (from_address, to_address, mode)
    if cache_key in _DURATION_CACHE:
        cached_result, timestamp = _DURATION_CACHE[cache_key]
        if time.time() - timestamp < _CACHE_EXPIRY:
            print(f"INFO: Using cached duration for {from_address} to {to_address}", file=sys.stderr)
            return cached_result
    
    # 高德API端点对应不同出行方式
    api_endpoints = {
        "driving": "https://restapi.amap.com/v3/direction/driving",
        "walking": "https://restapi.amap.com/v3/direction/walking",
        "riding": "https://restapi.amap.com/v3/direction/bicycling",
        "bus": "https://restapi.amap.com/v3/direction/transit/integrated",
    }
    
    endpoint = api_endpoints.get(mode, api_endpoints["driving"])
    
    try:
        import requests
        import urllib.parse
        import time
        
        # 配置安全的请求会话
        session = requests.Session()
        # 启用证书验证
        session.verify = True
        # 设置合理的超时
        session.timeout = 15
        
        # 第一步：地理编码获取经纬度
        def geocode(address: str) -> Optional[Tuple[float, float]]:
            # 检查缓存
            if address in _GEOCODE_CACHE:
                cached_result, timestamp = _GEOCODE_CACHE[address]
                if time.time() - timestamp < _CACHE_EXPIRY:
                    print(f"INFO: Using cached geocode for {address}", file=sys.stderr)
                    return cached_result
            
            # 对地址进行URL编码
            encoded_address = urllib.parse.quote(address)
            url = f"https://restapi.amap.com/v3/geocode/geo?address={encoded_address}&key={api_key}"
            try:
                resp = session.get(url)
                # 检查响应状态码
                if resp.status_code != 200:
                    print(f"ERROR: Geocode API returned status code {resp.status_code}", file=sys.stderr)
                    return None
                data = resp.json()
                if data.get('status') == '1' and data.get('geocodes'):
                    location = data['geocodes'][0]['location']
                    lng, lat = map(float, location.split(','))
                    # 缓存结果
                    _GEOCODE_CACHE[address] = ((lng, lat), time.time())
                    return lng, lat
                return None
            except requests.RequestException as e:
                print(f"ERROR: Geocode request failed: {e}", file=sys.stderr)
                return None
        
        from_loc = geocode(from_address)
        to_loc = geocode(to_address)
        if not from_loc or not to_loc:
            return None
        
        # 第二步：路径规划获取耗时
        if mode == "bus":
            # 公交默认获取第一条路线的耗时
            url = f"{endpoint}?origin={from_loc[0]},{from_loc[1]}&destination={to_loc[0]},{to_loc[1]}&key={api_key}"
            try:
                resp = session.get(url)
                if resp.status_code != 200:
                    print(f"ERROR: Direction API returned status code {resp.status_code}", file=sys.stderr)
                    return None
                data = resp.json()
                if data.get('status') == '1' and data.get('route') and data.get('route', {}).get('transits'):
                    duration_sec = int(data['route']['transits'][0]['duration'])
                    duration_min = int(duration_sec / 60) + 1
                    # 缓存结果
                    _DURATION_CACHE[cache_key] = (duration_min, time.time())
                    return duration_min
            except requests.RequestException as e:
                print(f"ERROR: Direction request failed: {e}", file=sys.stderr)
                return None
        else:
            url = f"{endpoint}?origin={from_loc[0]},{from_loc[1]}&destination={to_loc[0]},{to_loc[1]}&key={api_key}"
            try:
                resp = session.get(url)
                if resp.status_code != 200:
                    print(f"ERROR: Direction API returned status code {resp.status_code}", file=sys.stderr)
                    return None
                data = resp.json()
                if data.get('status') == '1' and data.get('route') and data.get('route', {}).get('paths'):
                    # 耗时是秒，转分钟
                    duration_sec = int(data['route']['paths'][0]['duration'])
                    duration_min = int(duration_sec / 60) + 1
                    # 缓存结果
                    _DURATION_CACHE[cache_key] = (duration_min, time.time())
                    return duration_min
            except requests.RequestException as e:
                print(f"ERROR: Direction request failed: {e}", file=sys.stderr)
                return None
        
        return None
    except ImportError:
        print("ERROR: requests library not installed", file=sys.stderr)
        return None
    except Exception as e:
        print(f"ERROR: Failed to calculate duration: {e}", file=sys.stderr)
        return None

def calculate_remind_time(target_dt: datetime, duration_min: Optional[int], config: Dict, same_location: bool = False) -> datetime:
    """
 根据路程耗时计算提醒时间
    """
    if same_location:
        # 同地点，固定提前
        return target_dt - timedelta(minutes=config['same_location_remind_before_minutes'])
    
    if not duration_min or duration_min <= 0:
        # 没有耗时数据，默认提前 15 分钟
        return target_dt - timedelta(minutes=15 + config['buffer_minutes'])
    
    # 路程时间 + 缓冲
    total_advance = duration_min + config['buffer_minutes']
    return target_dt - timedelta(minutes=total_advance)

if __name__ == "__main__":
    # 修复Windows中文输出乱码：强制stdout用utf-8
    if sys.stdout.encoding and 'utf' not in sys.stdout.encoding.lower():
        sys.stdout.reconfigure(encoding='utf-8')
    if len(sys.argv) >= 3:
        from_addr = sys.argv[1]
        to_addr = sys.argv[2]
        duration = calculate_duration(from_addr, to_addr)
        print(json.dumps({"duration_minutes": duration}, ensure_ascii=False))
    else:
        has, name = check_map_skill_installed()
        print(f"Has installed map skill: {has}, name: {name}")
        config = get_config()
        print(f"Config: {json.dumps(config, ensure_ascii=False)}")
