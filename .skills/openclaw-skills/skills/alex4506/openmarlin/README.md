# openmarlin-skill

OpenClaw skill for guided platform access and billing workflows for
OpenMarlin.

## Quick Summary

OpenMarlin is an OpenClaw-first access layer for registration, native
execution, and prepaid billing flows.

This repo covers the OpenClaw-first UX for:

- registration and account linking
- platform API key bootstrap and auth-profile storage
- server-side automatic routing with optional provider overrides and labels
- asynchronous task submission and polling for long-running jobs
- structured `402 Payment Required` recovery
- guided top-up and authoritative balance management

Primary entrypoints:

- `SKILL.md` for OpenClaw skill behavior and operator guidance
- `scripts/registration_session.py` for creating, polling, resuming, and
  bootstrapping workspace API keys after registration
- `scripts/platform_request.py` for authenticated `/v1/executions` requests and
  `/v1/models` discovery, plus `/v1/tasks` submission and polling for
  long-running jobs
- `scripts/billing.py` for structured 402 recovery guidance and
  authenticated top-up session handling, authoritative balance reads, local
  balance snapshots, and tracked
  top-up history

Internal helpers:

- `scripts/openclaw_platform_auth.py` for OpenClaw auth-profile storage
- `scripts/openclaw_billing_state.py` for local billing-state persistence

## Installation

Use the repo directly:

```bash
git clone <your-openmarlin-skill-repo>
cd <your-openmarlin-skill-directory>
```

By default the skill targets `https://api.openmarlin.ai`. Override
`OPENMARLIN_SERVER_URL` only when you want a different deployment such as a
local dev server, and use the bare origin without `/v1`.

To install it as a local OpenClaw skill, copy the repo contents into the
default skills workspace:

```text
~/.openclaw/workspace/skills/
```

Install into that default location:

```bash
mkdir -p "$HOME/.openclaw/workspace/skills/openmarlin"
rsync -a --delete \
  --exclude '.git' \
  /path/to/openmarlin-skill-directory/ \
  "$HOME/.openclaw/workspace/skills/openmarlin/"
```

After install, the main entrypoint should be:

```text
~/.openclaw/workspace/skills/openmarlin/SKILL.md
```

The helper scripts remain available relative to that installed skill directory:

```text
~/.openclaw/workspace/skills/openmarlin/scripts/registration_session.py
~/.openclaw/workspace/skills/openmarlin/scripts/platform_request.py
~/.openclaw/workspace/skills/openmarlin/scripts/billing.py
```

## Requirements

- `python3`
- `OPENMARLIN_SERVER_URL` defaults to `https://api.openmarlin.ai`

Optional but commonly useful:

- `OPENMARLIN_PLATFORM_API_KEY`
- `OPENMARLIN_DEFAULT_PROVIDER_ID`
- `OPENMARLIN_DEFAULT_ROUTING_LABELS`

These values do not have to come from a shell `export`. The helper scripts now
resolve them in this order:

1. process environment
2. persisted OpenClaw skill config in `~/.openclaw/openclaw.json`

The persisted OpenClaw config path is:

```text
skills.entries["openmarlin"].env
```

So OpenClaw can remember values such as:

```json
{
  "skills": {
    "entries": {
      "openmarlin": {
        "env": {
          "OPENMARLIN_SERVER_URL": "http://127.0.0.1:3000",
          "OPENMARLIN_DEFAULT_PROVIDER_ID": "node-a",
          "OPENMARLIN_DEFAULT_ROUTING_LABELS": "{\"region\":\"ap-sg\"}"
        }
      }
    }
  }
}
```

Users do not need to hand-edit config files if OpenClaw is writing skill config
through its normal settings or `skills.update` flow.

For browser handoff during registration, the skill expects the server to
return `handoff.authorization_url` directly. It no longer relies on locally
configured WorkOS URL templates. When `registration_session.py create` gets an
authorization URL back, it now tries to open that URL in the system browser
automatically and then tells the user how to continue polling in OpenClaw.
The browser callback path is treated as a user-facing landing page, not as the
machine-readable source of registration completion state.

## Trust And Secret Handling

- Treat `OPENMARLIN_SERVER_URL` as the trusted API origin for registration, bootstrap, routing, balance, and top-up calls. Use the bare origin, not an origin with `/v1`.
- Treat browser handoff URLs as trusted only when they come from the server's `handoff.authorization_url`.
- Do not reconstruct WorkOS or browser handoff URLs locally from device codes or callback state.
- Store issued platform API keys in OpenClaw auth-profile storage, not in ordinary skill config.
- Use `OPENMARLIN_PLATFORM_API_KEY` only as a temporary direct override when debugging or testing.

## First Run

After install, the shortest safe path is:

1. Confirm `OPENMARLIN_SERVER_URL` if you need to override the default `https://api.openmarlin.ai`.
2. Start registration with `python3 scripts/registration_session.py create`.
3. Finish external auth if the skill opens or prints a browser handoff URL.
4. Poll until completion with `python3 scripts/registration_session.py watch --session-id <session-id>`.
   Do not depend on the browser callback response body; machine flow should follow the registration session state.
5. Bootstrap and store the workspace API key with `python3 scripts/registration_session.py bootstrap --session-id <session-id> --store`.
6. Optionally discover exact models with `python3 scripts/platform_request.py models`.
7. Send your first routed execution with `python3 scripts/platform_request.py executions --body-json '{"instruction":"hello"}'`.
8. For long-running jobs such as video generation, prefer `python3 scripts/platform_request.py tasks-submit --watch ...` so submission and polling happen in one flow.

If you plan to force a specific `provider_id` and also pass an exact `model`,
first confirm that the same `python3 scripts/platform_request.py models` result
shows that provider under that exact model.

Common entrypoints:

```bash
python3 scripts/registration_session.py create
python3 scripts/registration_session.py --server-url https://your-server.example.com create --dry-run
python3 scripts/platform_request.py models
python3 scripts/platform_request.py executions --body-json '{"instruction":"hello"}'
python3 scripts/platform_request.py tasks-submit --watch --body-json '{"instruction":"generate a short plane video","metadata":{"mode":"video"}}'
python3 scripts/platform_request.py tasks-watch --task-id <task-id>
python3 scripts/platform_request.py executions --provider node-a --body-json '{"instruction":"hello"}'
python3 scripts/platform_request.py executions --body-json '{"instruction":"hello","model":"openai-codex/gpt-5.4"}'
python3 scripts/platform_request.py executions --dry-run --server-url https://your-server.example.com --api-key claw_wsk_placeholder --body-json '{"instruction":"hello"}'
python3 scripts/billing.py activity
python3 scripts/billing.py explain-402 --response-file /path/to/402.json
python3 scripts/billing.py explain-402 --auto-recover --response-file /path/to/402.json
```

## What You Can Do Now

- Register or connect an OpenMarlin account from inside OpenClaw.
- Store the issued workspace API key into OpenClaw auth profiles.
- Send routed execution requests with automatic provider and model selection.
- Submit long-running generation jobs and poll for final artifact metadata.
- When you do pass `model`, use the full exact ref returned by `/v1/models`.
- When forcing both `provider_id` and `model`, pair them from the same `/v1/models` result instead of guessing.
- Override routing with an explicit provider id or simple labels.
- Inspect recent prepaid usage and ledger activity from the server APIs.
- Recover from `402 Payment Required` by creating or resuming a top-up flow.

For full behavior and flow guidance, use `SKILL.md`.
