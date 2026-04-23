"""
hierarchical.py - 层级记忆管理
短期(对话级) → 中期(天级) → 长期(永久)，自动流转
"""

import time
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class HierarchicalMemory:
    """
    三级记忆层级：

    L1 短期记忆 (Short-term)
    - 生命周期: 单次对话 / 几小时
    - 容量: 50 条
    - 存储: 内存 buffer，不持久化
    - 用途: 当前对话上下文

    L2 中期记忆 (Mid-term)
    - 生命周期: 1-7 天
    - 容量: 500 条
    - 存储: SQLite (已持久化)
    - 用途: 近期对话回顾

    L3 长期记忆 (Long-term)
    - 生命周期: 永久
    - 容量: 无上限
    - 存储: SQLite + Chroma
    - 用途: 核心知识、决策、偏好

    流转规则:
    - L1 → L2: 对话结束 / buffer 满 → 自动沉淀
    - L2 → L3: 重要度 high / 被频繁检索 / 时间考验
    - L3 压缩: 低价值长期记忆 → 压缩为摘要
    """

    # 容量限制
    L1_CAPACITY = 50
    L2_CAPACITY = 500

    # L2 → L3 升级条件
    L2_TO_L3_MIN_AGE_DAYS = 3       # 至少存在 3 天
    L2_TO_L3_MIN_RETRIEVALS = 3     # 被检索至少 3 次
    L2_TO_L3_IMPORTANCE = "high"    # high 重要度直接升级

    def __init__(self, store, quality=None):
        self.store = store
        self.quality = quality

        # L1 短期记忆 buffer
        self._l1_buffer: list[dict] = []
        self._l1_session_id: str = datetime.now().strftime("session_%Y%m%d_%H%M%S")

    # ── L1 短期记忆 ────────────────────────────────────

    def l1_add(self, content: str, role: str = "user", metadata: dict = None) -> dict:
        """
        添加到短期记忆 buffer。

        参数:
            content: 消息内容
            role: user / assistant / system
            metadata: 附加元数据
        """
        entry = {
            "content": content,
            "role": role,
            "timestamp": int(time.time()),
            "session_id": self._l1_session_id,
            "metadata": metadata or {},
        }
        self._l1_buffer.append(entry)

        # 超容量则淘汰最旧的
        if len(self._l1_buffer) > self.L1_CAPACITY:
            evicted = self._l1_buffer.pop(0)
            logger.debug(f"L1 淘汰: {evicted['content'][:30]}...")

        return entry

    def l1_get(self, last_n: int = 10) -> list[dict]:
        """获取最近 N 条短期记忆"""
        return self._l1_buffer[-last_n:]

    def l1_context(self, max_tokens: int = 1500) -> str:
        """
        组装短期记忆为对话上下文。

        从最新的消息开始，逐步添加直到达到 token 预算。
        """
        lines = []
        token_count = 0

        for entry in reversed(self._l1_buffer):
            role = entry["role"]
            content = entry["content"]

            # 估算 tokens
            est_tokens = len(content) * 1.5
            if token_count + est_tokens > max_tokens:
                break

            prefix = {"user": "用户", "assistant": "助手", "system": "系统"}.get(role, role)
            lines.insert(0, f"{prefix}: {content}")
            token_count += est_tokens

        return "\n".join(lines)

    def l1_clear(self):
        """清空短期记忆（对话结束时调用）"""
        self._l1_buffer = []
        self._l1_session_id = datetime.now().strftime("session_%Y%m%d_%H%M%S")

    # ── L1 → L2 沉淀 ──────────────────────────────────

    def l1_flush_to_l2(self, pipeline=None) -> list[dict]:
        """
        将 L1 buffer 中的有价值内容沉淀到 L2（通过 pipeline 写入 SQLite）。

        参数:
            pipeline: IngestPipeline 实例

        返回: 写入的 memory 列表
        """
        if not pipeline or not self._l1_buffer:
            return []

        written = []
        for entry in self._l1_buffer:
            content = entry["content"]
            role = entry["role"]

            # 跳过系统消息和极短消息
            if role == "system" or len(content.strip()) < 10:
                continue

            # 角色映射到 person_code
            person_code = {"user": "main", "assistant": "main"}.get(role, "main")

            # 用 pipeline 写入
            result = pipeline.ingest(
                content=content,
                person_code=person_code,
                importance="medium",  # L2 默认 medium
            )
            written.append(result)

        logger.info(f"L1→L2 沉淀: {len(written)} 条")
        return written

    # ── L2 → L3 升级 ──────────────────────────────────

    def l2_promote_to_l3(self) -> dict:
        """
        将符合条件的 L2 记忆升级为 L3（提升重要度）。

        条件（满足任一）:
        - 重要度已经是 high
        - 存活超过 N 天且被检索超过 M 次
        - 有显式正反馈

        返回: {"promoted": [memory_ids], "count": int}
        """
        now = int(time.time())
        promoted = []

        memories = self.store.query(limit=self.L2_CAPACITY, importance="medium")

        for mem in memories:
            mid = mem["memory_id"]
            age_days = (now - mem.get("time_ts", now)) / 86400

            should_promote = False
            reason = ""

            # 条件 1: 高重要度直接升
            if mem.get("importance") == "high":
                should_promote = True
                reason = "already_high"

            # 条件 2: 时间 + 检索次数
            elif age_days >= self.L2_TO_L3_MIN_AGE_DAYS:
                retrieval_count = 0
                if self.quality:
                    retrieval_count = self.quality._stats.get("retrievals", {}).get(mid, 0)

                if retrieval_count >= self.L2_TO_L3_MIN_RETRIEVALS:
                    should_promote = True
                    reason = f"frequently_retrieved ({retrieval_count}x)"

            # 条件 3: 正反馈
            if self.quality and not should_promote:
                feedback = self.quality._stats.get("feedback", {}).get(mid)
                if feedback and feedback.get("useful"):
                    should_promote = True
                    reason = "positive_feedback"

            if should_promote:
                # 升级：更新 importance 为 high
                self.store.conn.execute(
                    "UPDATE memories SET importance = 'high' WHERE memory_id = ?",
                    (mid,),
                )
                self.store.conn.commit()
                promoted.append({"memory_id": mid, "reason": reason})
                logger.info(f"L2→L3 升级: {mid[:30]}... ({reason})")

        return {"promoted": promoted, "count": len(promoted)}

    # ── L3 维护 ─────────────────────────────────────────

    def l3_demote(self, threshold_days: int = 365) -> list[str]:
        """
        将长期未被访问的 L3 记忆降级（标记为可压缩）。

        被降级的条件：
        - importance=medium（high 不降级）
        - 超过 threshold_days 天未被检索
        """
        now = int(time.time())
        demoted = []

        memories = self.store.query(importance="medium", limit=500)
        for mem in memories:
            age_days = (now - mem.get("time_ts", now)) / 86400
            if age_days > threshold_days:
                mid = mem["memory_id"]
                # 检查最近是否被检索
                retrieval_count = 0
                if self.quality:
                    retrieval_count = self.quality._stats.get("retrievals", {}).get(mid, 0)

                if retrieval_count == 0:
                    demoted.append(mid)

        return demoted

    # ── 统计 ────────────────────────────────────────────

    def get_stats(self) -> dict:
        """各层级统计"""
        all_memories = self.store.query(limit=10000)

        l2_count = sum(1 for m in all_memories if m.get("importance") != "high")
        l3_count = sum(1 for m in all_memories if m.get("importance") == "high")

        return {
            "L1_short_term": {
                "count": len(self._l1_buffer),
                "capacity": self.L1_CAPACITY,
                "session_id": self._l1_session_id,
            },
            "L2_mid_term": {
                "count": l2_count,
                "capacity": self.L2_CAPACITY,
            },
            "L3_long_term": {
                "count": l3_count,
                "capacity": "unlimited",
            },
            "total": len(all_memories),
        }

    def generate_hierarchy_report(self) -> str:
        """生成层级记忆报告"""
        stats = self.get_stats()
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        lines = [
            "# 🏗️ 层级记忆报告",
            "",
            f"**生成时间**: {now_str}",
            "",
            "## 各层级状态",
            "",
            f"### L1 短期记忆 (对话级)",
            f"- 容量: {stats['L1_short_term']['count']}/{stats['L1_short_term']['capacity']}",
            f"- 会话: {stats['L1_short_term']['session_id']}",
            "",
            f"### L2 中期记忆 (天级)",
            f"- 容量: {stats['L2_mid_term']['count']}/{stats['L2_mid_term']['capacity']}",
            "",
            f"### L3 长期记忆 (永久)",
            f"- 容量: {stats['L3_long_term']['count']}/{stats['L3_long_term']['capacity']}",
            "",
            f"**总计**: {stats['total']} 条记忆",
        ]

        return "\n".join(lines)
