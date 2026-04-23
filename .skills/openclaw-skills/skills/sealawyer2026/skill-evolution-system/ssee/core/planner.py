#!/usr/bin/env python3
"""
进化规划器 - 生成技能进化计划
"""

import json
from pathlib import Path
from typing import Dict, Any


class EvolutionPlanner:
    """技能进化规划器"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.plans_file = self.data_dir / "evolution_plans.json"
        self._plans: Dict[str, Dict] = {}
    
    def initialize(self):
        """初始化规划器"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_plans()
    
    def generate(self, skill_id: str, analysis_result: Dict) -> Dict:
        """生成进化计划"""
        health_score = analysis_result.get("summary", {}).get("health_score", 0)
        bottlenecks = analysis_result.get("bottlenecks", [])
        recommendations = analysis_result.get("recommendations", [])
        
        # 确定进化优先级
        if health_score < 50:
            priority = "critical"
        elif health_score < 70:
            priority = "high"
        elif health_score < 85:
            priority = "medium"
        else:
            priority = "low"
        
        # 生成优化任务
        tasks = []
        for rec in recommendations:
            tasks.append({
                "id": f"{skill_id}_task_{len(tasks)+1}",
                "description": rec,
                "priority": priority,
                "status": "pending",
            })
        
        # 如果没有明显问题，添加持续优化任务
        if not tasks:
            tasks.append({
                "id": f"{skill_id}_task_1",
                "description": "持续监控和微调",
                "priority": "low",
                "status": "pending",
            })
        
        plan = {
            "skill_id": skill_id,
            "version": "auto-generated",
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "priority": priority,
            "health_score_current": health_score,
            "health_score_target": min(health_score + 15, 95),
            "tasks": tasks,
            "estimated_effort": len(tasks) * 2,  # 小时
        }
        
        self._plans[skill_id] = plan
        self._save_plans()
        
        return plan
    
    def _load_plans(self):
        """加载计划"""
        if self.plans_file.exists():
            with open(self.plans_file, 'r') as f:
                self._plans = json.load(f)
    
    def _save_plans(self):
        """保存计划"""
        with open(self.plans_file, 'w') as f:
            json.dump(self._plans, f, indent=2)
