#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCNet File Manager - SCNet文件管理模块

注意：此模块保留独立功能，但推荐从 scnet_chat 导入 FileManager：
    from scnet_chat import FileManager, SCNetClient
    
    client = SCNetClient(access_key, secret_key, user)
    client.init_tokens()
    file_manager = client.get_file_manager()
"""

import os
import sys
from typing import Optional, Dict, Any, List, Tuple

# 导入认证模块
from auth import (
    get_tokens, get_center_info, get_efile_url, get_home_path,
    _load_cache, generate_signature
)

# 导入 requests 用于独立函数
import requests

# ============== 基础认证和通用方法 ==============

# 从 auth 模块导入的函数已足够，不再重复定义

# ============== 文件操作方法 ==============

def list_files(efile_url: str, token: str, path: Optional[str] = None, 
               limit: int = 100, start: int = 0) -> Optional[Dict[str, Any]]:
    """
    查询文件列表
    
    API: GET /efile/openapi/v2/file/list
    Note: efile_url 已经包含 /efile 后缀，不需要重复添加
    """
    url = f"{efile_url}/openapi/v2/file/list"
    headers = {"token": token, "Content-Type": "application/json"}
    params = {"limit": limit, "start": start, "order": "asc", "orderBy": "name"}
    if path:
        params["path"] = path
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        return response.json()
    except Exception as e:
        print(f"❌ 查询文件列表失败: {e}")
        return None


def check_file_exists(efile_url: str, token: str, path: str) -> bool:
    """
    检查文件/文件夹是否存在
    
    API: POST /efile/openapi/v2/file/exist
    """
    url = f"{efile_url}/openapi/v2/file/exist"
    headers = {"token": token, "Content-Type": "application/x-www-form-urlencoded"}
    payload = {"path": path}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        result = response.json()
        if result.get("code") == "0":
            return result.get("data", {}).get("exist", False)
        return False
    except Exception as e:
        print(f"❌ 检查文件存在性失败: {e}")
        return False


def create_folder(efile_url: str, token: str, path: str, create_parents: bool = True) -> bool:
    """
    创建文件夹
    
    API: POST /efile/openapi/v2/file/mkdir
    """
    url = f"{efile_url}/openapi/v2/file/mkdir"
    headers = {"token": token, "Content-Type": "application/json"}
    params = {"path": path, "createParents": str(create_parents).lower()}
    
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        result = response.json()
        if result.get("code") == "0":
            return True
        elif result.get("code") == "911021":
            # 文件夹已存在
            return True
        else:
            print(f"❌ 创建文件夹失败: {result.get('msg', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 创建文件夹失败: {e}")
        return False


def create_file(efile_url: str, token: str, file_path: str) -> bool:
    """
    创建空文件
    
    API: POST /efile/openapi/v2/file/touch
    """
    url = f"{efile_url}/openapi/v2/file/touch"
    headers = {"token": token, "Content-Type": "application/x-www-form-urlencoded"}
    payload = {"fileAbsolutePath": file_path}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        result = response.json()
        if result.get("code") == "0":
            return True
        elif result.get("code") == "911021":
            # 文件已存在
            return True
        else:
            print(f"❌ 创建文件失败: {result.get('msg', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 创建文件失败: {e}")
        return False


def upload_file(efile_url: str, token: str, local_path: str, remote_path: str, 
                cover: str = "cover") -> bool:
    """
    上传文件（普通上传，适合小文件）
    
    API: POST /efile/openapi/v2/file/upload
    """
    url = f"{efile_url}/openapi/v2/file/upload"
    headers = {"token": token}
    
    try:
        with open(local_path, 'rb') as f:
            files = {"file": (os.path.basename(local_path), f)}
            data = {"path": remote_path, "cover": cover}
            response = requests.post(url, headers=headers, data=data, files=files, timeout=300)
            result = response.json()
            if result.get("code") == "0":
                return True
            else:
                print(f"❌ 上传文件失败: {result.get('msg', '未知错误')}")
                return False
    except Exception as e:
        print(f"❌ 上传文件失败: {e}")
        return False


def upload_file_chunked(efile_url: str, token: str, local_path: str, remote_path: str,
                        chunk_size: int = 5 * 1024 * 1024, cover: str = "cover") -> bool:
    """
    分片上传文件（适合大文件）
    
    API: POST /efile/openapi/v2/file/burst (分片上传)
         POST /efile/openapi/v2/file/merge (合并分片)
    """
    url_burst = f"{efile_url}/openapi/v2/file/burst"
    url_merge = f"{efile_url}/openapi/v2/file/merge"
    headers = {"token": token}
    
    file_size = os.path.getsize(local_path)
    filename = os.path.basename(local_path)
    total_chunks = (file_size + chunk_size - 1) // chunk_size
    identifier = f"{file_size}-{filename.replace('.', '')}"
    
    try:
        # 分片上传
        with open(local_path, 'rb') as f:
            for chunk_number in range(1, total_chunks + 1):
                chunk_data = f.read(chunk_size)
                current_chunk_size = len(chunk_data)
                
                files = {"file": (filename, chunk_data)}
                data = {
                    "chunkNumber": str(chunk_number),
                    "cover": cover,
                    "filename": filename,
                    "path": remote_path,
                    "relativePath": filename,
                    "totalChunks": str(total_chunks),
                    "totalSize": str(file_size),
                    "chunkSize": str(chunk_size),
                    "currentChunkSize": str(current_chunk_size),
                    "identifier": identifier
                }
                
                response = requests.post(url_burst, headers=headers, data=data, files=files, timeout=60)
                result = response.json()
                if result.get("code") != "0":
                    print(f"❌ 分片 {chunk_number}/{total_chunks} 上传失败: {result.get('msg', '未知错误')}")
                    return False
                
                print(f"  分片 {chunk_number}/{total_chunks} 上传完成")
        
        # 合并分片
        merge_data = {
            "cover": cover,
            "filename": filename,
            "path": remote_path,
            "relativePath": filename,
            "identifier": identifier
        }
        response = requests.post(url_merge, headers=headers, data=merge_data, timeout=60)
        result = response.json()
        if result.get("code") == "0":
            return True
        else:
            print(f"❌ 合并分片失败: {result.get('msg', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"❌ 分片上传失败: {e}")
        return False


def download_file(efile_url: str, token: str, remote_path: str, local_path: str) -> bool:
    """
    下载文件
    
    API: GET /efile/openapi/v2/file/download
    """
    url = f"{efile_url}/openapi/v2/file/download"
    headers = {"token": token, "Content-Type": "application/json"}
    params = {"path": remote_path}
    
    try:
        response = requests.get(url, headers=headers, params=params, stream=True, timeout=300)
        if response.status_code == 200:
            # 确保本地目录存在
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        else:
            print(f"❌ 下载文件失败: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 下载文件失败: {e}")
        return False


def delete_file(efile_url: str, token: str, path: str, recursive: bool = False) -> bool:
    """
    删除文件/文件夹
    
    API: POST /efile/openapi/v2/file/remove
    """
    url = f"{efile_url}/openapi/v2/file/remove"
    headers = {"token": token, "Content-Type": "application/json"}
    params = {"paths": path, "recursive": str(recursive).lower()}
    
    try:
        response = requests.post(url, headers=headers, params=params, timeout=30)
        result = response.json()
        if result.get("code") == "0":
            return True
        else:
            print(f"❌ 删除失败: {result.get('msg', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        return False


def rename_file(efile_url: str, token: str, file_path: str, new_name: str) -> bool:
    """
    重命名文件
    
    API: POST /efile/openapi/v2/file/rename
    """
    url = f"{efile_url}/openapi/v2/file/rename"
    headers = {"token": token, "Content-Type": "application/x-www-form-urlencoded"}
    payload = {"fileAbsolutePath": file_path, "newName": new_name}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        result = response.json()
        if result.get("code") == "0":
            return True
        else:
            print(f"❌ 重命名失败: {result.get('msg', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 重命名失败: {e}")
        return False


def copy_file(efile_url: str, token: str, source_paths: List[str], target_path: str, cover: str = "cover") -> bool:
    """
    复制文件
    
    API: POST /efile/openapi/v2/file/copy
    """
    url = f"{efile_url}/openapi/v2/file/copy"
    headers = {"token": token, "Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "sourcePaths": ",".join(source_paths),
        "targetPath": target_path,
        "cover": cover
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=60)
        result = response.json()
        if result.get("code") == "0":
            return True
        else:
            print(f"❌ 复制失败: {result.get('msg', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 复制失败: {e}")
        return False


def move_file(efile_url: str, token: str, source_paths: List[str], target_path: str, cover: str = "cover") -> bool:
    """
    移动文件
    
    API: POST /efile/openapi/v2/file/move
    """
    url = f"{efile_url}/openapi/v2/file/move"
    headers = {"token": token, "Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "sourcePaths": ",".join(source_paths),
        "targetPath": target_path,
        "cover": cover
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=60)
        result = response.json()
        if result.get("code") == "0":
            return True
        else:
            print(f"❌ 移动失败: {result.get('msg', '未知错误')}")
            return False
    except Exception as e:
        print(f"❌ 移动失败: {e}")
        return False


def check_permission(efile_url: str, token: str, path: str, action: str = "READ") -> bool:
    """
    检查文件权限
    
    API: POST /efile/openapi/v2/file/permission
    action: READ, WRITE, EXECUTE
    """
    url = f"{efile_url}/openapi/v2/file/permission"
    headers = {"token": token, "Content-Type": "application/x-www-form-urlencoded"}
    payload = {"path": path, "permissionAction": action}
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        result = response.json()
        if result.get("code") == "0":
            return result.get("data", {}).get("allowed", False)
        return False
    except Exception as e:
        print(f"❌ 检查权限失败: {e}")
        return False


# ============== 高级封装方法 ==============

class SCNetFileManager:
    """SCNet文件管理器类（独立版本，支持直接API调用）
    
    推荐使用 scnet_chat.FileManager（通过 SCNetClient 获取）：
        from scnet_chat import SCNetClient
        client = SCNetClient(access_key, secret_key, user)
        client.init_tokens()
        file_manager = client.get_file_manager()
    """
    
    def __init__(self, access_key: str = None, secret_key: str = None, user: str = None):
        self.access_key = access_key
        self.secret_key = secret_key
        self.user = user
        self._cache = None
        self._default_cluster = None
        self._tokens_cache = {}
        self._efile_url_cache = {}
        self._home_path_cache = {}
    
    def _load_cache(self) -> Optional[Dict[str, Any]]:
        """加载缓存（带内存缓存）"""
        if self._cache is not None:
            return self._cache
        self._cache = _load_cache()
        # 找到 default 为 true 的 cluster
        if self._cache and "clusters" in self._cache:
            for cluster in self._cache["clusters"]:
                if cluster.get("default") is True:
                    self._default_cluster = cluster
                    break
        return self._cache
    
    def get_default_token(self) -> Optional[str]:
        """获取默认计算中心的token（从缓存）"""
        self._load_cache()
        if self._default_cluster:
            return self._default_cluster.get("token")
        return None
    
    def get_default_cluster_name(self) -> Optional[str]:
        """获取默认计算中心名称"""
        self._load_cache()
        if self._default_cluster:
            return self._default_cluster.get("clusterName")
        return None
    
    def get_default_efile_url(self) -> Optional[str]:
        """获取默认计算中心的efileUrl（从缓存）"""
        self._load_cache()
        if self._default_cluster and "efileUrls" in self._default_cluster:
            for url_info in self._default_cluster["efileUrls"]:
                if url_info.get("enable") == "true":
                    return url_info.get("url")
        return None
    
    def get_default_home_path(self) -> Optional[str]:
        """获取默认计算中心的家目录（从缓存）"""
        self._load_cache()
        if self._default_cluster and "clusterUserInfo" in self._default_cluster:
            return self._default_cluster["clusterUserInfo"].get("homePath")
        return None
    
    def get_cluster_token(self, cluster_name: str = None) -> Optional[str]:
        """获取指定计算中心的token"""
        if not cluster_name:
            # 优先从缓存获取默认token
            default_token = self.get_default_token()
            if default_token:
                return default_token
        
        # 从缓存中获取指定计算中心的token
        self._load_cache()
        if self._cache and "clusters" in self._cache:
            for cluster in self._cache["clusters"]:
                if cluster_name in cluster.get("clusterName", ""):
                    return cluster.get("token")
        
        # 回退到API获取（如果提供了access_key等）
        if self.access_key and cluster_name:
            if cluster_name in self._tokens_cache:
                return self._tokens_cache[cluster_name]
            
            tokens_data = get_tokens(self.access_key, self.secret_key, self.user)
            if tokens_data and tokens_data.get("code") == "0":
                for token_info in tokens_data.get("data", []):
                    name = token_info.get("clusterName", "")
                    token = token_info.get("token", "")
                    self._tokens_cache[name] = token
                return self._tokens_cache.get(cluster_name)
        
        return None
    
    def get_cluster_efile_url(self, cluster_name: str = None) -> Optional[str]:
        """获取指定计算中心的efileUrl"""
        if not cluster_name:
            return self.get_default_efile_url()
        
        # 从缓存中获取
        self._load_cache()
        if self._cache and "clusters" in self._cache:
            for cluster in self._cache["clusters"]:
                if cluster_name in cluster.get("clusterName", ""):
                    if "efileUrls" in cluster:
                        for url_info in cluster["efileUrls"]:
                            if url_info.get("enable") == "true":
                                return url_info.get("url")
        
        # 回退到API获取
        token = self.get_cluster_token(cluster_name)
        if not token:
            return None
        
        center_info = get_center_info(token)
        if not center_info:
            return None
        
        efile_url = get_efile_url(center_info)
        if efile_url:
            self._efile_url_cache[cluster_name] = efile_url
        
        return efile_url
    
    def get_cluster_home_path(self, cluster_name: str = None) -> Optional[str]:
        """获取指定计算中心的家目录"""
        if not cluster_name:
            return self.get_default_home_path()
        
        # 从缓存中获取
        self._load_cache()
        if self._cache and "clusters" in self._cache:
            for cluster in self._cache["clusters"]:
                if cluster_name in cluster.get("clusterName", ""):
                    if "clusterUserInfo" in cluster:
                        return cluster["clusterUserInfo"].get("homePath")
        
        # 回退到API获取
        if cluster_name in self._home_path_cache:
            return self._home_path_cache[cluster_name]
        
        token = self.get_cluster_token(cluster_name)
        if not token:
            return None
        
        center_info = get_center_info(token)
        if not center_info:
            return None
        
        home_path = get_home_path(center_info)
        if home_path:
            self._home_path_cache[cluster_name] = home_path
        
        return home_path
    
    def _get_efile_url_and_token(self, cluster_name: str = None) -> Tuple[Optional[str], Optional[str]]:
        """获取efileUrl和token"""
        efile_url = self.get_cluster_efile_url(cluster_name)
        token = self.get_cluster_token(cluster_name)
        return efile_url, token
    
    # ============== 便捷操作方法 ==============
    
    def list_dir(self, cluster_name: str = None, path: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """列出目录内容"""
        efile_url, token = self._get_efile_url_and_token(cluster_name)
        if not efile_url or not token:
            cluster_display = cluster_name if cluster_name else "默认计算中心"
            print(f"❌ 无法获取 {cluster_display} 的文件服务地址或token")
            return None
        return list_files(efile_url, token, path)
    
    def mkdir(self, cluster_name: str = None, path: str = None, create_parents: bool = True) -> bool:
        """创建目录"""
        if path is None:
            print("❌ 必须指定目录路径")
            return False
        efile_url, token = self._get_efile_url_and_token(cluster_name)
        if not efile_url or not token:
            cluster_display = cluster_name if cluster_name else "默认计算中心"
            print(f"❌ 无法获取 {cluster_display} 的文件服务地址或token")
            return False
        return create_folder(efile_url, token, path, create_parents)
    
    def touch(self, cluster_name: str = None, file_path: str = None) -> bool:
        """创建空文件"""
        if file_path is None:
            print("❌ 必须指定文件路径")
            return False
        efile_url, token = self._get_efile_url_and_token(cluster_name)
        if not efile_url or not token:
            cluster_display = cluster_name if cluster_name else "默认计算中心"
            print(f"❌ 无法获取 {cluster_display} 的文件服务地址或token")
            return False
        return create_file(efile_url, token, file_path)
    
    def upload(self, cluster_name: str = None, local_path: str = None, remote_path: str = None, use_chunk: bool = False) -> bool:
        """上传文件"""
        if local_path is None or remote_path is None:
            print("❌ 必须指定本地和远程路径")
            return False
        efile_url, token = self._get_efile_url_and_token(cluster_name)
        if not efile_url or not token:
            cluster_display = cluster_name if cluster_name else "默认计算中心"
            print(f"❌ 无法获取 {cluster_display} 的文件服务地址或token")
            return False
        
        if use_chunk:
            return upload_file_chunked(efile_url, token, local_path, remote_path)
        else:
            return upload_file(efile_url, token, local_path, remote_path)
    
    def download(self, cluster_name: str = None, remote_path: str = None, local_path: str = None) -> bool:
        """下载文件"""
        if remote_path is None or local_path is None:
            print("❌ 必须指定远程和本地路径")
            return False
        efile_url, token = self._get_efile_url_and_token(cluster_name)
        if not efile_url or not token:
            cluster_display = cluster_name if cluster_name else "默认计算中心"
            print(f"❌ 无法获取 {cluster_display} 的文件服务地址或token")
            return False
        return download_file(efile_url, token, remote_path, local_path)
    
    def remove(self, cluster_name: str = None, path: str = None, recursive: bool = False) -> bool:
        """删除文件/目录"""
        if path is None:
            print("❌ 必须指定路径")
            return False
        efile_url, token = self._get_efile_url_and_token(cluster_name)
        if not efile_url or not token:
            cluster_display = cluster_name if cluster_name else "默认计算中心"
            print(f"❌ 无法获取 {cluster_display} 的文件服务地址或token")
            return False
        return delete_file(efile_url, token, path, recursive)
    
    def exists(self, cluster_name: str = None, path: str = None) -> bool:
        """检查文件是否存在"""
        if path is None:
            print("❌ 必须指定路径")
            return False
        efile_url, token = self._get_efile_url_and_token(cluster_name)
        if not efile_url or not token:
            cluster_display = cluster_name if cluster_name else "默认计算中心"
            print(f"❌ 无法获取 {cluster_display} 的文件服务地址或token")
            return False
        return check_file_exists(efile_url, token, path)


# 导出
__all__ = [
    'SCNetFileManager',
    'list_files', 'check_file_exists', 'create_folder', 'create_file',
    'upload_file', 'upload_file_chunked', 'download_file', 'delete_file',
    'rename_file', 'copy_file', 'move_file', 'check_permission',
    'get_tokens', 'get_center_info', 'get_efile_url', 'get_home_path',
]


if __name__ == "__main__":
    print("SCNet File Manager Module")
    print("推荐用法: from scnet_chat import SCNetClient")
    print("          client = SCNetClient(...)")
    print("          file_manager = client.get_file_manager()")
