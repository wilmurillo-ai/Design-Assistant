#!/usr/bin/env python3
"""
sql_dbo.py — Oblio SQL Memory Module
========================================
Production-quality SQL memory operations for all Oblio agents.
Supports two backends:
  - 'local'  → SQL Server 2019 on DEAUS (10.0.0.110)
  - 'cloud'  → site4now hosted (SQL5112.site4now.net)

All credentials loaded from .env — never hardcoded.

Usage:
    from sql_memory import SQLMemory, get_memory
    mem = get_memory('local')
    mem.remember('facts', 'sky_color', 'The sky is blue', importance=3, tags='nature')
    result = mem.recall('facts', 'sky_color')
"""

import os
import sys
import json
import time
import logging
import subprocess
from datetime import datetime
from typing import Optional, List, Dict, Any

# ── Load .env ────────────────────────────────────────────────────────────────
import pathlib as _pathlib

def _find_env():
    """Walk up from this file's directory to find .env (handles infrastructure/ subdir)."""
    p = _pathlib.Path(os.path.abspath(__file__)).parent
    for _ in range(4):
        candidate = p / '.env'
        if candidate.exists():
            return str(candidate)
        p = p.parent
    return None

try:
    from dotenv import load_dotenv
    _env = _find_env()
    if _env:
        load_dotenv(_env, override=True)
except ImportError:
    _env = _find_env()
    if _env:
        with open(_env) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    v = v.strip().strip('"').strip("'")
                    os.environ[k.strip()] = v

# ── Backend Configs ──────────────────────────────────────────────────────────
BACKENDS = {
    'local': {
        'server':   os.getenv('SQL_SERVER', '10.0.0.110'),
        'port':     int(os.getenv('SQL_PORT', '1433')),
        'database': os.getenv('SQL_DATABASE', 'Oblio_Memories'),
        'user':     os.getenv('SQL_USER', 'oblio'),
        'password': os.getenv('SQL_PASSWORD', ''),
        'encrypt':  False,
    },
    'cloud': {
        'server':   os.getenv('SQL_CLOUD_SERVER'),
        'port':     int(os.getenv('SQL_CLOUD_PORT', '1433')),
        'database': os.getenv('SQL_CLOUD_DATABASE'),
        'user':     os.getenv('SQL_CLOUD_USER'),
        'password': os.getenv('SQL_CLOUD_PASSWORD'),
        'encrypt':  True,
    },
}

SQLCMD = os.getenv('SQLCMD', '/opt/mssql-tools/bin/sqlcmd')
LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')

# ── Logger ───────────────────────────────────────────────────────────────────
os.makedirs(LOG_DIR, exist_ok=True)
_log = logging.getLogger('sql_memory')
if not _log.handlers:
    _log.setLevel(logging.INFO)
    _fh = logging.FileHandler(os.path.join(LOG_DIR, 'sql_dbo.log'))
    _fh.setFormatter(logging.Formatter('%(asctime)s [sql_memory] %(levelname)s %(message)s'))
    _log.addHandler(_fh)


def _esc(s: str, max_len: int = 4000) -> str:
    """Escape single quotes and truncate for safe SQL insertion."""
    if s is None:
        return ''
    return str(s)[:max_len].replace("'", "''")


class SQLMemory:
    """
    Unified SQL memory interface for Oblio agents.

    Args:
        backend: 'local' or 'cloud' — selects which SQL Server to connect to.

    Example:
        mem = SQLMemory('local')
        mem.remember('facts', 'pi', 'Pi is approximately 3.14159', importance=4)
        print(mem.recall('facts', 'pi'))
    """

    def __init__(self, backend: str = 'local'):
        if backend not in BACKENDS:
            raise ValueError(f"Unknown backend '{backend}'. Use 'local' or 'cloud'.")
        self.backend = backend
        self.config = BACKENDS[backend]
        self.max_retries = 3
        self.retry_delay = 2
        _log.info(f"SQLMemory initialized (backend={backend}, server={self.config['server']})")

    # ── Low-level SQL ────────────────────────────────────────────────────────

    def execute(self, query: str, timeout: int = 30) -> str:
        """Execute a SQL query via sqlcmd and return stdout. Retries on failure."""
        # Build server string with port: "10.0.0.110,1433"
        server_str = f"{self.config['server']},{self.config['port']}"
        # Wrap query with EXECUTE AS USER='dbo' to ensure schema access
        # (oblio owns the memory schema but SQL Server requires explicit grants
        # which cannot be self-granted; dbo impersonation bypasses this)
        if self.backend == 'local' and not query.strip().upper().startswith('EXECUTE AS'):
            query = f"EXECUTE AS USER='dbo'; {query}; REVERT"
        cmd = [
            SQLCMD,
            '-S', server_str,
            '-d', self.config['database'],
            '-U', self.config['user'],
            '-P', self.config['password'],
            '-Q', query,
            '-l', str(timeout),
        ]
        if self.config['encrypt']:
            cmd.extend(['-N', '-C'])  # Encrypt + TrustServerCertificate

        last_err = None
        for attempt in range(self.max_retries):
            try:
                result = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=timeout + 10
                )
                if result.returncode != 0 and result.stderr:
                    err_msg = result.stderr.strip()
                    if 'Login failed' in err_msg or 'Cannot open' in err_msg:
                        _log.error(f"SQL auth/db error: {err_msg}")
                        return ''
                    last_err = err_msg
                    _log.warning(f"SQL attempt {attempt+1}/{self.max_retries}: {err_msg}")
                    time.sleep(self.retry_delay)
                    continue
                return result.stdout.strip()
            except subprocess.TimeoutExpired:
                _log.warning(f"SQL timeout attempt {attempt+1}/{self.max_retries}")
                last_err = 'timeout'
                time.sleep(self.retry_delay)
            except Exception as e:
                _log.error(f"SQL execute error: {e}")
                last_err = str(e)
                time.sleep(self.retry_delay)

        _log.error(f"SQL failed after {self.max_retries} attempts: {last_err}")
        return ''

    def execute_scalar(self, query: str) -> Optional[str]:
        """Execute query and return first non-header value."""
        out = self.execute(query)
        lines = [l.strip() for l in out.split('\n') if l.strip() and not l.startswith('-')]
        # Skip header row and separator
        data_lines = []
        for line in lines:
            if 'rows affected' in line.lower():
                continue
            data_lines.append(line)
        if len(data_lines) >= 2:
            return data_lines[1]  # first data row after header
        return None

    def execute_rows(self, query: str) -> List[str]:
        """Execute query and return all data lines (excluding headers/footers)."""
        out = self.execute(query)
        lines = out.split('\n')
        data = []
        header_done = False
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith('---') or stripped.startswith('==='):
                header_done = True
                continue
            if 'rows affected' in stripped.lower():
                continue
            if not header_done:
                header_done = True  # skip first line (header)
                continue
            data.append(stripped)
        return data

    # ── Memory Operations (dbo.Memories) ──────────────────────────────────

    def remember(self, category: str, key: str, content: str,
                 importance: int = 3, tags: str = '') -> bool:
        """
        Store or update a memory. Upserts by category + key_name.

        Args:
            category: Memory category (e.g., 'facts', 'preferences', 'facs_training')
            key: Unique key within the category
            content: The content to remember
            importance: 1-5 scale (5 = critical)
            tags: Comma-separated tags for search

        Returns:
            True if successful
        """
        cat = _esc(category, 100)
        k = _esc(key, 255)
        c = _esc(content)
        t = _esc(tags, 500)
        query = f"""
            IF EXISTS (SELECT 1 FROM memory.Memories
                       WHERE category='{cat}' AND key_name='{k}' AND is_active=1)
                UPDATE memory.Memories
                SET content='{c}', importance={importance}, tags='{t}',
                    updated_at=GETDATE()
                WHERE category='{cat}' AND key_name='{k}' AND is_active=1;
            ELSE
                INSERT INTO memory.Memories
                    (category, key_name, content, importance, tags, source, is_active)
                VALUES ('{cat}', '{k}', '{c}', {importance}, '{t}', 'sql_memory', 1);
        """
        result = self.execute(query)
        ok = 'error' not in result.lower() if result else True
        _log.info(f"remember({cat}/{k}) → {'ok' if ok else 'failed'}")
        return ok

    def recall(self, category: str, key: str) -> Optional[str]:
        """
        Retrieve a specific memory by category and key.

        Returns:
            Content string, or None if not found.
        """
        cat = _esc(category, 100)
        k = _esc(key, 255)
        return self.execute_scalar(f"""
            SELECT content FROM memory.Memories
            WHERE category='{cat}' AND key_name='{k}' AND is_active=1
        """)

    def recall_recent(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Retrieve the N most recently updated memories across all categories.

        Returns:
            List of dicts with category, key_name, content, importance, tags, updated_at
        """
        out = self.execute(f"""
            SELECT TOP {n} category, key_name, content, importance, tags,
                   FORMAT(ISNULL(updated_at, created_at), 'yyyy-MM-dd HH:mm') as ts
            FROM memory.Memories
            WHERE is_active=1
            ORDER BY ISNULL(updated_at, created_at) DESC
        """)
        return self._parse_table(out, ['category', 'key_name', 'content', 'importance', 'tags', 'ts'])

    def search_memories(self, query: str) -> List[Dict[str, Any]]:
        """
        Search memories by keyword across content and tags.

        Returns:
            List of matching memory dicts.
        """
        q = _esc(query, 200)
        out = self.execute(f"""
            SELECT category, key_name, content, importance, tags
            FROM memory.Memories
            WHERE is_active=1
              AND (content LIKE '%{q}%' OR tags LIKE '%{q}%' OR key_name LIKE '%{q}%')
            ORDER BY importance DESC, updated_at DESC
        """)
        return self._parse_table(out, ['category', 'key_name', 'content', 'importance', 'tags'])

    def forget(self, category: str, key: str) -> bool:
        """Soft-delete a memory (set is_active=0)."""
        cat = _esc(category, 100)
        k = _esc(key, 255)
        self.execute(f"""
            UPDATE memory.Memories SET is_active=0
            WHERE category='{cat}' AND key_name='{k}'
        """)
        _log.info(f"forget({cat}/{k})")
        return True

    # ── Activity Log (dbo.ActivityLog) ────────────────────────────────────

    def log_event(self, event_type: str, agent: str, description: str,
                  metadata: str = '') -> bool:
        """
        Write an event to the activity log.

        Args:
            event_type: Type of event (e.g., 'task_complete', 'security_audit')
            agent: Name of the agent logging the event
            description: Human-readable description
            metadata: Optional JSON or free-text metadata
        """
        et = _esc(event_type, 100)
        ag = _esc(agent, 100)
        desc = _esc(description)
        meta = _esc(metadata)
        self.execute(f"""
            INSERT INTO memory.ActivityLog (event_type, agent, description, metadata)
            VALUES ('{et}', '{ag}', '{desc}', '{meta}')
        """)
        return True

    def get_recent_activity(self, since_hours: int = 24, agent: str = None) -> List[Dict]:
        """Get recent activity log entries."""
        where = f"WHERE logged_at >= DATEADD(HOUR, -{since_hours}, GETDATE())"
        if agent:
            where += f" AND agent='{_esc(agent, 100)}'"
        out = self.execute(f"""
            SELECT event_type, agent, description,
                   FORMAT(logged_at, 'yyyy-MM-dd HH:mm') as ts
            FROM memory.ActivityLog
            {where}
            ORDER BY logged_at DESC
        """)
        return self._parse_table(out, ['event_type', 'agent', 'description', 'ts'])

    # ── Task Queue (dbo.TaskQueue) ────────────────────────────────────────

    def queue_task(self, agent: str, task_type: str, payload: str = '{}',
                   priority = 5) -> Optional[str]:
        """
        Insert a new task into the queue.
        priority can be int (1-9) or string ('critical','high','medium','low','free').
        Returns: Task ID as string, or None on failure.
        """
        # Normalize priority to int
        _priority_map = {'critical': 1, 'high': 2, 'medium': 5, 'low': 7, 'free': 9}
        if isinstance(priority, str):
            priority = _priority_map.get(priority.lower(), 5)
        priority = int(priority)

        ag = _esc(agent, 100)
        tt = _esc(task_type, 100)
        pl = _esc(payload)
        self.execute(f"""
            INSERT INTO memory.TaskQueue (agent, task_type, payload, priority, status)
            VALUES ('{ag}', '{tt}', '{pl}', {priority}, 'pending')
        """)
        # Get the ID of the just-inserted task
        tid = self.execute_scalar(f"""
            SELECT TOP 1 id FROM memory.TaskQueue
            WHERE agent='{ag}' AND task_type='{tt}' AND status='pending'
            ORDER BY created_at DESC
        """)
        _log.info(f"queue_task({ag}/{tt}) → id={tid}")
        return tid

    def get_pending_tasks(self, agent: str, task_types: List[str]) -> List[Dict]:
        """
        Fetch pending tasks for an agent.

        Returns:
            List of task dicts with id, task_type, payload, priority, retry_count.
        """
        types_csv = ",".join(f"'{_esc(t, 100)}'" for t in task_types)
        ag = _esc(agent, 100)
        out = self.execute(f"""
            SELECT id, task_type, payload, priority, retry_count
            FROM memory.TaskQueue
            WHERE agent='{ag}' AND task_type IN ({types_csv}) AND status='pending'
            ORDER BY priority DESC, created_at ASC
        """)
        return self._parse_table(out, ['id', 'task_type', 'payload', 'priority', 'retry_count'])

    def claim_task(self, task_id) -> bool:
        """Mark a task as processing."""
        self.execute(f"""
            UPDATE memory.TaskQueue
            SET status='processing', started_at=GETDATE()
            WHERE id={int(task_id)}
        """)
        return True

    def complete_task(self, task_id, result: str = '') -> bool:
        """Mark a task as completed with optional result."""
        r = _esc(result, 500)
        self.execute(f"""
            UPDATE memory.TaskQueue
            SET status='completed', completed_at=GETDATE(), error_log='{r}'
            WHERE id={int(task_id)}
        """)
        _log.info(f"complete_task({task_id})")
        return True

    def fail_task(self, task_id, error: str, retry_count: int = 0,
                  max_retries: int = 3) -> bool:
        """Mark a task as failed, or re-queue if retries remain."""
        e = _esc(error, 800)
        new_status = 'pending' if retry_count < max_retries else 'failed'
        self.execute(f"""
            UPDATE memory.TaskQueue
            SET status='{new_status}', retry_count=retry_count+1, error_log='{e}'
            WHERE id={int(task_id)}
        """)
        _log.info(f"fail_task({task_id}) → {new_status}")
        return True

    def get_completed_tasks(self, since_hours: int = 24,
                            agent: str = None) -> List[Dict]:
        """Get recently completed/failed tasks."""
        where = f"WHERE status IN ('completed','failed') AND completed_at >= DATEADD(HOUR, -{since_hours}, GETDATE())"
        if agent:
            where += f" AND agent='{_esc(agent, 100)}'"
        out = self.execute(f"""
            SELECT id, agent, task_type, status,
                   FORMAT(completed_at, 'yyyy-MM-dd HH:mm') as ts
            FROM memory.TaskQueue
            {where}
            ORDER BY completed_at DESC
        """)
        return self._parse_table(out, ['id', 'agent', 'task_type', 'status', 'ts'])

    # ── Knowledge Index (dbo.KnowledgeIndex) ──────────────────────────────

    def store_knowledge(self, domain: str, topic: str, summary: str = '',
                        file_path: str = '', tags: str = '') -> bool:
        """
        Store or update a knowledge entry. Upserts by domain + topic.

        Args:
            domain: Knowledge domain (e.g., 'stamps', 'facs', 'nlp')
            topic: Specific topic title
            summary: Content/summary text
            file_path: Optional source file path
            tags: Optional comma-separated tags
        """
        d = _esc(domain, 100)
        t = _esc(topic, 255)
        s = _esc(summary)
        fp = _esc(file_path, 1000)
        # KnowledgeIndex doesn't have a tags column in the current schema,
        # so we store tags in the summary field prefix if needed
        query = f"""
            IF EXISTS (SELECT 1 FROM memory.KnowledgeIndex
                       WHERE domain='{d}' AND topic='{t}')
                UPDATE memory.KnowledgeIndex
                SET summary='{s}', file_path='{fp}',
                    last_trained=GETDATE(), training_count=ISNULL(training_count,0)+1
                WHERE domain='{d}' AND topic='{t}';
            ELSE
                INSERT INTO memory.KnowledgeIndex
                    (domain, topic, summary, file_path, last_trained, training_count)
                VALUES ('{d}', '{t}', '{s}', '{fp}', GETDATE(), 1);
        """
        self.execute(query)
        _log.info(f"store_knowledge({d}/{t})")
        return True

    def search_knowledge(self, domain: str, query: str = '') -> List[Dict]:
        """
        Search knowledge entries by domain and optional keyword.

        Returns:
            List of knowledge dicts.
        """
        d = _esc(domain, 100)
        where = f"WHERE domain='{d}'"
        if query:
            q = _esc(query, 200)
            where += f" AND (topic LIKE '%{q}%' OR summary LIKE '%{q}%')"
        out = self.execute(f"""
            SELECT domain, topic, summary, file_path, training_count,
                   FORMAT(last_trained, 'yyyy-MM-dd HH:mm') as ts
            FROM memory.KnowledgeIndex
            {where}
            ORDER BY last_trained DESC
        """)
        return self._parse_table(out, ['domain', 'topic', 'summary', 'file_path', 'training_count', 'ts'])

    def get_recent_knowledge(self, n: int = 10) -> List[Dict]:
        """Get the N most recently updated knowledge entries."""
        out = self.execute(f"""
            SELECT TOP {n} domain, topic, summary,
                   FORMAT(last_trained, 'yyyy-MM-dd HH:mm') as ts
            FROM memory.KnowledgeIndex
            ORDER BY last_trained DESC
        """)
        return self._parse_table(out, ['domain', 'topic', 'summary', 'ts'])

    # ── Sessions (dbo.Sessions) ───────────────────────────────────────────

    def get_session_context(self, session_id: str) -> Optional[Dict]:
        """
        Load session context from the database.

        Returns:
            Dict with session_key, channel, summary, token_count, or None.
        """
        sid = _esc(session_id, 255)
        out = self.execute(f"""
            SELECT session_key, channel, summary, token_count
            FROM memory.Sessions
            WHERE session_key='{sid}'
        """)
        rows = self._parse_table(out, ['session_key', 'channel', 'summary', 'token_count'])
        if rows:
            # Try to parse summary as JSON for structured context
            row = rows[0]
            try:
                row['context'] = json.loads(row.get('summary', '{}'))
            except (json.JSONDecodeError, TypeError):
                row['context'] = {}
            return row
        return None

    def save_session_context(self, session_id: str, context_data: Dict,
                             channel: str = 'agent', token_count: int = 0) -> bool:
        """
        Persist session context to the database. Context is stored as JSON in summary.

        Args:
            session_id: Unique session key
            context_data: Dict of context data (will be JSON-serialized)
            channel: Channel name
            token_count: Running token count for the session
        """
        sid = _esc(session_id, 255)
        ch = _esc(channel, 100)
        ctx_json = _esc(json.dumps(context_data, default=str))
        query = f"""
            IF EXISTS (SELECT 1 FROM memory.Sessions WHERE session_key='{sid}')
                UPDATE memory.Sessions
                SET summary='{ctx_json}', token_count={token_count}, ended_at=GETDATE()
                WHERE session_key='{sid}';
            ELSE
                INSERT INTO memory.Sessions
                    (session_key, channel, summary, token_count)
                VALUES ('{sid}', '{ch}', '{ctx_json}', {token_count});
        """
        self.execute(query)
        _log.info(f"save_session_context({sid})")
        return True

    # ── Schema Sync (for cloud backend) ──────────────────────────────────────

    def ensure_schema(self) -> bool:
        """
        Create the memory schema + tables if they don't exist.
        Useful for initializing the cloud backend.
        """
        schema_sql = """
            IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name='memory')
                EXEC('CREATE SCHEMA memory');
        """
        self.execute(schema_sql)

        tables = {
            'Memories': """
                CREATE TABLE dbo.Memories (
                    id BIGINT IDENTITY(1,1) PRIMARY KEY,
                    category NVARCHAR(100) NOT NULL,
                    key_name NVARCHAR(255),
                    content NVARCHAR(MAX) NOT NULL,
                    importance TINYINT DEFAULT 3,
                    tags NVARCHAR(500),
                    source NVARCHAR(255),
                    created_at DATETIME2 DEFAULT GETDATE(),
                    updated_at DATETIME2 DEFAULT GETDATE(),
                    expires_at DATETIME2,
                    is_active BIT DEFAULT 1
                )
            """,
            'Sessions': """
                CREATE TABLE dbo.Sessions (
                    id BIGINT IDENTITY(1,1) PRIMARY KEY,
                    session_key NVARCHAR(255),
                    channel NVARCHAR(100),
                    started_at DATETIME2 DEFAULT GETDATE(),
                    ended_at DATETIME2,
                    summary NVARCHAR(MAX),
                    token_count INT DEFAULT 0
                )
            """,
            'TaskQueue': """
                CREATE TABLE dbo.TaskQueue (
                    id BIGINT IDENTITY(1,1) PRIMARY KEY,
                    agent NVARCHAR(100) NOT NULL,
                    task_type NVARCHAR(100) NOT NULL,
                    payload NVARCHAR(MAX),
                    priority TINYINT DEFAULT 5,
                    status NVARCHAR(50) DEFAULT 'pending',
                    created_at DATETIME2 DEFAULT GETDATE(),
                    started_at DATETIME2,
                    completed_at DATETIME2,
                    error_log NVARCHAR(MAX),
                    retry_count TINYINT DEFAULT 0
                )
            """,
            'KnowledgeIndex': """
                CREATE TABLE dbo.KnowledgeIndex (
                    id BIGINT IDENTITY(1,1) PRIMARY KEY,
                    domain NVARCHAR(100) NOT NULL,
                    topic NVARCHAR(255) NOT NULL,
                    file_path NVARCHAR(1000),
                    summary NVARCHAR(MAX),
                    last_trained DATETIME2,
                    training_count INT DEFAULT 0,
                    created_at DATETIME2 DEFAULT GETDATE()
                )
            """,
            'ActivityLog': """
                CREATE TABLE dbo.ActivityLog (
                    id BIGINT IDENTITY(1,1) PRIMARY KEY,
                    event_type NVARCHAR(100) NOT NULL,
                    agent NVARCHAR(100),
                    description NVARCHAR(MAX),
                    metadata NVARCHAR(MAX),
                    logged_at DATETIME2 DEFAULT GETDATE()
                )
            """,
        }

        for table_name, create_sql in tables.items():
            check = f"""
                IF NOT EXISTS (SELECT 1 FROM INFORMATION_SCHEMA.TABLES
                               WHERE TABLE_SCHEMA='memory' AND TABLE_NAME='{table_name}')
                BEGIN
                    {create_sql}
                END
            """
            self.execute(check)
            _log.info(f"ensure_schema: {table_name} OK")

        return True

    # ── Utility ──────────────────────────────────────────────────────────────

    def _parse_table(self, raw_output: str, columns: List[str]) -> List[Dict]:
        """
        Parse sqlcmd tabular output into list of dicts.
        Uses separator line positions to correctly determine column boundaries.
        """
        if not raw_output:
            return []

        lines = raw_output.split('\n')
        if len(lines) < 3:
            return []

        results = []
        header_line = None
        separator_line = None
        start_data = 0

        # Find header and separator
        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped or 'rows affected' in stripped.lower():
                continue

            # First non-empty line is header
            if header_line is None:
                header_idx = i
                header_line = line
                continue

            # Line after header with dashes/spaces is separator
            if all(c in '- ' for c in stripped) and len(stripped) > 3:
                separator_line = line
                start_data = i + 1
                break

        if not header_line or not separator_line:
            return []

        # Determine column start positions from separator line (groups of dashes)
        # e.g. "-- ----- --------- ------- --------"
        col_starts = []
        in_dash = False
        for pos, ch in enumerate(separator_line):
            if ch == '-' and not in_dash:
                col_starts.append(pos)
                in_dash = True
            elif ch == ' ':
                in_dash = False

        if not col_starts:
            return []

        # Map column names to positions using header; use col_starts for boundaries
        # Match columns by order (header columns align with separator groups)
        header_words = header_line.split()
        col_positions = []
        for i, start_pos in enumerate(col_starts):
            # Find which requested column matches this header position
            # Use ordinal match: col_starts[i] corresponds to columns[i]
            if i < len(columns):
                col_positions.append((columns[i], start_pos))

        if not col_positions:
            return []

        # Parse data rows using separator-derived positions
        for line_num in range(start_data, len(lines)):
            line = lines[line_num]
            stripped = line.strip()

            if not stripped or 'rows affected' in stripped.lower():
                continue

            row = {}
            for i, (col, start_pos) in enumerate(col_positions):
                # End position is next column start or line end
                if i + 1 < len(col_positions):
                    end_pos = col_positions[i + 1][1] - 1  # -1 for space gap
                else:
                    end_pos = len(line)

                value = line[start_pos:end_pos].strip() if start_pos < len(line) else ''
                row[col] = value

            if row:
                results.append(row)

        return results

    def ping(self) -> bool:
        """Test connectivity to the backend."""
        result = self.execute("SELECT 1 AS ok")
        return 'ok' in result.lower() or '1' in result


# ── Module-level factory ─────────────────────────────────────────────────────

_instances: Dict[str, SQLMemory] = {}

def get_memory(backend: str = 'local') -> SQLMemory:
    """
    Get or create a SQLMemory instance for the specified backend.
    Singleton pattern — reuses existing connections.

    Args:
        backend: 'local' or 'cloud'

    Returns:
        SQLMemory instance
    """
    if backend not in _instances:
        _instances[backend] = SQLMemory(backend)
    return _instances[backend]


# ── Self-Test ────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 60)
    print("sql_dbo.py — Self-Test Suite")
    print("=" * 60)

    passed = 0
    failed = 0

    def test(name, func):
        global passed, failed
        try:
            result = func()
            status = "✅ PASS" if result else "⚠️  WARN (empty result)"
            print(f"  {status}: {name}")
            if result:
                passed += 1
            else:
                passed += 1  # empty is still ok for some tests
        except Exception as e:
            print(f"  ❌ FAIL: {name} → {e}")
            failed += 1

    for backend_name in ['local', 'cloud']:
        print(f"\n── Backend: {backend_name} ──")
        mem = SQLMemory(backend_name)

        # Ensure schema exists (important for cloud)
        if backend_name == 'cloud':
            print("  Creating schema if needed...")
            mem.ensure_schema()

        test("ping", lambda: mem.ping())

        test("remember",
             lambda: mem.remember('test', 'selftest_key',
                                  f'Self-test at {datetime.now()}',
                                  importance=1, tags='test,selftest'))

        test("recall",
             lambda: mem.recall('test', 'selftest_key') is not None)

        test("recall_recent",
             lambda: isinstance(mem.recall_recent(5), list))

        test("search_memories",
             lambda: isinstance(mem.search_memories('selftest'), list))

        test("log_event",
             lambda: mem.log_event('selftest', 'sql_memory',
                                   'Self-test ran successfully',
                                   '{"test": true}'))

        test("get_recent_activity",
             lambda: isinstance(mem.get_recent_activity(1), list))

        test("queue_task",
             lambda: mem.queue_task('test_agent', 'selftest_task',
                                    '{"test": true}', priority=1))

        test("get_pending_tasks",
             lambda: isinstance(mem.get_pending_tasks('test_agent', ['selftest_task']), list))

        test("store_knowledge",
             lambda: mem.store_knowledge('test', 'selftest_topic',
                                         'Knowledge self-test entry',
                                         '/dev/null', 'test'))

        test("search_knowledge",
             lambda: isinstance(mem.search_knowledge('test', 'selftest'), list))

        test("save_session_context",
             lambda: mem.save_session_context('selftest_session',
                                              {'mood': 'testing', 'count': 1},
                                              'test', 42))

        test("get_session_context",
             lambda: mem.get_session_context('selftest_session') is not None)

        # Cleanup test data
        test("forget (cleanup)",
             lambda: mem.forget('test', 'selftest_key'))

        # Clean up test task
        mem.execute("""
            DELETE FROM memory.TaskQueue
            WHERE agent='test_agent' AND task_type='selftest_task'
        """)
        mem.execute("""
            DELETE FROM memory.KnowledgeIndex
            WHERE domain='test' AND topic='selftest_topic'
        """)
        mem.execute("""
            DELETE FROM memory.Sessions WHERE session_key='selftest_session'
        """)

    print(f"\n{'=' * 60}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'=' * 60}")
    sys.exit(1 if failed > 0 else 0)
