#!/usr/bin/env python3
"""
技能进化报告生成器
生成技能使用、分析、进化的综合报告
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

class EvolutionReportGenerator:
    """生成技能进化综合报告"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.expanduser("~/.openclaw/workspace/skills/.evolution-data")
        self.data_dir = Path(data_dir)
        self.usage_file = self.data_dir / "usage_stats.json"
        self.analysis_file = self.data_dir / "analysis_results.json"
        self.plan_file = self.data_dir / "evolution_plans.json"
    
    def generate_full_report(self) -> str:
        """生成完整报告"""
        usage_data = self._load_json(self.usage_file)
        analysis_data = self._load_json(self.analysis_file)
        plan_data = self._load_json(self.plan_file)
        
        report_lines = [
            "# 🧬 技能进化系统报告",
            f"",
            f"**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
            f"**报告周期**: 最近30天",
            f"",
            "---",
            f"",
        ]
        
        # 概览
        report_lines.extend(self._generate_overview(usage_data, analysis_data))
        
        # 详细分析
        report_lines.extend(self._generate_detailed_analysis(analysis_data))
        
        # 进化计划
        report_lines.extend(self._generate_evolution_plans(plan_data))
        
        # 建议
        report_lines.extend(self._generate_recommendations(analysis_data))
        
        return '\n'.join(report_lines)
    
    def generate_skill_report(self, skill_name: str) -> str:
        """生成单个技能的详细报告"""
        usage_data = self._load_json(self.usage_file)
        analysis_data = self._load_json(self.analysis_file)
        plan_data = self._load_json(self.plan_file)
        
        if skill_name not in usage_data:
            return f"# 错误\n\n未找到技能 '{skill_name}' 的数据"
        
        report_lines = [
            f"# 📊 技能报告: {skill_name}",
            f"",
            f"**生成时间**: {datetime.now().strftime('%Y年%m月%d日 %H:%M')}",
            f"",
            "---",
            f"",
        ]
        
        # 使用统计
        stats = self._get_skill_stats(skill_name, usage_data)
        report_lines.extend([
            "## 📈 使用统计",
            f"",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 总使用次数 | {stats.get('total_usage', 0)} |",
            f"| 成功率 | {stats.get('success_rate', 0):.1%} |",
            f"| 平均响应时间 | {stats.get('avg_duration', 0):.2f} 秒 |",
            f"| 用户满意度 | {stats.get('avg_satisfaction', 'N/A')} |",
            f"| 趋势 | {stats.get('recent_trend', 'unknown')} |",
            f"",
        ])
        
        # 分析结果
        if skill_name in analysis_data:
            analysis = analysis_data[skill_name]
            report_lines.extend([
                "## 🔍 性能分析",
                f"",
            ])
            
            bottlenecks = analysis.get("bottlenecks", [])
            if bottlenecks:
                report_lines.append("### ⚠️ 发现的问题")
                report_lines.append("")
                for b in bottlenecks:
                    emoji = "🔴" if b["severity"] == "high" else "🟡"
                    report_lines.append(f"- {emoji} **{b['type']}**: {b['description']}")
                report_lines.append("")
            else:
                report_lines.extend([
                    "✅ 未发现明显问题",
                    f"",
                ])
        
        # 进化计划
        if skill_name in plan_data:
            plan = plan_data[skill_name]
            report_lines.extend([
                "## 🚀 进化计划",
                f"",
                f"**目标版本**: {plan.get('version', 'N/A')}",
                f"**预计工作量**: {plan.get('estimated_effort', 'N/A')}",
                f"",
                "### 阶段规划",
                f"",
            ])
            
            for i, phase in enumerate(plan.get("phases", []), 1):
                priority_emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}
                emoji = priority_emoji.get(phase.get("priority"), "⚪")
                report_lines.append(f"{i}. {emoji} **{phase['name']}** ({phase.get('estimated_days', 1)}天)")
            
            report_lines.append("")
        
        return '\n'.join(report_lines)
    
    def _generate_overview(self, usage_data: Dict, analysis_data: Dict) -> List[str]:
        """生成概览部分"""
        total_skills = len(usage_data)
        total_usage = sum(len(records) for records in usage_data.values())
        
        healthy_skills = 0
        at_risk_skills = 0
        
        for skill_name, analysis in analysis_data.items():
            bottlenecks = analysis.get("bottlenecks", [])
            if any(b["severity"] == "high" for b in bottlenecks):
                at_risk_skills += 1
            else:
                healthy_skills += 1
        
        return [
            "## 📊 概览",
            f"",
            f"| 指标 | 数值 |",
            f"|------|------|",
            f"| 技能总数 | {total_skills} |",
            f"| 总使用次数 | {total_usage} |",
            f"| 健康技能 | {healthy_skills} ✅ |",
            f"| 需关注技能 | {at_risk_skills} ⚠️ |",
            f"",
            "---",
            f"",
        ]
    
    def _generate_detailed_analysis(self, analysis_data: Dict) -> List[str]:
        """生成详细分析部分"""
        lines = [
            "## 🔍 详细分析",
            f"",
        ]
        
        if not analysis_data:
            lines.extend([
                "暂无分析数据。请运行分析脚本生成。",
                f"",
            ])
            return lines
        
        # 排序：有问题的排在前面
        sorted_skills = sorted(
            analysis_data.items(),
            key=lambda x: len([b for b in x[1].get("bottlenecks", []) if b["severity"] == "high"]),
            reverse=True
        )
        
        for skill_name, analysis in sorted_skills:
            summary = analysis.get("summary", {})
            bottlenecks = analysis.get("bottlenecks", [])
            
            status_emoji = "✅" if not bottlenecks else ("🔴" if any(b["severity"] == "high" for b in bottlenecks) else "🟡")
            
            lines.extend([
                f"### {status_emoji} {skill_name}",
                f"",
                f"- **使用次数**: {summary.get('total_usage', 0)}",
                f"- **成功率**: {summary.get('success_rate', 0):.1%}",
            ])
            
            if summary.get("avg_satisfaction"):
                lines.append(f"- **满意度**: {summary['avg_satisfaction']:.1f}/5")
            
            if bottlenecks:
                lines.append(f"- **问题**: {len(bottlenecks)} 项")
                for b in bottlenecks[:2]:  # 只显示前2个问题
                    lines.append(f"  - {b['description']}")
            
            lines.append("")
        
        lines.extend([
            "---",
            f"",
        ])
        
        return lines
    
    def _generate_evolution_plans(self, plan_data: Dict) -> List[str]:
        """生成进化计划部分"""
        lines = [
            "## 🚀 进化计划",
            f"",
        ]
        
        if not plan_data:
            lines.extend([
                "暂无进化计划。请运行计划生成脚本。",
                f"",
            ])
            return lines
        
        for skill_name, plan in plan_data.items():
            lines.extend([
                f"### {skill_name}",
                f"",
                f"- **目标版本**: {plan.get('version', 'N/A')}",
                f"- **预计工作量**: {plan.get('estimated_effort', 'N/A')}",
                f"- **阶段数**: {len(plan.get('phases', []))}",
                f"",
            ])
        
        lines.extend([
            "---",
            f"",
        ])
        
        return lines
    
    def _generate_recommendations(self, analysis_data: Dict) -> List[str]:
        """生成建议部分"""
        lines = [
            "## 💡 行动建议",
            f"",
        ]
        
        # 找出需要紧急关注的技能
        urgent_skills = []
        for skill_name, analysis in analysis_data.items():
            if any(b["severity"] == "high" for b in analysis.get("bottlenecks", [])):
                urgent_skills.append(skill_name)
        
        if urgent_skills:
            lines.extend([
                "### 🔴 紧急处理",
                f"",
                "以下技能需要立即关注：",
                f"",
            ])
            for skill in urgent_skills:
                lines.append(f"- **{skill}** - 存在严重问题")
            lines.append("")
        
        lines.extend([
            "### 📋 后续步骤",
            f"",
            "1. **立即行动**: 修复标记为紧急的技能问题",
            "2. **本周计划**: 执行高优先级进化阶段",
            "3. **持续监控**: 定期运行分析报告，追踪改进效果",
            "4. **反馈收集**: 鼓励用户提供使用反馈",
            f"",
            "---",
            f"",
            "*报告由技能进化系统自动生成*",
        ])
        
        return lines
    
    def _get_skill_stats(self, skill_name: str, usage_data: Dict) -> Dict:
        """获取技能统计"""
        if skill_name not in usage_data:
            return {}
        
        records = usage_data[skill_name]
        completed = [r for r in records if r["metrics"].get("success") is not None]
        
        if not completed:
            return {"total_usage": len(records), "success_rate": 0}
        
        successful = sum(1 for r in completed if r["metrics"]["success"])
        durations = [r["metrics"]["duration"] for r in completed if "duration" in r["metrics"]]
        satisfaction = [r["metrics"]["user_satisfaction"] for r in completed if r["metrics"].get("user_satisfaction") is not None]
        
        return {
            "total_usage": len(records),
            "success_rate": successful / len(completed) if completed else 0,
            "avg_duration": sum(durations) / len(durations) if durations else 0,
            "avg_satisfaction": sum(satisfaction) / len(satisfaction) if satisfaction else None,
            "recent_trend": self._calculate_trend(completed)
        }
    
    def _calculate_trend(self, records: List[Dict]) -> str:
        """计算趋势"""
        if len(records) < 10:
            return "数据不足"
        
        mid = len(records) // 2
        first_half = sum(1 for r in records[:mid] if r["metrics"].get("success")) / mid
        second_half = sum(1 for r in records[mid:] if r["metrics"].get("success")) / (len(records) - mid)
        
        if second_half > first_half + 0.1:
            return "↗️ 改善中"
        elif second_half < first_half - 0.1:
            return "↘️ 下降中"
        return "➡️ 稳定"
    
    def _load_json(self, file_path: Path) -> Dict:
        """加载JSON文件"""
        if not file_path.exists():
            return {}
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)


if __name__ == "__main__":
    import sys
    
    generator = EvolutionReportGenerator()
    
    if len(sys.argv) < 2:
        # 生成完整报告
        report = generator.generate_full_report()
        print(report)
    
    elif sys.argv[1] == "skill" and len(sys.argv) >= 3:
        # 生成单个技能报告
        report = generator.generate_skill_report(sys.argv[2])
        print(report)
    
    else:
        print(f"用法: python generate_report.py [skill <skill_name>]")
