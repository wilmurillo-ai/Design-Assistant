"""
recall.py - 检索引擎
双路检索（结构化 + 语义）+ 综合排序
"""

import time
from store import MemoryStore
from encoder import DimensionEncoder


class RecallEngine:
    """记忆检索引擎，支持结构化/语义/混合三种模式"""

    def __init__(self, store: MemoryStore, encoder: DimensionEncoder, embedding_store=None):
        self.store = store
        self.encoder = encoder
        self.embedding_store = embedding_store

    def recall(
        self,
        # 结构化过滤参数
        time_from: int = None,
        time_to: int = None,
        person_id: str = None,
        nature_code: str = None,
        topic_path: str = None,
        tool_id: str = None,
        knowledge_id: str = None,
        importance: str = None,
        keyword: str = None,
        # 语义搜索参数
        query: str = None,
        semantic_weight: float = 0.5,
        # 通用参数
        limit: int = 20,
    ) -> dict:
        """
        综合检索入口

        根据传入参数自动选择检索模式：
        - 只有结构化参数 → structured
        - 只有 query → semantic
        - 两者都有 → hybrid

        返回：
        {
            "search_mode": "structured|semantic|hybrid",
            "total": int,
            "primary": [memory dicts],      # 主结果
            "related": [memory dicts],      # 关联结果
            "query": str,                   # 原始查询
        }
        """
        has_structured = any([time_from, time_to, person_id, nature_code,
                              topic_path, tool_id, knowledge_id, importance, keyword])
        has_semantic = query is not None and self.embedding_store is not None

        if has_structured and has_semantic:
            mode = "hybrid"
        elif has_semantic:
            mode = "semantic"
        else:
            mode = "structured"

        # ── 结构化检索 ──────────────────────────────────
        structured_results = []
        if has_structured or mode == "structured":
            nature_id = None
            if nature_code:
                try:
                    nature_id = self.encoder.encode_nature(nature_code)
                except ValueError:
                    pass

            structured_results = self.store.query(
                time_from=time_from,
                time_to=time_to,
                person_id=person_id,
                nature_id=nature_id,
                topic_code=topic_path,
                tool_id=tool_id,
                knowledge_id=knowledge_id,
                importance=importance,
                keyword=keyword,
                limit=limit,
            )

        # ── 语义检索 ────────────────────────────────────
        semantic_results = []
        if has_semantic:
            # 构建语义过滤器
            filter_meta = {}
            if importance:
                filter_meta["importance"] = importance
            if person_id:
                filter_meta["person_id"] = person_id

            raw_semantic = self.embedding_store.search(
                query=query,
                top_k=limit,
                filter_metadata=filter_meta if filter_meta else None,
            )

            # 补充结构化信息
            for item in raw_semantic:
                mem = self.store.get_memory(item["memory_id"])
                if mem:
                    mem["_semantic_score"] = item["score"]
                    semantic_results.append(mem)

        # ── 合并去重 ────────────────────────────────────
        if mode == "structured":
            merged = structured_results
        elif mode == "semantic":
            merged = semantic_results
        else:
            merged = self._merge_results(structured_results, semantic_results)

        # ── 综合排序 ────────────────────────────────────
        ranked = self._rank_results(merged, query=query, semantic_weight=semantic_weight)

        # ── 关联记录 ────────────────────────────────────
        related = []
        if ranked:
            top_id = ranked[0].get("memory_id")
            if top_id:
                related = self.store.get_linked(top_id, max_depth=1)

        return {
            "search_mode": mode,
            "total": len(ranked),
            "primary": ranked[:limit],
            "related": related,
            "query": query or "",
        }

    def _merge_results(self, structured: list[dict], semantic: list[dict]) -> list[dict]:
        """合并结构化和语义结果，按 memory_id 去重"""
        seen = set()
        merged = []

        for mem in structured:
            mid = mem.get("memory_id")
            if mid and mid not in seen:
                seen.add(mid)
                mem["_structured_score"] = 1.0
                merged.append(mem)

        for mem in semantic:
            mid = mem.get("memory_id")
            if mid and mid not in seen:
                seen.add(mid)
                merged.append(mem)
            elif mid in seen:
                # 已有记录，附加语义分数
                for m in merged:
                    if m.get("memory_id") == mid:
                        m["_semantic_score"] = mem.get("_semantic_score", 0)
                        break

        return merged

    def _rank_results(self, results: list[dict], query: str = None, semantic_weight: float = 0.5) -> list[dict]:
        """综合打分排序
        权重：重要度 30% + 时间 20% + 结构化 20% + 语义 30%
        """
        now = time.time()
        importance_map = {"high": 1.0, "medium": 0.5, "low": 0.1}
        struct_weight = 1.0 - semantic_weight

        for mem in results:
            scores = {}

            # 重要度分数 (30%)
            imp = mem.get("importance", "medium")
            scores["importance"] = importance_map.get(imp, 0.5) * 0.3

            # 时间衰减分数 (20%)：越新越高，24h 内满分
            time_ts = mem.get("time_ts", 0)
            age_hours = (now - time_ts) / 3600 if time_ts else 999
            scores["time"] = max(0, 1.0 - age_hours / 168) * 0.2  # 一周内线性衰减

            # 结构化匹配分数 (20%)
            scores["structured"] = mem.get("_structured_score", 0.5) * 0.2

            # 语义分数 (30%)
            scores["semantic"] = mem.get("_semantic_score", 0) * 0.3

            mem["_rank_score"] = sum(scores.values())
            mem["_rank_breakdown"] = scores

        results.sort(key=lambda m: m.get("_rank_score", 0), reverse=True)
        return results

    def format_context(self, result: dict, max_items: int = 10) -> str:
        """格式化检索结果为可读上下文文本"""
        lines = []
        mode = result.get("search_mode", "unknown")
        total = result.get("total", 0)

        lines.append(f"📋 检索结果 [{mode}] 共 {total} 条")
        lines.append("")

        for i, mem in enumerate(result.get("primary", [])[:max_items]):
            # 标签
            tags = []
            imp = mem.get("importance", "medium")
            if imp == "high":
                tags.append("⚡高优先")
            elif imp == "low":
                tags.append("🔻低优先")

            # 语义相似度
            sem = mem.get("_semantic_score")
            if sem is not None:
                tags.append(f"~{sem:.2f}")

            # 主题
            topics = mem.get("topics", [])
            topic_str = ""
            if topics:
                codes = [t["code"] if isinstance(t, dict) else t for t in topics]
                topic_str = " | " + ", ".join(codes)

            # 时间
            time_id = mem.get("time_id", "")

            tag_str = " ".join(tags)
            content = mem.get("content", "")[:80]

            lines.append(f"  {i+1}. {tag_str} [{time_id}]{topic_str}")
            lines.append(f"     {content}")

        # 关联记录
        related = result.get("related", [])
        if related:
            lines.append("")
            lines.append(f"  🔗 关联记录 ({len(related)} 条):")
            for r in related[:3]:
                r_content = r.get("content", "")[:50]
                link_type = r.get("_link_type", "")
                lines.append(f"     → [{link_type}] {r_content}")

        return "\n".join(lines)

    def get_stats(self) -> dict:
        """返回检索引擎统计信息"""
        stats = {
            "structured_db": "SQLite",
            "semantic_db": "none",
        }
        if self.embedding_store:
            stats["semantic_db"] = "ChromaDB"
            stats["vector_count"] = self.embedding_store.count()
        return stats
