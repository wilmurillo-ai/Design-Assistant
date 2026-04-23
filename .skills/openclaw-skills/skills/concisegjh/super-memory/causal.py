"""
causal.py - 记忆因果链
追踪记忆之间的因果关系：哪些记忆影响了哪些决策
"""

import time
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class CausalChain:
    """
    因果关系类型：
    1. decision_based_on — 决策基于某条记忆
    2. led_to — 某条记忆导致了某个结果
    3. contradicts — 两条记忆矛盾
    4. supports — 互相印证
    5. evolved_from — 概念演进（旧认知 → 新认知）

    自动发现 + 手动标注
    """

    CAUSAL_LINK_TYPES = {
        "decision_based_on": {"weight": 0.9, "icon": "🎯→", "desc": "决策依据"},
        "led_to":            {"weight": 0.8, "icon": "→🌱", "desc": "导致结果"},
        "contradicts":       {"weight": 0.3, "icon": "⚡",  "desc": "互相矛盾"},
        "supports":          {"weight": 0.7, "icon": "🤝",  "desc": "互相印证"},
        "evolved_from":      {"weight": 0.6, "icon": "🔄",  "desc": "概念演进"},
    }

    def __init__(self, store):
        self.store = store

    def add_causal_link(
        self,
        source_id: str,
        target_id: str,
        link_type: str,
        explanation: str = None,
    ) -> dict:
        """
        手动添加因果关系。

        参数:
            source_id: 原因记忆 ID
            target_id: 结果记忆 ID
            link_type: decision_based_on / led_to / contradicts / supports / evolved_from
            explanation: 因果解释
        """
        if link_type not in self.CAUSAL_LINK_TYPES:
            raise ValueError(f"无效因果类型: {link_type}，可选: {list(self.CAUSAL_LINK_TYPES.keys())}")

        config = self.CAUSAL_LINK_TYPES[link_type]

        self.store.insert_link(
            source_id=source_id,
            target_id=target_id,
            link_type=f"causal.{link_type}",
            weight=config["weight"],
            reason=explanation or config["desc"],
        )

        logger.info(f"🔗 因果链: {source_id} {config['icon']} {target_id} ({link_type})")
        return {
            "source": source_id,
            "target": target_id,
            "link_type": link_type,
            "weight": config["weight"],
        }

    def auto_detect_causality(self, window_hours: int = 24) -> list[dict]:
        """
        自动检测因果关系（启发式）。

        规则：
        1. 先有 explore/ask，后有 decision → decision_based_on
        2. 先有 todo，后有 output → led_to
        3. 同主题但结论矛盾 → contradicts
        4. 同主题且结论一致 → supports

        参数:
            window_hours: 检测时间窗口
        """
        import time
        now = int(time.time())
        window_start = now - window_hours * 3600

        memories = self.store.query(limit=200)
        memories = [m for m in memories if m.get("time_ts", 0) >= window_start]
        memories.sort(key=lambda m: m.get("time_ts", 0))

        detected = []

        for i, mem_a in enumerate(memories):
            for mem_b in memories[i+1:]:
                # 检查时间窗口（两小时内）
                time_gap = mem_b.get("time_ts", 0) - mem_a.get("time_ts", 0)
                if time_gap > 7200:  # 2 小时
                    continue

                # 检查是否同主题
                topics_a = {t.get("code", "") if isinstance(t, dict) else t for t in mem_a.get("topics", [])}
                topics_b = {t.get("code", "") if isinstance(t, dict) else t for t in mem_b.get("topics", [])}
                shared_topics = topics_a & topics_b

                if not shared_topics:
                    continue

                # 推断因果类型
                nature_a = mem_a.get("nature_id", "")
                nature_b = mem_b.get("nature_id", "")

                link_type = None
                explanation = None

                # explore/ask → decision/task/output
                if nature_a in ("D04", "D12") and nature_b in ("D03", "D06", "D07"):
                    link_type = "decision_based_on"
                    explanation = f"探索后的决策 ({nature_a}→{nature_b})"

                # todo → output
                elif nature_a == "D07" and nature_b == "D06":
                    link_type = "led_to"
                    explanation = "待办导致产出"

                # 同性质的 note 互相印证
                elif nature_a == nature_b == "D05":
                    link_type = "supports"
                    explanation = "同类型笔记互相印证"

                if link_type:
                    link = self.add_causal_link(
                        mem_a["memory_id"],
                        mem_b["memory_id"],
                        link_type,
                        explanation,
                    )
                    detected.append(link)

        logger.info(f"🔍 自动检测到 {len(detected)} 条因果关系")
        return detected

    def get_causal_chain(self, memory_id: str, max_depth: int = 3) -> dict:
        """
        获取一条记忆的完整因果链。

        返回:
        {
            "root": memory_id,
            "caused_by": [...],    # 原因链（向上追溯）
            "led_to": [...],       # 结果链（向下展开）
            "contradictions": [...],  # 矛盾项
            "chain_depth": int,
        }
        """
        caused_by = self._traverse_causality(memory_id, direction="up", max_depth=max_depth)
        led_to = self._traverse_causality(memory_id, direction="down", max_depth=max_depth)
        contradictions = self._find_contradictions(memory_id)

        return {
            "root": memory_id,
            "caused_by": caused_by,
            "led_to": led_to,
            "contradictions": contradictions,
            "chain_depth": max(
                max((c.get("_depth", 0) for c in caused_by), default=0),
                max((c.get("_depth", 0) for c in led_to), default=0),
            ),
        }

    def _traverse_causality(self, memory_id: str, direction: str, max_depth: int) -> list[dict]:
        """遍历因果链"""
        visited = set()
        results = []

        def _walk(current_id, depth):
            if depth > max_depth or current_id in visited:
                return
            visited.add(current_id)

            if direction == "up":
                # 找"导致 current"的记忆（target=current）
                links = self.store.conn.execute(
                    """SELECT * FROM memory_links
                       WHERE target_id = ? AND link_type LIKE 'causal.%'""",
                    (current_id,),
                ).fetchall()
            else:
                # 找"被 current 导致"的记忆（source=current）
                links = self.store.conn.execute(
                    """SELECT * FROM memory_links
                       WHERE source_id = ? AND link_type LIKE 'causal.%'""",
                    (current_id,),
                ).fetchall()

            for link in links:
                related_id = link["source_id"] if direction == "up" else link["target_id"]
                if related_id not in visited:
                    mem = self.store.get_memory(related_id)
                    if mem:
                        causal_type = link["link_type"].replace("causal.", "")
                        config = self.CAUSAL_LINK_TYPES.get(causal_type, {})
                        mem["_causal_type"] = causal_type
                        mem["_causal_icon"] = config.get("icon", "→")
                        mem["_causal_desc"] = config.get("desc", "")
                        mem["_depth"] = depth
                        results.append(mem)
                    _walk(related_id, depth + 1)

        _walk(memory_id, 1)
        return results

    def _find_contradictions(self, memory_id: str) -> list[dict]:
        """找到与指定记忆矛盾的记录"""
        links = self.store.conn.execute(
            """SELECT * FROM memory_links
               WHERE (source_id = ? OR target_id = ?)
               AND link_type = 'causal.contradicts'""",
            (memory_id, memory_id),
        ).fetchall()

        results = []
        for link in links:
            other_id = link["target_id"] if link["source_id"] == memory_id else link["source_id"]
            mem = self.store.get_memory(other_id)
            if mem:
                results.append(mem)
        return results

    def format_causal_chain(self, chain: dict) -> str:
        """格式化因果链为可读文本"""
        lines = []
        root_id = chain["root"][:30]

        if chain["caused_by"]:
            lines.append("⬆️ 原因链:")
            for m in chain["caused_by"]:
                indent = "  " * m.get("_depth", 1)
                icon = m.get("_causal_icon", "→")
                content = m.get("content", "")[:50]
                lines.append(f"{indent}{icon} {content}")

        lines.append(f"🎯 当前: {root_id}...")

        if chain["led_to"]:
            lines.append("⬇️ 结果链:")
            for m in chain["led_to"]:
                indent = "  " * m.get("_depth", 1)
                icon = m.get("_causal_icon", "→")
                content = m.get("content", "")[:50]
                lines.append(f"{indent}{icon} {content}")

        if chain["contradictions"]:
            lines.append("⚡ 矛盾项:")
            for m in chain["contradictions"]:
                lines.append(f"  ⚡ {m.get('content', '')[:50]}")

        return "\n".join(lines) if lines else "无因果链"

    def get_stats(self) -> dict:
        """因果关系统计"""
        rows = self.store.conn.execute(
            """SELECT link_type, COUNT(*) as cnt
               FROM memory_links
               WHERE link_type LIKE 'causal.%'
               GROUP BY link_type"""
        ).fetchall()

        by_type = {}
        for r in rows:
            causal_type = r["link_type"].replace("causal.", "")
            by_type[causal_type] = r["cnt"]

        return {
            "total_causal_links": sum(by_type.values()),
            "by_type": by_type,
        }
