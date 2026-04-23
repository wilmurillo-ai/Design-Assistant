"""
dedup.py - 语义级记忆去重
防止语义相近但文字不同的记忆重复存储
"""

import hashlib
import logging
import re
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryDeduplicator:
    """
    三层去重：
    1. 精确去重 — content_hash 完全相同（已有）
    2. 近似去重 — 文本相似度 > 阈值
    3. 语义去重 — embedding 余弦相似度 > 阈值

    去重策略：
    - 保留较新/较高优先的版本
    - 旧版本标记为重复（不删除，保留溯源）
    - 合并两个版本的元数据（主题、标签等）
    """

    # 相似度阈值
    TEXT_SIMILARITY_THRESHOLD = 0.85   # 文本相似度阈值
    SEMANTIC_SIMILARITY_THRESHOLD = 0.92  # 语义相似度阈值（更严格，避免误判）

    def __init__(self, store, embedding_store=None):
        self.store = store
        self.embedding_store = embedding_store

    def check_duplicate(self, content: str, time_window_hours: int = 72) -> dict:
        """
        检查新内容是否与已有记忆重复。

        参数:
            content: 待写入的内容
            time_window_hours: 只检查这个时间窗口内的记忆

        返回:
        {
            "is_duplicate": bool,
            "duplicate_of": str | None,      # 重复的 memory_id
            "similarity": float,             # 最高相似度
            "method": str,                   # "exact" / "text" / "semantic"
            "action": str,                   # "skip" / "merge" / "keep_both"
        }
        """
        import time
        now = int(time.time())
        window_start = now - time_window_hours * 3600

        # 1. 精确去重（content_hash）
        content_hash = hashlib.sha256(content.encode()).hexdigest()
        exact = self.store.conn.execute(
            "SELECT memory_id FROM memories WHERE content_hash = ? AND time_ts >= ?",
            (content_hash, window_start),
        ).fetchone()
        if exact:
            return {
                "is_duplicate": True,
                "duplicate_of": exact["memory_id"],
                "similarity": 1.0,
                "method": "exact",
                "action": "skip",
            }

        # 2. 获取时间窗口内的记忆
        candidates = self.store.query(limit=100)
        candidates = [m for m in candidates if m.get("time_ts", 0) >= window_start]

        if not candidates:
            return {"is_duplicate": False, "duplicate_of": None, "similarity": 0, "method": "none", "action": "keep_both"}

        # 3. 文本相似度（快速筛选）
        best_text_score = 0
        best_text_id = None
        for mem in candidates:
            score = self._text_similarity(content, mem.get("content", ""))
            if score > best_text_score:
                best_text_score = score
                best_text_id = mem["memory_id"]

        if best_text_score >= self.TEXT_SIMILARITY_THRESHOLD:
            return {
                "is_duplicate": True,
                "duplicate_of": best_text_id,
                "similarity": round(best_text_score, 4),
                "method": "text",
                "action": self._decide_action(content, best_text_id, best_text_score),
            }

        # 4. 语义相似度（如果 embedding 可用）
        if self.embedding_store:
            best_semantic_score = 0
            best_semantic_id = None
            try:
                results = self.embedding_store.search(content, top_k=5)
                for r in results:
                    if r["score"] > best_semantic_score:
                        best_semantic_score = r["score"]
                        best_semantic_id = r["memory_id"]
            except Exception:
                pass

            if best_semantic_score >= self.SEMANTIC_SIMILARITY_THRESHOLD:
                return {
                    "is_duplicate": True,
                    "duplicate_of": best_semantic_id,
                    "similarity": round(best_semantic_score, 4),
                    "method": "semantic",
                    "action": self._decide_action(content, best_semantic_id, best_semantic_score),
                }

        return {
            "is_duplicate": False,
            "duplicate_of": None,
            "similarity": round(max(best_text_score, 0), 4),
            "method": "none",
            "action": "keep_both",
        }

    def deduplicate_batch(self, memory_ids: list[str] = None) -> dict:
        """
        批量去重：扫描现有记忆，找出并处理重复项。

        参数:
            memory_ids: 指定要检查的记忆 ID 列表（None=全部）

        返回:
        {
            "total_scanned": int,
            "duplicates_found": int,
            "merged": [{"kept": str, "removed": str, "similarity": float}],
            "groups": [[str]],  # 重复组
        }
        """
        if memory_ids:
            memories = [self.store.get_memory(mid) for mid in memory_ids]
            memories = [m for m in memories if m]
        else:
            memories = self.store.query(limit=500)

        if len(memories) < 2:
            return {"total_scanned": len(memories), "duplicates_found": 0, "merged": [], "groups": []}

        # 找出重复组
        visited = set()
        duplicate_groups = []

        for i, mem_a in enumerate(memories):
            mid_a = mem_a["memory_id"]
            if mid_a in visited:
                continue

            group = [mid_a]
            for j, mem_b in enumerate(memories):
                if i == j:
                    continue
                mid_b = mem_b["memory_id"]
                if mid_b in visited:
                    continue

                score = self._text_similarity(mem_a.get("content", ""), mem_b.get("content", ""))
                if score >= self.TEXT_SIMILARITY_THRESHOLD:
                    group.append(mid_b)

            if len(group) > 1:
                duplicate_groups.append(group)
                visited.update(group)

        # 合并每组（保留最新的/最高优先的）
        merged = []
        for group in duplicate_groups:
            memories_in_group = [self.store.get_memory(mid) for mid in group]
            memories_in_group = [m for m in memories_in_group if m]

            # 排序：high > medium > low，然后新的 > 旧的
            imp_order = {"high": 0, "medium": 1, "low": 2}
            memories_in_group.sort(key=lambda m: (
                imp_order.get(m.get("importance", "medium"), 1),
                -(m.get("time_ts", 0)),
            ))

            keeper = memories_in_group[0]
            for dup in memories_in_group[1:]:
                self._mark_duplicate(dup["memory_id"], keeper["memory_id"])
                merged.append({
                    "kept": keeper["memory_id"],
                    "removed": dup["memory_id"],
                    "similarity": self._text_similarity(
                        keeper.get("content", ""),
                        dup.get("content", ""),
                    ),
                })

        return {
            "total_scanned": len(memories),
            "duplicates_found": sum(len(g) - 1 for g in duplicate_groups),
            "merged": merged,
            "groups": duplicate_groups,
        }

    def _text_similarity(self, a: str, b: str) -> float:
        """
        文本相似度（Jaccard + 编辑距离混合）。
        比纯 embedding 快，适合大量初筛。
        """
        if not a or not b:
            return 0.0
        if a == b:
            return 1.0

        # 标准化
        a_norm = self._normalize(a)
        b_norm = self._normalize(b)

        if a_norm == b_norm:
            return 0.99

        # Jaccard 相似度（基于字符 bigram）
        set_a = set(self._char_ngrams(a_norm, 2))
        set_b = set(self._char_ngrams(b_norm, 2))

        if not set_a or not set_b:
            return 0.0

        intersection = len(set_a & set_b)
        union = len(set_a | set_b)

        return intersection / union if union > 0 else 0.0

    @staticmethod
    def _normalize(text: str) -> str:
        """标准化文本"""
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)  # 合并空白
        text = re.sub(r'[^\w\u4e00-\u9fff\s]', '', text)  # 去标点
        return text

    @staticmethod
    def _char_ngrams(text: str, n: int) -> list[str]:
        """字符 n-gram"""
        return [text[i:i+n] for i in range(len(text) - n + 1)]

    def _decide_action(self, new_content: str, existing_id: str, similarity: float) -> str:
        """决定如何处理重复"""
        existing = self.store.get_memory(existing_id)
        if not existing:
            return "keep_both"

        # 极高相似度 → 跳过
        if similarity >= 0.98:
            return "skip"

        # 新内容明显更长/更详细 → 合并（新覆盖旧）
        if len(new_content) > len(existing.get("content", "")) * 1.5:
            return "merge"

        # 相似度高但不完全一样 → 标记关联
        return "link"

    def _mark_duplicate(self, duplicate_id: str, keeper_id: str):
        """标记一条记忆为重复"""
        self.store.insert_link(
            source_id=duplicate_id,
            target_id=keeper_id,
            link_type="duplicate_of",
            weight=0.1,
            reason="语义去重",
        )

    def get_stats(self) -> dict:
        """去重统计"""
        rows = self.store.conn.execute(
            "SELECT COUNT(*) as cnt FROM memory_links WHERE link_type = 'duplicate_of'"
        ).fetchone()
        return {
            "duplicate_links": rows["cnt"] if rows else 0,
            "text_threshold": self.TEXT_SIMILARITY_THRESHOLD,
            "semantic_threshold": self.SEMANTIC_SIMILARITY_THRESHOLD,
        }
