---
name: meitu-tools
description: Unified Meitu CLI capability skill. Covers installation, credentials, command mapping, execution pattern, and user-facing error guidance for all built-in image/video commands.
requirements:
  credentials:
    - name: MEITU_OPENAPI_ACCESS_KEY
      source: env | ~/.meitu/credentials.json
    - name: MEITU_OPENAPI_SECRET_KEY
      source: env | ~/.meitu/credentials.json
  permissions:
    - type: file_read
      paths: ["~/.meitu/credentials.json", "~/.openapi/credentials.json"]
    - type: exec
      commands: ["meitu", "npm"]
    - type: file_write
      paths: ["~/.meitu/runtime-update-state.json"]
---

# meitu-tools

## Purpose

This skill is the single tool-execution hub for Meitu CLI commands.
Use one runner script for all supported commands:
- `scripts/run_command.js`

## Runtime Alignment

This skill is aligned with the Node.js `openapi-cli` command set.
Current built-in command coverage:
- `video-motion-transfer`
- `image-to-video`
- `text-to-video`
- `video-to-gif`
- `image-generate`
- `image-poster-generate`
- `image-edit`
- `image-upscale`
- `image-beauty-enhance`
- `image-face-swap`
- `image-try-on`
- `image-cutout`
- `image-grid-split`

Notes:
- No effect IDs are exposed in skill prompts.
- Command routing is done by built-in Meitu CLI commands.

## Install Runtime

```bash
npm install -g meitu-cli
meitu --version
```

If an existing `meitu` binary conflicts:

```bash
npm install -g meitu-cli@latest --force
```

## Agent Bootstrap Policy (Must Follow)

Agent behavior should optimize for zero-setup user experience:
- Always try execution via `scripts/run_command.js` first.
- Do not require user to install CLI before first attempt.
- Keep `MEITU_RUNTIME_UPDATE_MODE=check` by default.
- Use `MEITU_RUNTIME_UPDATE_MODE=off` to disable runtime version checks entirely.
- Only let the runner auto-install/update when the operator explicitly sets `MEITU_RUNTIME_UPDATE_MODE=apply`.

If runtime bootstrap fails, return concrete repair actions:
- Standard repair:

```bash
npm install -g meitu-cli
meitu --version
```

- If conflict error (`EEXIST`) appears:

```bash
npm install -g meitu-cli@latest --force
meitu --version
```

## Credentials

Use one of the following:

1. Environment variables:

```bash
export MEITU_OPENAPI_ACCESS_KEY="..."
export MEITU_OPENAPI_SECRET_KEY="..."
```

2. Credentials file (recommended): `~/.meitu/credentials.json`

```json
{"accessKey":"...","secretKey":"..."}
```

Legacy fallback is supported:
- `~/.openapi/credentials.json`

## Unified Execution

```bash
node "{baseDir}/scripts/run_command.js" --command "<command>" --input-json '<json object>'
```

Expected output JSON fields:
- `ok`
- `command`
- `task_id`
- `media_urls`
- `result`

## Lazy Runtime Update

Default behavior:
- `run_command.js` uses `MEITU_RUNTIME_UPDATE_MODE=check` by default.
- In `check` mode, it does not install anything automatically.
- In `apply` mode, it does not update on every call; it checks by TTL and installs only when stale/outdated.
- In `off` mode, it does not perform runtime version checks or installs.

Environment controls:
- `MEITU_RUNTIME_UPDATE_MODE=off|check|apply` (default `check`)
- `MEITU_UPDATE_CHECK_TTL_HOURS=<hours>` (default `24`)
- `MEITU_UPDATE_CHANNEL=<tag>` (default `latest`)
- `MEITU_UPDATE_PACKAGE=<name>` (default `meitu-cli`)
- `MEITU_ORDER_URL=<url>` (order/renewal page for insufficient quota)
- `MEITU_TASK_WAIT_TIMEOUT_MS=<ms>` (default `600000` for video commands, `900000` for others)
- `MEITU_TASK_WAIT_INTERVAL_MS=<ms>` (default `2000`)

Manual update intent:
- If the user explicitly asks for an immediate runtime update, run:

```bash
npm install -g meitu-cli@latest
meitu --version
```

Manual repair for missing/outdated runtime:

```bash
npm install -g meitu-ai@latest
meitu --version
```

## Error Contract (Must Be User-Visible)

When execution fails, runner output includes:
- `error_type`
- `error_code`
- `error_name`
- `user_hint`
- `next_action`
- `action_url` (when order/recharge is required)

Mandatory behavior:
- For `ORDER_REQUIRED`, explicitly tell the user to place an order/recharge first.
- If `action_url` exists, provide it directly.
- For `CREDENTIALS_MISSING`, ask the user to configure AK/SK first, then retry.

## Capability Catalog

<!-- BEGIN CAPABILITY_CATALOG -->
1. `video-motion-transfer`
- required: `image_url`, `video_url`, `prompt`
- optional: none

2. `image-to-video`
- required: `image`, `prompt`
- optional: `video_duration`, `ratio`

3. `text-to-video`
- required: `prompt`
- optional: `video_duration`, `sound`

4. `video-to-gif`
- required: `image`
- optional: `wechat_gif`

5. `image-generate`
- required: `prompt`
- optional: `image`, `size`, `ratio`

6. `image-poster-generate`
- required: `prompt`
- optional: `image_list`, `model`, `size`, `ratio`, `output_format`, `enhance_prompt`, `enhance_template`

7. `image-edit`
- required: `image`, `prompt`
- optional: `model`, `ratio`

8. `image-upscale`
- required: `image`
- optional: `model_type`

9. `image-beauty-enhance`
- required: `image`
- optional: `beatify_type`

10. `image-face-swap`
- required: `head_image_url`, `sence_image_url`, `prompt`
- optional: none

11. `image-try-on`
- required: `clothes_image_url`, `person_image_url`
- optional: `replace`, `need_sd`

12. `image-cutout`
- required: `image`
- optional: `model_type`

13. `image-grid-split`
- required: `image`
- optional: none
<!-- END CAPABILITY_CATALOG -->

## Natural Language Mapping

Typical intent-to-command mapping:
- motion transfer -> `video-motion-transfer`
- image edit -> `image-edit`
- image generate -> `image-generate`
- image upscale -> `image-upscale`
- virtual try-on -> `image-try-on`
- image to video -> `image-to-video`
- face swap -> `image-face-swap`
- image cutout -> `image-cutout`
- beauty enhancement -> `image-beauty-enhance`

## Security

See [SECURITY.md](../SECURITY.md) for full security model.

Key points:
- Credentials are read from environment or `~/.meitu/credentials.json`
- Default mode (`check`) does **not** auto-install packages
- `apply` mode enables `npm install -g` — use only with explicit consent
- Prefer manual updates: `npm install -g meitu-cli@latest`

## Robust Invocation Pattern

When the user provides structured execution intent, prefer:

```text
Use meitu-tools.
command: image-edit
input: {"image":["https://..."],"prompt":"..."}
```

Or via slash command:

```text
/skill meitu-tools
command=image-edit
input={"image":["https://..."],"prompt":"..."}
```
