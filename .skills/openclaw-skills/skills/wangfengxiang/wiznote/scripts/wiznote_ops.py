#!/usr/bin/env python3
"""
WizNote Operations Module
为知笔记操作模块 - 实现笔记的增删改查

Author: OpenClaw Worker
Date: 2026-03-26
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional

try:
    import requests
except ImportError:
    print("❌ 缺少依赖: requests")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WizNoteOps:
    """为知笔记操作类"""
    
    def __init__(self, endpoint: str, token: str, kb_guid: str):
        """
        初始化操作类
        
        Args:
            endpoint: API 地址
            token: 认证 token
            kb_guid: 知识库 GUID
        """
        self.endpoint = endpoint
        self.token = token
        self.kb_guid = kb_guid
        self.session = requests.Session()
    
    def list_categories(self) -> List[str]:
        """
        获取所有目录
        
        Returns:
            List[str]: 目录列表
        """
        url = f"{self.endpoint}/ks/category/all/{self.kb_guid}"
        params = {"token": self.token}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('returnCode') == 200:
                categories = data.get('result', [])
                logger.info(f"✅ 获取到 {len(categories)} 个目录")
                return categories
            else:
                logger.error(f"获取目录失败: {data.get('returnMessage')}")
                return []
        except Exception as e:
            logger.error(f"获取目录异常: {e}")
            return []
    
    def list_notes_by_category(self, category: str, start: int = 0, count: int = 50) -> List[Dict]:
        """
        按目录获取笔记列表
        
        Args:
            category: 目录路径（如 "/My Notes/"）
            start: 起始位置
            count: 数量
            
        Returns:
            List[Dict]: 笔记列表
        """
        url = f"{self.endpoint}/ks/note/list/category/{self.kb_guid}"
        params = {
            "token": self.token,
            "category": category,
            "start": start,
            "count": count,
            "orderBy": "modified",
            "ascending": "desc"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('returnCode') == 200:
                notes = data.get('result', [])
                logger.info(f"✅ 获取到 {len(notes)} 篇笔记")
                return notes
            else:
                logger.error(f"获取笔记失败: {data.get('returnMessage')}")
                return []
        except Exception as e:
            logger.error(f"获取笔记异常: {e}")
            return []
    
    def list_tags(self) -> List[Dict]:
        """
        获取所有标签
        
        Returns:
            List[Dict]: 标签列表
        """
        url = f"{self.endpoint}/ks/tag/all/{self.kb_guid}"
        params = {"token": self.token}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('returnCode') == 200:
                tags = data.get('result', [])
                logger.info(f"✅ 获取到 {len(tags)} 个标签")
                return tags
            else:
                logger.error(f"获取标签失败: {data.get('returnMessage')}")
                return []
        except Exception as e:
            logger.error(f"获取标签异常: {e}")
            return []
    
    def list_notes_by_tag(self, tag_guid: str, start: int = 0, count: int = 50) -> List[Dict]:
        """
        按标签获取笔记列表
        
        Args:
            tag_guid: 标签 GUID
            start: 起始位置
            count: 数量
            
        Returns:
            List[Dict]: 笔记列表
        """
        url = f"{self.endpoint}/ks/note/list/tag/{self.kb_guid}"
        params = {
            "token": self.token,
            "tag": tag_guid,
            "start": start,
            "count": count,
            "orderBy": "modified",
            "ascending": "desc"
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('returnCode') == 200:
                notes = data.get('result', [])
                logger.info(f"✅ 获取到 {len(notes)} 篇笔记")
                return notes
            else:
                logger.error(f"获取笔记失败: {data.get('returnMessage')}")
                return []
        except Exception as e:
            logger.error(f"获取笔记异常: {e}")
            return []
    
    def get_note_detail(self, doc_guid: str) -> Optional[Dict]:
        """
        获取笔记详情
        
        Args:
            doc_guid: 文档 GUID
            
        Returns:
            Optional[Dict]: 笔记详情
        """
        url = f"{self.endpoint}/ks/note/download/{self.kb_guid}/{doc_guid}"
        params = {"token": self.token}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('returnCode') == 200:
                note = data.get('result')
                logger.info(f"✅ 获取笔记详情成功: {note.get('title')}")
                return note
            else:
                logger.error(f"获取笔记详情失败: {data.get('returnMessage')}")
                return None
        except Exception as e:
            logger.error(f"获取笔记详情异常: {e}")
            return None
    
    def create_note(self, title: str, html: str, category: str = "/My Notes/", tags: str = "") -> Optional[Dict]:
        """
        创建笔记
        
        Args:
            title: 笔记标题
            html: HTML 内容
            category: 分类路径
            tags: 标签（注意：标签需要是 GUID，不是字符串）
            
        Returns:
            Optional[Dict]: 创建结果
        """
        url = f"{self.endpoint}/ks/note/create/{self.kb_guid}"
        params = {
            "clientType": "web",
            "clientVersion": "4.0",
            "lang": "zh-cn"
        }
        
        data = {
            "kbGuid": self.kb_guid,
            "html": html,
            "category": category,
            "owner": os.getenv('WIZ_USER', ''),
            "tags": tags,
            "title": title,
            "params": None,
            "appInfo": None
        }
        
        try:
            response = self.session.post(
                url,
                params=params,
                json=data,
                headers={
                    "X-Wiz-Token": self.token,
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            result = response.json()
            
            if result.get('returnCode') == 200:
                doc = result.get('doc', {})
                logger.info(f"✅ 创建笔记成功: {doc.get('title')} (ID: {doc.get('docGuid')[:10]}...)")
                return doc
            else:
                logger.error(f"创建笔记失败: {result.get('returnMessage')}")
                return None
        except Exception as e:
            logger.error(f"创建笔记异常: {e}")
            return None
    
    def update_note(self, doc_guid: str, title: str, html: str, category: str = "/My Notes/") -> Optional[Dict]:
        """
        更新笔记
        
        Args:
            doc_guid: 文档 GUID
            title: 笔记标题
            html: HTML 内容
            category: 分类路径
            
        Returns:
            Optional[Dict]: 更新结果
        """
        url = f"{self.endpoint}/ks/note/save/{self.kb_guid}/{doc_guid}"
        params = {
            "infoOnly": "",
            "clientType": "web",
            "clientVersion": "4.0",
            "lang": "zh-cn"
        }
        
        data = {
            "category": category,
            "docGuid": doc_guid,
            "kbGuid": self.kb_guid,
            "title": title,
            "html": html,
            "resources": []
        }
        
        try:
            response = self.session.put(
                url,
                params=params,
                json=data,
                headers={
                    "X-Wiz-Token": self.token,
                    "Content-Type": "application/json"
                },
                timeout=10
            )
            result = response.json()
            
            if result.get('returnCode') == 200:
                note = result.get('result', {})
                logger.info(f"✅ 更新笔记成功: {note.get('title')}")
                return note
            else:
                logger.error(f"更新笔记失败: {result.get('returnMessage')}")
                return None
        except Exception as e:
            logger.error(f"更新笔记异常: {e}")
            return None
    
    def get_user_info(self) -> Optional[Dict]:
        """
        获取用户信息
        
        Returns:
            Optional[Dict]: 用户信息
        """
        url = f"{self.endpoint}/wizas/a/users/get_info"
        params = {"token": self.token}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('returnCode') == 200:
                user = data.get('result')
                logger.info(f"✅ 获取用户信息成功: {user.get('displayName')}")
                return user
            else:
                logger.error(f"获取用户信息失败: {data.get('returnMessage')}")
                return None
        except Exception as e:
            logger.error(f"获取用户信息异常: {e}")
            return None
    
    def keep_alive(self) -> bool:
        """
        保持登录状态
        
        Returns:
            bool: 是否成功
        """
        url = f"{self.endpoint}/as/user/keep"
        params = {"token": self.token}
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('returnCode') == 200:
                logger.info("✅ 登录状态已保持")
                return True
            else:
                logger.error(f"保持登录失败: {data.get('returnMessage')}")
                return False
        except Exception as e:
            logger.error(f"保持登录异常: {e}")
            return False


def main():
    """测试函数"""
    import json
    
    # 配置
    endpoint = os.getenv('WIZ_ENDPOINT', 'http://192.168.1.121:30802')
    token = os.getenv('WIZ_TOKEN')
    kb_guid = os.getenv('WIZ_KB_GUID')
    
    if not token or not kb_guid:
        print("❌ 缺少环境变量 WIZ_TOKEN 或 WIZ_KB_GUID")
        return
    
    # 创建操作实例
    ops = WizNoteOps(endpoint, token, kb_guid)
    
    # 测试获取目录
    print("\n📁 获取目录列表:")
    categories = ops.list_categories()
    for i, cat in enumerate(categories[:5], 1):
        print(f"  {i}. {cat}")
    
    # 测试获取笔记
    if categories:
        print(f"\n📝 获取 '{categories[0]}' 目录下的笔记:")
        notes = ops.list_notes_by_category(categories[0])
        for i, note in enumerate(notes[:5], 1):
            print(f"  {i}. {note.get('title')} (ID: {note.get('docGuid')[:10]}...)")


if __name__ == '__main__':
    main()
