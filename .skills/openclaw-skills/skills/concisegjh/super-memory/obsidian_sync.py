"""
obsidian_sync.py - Obsidian 双向同步
记忆系统 ↔ Obsidian Vault (Markdown + Frontmatter)
"""

import os
import json
import time
import re
from datetime import datetime
from pathlib import Path


class ObsidianSync:
    """
    将 Agent Memory System 的数据同步到 Obsidian Vault。

    目录结构:
    vault/
    ├── 00-Inbox/           # 快速捕获
    ├── 01-Core-Memory/     # 核心记忆 (high importance)
    ├── 02-Episodes/        # 情节记忆 (按日期)
    ├── 03-Dialogues/       # 对话存档 (按主题)
    ├── 04-Knowledge/       # 知识库
    │   ├── Areas/          # 责任领域
    │   └── Resources/      # 资源
    ├── 05-Tasks/           # 待办任务
    ├── 06-Recording-Cards/ # 录音卡
    └── 07-Themes/          # 主题分类
    """

    NATURE_TO_FOLDER = {
        "D01": "00-Inbox",      # 碎片
        "D02": "02-Episodes",   # 日志
        "D03": "02-Episodes",   # 任务
        "D04": "02-Episodes",   # 探索
        "D05": "04-Knowledge",  # 笔记
        "D06": "04-Knowledge",  # 交付
        "D07": "05-Tasks",      # 待办
        "D08": "04-Knowledge/Archives",  # 典藏
        "D09": "02-Episodes",   # 回溯
        "D10": "00-Inbox",      # 配置
        "D11": "03-Dialogues",  # 漫谈
        "D12": "00-Inbox",      # 解惑
    }

    def __init__(self, store, encoder, vault_path: str):
        self.store = store
        self.encoder = encoder
        self.vault_path = Path(vault_path)

    def _ensure_dirs(self):
        """确保 Vault 目录结构存在"""
        dirs = [
            "00-Inbox", "01-Core-Memory", "02-Episodes",
            "03-Dialogues", "04-Knowledge/Areas", "04-Knowledge/Resources",
            "04-Knowledge/Archives", "05-Tasks", "06-Recording-Cards", "07-Themes",
        ]
        for d in dirs:
            (self.vault_path / d).mkdir(parents=True, exist_ok=True)

    def _make_frontmatter(self, memory: dict) -> str:
        """生成 YAML Frontmatter"""
        topics = memory.get("topics", [])
        topic_codes = []
        for t in topics:
            if isinstance(t, dict):
                topic_codes.append(t["code"])
            else:
                topic_codes.append(t)

        tools = memory.get("tools", [])
        knowledge = memory.get("knowledge", [])

        dt = datetime.fromtimestamp(memory.get("time_ts", time.time()))

        lines = ["---"]
        lines.append(f'id: "{memory.get("memory_id", "")}"')
        lines.append(f'type: memory')
        lines.append(f'nature: "{memory.get("nature_id", "")}"')
        lines.append(f'importance: "{memory.get("importance", "medium")}"')
        lines.append(f'created: {dt.strftime("%Y-%m-%dT%H:%M:%S")}')
        lines.append(f'person: "{memory.get("person_id", "")}"')

        if topic_codes:
            lines.append(f'topics: {json.dumps(topic_codes, ensure_ascii=False)}')
        if tools:
            lines.append(f'tools: {json.dumps(tools, ensure_ascii=False)}')
        if knowledge:
            lines.append(f'knowledge: {json.dumps(knowledge, ensure_ascii=False)}')

        # tags
        tags = ["memory"]
        if topic_codes:
            tags.append(topic_codes[0].replace(".", "-"))
        lines.append(f'tags: {json.dumps(tags, ensure_ascii=False)}')
        lines.append(f'source: agent-memory')
        lines.append("---")
        return "\n".join(lines)

    def _safe_filename(self, text: str, max_len: int = 50) -> str:
        """生成安全的文件名"""
        # 取内容前几个字
        clean = re.sub(r'[<>:"/\\|?*\n\r]', '', text)[:max_len].strip()
        if not clean:
            clean = f"memory_{int(time.time())}"
        return clean

    def export_memory(self, memory: dict) -> str:
        """
        导出单条记忆为 Obsidian Markdown 文件。

        返回: 写入的文件路径
        """
        self._ensure_dirs()

        nature_id = memory.get("nature_id", "D11")
        folder = self.NATURE_TO_FOLDER.get(nature_id, "00-Inbox")

        # 按日期分子目录（Episodes 和 Dialogues）
        if folder.startswith("02-") or folder.startswith("03-"):
            dt = datetime.fromtimestamp(memory.get("time_ts", time.time()))
            folder = f"{folder}/{dt.strftime('%Y-%m')}"

        dir_path = self.vault_path / folder
        dir_path.mkdir(parents=True, exist_ok=True)

        # 文件名
        time_id = memory.get("time_id", f"T{int(time.time())}")
        content_preview = self._safe_filename(memory.get("content", ""))
        filename = f"{time_id}_{content_preview}.md"

        filepath = dir_path / filename

        # 写入
        frontmatter = self._make_frontmatter(memory)
        body = memory.get("content", "")

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(frontmatter)
            f.write("\n\n")
            f.write(body)
            f.write("\n")

        return str(filepath)

    def export_batch(
        self,
        topic_path: str = None,
        importance: str = None,
        time_from: int = None,
        time_to: int = None,
        limit: int = 100,
    ) -> list[str]:
        """批量导出记忆到 Vault"""
        memories = self.store.query(
            topic_code=topic_path,
            importance=importance,
            time_from=time_from,
            time_to=time_to,
            limit=limit,
        )
        paths = []
        for mem in memories:
            p = self.export_memory(mem)
            paths.append(p)
        return paths

    def export_tasks(self) -> list[str]:
        """导出所有待办任务到 05-Tasks/"""
        self._ensure_dirs()
        tasks_dir = self.vault_path / "05-Tasks"
        tasks_dir.mkdir(parents=True, exist_ok=True)

        tasks = self.store.get_tasks(limit=200)
        paths = []

        status_labels = {
            "pending": "⬜",
            "in_progress": "🔄",
            "done": "✅",
            "overdue": "🔴",
        }

        for task in tasks:
            status = task.get("status", "pending")
            icon = status_labels.get(status, "❓")
            title = task.get("title", "Untitled")
            safe_title = self._safe_filename(title)

            filename = f"{icon}_{safe_title}.md"
            filepath = tasks_dir / filename

            dt_created = datetime.fromtimestamp(task.get("created_at", time.time()))
            lines = [
                "---",
                f'id: "{task.get("task_id", "")}"',
                f'type: task',
                f'status: "{status}"',
                f'assignee: "{task.get("assignee", "")}"',
                f'created: {dt_created.strftime("%Y-%m-%dT%H:%M:%S")}',
            ]
            if task.get("deadline"):
                dt_deadline = datetime.fromtimestamp(task["deadline"])
                lines.append(f'deadline: {dt_deadline.strftime("%Y-%m-%dT%H:%M:%S")}')
            if task.get("topic_code"):
                lines.append(f'topic: "{task["topic_code"]}"')
            lines.append('tags: [task]')
            lines.append('source: agent-memory')
            lines.append("---")
            lines.append("")
            lines.append(f"# {icon} {title}")
            lines.append("")
            lines.append(f"- **状态**: {status}")
            lines.append(f"- **负责人**: {task.get('assignee', '-')}")
            if task.get("topic_code"):
                lines.append(f"- **主题**: {task['topic_code']}")

            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            paths.append(str(filepath))

        return paths

    def export_theme_index(self) -> str:
        """生成主题索引文件 07-Themes/index.md"""
        self._ensure_dirs()
        themes_dir = self.vault_path / "07-Themes"
        themes_dir.mkdir(parents=True, exist_ok=True)

        # 查询所有主题分布
        all_topics = self.encoder.list_topics()
        lines = [
            "# 📚 主题索引",
            "",
            f"_更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}_",
            "",
        ]

        for topic in all_topics:
            count = len(self.store.query(topic_code=topic, limit=1000))
            if count > 0:
                lines.append(f"- [[{topic}]] ({count} 条)")

        index_path = themes_dir / "index.md"
        with open(index_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

        return str(index_path)

    def sync_all(self, limit: int = 200) -> dict:
        """
        全量同步到 Obsidian Vault。

        返回: {"memories": n, "tasks": n, "theme_index": bool}
        """
        self._ensure_dirs()

        mem_paths = self.export_batch(limit=limit)
        task_paths = self.export_tasks()
        theme_path = self.export_theme_index()

        return {
            "memories": len(mem_paths),
            "tasks": len(task_paths),
            "theme_index": True,
            "vault_path": str(self.vault_path),
        }

    def read_obsidian_file(self, filepath: str) -> dict | None:
        """
        读取一个 Obsidian Markdown 文件，解析 Frontmatter。
        用于双向同步（Vault → Memory System）。
        """
        if not os.path.exists(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # 解析 Frontmatter
        match = re.match(r'^---\n(.*?)\n---\n(.*)$', content, re.DOTALL)
        if not match:
            return {"content": content, "frontmatter": {}}

        fm_text = match.group(1)
        body = match.group(2).strip()

        # 简单 YAML 解析（支持 key: value 格式）
        frontmatter = {}
        for line in fm_text.split("\n"):
            if ":" in line:
                key, _, val = line.partition(":")
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if val.startswith("[") and val.endswith(""):
                    try:
                        val = json.loads(val)
                    except json.JSONDecodeError:
                        pass
                frontmatter[key] = val

        return {"content": body, "frontmatter": frontmatter}
