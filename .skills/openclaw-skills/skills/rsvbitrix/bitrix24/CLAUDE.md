# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Bitrix24 skill for OpenClaw — an agent that connects to Bitrix24 via Vibe Platform (vibecode.bitrix24.tech) and lets non-technical users (company directors) manage CRM, tasks, calendar, etc. through natural language. Published to ClawHub as `bitrix24`.

## Architecture

Two-layer design:

1. **Python scripts** (`scripts/`) — make REST calls via Vibe Platform, manage API key config, diagnose connectivity. No external dependencies beyond Python stdlib (`urllib`, `json`, `ssl`, `socket`).
2. **MCP documentation server** (`https://mcp-dev.bitrix24.tech/mcp`) — provides live method/event/article lookups via `bitrix-search`, `bitrix-method-details`, etc.

All REST calls go through a single Vibe API key stored in `~/.config/bitrix24-skill/config.json`.

## Key Files

- `SKILL.md` — **the most important file**. Agent entrypoint: frontmatter (metadata, tags, MCP config), user interaction rules, technical rules, domain reference index. This is what the bot reads to know how to behave.
- `scripts/vibe.py` — unified CLI for entity CRUD, raw endpoints, batch, auto-pagination. Usage: `python3 scripts/vibe.py deals --json`. Supports `--iterate`, `--dry-run`, `--confirm-write`, `--create`, `--update`, `--delete`, `--batch`, `--body`.
- `scripts/vibe_config.py` — config management: `load_key()`, `persist_key()`, `mask_key()`, `get_cached_user()`, `migrate_old_config()`
- `scripts/check_connection.py` — diagnostics: key validation + `/v1/me` probe
- `references/*.md` — 25 domain reference files with exact endpoint names, parameters, filter syntax, examples
- `docs/index.html` — GitHub Pages landing site (5 languages: EN/RU/ZH/ES/FR, auto-detects browser language)
- `agents/openai.yaml` — OpenAI/OpenClaw agent metadata

## Common Commands

```bash
# List entities
python3 scripts/vibe.py deals --json

# Search with filters
python3 scripts/vibe.py deals/search --body '{"filter":{"opportunity":{"$gte":100000}}}' --json

# Auto-paginate (collect all pages)
python3 scripts/vibe.py deals --iterate --json

# Dry-run (preview without executing)
python3 scripts/vibe.py deals --create --body '{"title":"Test"}' --dry-run --json

# Write operations require --confirm-write
python3 scripts/vibe.py deals --create --body '{"title":"Test"}' --confirm-write --json

# Diagnose connection
python3 scripts/check_connection.py --json

# Publish to ClawHub (check current version first)
npx clawhub inspect bitrix24 --versions
npx clawhub publish . --version X.Y.Z

# Batch call (multiple operations in one request)
echo '[{"method":"GET","url":"/v1/tasks","params":{"filter":{"responsibleId":5}}},{"method":"GET","url":"/v1/deals","params":{"filter":{"assignedById":5}}}]' | python3 scripts/vibe.py --batch --json

# Preview landing page locally
# Use Claude Preview with "landing" config from .claude/launch.json (port 8090)

# Install on remote (full PATH required)
ssh slon-mac "export PATH=\$HOME/.nvm/versions/node/*/bin:/opt/homebrew/bin:/usr/local/bin:\$PATH && npx clawhub install bitrix24 --version X.Y.Z --force"

# Restart gateway after install
ssh slon-mac "export PATH=\$HOME/.nvm/versions/node/*/bin:/opt/homebrew/bin:/usr/local/bin:\$PATH && openclaw gateway restart"
```

## Publishing Workflow

### Quick publish (recommended)

```bash
# 1. Update CHANGELOG.md with new version entry
# 2. Run the publish script:
bash scripts/publish.sh X.Y.Z
```

This script automatically:
- Updates version in `docs/index.html` footer
- Generates `docs/changelog.json` from CHANGELOG.md
- Commits, pushes, and publishes to ClawHub

### Manual steps (if needed)

1. Commit and push to `origin/main` (`https://github.com/rsvbitrix/bitrix24-skill.git`)
2. `npx clawhub publish . --version X.Y.Z` — publishes to ClawHub, triggers security scan (~1-2 min)
3. Wait ~90 seconds for scan to pass before installing (check with `npx clawhub inspect bitrix24`)
4. On slon-mac: `npx clawhub install bitrix24 --version X.Y.Z --force` (needs full PATH, see Common Commands)
5. Restart OpenClaw gateway: `openclaw gateway restart`

### Auto-update

A scheduled task (`bitrix24-auto-update`) checks ClawHub every 2 hours and auto-installs new versions on slon-mac. Manual install is only needed if you want it immediately.

**Known issue:** ClawHub rate-limits install requests. If you get `Rate limit exceeded`, wait 2-3 minutes and retry.

## Critical Design Decisions

- **No env vars** — API key in config JSON only, no `.env` files, no `BITRIX24_API_KEY`
- **SKILL.md rules go first** — user interaction rules are at the top before any technical content, because the bot must see them before anything else
- **Reference files use `vibe.py` examples** — not curl, not BX24.js. All examples are copy-paste ready for the agent.
- **Filter operators are MongoDB-style** — `{"$gte": value}`, `{"$lte": value}`, `{"$not": value}`. This is different from the old key-prefix syntax.
- **Fields are camelCase** in Vibe API — `opportunityAmount`, `assignedById`, `responsibleId`, not UPPER_CASE.
- **No `calendar.get`** — it doesn't exist. The correct method is `calendar.event.get` with mandatory `type` and `ownerId`. This was a real bot failure that triggered a full MCP audit.
- **Single skill, not multi-skill** — we intentionally keep everything in one skill (not split into 10 separate ones like the analysis doc suggests). One skill = simpler UX for the director.

## Bitrix24 API Patterns

- Entity endpoints: `/v1/{entity}` (RESTful) — e.g., `/v1/deals`, `/v1/contacts`, `/v1/tasks`
- Entity type IDs: 1=lead, 2=deal, 3=contact, 4=company, 7=quote, 31=smart invoice, 128+=custom
- Universal API: `crm.item.*` works across all entity types with `entityTypeId` param
- Fields: camelCase in Vibe API — `title`, `opportunityAmount`, `assignedById`
- Pagination: `page`/`pageSize` parameters (not `start`)
- Filters: MongoDB-style operators — `{"$gte": value}`, `{"$lte": value}`, `{"$not": value}`
- Dates: ISO 8601 for datetime, `YYYY-MM-DD` for date-only
- Batch API: POST array of operations, returns results array
- No REST API for emails: `mailservice.*` only configures SMTP/IMAP, cannot send/read emails
