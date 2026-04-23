---
name: memelord
description: |
  Memelord API integration with managed authentication. Generate AI-powered memes and video memes with text overlays.
  Use this skill when users want to create memes, edit meme text, generate video memes, or check video render status.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
  Requires network access and valid Maton API key.
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    requires:
      env:
        - MATON_API_KEY
---

# Memelord

Access the Memelord API with managed authentication. Generate AI-powered memes and video memes with customizable text overlays.

## Quick Start

```bash
# Generate a meme
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'prompt': 'when the code finally compiles'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/memelord/api/v1/ai-meme', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/memelord/{native-api-path}
```

Replace `{native-api-path}` with the actual Memelord API endpoint path. The gateway proxies requests to `www.memelord.com` and automatically injects your authentication token.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your Memelord connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=memelord&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'memelord'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "21fd90f9-5935-43cd-b6c8-bde9d915ca80",
    "status": "ACTIVE",
    "creation_time": "2025-12-08T07:20:53.488460Z",
    "last_updated_time": "2026-01-31T20:03:32.593153Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "memelord",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete authorization.

### Delete Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple Memelord connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'prompt': 'test meme'}).encode()
req = urllib.request.Request('https://gateway.maton.ai/memelord/api/v1/ai-meme', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
req.add_header('Maton-Connection', '21fd90f9-5935-43cd-b6c8-bde9d915ca80')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Generate Meme

Generate AI-powered memes with text overlays. Returns signed download URLs.

**Cost:** 1 credit per request

```bash
POST /memelord/api/v1/ai-meme
Content-Type: application/json

{
  "prompt": "when the code finally compiles",
  "count": 3,
  "category": "trending",
  "include_nsfw": false
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Text prompt for meme generation |
| `count` | integer | No | Number of memes to generate (1-10, default: 1) |
| `category` | string | No | Category filter: "trending" or "classic" |
| `include_nsfw` | boolean | No | Include NSFW templates (default: true) |

**Response:**
```json
{
  "success": true,
  "prompt": "when the code finally compiles",
  "total_generated": 3,
  "total_requested": 3,
  "results": [
    {
      "success": true,
      "url": "https://example.supabase.co/storage/v1/object/sign/user-assets/.../ai-memes/abc123.webp?token=...",
      "expires_in": 86400,
      "template_url": "https://example.supabase.co/storage/v1/object/public/public-assets/.../main.webp",
      "template_name": "Iceberg",
      "template_id": "282bf941-2f34-478f-abf4-fd26a399a652",
      "template_data": {
        "render_mode": "template",
        "width": 500,
        "height": 759,
        "template": [
          {
            "id": "text1",
            "text": "Code compiled",
            "font": "sans",
            "color": "white",
            "fontSize": "m"
          },
          {
            "id": "text2",
            "text": "All the logical bugs",
            "font": "sans",
            "color": "white",
            "fontSize": "m"
          }
        ]
      }
    }
  ]
}
```

### Edit Meme

Edit text on an existing meme using AI instructions.

**Cost:** 1 credit per request

```bash
POST /memelord/api/v1/ai-meme/edit
Content-Type: application/json

{
  "instruction": "make it about debugging instead",
  "template_id": "success-kid-001",
  "template_data": {
    "top_text": "When the code compiles",
    "bottom_text": "On the first try"
  },
  "target_index": 0
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `instruction` | string | Yes | AI instruction for editing the meme text |
| `template_id` | string | Yes | Template ID from original generation |
| `template_data` | object | Yes | Current template data with text fields |
| `target_index` | integer | No | Specific text element to edit |

**Response:**
```json
{
  "success": true,
  "url": "https://example.supabase.co/storage/v1/object/sign/user-assets/.../ai-memes/edited123.webp?token=...",
  "expires_in": 86400,
  "template_id": "282bf941-2f34-478f-abf4-fd26a399a652",
  "template_data": {
    "render_mode": "template",
    "width": 500,
    "height": 759,
    "template": [
      {
        "id": "text1",
        "text": "Debugging for hours",
        "font": "sans",
        "color": "white"
      },
      {
        "id": "text2",
        "text": "It was a typo",
        "font": "sans",
        "color": "white"
      }
    ]
  },
  "edit_summary": "Updated template text"
}
```

### Generate Video Meme

Generate captioned video memes with asynchronous rendering.

**Cost:** 5 credits per request (multiplied by count)

```bash
POST /memelord/api/v1/ai-video-meme
Content-Type: application/json

{
  "prompt": "explaining my code to a rubber duck",
  "count": 2,
  "category": "trending",
  "webhookUrl": "https://your-server.com/webhook",
  "webhookSecret": "your-secret-key"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Text prompt for video meme generation |
| `count` | integer | No | Number of videos to generate (1-5, default: 1) |
| `category` | string | No | Category filter: "trending" or "classic" |
| `template_id` | string | No | Specific template to use |
| `webhookUrl` | string | No | URL for completion notification |
| `webhookSecret` | string | No | Secret for webhook signature verification |

**Response:**
```json
{
  "success": true,
  "prompt": "when the code works on the first try",
  "total_requested": 2,
  "jobs": [
    {
      "job_id": "render-1740524400000-abc12",
      "template_name": "Surprised Pikachu Video",
      "template_id": "abc-123",
      "caption": "When the code works on the first try"
    }
  ],
  "message": "Render jobs started. Results will be POSTed to webhookUrl."
}
```

### Edit Video Meme

Modify captions on an existing video meme.

**Cost:** 5 credits per request

```bash
POST /memelord/api/v1/ai-video-meme/edit
Content-Type: application/json

{
  "instruction": "make it more dramatic",
  "template_id": "confused-travolta",
  "caption": "When the tests pass locally",
  "audio_overlay_url": "https://example.com/audio.mp3",
  "webhookUrl": "https://your-server.com/webhook"
}
```

**Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `instruction` | string | Yes | AI instruction for editing captions |
| `template_id` | string | Yes | Template ID from original generation |
| `caption` | string | Yes | Current caption text |
| `audio_overlay_url` | string | No | URL to audio file for overlay |
| `webhookUrl` | string | No | URL for completion notification |

**Response:**
```json
{
  "success": true,
  "job_id": "render-1740524400000-xyz99",
  "template_name": "Surprised Pikachu Video",
  "template_id": "abc-123",
  "original_caption": "When the tests pass locally",
  "edited_caption": "When the tests pass locally but fail in CI",
  "edit_summary": "Updated caption text",
  "message": "Render job started. Poll GET /api/video/render/remote?jobId=... for status."
}
```

### Check Video Render Status

Poll the status of an asynchronous video render job.

```bash
GET /memelord/api/video/render/remote?jobId={job_id}
```

**Response (Rendering):**
```json
{
  "success": true,
  "job": {
    "id": "render-1740524400000-abc12",
    "status": "rendering",
    "mp4Url": null,
    "storagePath": null,
    "error": null,
    "renderTimeMs": null,
    "createdAt": "2026-03-31T01:30:26.361825+00:00",
    "completedAt": null
  }
}
```

**Response (Completed):**
```json
{
  "success": true,
  "job": {
    "id": "render-1740524400000-abc12",
    "status": "completed",
    "mp4Url": "https://example.supabase.co/storage/v1/object/sign/user-assets/.../exports/ai-video-meme-1740524400000.mp4?token=...",
    "storagePath": "user-id/exports/ai-video-meme-1740524400000.mp4",
    "error": null,
    "renderTimeMs": 12664,
    "createdAt": "2026-03-31T01:30:26.361825+00:00",
    "completedAt": "2026-03-31T01:30:47.814+00:00"
  }
}
```

**Response (Failed):**
```json
{
  "success": true,
  "job": {
    "id": "render-1740524400000-abc12",
    "status": "failed",
    "mp4Url": null,
    "storagePath": null,
    "error": "Render timed out",
    "renderTimeMs": null,
    "createdAt": "2026-03-31T01:30:26.361825+00:00",
    "completedAt": null
  }
}
```

## Code Examples

### JavaScript

```javascript
// Generate a meme
const response = await fetch(
  'https://gateway.maton.ai/memelord/api/v1/ai-meme',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      prompt: 'when the code finally compiles',
      count: 3
    })
  }
);
const data = await response.json();
console.log(data.results[0].url);
```

### Python

```python
import os
import requests

# Generate a meme
response = requests.post(
    'https://gateway.maton.ai/memelord/api/v1/ai-meme',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={
        'prompt': 'when the code finally compiles',
        'count': 3
    }
)
data = response.json()
print(data['results'][0]['url'])
```

### Polling for Video Completion

```python
import os
import time
import requests

# Generate video meme
response = requests.post(
    'https://gateway.maton.ai/memelord/api/v1/ai-video-meme',
    headers={
        'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}',
        'Content-Type': 'application/json'
    },
    json={'prompt': 'debugging at 3am'}
)
job_id = response.json()['jobs'][0]['job_id']

# Poll for completion
while True:
    status_response = requests.get(
        f'https://gateway.maton.ai/memelord/api/video/render/remote?jobId={job_id}',
        headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
    )
    result = status_response.json()
    job = result['job']
    
    if job['status'] == 'completed':
        print(f"Video ready: {job['mp4Url']}")
        break
    elif job['status'] == 'failed':
        print(f"Error: {job['error']}")
        break
    
    time.sleep(2)
```

## Notes

- Download URLs for memes expire after 24 hours (check `expires_in` field in response, value is in seconds)
- Video MP4 URLs expire after 30 days
- Video meme generation is asynchronous - use polling or webhooks
- The `count` parameter multiplies credit cost (e.g., 3 videos = 15 credits)
- NSFW content is included by default; set `include_nsfw: false` to filter
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Memelord connection or invalid request |
| 401 | Invalid or missing Maton API key |
| 402 | Insufficient credits |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Memelord API |

### Troubleshooting: API Key Issues

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Invalid App Name

1. Ensure your URL path starts with `memelord`. For example:

- Correct: `https://gateway.maton.ai/memelord/api/v1/ai-meme`
- Incorrect: `https://gateway.maton.ai/api/v1/ai-meme`

## Resources

- [Memelord API Documentation](https://www.memelord.com/docs)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
