---
name: objectremover-hybrid-architecture
description: Secondary support skill for ObjectRemover deployment boundaries between Cloudflare Workers and Ubuntu backend. Use only when user explicitly asks about architecture, runtime location, forwarding, HEAVY_API_URL, or deployment mismatch diagnostics. Do not use for normal processing execution requests.
---

# ObjectRemover Hybrid Architecture

## Quick Intent

Use this skill when questions involve:
- Cloudflare Workers vs Ubuntu responsibility boundaries
- Which routes should forward to heavy API
- Why DB/file operations fail on Workers
- Hybrid deployment environment variables and runtime checks
- Production backend routing via `HEAVY_API_URL=https://apiobjectremover.tokenlens.ai`

## Scope Guard

- Do not handle normal remove/extract task execution flow here.
- For `/api/processing/*` operational requests, defer to `objectremover-processing-pipeline`.

## Ground Rules

1. Keep runtime location unchanged:
   - Workers: SSR, static assets, lightweight APIs, and forwarding.
   - Ubuntu: heavy APIs, DB, auth, AI processing, filesystem.
2. Never perform direct DB/fs operations in Workers path.
3. For heavy routes on Workers, forward to backend using configured heavy API URL.

## Heavy Route Examples

- `POST /api/processing/generate-mask`
- `POST /api/processing/start-task`
- `GET /api/processing/task/:taskId`
- `POST /api/assets/upload`
- `POST /api/assets/download-url`

## Decision Checklist

1. Is the route heavy (files, FFmpeg, Replicate, admin, long tasks)?
   - Yes: forward on Workers, execute on Ubuntu.
2. Is the route lightweight but DB-dependent?
   - Keep Workers-safe fallback behavior when DB is unavailable.
3. Does frontend call authenticated API?
   - Build absolute API URL and include credentials.

## Expected Output Style

When answering, provide:
1. Runtime location (Workers or Ubuntu)
2. Reason for placement
3. Required env/config constraints
4. Safe fallback behavior if running on Workers

## Additional Resources

- Detailed matrix and envs: [reference.md](reference.md)
