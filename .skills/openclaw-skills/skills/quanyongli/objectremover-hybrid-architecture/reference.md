# Hybrid Architecture Reference

## Runtime Split

- Workers: page SSR, static delivery, lightweight APIs, proxy/forward heavy APIs.
- Ubuntu backend: heavy APIs, PostgreSQL/Supabase access, Better Auth full behavior, Replicate and FFmpeg pipeline, upload/media endpoints.

## Route Classification

### Workers-first

- SSR pages and static assets.
- Lightweight APIs that do not require direct DB/filesystem.

### Workers with fallback

- Credits, tasks, storage, projects: route stays callable on Workers, but must tolerate missing DB client and return safe defaults.

### Ubuntu-only execution

- Asset upload/raw/clone/trim/download-and-trim.
- Processing generate-mask/start-task/task status.
- Admin operations.
- Any route touching filesystem, child process, FFmpeg, or external AI processing orchestration.

## Forwarding Rule

For heavy APIs:
1. If request is in Workers runtime, forward to heavy backend API.
2. If request is in Ubuntu runtime, execute local service logic.

## Critical Constraints

- Workers runtime cannot rely on Node `pg` and filesystem behavior.
- Runtime feature detection may be unreliable; explicit env marker is preferred.
- Backend URL env must be configured to avoid accidental localhost target in production.

## Env Highlights

- Workers:
  - `CLOUDFLARE_WORKERS=true` (or equivalent marker)
  - `HEAVY_API_URL=https://apiobjectremover.tokenlens.ai`
- Ubuntu:
  - `DATABASE_URL`, Supabase service credentials
  - Auth base URL points to API domain
  - Frontend URL points to frontend domain

## Production URL Contract

- Frontend domain: `https://objectremover.video`
- Heavy backend domain: `https://apiobjectremover.tokenlens.ai`
- Server-side forwarding target:
  - `HEAVY_API_URL=https://apiobjectremover.tokenlens.ai`
- Rule:
  - Workers handles edge-safe logic and forwards heavy APIs to `HEAVY_API_URL`.
  - Ubuntu executes heavy routes locally.

## Forwarding Examples

- Forward on Workers:
  - `POST /api/processing/generate-mask`
  - `POST /api/processing/start-task`
  - `GET /api/processing/task/:taskId`
  - `POST /api/assets/upload`
  - `POST /api/assets/download-url`
- Keep local on Workers-safe routes:
  - `GET /api/auth/region`
  - DB-dependent lightweight routes with fallback behavior (credits/tasks/storage/projects).

## Diagnostic Heuristics

- Symptom: API works locally but fails in production Workers path.
  - Check if route should have been forwarded.
- Symptom: auth/session mismatch across domains.
  - Check API absolute URL usage and cookie strategy.
- Symptom: DB-related null/fallback responses from Workers.
  - Confirm fallback is expected; move DB-heavy operation to Ubuntu path.
