#!/usr/bin/env python3
"""
性能分析器 - 分析技能性能瓶颈
"""

import json
import statistics
from pathlib import Path
from typing import Dict, Any, List


class PerformanceAnalyzer:
    """技能性能分析器"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.results_file = self.data_dir / "analysis_results.json"
        self._results: Dict[str, Dict] = {}
    
    def initialize(self):
        """初始化分析器"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self._load_results()
    
    def analyze(self, skill_id: str, tracking_data: List[Dict]) -> Dict:
        """分析技能性能"""
        if not tracking_data:
            return {"status": "no_data", "skill_id": skill_id}
        
        # 计算基础指标
        total_calls = len(tracking_data)
        durations = [r["metrics"].get("duration", 0) for r in tracking_data if "duration" in r.get("metrics", {})]
        success_count = sum(1 for r in tracking_data if r["metrics"].get("success", False))
        
        # 计算统计数据
        avg_duration = statistics.mean(durations) if durations else 0
        max_duration = max(durations) if durations else 0
        min_duration = min(durations) if durations else 0
        success_rate = (success_count / total_calls) * 100 if total_calls > 0 else 0
        
        # 健康度评分 (0-100)
        health_score = self._calculate_health_score(success_rate, avg_duration)
        
        # 识别瓶颈
        bottlenecks = self._identify_bottlenecks(tracking_data)
        
        result = {
            "skill_id": skill_id,
            "status": "analyzed",
            "timestamp": __import__('datetime').datetime.now().isoformat(),
            "summary": {
                "total_calls": total_calls,
                "success_rate": round(success_rate, 2),
                "avg_duration": round(avg_duration, 3),
                "max_duration": round(max_duration, 3),
                "min_duration": round(min_duration, 3),
                "health_score": round(health_score, 1),
            },
            "bottlenecks": bottlenecks,
            "recommendations": self._generate_recommendations(bottlenecks, health_score),
        }
        
        self._results[skill_id] = result
        self._save_results()
        
        return result
    
    def _calculate_health_score(self, success_rate: float, avg_duration: float) -> float:
        """计算健康度评分"""
        # 成功率权重 60%，性能权重 40%
        success_score = min(success_rate, 100) * 0.6
        
        # 性能评分（假设目标<1秒为满分）
        performance_score = max(0, 100 - avg_duration * 10) * 0.4
        
        return success_score + performance_score
    
    def _identify_bottlenecks(self, tracking_data: List[Dict]) -> List[Dict]:
        """识别性能瓶颈"""
        bottlenecks = []
        
        durations = [r["metrics"].get("duration", 0) for r in tracking_data if "duration" in r.get("metrics", {})]
        if durations:
            avg = statistics.mean(durations)
            slow_calls = [d for d in durations if d > avg * 2]
            if len(slow_calls) > len(durations) * 0.1:
                bottlenecks.append({
                    "type": "performance",
                    "severity": "medium",
                    "description": f"{len(slow_calls)} 次调用超过平均时长2倍",
                })
        
        return bottlenecks
    
    def _generate_recommendations(self, bottlenecks: List[Dict], health_score: float) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if health_score < 60:
            recommendations.append("健康度较低，建议进行全面优化")
        
        for b in bottlenecks:
            if b["type"] == "performance":
                recommendations.append("优化响应时间，考虑缓存或异步处理")
        
        return recommendations
    
    def _load_results(self):
        """加载分析结果"""
        if self.results_file.exists():
            with open(self.results_file, 'r') as f:
                self._results = json.load(f)
    
    def _save_results(self):
        """保存分析结果"""
        with open(self.results_file, 'w') as f:
            json.dump(self._results, f, indent=2)
