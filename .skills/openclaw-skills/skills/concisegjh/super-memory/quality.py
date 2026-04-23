"""
quality.py - 记忆质量评分系统
追踪记忆的有用性，反向优化检索排序
"""

import time
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class MemoryQuality:
    """
    记忆质量评估：

    1. 显式反馈 — 用户标记"有用/没用"
    2. 隐式信号 — 被检索次数、被引用次数
    3. 衰减修正 — 质量高的记忆延缓衰减
    4. 冷启动 — 基于规则的初始评分

    质量分数：0.0（无用）~ 1.0（极高价值）
    """

    # 隐式信号权重
    WEIGHTS = {
        "retrieval_count": 0.15,    # 被检索次数
        "reference_count": 0.20,    # 被其他记忆引用次数
        "age_bonus": 0.10,          # 存活时间越长价值越高（适度）
        "explicit_feedback": 0.40,  # 用户显式反馈
        "content_quality": 0.15,    # 内容质量启发式
    }

    def __init__(self, store, stats_path: str = None):
        self.store = store
        self._stats_path = Path(stats_path) if stats_path else Path(__file__).parent / "quality_stats.json"
        self._stats = self._load_stats()

    def _load_stats(self) -> dict:
        """加载质量统计数据"""
        if self._stats_path.exists():
            try:
                with open(self._stats_path, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"retrievals": {}, "feedback": {}, "references": {}}

    def _save_stats(self):
        """持久化统计数据"""
        self._stats_path.parent.mkdir(parents=True, exist_ok=True)
        tmp = str(self._stats_path) + ".tmp"
        with open(tmp, "w") as f:
            json.dump(self._stats, f, ensure_ascii=False)
        import os
        os.replace(tmp, str(self._stats_path))

    # ── 信号记录 ────────────────────────────────────────

    def record_retrieval(self, memory_id: str):
        """记录一次检索命中"""
        retrievals = self._stats["retrievals"]
        retrievals[memory_id] = retrievals.get(memory_id, 0) + 1
        self._save_stats()

    def record_reference(self, memory_id: str):
        """记录一次被引用"""
        refs = self._stats["references"]
        refs[memory_id] = refs.get(memory_id, 0) + 1
        self._save_stats()

    def record_feedback(self, memory_id: str, useful: bool, note: str = None):
        """
        记录用户显式反馈。

        参数:
            useful: True=有用, False=没用
            note: 可选备注
        """
        feedback = self._stats["feedback"]
        feedback[memory_id] = {
            "useful": useful,
            "note": note,
            "timestamp": int(time.time()),
        }
        self._save_stats()
        logger.info(f"📝 反馈记录: {memory_id} → {'👍' if useful else '👎'}")

    # ── 质量计算 ────────────────────────────────────────

    def compute_quality(self, memory: dict) -> dict:
        """
        计算单条记忆的质量分数。

        返回:
        {
            "memory_id": str,
            "quality_score": float,    # 0.0 ~ 1.0
            "grade": str,              # A/B/C/D/F
            "breakdown": dict,         # 各维度得分
            "recommendation": str,     # 建议操作
        }
        """
        mid = memory.get("memory_id", "")
        breakdown = {}

        # 1. 被检索次数 (0~1)
        retrieval_count = self._stats["retrievals"].get(mid, 0)
        breakdown["retrieval"] = min(1.0, retrieval_count / 10) * self.WEIGHTS["retrieval_count"]

        # 2. 被引用次数 (0~1)
        ref_count = self._stats["references"].get(mid, 0)
        breakdown["reference"] = min(1.0, ref_count / 5) * self.WEIGHTS["reference_count"]

        # 3. 存活时间 (适度奖励)
        age_days = (time.time() - memory.get("time_ts", time.time())) / 86400
        if age_days > 30:
            breakdown["age"] = min(1.0, age_days / 365) * self.WEIGHTS["age_bonus"]
        else:
            breakdown["age"] = 0

        # 4. 显式反馈
        feedback = self._stats["feedback"].get(mid)
        if feedback:
            breakdown["feedback"] = (1.0 if feedback["useful"] else 0.0) * self.WEIGHTS["explicit_feedback"]
        else:
            breakdown["feedback"] = 0.5 * self.WEIGHTS["explicit_feedback"]  # 无反馈给中性分

        # 5. 内容质量启发式
        content = memory.get("content", "")
        quality_signals = 0
        if len(content) > 50:
            quality_signals += 0.3
        if len(content) > 200:
            quality_signals += 0.2
        if memory.get("importance") == "high":
            quality_signals += 0.3
        if memory.get("is_aggregated"):
            quality_signals += 0.2
        breakdown["content"] = min(1.0, quality_signals) * self.WEIGHTS["content_quality"]

        # 总分
        total = sum(breakdown.values())
        total = round(min(1.0, max(0.0, total)), 4)

        # 等级
        if total >= 0.8:
            grade = "A"
        elif total >= 0.6:
            grade = "B"
        elif total >= 0.4:
            grade = "C"
        elif total >= 0.2:
            grade = "D"
        else:
            grade = "F"

        # 建议
        if grade == "F" and age_days > 90:
            recommendation = "考虑删除或归档"
        elif grade == "D":
            recommendation = "价值较低，可压缩"
        elif grade == "A":
            recommendation = "高价值记忆，永不衰减"
        else:
            recommendation = "正常保留"

        return {
            "memory_id": mid,
            "quality_score": total,
            "grade": grade,
            "breakdown": breakdown,
            "recommendation": recommendation,
        }

    def rank_by_quality(self, memories: list[dict]) -> list[dict]:
        """按质量分数排序检索结果"""
        for mem in memories:
            q = self.compute_quality(mem)
            mem["_quality_score"] = q["quality_score"]
            mem["_quality_grade"] = q["grade"]
        memories.sort(key=lambda m: m.get("_quality_score", 0), reverse=True)
        return memories

    def get_low_quality_memories(self, threshold: float = 0.2, limit: int = 50) -> list[dict]:
        """找出低质量记忆（可考虑清理）"""
        all_memories = self.store.query(limit=200)
        low_quality = []
        for mem in all_memories:
            q = self.compute_quality(mem)
            if q["quality_score"] < threshold:
                low_quality.append({**mem, "_quality": q})
        low_quality.sort(key=lambda m: m["_quality"]["quality_score"])
        return low_quality[:limit]

    def get_stats(self) -> dict:
        """质量系统统计"""
        total_feedback = len(self._stats["feedback"])
        useful_count = sum(1 for f in self._stats["feedback"].values() if f.get("useful"))
        total_retrievals = sum(self._stats["retrievals"].values())

        return {
            "total_feedback": total_feedback,
            "useful_ratio": useful_count / total_feedback if total_feedback else 0,
            "total_retrieval_events": total_retrievals,
            "unique_retrieved": len(self._stats["retrievals"]),
            "unique_referenced": len(self._stats["references"]),
        }

    def generate_quality_report(self) -> str:
        """生成质量分析报告"""
        stats = self.get_stats()
        all_memories = self.store.query(limit=200)

        # 计算所有记忆的质量
        quality_dist = {"A": 0, "B": 0, "C": 0, "D": 0, "F": 0}
        for mem in all_memories:
            q = self.compute_quality(mem)
            quality_dist[q["grade"]] = quality_dist.get(q["grade"], 0) + 1

        lines = [
            "# 📊 记忆质量报告",
            "",
            f"**总记忆数**: {len(all_memories)}",
            f"**总反馈数**: {stats['total_feedback']}",
            f"**有用率**: {stats['useful_ratio']:.0%}",
            f"**总检索事件**: {stats['total_retrieval_events']}",
            "",
            "## 质量分布",
            "",
        ]

        grade_icons = {"A": "🏆", "B": "✅", "C": "📝", "D": "⚠️", "F": "🗑️"}
        for grade in ["A", "B", "C", "D", "F"]:
            count = quality_dist.get(grade, 0)
            if count:
                icon = grade_icons[grade]
                bar = "█" * min(count, 20)
                lines.append(f"- {icon} **{grade}**: {count} {bar}")

        return "\n".join(lines)
