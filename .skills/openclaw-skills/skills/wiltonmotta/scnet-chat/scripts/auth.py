#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCNet 认证模块 - 统一处理身份验证和 Token 管理

此模块集中管理所有与 SCNet API 认证相关的功能：
- HMAC-SHA256 签名生成
- Token 获取和缓存
- 计算中心信息获取
"""

import hmac
import hashlib
import requests
import json
import time
import os
import sys
from typing import Optional, Dict, Any

# 缓存文件路径
CACHE_FILE = os.path.expanduser("~/.scnet-chat-cache.json")


def _get_logger():
    """获取日志记录器（延迟导入避免循环依赖）"""
    # 延迟导入，避免循环依赖
    if 'scnet_chat' in sys.modules:
        from scnet_chat import get_logger
        return get_logger()
    return None


def _log_info(message: str):
    """记录信息日志"""
    logger = _get_logger()
    if logger:
        logger.log_info(message)


def _log_api_call(method: str, url: str, params: Any = None, 
                  response: Any = None, error: str = None, duration_ms: float = None):
    """记录API调用日志"""
    logger = _get_logger()
    if logger:
        logger.log(method, url, params, response, error=error, duration_ms=duration_ms)


def escape_json(s: Optional[str]) -> str:
    """转义JSON字符串"""
    if s is None:
        return ""
    return s.replace("\\", "\\\\").replace('"', '\\"')


def generate_signature(access_key: str, timestamp: str, user: str, secret_key: str) -> str:
    """生成HMAC-SHA256签名"""
    escaped_ak = escape_json(access_key)
    escaped_ts = escape_json(timestamp)
    escaped_user = escape_json(user)
    data_to_sign = f'{{"accessKey":"{escaped_ak}","timestamp":"{escaped_ts}","user":"{escaped_user}"}}'
    signature = hmac.new(
        key=secret_key.encode('utf-8'),
        msg=data_to_sign.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()
    return signature.lower()


def _save_cache(data: Dict[str, Any]):
    """保存数据到缓存文件"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"⚠️  保存缓存失败: {e}")


def _load_cache() -> Optional[Dict[str, Any]]:
    """从缓存文件加载数据"""
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception:
        pass
    return None


def _clear_cache():
    """清空缓存文件"""
    try:
        with open(CACHE_FILE, 'w', encoding='utf-8') as f:
            f.write('')
    except Exception:
        pass


def get_tokens(access_key: str, secret_key: str, user: str, use_cache_first: bool = True) -> Optional[Dict[str, Any]]:
    """获取SCNet用户token列表
    
    Args:
        access_key: Access Key
        secret_key: Secret Key  
        user: 用户名
        use_cache_first: 是否优先使用缓存（默认True）
    
    Returns:
        token数据或None
    """
    # 优先尝试从缓存加载
    if use_cache_first:
        cache_data = _load_cache()
        if cache_data and "clusters" in cache_data and len(cache_data["clusters"]) > 0:
            _log_info("从缓存加载token数据")
            # 构造与API返回格式一致的数据
            return {
                "code": "0",
                "msg": "success",
                "data": cache_data["clusters"]
            }
    
    # 缓存不存在，调用认证接口
    timestamp = str(int(time.time()))
    signature = generate_signature(access_key, timestamp, user, secret_key)
    tokens_url = "https://api.scnet.cn/api/user/v3/tokens"
    headers = {"user": user, "accessKey": access_key, "signature": signature, "timestamp": timestamp}

    start_time = time.time()
    try:
        response = requests.post(tokens_url, headers=headers, timeout=30)
        result = response.json()
        duration_ms = (time.time() - start_time) * 1000
        _log_api_call("POST", tokens_url, headers, result, duration_ms=duration_ms)

        # 成功后处理缓存
        if result and result.get("code") == "0":
            _clear_cache()  # 清空缓存文件

            clusters_data = result.get("data", [])
            # 检查是否有已有的缓存数据，保留default设置
            existing_cache = _load_cache()
            existing_defaults = {}
            if existing_cache and "clusters" in existing_cache:
                for c in existing_cache["clusters"]:
                    existing_defaults[c.get("clusterId")] = c.get("default", False)
            
            # 添加 default 字段，优先使用已有的设置，否则第一个为 true
            for i, cluster in enumerate(clusters_data):
                cluster_id = cluster.get("clusterId")
                if cluster_id in existing_defaults:
                    cluster["default"] = existing_defaults[cluster_id]
                else:
                    cluster["default"] = (i == 0)

            cache_data = {"clusters": clusters_data}
            _save_cache(cache_data)
            _log_info("token数据已保存到缓存")

        return result
    except Exception as e:
        duration_ms = (time.time() - start_time) * 1000
        _log_api_call("POST", tokens_url, headers, error=str(e), duration_ms=duration_ms)
        print(f"❌ 获取token失败: {e}")
        return None


def get_center_info(token: str) -> Optional[Dict[str, Any]]:
    """获取授权区域信息"""
    urls = ["https://www.scnet.cn/ac/openapi/v2/center"]
    headers = {"token": token, "Content-Type": "application/json"}

    for url in urls:
        start_time = time.time()
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                result = response.json()
                duration_ms = (time.time() - start_time) * 1000

                # 成功后处理缓存
                if result and result.get("code") == "0":
                    cache_data = _load_cache()
                    if cache_data and "clusters" in cache_data:
                        data = result.get("data", {})
                        # 筛选 enable="true" 的元素
                        url_fields = ['hpcUrls', 'aiUrls', 'efileUrls']
                        filtered_data = {}
                        for field in url_fields:
                            if field in data:
                                filtered_data[field] = [
                                    item for item in data[field]
                                    if item.get("enable") == "true"
                                ]
                        # clusterUserInfo 直接保留
                        if 'clusterUserInfo' in data:
                            filtered_data['clusterUserInfo'] = data['clusterUserInfo']

                        # 追加到 default 为 true 的 cluster 中
                        for cluster in cache_data["clusters"]:
                            if cluster.get("default") is True:
                                cluster.update(filtered_data)
                                break

                        _save_cache(cache_data)

                _log_api_call("GET", url, headers, result, duration_ms=duration_ms)
                return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            _log_api_call("GET", url, headers, error=str(e), duration_ms=duration_ms)
            continue
    return None


def get_hpc_url(center_info: Dict[str, Any]) -> Optional[str]:
    """获取hpcUrl（作业服务地址）"""
    if center_info.get("code") != "0":
        return None
    data = center_info.get("data", {})
    for url_info in data.get("hpcUrls", []):
        if url_info.get("enable") == "true":
            return url_info.get("url")
    return None


def get_efile_url(center_info: Dict[str, Any]) -> Optional[str]:
    """获取efileUrl（文件服务地址）"""
    if center_info.get("code") != "0":
        return None
    data = center_info.get("data", {})
    for url_info in data.get("efileUrls", []):
        if url_info.get("enable") == "true":
            return url_info.get("url")
    return None


def get_ai_url(center_info: Dict[str, Any]) -> Optional[str]:
    """获取aiUrl（AI服务地址）"""
    if center_info.get("code") != "0":
        return None
    data = center_info.get("data", {})
    for url_info in data.get("aiUrls", []):
        if url_info.get("enable") == "true":
            return url_info.get("url")
    return None


def get_home_path(center_info: Dict[str, Any]) -> Optional[str]:
    """获取用户家目录"""
    if center_info.get("code") != "0":
        return None
    data = center_info.get("data", {})
    return data.get("clusterUserInfo", {}).get("homePath")


def get_user_info(token: str) -> Optional[Dict[str, Any]]:
    """获取用户信息（包含账户余额）"""
    urls = ["https://www.scnet.cn/ac/openapi/v2/user"]
    headers = {"token": token, "Content-Type": "application/json"}
    for url in urls:
        start_time = time.time()
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                result = response.json()
                duration_ms = (time.time() - start_time) * 1000
                _log_api_call("GET", url, headers, result, duration_ms=duration_ms)
                return result
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            _log_api_call("GET", url, headers, error=str(e), duration_ms=duration_ms)
            continue
    return None


# 导出
__all__ = [
    'escape_json',
    'generate_signature',
    'get_tokens',
    'get_center_info',
    'get_hpc_url',
    'get_efile_url',
    'get_ai_url',
    'get_home_path',
    'get_user_info',
    '_load_cache',
    '_save_cache',
    '_clear_cache',
    'CACHE_FILE',
]
