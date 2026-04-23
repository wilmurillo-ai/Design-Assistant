# AIVideoMaker API Reference (for Skill Runtime)

## Base
- Base URL: `https://aivideomaker.ai`
- Auth header: `key: <AIVIDEO_API_KEY>`
- Optional header: `webhookUrl: <callback-url>`

## Endpoints

### 1) Create generation task
- `POST /api/v1/generate/{model}`
- Path param `model`:
  - `t2v`, `i2v`, `lv`, `t2v_v3`, `i2v_v3`

### 2) List tasks
- `GET /api/v1/tasks`

### 3) Get task details
- `GET /api/v1/tasks/{taskId}`

### 4) Get task status
- `GET /api/v1/tasks/{taskId}/status`

### 5) Cancel task
- `PUT /api/v1/tasks/{taskId}/cancel`
- Effective only while status is `SUBMITTED`

## Model Payload Matrix

### `t2v`
- `prompt`: string, required
- `aspectRatio`: `16:9` | `9:16` | `1:1`, required
- `filterMode`: `strict` | `custom`, required
- `duration`: `5` | `8`, required

### `i2v`
- `image`: string URL, required
- `prompt`: string | null, optional
- `filterMode`: `strict` | `custom`, required
- `duration`: `5` | `8`, required

### `lv`
- `image`: string URL, required
- `prompt`: string[], required, max 6
- `filterMode`: `strict` | `custom`, required

### `t2v_v3`
- `prompt`: string, required
- `aspectRatio`: `16:9` | `9:16` | `1:1`, required
- `duration`: `5` | `10` | `15` | `20`, required

### `i2v_v3`
- `image`: string URL, required
- `prompt`: string | null, optional
- `duration`: `5` | `10` | `15` | `20`, required

## Task Status
- `SUBMITTED`
- `PROGRESS`
- `COMPLETED`
- `FAILED`
- `CANCEL`

Terminal states:
- `COMPLETED`
- `FAILED`
- `CANCEL`

## Rate Limiting
- Query endpoints are limited to `60 requests / minute / IP`.
- On exceed, API returns `429` with `Retry-After` header.

Runtime handling recommendation:
1. Read `Retry-After` first.
2. If missing, use exponential backoff.
3. Add jitter to avoid synchronized retries.

## Standardized Skill Response

```json
{
  "ok": true,
  "status": "COMPLETED",
  "taskId": "ckxxxxxxxx",
  "data": {},
  "errorCode": null,
  "errorMessage": null,
  "retryAfter": null,
  "httpStatus": 200,
  "timestamp": "2026-03-23T10:00:00.000Z"
}
```

## Error Mapping
- `400` + message includes validation -> `INVALID_PAYLOAD`
- `401`/`403` -> `AUTH_FAILED`
- `404` -> `TASK_NOT_FOUND`
- `429` -> `RATE_LIMITED`
- message includes `Insufficient credits` -> `INSUFFICIENT_CREDITS`
- fetch/timeout -> `NETWORK_ERROR`
- others -> `UNKNOWN_ERROR`

## Quick English Summary
- Authentication: request header `key` is required.
- Models: `t2v/i2v/lv/t2v_v3/i2v_v3`.
- Terminal statuses: `COMPLETED/FAILED/CANCEL`.
- Rate limit: query endpoints are limited to `60 req/min/IP`, exceeding returns `429 + Retry-After`.
