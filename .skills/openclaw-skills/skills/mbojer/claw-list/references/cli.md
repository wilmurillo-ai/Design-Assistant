# Todo CLI — Full Reference

## Environment Variables

Set in `.env` file in skill directory:

| Variable | Default | Description |
|---|---|---|
| `TODO_DB_HOST` | 127.0.0.1 | PostgreSQL host |
| `TODO_DB_PORT` | 5432 | PostgreSQL port |
| `TODO_DB_NAME` | researcher | Database name |
| `TODO_DB_USER` | researcher_agent | Database user |
| `TODO_DB_PASSWORD` | (required) | Database password |

## Commands — Full Examples

### setup

Create tables (run once):

```bash
python3 scripts/todo_cli.py setup
```

Creates: `todo_lists`, `todo_categories`, `todos`, `todo_access_log` + indexes.

### add

```bash
# Simple
python3 scripts/todo_cli.py add --title "Buy groceries" --agent researcher

# With all options
python3 scripts/todo_cli.py add --title "Apply to Novo Nordisk" \
  --list "Job Search" --category Applications --priority high \
  --due 2026-03-20 --description "Senior DevOps role" --agent researcher
```

Options:
- `--title` (required)
- `--list` (default: "default")
- `--category` (auto-created if doesn't exist)
- `--priority` (low|medium|high, default: medium)
- `--due` (YYYY-MM-DD)
- `--description` (optional text)
- `--agent` (required — owner agent name)

### list

```bash
# All active todos for agent
python3 scripts/todo_cli.py list --agent researcher

# All agents — grouped by owner
python3 scripts/todo_cli.py list --all-agents

# Filtered
python3 scripts/todo_cli.py list --list "Job Search" --agent researcher
python3 scripts/todo_cli.py list --priority high --agent researcher
python3 scripts/todo_cli.py list --due-before 2026-03-20 --agent researcher
python3 scripts/todo_cli.py list --completed --agent researcher
python3 scripts/todo_cli.py list --all --agent researcher

# Compact output (minimal tokens)
python3 scripts/todo_cli.py list --agent researcher --compact
python3 scripts/todo_cli.py list --all-agents --compact

# JSON output (for programmatic use)
python3 scripts/todo_cli.py list --agent researcher --json
```

Options:
- `--agent` (owner filter — or use `--all-agents` instead)
- `--all-agents` (show todos from all agents, grouped by owner)
- `--list`, `--category`, `--priority` (filters)
- `--due-before`, `--due-after` (date range)
- `--completed` (include completed)
- `--archived` (include archived)
- `--all` (show everything)
- `--compact` (single-line format)
- `--json` (JSON output)
- `--limit N` (max items, default: 20; use `--no-limit` to disable)

### complete / uncomplete

```bash
python3 scripts/todo_cli.py complete 42 --agent researcher
python3 scripts/todo_cli.py uncomplete 42 --agent researcher
```

### edit

```bash
python3 scripts/todo_cli.py edit 42 --title "New title" --agent researcher
python3 scripts/todo_cli.py edit 42 --due 2026-03-25 --priority low --agent researcher
python3 scripts/todo_cli.py edit 42 --category "Networking" --agent researcher
```

Editable fields: `--title`, `--description`, `--due`, `--priority`, `--category`, `--list`

### transfer

```bash
# Transfer to another agent (default list)
python3 scripts/todo_cli.py transfer 42 --from-agent researcher --to-agent jobhunter

# Transfer to a specific list on the target agent
python3 scripts/todo_cli.py transfer 42 --from-agent researcher --to-agent jobhunter --to-list "Shared Tasks"
```

Options:
- `id` (required — todo ID to transfer)
- `--from-agent` (required — current owner)
- `--to-agent` (required — new owner)
- `--to-list` (optional — target list, defaults to "default")

Cross-agent transfers are logged to `todo_access_log`.

### delete

```bash
python3 scripts/todo_cli.py delete 42 --agent researcher
```

### archive

```bash
# Archive all completed for agent
python3 scripts/todo_cli.py archive --agent researcher

# Archive for specific list
python3 scripts/todo_cli.py archive --list "Job Search" --agent researcher
```

### due-soon

```bash
# Default: next 7 days
python3 scripts/todo_cli.py due-soon --agent researcher

# Custom range
python3 scripts/todo_cli.py due-soon --agent researcher --days 3
```

### overdue

```bash
python3 scripts/todo_cli.py overdue --agent researcher
```

### lists / create-list / delete-list

```bash
python3 scripts/todo_cli.py lists --agent researcher
python3 scripts/todo_cli.py create-list --name "Home" --agent researcher
python3 scripts/todo_cli.py delete-list --name "Home" --agent researcher
```

### categories / create-category

```bash
python3 scripts/todo_cli.py categories --list "Job Search" --agent researcher
python3 scripts/todo_cli.py create-category --name "Applications" --list "Job Search" --agent researcher
```

### migrate-check / migrate

```bash
# Scan for task files
python3 scripts/todo_cli.py migrate-check

# Import from file
python3 scripts/todo_cli.py migrate --file THELIST.md --list "Projects" --agent researcher
python3 scripts/todo_cli.py migrate --file old-tasks.txt --list "Archive" --agent researcher --action import-delete
```

Actions:
- `import-keep` (default): Import items, keep source file
- `import-delete`: Import items, delete source file

## Output Format Examples

### Default
```
📋 Job Search
----------------------------------------
  ⬜ [7] 🔴 Apply to Novo Nordisk 📅 Due 2026-03-22 (soon) 📂 Applications
  ✅ [8] 🟡 Old application (due: 2026-03-10) 📂 Applications 📦 archived
```

### Compact (`--compact`)
```
Job Search:
  7 | Apply to Novo Nordisk | high | due:2026-03-22 | Applications
  8 | Old application ✓ | medium | due:2026-03-10 | Applications [archived]
```

### JSON (`--json`)
```json
[
  {
    "id": 7,
    "title": "Apply to Novo Nordisk",
    "list": "Job Search",
    "category": "Applications",
    "priority": "high",
    "due_date": "2026-03-22",
    "completed": false,
    "archived": false,
    "created_at": "2026-03-17T19:00:00"
  }
]
```

## Database Schema

See [schema.md](schema.md) for table definitions.
