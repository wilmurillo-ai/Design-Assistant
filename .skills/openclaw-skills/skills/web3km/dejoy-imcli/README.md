# DeJoy IM CLI (imcli) — ClawHub bundle

This folder is meant to be **zipped and uploaded to ClawHub** (or similar skill registries). It contains `SKILL.md` (agent instructions) and this README.

## Contents

| File | Role |
|------|------|
| `SKILL.md` | Main skill document (YAML frontmatter); follow this for agent behavior |
| `README.md` | Human-readable notes (this file) |
| `PACKAGE.md` | Publishing notes and upstream source location |

## Quick start (English)

### 0) Before installing / running

1. Verify and build `imcli` from trusted upstream source; avoid untrusted prebuilt binaries.
2. Supply credentials via secure env var or secret store:
   - `DEJOY_HOMESERVER`
   - `DEJOY_ACCESS_TOKEN` (primary secret)
3. Use a least-privilege test token and validate operations in a non-production room first.
4. Ensure your agent/runtime policy does not log or exfiltrate tokens.

### 1) Build or install `imcli`

This bundle does not include source code. Build from upstream:

```bash
cd tools/imcli
go build -o imcli ./cmd/imcli
```

Then either:

- add `imcli` to `PATH`, or
- call it by absolute path (for example: `/path/to/imcli`).

Credential setup example:

```bash
export DEJOY_HOMESERVER="http://127.0.0.1:8008"
export DEJOY_ACCESS_TOKEN="your_access_token_here"
```

### 2) Common commands

Create a space (with topic/avatar):

```bash
imcli create-space \
  --name "AI Ops Space" \
  --topic "automation workspace" \
  --avatar "mxc://example.com/space-avatar" \
  --visibility private
```

Create a room under a space (with topic/avatar):

```bash
imcli create-room \
  --name "AI Team Room" \
  --space-id "!spaceid:example.com" \
  --topic "team announcement" \
  --avatar "mxc://example.com/room-avatar" \
  --visibility private
```

Set topic / clear topic:

```bash
imcli set-topic --room-id "!roomid:example.com" --topic "new announcement"
imcli set-topic --room-id "!roomid:example.com" --clear
```

Set avatar / clear avatar:

```bash
imcli set-avatar --room-id "!roomid:example.com" --avatar "mxc://example.com/new-avatar"
imcli set-avatar --room-id "!roomid:example.com" --clear
```

Other common operations:

```bash
imcli invite --room-id "!roomid:example.com" --user-id "@alice:example.com"
imcli join --room "#general:example.com"
imcli send-message --room-id "!roomid:example.com" --message "hello from bot"
imcli kick-user --room-id "!roomid:example.com" --user-id "@alice:example.com" --reason "policy violation"
imcli remove-user --room-id "!roomid:example.com" --user-id "@alice:example.com" --reason "cleanup"
```

### 3) JSON output and exit codes

- Success output: `{"ok": true, ...}`
- Error output: `{"ok": false, "status": ..., "errcode": "...", "error": "..."}`
- Exit code `0`: success
- Exit code `2`: argument or local error
- Exit code `4`: HTTP 4xx
- Exit code `5`: HTTP 5xx

## What is not included

- **No** Go source or `go.mod`. Installers must build from the upstream repo under `tools/imcli`, or use your published binary.

## Building imcli (developers)

From a checkout that contains the `tools/imcli` module:

```bash
cd tools/imcli
go build -o imcli ./cmd/imcli
```

Add the binary to `PATH`, or invoke it by absolute path.

## Slug / display name (ClawHub)

- **Slug:** `dejoy-imcli`
- **Display name:** `DeJoy IM CLI`

(Confirm against the ClawHub submission form.)
