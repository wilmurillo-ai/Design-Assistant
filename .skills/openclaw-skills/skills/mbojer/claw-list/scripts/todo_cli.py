#!/usr/bin/env python3
"""
todo_cli.py — Todo list management via PostgreSQL.

Usage:
    python3 todo_cli.py <command> [options]

See SKILL.md for full command reference.
"""

import argparse
import json
import os
import sys
import time
from datetime import date, datetime, timedelta
from pathlib import Path

# ---------------------------------------------------------------------------
# DB helpers
# ---------------------------------------------------------------------------

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    print("ERROR: psycopg2 not installed. Run: pip install psycopg2-binary", file=sys.stderr)
    sys.exit(1)


def get_db_config():
    """Load DB config from env or .env file."""
    env_file = Path(__file__).parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())

    cfg = {
        "host": os.environ.get("TODO_DB_HOST", "127.0.0.1"),
        "port": int(os.environ.get("TODO_DB_PORT", "5432")),
        "dbname": os.environ.get("TODO_DB_NAME", "researcher"),
        "user": os.environ.get("TODO_DB_USER", "researcher_agent"),
        "password": os.environ.get("TODO_DB_PASSWORD", ""),
    }
    sslmode = os.environ.get("TODO_DB_SSLMODE")
    if sslmode:
        cfg["sslmode"] = sslmode
    return cfg


def connect():
    """Return a database connection with retry logic and timeout."""
    cfg = get_db_config()
    cfg["connect_timeout"] = 10

    max_retries = 3
    backoff = 1  # seconds, doubles each retry

    for attempt in range(1, max_retries + 1):
        try:
            return psycopg2.connect(**cfg)
        except Exception as e:
            if attempt < max_retries:
                print(f"WARNING: DB connection attempt {attempt}/{max_retries} failed: {e}. Retrying in {backoff}s...", file=sys.stderr)
                time.sleep(backoff)
                backoff *= 2
            else:
                print(f"ERROR: Database connection failed after {max_retries} attempts: {e}", file=sys.stderr)
                sys.exit(1)


def query(conn, sql, params=None, fetch=True):
    """Execute a query and optionally return results."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute(sql, params)
        if fetch:
            return cur.fetchall()
        conn.commit()
        return None


def query_one(conn, sql, params=None):
    """Execute a query and return a single row."""
    rows = query(conn, sql, params)
    return rows[0] if rows else None


# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

def cmd_setup(args):
    """Create database tables if they don't exist."""
    conn = connect()
    try:
        query(conn, """
            CREATE TABLE IF NOT EXISTS todo_lists (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                owner_agent VARCHAR(100) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW(),
                UNIQUE(name, owner_agent)
            )
        """, fetch=False)

        query(conn, """
            CREATE TABLE IF NOT EXISTS todo_categories (
                id SERIAL PRIMARY KEY,
                list_id INTEGER NOT NULL REFERENCES todo_lists(id) ON DELETE CASCADE,
                name VARCHAR(255) NOT NULL,
                color VARCHAR(7),
                UNIQUE(list_id, name)
            )
        """, fetch=False)

        query(conn, """
            CREATE TABLE IF NOT EXISTS todos (
                id SERIAL PRIMARY KEY,
                list_id INTEGER NOT NULL REFERENCES todo_lists(id) ON DELETE CASCADE,
                category_id INTEGER REFERENCES todo_categories(id) ON DELETE SET NULL,
                title VARCHAR(500) NOT NULL,
                description TEXT,
                priority VARCHAR(10) DEFAULT 'medium'
                    CHECK (priority IN ('low', 'medium', 'high')),
                due_date DATE,
                completed BOOLEAN DEFAULT FALSE,
                archived BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT NOW(),
                completed_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT NOW()
            )
        """, fetch=False)

        query(conn, """
            CREATE TABLE IF NOT EXISTS todo_access_log (
                id SERIAL PRIMARY KEY,
                requesting_agent VARCHAR(100) NOT NULL,
                target_agent VARCHAR(100) NOT NULL,
                list_id INTEGER NOT NULL REFERENCES todo_lists(id),
                accessed_at TIMESTAMP DEFAULT NOW()
            )
        """, fetch=False)

        # Indexes
        query(conn, "CREATE INDEX IF NOT EXISTS idx_todos_list_id ON todos(list_id)", fetch=False)
        query(conn, "CREATE INDEX IF NOT EXISTS idx_todos_completed ON todos(completed)", fetch=False)
        query(conn, "CREATE INDEX IF NOT EXISTS idx_todos_due_date ON todos(due_date)", fetch=False)
        query(conn, "CREATE INDEX IF NOT EXISTS idx_todos_priority ON todos(priority)", fetch=False)

        conn.commit()
        print("✅ Todo database tables created successfully.")
    except Exception as e:
        conn.rollback()
        print(f"ERROR: Setup failed: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_or_create_list(conn, list_name, agent):
    """Get a list ID, creating it if it doesn't exist."""
    row = query_one(conn,
        "SELECT id FROM todo_lists WHERE name = %s AND owner_agent = %s",
        (list_name, agent))
    if row:
        return row["id"]

    row = query_one(conn,
        "INSERT INTO todo_lists (name, owner_agent) VALUES (%s, %s) RETURNING id",
        (list_name, agent))
    return row["id"]


def get_category_id(conn, list_id, category_name):
    """Get category ID by name within a list."""
    if not category_name:
        return None
    row = query_one(conn,
        "SELECT id FROM todo_categories WHERE list_id = %s AND name = %s",
        (list_id, category_name))
    return row["id"] if row else None


def format_todo(todo):
    """Format a todo for display."""
    status = "✅" if todo["completed"] else "⬜"
    priority_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
    pri = priority_icons.get(todo["priority"], "⚪")

    parts = [f"{status} [{todo['id']}] {pri} {todo['title']}"]

    if todo.get("due_date"):
        due = todo["due_date"]
        if isinstance(due, str):
            due = date.fromisoformat(due)
        today = date.today()
        if todo["completed"]:
            parts.append(f"(due: {due.isoformat()})")
        elif due < today:
            parts.append(f"⚠️ OVERDUE (was: {due.isoformat()})")
        elif due == today:
            parts.append(f"📅 Due TODAY")
        elif due <= today + timedelta(days=3):
            parts.append(f"📅 Due {due.isoformat()} (soon)")
        else:
            parts.append(f"(due: {due.isoformat()})")

    if todo.get("category_name"):
        parts.append(f"📂 {todo['category_name']}")

    if todo.get("archived"):
        parts.append("📦 archived")

    return " ".join(parts)


def format_todo_compact(todo):
    """Format a todo as a single compact line."""
    mark = "✓" if todo["completed"] else " "
    pri = {"high": "H", "medium": "M", "low": "L"}.get(todo["priority"], "?")
    due = ""
    if todo.get("due_date"):
        d = todo["due_date"]
        if isinstance(d, str):
            d = date.fromisoformat(d)
        if not todo["completed"] and d < date.today():
            due = f" [OVERDUE:{d.isoformat()}]"
        else:
            due = f" due:{d.isoformat()}"
    cat = f" | {todo['category_name']}" if todo.get("category_name") else ""
    arch = " [archived]" if todo.get("archived") else ""
    return f"{todo['id']} | [{mark}] {todo['title']} | {pri}{due}{cat}{arch}"


def todo_to_dict(todo):
    """Convert a todo row to a clean dict for JSON output."""
    return {
        "id": todo["id"],
        "title": todo["title"],
        "description": todo.get("description"),
        "list": todo.get("list_name"),
        "owner_agent": todo.get("owner_agent"),
        "category": todo.get("category_name"),
        "priority": todo["priority"],
        "due_date": todo["due_date"].isoformat() if todo.get("due_date") and hasattr(todo["due_date"], "isoformat") else todo.get("due_date"),
        "completed": todo["completed"],
        "archived": todo.get("archived", False),
        "created_at": todo["created_at"].isoformat() if todo.get("created_at") and hasattr(todo["created_at"], "isoformat") else str(todo.get("created_at", "")),
    }


def check_cross_agent(conn, requesting_agent, target_agent, list_id):
    """Log cross-agent access. Returns True if access is allowed."""
    if requesting_agent == target_agent:
        return True

    query(conn,
        """INSERT INTO todo_access_log (requesting_agent, target_agent, list_id)
           VALUES (%s, %s, %s)""",
        (requesting_agent, target_agent, list_id), fetch=False)
    conn.commit()
    return True  # For now, all cross-agent access is allowed but logged


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_add(args):
    """Add a new todo."""
    conn = connect()
    try:
        list_name = args.list or "default"
        list_id = get_or_create_list(conn, list_name, args.agent)

        category_id = get_category_id(conn, list_id, args.category)
        if args.category and not category_id:
            print(f"Warning: Category '{args.category}' not found in list '{list_name}'. Creating it.")
            row = query_one(conn,
                "INSERT INTO todo_categories (list_id, name) VALUES (%s, %s) RETURNING id",
                (list_id, args.category))
            category_id = row["id"]

        due = None
        if args.due:
            try:
                due = date.fromisoformat(args.due)
            except ValueError:
                print(f"ERROR: Invalid date format '{args.due}'. Use YYYY-MM-DD.", file=sys.stderr)
                sys.exit(1)

        row = query_one(conn,
            """INSERT INTO todos (list_id, category_id, title, description, priority, due_date)
               VALUES (%s, %s, %s, %s, %s, %s)
               RETURNING id""",
            (list_id, category_id, args.title, args.description, args.priority, due))
        conn.commit()
        print(f"✅ Added todo #{row['id']}: {args.title}")
    finally:
        conn.close()


def cmd_list(args):
    """List todos."""
    # Validate: --all-agents or --agent required
    if not args.all_agents and not args.agent:
        print("ERROR: Either --agent or --all-agents is required.", file=sys.stderr)
        sys.exit(1)

    conn = connect()
    try:
        conditions = []
        params = []

        if args.all_agents:
            # Show all agents — add l.owner_agent to select for grouping
            pass
        else:
            conditions.append("l.owner_agent = %s")
            params.append(args.agent)

        if args.list:
            conditions.append("l.name = %s")
            params.append(args.list)

        if args.category:
            conditions.append("c.name = %s")
            params.append(args.category)

        if args.priority:
            conditions.append("t.priority = %s")
            params.append(args.priority)

        if not args.all:
            if not args.completed:
                conditions.append("t.completed = FALSE")
            if not args.archived:
                conditions.append("t.archived = FALSE")

        if args.due_before:
            conditions.append("t.due_date <= %s")
            params.append(args.due_before)
        if args.due_after:
            conditions.append("t.due_date >= %s")
            params.append(args.due_after)

        where = " WHERE " + " AND ".join(conditions) if conditions else ""

        # Get total count first
        count_row = query_one(conn, f"""
            SELECT COUNT(*) as total
            FROM todos t
            JOIN todo_lists l ON t.list_id = l.id
            LEFT JOIN todo_categories c ON t.category_id = c.id
            {where}
        """, params)
        total = count_row["total"] if count_row else 0

        # Apply limit
        limit_clause = ""
        if not getattr(args, 'no_limit', False) and not getattr(args, 'json', False) and not getattr(args, 'compact', False):
            limit_val = getattr(args, 'limit', 20)
            if limit_val > 0:
                limit_clause = f" LIMIT {limit_val}"

        rows = query(conn, f"""
            SELECT t.*, l.name as list_name, l.owner_agent, c.name as category_name
            FROM todos t
            JOIN todo_lists l ON t.list_id = l.id
            LEFT JOIN todo_categories c ON t.category_id = c.id
            {where}
            ORDER BY t.completed ASC, t.priority DESC, t.due_date ASC NULLS LAST, t.created_at DESC
            {limit_clause}
        """, params)

        if not rows:
            print("No todos found.")
            return

        # JSON output
        if getattr(args, 'json', False):
            output = [todo_to_dict(r) for r in rows]
            print(json.dumps(output, indent=2, default=str))
            return

        # Compact output
        if getattr(args, 'compact', False):
            current_group = None
            for todo in rows:
                if args.all_agents:
                    group = todo["owner_agent"]
                else:
                    group = todo["list_name"]
                if group != current_group:
                    current_group = group
                    if args.all_agents:
                        print(f"\n🤖 {current_group}")
                    else:
                        print(f"{current_group}:")
                print(f"  {format_todo_compact(todo)}")
            if total > len(rows):
                print(f"  ... ({len(rows)} of {total} shown)")
            return

        # Default output — group by agent (all-agents) or list (single agent)
        current_group = None
        for todo in rows:
            if args.all_agents:
                group = todo["owner_agent"]
            else:
                group = todo["list_name"]

            if group != current_group:
                current_group = group
                if args.all_agents:
                    print(f"\n🤖 Agent: {current_group}")
                    print("-" * 40)
                else:
                    print(f"\n📋 {current_group}")
                    print("-" * 40)
            print(f"  {format_todo(todo)}")
        if total > len(rows):
            print(f"\n  Showing {len(rows)} of {total} todos. Use --no-limit to show all.")
        print()
    finally:
        conn.close()


def cmd_complete(args):
    """Mark a todo as complete."""
    conn = connect()
    try:
        row = query_one(conn,
            """UPDATE todos SET completed = TRUE, completed_at = NOW(), updated_at = NOW()
               WHERE id = %s AND list_id IN (SELECT id FROM todo_lists WHERE owner_agent = %s)
               RETURNING title""",
            (args.id, args.agent))
        if row:
            conn.commit()
            print(f"✅ Completed: {row['title']}")
        else:
            print(f"ERROR: Todo #{args.id} not found or not owned by {args.agent}", file=sys.stderr)
    finally:
        conn.close()


def cmd_uncomplete(args):
    """Mark a todo as incomplete."""
    conn = connect()
    try:
        row = query_one(conn,
            """UPDATE todos SET completed = FALSE, completed_at = NULL, updated_at = NOW()
               WHERE id = %s AND list_id IN (SELECT id FROM todo_lists WHERE owner_agent = %s)
               RETURNING title""",
            (args.id, args.agent))
        if row:
            conn.commit()
            print(f"⬜ Uncompleted: {row['title']}")
        else:
            print(f"ERROR: Todo #{args.id} not found or not owned by {args.agent}", file=sys.stderr)
    finally:
        conn.close()


def cmd_edit(args):
    """Edit a todo."""
    conn = connect()
    try:
        updates = {"updated_at": "NOW()"}
        params = []

        if args.title:
            updates["title"] = "%s"
            params.append(args.title)
        if args.description is not None:
            updates["description"] = "%s"
            params.append(args.description)
        if args.priority:
            updates["priority"] = "%s"
            params.append(args.priority)
        if args.due:
            updates["due_date"] = "%s"
            params.append(date.fromisoformat(args.due))
        if args.category is not None:
            # Need to get list_id for the todo being edited
            todo_row = query_one(conn,
                "SELECT list_id FROM todos WHERE id = %s AND list_id IN (SELECT id FROM todo_lists WHERE owner_agent = %s)",
                (args.id, args.agent))
            if not todo_row:
                print(f"ERROR: Todo #{args.id} not found or not owned by {args.agent}", file=sys.stderr)
                return  # finally block will close conn
            cat_id = get_category_id(conn, todo_row["list_id"], args.category)
            if args.category and not cat_id:
                # Auto-create category
                row = query_one(conn,
                    "INSERT INTO todo_categories (list_id, name) VALUES (%s, %s) RETURNING id",
                    (todo_row["list_id"], args.category))
                cat_id = row["id"]
            updates["category_id"] = "%s"
            params.append(cat_id)

        ALLOWED_COLUMNS = {"title", "description", "priority", "due_date", "category_id", "updated_at"}
        set_clause = ", ".join(f"{k} = {v}" for k, v in updates.items() if k in ALLOWED_COLUMNS)
        params.extend([args.id, args.agent])

        row = query_one(conn,
            f"""UPDATE todos SET {set_clause}
                WHERE id = %s AND list_id IN (SELECT id FROM todo_lists WHERE owner_agent = %s)
                RETURNING title""",
            params)
        if row:
            conn.commit()
            print(f"✏️ Updated: {row['title']}")
        else:
            print(f"ERROR: Todo #{args.id} not found or not owned by {args.agent}", file=sys.stderr)
    finally:
        conn.close()


def cmd_transfer(args):
    """Transfer a todo to another agent."""
    conn = connect()
    try:
        # Verify the todo exists and belongs to the source agent
        todo = query_one(conn,
            """SELECT t.id, t.title, t.list_id, l.name as list_name, l.owner_agent
               FROM todos t
               JOIN todo_lists l ON t.list_id = l.id
               WHERE t.id = %s AND l.owner_agent = %s""",
            (args.id, args.from_agent))
        if not todo:
            print(f"ERROR: Todo #{args.id} not found or not owned by {args.from_agent}.", file=sys.stderr)
            sys.exit(1)

        # Get or create target list for the target agent
        target_list_name = args.to_list or "default"
        target_list_id = get_or_create_list(conn, target_list_name, args.to_agent)

        # Move the todo
        query(conn,
            "UPDATE todos SET list_id = %s, updated_at = NOW() WHERE id = %s",
            (target_list_id, args.id), fetch=False)

        # Log cross-agent access
        check_cross_agent(conn, args.from_agent, args.to_agent, target_list_id)

        conn.commit()
        print(f"➡️ Transferred [{args.id}] \"{todo['title']}\" from {args.from_agent}/{todo['list_name']} → {args.to_agent}/{target_list_name}")
    finally:
        conn.close()


def cmd_delete(args):
    """Delete a todo."""
    conn = connect()
    try:
        row = query_one(conn,
            """DELETE FROM todos
               WHERE id = %s AND list_id IN (SELECT id FROM todo_lists WHERE owner_agent = %s)
               RETURNING title""",
            (args.id, args.agent))
        if row:
            conn.commit()
            print(f"🗑️ Deleted: {row['title']}")
        else:
            print(f"ERROR: Todo #{args.id} not found or not owned by {args.agent}", file=sys.stderr)
    finally:
        conn.close()


def cmd_archive(args):
    """Archive completed todos."""
    conn = connect()
    try:
        conditions = ["l.owner_agent = %s", "t.completed = TRUE", "t.archived = FALSE"]
        params = [args.agent]

        if args.list:
            conditions.append("l.name = %s")
            params.append(args.list)

        where = " AND ".join(conditions)

        rows = query(conn, f"""
            UPDATE todos t SET archived = TRUE, updated_at = NOW()
            FROM todo_lists l
            WHERE t.list_id = l.id AND {where}
            RETURNING t.id, t.title
        """, params)
        conn.commit()

        if rows:
            print(f"📦 Archived {len(rows)} completed todo(s):")
            for r in rows:
                print(f"  - [{r['id']}] {r['title']}")
        else:
            print("No completed todos to archive.")
    finally:
        conn.close()


def cmd_due_soon(args):
    """Show todos due within N days."""
    conn = connect()
    try:
        cutoff = date.today() + timedelta(days=args.days)
        rows = query(conn, """
            SELECT t.*, l.name as list_name, c.name as category_name
            FROM todos t
            JOIN todo_lists l ON t.list_id = l.id
            LEFT JOIN todo_categories c ON t.category_id = c.id
            WHERE l.owner_agent = %s
              AND t.completed = FALSE
              AND t.archived = FALSE
              AND t.due_date IS NOT NULL
              AND t.due_date <= %s
            ORDER BY t.due_date ASC, t.priority DESC
        """, (args.agent, cutoff))

        if not rows:
            print(f"No todos due in the next {args.days} days.")
            return

        if getattr(args, 'json', False):
            print(json.dumps([todo_to_dict(r) for r in rows], indent=2, default=str))
            return

        print(f"📅 Todos due in the next {args.days} days:")
        for todo in rows:
            if getattr(args, 'compact', False):
                print(f"  {format_todo_compact(todo)}")
            else:
                print(f"  {format_todo(todo)}")
    finally:
        conn.close()


def cmd_overdue(args):
    """Show overdue todos."""
    conn = connect()
    try:
        rows = query(conn, """
            SELECT t.*, l.name as list_name, c.name as category_name
            FROM todos t
            JOIN todo_lists l ON t.list_id = l.id
            LEFT JOIN todo_categories c ON t.category_id = c.id
            WHERE l.owner_agent = %s
              AND t.completed = FALSE
              AND t.archived = FALSE
              AND t.due_date IS NOT NULL
              AND t.due_date < %s
            ORDER BY t.due_date ASC, t.priority DESC
        """, (args.agent, date.today()))

        if not rows:
            print("✅ No overdue todos!")
            return

        if getattr(args, 'json', False):
            print(json.dumps([todo_to_dict(r) for r in rows], indent=2, default=str))
            return

        print(f"⚠️ Overdue todos:")
        for todo in rows:
            if getattr(args, 'compact', False):
                print(f"  {format_todo_compact(todo)}")
            else:
                print(f"  {format_todo(todo)}")
    finally:
        conn.close()


def cmd_lists(args):
    """List all lists for an agent."""
    conn = connect()
    try:
        rows = query(conn,
            """SELECT l.*, COUNT(t.id) as todo_count,
                      COUNT(t.id) FILTER (WHERE t.completed = FALSE) as active_count
               FROM todo_lists l
               LEFT JOIN todos t ON t.list_id = l.id
               WHERE l.owner_agent = %s
               GROUP BY l.id
               ORDER BY l.name""",
            (args.agent,))

        if not rows:
            print(f"No lists found for agent '{args.agent}'.")
            return

        print(f"📋 Lists for {args.agent}:")
        for r in rows:
            print(f"  - {r['name']} ({r['active_count']} active / {r['todo_count']} total)")
    finally:
        conn.close()


def cmd_create_list(args):
    """Create a new list."""
    conn = connect()
    try:
        list_id = get_or_create_list(conn, args.name, args.agent)
        conn.commit()
        print(f"✅ List '{args.name}' ready (id: {list_id}).")
    finally:
        conn.close()


def cmd_delete_list(args):
    """Delete a list and all its todos."""
    conn = connect()
    try:
        row = query_one(conn,
            """DELETE FROM todo_lists
               WHERE name = %s AND owner_agent = %s
               RETURNING id""",
            (args.name, args.agent))
        if row:
            conn.commit()
            print(f"🗑️ Deleted list '{args.name}' and all its todos.")
        else:
            print(f"ERROR: List '{args.name}' not found for agent '{args.agent}'.", file=sys.stderr)
    finally:
        conn.close()


def cmd_categories(args):
    """List categories for a list."""
    conn = connect()
    try:
        list_id = get_or_create_list(conn, args.list, args.agent)
        rows = query(conn,
            "SELECT * FROM todo_categories WHERE list_id = %s ORDER BY name",
            (list_id,))

        if not rows:
            print(f"No categories in list '{args.list}'.")
            return

        print(f"📂 Categories in '{args.list}':")
        for r in rows:
            color = r.get("color") or "no color"
            print(f"  - {r['name']} ({color})")
    finally:
        conn.close()


def cmd_create_category(args):
    """Create a category in a list."""
    conn = connect()
    try:
        list_id = get_or_create_list(conn, args.list, args.agent)
        row = query_one(conn,
            "INSERT INTO todo_categories (list_id, name, color) VALUES (%s, %s, %s) RETURNING id",
            (list_id, args.name, getattr(args, 'color', None)))
        conn.commit()
        print(f"✅ Category '{args.name}' created in list '{args.list}'.")
    finally:
        conn.close()


def cmd_migrate_check(args):
    """Check for existing task files that can be migrated."""
    workspace = os.environ.get("TODO_WORKSPACE", str(Path.home() / ".openclaw" / "workspace-researcher"))
    candidates = ["THELIST.md", "todo.md", "todo.txt", "TODO.md", "TODO.txt", "tasks.md", "tasks.txt"]

    found = []
    for fname in candidates:
        fpath = Path(workspace) / fname
        if fpath.exists():
            content = fpath.read_text().strip()
            if content:
                # Count list items (lines starting with - or *)
                items = [l.strip() for l in content.splitlines()
                         if l.strip().startswith(("-", "*", "1."))]
                found.append({"file": str(fpath), "items": len(items), "preview": content[:500]})

    if not found:
        print("No existing task files found to migrate.")
        return

    print("📁 Found existing task files:\n")
    for i, f in enumerate(found, 1):
        print(f"  {i}. {f['file']} ({f['items']} items)")
        print(f"     Preview: {f['preview'][:200]}...")
        print()

    print("To migrate, run:")
    print("  python3 todo_cli.py migrate --file <path> --list <list_name> --agent <agent>")
    print("Options: --action import-keep | import-delete (default: import-keep)")


def cmd_migrate(args):
    """Migrate a task file into the todo system."""
    fpath = Path(args.file).resolve()
    if not fpath.exists() or not fpath.is_file():
        print(f"ERROR: File not found or not a regular file: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Restrict to workspace directory
    workspace = Path(os.environ.get("TODO_WORKSPACE", str(Path.home() / ".openclaw" / "workspace-researcher"))).resolve()
    try:
        fpath.relative_to(workspace)
    except ValueError:
        print(f"ERROR: File must be within workspace directory: {workspace}", file=sys.stderr)
        sys.exit(1)

    content = fpath.read_text()
    items = []
    for line in content.splitlines():
        line = line.strip()
        if line.startswith(("-", "*")):
            # Remove bullet and any checkbox markers
            text = line.lstrip("-* ").strip()
            text = text.replace("[ ]", "").replace("[x]", "").replace("[X]", "").strip()
            if text:
                items.append(text)
        elif any(line.startswith(f"{n}.") for n in range(1, 100)):
            text = line.split(".", 1)[1].strip()
            if text:
                items.append(text)

    if not items:
        print("No list items found in file.")
        return

    print(f"Found {len(items)} items to migrate:")
    for item in items:
        print(f"  - {item}")

    action = getattr(args, 'action', 'import-keep')
    if action not in ('import-keep', 'import-delete'):
        print(f"ERROR: Unknown action '{action}'. Use 'import-keep' or 'import-delete'.", file=sys.stderr)
        sys.exit(1)

    conn = connect()
    try:
        list_name = args.list or "Migrated"
        list_id = get_or_create_list(conn, list_name, args.agent)

        for item in items:
            query(conn,
                "INSERT INTO todos (list_id, title) VALUES (%s, %s)",
                (list_id, item), fetch=False)

        conn.commit()
        print(f"\n✅ Imported {len(items)} items into list '{list_name}'.")

        if action == 'import-delete':
            fpath.unlink()
            print(f"🗑️ Deleted source file: {args.file}")
        else:
            print(f"📁 Source file kept: {args.file}")
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Todo list management")
    sub = parser.add_subparsers(dest="command", required=True)

    # setup
    sub.add_parser("setup")

    # add
    p = sub.add_parser("add")
    p.add_argument("--title", required=True)
    p.add_argument("--list", default=None)
    p.add_argument("--category", default=None)
    p.add_argument("--priority", default="medium", choices=["low", "medium", "high"])
    p.add_argument("--due", default=None)
    p.add_argument("--description", default=None)
    p.add_argument("--agent", required=True)

    # list
    p = sub.add_parser("list")
    p.add_argument("--agent", default=None)
    p.add_argument("--all-agents", action="store_true", help="Show todos from all agents, grouped by owner")
    p.add_argument("--list", default=None)
    p.add_argument("--category", default=None)
    p.add_argument("--priority", default=None)
    p.add_argument("--due-before", default=None)
    p.add_argument("--due-after", default=None)
    p.add_argument("--completed", action="store_true")
    p.add_argument("--archived", action="store_true")
    p.add_argument("--all", action="store_true")
    p.add_argument("--compact", action="store_true", help="Single-line output (fewer tokens)")
    p.add_argument("--json", action="store_true", help="JSON output")
    p.add_argument("--limit", type=int, default=20, help="Max items (default: 20)")
    p.add_argument("--no-limit", action="store_true", help="Show all items")

    # complete
    p = sub.add_parser("complete")
    p.add_argument("id", type=int)
    p.add_argument("--agent", required=True)

    # uncomplete
    p = sub.add_parser("uncomplete")
    p.add_argument("id", type=int)
    p.add_argument("--agent", required=True)

    # edit
    p = sub.add_parser("edit")
    p.add_argument("id", type=int)
    p.add_argument("--title", default=None)
    p.add_argument("--description", default=None)
    p.add_argument("--priority", default=None, choices=["low", "medium", "high"])
    p.add_argument("--due", default=None)
    p.add_argument("--category", default=None)
    p.add_argument("--list", default=None)
    p.add_argument("--agent", required=True)

    # transfer
    p = sub.add_parser("transfer")
    p.add_argument("id", type=int, help="Todo ID to transfer")
    p.add_argument("--from-agent", required=True, help="Current owner agent")
    p.add_argument("--to-agent", required=True, help="Target owner agent")
    p.add_argument("--to-list", default=None, help="Target list name (default: 'default')")

    # delete
    p = sub.add_parser("delete")
    p.add_argument("id", type=int)
    p.add_argument("--agent", required=True)

    # archive
    p = sub.add_parser("archive")
    p.add_argument("--agent", required=True)
    p.add_argument("--list", default=None)

    # due-soon
    p = sub.add_parser("due-soon")
    p.add_argument("--agent", required=True)
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--compact", action="store_true", help="Single-line output (fewer tokens)")
    p.add_argument("--json", action="store_true", help="JSON output")

    # overdue
    p = sub.add_parser("overdue")
    p.add_argument("--agent", required=True)
    p.add_argument("--compact", action="store_true", help="Single-line output (fewer tokens)")
    p.add_argument("--json", action="store_true", help="JSON output")

    # lists
    p = sub.add_parser("lists")
    p.add_argument("--agent", required=True)

    # create-list
    p = sub.add_parser("create-list")
    p.add_argument("--name", required=True)
    p.add_argument("--agent", required=True)

    # delete-list
    p = sub.add_parser("delete-list")
    p.add_argument("--name", required=True)
    p.add_argument("--agent", required=True)

    # categories
    p = sub.add_parser("categories")
    p.add_argument("--list", required=True)
    p.add_argument("--agent", required=True)

    # create-category
    p = sub.add_parser("create-category")
    p.add_argument("--name", required=True)
    p.add_argument("--list", required=True)
    p.add_argument("--agent", required=True)
    p.add_argument("--color", default=None)

    # migrate-check
    sub.add_parser("migrate-check")

    # migrate
    p = sub.add_parser("migrate")
    p.add_argument("--file", required=True)
    p.add_argument("--list", default=None)
    p.add_argument("--agent", required=True)
    p.add_argument("--action", default="import-keep", choices=["import-keep", "import-delete"])

    args = parser.parse_args()

    # Route to command handler
    cmd_map = {
        "setup": cmd_setup,
        "add": cmd_add,
        "list": cmd_list,
        "complete": cmd_complete,
        "uncomplete": cmd_uncomplete,
        "edit": cmd_edit,
        "transfer": cmd_transfer,
        "delete": cmd_delete,
        "archive": cmd_archive,
        "due-soon": cmd_due_soon,
        "overdue": cmd_overdue,
        "lists": cmd_lists,
        "create-list": cmd_create_list,
        "delete-list": cmd_delete_list,
        "categories": cmd_categories,
        "create-category": cmd_create_category,
        "migrate-check": cmd_migrate_check,
        "migrate": cmd_migrate,
    }

    handler = cmd_map.get(args.command)
    if handler:
        handler(args)
    else:
        print(f"ERROR: Unknown command '{args.command}'", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
