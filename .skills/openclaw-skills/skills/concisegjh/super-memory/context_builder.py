"""
context_builder.py - Agent 上下文组装器
把检索结果格式化为结构化的系统提示词片段，直接拼入 Agent prompt
"""

import time
from datetime import datetime
from recall import RecallEngine


class ContextBuilder:
    """
    将记忆检索结果组装成 Agent 可用的上下文。

    核心能力：
    1. Token 预算控制 — 不超过模型上下文窗口
    2. 多策略组装 — 按场景选择不同格式
    3. 时间衰减感知 — 越近越详细，越远越简略
    4. 分层输出 — 高优先单独列出，普通记忆合并
    """

    # token 估算：中文 ≈ 1.5 token/字，英文 ≈ 1.3 token/词
    CN_TOKEN_RATIO = 1.5
    EN_TOKEN_RATIO = 1.3

    def __init__(self, recall_engine: RecallEngine):
        self.recall = recall_engine

    def build(
        self,
        query: str = None,
        topic: str = None,
        max_tokens: int = 2000,
        style: str = "structured",
        include_tasks: bool = True,
        include_decay: bool = False,
    ) -> dict:
        """
        组装上下文。

        参数:
            query: 用户当前查询（语义检索用）
            topic: 指定主题过滤
            max_tokens: token 预算上限
            style: 组装风格
                - "structured": 分类结构化（默认）
                - "narrative": 自然语言叙述
                - "compact": 极简一行一条
                - "xml": XML 标签格式（适合某些模型）
            include_tasks: 是否包含待办任务
            include_decay: 是否显示衰减信息

        返回:
        {
            "context": str,           # 组装好的上下文文本
            "token_estimate": int,    # 估算 token 数
            "memory_count": int,      # 包含的记忆条数
            "truncated": bool,        # 是否被截断
            "sources": [str],         # 包含的 memory_id 列表
        }
        """
        # 检索
        result = self.recall.recall(
            query=query,
            topic_path=topic,
            limit=20,
        )

        memories = result.get("primary", [])
        related = result.get("related", [])

        if not memories:
            return {
                "context": "",
                "token_estimate": 0,
                "memory_count": 0,
                "truncated": False,
                "sources": [],
            }

        # 分层
        high_priority = [m for m in memories if m.get("importance") == "high"]
        normal = [m for m in memories if m.get("importance") != "high"]

        # 按风格组装
        if style == "structured":
            text = self._build_structured(high_priority, normal, related, include_tasks, include_decay)
        elif style == "narrative":
            text = self._build_narrative(memories, related)
        elif style == "compact":
            text = self._build_compact(memories)
        elif style == "xml":
            text = self._build_xml(high_priority, normal, related)
        else:
            text = self._build_structured(high_priority, normal, related, include_tasks, include_decay)

        # Token 控制
        truncated = False
        if self._estimate_tokens(text) > max_tokens:
            text = self._truncate_to_tokens(text, max_tokens)
            truncated = True

        sources = [m.get("memory_id", "") for m in memories[:10]]

        return {
            "context": text,
            "token_estimate": self._estimate_tokens(text),
            "memory_count": len(memories),
            "truncated": truncated,
            "sources": sources,
        }

    def _build_structured(self, high: list, normal: list, related: list, include_tasks: bool, include_decay: bool) -> str:
        """结构化风格：分类分组"""
        lines = ["# 相关记忆", ""]

        # 高优先单独列出
        if high:
            lines.append("## ⚡ 关键记忆")
            for m in high:
                line = self._format_memory_line(m, include_decay)
                lines.append(f"- {line}")
            lines.append("")

        # 普通记忆按主题分组
        if normal:
            by_topic = {}
            for m in normal:
                topics = m.get("topics", [])
                key = topics[0].get("code", "misc") if topics else "misc"
                if key not in by_topic:
                    by_topic[key] = []
                by_topic[key].append(m)

            lines.append("## 📝 相关记录")
            for topic, mems in sorted(by_topic.items()):
                lines.append(f"**{topic}**:")
                for m in mems[:5]:
                    line = self._format_memory_line(m, include_decay)
                    lines.append(f"  - {line}")
            lines.append("")

        # 待办任务
        if include_tasks:
            tasks = self._get_related_tasks(normal)
            if tasks:
                lines.append("## 📋 相关待办")
                for t in tasks[:5]:
                    icon = {"pending": "⬜", "in_progress": "🔄", "done": "✅", "overdue": "🔴"}.get(t["status"], "❓")
                    lines.append(f"- {icon} {t['title'][:60]}")
                lines.append("")

        # 关联记录（简略）
        if related:
            lines.append("## 🔗 上下文关联")
            for r in related[:3]:
                content = r.get("content", "")[:50]
                link = r.get("_link_type", "")
                lines.append(f"- [{link}] {content}")
            lines.append("")

        return "\n".join(lines)

    def _build_narrative(self, memories: list, related: list) -> str:
        """叙述风格：自然语言段落"""
        lines = ["关于这个话题，你之前有以下记忆：", ""]

        for m in memories[:8]:
            dt = self._format_time(m.get("time_ts", 0))
            content = m.get("content", "")[:100]
            imp = m.get("importance", "medium")
            prefix = "（重要）" if imp == "high" else ""
            lines.append(f"{dt}，你记录了{prefix}：{content}")

        if related:
            lines.append("")
            lines.append("此外相关联的还有：")
            for r in related[:3]:
                lines.append(f"- {r.get('content', '')[:60]}")

        return "\n".join(lines)

    def _build_compact(self, memories: list) -> str:
        """极简风格：一行一条"""
        lines = []
        for m in memories[:10]:
            dt = self._format_time_short(m.get("time_ts", 0))
            content = m.get("content", "")[:60]
            imp_icon = "⚡" if m.get("importance") == "high" else ""
            lines.append(f"{imp_icon}[{dt}] {content}")
        return "\n".join(lines)

    def _build_xml(self, high: list, normal: list, related: list) -> str:
        """XML 标签风格（适合 Claude 等模型）"""
        parts = ["<memory_context>"]

        if high:
            parts.append("  <critical_memories>")
            for m in high:
                content = self._escape_xml(m.get("content", "")[:200])
                dt = self._format_time(m.get("time_ts", 0))
                parts.append(f'    <memory date="{dt}" importance="high">{content}</memory>')
            parts.append("  </critical_memories>")

        if normal:
            parts.append("  <related_memories>")
            for m in normal[:8]:
                content = self._escape_xml(m.get("content", "")[:150])
                dt = self._format_time(m.get("time_ts", 0))
                imp = m.get("importance", "medium")
                parts.append(f'    <memory date="{dt}" importance="{imp}">{content}</memory>')
            parts.append("  </related_memories>")

        parts.append("</memory_context>")
        return "\n".join(parts)

    def _format_memory_line(self, mem: dict, include_decay: bool = False) -> str:
        """格式化单条记忆为列表项"""
        content = mem.get("content", "")[:80]
        dt = self._format_time_short(mem.get("time_ts", 0))

        tags = []
        if mem.get("importance") == "high":
            tags.append("⚡")
        if include_decay and mem.get("_decay_score") is not None:
            score = mem["_decay_score"]
            if score < 0.3:
                tags.append("⏳旧")

        tag_str = "".join(tags)
        return f"{tag_str}[{dt}] {content}"

    def _get_related_tasks(self, memories: list) -> list:
        """获取与记忆相关的待办任务"""
        try:
            store = self.recall.store
            return store.get_tasks(limit=5)
        except Exception:
            return []

    @staticmethod
    def _format_time(ts: int) -> str:
        if not ts:
            return "?"
        return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")

    @staticmethod
    def _format_time_short(ts: int) -> str:
        if not ts:
            return "?"
        dt = datetime.fromtimestamp(ts)
        now = datetime.now()
        if dt.date() == now.date():
            return dt.strftime("%H:%M")
        return dt.strftime("%m-%d")

    @staticmethod
    def _escape_xml(text: str) -> str:
        return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def _estimate_tokens(self, text: str) -> int:
        """粗略估算 token 数"""
        cn_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        en_words = len(text.split()) - cn_chars
        return int(cn_chars * self.CN_TOKEN_RATIO + en_words * self.EN_TOKEN_RATIO)

    def _truncate_to_tokens(self, text: str, max_tokens: int) -> str:
        """截断到指定 token 数"""
        lines = text.split("\n")
        result = []
        current_tokens = 0

        for line in lines:
            line_tokens = self._estimate_tokens(line)
            if current_tokens + line_tokens > max_tokens:
                result.append("...（已截断）")
                break
            result.append(line)
            current_tokens += line_tokens

        return "\n".join(result)

    def build_system_prompt(
        self,
        agent_name: str = "AI",
        query: str = None,
        max_tokens: int = 1500,
        base_prompt: str = None,
    ) -> str:
        """
        直接生成完整的系统提示词（基础 prompt + 记忆上下文）。

        参数:
            agent_name: Agent 名称
            query: 当前对话上下文（用于语义检索）
            max_tokens: 记忆部分的 token 上限
            base_prompt: 基础系统提示词

        返回: 完整的 system prompt
        """
        ctx = self.build(query=query, max_tokens=max_tokens, style="structured")

        parts = []
        if base_prompt:
            parts.append(base_prompt)
            parts.append("")

        if ctx["context"]:
            parts.append(ctx["context"])
            parts.append("")
            parts.append(f"（以上为记忆系统自动检索，共 {ctx['memory_count']} 条相关记录）")

        return "\n".join(parts)
