---
name: scavio-youtube
description: Search YouTube, retrieve video metadata, extract full transcripts, and check AI trainability. Use for RAG pipelines or any task requiring video content.
version: 2.0.0
tags: youtube, video-search, transcript, metadata, captions, agents, langchain, crewai, autogen, structured-data, json, ai-agents, content-research, rag
metadata:
  openclaw:
    requires:
      env:
        - SCAVIO_API_KEY
    primaryEnv: SCAVIO_API_KEY
    emoji: "\u25B6"
    homepage: https://scavio.dev/docs
---

# YouTube Search and Transcripts via Scavio

Search YouTube, retrieve video metadata, extract transcripts, and check AI trainability. All endpoints return structured JSON.

## When to trigger

Use this skill when the user asks to:
- Find YouTube videos on a topic
- Get the transcript of a YouTube video (for summarization, RAG, Q&A)
- Check view counts, upload date, or video metadata
- Verify if a video is suitable for AI training or has captions available

## Setup

Get a free API key at https://scavio.dev (1,000 free credits/month, no card required):

```bash
export SCAVIO_API_KEY=sk_live_your_key
```

## Workflow

1. **Finding a video:** call `/search` with the topic. Use `sort_by: view_count` for the most-watched result.
2. **Getting content:** if the user wants a summary, call `/transcript` with the `videoId` from search results.
3. **Checking metadata:** call `/metadata` for view counts, likes, tags, or channel info.
4. **RAG pipelines:** inject transcript segments directly into context. Each segment has `text`, `start`, and `duration`.
5. **Trainability:** call `/trainability` to check license and caption availability before ingesting.

## Endpoints

| Endpoint | Description |
|---|---|
| `POST https://api.scavio.dev/api/v1/youtube/search` | Search YouTube videos |
| `POST https://api.scavio.dev/api/v1/youtube/metadata` | Get structured video metadata |
| `POST https://api.scavio.dev/api/v1/youtube/transcript` | Extract video transcript |
| `POST https://api.scavio.dev/api/v1/youtube/trainability` | Check AI training suitability |

```
Authorization: Bearer $SCAVIO_API_KEY
```

## Search Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `search` | string | required | Search query — note: this field is `search`, not `query` |
| `upload_date` | string | -- | `last_hour`, `today`, `this_week`, `this_month`, `this_year` |
| `type` | string | -- | `video`, `channel`, or `playlist` |
| `duration` | string | -- | `short` (< 4 min), `medium` (4-20 min), `long` (> 20 min) |
| `sort_by` | string | `relevance` | `relevance`, `date`, `view_count`, `rating` |
| `subtitles` | boolean | `false` | Videos with captions only |
| `creative_commons` | boolean | `false` | Creative Commons videos only |

## Transcript Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `video_id` | string | required | YouTube video ID (e.g. `sVcwVQRHIc8`) |
| `language` | string | `en` | Language code for transcript |
| `transcript_origin` | string | -- | `auto_generated` or `uploader_provided` |

## Examples

```python
import os, requests

BASE = "https://api.scavio.dev"
HEADERS = {"Authorization": f"Bearer {os.environ['SCAVIO_API_KEY']}"}

# Search — use "search" field, not "query"
results = requests.post(f"{BASE}/api/v1/youtube/search", headers=HEADERS,
    json={"search": "langchain tutorial", "type": "video", "sort_by": "view_count"}).json()

video_id = results["data"][0]["videoId"]

# Transcript for RAG
transcript = requests.post(f"{BASE}/api/v1/youtube/transcript", headers=HEADERS,
    json={"video_id": video_id, "language": "en"}).json()

text = " ".join(seg["text"] for seg in transcript["data"])
```

## Search Response

```json
{
  "data": [
    {
      "videoId": "sVcwVQRHIc8",
      "title": "Learn RAG From Scratch - Python AI Tutorial",
      "channel": "freeCodeCamp.org",
      "publishedAt": "2024-04-17",
      "duration": "2:33:11",
      "viewCount": 1258310,
      "thumbnail": "https://i.ytimg.com/vi/sVcwVQRHIc8/hq720.jpg"
    }
  ],
  "credits_used": 1
}
```

Transcript response: `[{"text": "...", "start": 0.0, "duration": 3.2}]`

Metadata response: `title`, `view_count`, `like_count`, `comment_count`, `categories`, `tags`, `channel_id`, `upload_date`, `thumbnails`.

Trainability response: `has_transcript`, `transcript_languages`, `license`, `is_trainable`.

## Guardrails

- The search parameter is `search`, not `query` — this is different from other Scavio endpoints.
- Never fabricate video IDs, view counts, or transcript content.
- Transcripts are raw captions — they may lack punctuation. Summarize them clearly.
- If a transcript is not available, call `/trainability` to check why before reporting an error.

## Failure handling

- If search returns no results, suggest different keywords or relaxing filters.
- If transcript fails, check if the video has captions using `/trainability`.
- If `SCAVIO_API_KEY` is not set, prompt the user to export it before continuing.

## LangChain

```bash
pip install scavio-langchain
```

```python
from scavio_langchain import ScavioSearchTool
tool = ScavioSearchTool(engine="youtube")
```
