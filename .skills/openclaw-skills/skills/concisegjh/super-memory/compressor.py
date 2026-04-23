"""
compressor.py - LLM 驱动的记忆压缩器
将衰减的同主题记忆压缩为结构化摘要，减少存储冗余
"""

import json
import logging
import time
from datetime import datetime

logger = logging.getLogger(__name__)


class MemoryCompressor:
    """
    记忆压缩流程：
    1. 找出需要压缩的记忆（decay 状态的 medium/low）
    2. 按主题分组
    3. 调用 LLM 生成压缩摘要
    4. 写入新的聚合记忆，标记 is_aggregated=True
    5. 原始记忆标记为已压缩（软删除）

    LLM 调用签名: llm_fn(prompt: str) -> str
    """

    COMPRESS_PROMPT = """你是一个记忆压缩器。请将以下多条对话记忆压缩为一条结构化摘要。

主题: {topic}
记忆条数: {count}
时间跨度: {time_range}

原始记忆:
{memories}

要求：
1. 保留所有关键信息：决策、结论、事实、待办
2. 丢弃闲聊、重复、过渡性内容
3. 输出简洁的结构化摘要，不超过 300 字
4. 标注哪些是"关键决策"、"事实记录"、"待办事项"

输出格式：
## 摘要
[一段话概括核心内容]

## 关键决策
- [决策1]
- [决策2]

## 事实记录
- [事实1]

## 待办事项
- [待办1]
"""

    # 压缩策略
    BATCH_SIZE = 10           # 每批最多压缩几条
    MIN_GROUP_SIZE = 3        # 至少几条才触发压缩
    MAX_CONTENT_LENGTH = 500  # 每条记忆截断长度

    def __init__(self, store, encoder=None, llm_fn=None):
        """
        store: MemoryStore 实例
        encoder: DimensionEncoder 实例
        llm_fn: LLM 调用函数，签名 fn(prompt: str) -> str
                如果为 None，压缩功能不可用
        """
        self.store = store
        self.encoder = encoder
        self.llm_fn = llm_fn

    def compress(
        self,
        topic_code: str = None,
        importance: str = None,
        dry_run: bool = False,
    ) -> dict:
        """
        执行压缩操作。

        参数:
            topic_code: 只压缩指定主题（None=全部）
            importance: 只压缩指定重要度（None=全部可压缩的）
            dry_run: True=只分析不执行

        返回:
        {
            "total_candidates": int,
            "groups": [{"topic": str, "count": int, "memories": [...]}],
            "compressed": [{"summary_id": str, "topic": str, "source_count": int}],
            "dry_run": bool,
        }
        """
        if not self.llm_fn:
            return {"error": "LLM function not set, compression unavailable"}

        # 1. 找出可压缩的记忆
        candidates = self._find_candidates(topic_code, importance)
        if not candidates:
            return {"total_candidates": 0, "groups": [], "compressed": [], "dry_run": dry_run}

        # 2. 按主题分组
        groups = self._group_by_topic(candidates)

        # 3. 过滤太小的组
        groups = [g for g in groups if len(g["memories"]) >= self.MIN_GROUP_SIZE]

        if dry_run:
            return {
                "total_candidates": len(candidates),
                "groups": groups,
                "compressed": [],
                "dry_run": True,
            }

        # 4. 逐组压缩
        compressed = []
        for group in groups:
            result = self._compress_group(group)
            if result:
                compressed.append(result)

        return {
            "total_candidates": len(candidates),
            "groups": groups,
            "compressed": compressed,
            "dry_run": False,
        }

    def _find_candidates(self, topic_code: str = None, importance: str = None) -> list[dict]:
        """
        找出需要压缩的记忆。
        条件：importance=medium 且 age>=180天，或 importance=low 且 age>=30天
        """
        now = time.time()
        candidates = []

        # 查询 medium 和 low 的记忆
        for imp in [importance] if importance else ["medium", "low"]:
            memories = self.store.query(importance=imp, limit=500, topic_code=topic_code)
            for mem in memories:
                if mem.get("is_aggregated"):
                    continue  # 跳过已聚合的
                age_days = (now - mem.get("time_ts", now)) / 86400
                if imp == "medium" and age_days >= 180:
                    candidates.append(mem)
                elif imp == "low" and age_days >= 30:
                    candidates.append(mem)

        return candidates

    def _group_by_topic(self, memories: list[dict]) -> list[dict]:
        """按主主题分组"""
        topic_groups: dict[str, list[dict]] = {}

        for mem in memories:
            topics = mem.get("topics", [])
            primary = None
            for t in topics:
                if isinstance(t, dict) and t.get("is_primary"):
                    primary = t["code"]
                    break
                elif isinstance(t, str):
                    primary = t
                    break
            if not primary:
                primary = "misc"

            # 归到一级主题下（减少碎片化）
            top_topic = primary.split(".")[0]
            if top_topic not in topic_groups:
                topic_groups[top_topic] = []
            topic_groups[top_topic].append(mem)

        groups = []
        for topic, mems in topic_groups.items():
            # 按时间排序
            mems.sort(key=lambda m: m.get("time_ts", 0))
            time_range = self._format_time_range(mems)
            groups.append({
                "topic": topic,
                "count": len(mems),
                "time_range": time_range,
                "memories": mems,
            })

        # 大的组优先
        groups.sort(key=lambda g: -g["count"])
        return groups

    def _compress_group(self, group: dict) -> dict | None:
        """压缩一个主题组"""
        topic = group["topic"]
        memories = group["memories"][:self.BATCH_SIZE]  # 限制每批数量
        time_range = group["time_range"]

        # 构建记忆文本
        mem_texts = []
        for i, mem in enumerate(memories):
            content = mem.get("content", "")[:self.MAX_CONTENT_LENGTH]
            ts = mem.get("time_ts", 0)
            dt = datetime.fromtimestamp(ts).strftime("%m-%d %H:%M") if ts else "?"
            mem_texts.append(f"[{i+1}] ({dt}) {content}")

        memories_block = "\n\n".join(mem_texts)

        prompt = self.COMPRESS_PROMPT.format(
            topic=topic,
            count=len(memories),
            time_range=time_range,
            memories=memories_block,
        )

        try:
            summary_text = self.llm_fn(prompt)
        except Exception as e:
            logger.error(f"LLM compression failed for topic {topic}: {e}")
            return None

        # 生成压缩记忆的 memory_id
        import hashlib
        first_ts = memories[0].get("time_ts", int(time.time()))
        time_id = self.encoder.encode_time(first_ts, precision="second") if self.encoder else f"T{first_ts}"
        person_id = memories[0].get("person_id", "P01")
        summary_id = f"{time_id}_{person_id}_{topic.replace('.', '_')}_compressed"

        # 写入聚合记忆
        self.store.insert_memory(
            memory_id=summary_id,
            time_id=time_id,
            time_ts=int(time.time()),
            person_id=person_id,
            nature_id="D09",  # retro/回溯
            content=summary_text,
            content_hash=hashlib.sha256(summary_text.encode()).hexdigest(),
            topics=[topic],
            importance=memories[0].get("importance", "medium"),
            is_aggregated=True,
            source_count=len(memories),
        )

        # 建立关联：压缩记忆 → 原始记忆
        for mem in memories:
            self.store.insert_link(
                source_id=summary_id,
                target_id=mem["memory_id"],
                link_type="compressed_from",
                weight=0.5,
                reason=f"压缩自 {len(memories)} 条原始记忆",
            )

        # 原始记忆标记为已压缩（通过 content 追加标记）
        # 注意：不删除，保留用于溯源
        for mem in memories:
            self._mark_compressed(mem["memory_id"], summary_id)

        logger.info(f"📦 压缩完成: {topic} ({len(memories)}条 → 1条摘要)")
        return {
            "summary_id": summary_id,
            "topic": topic,
            "source_count": len(memories),
            "time_range": time_range,
        }

    def _mark_compressed(self, memory_id: str, summary_id: str):
        """标记原始记忆为已压缩（添加关联）"""
        self.store.insert_link(
            source_id=memory_id,
            target_id=summary_id,
            link_type="compressed_to",
            weight=0.3,
            reason="已压缩为摘要",
        )

    def _format_time_range(self, memories: list[dict]) -> str:
        """格式化时间范围"""
        if not memories:
            return "?"
        timestamps = [m.get("time_ts", 0) for m in memories if m.get("time_ts")]
        if not timestamps:
            return "?"
        earliest = datetime.fromtimestamp(min(timestamps)).strftime("%Y-%m-%d")
        latest = datetime.fromtimestamp(max(timestamps)).strftime("%Y-%m-%d")
        if earliest == latest:
            return earliest
        return f"{earliest} ~ {latest}"

    def get_compression_stats(self) -> dict:
        """获取压缩统计"""
        # 查询已压缩的记忆数
        rows = self.store.conn.execute(
            """SELECT COUNT(DISTINCT m.memory_id) as cnt
               FROM memories m
               WHERE m.is_aggregated = 1"""
        ).fetchone()

        aggregated_count = rows["cnt"] if rows else 0

        # 查询被压缩的原始记忆数
        rows2 = self.store.conn.execute(
            """SELECT COUNT(*) as cnt
               FROM memory_links
               WHERE link_type = 'compressed_to'"""
        ).fetchone()
        compressed_source_count = rows2["cnt"] if rows2 else 0

        # 查询候选压缩数
        candidates = self._find_candidates()
        pending_count = len(candidates)

        return {
            "aggregated_summaries": aggregated_count,
            "compressed_sources": compressed_source_count,
            "pending_compression": pending_count,
            "llm_available": self.llm_fn is not None,
        }

    def generate_compression_report(self) -> str:
        """生成压缩状态报告"""
        stats = self.get_compression_stats()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        lines = [
            "# 📦 记忆压缩报告",
            "",
            f"**生成时间**: {now_str}",
            f"**LLM 可用**: {'✅' if stats['llm_available'] else '❌'}",
            "",
            "## 统计",
            "",
            f"- 聚合摘要数: **{stats['aggregated_summaries']}**",
            f"- 已压缩原始记忆: **{stats['compressed_sources']}**",
            f"- 待压缩候选: **{stats['pending_compression']}**",
        ]

        if stats["pending_compression"] > 0:
            lines.extend([
                "",
                "## ⚠️ 待压缩主题分布",
                "",
            ])
            candidates = self._find_candidates()
            groups = self._group_by_topic(candidates)
            for g in groups:
                lines.append(f"- **{g['topic']}**: {g['count']} 条 ({g['time_range']})")

        return "\n".join(lines)

    def smart_compress(
        self,
        embedding_store=None,
        topic_code: str = None,
    ) -> dict:
        """
        智能压缩：用向量聚类区分核心记忆 vs 边缘记忆。

        核心记忆（聚类中心）→ 保留原文
        边缘记忆（远离中心）→ 压缩为摘要，可物理删除

        参数:
            embedding_store: EmbeddingStore 实例
            topic_code: 指定主题

        返回:
        {
            "topic": str,
            "core_memories": [memory_ids],    # 保留的核心记忆
            "edge_memories": [memory_ids],    # 被压缩的边缘记忆
            "summary_id": str,
            "saved_tokens": int,              # 预估节省的 token
        }
        """
        if not self.llm_fn:
            return {"error": "LLM function not set"}

        candidates = self._find_candidates(topic_code=topic_code)
        if len(candidates) < self.MIN_GROUP_SIZE:
            return {"error": f"候选记忆不足 {self.MIN_GROUP_SIZE} 条"}

        groups = self._group_by_topic(candidates)
        results = []

        for group in groups:
            if len(group["memories"]) < self.MIN_GROUP_SIZE:
                continue

            # 向量聚类：找核心 vs 边缘
            core, edge = self._cluster_core_edge(
                group["memories"],
                embedding_store,
            )

            if not edge:
                # 没有边缘记忆，跳过
                continue

            # 只压缩边缘记忆
            edge_group = {
                "topic": group["topic"],
                "count": len(edge),
                "time_range": self._format_time_range(edge),
                "memories": edge,
            }
            compress_result = self._compress_group(edge_group)

            if compress_result:
                compress_result["core_memories"] = [m["memory_id"] for m in core]
                compress_result["edge_memories"] = [m["memory_id"] for m in edge]
                compress_result["saved_tokens"] = sum(
                    len(m.get("content", "")) // 2 for m in edge
                )
                results.append(compress_result)

        if not results:
            return {"error": "无有效压缩"}

        return results[0] if len(results) == 1 else {"multi_topic": results}

    def _cluster_core_edge(
        self,
        memories: list[dict],
        embedding_store=None,
    ) -> tuple[list[dict], list[dict]]:
        """
        将记忆分为核心和边缘。

        有 embedding 时：用向量聚类
        无 embedding 时：用重要度 + 时间启发式
        """
        if not embedding_store or not memories:
            # 启发式：high 重要度或最新的是核心
            sorted_mems = sorted(
                memories,
                key=lambda m: (
                    0 if m.get("importance") == "high" else 1,
                    -(m.get("time_ts", 0)),
                ),
            )
            # 前 30% 为核心
            split = max(1, len(sorted_mems) // 3)
            return sorted_mems[:split], sorted_mems[split:]

        # 向量聚类：计算每个记忆到其他记忆的平均相似度
        # 平均相似度最高的 = 最核心的
        try:
            contents = [m.get("content", "") for m in memories]
            vectors = []
            for c in contents:
                try:
                    results = embedding_store.search(c, top_k=1)
                    # 用 search 的 score 作为与其他记忆关系的代理
                    vectors.append(results[0]["score"] if results else 0)
                except Exception:
                    vectors.append(0)

            # 按 score 排序（高 = 核心）
            indexed = list(enumerate(vectors))
            indexed.sort(key=lambda x: -x[1])

            split = max(1, len(memories) // 3)
            core_indices = {idx for idx, _ in indexed[:split]}
            edge_indices = {idx for idx, _ in indexed[split:]}

            core = [memories[i] for i in core_indices]
            edge = [memories[i] for i in edge_indices]
            return core, edge

        except Exception:
            # 降级到启发式
            return self._cluster_core_edge(memories, None)
