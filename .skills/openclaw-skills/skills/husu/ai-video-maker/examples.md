# Usage Examples

## 1) End-to-end generation workflow (`t2v`)

Command:
```bash
node scripts/run-workflow.mjs --model t2v --input ./examples/t2v-input.json
```

Input file (`examples/t2v-input.json`):
```json
{
  "prompt": "A cinematic sunset over a futuristic city skyline",
  "aspectRatio": "16:9",
  "filterMode": "strict",
  "duration": "8"
}
```

Typical output:
```json
{
  "ok": true,
  "status": "COMPLETED",
  "taskId": "ckxxxxxxxx",
  "data": {
    "id": "ckxxxxxxxx",
    "output": {
      "videoUrl": "https://..."
    }
  }
}
```

## 2) Query task status

```bash
node scripts/run-workflow.mjs --action getStatus --taskId ckxxxxxxxx
```

Possible output:
```json
{
  "ok": true,
  "status": "PROGRESS",
  "taskId": "ckxxxxxxxx",
  "data": {
    "status": "PROGRESS"
  }
}
```

## 3) Cancel task

```bash
node scripts/run-workflow.mjs --action cancelTask --taskId ckxxxxxxxx
```

Possible output:
```json
{
  "ok": true,
  "status": "CANCEL",
  "taskId": "ckxxxxxxxx",
  "data": {
    "status": "CANCEL"
  }
}
```

## 4) Handling insufficient credits

Typical API error:
```json
{
  "status": "FAILED",
  "message": "Insufficient credits"
}
```

Skill output:
```json
{
  "ok": false,
  "status": "FAILED",
  "errorCode": "INSUFFICIENT_CREDITS",
  "errorMessage": "Insufficient credits",
  "taskId": null
}
```

Recommended next actions:
- Reduce `duration` or use a lower-cost model.
- Ensure the account has enough credits.
- Retry after top-up.

## 5) Handling 429 rate limit

Skill behavior:
1. Detect `429`.
2. Parse `Retry-After` if present.
3. Sleep and retry (up to max retries).
4. Return `RATE_LIMITED` when retries are exhausted.

Output example:
```json
{
  "ok": false,
  "status": "FAILED",
  "errorCode": "RATE_LIMITED",
  "errorMessage": "Rate limited by upstream API",
  "retryAfter": 2
}
```

## Quick English Summary
- One-command workflow: `node scripts/run-workflow.mjs --model t2v --input ./examples/t2v-input.json`
- Check status: `--action getStatus --taskId <taskId>`
- Cancel task: `--action cancelTask --taskId <taskId>`
- Common failures: insufficient credits (`INSUFFICIENT_CREDITS`), rate limiting (`RATE_LIMITED`)
