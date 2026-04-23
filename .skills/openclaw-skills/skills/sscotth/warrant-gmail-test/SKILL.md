---
name: gmail
description: |
  Call Gmail through warrant-claw — a policy-gated proxy that evaluates
  every request against a Cedar policy bound to the calling API key
  before touching Gmail. Send, read, search, label, draft, thread,
  trash, and delete, each gated by rules Gmail itself can't express
  ("send to @example.com only, max 5/hour" is a first-class rule here).
  Use this skill to call Gmail with per-agent, fine-grained access
  controls.
homepage: https://warrantclaw.com
version: 0.0.4
metadata:
  openclaw:
    emoji: ✉️
    homepage: https://warrantclaw.com
    requires:
      env:
        - WARRANTCLAW_API_KEY
    primaryEnv: WARRANTCLAW_API_KEY
---

# Gmail (via Warrant Claw)

Call Gmail through warrant-claw, a policy-gated proxy. Every request is
evaluated against a Cedar policy bound to the calling API key **before**
Gmail is touched.

The differentiator: Cedar expresses access controls Gmail doesn't. "Allow
`gmail.send` only to `@example.com` recipients, max 5/hour, weekdays
9am–6pm UTC" is a first-class rule here.

## Quick start

```bash
curl -X POST https://gmail-proxy.warrantclaw.com/tools/gmail.list \
  -H "Authorization: Bearer $WARRANTCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"max_results": 5}'
```

On success: `{"messages": [{"id", "threadId", "subject"}, ...], "resultSizeEstimate": N}`.

## Base URL

```
https://gmail-proxy.warrantclaw.com
```

Override with `WARRANTCLAW_BASE_URL` for self-hosted instances.

## Authentication

All endpoints except `GET /health` require:

```
Authorization: Bearer $WARRANTCLAW_API_KEY
```

Keys are prefixed `sk_` and have the shape `sk_XXXXXXXXXXXXXXXX…`.

### Getting a key

The human running this agent mints a key at the Warrant Claw dashboard:

1. Sign in at https://dash.warrantclaw.com
2. Connect Gmail via the Pipes widget
3. Mint an API key
4. Pick a policy preset (or bind custom Cedar)
5. Copy the `sk_…` into the agent's environment as `WARRANTCLAW_API_KEY`

## Policy model

Every tool call flows through Cedar. Cedar evaluates

```
permit(principal, action == Action::"<tool-id>", resource) when { ... };
```

against a context object the proxy builds from the request. If no matching
`permit` clause fires, the call is denied and the upstream service is never
touched.

### Context attributes

Every action populates the same context shape. Custom Cedar can gate on any
of these:

| Attribute | Type | Notes |
|---|---|---|
| `to_domain` | `string[]` | Recipient domains, deduped, lowercase. Empty for read-only actions. |
| `recipient_count` | `number` | Count of `to` entries. Zero for read-only. |
| `body_length` | `number` | UTF-8 length of the message body. |
| `has_attachments` | `boolean` | Attachments array non-empty. |
| `current_hour` | `number` | UTC hour (0–23). |
| `label_ids` | `string[]` | Label IDs from the request (label tools only). |
| `send_count` | `number` | Allowed `gmail.send` calls by this agent in the past rolling hour. |

### Presets

Apply via `POST /agent/policies/apply { "presetId": "..." }`:

| `presetId` | Allows |
|---|---|
| `read_only` | `gmail.read`, `gmail.list`, `gmail.search`, `gmail.thread.read` |
| `draft_only` | `gmail.draft.create` |
| `full_access` | every supported Gmail action |
| `send_allow_domains` | `gmail.send`, only when every recipient domain is in `domains[]` |

`send_allow_domains` requires an additional `domains: string[]`:

```bash
curl -X POST https://gmail-proxy.warrantclaw.com/agent/policies/apply \
  -H "Authorization: Bearer $WARRANTCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"presetId": "send_allow_domains", "domains": ["example.com"]}'
```

Response: `201` with `{"policy": <binding>}`.

### Custom Cedar

Pass `content` (Cedar source) and optional `description`:

```bash
curl -X POST https://gmail-proxy.warrantclaw.com/agent/policies/apply \
  -H "Authorization: Bearer $WARRANTCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "permit(principal, action == Action::\"gmail.send\", resource) when { [\"example.com\"].containsAll(context.to_domain) && context.send_count < 5 };",
    "description": "Example.com only, max 5/hour"
  }'
```

Policies are content-hashed: reapplying identical `content` reuses the same
policy id and reactivates it if previously deactivated. Binding ids are
deterministic from `sha256(userId:agentId:policyId)[:12]`, so apply is
idempotent.

## Tool catalog

All tools: `POST /tools/:toolId` with the auth header and
`Content-Type: application/json`. All return `200` unless noted.
This catalog is exhaustive for the Gmail proxy surface. If a tool is not
listed here, it is unsupported. In particular, there is no `gmail.get`;
use `gmail.read` to fetch a single message by id.

### gmail.send

Request:
```json
{
  "to": ["alice@example.com"],
  "subject": "Hello",
  "body": "Body text",
  "attachments": [{"filename": "doc.pdf", "content": "<base64>"}]
}
```

- `to`, `subject`, `body` required. `attachments` optional.
- CR and LF characters are rejected in `to`, `subject`, `body`
  (header-injection guard).

Response: `{"messageId": "..."}`.

### gmail.reply

Request: same as `gmail.send` plus:
- `in_reply_to` (string, required)
- `thread_id` (string, required)

Response: `{"messageId": "..."}`.

### gmail.draft.create

Request: same shape as `gmail.send`.

Response: `{"id": "<draft-id>", "message": {"id": "...", "threadId": "..."}}`.

### gmail.read

Fetch one message by id. Use this when you need the contents of a specific
email, including headers and body data.

Request: `{"message_id": "<id>"}`.

Response: raw Gmail `users.messages.get?format=full` payload —
typically `{id, threadId, snippet, payload: {headers, body, parts}}`.
The message body may appear in `payload.body.data` or in one of
`payload.parts[].body.data`, depending on the MIME structure.

### gmail.list

Request (both fields optional):
```json
{"max_results": 10, "label_ids": ["INBOX"]}
```

`max_results` defaults to 10.

Response: `{"messages": [{"id", "threadId", "subject"}], "resultSizeEstimate": N}`.

**Unique to `gmail.list`:** each returned message is enriched in parallel
with its `Subject` header. If a subject lookup fails the field is `null`
but the message is still included. Other read endpoints (`gmail.search`,
`gmail.thread.read`) return raw Gmail payloads without enrichment.

### gmail.search

Request:
```json
{"query": "from:alice@example.com is:unread", "max_results": 10}
```

`query` required (Gmail search syntax); `max_results` optional, default 10.

Response: `{"messages": [{"id", "threadId"}], "resultSizeEstimate": N}`.
Call `gmail.read` per message if you need more than ids.

### gmail.thread.read

Request: `{"thread_id": "<id>"}`.

Response: raw Gmail `users.threads.get` payload — `{id, messages: [...]}`.

### gmail.label.add

Request: `{"message_id": "<id>", "label_ids": ["STARRED", "IMPORTANT"]}`.

- `label_ids` must be a non-empty array of strings.

Response: `{"id": "<id>", "labelIds": [...]}`.

### gmail.label.remove

Request: same shape as `gmail.label.add`.

Response: `{"id": "<id>", "labelIds": [...]}`.

### gmail.trash

Request: `{"message_id": "<id>"}`.

Response: `{"id": "<id>", "labelIds": ["TRASH", ...]}`.

### gmail.delete

Request: `{"message_id": "<id>"}`.

Response: **`204 No Content`**, empty body.

## Inspecting policies

List bindings on the calling key:

```bash
curl https://gmail-proxy.warrantclaw.com/agent/policies \
  -H "Authorization: Bearer $WARRANTCLAW_API_KEY"
```

Response:
```json
{
  "policies": [
    {
      "bindingId": "...",
      "policyId": "...",
      "description": "...",
      "content": "permit(...);",
      "active": 1,
      "createdAt": "2026-...",
      "deactivatedAt": null
    }
  ]
}
```

`active: 1` is enforced; `active: 0` is soft-deleted.

Calling `GET /agent/policies` before the first tool call is a cheap way
to explain to the human what this key is allowed to do without probing
each action.

### Deactivating a binding

```bash
curl -X POST https://gmail-proxy.warrantclaw.com/agent/policies/<bindingId>/deactivate \
  -H "Authorization: Bearer $WARRANTCLAW_API_KEY"
```

Response: `{"ok": true}`.

## Errors

All errors use `{"error": "..."}`. `403` also carries extra fields — always
parse the body before deciding what to do.

| Status | Cause | Extra fields | Next step |
|---|---|---|---|
| `400` | Unknown tool, bad body, missing required field | — | Check request shape against the catalog |
| `401` | `WARRANTCLAW_API_KEY` missing, invalid, or revoked | — | Ask the human to mint a new key |
| `403` | Cedar denied, **or** Gmail not connected, **or** Gmail token expired | `rate_limit_results`, `pipes_error` | **Parse the body — see below** |
| `502` | Upstream (Pipes/Gmail) failed | — | Retry with backoff |
| `503` | Proxy DB check failed | — | Rare; `GET /health` to confirm |

### 403 disambiguation

This is the one error worth parsing carefully — three distinct failure
modes share the status code.

**Cedar denied:**
```json
{
  "error": "forbidden",
  "rate_limit_results": [
    {"type":"Rate","field":"send_count","operator":"lte",
     "expected":5,"actual":5,"passed":false}
  ]
}
```

`rate_limit_results` is always present on Cedar denials. If any entry has
`"passed": false`, a rate limit tripped — tell the human in plain terms
("you've hit 5/5 sends this hour; wait until the hour rolls over or bind
a looser policy"). Otherwise the policy itself doesn't cover this action
— suggest a preset or custom Cedar that would.

**Gmail not connected:**
```json
{"error": "Google account not connected", "pipes_error": "not_installed"}
```

Ask the human to connect Gmail at https://dash.warrantclaw.com.

**Gmail token expired:**
```json
{"error": "Google authorization expired — re-authorization required", "pipes_error": "unauthorized"}
```

Same fix: reconnect Gmail at the dashboard.

## Recipes

### Read five most recent unread

```bash
curl -X POST https://gmail-proxy.warrantclaw.com/tools/gmail.search \
  -H "Authorization: Bearer $WARRANTCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"query": "is:unread", "max_results": 5}'
```

### Send a simple message

```bash
curl -X POST https://gmail-proxy.warrantclaw.com/tools/gmail.send \
  -H "Authorization: Bearer $WARRANTCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["alice@example.com"],
    "subject": "Hi",
    "body": "Hello from warrant-claw."
  }'
```

### Reply to a message

```bash
curl -X POST https://gmail-proxy.warrantclaw.com/tools/gmail.reply \
  -H "Authorization: Bearer $WARRANTCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "to": ["alice@example.com"],
    "subject": "Re: Earlier thread",
    "body": "Replying.",
    "in_reply_to": "<message-id>",
    "thread_id": "thread_abc"
  }'
```

### Check permissions before acting

```bash
curl https://gmail-proxy.warrantclaw.com/agent/policies \
  -H "Authorization: Bearer $WARRANTCLAW_API_KEY"
```

## Troubleshooting

**Every call returns `unauthorized`:** `WARRANTCLAW_API_KEY` isn't set,
doesn't start with `sk_`, or was revoked.

**Every call returns `forbidden` regardless of tool:** the key has no
active policy binding. Apply a preset:

```bash
curl -X POST https://gmail-proxy.warrantclaw.com/agent/policies/apply \
  -H "Authorization: Bearer $WARRANTCLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"presetId": "read_only"}'
```

**Response ids are prefixed `stub_`:** the proxy is running in stub mode
(test/dev deployment). Responses are synthetic. Point at the production
base URL.

## Resources

- Dashboard (mint keys, manage policies, connect Gmail): https://dash.warrantclaw.com
- Product: https://warrantclaw.com
