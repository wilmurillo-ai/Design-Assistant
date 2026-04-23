"""
store.py - SQLite 存储层
所有结构化维度的 CRUD 操作
并发安全 + FTS5 全文搜索 + 查询缓存
"""

import sqlite3
import threading
import hashlib
import time
import json
import logging
from pathlib import Path
from datetime import datetime
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "memory.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class MemoryStore:
    def __init__(self, db_path: str = None):
        self.db_path = str(db_path or DB_PATH)
        self._local = threading.local()
        self._lock = threading.Lock()
        self._query_cache: dict = {}
        self._cache_max_size = 200
        self._stats = {"reads": 0, "writes": 0, "cache_hits": 0, "cache_misses": 0}
        # 先初始化连接，再建表，再初始化 FTS
        _ = self.conn  # 触发连接创建
        self._ensure_schema()
        self._init_fts()

    @property
    def conn(self):
        """线程安全的连接获取"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
            self._local.conn.execute("PRAGMA journal_mode=WAL")
            self._local.conn.execute("PRAGMA foreign_keys=ON")
            self._local.conn.execute("PRAGMA synchronous=NORMAL")
            self._local.conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
            self._local.conn.execute("PRAGMA busy_timeout=5000")
        return self._local.conn

    @contextmanager
    def transaction(self):
        """原子事务上下文管理器"""
        conn = self.conn
        try:
            conn.execute("BEGIN")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    def _ensure_schema(self):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            schema = f.read()
        self.conn.executescript(schema)
        self.conn.commit()

    def _init_fts(self):
        """初始化 FTS5 全文搜索"""
        try:
            self.conn.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS memories_fts USING fts5(
                    memory_id UNINDEXED,
                    content,
                    tokenize='unicode61 remove_diacritics 2'
                )
            """)
            # 检查是否需要初始同步
            count = self.conn.execute("SELECT COUNT(*) FROM memories_fts").fetchone()[0]
            mem_count = self.conn.execute("SELECT COUNT(*) FROM memories").fetchone()[0]
            if count < mem_count:
                logger.info(f"FTS 同步: {mem_count - count} 条记忆")
                self.conn.execute("""
                    INSERT OR IGNORE INTO memories_fts(memory_id, content)
                    SELECT memory_id, content FROM memories
                """)
            self.conn.commit()
            self._has_fts = True
        except Exception as e:
            logger.warning(f"FTS5 不可用: {e}")
            self._has_fts = False

    def _invalidate_cache(self):
        """写入时清除缓存"""
        with self._lock:
            self._query_cache.clear()

    def _cache_get(self, key: str):
        with self._lock:
            self._stats["reads"] += 1
            if key in self._query_cache:
                self._stats["cache_hits"] += 1
                return self._query_cache[key]
            self._stats["cache_misses"] += 1
            return None

    def _cache_set(self, key: str, value):
        with self._lock:
            if len(self._query_cache) >= self._cache_max_size:
                # LRU: 删最旧的 25%
                keys = list(self._query_cache.keys())
                for k in keys[:self._cache_max_size // 4]:
                    del self._query_cache[k]
            self._query_cache[key] = value

    # ── 写入 ──────────────────────────────────────────────

    def insert_memory(
        self,
        memory_id: str,
        time_id: str,
        time_ts: int,
        person_id: str,
        nature_id: str,
        content: str,
        content_hash: str,
        topics: list[str] = None,
        tools: list[str] = None,
        knowledge_types: list[str] = None,
        importance: str = "medium",
        is_aggregated: bool = False,
        source_count: int = 1,
    ) -> str:
        """写入一条记忆记录，返回 memory_id（原子写入）"""
        with self.transaction() as conn:
            self._stats["writes"] += 1
            conn.execute(
                """INSERT OR IGNORE INTO memories
                   (memory_id, time_id, time_ts, person_id, nature_id,
                    content, content_hash, importance, is_aggregated, source_count)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (memory_id, time_id, time_ts, person_id, nature_id,
                 content, content_hash, importance, int(is_aggregated), source_count),
            )

            if topics:
                for i, topic in enumerate(topics):
                    conn.execute(
                        """INSERT OR IGNORE INTO memory_topics (memory_id, topic_code, is_primary)
                           VALUES (?, ?, ?)""",
                        (memory_id, topic, 1 if i == 0 else 0),
                    )

            if tools:
                for tool_id in tools:
                    conn.execute(
                        """INSERT OR IGNORE INTO memory_tools (memory_id, tool_id)
                           VALUES (?, ?)""",
                        (memory_id, tool_id),
                    )

            if knowledge_types:
                for kid in knowledge_types:
                    conn.execute(
                        """INSERT OR IGNORE INTO memory_knowledge (memory_id, knowledge_id)
                           VALUES (?, ?)""",
                        (memory_id, kid),
                    )

            # 同步 FTS
            if self._has_fts:
                conn.execute(
                    "INSERT OR IGNORE INTO memories_fts(memory_id, content) VALUES (?, ?)",
                    (memory_id, content),
                )

        self._invalidate_cache()
        return memory_id

    def insert_link(
        self,
        source_id: str,
        target_id: str,
        link_type: str,
        weight: float = 1.0,
        reason: str = None,
    ):
        """插入一条关联关系"""
        with self.transaction() as conn:
            conn.execute(
                """INSERT INTO memory_links (source_id, target_id, link_type, weight, reason)
                   VALUES (?, ?, ?, ?, ?)""",
                (source_id, target_id, link_type, weight, reason),
            )
        self._invalidate_cache()

    # ── 查询 ──────────────────────────────────────────────

    def get_memory(self, memory_id: str) -> dict | None:
        row = self.conn.execute(
            "SELECT * FROM memories WHERE memory_id = ?", (memory_id,)
        ).fetchone()
        if not row:
            return None
        mem = dict(row)
        mem["topics"] = self._get_topics(memory_id)
        mem["tools"] = self._get_tools(memory_id)
        mem["knowledge"] = self._get_knowledge(memory_id)
        mem["links"] = self._get_links(memory_id)
        return mem

    def query(
        self,
        time_from: int = None,
        time_to: int = None,
        person_id: str = None,
        nature_id: str = None,
        topic_code: str = None,
        tool_id: str = None,
        knowledge_id: str = None,
        importance: str = None,
        keyword: str = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        """多维度结构化查询（带缓存 + FTS 加速）"""

        # 缓存键
        cache_key = f"q:{time_from}:{time_to}:{person_id}:{nature_id}:{topic_code}:{tool_id}:{knowledge_id}:{importance}:{keyword}:{limit}:{offset}"
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        # FTS 加速关键词搜索
        if keyword and self._has_fts and not any([time_from, time_to, person_id, nature_id, topic_code, tool_id, knowledge_id, importance]):
            results = self._query_fts(keyword, limit)
            self._cache_set(cache_key, results)
            return results

        conditions = []
        params = []

        if time_from is not None:
            conditions.append("m.time_ts >= ?")
            params.append(time_from)
        if time_to is not None:
            conditions.append("m.time_ts <= ?")
            params.append(time_to)
        if person_id:
            conditions.append("m.person_id = ?")
            params.append(person_id)
        if nature_id:
            conditions.append("m.nature_id = ?")
            params.append(nature_id)
        if importance:
            conditions.append("m.importance = ?")
            params.append(importance)
        if keyword:
            # 同时尝试 FTS 和 LIKE
            if self._has_fts:
                fts_results = self._query_fts(keyword, limit * 2)
                fts_ids = [r["memory_id"] for r in fts_results]
                if fts_ids:
                    placeholders = ",".join("?" * len(fts_ids))
                    conditions.append(f"m.memory_id IN ({placeholders})")
                    params.extend(fts_ids)
                else:
                    conditions.append("m.content LIKE ?")
                    params.append(f"%{keyword}%")
            else:
                conditions.append("m.content LIKE ?")
                params.append(f"%{keyword}%")

        where = " AND ".join(conditions) if conditions else "1=1"

        sql = f"""
            SELECT DISTINCT m.* FROM memories m
            {"JOIN memory_topics mt ON m.memory_id = mt.memory_id" if topic_code else ""}
            {"JOIN memory_tools mt2 ON m.memory_id = mt2.memory_id" if tool_id else ""}
            {"JOIN memory_knowledge mk ON m.memory_id = mk.memory_id" if knowledge_id else ""}
            WHERE {where}
            {"AND mt.topic_code LIKE ?" if topic_code else ""}
            {"AND mt2.tool_id = ?" if tool_id else ""}
            {"AND mk.knowledge_id = ?" if knowledge_id else ""}
            ORDER BY m.time_ts DESC
            LIMIT ? OFFSET ?
        """
        if topic_code:
            params.append(topic_code + "%")
        if tool_id:
            params.append(tool_id)
        if knowledge_id:
            params.append(knowledge_id)
        params.extend([limit, offset])

        rows = self.conn.execute(sql, params).fetchall()
        results = []
        for row in rows:
            mem = dict(row)
            mem["topics"] = self._get_topics(mem["memory_id"])
            mem["tools"] = self._get_tools(mem["memory_id"])
            mem["knowledge"] = self._get_knowledge(mem["memory_id"])
            results.append(mem)

        self._cache_set(cache_key, results)
        return results

    def _query_fts(self, keyword: str, limit: int) -> list[dict]:
        """FTS5 全文搜索"""
        try:
            # FTS5 查询语法：转义特殊字符
            safe_keyword = keyword.replace('"', '""')
            rows = self.conn.execute(
                """SELECT m.* FROM memories m
                   JOIN memories_fts fts ON m.memory_id = fts.memory_id
                   WHERE memories_fts MATCH ?
                   ORDER BY rank
                   LIMIT ?""",
                (f'"{safe_keyword}"', limit),
            ).fetchall()
            return [dict(r) for r in rows]
        except Exception:
            return []

    def get_linked(self, memory_id: str, link_type: str = None, max_depth: int = 1) -> list[dict]:
        """获取关联记录，支持多层深度"""
        visited = set()
        results = []

        def _traverse(current_id, depth, weight):
            if depth > max_depth or current_id in visited:
                return
            visited.add(current_id)

            conditions = ["(source_id = ? OR target_id = ?)"]
            params = [current_id, current_id]
            if link_type:
                conditions.append("link_type = ?")
                params.append(link_type)

            links = self.conn.execute(
                f"SELECT * FROM memory_links WHERE {' AND '.join(conditions)}",
                params,
            ).fetchall()

            for link in links:
                target = link["target_id"] if link["source_id"] == current_id else link["source_id"]
                if target not in visited:
                    mem = self.get_memory(target)
                    if mem:
                        mem["_link_weight"] = weight * link["weight"]
                        mem["_link_type"] = link["link_type"]
                        mem["_link_depth"] = depth
                        results.append(mem)
                    _traverse(target, depth + 1, weight * link["weight"])

        _traverse(memory_id, 1, 1.0)
        return results

    # ── 待办任务管理 ──────────────────────────────────────

    def add_task(
        self,
        memory_id: str,
        title: str,
        assignee: str = "ai",
        deadline: int = None,
        topic_code: str = None,
    ) -> str:
        """添加一个待办任务，返回 task_id"""
        raw = f"{memory_id}_{title}_{time.time()}"
        task_id = "task_" + hashlib.sha256(raw.encode()).hexdigest()[:12]

        with self.transaction() as conn:
            conn.execute(
                """INSERT INTO tasks (task_id, memory_id, title, status, assignee, deadline, topic_code)
                   VALUES (?, ?, ?, 'pending', ?, ?, ?)""",
                (task_id, memory_id, title, assignee, deadline, topic_code),
            )
        self._invalidate_cache()
        return task_id

    def update_task_status(self, task_id: str, status: str) -> bool:
        """更新任务状态"""
        valid = {"pending", "in_progress", "done", "overdue"}
        if status not in valid:
            raise ValueError(f"无效状态: {status}，可选: {valid}")

        now = int(time.time())
        params = [status, now]
        sql = "UPDATE tasks SET status = ?, updated_at = ?"

        if status == "done":
            sql += ", completed_at = ?"
            params.append(now)

        sql += " WHERE task_id = ?"
        params.append(task_id)

        with self.transaction() as conn:
            cur = conn.execute(sql, params)
        self._invalidate_cache()
        return cur.rowcount > 0

    def get_tasks(
        self,
        status: str = None,
        assignee: str = None,
        topic_code: str = None,
        overdue_only: bool = False,
        limit: int = 50,
    ) -> list[dict]:
        """查询任务列表"""
        conditions = []
        params = []

        if status:
            conditions.append("t.status = ?")
            params.append(status)
        if assignee:
            conditions.append("t.assignee = ?")
            params.append(assignee)
        if topic_code:
            conditions.append("t.topic_code LIKE ?")
            params.append(topic_code + "%")
        if overdue_only:
            conditions.append("t.deadline < ? AND t.status NOT IN ('done', 'overdue')")
            params.append(int(time.time()))

        where = " AND ".join(conditions) if conditions else "1=1"

        rows = self.conn.execute(
            f"""SELECT t.*, m.content as memory_content
                FROM tasks t
                LEFT JOIN memories m ON t.memory_id = m.memory_id
                WHERE {where}
                ORDER BY
                    CASE t.status
                        WHEN 'overdue' THEN 0
                        WHEN 'pending' THEN 1
                        WHEN 'in_progress' THEN 2
                        WHEN 'done' THEN 3
                    END,
                    t.created_at DESC
                LIMIT ?""",
            params + [limit],
        ).fetchall()
        return [dict(r) for r in rows]

    def check_overdue(self) -> list[dict]:
        """检查并标记超时任务，返回被标记的列表"""
        now = int(time.time())
        rows = self.conn.execute(
            """SELECT task_id FROM tasks
               WHERE deadline < ? AND status IN ('pending', 'in_progress')""",
            (now,),
        ).fetchall()

        overdue_ids = [r["task_id"] for r in rows]
        if overdue_ids:
            with self.transaction() as conn:
                for tid in overdue_ids:
                    conn.execute(
                        "UPDATE tasks SET status = 'overdue', updated_at = ? WHERE task_id = ?",
                        (now, tid),
                    )

        result = []
        for tid in overdue_ids:
            row = self.conn.execute("SELECT * FROM tasks WHERE task_id = ?", (tid,)).fetchone()
            if row:
                result.append(dict(row))
        return result

    def get_task_stats(self) -> dict:
        """返回任务统计"""
        rows = self.conn.execute(
            "SELECT status, COUNT(*) as cnt FROM tasks GROUP BY status"
        ).fetchall()
        stats = {r["status"]: r["cnt"] for r in rows}
        stats["total"] = sum(stats.values())
        return stats

    # ── 内部方法 ──────────────────────────────────────────

    def _get_topics(self, memory_id: str) -> list[dict]:
        rows = self.conn.execute(
            "SELECT topic_code, is_primary FROM memory_topics WHERE memory_id = ?",
            (memory_id,),
        ).fetchall()
        return [{"code": r["topic_code"], "is_primary": bool(r["is_primary"])} for r in rows]

    def _get_tools(self, memory_id: str) -> list[str]:
        rows = self.conn.execute(
            "SELECT tool_id FROM memory_tools WHERE memory_id = ?", (memory_id,)
        ).fetchall()
        return [r["tool_id"] for r in rows]

    def _get_knowledge(self, memory_id: str) -> list[str]:
        rows = self.conn.execute(
            "SELECT knowledge_id FROM memory_knowledge WHERE memory_id = ?", (memory_id,)
        ).fetchall()
        return [r["knowledge_id"] for r in rows]

    def _get_links(self, memory_id: str) -> list[dict]:
        rows = self.conn.execute(
            """SELECT * FROM memory_links
               WHERE source_id = ? OR target_id = ?""",
            (memory_id, memory_id),
        ).fetchall()
        return [dict(r) for r in rows]

    def close(self):
        if hasattr(self._local, 'conn') and self._local.conn:
            self._local.conn.close()
            self._local.conn = None

    def get_io_stats(self) -> dict:
        """IO 统计"""
        with self._lock:
            stats = dict(self._stats)
        total = stats["reads"] + stats["cache_misses"]
        stats["cache_hit_rate"] = stats["cache_hits"] / total if total > 0 else 0
        stats["has_fts"] = self._has_fts
        return stats

    def optimize(self):
        """数据库优化：VACUUM + ANALYZE + FTS 重建"""
        logger.info("数据库优化中...")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("ANALYZE")
            conn.execute("PRAGMA optimize")
        logger.info("数据库优化完成")

    def backup(self, backup_path: str):
        """原子备份"""
        import shutil
        tmp = backup_path + ".tmp"
        shutil.copy2(self.db_path, tmp)
        import os
        os.replace(tmp, backup_path)
        logger.info(f"备份完成: {backup_path}")

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
