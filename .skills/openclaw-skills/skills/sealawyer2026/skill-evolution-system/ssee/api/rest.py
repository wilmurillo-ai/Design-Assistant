#!/usr/bin/env python3
"""
REST API - 开放接口层

提供HTTP RESTful API供外部调用
"""

from typing import Dict, Any
import json


class RESTAPI:
    """
    SSE REST API
    
    标准化HTTP接口
    """
    
    def __init__(self, kernel):
        self.kernel = kernel
    
    def track(self, skill_id: str, metrics: Dict) -> Dict:
        """POST /v1/track"""
        return self.kernel.track(skill_id, metrics)
    
    def analyze(self, skill_id: str) -> Dict:
        """GET /v1/analyze/{skill_id}"""
        return self.kernel.analyze(skill_id)
    
    def plan(self, skill_id: str) -> Dict:
        """POST /v1/plan"""
        return self.kernel.plan(skill_id)
    
    def evolve(self, skill_id: str, plan: Dict = None) -> Dict:
        """POST /v1/evolve"""
        return self.kernel.evolve(skill_id, plan)
    
    def sync(self, skill_ids: list) -> Dict:
        """POST /v1/sync"""
        return self.kernel.sync_skills(skill_ids)
    
    def status(self) -> Dict:
        """GET /v1/status"""
        return self.kernel.get_status()


# Flask/FastAPI 路由示例
def create_routes(app, api: RESTAPI):
    """创建API路由"""
    
    @app.post("/v1/track")
    def track(skill_id: str, metrics: Dict):
        return api.track(skill_id, metrics)
    
    @app.get("/v1/analyze/{skill_id}")
    def analyze(skill_id: str):
        return api.analyze(skill_id)
    
    @app.post("/v1/plan")
    def plan(skill_id: str):
        return api.plan(skill_id)
    
    @app.post("/v1/evolve")
    def evolve(skill_id: str, plan: Dict = None):
        return api.evolve(skill_id, plan)
    
    @app.post("/v1/sync")
    def sync(skill_ids: list):
        return api.sync(skill_ids)
    
    @app.get("/v1/status")
    def status():
        return api.status()
