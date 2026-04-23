# Vibe Platform Migration Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate the Bitrix24 skill from webhook-based API to Vibe Platform (vibecode.bitrix24.tech) — new scripts, new onboarding, rewritten references, 6 new domains.

**Architecture:** Single unified CLI script (`vibe.py`) replaces 5 old scripts. Auth via `Authorization: Bearer {api_key}` header. Entity CRUD via `/v1/{entity}`, special endpoints via `--raw`, batch via `--batch`. Config in `~/.config/bitrix24-skill/config.json` with `api_key` instead of `webhook_url`.

**Tech Stack:** Python 3 stdlib only (urllib, json, pathlib, argparse). No external dependencies.

---

## Chunk 1: Scripts

### Task 1: Create `scripts/vibe_config.py`

**Files:**
- Create: `scripts/vibe_config.py`

This module provides configuration management for the Vibe Platform. It replaces `scripts/bitrix24_config.py`.

- [ ] **Step 1: Create `vibe_config.py` with all functions**

```python
#!/usr/bin/env python3
"""Configuration management for Vibe Platform API key."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

DEFAULT_CONFIG_PATH = Path.home() / ".config" / "bitrix24-skill" / "config.json"
BASE_URL = "https://vibecode.bitrix24.tech"


def load_config(path: Path = DEFAULT_CONFIG_PATH) -> dict:
    """Read config file, return dict or empty dict on failure."""
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def save_config(path: Path, data: dict) -> None:
    """Write config dict to file, creating parent dirs."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_key(config_file: str | None = None) -> str | None:
    """Return api_key from config or None."""
    path = Path(config_file).expanduser() if config_file else DEFAULT_CONFIG_PATH
    config = load_config(path)
    key = config.get("api_key")
    return key if isinstance(key, str) and key.strip() else None


def persist_key(key: str, config_file: str | None = None) -> Path:
    """Save api_key to config. Returns config path."""
    path = Path(config_file).expanduser() if config_file else DEFAULT_CONFIG_PATH
    config = load_config(path)
    config["api_key"] = key.strip()
    config["base_url"] = BASE_URL
    save_config(path, config)
    return path


def mask_key(key: str) -> str:
    """Mask key: first 10 chars + **** + last 2. E.g. vibe_api_ab****cd."""
    if len(key) <= 12:
        return key[:4] + "****"
    return key[:10] + "****" + key[-2:]


def get_cached_user(config_file: str | None = None) -> dict | None:
    """Return cached {user_id, timezone} or None."""
    path = Path(config_file).expanduser() if config_file else DEFAULT_CONFIG_PATH
    config = load_config(path)
    user_id = config.get("user_id")
    if user_id is not None:
        return {"user_id": user_id, "timezone": config.get("timezone", "")}
    return None


def cache_user_data(user_id: int, timezone: str = "", config_file: str | None = None) -> None:
    """Save user_id and timezone to config."""
    path = Path(config_file).expanduser() if config_file else DEFAULT_CONFIG_PATH
    config = load_config(path)
    config["user_id"] = user_id
    if timezone:
        config["timezone"] = timezone
    save_config(path, config)


def migrate_old_config(config_file: str | None = None) -> bool:
    """Detect old webhook_url config, back up, and remove it. Returns True if migration happened."""
    path = Path(config_file).expanduser() if config_file else DEFAULT_CONFIG_PATH
    config = load_config(path)
    if "webhook_url" not in config:
        return False
    # Back up
    backup = path.with_suffix(".json.bak")
    shutil.copy2(path, backup)
    # Remove old keys
    del config["webhook_url"]
    config.pop("user_id", None)
    config.pop("timezone", None)
    save_config(path, config)
    return True
```

- [ ] **Step 2: Verify the file runs without syntax errors**

Run: `python3 scripts/vibe_config.py`
Expected: exits cleanly with no output (module, no `if __name__`)

- [ ] **Step 3: Commit**

```bash
git add scripts/vibe_config.py
git commit -m "feat: add vibe_config.py for Vibe Platform key management"
```

---

### Task 2: Create `scripts/vibe.py`

**Files:**
- Create: `scripts/vibe.py`

Unified CLI script replacing `bitrix24_call.py` and `bitrix24_batch.py`. Supports 4 modes: entity CRUD, raw endpoint, batch, iterate.

- [ ] **Step 1: Create `vibe.py` with argument parsing and mode routing**

```python
#!/usr/bin/env python3
"""Unified Vibe Platform CLI for Bitrix24 REST API.

Modes:
    Entity CRUD:  vibe.py deals --json
                  vibe.py deals/123 --json
                  vibe.py deals --create --body '{"title":"X"}' --confirm-write --json
                  vibe.py deals --update --id 123 --body '{"stageId":"WON"}' --confirm-write --json
                  vibe.py deals --delete --id 123 --confirm-destructive --json
                  vibe.py deals/search --body '{"filter":{...}}' --json
                  vibe.py deals/aggregate --body '{"field":"opportunity","function":"sum"}' --json
                  vibe.py deals/fields --json

    Raw:          vibe.py --raw GET /v1/chats/recent --json
                  vibe.py --raw POST /v1/notifications --body '{"..."}' --json

    Batch:        echo '[{"method":"GET","path":"/v1/deals"}]' | vibe.py --batch --json

    Iterate:      vibe.py deals --iterate --json
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from urllib import error, parse, request

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vibe_config import load_key, cache_user_data, BASE_URL  # noqa: E402

MAX_PAGES = 200
RETRY_CODES = {429, 502}
MAX_RETRIES_429 = 3
MAX_RETRIES_502 = 2
DEFAULT_RETRY_AFTER = 45


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Vibe Platform CLI for Bitrix24.")
    parser.add_argument("path", nargs="?", help="Entity path, e.g. 'deals', 'deals/123', 'deals/search'")
    parser.add_argument("--raw", nargs=2, metavar=("METHOD", "PATH"), help="Raw endpoint: --raw GET /v1/chats/recent")
    parser.add_argument("--batch", action="store_true", help="Batch mode: read JSON array from stdin")
    parser.add_argument("--create", action="store_true", help="Create entity")
    parser.add_argument("--update", action="store_true", help="Update entity")
    parser.add_argument("--delete", action="store_true", help="Delete entity")
    parser.add_argument("--id", help="Entity ID for update/delete")
    parser.add_argument("--body", help="JSON body for create/update/raw/search")
    parser.add_argument("--iterate", action="store_true", help="Auto-paginate, collect all pages")
    parser.add_argument("--max-items", type=int, help="Limit items when iterating")
    parser.add_argument("--page-size", type=int, default=50, help="Page size (default 50)")
    parser.add_argument("--confirm-write", action="store_true", help="Required for create/update")
    parser.add_argument("--confirm-destructive", action="store_true", help="Required for delete")
    parser.add_argument("--dry-run", action="store_true", help="Show request without executing")
    parser.add_argument("--json", action="store_true", help="Pretty-print JSON output")
    parser.add_argument("--config-file", help="Config file path override")
    parser.add_argument("--timeout", type=float, default=20.0, help="HTTP timeout seconds")
    return parser.parse_args()


def do_request(url: str, method: str, body: dict | None, api_key: str, timeout: float) -> dict:
    """Execute HTTP request with retry logic for 429 and 502."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    data = json.dumps(body).encode("utf-8") if body else None
    max_attempts = max(MAX_RETRIES_429, MAX_RETRIES_502) + 1  # total attempts including initial

    for attempt in range(max_attempts):
        req = request.Request(url, data=data, headers=headers, method=method)
        resp_headers = {}
        try:
            with request.urlopen(req, timeout=timeout) as response:
                payload = response.read().decode("utf-8", errors="replace")
                status = response.getcode()
        except error.HTTPError as exc:
            payload = exc.read().decode("utf-8", errors="replace")
            status = exc.code
            resp_headers = dict(exc.headers) if exc.headers else {}
        except Exception as exc:
            return {"ok": False, "error": str(exc)}

        # Retry logic
        if status == 429 and attempt < MAX_RETRIES_429:
            retry_after = int(resp_headers.get("Retry-After", DEFAULT_RETRY_AFTER))
            time.sleep(retry_after)
            continue
        if status == 502 and attempt < MAX_RETRIES_502:
            time.sleep(5)
            continue
        break

    try:
        parsed = json.loads(payload)
    except Exception:
        parsed = {"raw": payload}

    return {"ok": status < 400, "status": status, "data": parsed}


def resolve_entity_request(args: argparse.Namespace) -> tuple[str, str, dict | None]:
    """Resolve entity path + flags into (http_method, url_path, body)."""
    path = args.path
    body = json.loads(args.body) if args.body else None

    if args.delete:
        entity_id = args.id or (path.split("/")[1] if "/" in path else None)
        entity = path.split("/")[0]
        if not entity_id:
            raise ValueError("--delete requires --id or path like 'deals/123'")
        return "DELETE", f"/v1/{entity}/{entity_id}", None

    if args.update:
        entity_id = args.id or (path.split("/")[1] if "/" in path else None)
        entity = path.split("/")[0]
        if not entity_id:
            raise ValueError("--update requires --id or path like 'deals/123'")
        return "PUT", f"/v1/{entity}/{entity_id}", body

    if args.create:
        entity = path.split("/")[0] if path else ""
        return "POST", f"/v1/{entity}", body

    # Sub-resources: deals/search, deals/aggregate, deals/fields, deals/123
    if "/" in path:
        parts = path.split("/", 1)
        entity, sub = parts[0], parts[1]
        if sub in ("search", "aggregate"):
            return "POST", f"/v1/{entity}/{sub}", body
        elif sub == "fields":
            return "GET", f"/v1/{entity}/{sub}", None
        else:
            # deals/123 — get by ID
            return "GET", f"/v1/{entity}/{sub}", None

    # Default: list
    return "GET", f"/v1/{path}", None


def classify_operation(http_method: str, args: argparse.Namespace) -> str:
    """Classify as read/write/destructive."""
    if args.delete or http_method == "DELETE":
        return "destructive"
    if args.create or args.update or http_method in ("POST", "PUT", "PATCH"):
        # search and aggregate are POST but read-only
        if args.path and "/" in args.path:
            sub = args.path.split("/", 1)[1]
            if sub in ("search", "aggregate", "fields"):
                return "read"
        return "write"
    return "read"


def main() -> int:
    args = parse_args()
    api_key = load_key(args.config_file)

    if not api_key:
        result = {"ok": False, "error": "No Vibe API key configured. Run setup first."}
        print(json.dumps(result, ensure_ascii=False, indent=2 if args.json else None))
        return 1

    # --- Batch mode ---
    if args.batch:
        stdin_data = sys.stdin.read()
        try:
            commands = json.loads(stdin_data)
        except json.JSONDecodeError as e:
            print(json.dumps({"ok": False, "error": f"Invalid JSON from stdin: {e}"}, indent=2))
            return 1
        if not isinstance(commands, list):
            print(json.dumps({"ok": False, "error": "Batch input must be a JSON array"}, indent=2))
            return 1

        results = {}
        for i, cmd in enumerate(commands):
            cmd_method = cmd.get("method", "GET")
            cmd_path = cmd.get("path", "")
            cmd_body = cmd.get("body")
            url = f"{BASE_URL}{cmd_path}"
            result = do_request(url, cmd_method, cmd_body, api_key, args.timeout)
            results[f"cmd{i}"] = result

        output = {"ok": all(r.get("ok") for r in results.values()), "results": results}
        print(json.dumps(output, ensure_ascii=False, indent=2 if args.json else None))
        return 0 if output["ok"] else 1

    # --- Raw mode ---
    if args.raw:
        http_method, url_path = args.raw
        http_method = http_method.upper()
        body = json.loads(args.body) if args.body else None

        if args.dry_run:
            print(json.dumps({"dry_run": True, "method": http_method, "url": f"{BASE_URL}{url_path}"}, indent=2))
            return 0

        url = f"{BASE_URL}{url_path}"
        result = do_request(url, http_method, body, api_key, args.timeout)
        print(json.dumps(result, ensure_ascii=False, indent=2 if args.json else None))
        return 0 if result.get("ok") else 1

    # --- Entity mode ---
    if not args.path:
        print(json.dumps({"ok": False, "error": "Provide entity path (e.g. 'deals') or use --raw/--batch"}, indent=2))
        return 1

    try:
        http_method, url_path, body = resolve_entity_request(args)
    except ValueError as e:
        print(json.dumps({"ok": False, "error": str(e)}, indent=2))
        return 1

    op_type = classify_operation(http_method, args)

    if args.dry_run:
        print(json.dumps({
            "dry_run": True,
            "method": http_method,
            "url": f"{BASE_URL}{url_path}",
            "operation": op_type,
            "body": body,
        }, ensure_ascii=False, indent=2))
        return 0

    if op_type == "write" and not args.confirm_write:
        print(json.dumps({
            "ok": False,
            "error": f"Write operation requires --confirm-write flag",
            "operation": op_type,
        }, ensure_ascii=False, indent=2))
        return 2

    if op_type == "destructive" and not args.confirm_destructive:
        print(json.dumps({
            "ok": False,
            "error": f"Destructive operation requires --confirm-destructive flag",
            "operation": op_type,
        }, ensure_ascii=False, indent=2))
        return 2

    # --- Iterate mode ---
    if args.iterate:
        all_items = []
        page = 1
        total = None
        for _ in range(MAX_PAGES):
            sep = "&" if "?" in url_path else "?"
            paginated_path = f"{url_path}{sep}page={page}&pageSize={args.page_size}"
            url = f"{BASE_URL}{paginated_path}"
            result = do_request(url, http_method, body, api_key, args.timeout)

            if not result.get("ok"):
                print(json.dumps(result, ensure_ascii=False, indent=2 if args.json else None))
                return 1

            data = result.get("data", {})
            page_items = data.get("data", [])
            if not isinstance(page_items, list):
                page_items = []
            all_items.extend(page_items)

            if total is None:
                total = data.get("total", len(all_items))

            if args.max_items and len(all_items) >= args.max_items:
                all_items = all_items[:args.max_items]
                break

            if len(page_items) < args.page_size:
                break
            page += 1

        output = {"ok": True, "data": all_items, "total": total, "fetched": len(all_items)}
        print(json.dumps(output, ensure_ascii=False, indent=2 if args.json else None))
        return 0

    # --- Single request ---
    url = f"{BASE_URL}{url_path}"
    result = do_request(url, http_method, body, api_key, args.timeout)

    # Auto-cache user data after /v1/me
    if url_path == "/v1/me" and result.get("ok"):
        user_data = result.get("data", {}).get("data", {})
        uid = user_data.get("id") or user_data.get("userId")
        tz = user_data.get("timezone", "")
        if uid:
            try:
                cache_user_data(int(uid), tz, args.config_file)
            except Exception:
                pass

    print(json.dumps(result, ensure_ascii=False, indent=2 if args.json else None))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Verify syntax**

Run: `python3 -c "import py_compile; py_compile.compile('scripts/vibe.py', doraise=True)"`
Expected: no errors

- [ ] **Step 3: Test dry-run mode**

Run: `python3 scripts/vibe.py deals --dry-run --json`
Expected: error about missing API key (no config yet) — confirms the script runs and argument parsing works

- [ ] **Step 4: Commit**

```bash
git add scripts/vibe.py
git commit -m "feat: add vibe.py unified CLI for Vibe Platform"
```

---

### Task 3: Create `scripts/check_connection.py`

**Files:**
- Create: `scripts/check_connection.py`

Diagnostics script that calls `GET /v1/me` and reports connection status.

- [ ] **Step 1: Create `check_connection.py`**

```python
#!/usr/bin/env python3
"""Check Vibe Platform connection using saved API key."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib import error, request

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from vibe_config import load_key, mask_key, BASE_URL, migrate_old_config  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check Vibe Platform connection.")
    parser.add_argument("--config-file", help="Config file path override")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout seconds")
    return parser.parse_args()


def probe_me(api_key: str, timeout: float) -> dict:
    """Call GET /v1/me and return parsed result."""
    url = f"{BASE_URL}/v1/me"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
    }
    req = request.Request(url, headers=headers, method="GET")
    try:
        with request.urlopen(req, timeout=timeout) as response:
            payload = response.read().decode("utf-8", errors="replace")
            status = response.getcode()
    except error.HTTPError as exc:
        payload = exc.read().decode("utf-8", errors="replace")
        status = exc.code
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

    try:
        body = json.loads(payload)
    except Exception:
        body = {"raw": payload}

    return {"ok": status < 400, "status": status, "body": body}


def build_result(args: argparse.Namespace) -> dict:
    # Check for old config
    migrated = migrate_old_config(args.config_file)

    api_key = load_key(args.config_file)
    result = {
        "key_found": api_key is not None,
        "migrated_from_webhook": migrated,
    }

    if not api_key:
        result["connection_ok"] = False
        result["error"] = "No Vibe API key found in config"
        return result

    result["key_prefix"] = mask_key(api_key)

    probe = probe_me(api_key, args.timeout)
    if not probe.get("ok"):
        result["connection_ok"] = False
        result["error"] = probe.get("error") or f"HTTP {probe.get('status')}"
        return result

    result["connection_ok"] = True
    body = probe.get("body", {})
    data = body.get("data", body)
    result["scopes"] = data.get("scopes", [])
    result["portal"] = data.get("portal", "")
    result["user"] = data.get("name", data.get("user", ""))
    return result


def main() -> int:
    args = parse_args()
    result = build_result(args)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        for k, v in result.items():
            print(f"{k}: {v}")

    return 0 if result.get("connection_ok") else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Verify syntax**

Run: `python3 -c "import py_compile; py_compile.compile('scripts/check_connection.py', doraise=True)"`
Expected: no errors

- [ ] **Step 3: Commit**

```bash
git add scripts/check_connection.py
git commit -m "feat: add check_connection.py for Vibe Platform diagnostics"
```

---

### Task 4: Delete old webhook scripts

**Files:**
- Delete: `scripts/bitrix24_call.py`
- Delete: `scripts/bitrix24_batch.py`
- Delete: `scripts/bitrix24_config.py`
- Delete: `scripts/save_webhook.py`
- Delete: `scripts/check_webhook.py`

- [ ] **Step 1: Delete all 5 old scripts**

```bash
git rm scripts/bitrix24_call.py scripts/bitrix24_batch.py scripts/bitrix24_config.py scripts/save_webhook.py scripts/check_webhook.py
```

- [ ] **Step 2: Verify no remaining imports reference old modules**

Run: `grep -r "bitrix24_call\|bitrix24_batch\|bitrix24_config\|save_webhook\|check_webhook" scripts/`
Expected: no matches

- [ ] **Step 3: Commit**

```bash
git commit -m "chore: remove old webhook-based scripts (replaced by vibe.py)"
```

---

## Chunk 2: SKILL.md Rewrite

### Task 5: Rewrite SKILL.md — Frontmatter

**Files:**
- Modify: `SKILL.md:1-96` (frontmatter section)

- [ ] **Step 1: Replace entire frontmatter**

Replace lines 1-96 of `SKILL.md` with updated frontmatter. Key changes:
- Remove `webhook` tag, add `vibe`, `bots`, `telephony`, `workflows`, `ecommerce`
- Add trigger phrases for new domains: bots ("боты", "бот"), telephony ("звонки", "телефония", "АТС"), workflows ("бизнес-процессы", "автоматизация"), e-commerce ("платежи", "заказы", "корзина"), duplicates ("дубликаты", "дубли")
- Keep MCP server config unchanged (`mcp-dev.bitrix24.tech/mcp`)

```yaml
---
name: bitrix24
description: >
  Work with Bitrix24 (Битрикс24) via Vibe Platform API. Triggers on:
  CRM — "сделки", "контакты", "лиды", "воронка", "клиенты", "deals", "contacts", "leads", "pipeline";
  Tasks — "задачи", "мои задачи", "просроченные", "создай задачу", "tasks", "overdue", "to-do";
  Calendar — "расписание", "встречи", "календарь", "schedule", "meetings", "events";
  Chat — "чаты", "сообщения", "уведомления", "написать", "notifications", "messages";
  Channels — "каналы", "канал", "объявления", "подписчики", "channels", "announcements", "subscribers";
  Open Lines — "открытые линии", "поддержка", "обращения", "клиентские чаты", "операторы",
  "омниканал", "виджет чата", "open lines", "support", "customer chat", "helpdesk", "operator";
  Bots — "боты", "бот", "чат-бот", "слэш-команды", "bots", "chatbot", "slash commands";
  Telephony — "звонки", "телефония", "АТС", "транскрипция", "calls", "telephony", "PBX";
  Workflows — "бизнес-процессы", "автоматизация", "триггеры", "workflows", "automation", "triggers";
  Projects — "проекты", "рабочие группы", "projects", "workgroups";
  Time — "рабочее время", "кто на работе", "учёт времени", "timeman", "work status";
  Drive — "файлы", "документы", "диск", "files", "documents", "drive";
  Structure — "сотрудники", "отделы", "структура", "подчинённые", "departments", "employees", "org structure";
  Feed — "лента", "новости", "объявления", "feed", "announcements";
  E-commerce — "платежи", "заказы", "корзина", "payments", "orders", "basket";
  Duplicates — "дубликаты", "дубли", "duplicates";
  Scenarios — "утренний брифинг", "morning briefing", "еженедельный отчёт", "weekly report",
  "статус команды", "что у меня сегодня", "итоги дня", "план на день", "воронка продаж",
  "расскажи про клиента", "подготовь к встрече", "как работает отдел".
metadata:
  openclaw:
    requires:
      bins:
        - python3
      mcp:
        - url: https://mcp-dev.bitrix24.tech/mcp
          transport: streamable_http
          tools:
            - bitrix-search
            - bitrix-app-development-doc-details
            - bitrix-method-details
            - bitrix-article-details
            - bitrix-event-details
    emoji: "B24"
    homepage: https://github.com/rsvbitrix/bitrix24-skill
    aliases:
      - Bitrix24
      - bitrix24
      - Bitrix
      - bitrix
      - b24
      - Битрикс24
      - битрикс24
      - Битрикс
      - битрикс
    tags:
      - bitrix24
      - bitrix
      - b24
      - crm
      - tasks
      - calendar
      - drive
      - chat
      - messenger
      - im
      - vibe
      - mcp
      - Битрикс24
      - CRM
      - задачи
      - чат
      - проекты
      - группы
      - лента
      - рабочее время
      - timeman
      - socialnetwork
      - feed
      - projects
      - workgroups
      - org structure
      - smart process
      - смарт-процесс
      - products
      - товары
      - каталог
      - quotes
      - предложения
      - invoices
      - счета
      - open lines
      - openlines
      - imopenlines
      - открытые линии
      - поддержка
      - обращения
      - операторы
      - омниканал
      - helpdesk
      - landing
      - sites
      - сайты
      - лендинги
      - bots
      - боты
      - telephony
      - телефония
      - звонки
      - workflows
      - бизнес-процессы
      - ecommerce
      - платежи
      - заказы
      - duplicates
      - дубликаты
---
```

- [ ] **Step 2: Verify YAML frontmatter is valid**

Run: `python3 -c "import yaml; yaml.safe_load(open('SKILL.md').read().split('---')[1])"`
Expected: no errors (requires PyYAML — if not installed, manually check `---` delimiters)

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "feat: update SKILL.md frontmatter for Vibe Platform + new domains"
```

---

### Task 6: Rewrite SKILL.md — Rules section

**Files:**
- Modify: `SKILL.md:98-168` (rules section)

- [ ] **Step 1: Replace rules section**

Replace the "STOP — Read These Rules" section. Keep all 8 rules identical in spirit. Specific text changes:

**Rule 1** — replace the example sequence:
```
User says "дай расписание на среду" → you IMMEDIATELY:
1. Call `/v1/me` to get user ID and timezone
2. Call `vibe.py --raw GET /v1/calendar/events` for that date (read `references/calendar.md`)
3. Call `vibe.py tasks/search` with deadline filter for that date (read `references/tasks.md`)
4. Show combined schedule
```
Replace `"покажи сделки" → you IMMEDIATELY call vibe.py deals` and `"мои задачи" → you IMMEDIATELY call vibe.py tasks`.

**Rule 2** — FORBIDDEN words list, replace with:
```
API, REST, Vibe, endpoint, scope, token, curl, JSON, method, parameter, SDK, OAuth,
vibe.py, config.json, /v1/me, /v1/deals, Authorization, Bearer
```

**Rule 5** — replace `user.current` → `/v1/me` in the timezone note:
```
- Get timezone from `/v1/me`, never ask the user
```

**Rules 3, 4, 6, 7, 8** — copy verbatim from current SKILL.md (no method names appear in these rules, so no changes needed). Read the current file first and preserve these rules exactly as-is:
- Rule 3: "Write requests — one short yes/no question" (confirm in one sentence)
- Rule 4: "Errors — fix silently or say one sentence" (retry automatically)
- Rule 6: "Proactive insights" (flag overdue tasks, stuck deals, conflicts)
- Rule 7: "Suggest next actions" (one short hint after results)
- Rule 8: "First message in session" (brief intro if greeting/unclear)

- [ ] **Step 2: Commit**

```bash
git add SKILL.md
git commit -m "feat: update SKILL.md rules with Vibe Platform commands"
```

---

### Task 7: Rewrite SKILL.md — Setup, Making REST Calls, Batch, and Technical Rules

**Files:**
- Modify: `SKILL.md:386-593` (setup, REST calls, batch, technical rules, domain references)

- [ ] **Step 1: Replace Setup section**

Replace the "Setup" section (webhook setup) with Vibe Platform onboarding:

```markdown
## Setup

The only thing needed is a Vibe API key. When the key is not configured, show these instructions:

> **Чтобы начать, нужно подключиться к вашему Битрикс24:**
>
> 1. Откройте сайт **vibecode.bitrix24.tech**
> 2. Нажмите «Войти» — используйте логин и пароль от вашего Битрикс24
> 3. В личном кабинете нажмите «Создать ключ»
> 4. Назовите его как угодно (например, «Мой помощник»)
> 5. В разделе «Доступы» отметьте все пункты — это позволит работать со сделками, задачами, календарём и всем остальным
> 6. Нажмите «Создать» и скопируйте ключ (он показывается один раз!)
> 7. Вставьте ключ сюда в чат
>
> Это займёт пару минут. После этого я смогу работать с вашим Битрикс24.

When the user provides a key, save and verify:

```bash
python3 scripts/vibe.py --raw GET /v1/me --json
```

If the key works, confirm: "Готово! Подключился к порталу **{portal}**. Чем могу помочь?"

If the key fails (401/403): "Ключ не подошёл. Проверьте, что вы скопировали его полностью — он начинается с `vibe_api_`. Если не помогло, создайте новый ключ на vibecode.bitrix24.tech."

If calls fail later, run `scripts/check_connection.py --json`.
```

- [ ] **Step 2: Replace "Making REST Calls" section**

Replace with Vibe Platform CLI usage:

```markdown
## Making REST Calls

```bash
python3 scripts/vibe.py {entity} --json
```

Examples:

```bash
# List deals
python3 scripts/vibe.py deals --json

# Get deal by ID
python3 scripts/vibe.py deals/123 --json

# Search with filters (MongoDB-style)
python3 scripts/vibe.py deals/search --body '{"filter":{"opportunity":{"$gte":100000},"stageId":{"$eq":"NEW"}}}' --json

# Get available fields
python3 scripts/vibe.py deals/fields --json

# Create (requires --confirm-write)
python3 scripts/vibe.py deals --create --body '{"title":"New Deal","stageId":"NEW","opportunity":50000}' --confirm-write --json

# Update
python3 scripts/vibe.py deals/123 --update --body '{"stageId":"WON"}' --confirm-write --json

# Delete (requires --confirm-destructive)
python3 scripts/vibe.py deals/123 --delete --confirm-destructive --json

# Auto-paginate
python3 scripts/vibe.py deals --iterate --json

# Dry-run
python3 scripts/vibe.py deals --create --body '{"title":"Test"}' --dry-run --json

# Raw endpoint (non-entity)
python3 scripts/vibe.py --raw GET /v1/chats/recent --json
python3 scripts/vibe.py --raw POST /v1/notifications --body '{"userId":5,"message":"Hello"}' --json
```
```

- [ ] **Step 3: Replace "Batch Calls" section**

```markdown
## Batch Calls

For scenarios needing 2+ calls, use batch mode with JSON array from stdin:

```bash
echo '[
  {"method":"GET","path":"/v1/tasks","body":{"filter":{"assignedById":{"$eq":5}}}},
  {"method":"GET","path":"/v1/deals","body":{"filter":{"assignedById":{"$eq":5}}}}
]' | python3 scripts/vibe.py --batch --json
```

Results are returned keyed by command index (`cmd0`, `cmd1`, etc.).
```

- [ ] **Step 4: Replace "Technical Rules" section**

Replace the entire "Technical Rules" block with this content:

```markdown
## Technical Rules

These rules are for the agent internally, not for user-facing output.

- Start with `vibe.py --raw GET /v1/me --json` to get the user's ID and timezone.
- Entity CRUD uses `vibe.py {entity}` — see reference files for exact entity names.
- Non-entity endpoints use `vibe.py --raw {HTTP_VERB} {path}` — see reference files.
- Filters use MongoDB-style operators in JSON body: `{"filter":{"opportunity":{"$gte":100000}}}`.
  Operators: `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$contains`, `$in`.
- Fields are camelCase: `stageId`, `opportunity`, `assignedById`, `createdAt`.
- Pagination: `page`/`pageSize` parameters (default page size 50).
- Use `vibe.py {entity}/fields --json` before writing custom or portal-specific fields.
- Dates: ISO 8601 for datetime, `YYYY-MM-DD` for date-only.
- When a call fails, run `scripts/check_connection.py --json` before asking the user.
- For batch operations, use `vibe.py --batch` with JSON array from stdin.
- Safety: `--confirm-write` for create/update, `--confirm-destructive` for delete, `--dry-run` to preview.
```

- [ ] **Step 5: Replace "Domain References" section**

Replace the domain reference list with the full updated list (18 existing + 6 new):

```markdown
## Domain References

- `references/access.md` — Vibe key setup, scopes, MCP docs endpoint.
- `references/troubleshooting.md` — diagnostics and error handling.
- `references/mcp-workflow.md` — MCP tool selection and query patterns.
- `references/crm.md` — deals, contacts, leads, companies, activities.
- `references/smartprocess.md` — smart processes, funnels, stages.
- `references/products.md` — product catalog, product rows.
- `references/quotes.md` — quotes (commercial proposals), smart invoices.
- `references/tasks.md` — tasks, checklists, comments, planner, time tracking.
- `references/chat.md` — chats, notifications, dialog history.
- `references/channels.md` — channels, announcements, subscribers.
- `references/openlines.md` — open lines, omnichannel, operators, sessions.
- `references/bots.md` — bot platform, registration, messages, slash-commands.
- `references/telephony.md` — calls, TTS, transcription, statistics.
- `references/workflows.md` — business processes, triggers, workflow tasks.
- `references/calendar.md` — sections, events, attendees, availability.
- `references/drive.md` — storage, folders, files, external links.
- `references/files.md` — file uploads: base64 inline, disk+attach.
- `references/users.md` — users, departments, org-structure, subordinates.
- `references/projects.md` — workgroups, projects, scrum, membership.
- `references/feed.md` — activity stream, feed posts, comments.
- `references/timeman.md` — work day, absence reports, schedule.
- `references/ecommerce.md` — payments, basket, order statuses.
- `references/duplicates.md` — duplicate search by phone/email.
- `references/timeline-logs.md` — timeline entries, pin, bind, notes.
- `references/sites.md` — landing pages, sites, blocks, publishing.
```

- [ ] **Step 6: Commit**

```bash
git add SKILL.md
git commit -m "feat: rewrite SKILL.md setup, REST calls, batch, and technical rules for Vibe"
```

---

### Task 8: Rewrite SKILL.md — Scenarios

**Files:**
- Modify: `SKILL.md:174-382` (scenarios section)

- [ ] **Step 1: Rewrite all 7 existing scenarios with `vibe.py` commands**

For each scenario, replace all `bitrix24_batch.py`/`bitrix24_call.py` calls with `vibe.py` equivalents. Use this conversion pattern:

**Morning briefing** — replace the batch call with:
```bash
echo '[
  {"method":"GET","path":"/v1/calendar/events","body":{"ownerId":<ID>,"days":1}},
  {"method":"POST","path":"/v1/tasks/search","body":{"filter":{"responsibleId":{"$eq":<ID>},"status":{"$ne":5},"deadline":{"$lte":"<today_end>"}}}},
  {"method":"POST","path":"/v1/deals/search","body":{"filter":{"assignedById":{"$eq":<ID>},"stageSemantic":{"$eq":"P"}}}}
]' | python3 scripts/vibe.py --batch --json
```

**Apply this pattern to all 7 scenarios.** Field name mapping:
| Old (UPPER_CASE) | New (camelCase) |
|---|---|
| `RESPONSIBLE_ID` | `responsibleId` |
| `ASSIGNED_BY_ID` | `assignedById` |
| `STAGE_SEMANTIC_ID` | `stageSemantic` |
| `DATE_CREATE` | `createdAt` |
| `DATE_MODIFY` | `updatedAt` |
| `CLOSED_DATE` | `closedAt` |
| `DEADLINE` | `deadline` |
| `STATUS` | `status` |
| `TITLE` | `title` |
| `OPPORTUNITY` | `opportunity` |
| `STAGE_ID` | `stageId` |
| `LAST_NAME` | `lastName` |
| `COMPANY_ID` | `companyId` |
| `OWNER_TYPE_ID` | `ownerTypeId` |
| `OWNER_ID` | `ownerId` |

Filter operator mapping:
| Old | New |
|---|---|
| `filter[>FIELD]=val` | `{"field":{"$gt":"val"}}` |
| `filter[>=FIELD]=val` | `{"field":{"$gte":"val"}}` |
| `filter[<FIELD]=val` | `{"field":{"$lt":"val"}}` |
| `filter[!FIELD]=val` | `{"field":{"$ne":"val"}}` |
| `filter[%FIELD]=val` | `{"field":{"$contains":"val"}}` |
| `filter[FIELD]=val` | `{"field":{"$eq":"val"}}` |

Presentation format (emoji + section headers) stays identical.

- [ ] **Step 2: Add 5 new scenarios**

Add after existing scenarios:

**Duplicates check:**
```markdown
### Duplicates check ("проверь дубли", "найди дубликаты")

```bash
python3 scripts/vibe.py --raw POST /v1/duplicates/find --body '{"type":"PHONE","values":["+79001234567"]}' --json
```
```

**Workflow start:**
```markdown
### Start workflow ("запусти процесс", "бизнес-процесс")

```bash
python3 scripts/vibe.py --raw POST /v1/workflows/start --body '{"templateId":1,"documentId":"DEAL_123"}' --confirm-write --json
```
```

**Call statistics:**
```markdown
### Call statistics ("статистика звонков", "отчёт по звонкам")

```bash
python3 scripts/vibe.py --raw GET /v1/calls/statistics --json
```
```

**Workday report:**
```markdown
### Workday report ("табель", "кто на работе")

```bash
python3 scripts/vibe.py --raw GET /v1/workday/status --json
```
```

**Feed post:**
```markdown
### Feed post ("напиши в ленту", "объявление в ленте")

```bash
python3 scripts/vibe.py posts --create --body '{"title":"Объявление","message":"Завтра корпоратив!"}' --confirm-write --json
```
```

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "feat: rewrite SKILL.md scenarios for Vibe + add 5 new scenarios"
```

---

### Task 9: Rewrite SKILL.md — Scheduled Tasks

**Files:**
- Modify: `SKILL.md:291-382` (scheduled tasks section)

- [ ] **Step 1: Rewrite all 5 existing scheduled task templates with `vibe.py` commands**

Apply the same field mapping and filter conversion from Task 8 Step 1. Each template's batch call becomes `echo '[...]' | vibe.py --batch --json`. Example for **Day plan**:

```bash
echo '[
  {"method":"GET","path":"/v1/calendar/events","body":{"ownerId":<ID>,"from":"<today_start>","to":"<today_end>"}},
  {"method":"POST","path":"/v1/tasks/search","body":{"filter":{"responsibleId":{"$eq":<ID>},"deadline":{"$lte":"<today_end>"},"status":{"$lt":5}},"order":{"deadline":"asc"}}}
]' | python3 scripts/vibe.py --batch --json
```

Apply same pattern to: Morning briefing, Evening summary, Weekly report, Overdue alert, New leads monitor.

- [ ] **Step 2: Add 2 new scheduled task templates**

**Duplicate monitor (weekly, Monday 10:00):**
```markdown
### Duplicate monitor (weekly, Monday 10:00)

Check CRM for potential duplicates by phone/email. Only notify if duplicates found.

```bash
python3 scripts/vibe.py --raw POST /v1/duplicates/find --body '{"type":"PHONE","values":["recent_contacts_phones"]}' --json
```

If results contain duplicates, list them. If no duplicates, do not send anything.
```

**Call digest (daily, workdays 17:00):**
```markdown
### Call digest (daily, workdays 17:00)

Summarize today's call statistics.

```bash
python3 scripts/vibe.py --raw GET '/v1/calls/statistics?from=<today_start>&to=<today_end>' --json
```

Present as: total calls, average duration, missed calls count.
```

- [ ] **Step 3: Commit**

```bash
git add SKILL.md
git commit -m "feat: rewrite SKILL.md scheduled tasks for Vibe + add 2 new templates"
```

---

## Chunk 3: Reference Files

### Task 10: Rewrite `references/access.md`

**Files:**
- Modify: `references/access.md`

- [ ] **Step 1: Replace entire content**

Rewrite to cover Vibe Platform key setup instead of webhook. Include:
1. Vibe key setup instructions (same as SKILL.md onboarding section)
2. Saving the key: `python3 scripts/vibe.py --raw GET /v1/me --json` (auto-saves on first call)
3. Replacing a key: edit `~/.config/bitrix24-skill/config.json` directly or delete and re-setup
4. Permissions / scopes section
5. MCP docs endpoint (unchanged)
6. Remove OAuth section (not applicable to Vibe)

- [ ] **Step 2: Commit**

```bash
git add references/access.md
git commit -m "feat: rewrite access.md for Vibe Platform key setup"
```

---

### Task 11: Rewrite `references/crm.md`

**Files:**
- Modify: `references/crm.md`

- [ ] **Step 1: Replace all method names and examples**

Key changes:
- Replace `crm.deal.list` with `vibe.py deals --json`
- Replace `crm.deal.add` with `vibe.py deals --create --body '{...}' --confirm-write --json`
- Replace filter syntax: `filter[>OPPORTUNITY]=10000` → `{"filter":{"opportunity":{"$gt":10000}}}`
- Replace UPPER_CASE fields with camelCase: `OPPORTUNITY` → `opportunity`, `STAGE_ID` → `stageId`, `ASSIGNED_BY_ID` → `assignedById`
- Update timeline methods to use `--raw` with `/v1/timeline-logs`
- Update stage history to use `--raw` with `/v1/stage-history`
- Keep entity type IDs table unchanged
- Keep MCP query suggestions updated

Follow the reference file format from spec Section 7: domain description, endpoint table, key fields, examples, filter examples, pitfalls.

- [ ] **Step 2: Commit**

```bash
git add references/crm.md
git commit -m "feat: rewrite crm.md for Vibe Platform"
```

---

### Task 12: Rewrite `references/tasks.md`

**Files:**
- Modify: `references/tasks.md`

- [ ] **Step 1: Read current file and rewrite**

Replace all `tasks.task.*` method calls with `vibe.py tasks` entity CRUD. Add time tracking via `--raw GET/POST /v1/tasks/:id/time`. Update field names to camelCase. Update filter syntax to MongoDB-style.

- [ ] **Step 2: Commit**

```bash
git add references/tasks.md
git commit -m "feat: rewrite tasks.md for Vibe Platform"
```

---

### Task 13: Rewrite remaining confirmed domain references

**Files:**
- Modify: `references/chat.md`
- Modify: `references/channels.md`
- Modify: `references/feed.md`
- Modify: `references/timeman.md`

These are domains with confirmed Vibe endpoints (Section 5.2 of spec).

- [ ] **Step 1: Rewrite `references/chat.md`**

Replace `im.*` methods with `--raw` calls. Endpoint table:

| Action | Command |
|--------|---------|
| Recent chats | `vibe.py --raw GET /v1/chats/recent --json` |
| Find chat | `vibe.py --raw GET /v1/chats/find --body '{"query":"..."}' --json` |
| Get messages | `vibe.py --raw GET /v1/chats/<id>/messages --json` |
| Send message | `vibe.py --raw POST /v1/chats/<id>/messages --body '{"message":"..."}' --confirm-write --json` |
| Send notification | `vibe.py --raw POST /v1/notifications --body '{"userId":5,"message":"..."}' --confirm-write --json` |

- [ ] **Step 2: Rewrite `references/channels.md`**

Update to use Vibe equivalents. Read current file first to understand channel-specific methods. Map each `im.chat.channel.*` method to the Vibe equivalent (likely under `/v1/chats` with channel-specific params or a separate `/v1/channels` endpoint — verify at implementation).

- [ ] **Step 3: Rewrite `references/feed.md`**

Replace `log.blogpost.*` with `vibe.py posts` entity CRUD:

| Action | Command |
|--------|---------|
| List posts | `vibe.py posts --json` |
| Create post | `vibe.py posts --create --body '{"title":"...","message":"..."}' --confirm-write --json` |
| Update post | `vibe.py posts/<id> --update --body '{"message":"..."}' --confirm-write --json` |
| Delete post | `vibe.py posts/<id> --delete --confirm-destructive --json` |

- [ ] **Step 4: Rewrite `references/timeman.md`**

Replace `timeman.*` with `--raw` calls:

| Action | Command |
|--------|---------|
| Open day | `vibe.py --raw POST /v1/workday/open --confirm-write --json` |
| Close day | `vibe.py --raw POST /v1/workday/close --confirm-write --json` |
| Pause | `vibe.py --raw POST /v1/workday/pause --confirm-write --json` |
| Status | `vibe.py --raw GET /v1/workday/status --json` |
| Settings | `vibe.py --raw GET /v1/workday/settings --json` |
| Schedule | `vibe.py --raw GET /v1/workday/schedule --json` |

- [ ] **Step 5: Commit all 4**

```bash
git add references/chat.md references/channels.md references/feed.md references/timeman.md
git commit -m "feat: rewrite chat, channels, feed, timeman references for Vibe"
```

---

### Task 14: Create new reference files (6 new domains)

**Files:**
- Create: `references/bots.md`
- Create: `references/telephony.md`
- Create: `references/workflows.md`
- Create: `references/ecommerce.md`
- Create: `references/duplicates.md`
- Create: `references/timeline-logs.md`

- [ ] **Step 1: Create `references/bots.md`**

Cover: bot registration (`POST /v1/bots`), long-polling events (`GET /v1/bots/:id/events`), sending messages (`POST /v1/bots/:id/messages`), typing indicator, slash-commands, file attachments. All via `--raw` mode.

- [ ] **Step 2: Create `references/telephony.md`**

Cover: call registration (`POST /v1/calls/register`), finish (`/finish`), transcript attachment (`/transcript/attach`), auto-call/TTS, statistics (`GET /v1/calls/statistics`). Note that this creates call records, not actual voice calls.

- [ ] **Step 3: Create `references/workflows.md`**

Cover: start process (`POST /v1/workflows/start`), terminate, list instances, list templates, complete workflow task, triggers (fire, add, delete, list).

- [ ] **Step 4: Create `references/ecommerce.md`**

Cover: `vibe.py payments` entity CRUD, `vibe.py basket-items` CRUD, `vibe.py order-statuses` CRUD.

- [ ] **Step 5: Create `references/duplicates.md`**

Cover: `POST /v1/duplicates/find` via `--raw`. Search by phone, email, or both. Example queries for common duplicate-check scenarios.

- [ ] **Step 6: Create `references/timeline-logs.md`**

Cover: CRUD `/v1/timeline-logs`, pin/unpin, bind, notes. Icon codes and color options.

- [ ] **Step 7: Commit all 6**

```bash
git add references/bots.md references/telephony.md references/workflows.md references/ecommerce.md references/duplicates.md references/timeline-logs.md
git commit -m "feat: add 6 new reference files for bots, telephony, workflows, ecommerce, duplicates, timeline-logs"
```

---

### Task 15: Rewrite `references/troubleshooting.md`

**Files:**
- Modify: `references/troubleshooting.md`

- [ ] **Step 1: Replace entire content**

Replace webhook-based diagnostics with Vibe Platform error handling:
- Replace `check_webhook.py` → `check_connection.py`
- Replace webhook format/DNS/HTTP checks → key validation + `/v1/me` probe
- Map HTTP error codes: 401 (invalid key), 403 (revoked/scope denied), 422 (Bitrix error), 429 (rate limit), 502 (unavailable)
- Keep user-facing style rules (plain business language, no jargon, autonomous retry)
- Update response templates for Vibe-specific errors

- [ ] **Step 2: Commit**

```bash
git add references/troubleshooting.md
git commit -m "feat: rewrite troubleshooting.md for Vibe Platform errors"
```

---

### Task 16: Rewrite unverified domain references (10 files)

**Files:**
- Modify: `references/calendar.md`
- Modify: `references/drive.md`
- Modify: `references/files.md`
- Modify: `references/users.md`
- Modify: `references/projects.md`
- Modify: `references/smartprocess.md`
- Modify: `references/products.md`
- Modify: `references/quotes.md`
- Modify: `references/sites.md`
- Modify: `references/openlines.md`

These domains have unverified Vibe endpoints (Section 10 of spec). For each file:

1. Check the Vibe API docs or test with a real key to discover actual endpoints
2. If entity CRUD is available → use standard `vibe.py {entity}` format
3. If special endpoints exist → use `--raw` mode with discovered paths
4. **If endpoints don't exist in Vibe** → keep the reference file but rewrite it to use `vibe.py --raw POST /v1/bitrix --body '{"method":"old.method.name","params":{...}}'` as a passthrough to Bitrix24 REST API. Add a note at the top: "This domain uses Bitrix24 REST passthrough — endpoints may differ from standard Vibe entity format."

- [ ] **Step 1: Rewrite `references/calendar.md`**

Assume `--raw GET/POST /v1/calendar/events` (verify). Keep critical notes: no `calendar.get` method, mandatory `type` and `ownerId`.

- [ ] **Step 2: Rewrite `references/drive.md`**

Assume `--raw GET/POST /v1/drive/files` (verify).

- [ ] **Step 3: Rewrite `references/files.md`**

Update file upload strategy for Vibe (likely multipart or base64 in body).

- [ ] **Step 4: Rewrite `references/users.md`**

`/v1/me` is confirmed. For user lists, assume `--raw GET /v1/users` (verify).

- [ ] **Step 5: Rewrite `references/projects.md`**

Assume `--raw GET/POST /v1/projects` (verify).

- [ ] **Step 6: Rewrite `references/smartprocess.md`**

Assume `--raw GET/POST /v1/crm/items` (verify).

- [ ] **Step 7: Rewrite `references/products.md`**

Assume `--raw GET/POST /v1/products` (verify).

- [ ] **Step 8: Rewrite `references/quotes.md`**

Assume `--raw GET/POST /v1/quotes` (verify).

- [ ] **Step 9: Rewrite `references/sites.md`**

Assume `--raw GET/POST /v1/sites` (verify).

- [ ] **Step 10: Rewrite `references/openlines.md`**

Assume `--raw GET/POST /v1/openlines` (verify).

- [ ] **Step 11: Commit all**

```bash
git add references/calendar.md references/drive.md references/files.md references/users.md references/projects.md references/smartprocess.md references/products.md references/quotes.md references/sites.md references/openlines.md
git commit -m "feat: rewrite 10 unverified domain references for Vibe Platform"
```

---

## Chunk 4: Supporting Files and Cleanup

### Task 17: Update `CLAUDE.md`

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Replace all content**

Key changes:
- "What This Is": Replace "webhook" with "Vibe Platform"
- "Architecture": Replace "webhook URL" with "Vibe API key", update script names
- "Key Files": Replace `bitrix24_call.py`, `bitrix24_batch.py`, `bitrix24_config.py`, `save_webhook.py`, `check_webhook.py` with `vibe.py`, `vibe_config.py`, `check_connection.py`
- "Common Commands": Replace all command examples with `vibe.py` equivalents
- "Publishing Workflow": Keep unchanged (operates on the skill package, not the API)
- "Critical Design Decisions": Update for Vibe (no webhook, camelCase fields, MongoDB filters)
- "Bitrix24 API Patterns": Update with Vibe patterns (RESTful endpoints, camelCase, page/pageSize)

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "feat: update CLAUDE.md for Vibe Platform migration"
```

---

### Task 18: Update `CHANGELOG.md`

**Files:**
- Modify: `CHANGELOG.md`

- [ ] **Step 1: Add v1.0.0 entry at the top**

```markdown
## [1.0.0] - 2026-03-24

### Changed
- **BREAKING:** Migrated from webhook-based API to Vibe Platform (vibecode.bitrix24.tech)
- Authentication now uses Vibe API key instead of webhook URL
- All CLI scripts replaced: `bitrix24_call.py` → `vibe.py`, `bitrix24_config.py` → `vibe_config.py`, `check_webhook.py` → `check_connection.py`
- Field names changed from UPPER_CASE to camelCase
- Filter syntax changed from key-prefix (`>=FIELD`) to MongoDB-style (`{"$gte": value}`)
- Pagination changed from `start` to `page`/`pageSize`
- All reference files rewritten with new command format

### Added
- 6 new domains: Bots, Telephony, Workflows, E-commerce, Duplicates, Timeline Logs
- 5 new scenarios: duplicates check, workflow start, call statistics, workday report, feed post
- 2 new scheduled task templates: duplicate monitor, call digest
- Config migration: old webhook configs automatically backed up

### Removed
- Webhook-based scripts: `bitrix24_call.py`, `bitrix24_batch.py`, `bitrix24_config.py`, `save_webhook.py`, `check_webhook.py`
- Webhook setup flow in `access.md`
```

- [ ] **Step 2: Commit**

```bash
git add CHANGELOG.md
git commit -m "docs: add v1.0.0 changelog entry for Vibe Platform migration"
```

---

### Task 19: Update `docs/index.html`

**Files:**
- Modify: `docs/index.html`

- [ ] **Step 1: Read the file to understand its structure**

Read `docs/index.html` to find the webhook-related text.

- [ ] **Step 2: Replace webhook mentions**

Find and replace:
- "webhook" → "Vibe Platform" in all language sections
- "вебхук" → "Vibe Platform" in Russian text
- Add link to `vibecode.bitrix24.tech` in setup instructions
- Update version in footer to v1.0.0

- [ ] **Step 3: Commit**

```bash
git add docs/index.html
git commit -m "feat: update landing page for Vibe Platform"
```

---

### Task 20: Update `agents/openai.yaml`

**Files:**
- Modify: `agents/openai.yaml`

- [ ] **Step 1: Read the file**

Read current content.

- [ ] **Step 2: Update description**

Replace any mention of "webhook" with "Vibe Platform". Update the description to reflect the new architecture.

- [ ] **Step 3: Commit**

```bash
git add agents/openai.yaml
git commit -m "chore: update openai.yaml description for Vibe Platform"
```

---

### Task 21: Verify `scripts/publish.sh` and `scripts/auto_update.sh`

**Files:**
- Verify: `scripts/publish.sh`
- Verify: `scripts/auto_update.sh`
- Verify: `scripts/changelog_to_json.py`

- [ ] **Step 1: Check `publish.sh` for old script references**

Run: `grep -n "bitrix24_call\|bitrix24_batch\|check_webhook\|save_webhook\|bitrix24_config" scripts/publish.sh`
Expected: no matches (publish.sh operates on git/clawhub, not on API scripts)

- [ ] **Step 2: Check `auto_update.sh` for old references**

Run: `grep -n "bitrix24_call\|bitrix24_batch\|check_webhook\|save_webhook\|bitrix24_config" scripts/auto_update.sh`
Expected: no matches

- [ ] **Step 3: Check `changelog_to_json.py`**

Run: `grep -n "bitrix24_call\|bitrix24_batch\|check_webhook\|save_webhook\|bitrix24_config" scripts/changelog_to_json.py`
Expected: no matches

- [ ] **Step 4: If any matches found, update those files and commit**

---

### Task 22: Final verification

- [ ] **Step 1: Check for any remaining references to old scripts across the entire project**

Run: `grep -rn "bitrix24_call\|bitrix24_batch\|bitrix24_config\|save_webhook\|check_webhook" --include="*.md" --include="*.py" --include="*.sh" --include="*.yaml" --include="*.html" .`
Expected: no matches (all references should be migrated)

- [ ] **Step 2: Check for remaining webhook references**

Run: `grep -rn "webhook_url\|webhook URL\|webhook" --include="*.md" --include="*.py" . | grep -v "mcp-workflow\|CHANGELOG\|\.bak"`
Expected: minimal matches (only historical mentions in CHANGELOG, or MCP docs context where "webhook" is a Bitrix24 concept)

- [ ] **Step 3: Verify all Python scripts have valid syntax**

Run: `python3 -c "import py_compile; [py_compile.compile(f, doraise=True) for f in ['scripts/vibe.py', 'scripts/vibe_config.py', 'scripts/check_connection.py']]"`
Expected: no errors

- [ ] **Step 4: Verify file count**

Run: `ls references/*.md | wc -l`
Expected: 25 (18 rewritten + 6 new + 1 mcp-workflow.md unchanged = 25 total)

- [ ] **Step 5: Final commit if any cleanup was needed**

```bash
git add -A
git commit -m "chore: final cleanup after Vibe Platform migration"
```
