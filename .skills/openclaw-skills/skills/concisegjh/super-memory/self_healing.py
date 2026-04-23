"""
self_healing.py - 记忆自我修复
检测矛盾、过时信息、自动修正或标记
"""

import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SelfHealing:
    """
    三种自我修复能力：

    1. 矛盾检测 — 同主题下结论相反的记忆
    2. 过时检测 — 事实性记忆被更新版本替代
    3. 一致性修复 — 关联记忆的元数据同步

    检测策略：
    - 同主题 + 同性质（note/note）→ 检查是否矛盾
    - 时间较新的覆盖较旧的 → 标记旧的为过时
    - 关联记忆的 importance 差异过大 → 同步
    """

    def __init__(self, store, embedding_store=None):
        self.store = store
        self.embedding_store = embedding_store

    def detect_contradictions(self, topic_code: str = None, limit: int = 100) -> list[dict]:
        """
        检测矛盾记忆。

        规则：
        - 同主题、同性质(note/note)、但内容中的结论词相反
        - 例如："A 比 B 好" vs "B 比 A 好"
        """
        memories = self.store.query(limit=limit, topic_code=topic_code)

        # 只看 note 性质
        notes = [m for m in memories if m.get("nature_id") == "D05"]

        contradictions = []
        checked = set()

        for i, mem_a in enumerate(notes):
            for mem_b in notes[i+1:]:
                pair_key = tuple(sorted([mem_a["memory_id"], mem_b["memory_id"]]))
                if pair_key in checked:
                    continue
                checked.add(pair_key)

                # 检查是否同主主题
                topics_a = self._get_primary_topics(mem_a)
                topics_b = self._get_primary_topics(mem_b)
                if not topics_a & topics_b:
                    continue

                # 检查矛盾信号
                score = self._contradiction_score(
                    mem_a.get("content", ""),
                    mem_b.get("content", ""),
                )

                if score > 0.6:
                    contradictions.append({
                        "memory_a": mem_a["memory_id"],
                        "memory_b": mem_b["memory_id"],
                        "content_a": mem_a.get("content", "")[:80],
                        "content_b": mem_b.get("content", "")[:80],
                        "contradiction_score": round(score, 2),
                        "shared_topics": list(topics_a & topics_b),
                        "action": "needs_review",
                    })

        if contradictions:
            logger.info(f"⚡ 检测到 {len(contradictions)} 组矛盾记忆")
            # 自动建立矛盾关联
            for c in contradictions:
                self.store.insert_link(
                    source_id=c["memory_a"],
                    target_id=c["memory_b"],
                    link_type="causal.contradicts",
                    weight=0.3,
                    reason=f"矛盾检测 (score={c['contradiction_score']})",
                )

        return contradictions

    def detect_outdated(self, window_days: int = 30) -> list[dict]:
        """
        检测过时记忆。

        规则：
        - 同主题有多条 note，时间较新的"可能"替代较旧的
        - 只标记，不删除（保留历史）
        """
        now = int(time.time())
        window_start = now - window_days * 86400

        memories = self.store.query(limit=200)
        notes = [m for m in memories if m.get("nature_id") == "D05"]

        # 按主题分组
        by_topic: dict[str, list[dict]] = {}
        for mem in notes:
            for topic in self._get_primary_topics(mem):
                top = topic.split(".")[0]
                if top not in by_topic:
                    by_topic[top] = []
                by_topic[top].append(mem)

        outdated = []

        for topic, group in by_topic.items():
            if len(group) < 2:
                continue

            # 按时间排序
            group.sort(key=lambda m: m.get("time_ts", 0))

            # 最新的可能替代旧的
            newest = group[-1]
            for old in group[:-1]:
                age_gap_days = (newest.get("time_ts", 0) - old.get("time_ts", 0)) / 86400

                # 时间差距足够大 + 旧的不是 high 重要度
                if age_gap_days >= 7 and old.get("importance") != "high":
                    # 检查内容是否有更新信号
                    if self._is_updated_content(old.get("content", ""), newest.get("content", "")):
                        outdated.append({
                            "outdated_id": old["memory_id"],
                            "updated_id": newest["memory_id"],
                            "outdated_content": old.get("content", "")[:60],
                            "updated_content": newest.get("content", "")[:60],
                            "age_gap_days": round(age_gap_days, 1),
                            "topic": topic,
                            "action": "mark_outdated",
                        })

                        # 标记过时关联
                        self.store.insert_link(
                            source_id=old["memory_id"],
                            target_id=newest["memory_id"],
                            link_type="outdated_by",
                            weight=0.2,
                            reason=f"被 {age_gap_days:.0f} 天后的新信息替代",
                        )

        if outdated:
            logger.info(f"📅 检测到 {len(outdated)} 条过时记忆")

        return outdated

    def heal_importance_consistency(self) -> dict:
        """
        修复重要度一致性。

        规则：
        - 关联记忆中，如果一个是 high，另一个是 low → 考虑同步
        - 同主题下的"决策"记忆应为 high
        """
        healed = []

        # 找 importance 差异过大的关联对
        links = self.store.conn.execute(
            """SELECT * FROM memory_links
               WHERE link_type IN ('temporal', 'topic', 'causal.decision_based_on')"""
        ).fetchall()

        for link in links:
            mem_a = self.store.get_memory(link["source_id"])
            mem_b = self.store.get_memory(link["target_id"])

            if not mem_a or not mem_b:
                continue

            imp_a = mem_a.get("importance", "medium")
            imp_b = mem_b.get("importance", "medium")

            # high 和 low 差异大
            if {imp_a, imp_b} == {"high", "low"}:
                # 提升 low 为 medium
                low_mem = mem_a if imp_a == "low" else mem_b
                self.store.conn.execute(
                    "UPDATE memories SET importance = 'medium' WHERE memory_id = ?",
                    (low_mem["memory_id"],),
                )
                self.store.conn.commit()
                healed.append({
                    "memory_id": low_mem["memory_id"],
                    "from": "low",
                    "to": "medium",
                    "reason": f"关联了 {imp_a} 级记忆",
                })

        return {"healed": healed, "count": len(healed)}

    def full_scan(self) -> dict:
        """
        执行完整的自我修复扫描。

        返回:
        {
            "contradictions": [...],
            "outdated": [...],
            "importance_healed": int,
            "total_issues": int,
        }
        """
        contradictions = self.detect_contradictions()
        outdated = self.detect_outdated()
        importance_result = self.heal_importance_consistency()

        total = len(contradictions) + len(outdated) + importance_result["count"]

        if total > 0:
            logger.info(f"🔧 自我修复扫描完成: {total} 个问题")

        return {
            "contradictions": contradictions,
            "outdated": outdated,
            "importance_healed": importance_result["count"],
            "total_issues": total,
        }

    # ── 内部方法 ────────────────────────────────────────

    def _get_primary_topics(self, mem: dict) -> set[str]:
        topics = mem.get("topics", [])
        result = set()
        for t in topics:
            if isinstance(t, dict):
                result.add(t.get("code", ""))
            else:
                result.add(t)
        return {t for t in result if t}

    def _contradiction_score(self, text_a: str, text_b: str) -> float:
        """
        判断两段文本是否矛盾。

        启发式规则：
        - 包含相反结论词（更好/更差，推荐/不推荐）
        - 同一主题但观点相反
        """
        a_lower = text_a.lower()
        b_lower = text_b.lower()

        # 相反结论词对
        opposite_pairs = [
            (["更好", "最好", "推荐", "好用", "优秀"], ["更差", "最差", "不推荐", "难用", "差"]),
            (["支持", "赞成", "可以"], ["反对", "不赞成", "不行"]),
            (["快", "高效"], ["慢", "低效"]),
            (["安全", "可靠"], ["不安全", "不可靠"]),
            (["简单", "容易"], ["复杂", "困难"]),
            (["better", "best", "recommend"], ["worse", "worst", "avoid"]),
            (["fast", "efficient"], ["slow", "inefficient"]),
        ]

        score = 0.0
        for pos_words, neg_words in opposite_pairs:
            a_has_pos = any(w in a_lower for w in pos_words)
            a_has_neg = any(w in a_lower for w in neg_words)
            b_has_pos = any(w in b_lower for w in pos_words)
            b_has_neg = any(w in b_lower for w in neg_words)

            # A 说好，B 说差
            if (a_has_pos and b_has_neg) or (a_has_neg and b_has_pos):
                score += 0.4

        return min(1.0, score)

    def _is_updated_content(self, old_content: str, new_content: str) -> bool:
        """检查新内容是否可能是旧内容的更新版"""
        old_lower = old_content.lower()
        new_lower = new_content.lower()

        # 更新信号词
        update_signals = ["更新", "改为", "现在", "改成", "最新", "修正", "修正为", "updated", "changed", "now"]

        has_signal = any(w in new_lower for w in update_signals)

        # 共享关键词多 → 可能是同一话题的更新
        old_words = set(old_lower.split())
        new_words = set(new_lower.split())
        if old_words and new_words:
            overlap = len(old_words & new_words) / min(len(old_words), len(new_words))
            return has_signal and overlap > 0.3

        return has_signal

    def get_stats(self) -> dict:
        """自我修复统计"""
        contradictions = self.store.conn.execute(
            "SELECT COUNT(*) as cnt FROM memory_links WHERE link_type = 'causal.contradicts'"
        ).fetchone()

        outdated = self.store.conn.execute(
            "SELECT COUNT(*) as cnt FROM memory_links WHERE link_type = 'outdated_by'"
        ).fetchone()

        return {
            "contradiction_links": contradictions["cnt"] if contradictions else 0,
            "outdated_links": outdated["cnt"] if outdated else 0,
        }
