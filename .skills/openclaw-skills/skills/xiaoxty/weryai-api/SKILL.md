---
name: weryai-api
description: Integrate WeryAI API for AI image generation, video generation, chat, and podcast creation. Use when the user wants to call WeryAI API, generate images/videos with AI, use text-to-image, image-to-video, or any WeryAI generation feature.
---

# WeryAI API Integration

Official docs: https://docs.weryai.com/en

## Authentication

Base URL: `https://api.weryai.com`

All requests require:
```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

Get API key at: https://weryai.com/api/keys

## Core Workflow

All generation tasks are **async**: submit → get `task_id` → poll status → get result.

### 1. Submit Task

```python
import requests

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Text-to-Image
resp = requests.post("https://api.weryai.com/v1/generation/text-to-image", headers=headers, json={
    "model": "WERYAI_IMAGE_2_0",
    "prompt": "A beautiful sunset over the ocean",
    "negative_prompt": "blurry, low quality",
    "aspect_ratio": "16:9",
    "image_number": 1,
    "webhook_url": "https://your-server.com/webhook"  # optional
})
task_id = resp.json()["data"]["task_ids"][0]
```

### 2. Poll Task Status

```python
import time

def wait_for_result(task_id, max_wait=300):
    url = f"https://api.weryai.com/v1/generation/{task_id}/status"
    start = time.time()
    while time.time() - start < max_wait:
        result = requests.get(url, headers=headers).json()["data"]
        status = result["task_status"]
        if status == "succeed":
            return result.get("images") or result.get("videos")
        elif status == "failed":
            raise Exception(result.get("msg", "Task failed"))
        time.sleep(3)
    raise TimeoutError("Task timed out")
```

## API Endpoints

### Image Generation

| Endpoint | Method | Description |
|---|---|---|
| `/v1/generation/text-to-image` | POST | Text → Image |
| `/v1/generation/image-to-image` | POST | Image → Image |

**Text-to-Image required fields**: `model`, `prompt`, `aspect_ratio`

**Common models**:
- `WERYAI_IMAGE_2_0` — WeryAI Image 2.0
- `FLUX_PRO` — Flux Pro
- `GPT_IMAGE_MINI` — GPT Image Mini
- `GROK_2_IMAGE` — Grok 2 Image
- `IMAGE4` — Imagen4
- `QWEN` — Qwen Image

### Video Generation

| Endpoint | Method | Description |
|---|---|---|
| `/v1/generation/text-to-video` | POST | Text → Video |
| `/v1/generation/image-to-video` | POST | Image → Video |
| `/v1/generation/multi-image-to-video` | POST | Multi-image → Video |

**Text-to-Video required fields**: `model`, `prompt`, `aspect_ratio`, `duration`

**Common models**:
- `WERYAI_VIDEO_1_0` — WeryAI Video 1.0
- `SORA_2` / `SORA_2_PRO` — Sora 2
- `VEO_3` / `VEO_3_FAST` — Veo 3
- `KLING_V2_6_PRO` — Kling 2.6 Pro
- `WAN_2_6` — Wan 2.6
- `DOUBAO_1_5_PRO` — Seedance 1.5 Pro

### Task Query

```
GET /v1/generation/{taskId}/status    # Single task
GET /v1/generation/batch/{batchId}/status  # Batch tasks
```

### Account

```
GET /v1/account/credits    # Query credit balance
```

### Chat (OpenAI-compatible)

```
POST /v1/chat/completions
GET  /v1/chat/models
```

## Request Parameters

### Image Generation

```json
{
  "model": "WERYAI_IMAGE_2_0",
  "prompt": "...",                    // required, max 2000 chars
  "negative_prompt": "...",           // optional, max 1000 chars
  "aspect_ratio": "16:9",             // required (1:1, 16:9, 9:16, 4:3, 21:9)
  "resolution": "1080p",              // optional
  "image_number": 1,                  // default 1
  "use_web_search": false,            // optional
  "webhook_url": "https://...",       // optional
  "caller_id": 123                    // optional, for business tracking
}
```

### Video Generation

```json
{
  "model": "WERYAI_VIDEO_1_0",
  "prompt": "...",                    // required, max 2000 chars
  "negative_prompt": "...",           // optional
  "aspect_ratio": "16:9",             // required
  "duration": 5,                      // required, seconds
  "generate_audio": false,            // optional
  "webhook_url": "https://...",       // optional
  "video_number": 1                   // max 1
}
```

## Task Status Values

| Status | Description |
|---|---|
| `waiting` | Queued |
| `processing` | Generating |
| `succeed` | Done — check `images` or `videos` field |
| `failed` | Failed — check `msg` field |

## Response Format

```json
{
  "status": 0,          // 0 = success
  "desc": "success",
  "message": "success",
  "data": { ... }
}
```

Success response after task completes:
```json
{
  "data": {
    "task_id": "task_abc123",
    "task_status": "succeed",
    "images": ["https://cdn.weryai.com/result/image1.png"]
  }
}
```

## Error Codes

| Status | Meaning | Solution |
|---|---|---|
| 1001 | Parameter error | Check required fields and formats |
| 1002 | Unauthorized | Verify API key |
| 1003 | Not found | Check task/batch ID |
| 1004 | Insufficient credits | Recharge at https://weryai.com/api/pricing |
| 1005 | Content moderation | Revise prompt |

## Webhook

Add `webhook_url` to any generation request. WeryAI will POST results to it on completion:

```javascript
// Express.js handler
app.post('/webhook', (req, res) => {
  const { task_id, task_status, images, videos, msg } = req.body.data;
  if (task_status === 'succeed') {
    // process images or videos
  } else if (task_status === 'failed') {
    console.error('Failed:', msg);
  }
  res.sendStatus(200);
});
```

## Prompt Tips

- Be specific: "A fluffy orange tabby cat on a windowsill, soft natural lighting, photorealistic"
- Add style: "photorealistic", "anime style", "oil painting", "8k"
- Use `negative_prompt` to exclude: "blurry, low quality, watermark, text"

## Java Integration Example

```java
@Service
public class WeryAiService {
    private static final String BASE_URL = "https://api.weryai.com";
    
    public String submitTextToImage(String prompt, String aspectRatio) {
        Map<String, Object> body = Map.of(
            "model", "WERYAI_IMAGE_2_0",
            "prompt", prompt,
            "aspect_ratio", aspectRatio
        );
        // POST BASE_URL + "/v1/generation/text-to-image"
        // Authorization: Bearer API_KEY
        // return task_id from response data.task_ids[0]
    }
    
    public List<String> pollTaskResult(String taskId) {
        // GET BASE_URL + "/v1/generation/" + taskId + "/status"
        // poll every 3s until task_status == "succeed"
        // return data.images or data.videos
    }
}
```

## Additional Resources

- [API Reference](https://docs.weryai.com/api-reference)
- [Quick Start](https://docs.weryai.com/en/quickstart)
- [Call History](https://weryai.com/api/history)
- [Pricing & Models](https://weryai.com/api/pricing)
