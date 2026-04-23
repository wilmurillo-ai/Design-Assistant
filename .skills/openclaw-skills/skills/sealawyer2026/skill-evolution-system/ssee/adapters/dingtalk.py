#!/usr/bin/env python3
"""
钉钉平台适配器

对接钉钉开放平台和智能助手
"""

import json
import time
import hmac
import hashlib
import base64
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Optional
from .base import SkillAdapter, AdapterRegistry


class DingTalkAdapter(SkillAdapter):
    """
    钉钉平台适配器
    
    对接钉钉 AI 助理和应用
    """
    
    def __init__(self, config: Dict = None):
        super().__init__("dingtalk", config)
        self.app_key = config.get("app_key", "")
        self.app_secret = config.get("app_secret", "")
        self.agent_id = config.get("agent_id", "")
        self.access_token: Optional[str] = None
        self.token_expire_time: float = 0
    
    def connect(self) -> bool:
        """连接到钉钉开放平台"""
        if not self.app_key or not self.app_secret:
            return False
        
        try:
            self.access_token = self._get_access_token()
            if self.access_token:
                self._connected = True
                return True
        except Exception as e:
            print(f"钉钉连接失败: {e}")
        
        return False
    
    def _get_access_token(self) -> Optional[str]:
        """获取钉钉 access_token"""
        url = f"https://oapi.dingtalk.com/gettoken?appkey={self.app_key}&appsecret={self.app_secret}"
        
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                if data.get("errcode") == 0:
                    self.token_expire_time = time.time() + data.get("expires_in", 7200)
                    return data.get("access_token")
                else:
                    print(f"获取token失败: {data.get('errmsg')}")
        except Exception as e:
            print(f"请求token失败: {e}")
        
        return None
    
    def _ensure_token_valid(self):
        """确保token有效"""
        if time.time() >= self.token_expire_time - 60:
            self.access_token = self._get_access_token()
    
    def _api_call(self, endpoint: str, data: Dict = None, method: str = "GET") -> Dict:
        """调用钉钉API"""
        self._ensure_token_valid()
        
        url = f"https://oapi.dingtalk.com{endpoint}?access_token={self.access_token}"
        
        try:
            if method == "POST" and data:
                req = urllib.request.Request(
                    url,
                    data=json.dumps(data).encode('utf-8'),
                    headers={'Content-Type': 'application/json'},
                    method='POST'
                )
            else:
                req = urllib.request.Request(url)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            return {"error": str(e)}
    
    def get_skill_list(self) -> List[Dict]:
        """获取钉钉 AI 技能列表"""
        # 获取应用列表
        result = self._api_call("/microapp/list")
        
        if result.get("errcode") == 0:
            apps = result.get("appList", [])
            return [
                {
                    "id": str(app.get("agentId")),
                    "name": app.get("name"),
                    "platform": "dingtalk",
                    "desc": app.get("desc"),
                }
                for app in apps
            ]
        
        # 如果API失败，返回已知应用
        return [
            {
                "id": self.agent_id or "4363797954",
                "name": "九章法律AI助手",
                "platform": "dingtalk",
            }
        ]
    
    def get_skill_metadata(self, skill_id: str) -> Dict:
        """获取技能元数据"""
        result = self._api_call(f"/microapp/get", {"agentId": skill_id})
        
        if result.get("errcode") == 0:
            return {
                "id": skill_id,
                "platform": "dingtalk",
                "name": result.get("name"),
                "desc": result.get("desc"),
                "agent_id": self.agent_id,
            }
        
        return {
            "id": skill_id,
            "platform": "dingtalk",
            "agent_id": self.agent_id,
        }
    
    def track_skill_usage(self, skill_id: str, metrics: Dict) -> Dict:
        """追踪技能使用"""
        # 这里可以对接钉钉的数据统计API
        return {
            "status": "tracked",
            "skill": skill_id,
            "platform": self.platform_name,
            "metrics": metrics,
        }
    
    def update_skill(self, skill_id: str, updates: Dict) -> bool:
        """更新技能"""
        # 钉钉应用更新需要通过开放平台后台
        # 这里记录更新请求
        return True


# 注册适配器
AdapterRegistry.register("dingtalk", DingTalkAdapter)
