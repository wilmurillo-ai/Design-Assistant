---
name: dejoy-imcli
description: >-
  DeJoy IM automation via the Go CLI imcli against the Matrix Client API:
  create rooms/spaces, attach rooms to a space, set topic/avatar (during
  creation or separately), invite/join/send message, upload/send images, and
  kick/remove users. Requires a configured DeJoy server URL and access token.
primaryEnv: DEJOY_ACCESS_TOKEN
requiredEnv:
  - DEJOY_HOMESERVER
  - DEJOY_ACCESS_TOKEN
---

# DeJoy IM CLI (imcli) Skill

## Purpose

- Lets an AI agent drive `imcli` (Go) to call the Matrix Client API for common DeJoy IM tasks.
- Covers: create room/space, create room under a space, set topic/avatar, invite, join,
  send message, upload image media, send image message, `kick-user`, `remove-user` (alias of kick).
- For automation where you already have a DeJoy server base URL and a user `access_token`.

## Scope

- This skill does **not** log users in or mint tokens; it only uses an existing `access_token`.
- Default API prefix is `/_matrix/client/v3` (Matrix Client API).
- Plain text messages use `m.room.message` with `msgtype=m.text`.

## Obtaining the `imcli` binary

This upload bundle contains **skill documentation only**, not Go source. Either:

1. From the upstream repo, under `tools/imcli`, run `go build -o imcli ./cmd/imcli`, then put `imcli` on `PATH` or use the absolute path to the binary.
2. If you ship a prebuilt package, install `imcli` on `PATH` and use the commands below as `imcli`.

Examples assume `imcli` is on `PATH`. If you run a binary in the current directory, use `./imcli` instead.

## Credentials and connection

- **Required env vars:** `DEJOY_HOMESERVER`, `DEJOY_ACCESS_TOKEN`
- **Primary credential for registry/audit:** `DEJOY_ACCESS_TOKEN`
- **CLI flags (override env):** `--dejoy-homeserver`, `--access-token`

Set credentials once per shell session (recommended for automation):

```bash
export DEJOY_HOMESERVER="http://127.0.0.1:8008"
export DEJOY_ACCESS_TOKEN="your_access_token_here"
```

Equivalent one-off usage (less recommended because token can appear in shell history):

```bash
imcli --dejoy-homeserver "http://127.0.0.1:8008" --access-token "$DEJOY_ACCESS_TOKEN" help
```

Credential safety guidance:

- Prefer secret store / CI secret injection over hardcoding token in files.
- Use least-privilege tokens and test in non-production rooms first.
- Never print, log, or echo the full token in agent outputs.

## Command examples

### 1) Create a space

```bash
imcli create-space \
  --name "AI Ops Space" \
  --topic "automation workspace" \
  --avatar "mxc://example.com/space-avatar" \
  --visibility "private"
```

### 2) Create a room under a space

```bash
imcli create-room \
  --name "AI Team Room" \
  --space-id "!spaceid:example.com" \
  --topic "team coordination" \
  --avatar "mxc://example.com/room-avatar" \
  --visibility "private"
```

### 3) Set or clear topic

```bash
imcli set-topic \
  --room-id "!roomid:example.com" \
  --topic "new announcement"
```

```bash
imcli set-topic \
  --room-id "!roomid:example.com" \
  --clear
```

### 4) Set or clear avatar

```bash
imcli set-avatar \
  --room-id "!roomid:example.com" \
  --avatar "mxc://example.com/new-avatar"
```

```bash
imcli set-avatar \
  --room-id "!roomid:example.com" \
  --clear
```

### 5) Invite

```bash
imcli invite \
  --room-id "!roomid:example.com" \
  --user-id "@alice:example.com"
```

### 6) Join (room id or alias)

```bash
imcli join \
  --room "#general:example.com"
```

### 7) Send a message

```bash
imcli send-message \
  --room-id "!roomid:example.com" \
  --message "hello from ai agent" \
  --event-type "m.room.message"
```

### 8) Kick / remove user

```bash
imcli kick-user \
  --room-id "!roomid:example.com" \
  --user-id "@alice:example.com" \
  --reason "violate room policy"
```

```bash
imcli remove-user \
  --room-id "!roomid:example.com" \
  --user-id "@alice:example.com" \
  --reason "cleanup member list"
```

### 9) Upload an image

```bash
imcli upload-image \
  --file "./assets/incident.png"
```

```bash
imcli upload-image \
  --file "./assets/incident.png" \
  --filename "incident-2026-04-03.png" \
  --content-type "image/png"
```

Successful response includes `content_uri` (example: `mxc://example.com/abc123`), which can be used later in room events (for example, as an image message `url` field).

### 10) Upload and send image in one step

```bash
imcli send-image \
  --room-id "!roomid:example.com" \
  --file "./assets/incident.png"
```

```bash
imcli send-image \
  --room-id "!roomid:example.com" \
  --file "./assets/incident.png" \
  --filename "incident-2026-04-03.png" \
  --content-type "image/png" \
  --body "incident screenshot"
```

## Parameters summary

| Subcommand | Required | Notes |
|------------|----------|--------|
| create-space | `--name` | Optional `--topic`, `--avatar`, `--visibility` (default `private`) |
| create-room | `--name` | Optional `--space-id`, `--topic`, `--avatar`, `--visibility` |
| set-topic | `--room-id` | Use either `--topic` or `--clear` |
| set-avatar | `--room-id` | Use either `--avatar` or `--clear` |
| invite | `--room-id`, `--user-id` | |
| join | `--room` | `!id:server` or `#alias:server` |
| send-message | `--room-id`, `--message` | Optional `--event-type` (default `m.room.message`) |
| upload-image | `--file` | Optional `--filename`, `--content-type`; returns `content_uri` |
| send-image | `--room-id`, `--file` | Optional `--filename`, `--content-type`, `--body`; returns `event_id` + `content_uri` |
| kick-user / remove-user | `--room-id`, `--user-id` | Optional `--reason` |

## Output

- Stdout is **JSON**: on success `ok=true`; on failure `ok=false` with `status`, `errcode`, and `error` when the server returns them.

## Agent guidelines

- Validate the token with a low-risk call first (e.g. `join` or `send-message` to a test room).
- For bulk operations, add retries with backoff; branch on `errcode` when handling failures.
- Never log the full access token.
