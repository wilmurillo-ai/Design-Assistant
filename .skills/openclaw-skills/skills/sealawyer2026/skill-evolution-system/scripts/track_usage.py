#!/usr/bin/env python3
"""
技能使用数据追踪器
收集技能使用频率、响应时间、成功率等数据
"""

import json
import os
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

class SkillUsageTracker:
    """追踪技能使用情况的类"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.openclaw/workspace/skills/.evolution-data")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.usage_file = self.data_dir / "usage_stats.json"
        self.feedback_file = self.data_dir / "feedback.json"
        
    def record_usage(self, skill_name: str, context: Dict[str, Any]) -> str:
        """记录一次技能使用"""
        record_id = f"{skill_name}_{int(time.time() * 1000)}"
        
        data = self._load_data(self.usage_file)
        
        record = {
            "id": record_id,
            "skill": skill_name,
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "metrics": {
                "start_time": time.time(),
                "tokens_used": context.get("tokens_used", 0),
                "success": None,  # 待后续更新
                "user_satisfaction": None  # 待后续更新
            }
        }
        
        if skill_name not in data:
            data[skill_name] = []
        data[skill_name].append(record)
        
        # 只保留最近1000条记录
        data[skill_name] = data[skill_name][-1000:]
        
        self._save_data(self.usage_file, data)
        return record_id
    
    def update_result(self, record_id: str, success: bool, satisfaction: int = None):
        """更新使用结果"""
        data = self._load_data(self.usage_file)
        
        for skill_records in data.values():
            for record in skill_records:
                if record.get("id") == record_id:
                    record["metrics"]["success"] = success
                    record["metrics"]["end_time"] = time.time()
                    record["metrics"]["duration"] = record["metrics"]["end_time"] - record["metrics"]["start_time"]
                    if satisfaction is not None:
                        record["metrics"]["user_satisfaction"] = satisfaction
                    break
        
        self._save_data(self.usage_file, data)
    
    def collect_feedback(self, skill_name: str, feedback_type: str, details: str, rating: int = None):
        """收集用户反馈"""
        data = self._load_data(self.feedback_file)
        
        feedback = {
            "skill": skill_name,
            "timestamp": datetime.now().isoformat(),
            "type": feedback_type,  # 'improvement', 'bug', 'praise', 'suggestion'
            "details": details,
            "rating": rating  # 1-5分
        }
        
        if skill_name not in data:
            data[skill_name] = []
        data[skill_name].append(feedback)
        
        self._save_data(self.feedback_file, data)
    
    def get_skill_stats(self, skill_name: str, days: int = 30) -> Dict[str, Any]:
        """获取技能使用统计"""
        data = self._load_data(self.usage_file)
        
        if skill_name not in data:
            return {"total_usage": 0, "success_rate": 0, "avg_duration": 0}
        
        cutoff = datetime.now() - timedelta(days=days)
        records = [
            r for r in data[skill_name]
            if datetime.fromisoformat(r["timestamp"]) > cutoff
            and r["metrics"].get("success") is not None
        ]
        
        if not records:
            return {"total_usage": 0, "success_rate": 0, "avg_duration": 0}
        
        total = len(records)
        successful = sum(1 for r in records if r["metrics"]["success"])
        durations = [r["metrics"].get("duration", 0) for r in records if "duration" in r["metrics"]]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        satisfaction_scores = [
            r["metrics"]["user_satisfaction"] 
            for r in records 
            if r["metrics"].get("user_satisfaction") is not None
        ]
        avg_satisfaction = sum(satisfaction_scores) / len(satisfaction_scores) if satisfaction_scores else None
        
        return {
            "total_usage": total,
            "success_rate": successful / total,
            "avg_duration": round(avg_duration, 2),
            "avg_satisfaction": round(avg_satisfaction, 2) if avg_satisfaction else None,
            "recent_trend": self._calculate_trend(records)
        }
    
    def _calculate_trend(self, records: List[Dict]) -> str:
        """计算使用趋势"""
        if len(records) < 10:
            return "insufficient_data"
        
        # 分成两半比较
        mid = len(records) // 2
        first_half = records[:mid]
        second_half = records[mid:]
        
        first_success = sum(1 for r in first_half if r["metrics"].get("success")) / len(first_half)
        second_success = sum(1 for r in second_half if r["metrics"].get("success")) / len(second_half)
        
        if second_success > first_success + 0.1:
            return "improving"
        elif second_success < first_success - 0.1:
            return "declining"
        return "stable"
    
    def list_all_skills(self) -> List[str]:
        """列出所有追踪过的技能"""
        data = self._load_data(self.usage_file)
        return list(data.keys())
    
    def _load_data(self, file_path: Path) -> Dict:
        """加载JSON数据"""
        if not file_path.exists():
            return {}
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_data(self, file_path: Path, data: Dict):
        """保存JSON数据"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    import sys
    
    tracker = SkillUsageTracker()
    
    if len(sys.argv) < 2:
        print("用法: python track_usage.py <command> [args]")
        print("命令: record, update, feedback, stats, list")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "record" and len(sys.argv) >= 3:
        record_id = tracker.record_usage(sys.argv[2], {})
        print(f"记录ID: {record_id}")
    
    elif cmd == "stats" and len(sys.argv) >= 3:
        stats = tracker.get_skill_stats(sys.argv[2])
        print(json.dumps(stats, indent=2, ensure_ascii=False))
    
    elif cmd == "list":
        skills = tracker.list_all_skills()
        for skill in skills:
            print(skill)
    
    else:
        print(f"未知命令: {cmd}")
