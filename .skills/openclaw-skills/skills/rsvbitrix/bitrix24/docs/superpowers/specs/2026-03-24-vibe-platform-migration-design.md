# Vibe Platform Migration Design

**Date:** 2026-03-24
**Status:** Draft
**Scope:** Full migration of Bitrix24 Skill from webhook-based API to Vibe Platform (vibecode.bitrix24.tech)

---

## 1. Summary

Migrate the entire Bitrix24 skill from webhook-based architecture (per-portal webhooks, direct REST API calls) to the Vibe Platform (vibecode.bitrix24.tech). Authentication switches from webhook URLs to Vibe API keys. All scripts, references, and onboarding flow are rewritten. Six new domains are added: Bots, Telephony, Workflows, Duplicates, E-commerce, Infrastructure.

---

## 2. Architecture

### 2.1 Single Script: `vibe.py`

One unified CLI script replaces `bitrix24_call.py`, `bitrix24_batch.py`, `bitrix24_config.py`, `save_webhook.py`, `check_webhook.py`.

**Base URL:** `https://vibecode.bitrix24.tech`

**Auth:** `Authorization: Bearer {api_key}` header on every request.

**Modes:**

| Mode | Flag | Purpose |
|------|------|---------|
| Entity CRUD | `vibe.py {entity} [--list\|--create\|--update\|--delete]` | Standard entities (deals, contacts, tasks, etc.) |
| Raw endpoint | `vibe.py --raw {HTTP_VERB} {path}` | Non-entity endpoints (bots, telephony, workflows). `{HTTP_VERB}` is GET, POST, PUT, or DELETE. |
| Batch | `vibe.py --batch` | Multiple operations in one call, JSON array from stdin. Each element: `{"method": "GET\|POST\|...", "path": "/v1/...", "body": {}}`. |
| Iterate | `vibe.py {entity} --iterate` | Auto-pagination, collects all pages |

**Safety flags:**
- `--confirm-write` — required for create/update operations
- `--confirm-destructive` — required for delete operations
- `--dry-run` — shows what would happen without executing

**Sub-resource operations** (search, aggregate, fields):
- `vibe.py deals/search --body '{"filter":{...}}' --json` — search with filters
- `vibe.py deals/aggregate --body '{"field":"opportunity","function":"sum"}' --json` — aggregation
- `vibe.py deals/fields --json` — list available fields

These are path-based, not flag-based: `{entity}/search`, `{entity}/aggregate`, `{entity}/fields`.

**Output:** Always `--json` flag, returns raw JSON for agent parsing.

### 2.2 Configuration Module: `vibe_config.py`

Functions:
- `load_key()` — reads `api_key` from `~/.config/bitrix24-skill/config.json`
- `persist_key(key)` — saves key to config
- `mask_key(key)` — returns masked format (first 10 chars + `****` + last 2), e.g. `vibe_api_ab****cd`
- `get_cached_user()` — returns cached `user_id` and `timezone` from config
- `migrate_old_config()` — detects old `webhook_url` in config, backs up to `config.json.bak`, removes `webhook_url`, prompts for Vibe key

### 2.3 Diagnostics: `check_connection.py`

Calls `GET /v1/me`, uses `mask_key()` from `vibe_config.py` for output. Returns JSON:
```json
{
  "key_found": true,
  "key_prefix": "vibe_api_ab****cd",
  "connection_ok": true,
  "scopes": ["crm", "task", "im"],
  "portal": "company.bitrix24.ru",
  "user": "Иван Петров"
}
```

---

## 3. File Structure

### 3.1 Files to Delete
- `scripts/bitrix24_call.py`
- `scripts/bitrix24_batch.py`
- `scripts/bitrix24_config.py`
- `scripts/save_webhook.py`
- `scripts/check_webhook.py`

### 3.2 New Files
- `scripts/vibe.py` — unified CLI script
- `scripts/vibe_config.py` — configuration module
- `scripts/check_connection.py` — diagnostics

### 3.3 New Reference Files
- `references/bots.md` — Bot Platform (registration, long-polling, messages, slash-commands)
- `references/telephony.md` — calls, TTS, callbacks, transcription, statistics
- `references/workflows.md` — business processes, triggers, instances, workflow tasks
- `references/ecommerce.md` — payments, basket, order statuses
- `references/duplicates.md` — duplicate search
- `references/timeline-logs.md` — extended timeline (pin, bind, notes, icons)

### 3.4 Files to Rewrite
- `SKILL.md` — complete rewrite (onboarding, domains, scenarios, examples)
- All 18 existing `references/*.md` files — examples changed to `vibe.py`, camelCase fields, MongoDB-style filters:
  - `access.md` — rewrite to cover Vibe key onboarding and `/v1/me` (replaces webhook setup)
  - `crm.md`, `tasks.md`, `calendar.md`, `chat.md`, `channels.md`, `openlines.md`, `drive.md`, `files.md`, `users.md`, `projects.md`, `feed.md`, `timeman.md`, `smartprocess.md`, `products.md`, `quotes.md`, `sites.md` — domain references
  - `troubleshooting.md` — rewrite with Vibe error codes (401/403/422/429/502) replacing webhook diagnostics

### 3.5 Files Unchanged
- `references/mcp-workflow.md` — MCP documentation server reference, not affected by migration

### 3.6 Files to Update
- `CLAUDE.md` — command examples
- `CHANGELOG.md` — migration entry
- `docs/index.html` — landing page text
- `agents/openai.yaml` — description
- `scripts/publish.sh` — update any references to old script names
- `scripts/auto_update.sh` — verify compatibility
- `scripts/changelog_to_json.py` — no changes expected (operates on CHANGELOG.md format)

---

## 4. Configuration and Onboarding

### 4.1 Config Format

File: `~/.config/bitrix24-skill/config.json`
```json
{
  "api_key": "vibe_api_...",
  "base_url": "https://vibecode.bitrix24.tech",
  "user_id": 5,
  "timezone": "Europe/Moscow"
}
```

Fields `user_id` and `timezone` are cached after the first successful `/v1/me` call.

### 4.2 Onboarding Flow

When `api_key` is not found in config, the skill shows step-by-step instructions:

1. Open **vibecode.bitrix24.tech**
2. Sign in with Bitrix24 credentials
3. Create a new key in the dashboard
4. Select all scopes
5. Copy the key (shown only once)
6. Paste it into the chat

After receiving the key:
1. Save via `vibe_config.py`
2. Call `GET /v1/me` to validate
3. Cache `user_id` and `timezone`
4. Confirm connection to the user

### 4.3 Error Recovery

- Invalid key (401/403): prompt to create a new key
- Revoked key: same prompt
- Missing scope (403 SCOPE_DENIED): prompt to create a new key with full permissions

No technical jargon shown to users — no "API key", "scope", "endpoint".

---

## 5. Entity Endpoint Mapping

### 5.1 Standard Entities (CRUD via `/v1/{entity}`)

| Entity | Vibe Endpoint | Old Method | Scope |
|--------|--------------|------------|-------|
| deals | `/v1/deals` | `crm.deal.*` | crm |
| contacts | `/v1/contacts` | `crm.contact.*` | crm |
| companies | `/v1/companies` | `crm.company.*` | crm |
| leads | `/v1/leads` | `crm.lead.*` | crm |
| tasks | `/v1/tasks` | `tasks.task.*` | task |
| posts | `/v1/posts` | `log.blogpost.*` | log |
| payments | `/v1/payments` | `sale.payment.*` | sale |
| basket-items | `/v1/basket-items` | `sale.basketitem.*` | sale |
| order-statuses | `/v1/order-statuses` | `sale.status.*` | sale |

All entities support: list, get, create, update, delete, search, aggregate, fields.

### 5.2 Special Endpoints (via `--raw`)

| Domain | Key Endpoints | Scope |
|--------|--------------|-------|
| Chats | `GET /v1/chats/recent`, `/find`, `GET/POST /v1/chats/:id/messages` | im |
| Notifications | `POST /v1/notifications` | im |
| Bots | `POST /v1/bots`, `GET /v1/bots/:id/events`, `POST /v1/bots/:id/messages` | imbot |
| Telephony | `POST /v1/calls/register`, `/finish`, `/transcript/attach`, `GET /v1/calls/statistics` | call |
| Workflows | `POST /v1/workflows/start`, `/terminate`, `GET /v1/workflows/instances` | bizproc |
| Triggers | `POST /v1/triggers/fire`, `/add`, `/delete`, `GET /v1/triggers/list` | crm |
| Timeline | CRUD `/v1/timeline-logs`, `/pin`, `/unpin`, `/bind`, `/notes` | crm |
| Workday | `POST /v1/workday/open`, `/close`, `/pause`, `GET /v1/workday/status` | timeman |
| Time Tracking | `GET/POST /v1/tasks/:id/time` | task |
| Duplicates | `POST /v1/duplicates/find` | crm |
| Stage History | `GET /v1/stage-history` | crm |
| Infrastructure | CRUD `/v1/infra/servers` | — |

### 5.3 API Differences from Webhook

| Aspect | Webhook (old) | Vibe (new) |
|--------|--------------|-----------|
| Fields | UPPER_CASE (`STAGE_ID`) | camelCase (`stageId`) |
| Pagination | `start` param | `page`/`pageSize` params |
| Response | `{"result": [], "total": N, "next": 50}` | `{"success": true, "data": [], "total": N}` |
| Filters | Key-prefix (`>=DEADLINE`) | MongoDB-style (`{"$gte": value}`) |

Filter operators: `$eq`, `$ne`, `$gt`, `$gte`, `$lt`, `$lte`, `$contains`, `$in`.

---

## 6. SKILL.md Structure

### 6.1 Sections

1. **Frontmatter** — trigger phrases updated for new domains
2. **Onboarding** — Vibe key setup (section 4.2)
3. **Interaction rules** — preserved (read=immediate, no jargon, write=confirm, silent retry, proactive insights)
4. **Technical rules** — rewritten for Vibe API (entity CRUD, filters, pagination, batch, raw, safety flags)
5. **Domains** — expanded from 12 to 18 (add: Bots, Telephony, Workflows, Duplicates, E-commerce, Infrastructure)
6. **Scenarios** — 7 existing updated + 5 new (duplicates check, workflow start, call stats, workday report, feed post)
7. **Scheduled task templates** — 5 existing updated + 2 new (duplicate monitor, call digest)

---

## 7. Reference File Format

Each reference file follows a consistent structure:

1. Domain description (1-2 sentences)
2. Endpoint table (action, command)
3. Key fields (camelCase)
4. Copy-paste ready examples using `vibe.py`
5. MongoDB-style filter examples
6. Common pitfalls

Example format:
```
## Deals

| Action | Command |
|--------|---------|
| List | `vibe.py deals --json` |
| By ID | `vibe.py deals/123 --json` |
| Create | `vibe.py deals --create --body '{"title":"Deal","stageId":"NEW"}' --confirm-write --json` |
| Search | `vibe.py deals/search --body '{"filter":{"opportunity":{"$gte":100000}}}' --json` |

Key fields: title, stageId, opportunity, currencyId, contactId, companyId, assignedById
```

### 7.1 Existing Files to Rewrite (18)

access.md, crm.md, tasks.md, calendar.md, chat.md, channels.md, openlines.md, drive.md, files.md, users.md, projects.md, feed.md, timeman.md, smartprocess.md, products.md, quotes.md, sites.md, troubleshooting.md

### 7.2 New Files (6)

bots.md, telephony.md, workflows.md, ecommerce.md, duplicates.md, timeline-logs.md

---

## 8. Error Handling

| HTTP | Code | User-Facing Message |
|------|------|-------------------|
| 401 | AUTH_REQUIRED | Key invalid, create new one |
| 403 | KEY_REVOKED | Key disabled, create new one |
| 403 | SCOPE_DENIED | Missing permissions, create key with full access |
| 404 | NOT_FOUND | Record not found |
| 422 | BITRIX_ERROR | No retry; show "Битрикс24 вернул ошибку, попробуйте позже" |
| 429 | RATE_LIMIT | Auto-pause ~45s + retry (invisible to user) |
| 502 | BITRIX_UNAVAILABLE | Portal temporarily unavailable |
| 400 | VALIDATION_ERROR | Log only (agent error) |
| 400 | BATCH_TOO_LARGE | Auto-split into 50-item chunks |
| 500 | INTERNAL_ERROR | Service temporarily unavailable |

Retry logic:
- 429 → wait `retry-after` or 45s → up to 3 retries
- 502 → retry after 5s → up to 2 retries
- 422/500 → no retry

---

## 9. Migration Strategy

- Single major version release (1.0.0)
- All webhook scripts deleted, no backward compatibility shims
- Users with old config (containing `webhook_url`) see onboarding for Vibe key
- CHANGELOG entry: "Version 1.0 — migration to Vibe Platform. Webhooks no longer supported."

---

## 10. Unverified Domains

The following 9 domains exist in current references but are NOT in the confirmed entity list (Section 5.1). Their Vibe endpoint style is unknown:

| Domain | Current Reference | Implementation Strategy |
|--------|------------------|------------------------|
| Calendar | `calendar.md` | Assume `--raw` calls (`GET/POST /v1/calendar/events`). Verify at implementation. |
| Drive | `drive.md` | Assume `--raw` calls (`GET/POST /v1/drive/files`). Verify at implementation. |
| Users | `users.md` | `/v1/me` confirmed; for user lists assume `--raw` (`GET /v1/users`). Verify. |
| Projects | `projects.md` | Assume `--raw` (`GET/POST /v1/projects`). Verify. |
| Smart Processes | `smartprocess.md` | Assume `--raw` (`GET/POST /v1/crm/items`). Verify. |
| Products | `products.md` | Assume `--raw` (`GET/POST /v1/products`). Verify. |
| Quotes | `quotes.md` | Assume `--raw` (`GET/POST /v1/quotes`). Verify. |
| Sites | `sites.md` | Assume `--raw` (`GET/POST /v1/sites`). Verify. |
| Open Lines | `openlines.md` | Assume `--raw` (`GET/POST /v1/openlines`). Verify. |

**Implementation approach:** During implementation, for each domain: (1) check Vibe API docs or test with a real key, (2) if entity CRUD is available, use standard mode, (3) if not, use `--raw` mode with the actual endpoints discovered. Reference files for these domains will be written with the verified endpoints.

## 11. Migration Config Handling

When old config (`~/.config/bitrix24-skill/config.json`) contains `webhook_url`:
1. `vibe_config.py` detects old format via `migrate_old_config()`
2. Backs up to `config.json.bak`
3. Removes `webhook_url` from config
4. Skill triggers onboarding flow for Vibe key

## 12. Implementation Phases

Recommended execution order:
1. **Phase 1 — Scripts:** Create `vibe.py`, `vibe_config.py`, `check_connection.py`. Delete old scripts.
2. **Phase 2 — SKILL.md:** Full rewrite with new onboarding, domains, scenarios.
3. **Phase 3 — Confirmed references:** Rewrite references for domains with known endpoints (crm, tasks, chat, feed, timeman, ecommerce, bots, telephony, workflows, duplicates, timeline-logs).
4. **Phase 4 — Unverified references:** Verify and rewrite remaining 9 domain references.
5. **Phase 5 — Supporting files:** CLAUDE.md, CHANGELOG, landing page, agents metadata, publishing scripts.
