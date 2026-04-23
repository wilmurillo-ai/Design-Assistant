"""
pipeline.py - 写入管道
主题检测 → 编码 → 关联建立 → 写入存储
"""

import time
import os
import json
from datetime import datetime
from encoder import DimensionEncoder
from store import MemoryStore
from detector import TopicDetector, TopicSplitter


class IngestPipeline:
    """将原始对话消息写入记忆系统"""

    def __init__(self, store: MemoryStore, encoder: DimensionEncoder, index_dir: str = None, embedding_store=None, topic_registry=None, semantic_matcher=None):
        self.store = store
        self.encoder = encoder
        self.topic_registry = topic_registry
        self.semantic_matcher = semantic_matcher
        self.detector = TopicDetector(encoder, topic_registry=topic_registry, semantic_matcher=semantic_matcher)
        self.splitter = TopicSplitter(encoder)  # 默认无 LLM，回退单片段
        self.embedding_store = embedding_store  # EmbeddingStore 实例，可选

        # 每日索引目录
        self._index_dir = index_dir or str(
            os.path.join(os.path.dirname(__file__), "daily_index")
        )

        # 窗口状态
        self._last_time_ts: int = 0
        self._last_person: str = ""
        self._last_memory_id: str = ""
        self._last_topic: str = ""
        self._window_buffer: list[str] = []
        self._window_size: int = 5  # 用户可配置

    def ingest(
        self,
        content: str,
        person_code: str = "main",
        ts: float = None,
        topics: list[str] = None,
        nature_code: str = None,
        tool_codes: list[str] = None,
        knowledge_codes: list[str] = None,
        importance: str = "medium",
    ) -> dict:
        """
        写入一条消息

        参数：
            content: 对话内容
            person_code: 端口 code（main/mobile/web）
            ts: 时间戳，None 则取当前时间
            topics: 显式指定主题路径列表，None 则自动检测
            nature_code: 显式指定性质 code，None 则自动检测
            tool_codes: 显式指定工具 code 列表，None 则自动检测
            knowledge_codes: 显式指定知识类型 code 列表，None 则自动检测
            importance: 重要度 (high/medium/low)

        返回：写入的 memory 记录
        """
        ts = ts or time.time()
        person_id = self.encoder.get_person_by_code(person_code)
        content_hash = DimensionEncoder.content_hash(content)

        # 检测主题
        if topics is None:
            topics = self.detector.detect(content, auto_register=True)
        if not topics:
            topics = ["misc"]

        # 检测性质
        if nature_code is None:
            nature_code = self.detector.detect_nature(content)
        nature_id = self.encoder.encode_nature(nature_code)

        # 检测工具
        tool_ids = []
        if tool_codes:
            for code in tool_codes:
                tool_ids.append(self.encoder.get_tool_by_code(code))

        # 检测知识类型
        knowledge_ids = []
        if knowledge_codes:
            for code in knowledge_codes:
                knowledge_ids.append(self.encoder.encode_knowledge(code))
        else:
            for code in self.detector.detect_knowledge(content):
                knowledge_ids.append(self.encoder.encode_knowledge(code))

        # 编码
        time_id = self.encoder.encode_time(ts, precision="second")
        memory_id = self.encoder.generate_memory_id(
            time_id, person_id, topics, nature_id, tool_ids
        )

        # 写入
        self.store.insert_memory(
            memory_id=memory_id,
            time_id=time_id,
            time_ts=int(ts),
            person_id=person_id,
            nature_id=nature_id,
            content=content,
            content_hash=content_hash,
            topics=topics,
            tools=tool_ids,
            knowledge_types=knowledge_ids,
            importance=importance,
        )

        # 自动提取待办任务（性质为 todo 时）
        task_id = None
        if nature_code == "todo":
            topic = topics[0] if topics else None
            task_id = self.store.add_task(
                memory_id=memory_id,
                title=content[:100],
                assignee="ai" if any(w in content for w in ["配置", "添加", "开发", "实现", "写"]) else "user",
                topic_code=topic,
            )

        # 写入向量库（语义搜索用）
        if self.embedding_store:
            self.embedding_store.add(
                memory_id=memory_id,
                content=content,
                metadata={
                    "nature_id": nature_id,
                    "importance": importance,
                    "person_id": person_id,
                },
            )

        # 更新每日索引
        self._update_daily_index(ts, memory_id, topics, nature_id, importance)

        # 建立时间关联
        if self._last_memory_id and self._last_person == person_id:
            time_gap = int(ts) - self._last_time_ts
            if time_gap < 300:  # 5分钟内算连续对话
                self.store.insert_link(
                    self._last_memory_id, memory_id,
                    link_type="temporal",
                    weight=max(0.1, 1.0 - time_gap / 300),
                    reason=f"时间间隔 {time_gap}s",
                )

        # 建立主题关联
        if self._last_topic and topics and self._last_topic == topics[0]:
            self.store.insert_link(
                self._last_memory_id, memory_id,
                link_type="topic",
                weight=0.8,
                reason=f"同主题 {topics[0]}",
            )

        # 更新窗口状态
        self._last_time_ts = int(ts)
        self._last_person = person_id
        self._last_memory_id = memory_id
        self._last_topic = topics[0] if topics else ""
        self._window_buffer.append(memory_id)
        if len(self._window_buffer) > self._window_size:
            self._window_buffer.pop(0)

        return {
            "memory_id": memory_id,
            "time_id": time_id,
            "person_id": person_id,
            "nature_id": nature_id,
            "topics": topics,
            "tools": tool_ids,
            "knowledge": knowledge_ids,
            "importance": importance,
            "task_id": task_id,
        }

    def _update_daily_index(self, ts: float, memory_id: str, topics: list[str], nature_id: str, importance: str):
        """写入时自动生成/更新每日索引文件"""
        dt = datetime.fromtimestamp(ts)
        date_str = dt.strftime("%Y-%m-%d")
        hour_str = dt.strftime("%H:%M")

        os.makedirs(self._index_dir, exist_ok=True)
        index_path = os.path.join(self._index_dir, f"{date_str}.json")

        # 读取已有索引
        if os.path.exists(index_path):
            with open(index_path, "r", encoding="utf-8") as f:
                index = json.load(f)
        else:
            index = {
                "date": date_str,
                "total": 0,
                "topics_summary": {},
                "entries": [],
            }

        # 追加条目
        entry = {
            "time": hour_str,
            "memory_id": memory_id,
            "topics": topics,
            "nature": nature_id,
            "importance": importance,
        }
        index["entries"].append(entry)
        index["total"] = len(index["entries"])

        # 更新主题统计
        for topic in topics:
            if topic not in index["topics_summary"]:
                index["topics_summary"][topic] = 0
            index["topics_summary"][topic] += 1

        # 写回
        with open(index_path, "w", encoding="utf-8") as f:
            json.dump(index, f, ensure_ascii=False, indent=2)

    def set_window_size(self, size: int):
        """设置连续对话窗口大小"""
        self._window_size = size

    def set_llm(self, llm_fn):
        """设置 LLM 函数，启用多主题智能拆分
        llm_fn 签名: fn(prompt: str) -> str
        """
        self.splitter = TopicSplitter(self.encoder, llm_fn=llm_fn)

    def split_and_ingest(
        self,
        content: str,
        person_code: str = "main",
        ts: float = None,
        importance: str = "medium",
    ) -> list[dict]:
        """
        先用 LLM 拆分多主题，再逐片段写入。
        返回所有写入的 memory 记录列表。
        """
        ts = ts or time.time()
        fragments = self.splitter.split(content)

        results = []
        for i, frag in enumerate(fragments):
            frag_ts = ts + i  # 同一秒内递增
            topics = [frag["topic"]] if frag.get("topic") else None
            nature = frag.get("nature") or None
            tools = frag.get("tools") or None
            knowledge = frag.get("knowledge") or None

            result = self.ingest(
                content=frag["content"],
                person_code=person_code,
                ts=frag_ts,
                topics=topics,
                nature_code=nature,
                tool_codes=tools,
                knowledge_codes=knowledge,
                importance=importance,
            )
            result["_split_fragment"] = i
            results.append(result)

        return results
