#!/usr/bin/env python3
"""
飞书平台适配器

对接飞书开放平台
"""

import json
import time
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Optional
from .base import SkillAdapter, AdapterRegistry


class FeishuAdapter(SkillAdapter):
    """
    飞书平台适配器
    
    对接飞书机器人和应用
    """
    
    BASE_URL = "https://open.feishu.cn/open-apis"
    
    def __init__(self, config: Dict = None):
        super().__init__("feishu", config)
        self.app_id = config.get("app_id", "")
        self.app_secret = config.get("app_secret", "")
        self.tenant_access_token: Optional[str] = None
        self.token_expire_time: float = 0
    
    def connect(self) -> bool:
        """连接到飞书开放平台"""
        if not self.app_id or not self.app_secret:
            return False
        
        try:
            self.tenant_access_token = self._get_tenant_access_token()
            if self.tenant_access_token:
                self._connected = True
                return True
        except Exception as e:
            print(f"飞书连接失败: {e}")
        
        return False
    
    def _get_tenant_access_token(self) -> Optional[str]:
        """获取飞书 tenant_access_token"""
        url = f"{self.BASE_URL}/auth/v3/tenant_access_token/internal"
        data = {
            "app_id": self.app_id,
            "app_secret": self.app_secret,
        }
        
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                if result.get("code") == 0:
                    self.token_expire_time = time.time() + result.get("expire", 7200)
                    return result.get("tenant_access_token")
                else:
                    print(f"获取token失败: {result.get('msg')}")
        except Exception as e:
            print(f"请求token失败: {e}")
        
        return None
    
    def _ensure_token_valid(self):
        """确保token有效"""
        if time.time() >= self.token_expire_time - 60:
            self.tenant_access_token = self._get_tenant_access_token()
    
    def _api_call(self, endpoint: str, data: Dict = None, method: str = "GET") -> Dict:
        """调用飞书API"""
        self._ensure_token_valid()
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            headers = {
                'Authorization': f'Bearer {self.tenant_access_token}',
                'Content-Type': 'application/json',
            }
            
            if method == "POST" and data:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(data).encode('utf-8'),
                    headers=headers,
                    method='POST'
                )
            else:
                req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            return {"error": str(e)}
    
    def get_skill_list(self) -> List[Dict]:
        """获取飞书技能列表"""
        # 获取应用列表
        result = self._api_call("/application/v3/apps/list")
        
        if result.get("code") == 0:
            apps = result.get("data", {}).get("apps", [])
            return [
                {
                    "id": app.get("app_id"),
                    "name": app.get("name"),
                    "platform": "feishu",
                    "desc": app.get("description"),
                }
                for app in apps
            ]
        
        return []
    
    def get_skill_metadata(self, skill_id: str) -> Dict:
        """获取技能元数据"""
        result = self._api_call(f"/application/v3/apps/{skill_id}")
        
        if result.get("code") == 0:
            app = result.get("data", {})
            return {
                "id": skill_id,
                "platform": "feishu",
                "name": app.get("name"),
                "desc": app.get("description"),
            }
        
        return {
            "id": skill_id,
            "platform": "feishu",
        }
    
    def track_skill_usage(self, skill_id: str, metrics: Dict) -> Dict:
        """追踪技能使用"""
        return {
            "status": "tracked",
            "skill": skill_id,
            "platform": self.platform_name,
            "metrics": metrics,
        }
    
    def update_skill(self, skill_id: str, updates: Dict) -> bool:
        """更新技能"""
        return True


# 注册适配器
AdapterRegistry.register("feishu", FeishuAdapter)
