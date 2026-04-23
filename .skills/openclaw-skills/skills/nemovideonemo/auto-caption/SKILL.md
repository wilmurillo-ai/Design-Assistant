---
name: auto-caption
version: "1.0.0"
displayName: "Auto Caption - AI Subtitle Generator for TikTok YouTube and Reels"
description: >
  One-click automatic captions for any video. Drop a file, get perfectly timed subtitles
  in seconds. Built-in presets for TikTok, YouTube, and Instagram Reels — font size,
  safe zones, and positioning are handled automatically. Zero configuration needed.
  Use when user wants to: auto caption video, automatic subtitles, one click captions,
  TikTok captions, YouTube subtitles, Reels captions, instant subtitles, quick captions,
  no config subtitle, fast caption generator, auto transcribe video, voice to text video,
  caption preset, platform ready subtitles. Supports mp4, mov, webm, mkv.
metadata: {"openclaw": {"emoji": "⚡", "requires": {"env": [], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
---

# Auto Caption — Instant Subtitles, Zero Setup

Drop a video, get captions. No settings to tweak, no timelines to scrub. Auto Caption transcribes speech, syncs timing to the word, and formats subtitles for your target platform automatically.

## 1. What This Skill Does

You are an OpenClaw agent that provides **instant, zero-configuration captioning**. The philosophy: users should never have to think about font size, positioning, or timing — the skill handles all of it based on the target platform.

**Speed-first design:**
- Upload → captions generated → delivered. Three steps, no questions asked.
- Platform preset applied automatically (TikTok / YouTube / Reels) or user specifies.
- Default: burn captions into video. User can request SRT/VTT instead.

**The backend does NOT know about OpenClaw.** GUI references from the backend are intercepted and translated to chat actions.

### Environment Variables

| Variable | Required | Default |
|----------|----------|---------|
| `NEMO_TOKEN` | No | Auto-generated on first use |
| `NEMO_API_URL` | No | `https://mega-api-prod.nemovideo.ai` |
| `NEMO_WEB_URL` | No | `https://nemovideo.com` |
| `NEMO_CLIENT_ID` | No | Auto-generated UUID, persisted to `~/.config/nemovideo/client_id` |
| `SKILL_SOURCE` | No | Auto-detected from install path |

Token setup if `NEMO_TOKEN` is not set:
```bash
CLIENT_ID="${NEMO_CLIENT_ID:-$(cat ~/.config/nemovideo/client_id 2>/dev/null)}"
if [ -z "$CLIENT_ID" ]; then
  CLIENT_ID=$(uuidgen 2>/dev/null || echo "client-$(date +%s)-$RANDOM")
  mkdir -p ~/.config/nemovideo && echo "$CLIENT_ID" > ~/.config/nemovideo/client_id
fi
curl -s -X POST "$API/api/auth/anonymous-token" -H "X-Client-Id: $CLIENT_ID"
```
Save `token` as `NEMO_TOKEN`. Expires after 7 days; re-request with same `X-Client-Id`.

## 2. The Fast Path

When a user sends a video (or asks for captions), run the entire pipeline without asking questions:

**Step 1 — Upload** → **Step 2 — Caption** → **Step 3 — Deliver**

Only pause to ask if the user hasn't specified a language and the audio is ambiguous.

### Decision Table

| User input | Action | Ask anything? |
|------------|--------|:---:|
| Sends video file, no other context | Upload → auto-caption → burn → deliver | No |
| "caption this for TikTok" | Upload → caption with TikTok preset → deliver | No |
| "add subtitles in Spanish" | Upload → caption → translate to Spanish → deliver | No |
| "just give me the SRT" | Upload → caption → export SRT file | No |
| "translate my captions to French" | Translate existing captions → deliver | No |
| "make the text bigger" / "change font" | Style adjustment via SSE | No |
| "export" / "download" | Render with captions → deliver | No |
| "credits" / "balance" | Check §3.3 | No |

## 3. API Reference

`$API` = `${NEMO_API_URL:-https://mega-api-prod.nemovideo.ai}`, `$TOKEN` = `${NEMO_TOKEN}`, `$WEB` = `${NEMO_WEB_URL:-https://nemovideo.com}`.

All requests require headers:
```
X-Skill-Source: $SKILL_NAME
X-Skill-Version: $SKILL_VERSION
X-Skill-Platform: $SKILL_SOURCE
```

### 3.0 Session
```bash
curl -s -X POST "$API/api/tasks/me/with-session/nemo_agent" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"task_name":"auto_caption","language":"<lang>"}'
```
Save `session_id`, `task_id`. Browser: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### 3.1 Send Message (SSE)
```bash
curl -s -X POST "$API/run_sse" \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" --max-time 900 \
  -d '{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}'
```
SSE: text → show user (strip GUI); tools → wait; heartbeat → "⏳ Captioning..."; close → show result. Silent edits (~30%): query §3.4, diff text tracks, report.

### 3.2 Upload
**File**: `curl -s -X POST "$API/api/upload-video/nemo_agent/me/<sid>" -H "Authorization: Bearer $TOKEN" -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" -F "files=@/path/to/file"`

**URL**: same endpoint, `-d '{"urls":["<url>"],"source_type":"url"}'`

Accepts: mp4, mov, avi, webm, mkv, mp3, wav, m4a, aac.

### 3.3 Credits
```bash
curl -s "$API/api/credits/balance/simple" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
```

### 3.4 Project State
```bash
curl -s "$API/api/state/nemo_agent/me/<sid>/latest" -H "Authorization: Bearer $TOKEN" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE"
```
Draft: `t`=tracks, `tt`=type (0=video, 1=audio, 7=text), `sg`=segments. Captions live in tt=7 tracks.

### 3.5 Render & Deliver
Export is free. Confirm captions exist (§3.4), then:
```bash
curl -s -X POST "$API/api/render/proxy/lambda" -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -H "X-Skill-Source: $SKILL_NAME" -H "X-Skill-Version: $SKILL_VERSION" -H "X-Skill-Platform: $SKILL_SOURCE" \
  -d '{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}'
```
Poll `GET $API/api/render/proxy/lambda/<id>` every 30s. Download from `output.url`.

### 3.6 Disconnect Recovery
Don't re-send. Wait 30s → check §3.4. After 5 unchanged checks → report failure.

### 3.7 SRT/VTT Export
Extract text tracks from §3.4, format as SRT (`1\n00:00:01,000 --> 00:00:04,500\nText`) or VTT (`WEBVTT\n\n00:00:01.000 --> 00:00:04.500\nText`). Deliver file directly — no render needed.

## 4. Platform Presets

Auto-applied based on user mention or video aspect ratio:

| Platform | Aspect | Font | Position | Safe zone |
|----------|--------|------|----------|-----------|
| TikTok | 9:16 | Bold, 40px | Bottom center | Avoid bottom 20% (controls) |
| YouTube | 16:9 | Regular, 32px | Bottom center | Standard CC area |
| Reels | 9:16 | Bold, 38px | Bottom third | Avoid top 15% (username) |
| Default | Auto | Regular, 36px | Bottom center | 10% margins |

If user doesn't specify, detect from aspect ratio: 9:16 → TikTok preset, 16:9 → YouTube preset.

## 5. GUI Translation

| Backend says | You do |
|-------------|--------|
| "click Export" | §3.5 render |
| "open subtitle editor" | Show captions from §3.4 |
| "adjust in timeline" | Edit via §3.1 |
| "check billing" | §3.3 |

## 6. Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | OK | Continue |
| 1001 | Token expired | Re-auth |
| 1002 | Session gone | New session |
| 2001 | No credits | Show registration link |
| 4001 | Bad format | Show accepted formats |
| 402 | Export restricted | "Register at nemovideo.ai" |
| 429 | Rate limited | Retry in 30s |

No speech detected → "No spoken audio found in this video. Send a video with speech, or tell me what text to overlay."

## 7. Costs & Updates

Token scopes: `read` | `write` | `upload` | `render` | `*`. Check for updates: `clawhub search auto-caption --json`.