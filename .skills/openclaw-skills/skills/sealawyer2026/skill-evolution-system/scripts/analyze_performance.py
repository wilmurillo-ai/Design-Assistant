#!/usr/bin/env python3
"""
技能性能分析器
分析技能使用数据，识别瓶颈和改进机会
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict

class PerformanceAnalyzer:
    """分析技能性能并提供优化建议"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.openclaw/workspace/skills/.evolution-data")
        self.data_dir = Path(data_dir)
        self.usage_file = self.data_dir / "usage_stats.json"
        self.feedback_file = self.data_dir / "feedback.json"
        self.analysis_file = self.data_dir / "analysis_results.json"
    
    def analyze_skill(self, skill_name: str) -> Dict[str, Any]:
        """深度分析单个技能"""
        usage_data = self._load_json(self.usage_file)
        feedback_data = self._load_json(self.feedback_file)
        
        if skill_name not in usage_data:
            return {"error": f"未找到技能 '{skill_name}' 的使用数据"}
        
        records = usage_data[skill_name]
        feedback_list = feedback_data.get(skill_name, [])
        
        analysis = {
            "skill_name": skill_name,
            "analysis_time": datetime.now().isoformat(),
            "summary": self._generate_summary(records),
            "bottlenecks": self._identify_bottlenecks(records),
            "improvement_opportunities": self._find_improvements(records, feedback_list),
            "patterns": self._extract_patterns(records),
            "recommendations": []
        }
        
        # 生成具体建议
        analysis["recommendations"] = self._generate_recommendations(analysis)
        
        # 保存分析结果
        self._save_analysis(skill_name, analysis)
        
        return analysis
    
    def analyze_all_skills(self) -> Dict[str, Any]:
        """分析所有技能"""
        usage_data = self._load_json(self.usage_file)
        results = {}
        
        for skill_name in usage_data.keys():
            results[skill_name] = self.analyze_skill(skill_name)
        
        return results
    
    def compare_skills(self, skill_names: List[str]) -> Dict[str, Any]:
        """比较多个技能的表现"""
        comparison = {
            "skills_compared": skill_names,
            "analysis_time": datetime.now().isoformat(),
            "rankings": [],
            "insights": []
        }
        
        stats = []
        for name in skill_names:
            analysis = self.analyze_skill(name)
            if "error" not in analysis:
                stats.append({
                    "name": name,
                    "score": self._calculate_health_score(analysis),
                    "usage": analysis["summary"]["total_usage"],
                    "success_rate": analysis["summary"]["success_rate"]
                })
        
        # 排序
        stats.sort(key=lambda x: x["score"], reverse=True)
        comparison["rankings"] = stats
        
        # 生成洞察
        if len(stats) >= 2:
            best = stats[0]
            worst = stats[-1]
            comparison["insights"].append(
                f"'{best['name']}' 表现最佳 (健康度: {best['score']:.1f})，"
                f"而 '{worst['name']}' 需要关注 (健康度: {worst['score']:.1f})"
            )
        
        return comparison
    
    def _generate_summary(self, records: List[Dict]) -> Dict[str, Any]:
        """生成使用摘要"""
        if not records:
            return {"total_usage": 0, "success_rate": 0}
        
        completed = [r for r in records if r["metrics"].get("success") is not None]
        
        total = len(completed)
        successful = sum(1 for r in completed if r["metrics"]["success"])
        
        durations = [
            r["metrics"]["duration"] 
            for r in completed 
            if "duration" in r["metrics"]
        ]
        
        satisfaction = [
            r["metrics"]["user_satisfaction"]
            for r in completed
            if r["metrics"].get("user_satisfaction") is not None
        ]
        
        return {
            "total_usage": len(records),
            "completed_tasks": total,
            "success_rate": round(successful / total, 3) if total > 0 else 0,
            "avg_duration": round(sum(durations) / len(durations), 2) if durations else 0,
            "avg_satisfaction": round(sum(satisfaction) / len(satisfaction), 2) if satisfaction else None,
            "time_range": {
                "first": records[0]["timestamp"] if records else None,
                "last": records[-1]["timestamp"] if records else None
            }
        }
    
    def _identify_bottlenecks(self, records: List[Dict]) -> List[Dict[str, Any]]:
        """识别性能瓶颈"""
        bottlenecks = []
        
        completed = [r for r in records if r["metrics"].get("success") is not None]
        if len(completed) < 5:
            return bottlenecks
        
        # 检查失败率
        failures = [r for r in completed if not r["metrics"]["success"]]
        failure_rate = len(failures) / len(completed)
        
        if failure_rate > 0.2:
            bottlenecks.append({
                "type": "high_failure_rate",
                "severity": "high" if failure_rate > 0.4 else "medium",
                "description": f"失败率达到 {failure_rate:.1%}，高于20%警戒线",
                "affected_tasks": len(failures)
            })
        
        # 检查响应时间
        durations = [r["metrics"]["duration"] for r in completed if "duration" in r["metrics"]]
        if durations:
            avg_duration = sum(durations) / len(durations)
            if avg_duration > 30:  # 超过30秒
                bottlenecks.append({
                    "type": "slow_response",
                    "severity": "high" if avg_duration > 60 else "medium",
                    "description": f"平均响应时间 {avg_duration:.1f} 秒，需要优化",
                    "avg_duration": avg_duration
                })
        
        # 检查满意度
        satisfaction_scores = [
            r["metrics"]["user_satisfaction"]
            for r in completed
            if r["metrics"].get("user_satisfaction") is not None
        ]
        if satisfaction_scores:
            avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores)
            if avg_satisfaction < 3.5:
                bottlenecks.append({
                    "type": "low_satisfaction",
                    "severity": "high" if avg_satisfaction < 2.5 else "medium",
                    "description": f"平均满意度 {avg_satisfaction:.1f}/5，用户体验需要提升",
                    "avg_satisfaction": avg_satisfaction
                })
        
        return bottlenecks
    
    def _find_improvements(self, records: List[Dict], feedback_list: List[Dict]) -> List[Dict[str, Any]]:
        """发现改进机会"""
        opportunities = []
        
        # 分析反馈中的关键词
        if feedback_list:
            suggestion_feedback = [f for f in feedback_list if f["type"] == "suggestion"]
            improvement_feedback = [f for f in feedback_list if f["type"] == "improvement"]
            
            if suggestion_feedback:
                opportunities.append({
                    "type": "user_suggestions",
                    "count": len(suggestion_feedback),
                    "description": f"有 {len(suggestion_feedback)} 条用户建议待实现",
                    "priority": "high" if len(suggestion_feedback) > 3 else "medium"
                })
        
        # 检查使用频率趋势
        if len(records) >= 20:
            recent = records[-10:]
            older = records[-20:-10]
            
            recent_success = sum(1 for r in recent if r["metrics"].get("success")) / len(recent)
            older_success = sum(1 for r in older if r["metrics"].get("success")) / len(older)
            
            if recent_success < older_success:
                opportunities.append({
                    "type": "declining_performance",
                    "description": f"近期成功率 ({recent_success:.1%}) 低于前期 ({older_success:.1%})",
                    "priority": "high"
                })
        
        return opportunities
    
    def _extract_patterns(self, records: List[Dict]) -> Dict[str, Any]:
        """提取使用模式"""
        patterns = {
            "peak_usage_hours": [],
            "common_contexts": [],
            "task_complexity_distribution": {"simple": 0, "medium": 0, "complex": 0}
        }
        
        # 分析使用高峰时段
        hour_counts = defaultdict(int)
        for r in records:
            hour = datetime.fromisoformat(r["timestamp"]).hour
            hour_counts[hour] += 1
        
        peak_hours = sorted(hour_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        patterns["peak_usage_hours"] = [h[0] for h in peak_hours]
        
        return patterns
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[Dict[str, str]]:
        """生成优化建议"""
        recommendations = []
        
        for bottleneck in analysis.get("bottlenecks", []):
            if bottleneck["type"] == "high_failure_rate":
                recommendations.append({
                    "category": "可靠性",
                    "action": "审查失败任务，添加错误处理和边界情况处理",
                    "priority": "urgent"
                })
            elif bottleneck["type"] == "slow_response":
                recommendations.append({
                    "category": "性能",
                    "action": "优化脚本执行效率，考虑添加缓存机制",
                    "priority": "high"
                })
            elif bottleneck["type"] == "low_satisfaction":
                recommendations.append({
                    "category": "用户体验",
                    "action": "收集更多用户反馈，改进交互流程",
                    "priority": "high"
                })
        
        for opp in analysis.get("improvement_opportunities", []):
            if opp["type"] == "user_suggestions":
                recommendations.append({
                    "category": "功能增强",
                    "action": "实现用户建议的功能点",
                    "priority": opp["priority"]
                })
        
        # 通用建议
        summary = analysis.get("summary", {})
        if summary.get("total_usage", 0) > 100 and not recommendations:
            recommendations.append({
                "category": "维护",
                "action": "技能运行良好，建议定期代码审查和文档更新",
                "priority": "low"
            })
        
        return recommendations
    
    def _calculate_health_score(self, analysis: Dict[str, Any]) -> float:
        """计算技能健康度评分 (0-100)"""
        score = 100.0
        
        summary = analysis.get("summary", {})
        bottlenecks = analysis.get("bottlenecks", [])
        
        # 成功率影响
        success_rate = summary.get("success_rate", 1.0)
        score -= (1 - success_rate) * 30
        
        # 满意度影响
        satisfaction = summary.get("avg_satisfaction")
        if satisfaction is not None:
            score -= (5 - satisfaction) * 5
        
        # 瓶颈扣分
        for b in bottlenecks:
            if b["severity"] == "high":
                score -= 15
            elif b["severity"] == "medium":
                score -= 8
        
        return max(0, min(100, score))
    
    def _save_analysis(self, skill_name: str, analysis: Dict[str, Any]):
        """保存分析结果"""
        all_analysis = self._load_json(self.analysis_file)
        all_analysis[skill_name] = analysis
        self._save_json(self.analysis_file, all_analysis)
    
    def _load_json(self, file_path: Path) -> Dict:
        """加载JSON文件"""
        if not file_path.exists():
            return {}
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_json(self, file_path: Path, data: Dict):
        """保存JSON文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import sys
    
    analyzer = PerformanceAnalyzer()
    
    if len(sys.argv) < 2:
        print("用法: python analyze_performance.py <command> [args]")
        print("命令: analyze <skill>, analyze-all, compare <skill1> <skill2> ...")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "analyze" and len(sys.argv) >= 3:
        result = analyzer.analyze_skill(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == "analyze-all":
        results = analyzer.analyze_all_skills()
        print(json.dumps(results, indent=2, ensure_ascii=False))
    
    elif cmd == "compare" and len(sys.argv) >= 4:
        result = analyzer.compare_skills(sys.argv[2:])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"未知命令: {cmd}")
