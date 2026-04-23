"""
memory_system.py - Agent Memory System 统一入口
一行初始化，一行调用
"""

import os
import logging

logger = logging.getLogger(__name__)


class AgentMemory:
    """
    Agent Memory System v4 — 统一 API

    用法:
        memory = AgentMemory(db_path="memory.db")

        # 写入（自动过滤 + 去重 + 编码 + 存储）
        memory.remember("用户偏好用 Chroma 做向量库")

        # 检索（结构化 + 语义混合）
        results = memory.recall("用户的向量库偏好")

        # 组装上下文（直接拼入 Agent prompt）
        prompt = memory.build_context(query="用户的问题")

        # 反馈（优化质量评分）
        memory.feedback(memory_id, useful=True)
    """

    def __init__(
        self,
        db_path: str = None,
        project_dir: str = None,
        llm_fn=None,
        enable_semantic: bool = True,
        enable_filter: bool = True,
        enable_dedup: bool = True,
    ):
        """
        参数:
            db_path: SQLite 数据库路径
            project_dir: 项目根目录（存放 registry、daily_index 等）
            llm_fn: LLM 函数（用于主题拆分 + 记忆压缩）
            enable_semantic: 启用语义搜索
            enable_filter: 启用记忆过滤
            enable_dedup: 启用去重
        """
        from encoder import DimensionEncoder
        from store import MemoryStore
        from pipeline import IngestPipeline
        from recall import RecallEngine
        from topic_registry import TopicRegistry
        from archiver import Archiver
        from decay import MemoryDecay
        from context_builder import ContextBuilder
        from memory_filter import MemoryFilter
        from dedup import MemoryDeduplicator
        from quality import MemoryQuality
        from causal import CausalChain
        from compressor import MemoryCompressor
        from hierarchical import HierarchicalMemory
        from self_healing import SelfHealing
        from memory_graph import MemoryGraph

        self._project_dir = project_dir or os.path.dirname(__file__)

        # 核心组件
        self.encoder = DimensionEncoder(registry_path=os.path.join(self._project_dir, "registry", "dimensions.json"))
        self.store = MemoryStore(db_path)
        self.topic_registry = TopicRegistry(os.path.join(self._project_dir, "registry", "dimensions.json"))

        # 向量存储（可选）
        self.embedding_store = None
        if enable_semantic:
            try:
                from embedding_store import EmbeddingStore
                chroma_dir = os.path.join(self._project_dir, "chroma_db")
                self.embedding_store = EmbeddingStore(persist_dir=chroma_dir)
                logger.info("✅ Chroma 向量库已加载")
            except Exception as e:
                logger.warning(f"⚠️ Chroma 不可用: {e}")

        # 语义主题匹配（可选）
        self.semantic_matcher = None
        if enable_semantic and self.embedding_store:
            try:
                from semantic_topic import SemanticTopicMatcher
                self.semantic_matcher = SemanticTopicMatcher(
                    embedding_store=self.embedding_store,
                    registry_path=os.path.join(self._project_dir, "registry", "dimensions.json"),
                )
            except Exception as e:
                logger.warning(f"⚠️ 语义主题匹配不可用: {e}")

        # 管道
        index_dir = os.path.join(self._project_dir, "daily_index")
        self.pipeline = IngestPipeline(
            self.store, self.encoder,
            index_dir=index_dir,
            embedding_store=self.embedding_store,
            topic_registry=self.topic_registry,
            semantic_matcher=self.semantic_matcher,
        )

        # LLM 接入
        if llm_fn:
            self.pipeline.set_llm(llm_fn)

        # 检索
        self.recall_engine = RecallEngine(self.store, self.encoder, self.embedding_store)

        # 归档
        self.archiver = Archiver(self.pipeline, self.store, self.encoder)

        # 增强组件
        self.filter = MemoryFilter(llm_fn=llm_fn) if enable_filter else None
        self.dedup = MemoryDeduplicator(self.store, self.embedding_store) if enable_dedup else None
        self.context_builder = ContextBuilder(self.recall_engine)
        self.quality = MemoryQuality(self.store, os.path.join(self._project_dir, "quality_stats.json"))
        self.causal = CausalChain(self.store)
        self.compressor = MemoryCompressor(self.store, self.encoder, llm_fn=llm_fn)
        self.decay = MemoryDecay(self.store, self.encoder)
        self.hierarchy = HierarchicalMemory(self.store, self.quality)
        self.self_healing = SelfHealing(self.store, self.embedding_store)
        self.graph = MemoryGraph(self.store, self.topic_registry)

        # 启用的标志
        self._enable_filter = enable_filter
        self._enable_dedup = enable_dedup

    def remember(
        self,
        content: str,
        importance: str = None,
        topics: list[str] = None,
        nature: str = None,
        force: bool = False,
    ) -> dict:
        """
        写入一条记忆。

        自动执行：过滤 → 去重 → 编码 → 存储 → 向量索引

        参数:
            content: 记忆内容
            importance: 重要度（None 则自动评估）
            topics: 主题列表（None 则自动检测）
            nature: 性质（None 则自动检测）
            force: 跳过过滤强制写入

        返回: {"written": bool, "memory_id": str, "reason": str}
        """
        # 1. 过滤
        if not force and self._enable_filter and self.filter:
            filter_result = self.filter.should_remember(content)
            if not filter_result["remember"]:
                return {
                    "written": False,
                    "memory_id": None,
                    "reason": f"过滤: {filter_result['reason']}",
                }
            if importance is None:
                importance = filter_result["suggested_importance"]
            if nature is None:
                nature = filter_result["suggested_nature"]

        # 2. 去重
        if self._enable_dedup and self.dedup:
            dup_result = self.dedup.check_duplicate(content)
            if dup_result["is_duplicate"]:
                action = dup_result["action"]
                if action == "skip":
                    return {
                        "written": False,
                        "memory_id": dup_result["duplicate_of"],
                        "reason": f"重复: {dup_result['method']} (sim={dup_result['similarity']:.2f})",
                    }
                elif action == "link":
                    # 写入但建立关联
                    pass

        # 3. 写入
        result = self.pipeline.ingest(
            content=content,
            importance=importance or "medium",
            topics=topics,
            nature_code=nature,
        )

        # 4. 建立去重关联
        if self._enable_dedup and self.dedup and dup_result.get("is_duplicate") and dup_result.get("action") == "link":
            self.store.insert_link(
                source_id=result["memory_id"],
                target_id=dup_result["duplicate_of"],
                link_type="similar_to",
                weight=dup_result["similarity"],
                reason="近似重复",
            )

        return {
            "written": True,
            "memory_id": result["memory_id"],
            "reason": "ok",
            "topics": result.get("topics", []),
            "nature": result.get("nature_id", ""),
            "importance": importance or "medium",
        }

    def recall(
        self,
        query: str = None,
        topic: str = None,
        importance: str = None,
        limit: int = 10,
    ) -> dict:
        """
        检索记忆。

        自动执行：结构化 + 语义混合检索 → 质量评分排序

        参数:
            query: 自然语言查询
            topic: 主题过滤
            importance: 重要度过滤
            limit: 返回条数
        """
        result = self.recall_engine.recall(
            query=query,
            topic_path=topic,
            importance=importance,
            limit=limit,
        )

        # 质量评分排序
        if result.get("primary"):
            result["primary"] = self.quality.rank_by_quality(result["primary"])

            # 记录检索事件
            for mem in result["primary"]:
                self.quality.record_retrieval(mem.get("memory_id", ""))

        return result

    def build_context(
        self,
        query: str = None,
        max_tokens: int = 2000,
        style: str = "structured",
    ) -> str:
        """
        组装 Agent 上下文（直接拼入 system prompt）。

        参数:
            query: 当前对话内容
            max_tokens: token 预算
            style: structured / narrative / compact / xml
        """
        result = self.context_builder.build(
            query=query,
            max_tokens=max_tokens,
            style=style,
        )
        return result["context"]

    def feedback(self, memory_id: str, useful: bool, note: str = None):
        """对一条记忆给出有用/没用的反馈"""
        self.quality.record_feedback(memory_id, useful, note)

    def compress(self, topic: str = None, smart: bool = True) -> dict:
        """
        压缩记忆。

        参数:
            topic: 指定主题
            smart: 使用智能压缩（向量聚类区分核心/边缘）
        """
        if smart:
            return self.compressor.smart_compress(
                embedding_store=self.embedding_store,
                topic_code=topic,
            )
        return self.compressor.compress(topic_code=topic)

    def deduplicate(self) -> dict:
        """批量去重"""
        if self.dedup:
            return self.dedup.deduplicate_batch()
        return {"error": "dedup not enabled"}

    def analyze_decay(self) -> dict:
        """分析记忆衰减状态"""
        return self.decay.analyze_all()

    def detect_causality(self, window_hours: int = 24) -> list[dict]:
        """自动检测因果关系"""
        return self.causal.auto_detect_causality(window_hours)

    def self_heal(self) -> dict:
        """执行自我修复扫描"""
        return self.self_healing.full_scan()

    def generate_graph(self, topic: str = None, format: str = "mermaid") -> str:
        """生成记忆图谱"""
        return self.graph.generate(center_topic=topic, format=format)

    def l1_add(self, content: str, role: str = "user") -> dict:
        """添加到短期记忆"""
        return self.hierarchy.l1_add(content, role)

    def l1_context(self, max_tokens: int = 1500) -> str:
        """获取短期记忆上下文"""
        return self.hierarchy.l1_context(max_tokens)

    def flush_session(self) -> list[dict]:
        """对话结束：L1 沉淀到 L2"""
        result = self.hierarchy.l1_flush_to_l2(self.pipeline)
        self.hierarchy.l1_clear()
        return result

    def get_stats(self) -> dict:
        """系统整体统计"""
        stats = {
            "total_memories": len(self.store.query(limit=10000)),
            "quality": self.quality.get_stats(),
            "causal": self.causal.get_stats(),
            "hierarchy": self.hierarchy.get_stats(),
            "self_healing": self.self_healing.get_stats(),
            "decay": self.decay.analyze_all() if self.store.query(limit=1) else {},
        }
        if self.dedup:
            stats["dedup"] = self.dedup.get_stats()
        if self.embedding_store:
            stats["vectors"] = self.embedding_store.count()
        return stats

    def close(self):
        """关闭数据库连接"""
        self.store.close()
