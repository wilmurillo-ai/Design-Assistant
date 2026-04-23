#!/usr/bin/env python3
"""
技能进化计划生成器
基于分析结果，生成具体的优化和迭代计划
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

class EvolutionPlanGenerator:
    """生成技能进化计划"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.openclaw/workspace/skills/.evolution-data")
        self.data_dir = Path(data_dir)
        self.analysis_file = self.data_dir / "analysis_results.json"
        self.plan_file = self.data_dir / "evolution_plans.json"
        self.skills_dir = Path(os.path.expanduser("~/.openclaw/workspace/skills"))
    
    def generate_plan(self, skill_name: str) -> Dict[str, Any]:
        """为单个技能生成进化计划"""
        analysis = self._load_analysis(skill_name)
        
        if "error" in analysis:
            return {"error": f"无法生成计划: {analysis['error']}"}
        
        skill_path = self.skills_dir / skill_name
        if not skill_path.exists():
            return {"error": f"技能 '{skill_name}' 不存在"}
        
        plan = {
            "skill_name": skill_name,
            "generated_at": datetime.now().isoformat(),
            "version": self._get_next_version(skill_name),
            "phases": [],
            "estimated_effort": "",
            "expected_impact": {}
        }
        
        # 基于分析结果构建进化阶段
        phases = []
        
        # 阶段1: 紧急修复
        urgent_items = [
            r for r in analysis.get("recommendations", [])
            if r.get("priority") == "urgent"
        ]
        if urgent_items or any(b["severity"] == "high" for b in analysis.get("bottlenecks", [])):
            phases.append(self._create_phase("紧急修复", "critical", urgent_items, analysis.get("bottlenecks", [])))
        
        # 阶段2: 性能优化
        perf_items = [
            r for r in analysis.get("recommendations", [])
            if r.get("category") == "性能"
        ]
        if perf_items:
            phases.append(self._create_phase("性能优化", "high", perf_items))
        
        # 阶段3: 功能增强
        feature_items = [
            r for r in analysis.get("recommendations", [])
            if r.get("category") in ["功能增强", "用户体验"]
        ]
        if feature_items:
            phases.append(self._create_phase("功能增强", "medium", feature_items))
        
        # 阶段4: 文档和测试
        phases.append({
            "name": "文档更新",
            "priority": "low",
            "tasks": [
                "更新SKILL.md以反映最新功能",
                "添加使用示例和最佳实践",
                "更新references文档"
            ],
            "estimated_days": 1
        })
        
        plan["phases"] = phases
        plan["estimated_effort"] = self._estimate_effort(phases)
        plan["expected_impact"] = self._calculate_expected_impact(analysis, phases)
        
        # 保存计划
        self._save_plan(skill_name, plan)
        
        return plan
    
    def generate_batch_plan(self, skill_names: List[str] = None) -> Dict[str, Any]:
        """批量生成进化计划"""
        if skill_names is None:
            # 获取所有技能
            analysis_data = self._load_json(self.analysis_file)
            skill_names = list(analysis_data.keys())
        
        batch_plan = {
            "generated_at": datetime.now().isoformat(),
            "total_skills": len(skill_names),
            "plans": {},
            "execution_order": [],
            "resource_allocation": {}
        }
        
        # 为每个技能生成计划
        for skill_name in skill_names:
            plan = self.generate_plan(skill_name)
            if "error" not in plan:
                batch_plan["plans"][skill_name] = plan
        
        # 确定执行优先级
        batch_plan["execution_order"] = self._prioritize_skills(batch_plan["plans"])
        
        # 资源分配建议
        batch_plan["resource_allocation"] = self._allocate_resources(batch_plan["plans"])
        
        return batch_plan
    
    def _create_phase(self, name: str, priority: str, recommendations: List[Dict], bottlenecks: List[Dict] = None) -> Dict[str, Any]:
        """创建进化阶段"""
        tasks = []
        
        for rec in recommendations:
            tasks.append({
                "description": rec["action"],
                "category": rec.get("category", "general"),
                "priority": rec.get("priority", "medium")
            })
        
        if bottlenecks:
            for b in bottlenecks:
                if b["severity"] == "high" or (priority == "critical" and b["severity"] == "medium"):
                    tasks.append({
                        "description": f"修复问题: {b['description']}",
                        "category": "bugfix",
                        "priority": "urgent" if b["severity"] == "high" else "high"
                    })
        
        # 估算天数
        days = 1
        if priority == "critical":
            days = 2
        elif priority == "high":
            days = 3
        elif priority == "medium":
            days = 5
        
        return {
            "name": name,
            "priority": priority,
            "tasks": tasks,
            "estimated_days": days
        }
    
    def _get_next_version(self, skill_name: str) -> str:
        """获取下一个版本号"""
        skill_path = self.skills_dir / skill_name
        skill_md = skill_path / "SKILL.md"
        
        current_version = "1.0.0"
        
        if skill_md.exists():
            content = skill_md.read_text(encoding='utf-8')
            # 简单解析版本号
            if "version:" in content:
                for line in content.split('\n'):
                    if 'version:' in line and not line.strip().startswith('#'):
                        parts = line.split(':')
                        if len(parts) >= 2:
                            current_version = parts[1].strip().strip('"\'')
                            break
        
        # 递增补丁版本
        try:
            parts = current_version.split('.')
            if len(parts) >= 3:
                parts[2] = str(int(parts[2]) + 1)
            return '.'.join(parts)
        except:
            return "1.0.1"
    
    def _estimate_effort(self, phases: List[Dict]) -> str:
        """估算总体工作量"""
        total_days = sum(p.get("estimated_days", 1) for p in phases)
        
        if total_days <= 2:
            return f"约 {total_days} 天"
        elif total_days <= 5:
            return f"约 {total_days} 天 (1周)"
        elif total_days <= 10:
            return f"约 {total_days} 天 (2周)"
        else:
            return f"约 {total_days} 天 ({total_days // 5} 周)"
    
    def _calculate_expected_impact(self, analysis: Dict, phases: List[Dict]) -> Dict[str, Any]:
        """计算预期影响"""
        summary = analysis.get("summary", {})
        bottlenecks = analysis.get("bottlenecks", [])
        
        impact = {
            "success_rate_improvement": "+5-15%",
            "user_satisfaction_improvement": "+0.5-1.0",
            "performance_improvement": "20-40%"
        }
        
        # 根据当前状态调整预期
        current_success = summary.get("success_rate", 1.0)
        if current_success < 0.8:
            impact["success_rate_improvement"] = "+15-25%"
        elif current_success > 0.95:
            impact["success_rate_improvement"] = "+2-5%"
        
        return impact
    
    def _prioritize_skills(self, plans: Dict[str, Dict]) -> List[str]:
        """确定技能执行优先级"""
        scored_skills = []
        
        for skill_name, plan in plans.items():
            score = 0
            for phase in plan.get("phases", []):
                if phase["priority"] == "critical":
                    score += 100
                elif phase["priority"] == "high":
                    score += 50
                elif phase["priority"] == "medium":
                    score += 20
            scored_skills.append((skill_name, score))
        
        scored_skills.sort(key=lambda x: x[1], reverse=True)
        return [s[0] for s in scored_skills]
    
    def _allocate_resources(self, plans: Dict[str, Dict]) -> Dict[str, Any]:
        """资源分配建议"""
        total_days = 0
        critical_count = 0
        
        for plan in plans.values():
            for phase in plan.get("phases", []):
                total_days += phase.get("estimated_days", 1)
                if phase["priority"] == "critical":
                    critical_count += 1
        
        return {
            "estimated_total_days": total_days,
            "skills_needing_immediate_attention": critical_count,
            "recommended_sprint_size": min(3, len(plans)),
            "suggested_schedule": f"分 {max(1, total_days // 10)} 个迭代周期完成"
        }
    
    def _load_analysis(self, skill_name: str) -> Dict:
        """加载分析结果"""
        data = self._load_json(self.analysis_file)
        return data.get(skill_name, {"error": "未找到分析结果"})
    
    def _save_plan(self, skill_name: str, plan: Dict):
        """保存进化计划"""
        all_plans = self._load_json(self.plan_file)
        all_plans[skill_name] = plan
        self._save_json(self.plan_file, all_plans)
    
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
    
    generator = EvolutionPlanGenerator()
    
    if len(sys.argv) < 2:
        print("用法: python generate_evolution_plan.py <command> [args]")
        print("命令: plan <skill>, batch [skill1 skill2 ...]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "plan" and len(sys.argv) >= 3:
        result = generator.generate_plan(sys.argv[2])
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    elif cmd == "batch":
        skills = sys.argv[2:] if len(sys.argv) > 2 else None
        result = generator.generate_batch_plan(skills)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    
    else:
        print(f"未知命令: {cmd}")
