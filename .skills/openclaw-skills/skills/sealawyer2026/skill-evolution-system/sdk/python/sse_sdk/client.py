#!/usr/bin/env python3
"""
SSE Python SDK - 客户端实现

提供简单的API接口与SSE服务交互
"""

import json
import time
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .exceptions import SSEError, AuthenticationError, RateLimitError


@dataclass
class SSEConfig:
    """SSE客户端配置"""
    endpoint: str = "http://localhost:8080"
    api_key: str = ""
    timeout: int = 30
    retry_count: int = 3
    retry_delay: float = 1.0


class SSEClient:
    """
    SSE SDK客户端
    
    简化与技能自进化引擎的交互
    """
    
    def __init__(self, api_key: str = None, endpoint: str = None, config: SSEConfig = None):
        """
        初始化SSE客户端
        
        Args:
            api_key: API认证密钥
            endpoint: SSE服务端点
            config: 完整配置对象（可选）
        """
        if config:
            self.config = config
        else:
            self.config = SSEConfig(
                api_key=api_key or "",
                endpoint=endpoint or "http://localhost:8080"
            )
        
        self._version = "2.0.0"
    
    def _request(self, method: str, path: str, data: Dict = None) -> Dict:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法 (GET/POST)
            path: API路径
            data: 请求数据
            
        Returns:
            Dict: 响应数据
            
        Raises:
            AuthenticationError: 认证失败
            RateLimitError: 频率限制
            SSEError: 其他错误
        """
        url = f"{self.config.endpoint}{path}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "X-SSE-Version": self._version,
        }
        
        for attempt in range(self.config.retry_count):
            try:
                if method == "GET":
                    req = urllib.request.Request(url, headers=headers)
                else:  # POST
                    req = urllib.request.Request(
                        url,
                        data=json.dumps(data).encode('utf-8'),
                        headers=headers,
                        method='POST'
                    )
                
                with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                    result = json.loads(response.read().decode('utf-8'))
                    
                    if result.get("status") == "error":
                        error = result.get("error", {})
                        code = error.get("code", "")
                        
                        if code == "SEP_002":
                            raise AuthenticationError(error.get("message"))
                        elif code == "SEP_005":
                            raise RateLimitError(error.get("message"))
                        else:
                            raise SSEError(error.get("message"), code)
                    
                    return result.get("data", {})
                    
            except urllib.error.HTTPError as e:
                if e.code == 401:
                    raise AuthenticationError("Invalid API key")
                elif e.code == 429:
                    raise RateLimitError("Rate limit exceeded")
                elif attempt < self.config.retry_count - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))
                    continue
                else:
                    raise SSEError(f"HTTP {e.code}: {e.reason}")
                    
            except Exception as e:
                if attempt < self.config.retry_count - 1:
                    time.sleep(self.config.retry_delay * (2 ** attempt))
                    continue
                raise SSEError(str(e))
        
        raise SSEError("Max retry exceeded")
    
    def track(self, skill_id: str, metrics: Dict, context: Dict = None) -> Dict:
        """
        追踪技能使用
        
        Args:
            skill_id: 技能标识符
            metrics: 使用指标
            context: 上下文信息（可选）
            
        Returns:
            Dict: 追踪结果
            
        Example:
            >>> client.track("my-skill", {
            ...     "duration_ms": 1500,
            ...     "success": True,
            ...     "satisfaction": 4
            ... })
        """
        payload = {
            "skill_id": skill_id,
            "action": "complete",
            "metrics": metrics,
        }
        if context:
            payload["context"] = context
        
        return self._request("POST", "/v2/track", {
            "version": self._version,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
            "message_id": f"track_{int(time.time() * 1000)}",
            "type": "track",
            "payload": payload,
            "meta": {"source": "python_sdk", "skill_id": skill_id}
        })
    
    def analyze(self, skill_id: str, time_range: str = "30d") -> Dict:
        """
        分析技能性能
        
        Args:
            skill_id: 技能标识符
            time_range: 时间范围 (7d, 30d, 90d)
            
        Returns:
            Dict: 分析结果
        """
        return self._request("GET", f"/v2/analyze/{skill_id}?time_range={time_range}")
    
    def plan(self, skill_id: str, strategy: str = "balanced") -> Dict:
        """
        生成进化计划
        
        Args:
            skill_id: 技能标识符
            strategy: 进化策略 (aggressive, balanced, conservative)
            
        Returns:
            Dict: 进化计划
        """
        return self._request("POST", "/v2/plan", {
            "version": self._version,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
            "message_id": f"plan_{int(time.time() * 1000)}",
            "type": "plan",
            "payload": {
                "skill_id": skill_id,
                "strategy": strategy,
            },
            "meta": {"source": "python_sdk", "skill_id": skill_id}
        })
    
    def evolve(self, skill_id: str, plan_id: str = None, mode: str = "dry_run") -> Dict:
        """
        执行技能进化
        
        Args:
            skill_id: 技能标识符
            plan_id: 进化计划ID（可选）
            mode: 执行模式 (dry_run, auto, manual)
            
        Returns:
            Dict: 进化结果
        """
        payload = {
            "skill_id": skill_id,
            "mode": mode,
        }
        if plan_id:
            payload["plan_id"] = plan_id
        
        return self._request("POST", "/v2/evolve", {
            "version": self._version,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
            "message_id": f"evolve_{int(time.time() * 1000)}",
            "type": "evolve",
            "payload": payload,
            "meta": {"source": "python_sdk", "skill_id": skill_id}
        })
    
    def sync(self, skill_ids: List[str], source_skill: str = None) -> Dict:
        """
        技能间同步
        
        Args:
            skill_ids: 目标技能列表
            source_skill: 源技能（可选，默认自动选择）
            
        Returns:
            Dict: 同步结果
        """
        payload = {
            "target_skills": skill_ids,
            "sync_type": "patterns",
        }
        if source_skill:
            payload["source_skill"] = source_skill
        
        return self._request("POST", "/v2/sync", {
            "version": self._version,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime()),
            "message_id": f"sync_{int(time.time() * 1000)}",
            "type": "sync",
            "payload": payload,
            "meta": {"source": "python_sdk"}
        })
    
    def status(self) -> Dict:
        """
        获取引擎状态
        
        Returns:
            Dict: 引擎状态
        """
        return self._request("GET", "/v2/status")
    
    def get_skills(self) -> List[Dict]:
        """
        获取所有技能列表
        
        Returns:
            List[Dict]: 技能列表
        """
        status = self.status()
        return status.get("skills", {})


def create_client(api_key: str = None, endpoint: str = None) -> SSEClient:
    """
    创建SSE客户端的便捷函数
    
    Args:
        api_key: API密钥
        endpoint: 服务端点
        
    Returns:
        SSEClient: 客户端实例
    """
    return SSEClient(api_key=api_key, endpoint=endpoint)
