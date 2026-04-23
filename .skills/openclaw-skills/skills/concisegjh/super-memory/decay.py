"""
decay.py - 记忆衰减管理器
基于重要度 × 时间的自动衰减、压缩、清理
"""

import time
import json
import os
from datetime import datetime


class MemoryDecay:
    """
    记忆衰减策略：

    高优先 (high):    永不自动衰减，人工审查
    中优先 (medium):  90天后衰减为摘要，180天后归档
    低优先 (low):     7天衰减，30天压缩为摘要，90天归档
    """

    # 衰减策略配置
    POLICIES = {
        "high": {
            "review_days": 0,       # 不自动审查
            "decay_days": 0,        # 不衰减
            "archive_days": 0,      # 不自动归档
        },
        "medium": {
            "review_days": 90,      # 90天后标记待审查
            "decay_days": 180,      # 180天后衰减为摘要
            "archive_days": 365,    # 365天后归档
        },
        "low": {
            "review_days": 7,       # 7天后标记待审查
            "decay_days": 30,       # 30天后衰减为摘要
            "archive_days": 90,     # 90天后归档
        },
    }

    def __init__(self, store, encoder=None):
        self.store = store
        self.encoder = encoder

    def compute_decay_score(self, memory: dict) -> dict:
        """
        计算单条记忆的衰减分数。

        返回: {
            "memory_id": str,
            "importance": str,
            "age_days": int,
            "decay_score": float,      # 0.0 ~ 1.0，1.0=完全新鲜
            "status": str,             # fresh / aging / review / decay / archive
            "next_action": str,        # 无 / 标记审查 / 压缩摘要 / 归档
        }
        """
        now = time.time()
        time_ts = memory.get("time_ts", now)
        age_seconds = now - time_ts
        age_days = age_seconds / 86400

        importance = memory.get("importance", "medium")
        policy = self.POLICIES.get(importance, self.POLICIES["medium"])

        # 计算衰减分数
        if policy["decay_days"] == 0:
            # high priority: 不衰减
            decay_score = 1.0
        else:
            # 线性衰减: 从 1.0 到 0.0
            decay_score = max(0.0, 1.0 - age_days / policy["decay_days"])

        # 判断状态
        if policy["archive_days"] and age_days >= policy["archive_days"]:
            status = "archive"
            next_action = "归档"
        elif policy["decay_days"] and age_days >= policy["decay_days"]:
            status = "decay"
            next_action = "压缩为摘要"
        elif policy["review_days"] and age_days >= policy["review_days"]:
            status = "review"
            next_action = "标记审查"
        else:
            status = "fresh" if age_days < 1 else "aging"
            next_action = "无"

        return {
            "memory_id": memory.get("memory_id", ""),
            "importance": importance,
            "age_days": round(age_days, 1),
            "decay_score": round(decay_score, 4),
            "status": status,
            "next_action": next_action,
        }

    def analyze_all(self, limit: int = 500) -> dict:
        """
        分析所有记忆的衰减状态。

        返回: {
            "total": int,
            "by_status": {"fresh": n, "aging": n, ...},
            "by_importance": {"high": n, "medium": n, "low": n},
            "needs_action": [decay_score dicts],
            "summary": str,
        }
        """
        memories = self.store.query(limit=limit)
        analyses = [self.compute_decay_score(m) for m in memories]

        by_status = {}
        by_importance = {}
        needs_action = []

        for a in analyses:
            by_status[a["status"]] = by_status.get(a["status"], 0) + 1
            by_importance[a["importance"]] = by_importance.get(a["importance"], 0) + 1
            if a["status"] in ("review", "decay", "archive"):
                needs_action.append(a)

        summary_parts = []
        for status, count in sorted(by_status.items()):
            icon = {"fresh": "🟢", "aging": "🟡", "review": "👀", "decay": "📦", "archive": "🗄️"}.get(status, "❓")
            summary_parts.append(f"{icon}{status}={count}")

        return {
            "total": len(analyses),
            "by_status": by_status,
            "by_importance": by_importance,
            "needs_action": needs_action,
            "summary": " | ".join(summary_parts),
        }

    def get_decay_weight(self, memory: dict) -> float:
        """
        获取记忆的衰减权重，用于检索排序。
        返回 0.0 ~ 1.0
        """
        result = self.compute_decay_score(memory)
        return result["decay_score"]

    def apply_decay_to_recall(self, memories: list[dict]) -> list[dict]:
        """
        给检索结果附加衰减权重信息。
        检索排序时可用 _decay_weight 参与综合评分。
        """
        for mem in memories:
            decay = self.compute_decay_score(mem)
            mem["_decay_score"] = decay["decay_score"]
            mem["_decay_status"] = decay["status"]
            mem["_age_days"] = decay["age_days"]
        return memories

    def generate_report(self, output_path: str = None) -> str:
        """
        生成衰减分析报告 Markdown。
        """
        analysis = self.analyze_all()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        lines = [
            "# 📊 记忆衰减分析报告",
            "",
            f"**生成时间**: {now_str}",
            f"**总记忆数**: {analysis['total']}",
            "",
            "## 状态分布",
            "",
        ]

        status_icons = {"fresh": "🟢", "aging": "🟡", "review": "👀", "decay": "📦", "archive": "🗄️"}
        for status in ("fresh", "aging", "review", "decay", "archive"):
            count = analysis["by_status"].get(status, 0)
            if count:
                icon = status_icons.get(status, "❓")
                lines.append(f"- {icon} **{status}**: {count} 条")

        lines.append("")
        lines.append("## 重要度分布")
        lines.append("")
        imp_icons = {"high": "⚡", "medium": "", "low": "🔻"}
        for imp in ("high", "medium", "low"):
            count = analysis["by_importance"].get(imp, 0)
            if count:
                icon = imp_icons.get(imp, "")
                lines.append(f"- {icon} **{imp}**: {count} 条")

        if analysis["needs_action"]:
            lines.append("")
            lines.append("## ⚠️ 需要处理")
            lines.append("")
            lines.append("| 状态 | 重要度 | 天数 | 记忆 ID | 下一步 |")
            lines.append("|------|--------|------|---------|--------|")
            for item in analysis["needs_action"][:20]:
                icon = status_icons.get(item["status"], "")
                lines.append(
                    f"| {icon} {item['status']} | {item['importance']} | {item['age_days']}d | "
                    f"`{item['memory_id'][:20]}...` | {item['next_action']} |"
                )

        lines.append("")
        lines.append(f"**摘要**: {analysis['summary']}")
        lines.append("")
        lines.append("---")
        lines.append("_由 Agent Memory Decay 系统自动生成_")

        report = "\n".join(lines)

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report)

        return report
