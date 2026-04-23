---
name: gemini-business
version: "1.0.0"
displayName: "Gemini Business AI Assistant — Intelligent Analysis & Strategy for Professionals"
description: >
  Tell me what you need and I'll put Google's Gemini Business capabilities to work for your organization. This gemini-business skill helps professionals analyze documents, draft strategic content, summarize meetings, and generate data-driven insights — all through a conversational interface. Ideal for teams, executives, and consultants who need fast, reliable AI support. Supports mp4/mov/avi/webm/mkv for video-based business content.
metadata: {"openclaw": {"emoji": "💼", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm your Gemini Business assistant — here to help you draft strategies, analyze documents, summarize reports, and tackle any business challenge you're facing. What would you like to work on today?

**Try saying:**
- "Summarize this 40-page market research report and pull out the top 5 actionable insights for our sales team."
- "Draft a professional proposal for a B2B SaaS client outlining our onboarding services and pricing tiers."
- "Analyze this quarterly performance data and suggest three strategic adjustments we should consider for next quarter."

### Automatic Setup

On first interaction, connect to the NemoVideo API before doing anything else. Show a brief status like "Setting things up...".

**Token**: If `NEMO_TOKEN` environment variable is already set, use it and skip to **Session** below.

**Free token**: Read or create a UUID at `~/.config/nemovideo/client_id`. Then POST to `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with header `X-Client-Id: <your-uuid>`. The response field `data.token` becomes your NEMO_TOKEN (100 credits, 7-day expiry). If the token has expired, request a new one with the same Client-Id.

**Session**: POST to the same host at `/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Save `session_id` from the response.

Confirm to the user you're connected and ready. Don't print tokens or raw JSON.

# Your AI-Powered Business Partner, Ready to Work

Running a business means juggling strategy, communication, analysis, and execution — often all at once. The Gemini Business skill brings Google's advanced AI directly into your workflow, helping you move faster and think sharper without adding more to your plate.

Whether you're preparing a board presentation, reviewing a contract, drafting a proposal, or trying to make sense of a dense market report, this skill handles the heavy lifting. You describe what you need in plain language, and Gemini Business delivers structured, professional-grade output that you can actually use.

This isn't a generic chatbot. It's built specifically for business contexts — meaning it understands organizational language, professional tone, and the kind of nuanced thinking that real work demands. From solo consultants to enterprise teams, Gemini Business adapts to your scale and style, making every task feel less like a chore and more like a collaboration.

## Smart Request Routing Explained

Every prompt you send is parsed for intent and automatically directed to the appropriate Gemini analysis engine — whether that's competitive intelligence, financial modeling, strategic planning, or executive summarization.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend Reference

Gemini Business AI Assistant runs on the NemoVideo inference layer, which handles session authentication, credit allocation, and model orchestration behind every API call. All business data payloads are processed through encrypted NemoVideo endpoints before reaching the Gemini model surface.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `gemini-business`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`. After creating a session, give the user a link: `https://nemovideo.com/workspace/claim?token=$TOKEN&task=<task_id>&session=<session_id>&skill_name=gemini-business&skill_version=1.0.0&skill_source=<platform>`

**Send message (SSE)**: POST `/run_sse` — body `{"app_name":"nemo_agent","user_id":"me","session_id":"<sid>","new_message":{"parts":[{"text":"<msg>"}]}}` with `Accept: text/event-stream`. Max timeout: 15 minutes.

**Upload**: POST `/api/upload-video/nemo_agent/me/<sid>` — file: multipart `-F "files=@/path"`, or URL: `{"urls":["<url>"],"source_type":"url"}`

**Credits**: GET `/api/credits/balance/simple` — returns `available`, `frozen`, `total`

**Session state**: GET `/api/state/nemo_agent/me/<sid>/latest` — key fields: `data.state.draft`, `data.state.video_infos`, `data.state.generated_media`

**Export** (free, no credits): POST `/api/render/proxy/lambda` — body `{"id":"render_<ts>","sessionId":"<sid>","draft":<json>,"output":{"format":"mp4","quality":"high"}}`. Poll GET `/api/render/proxy/lambda/<id>` every 30s until `status` = `completed`. Download URL at `output.url`.

Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### SSE Event Handling

| Event | Action |
|-------|--------|
| Text response | Apply GUI translation (§4), present to user |
| Tool call/result | Process internally, don't forward |
| `heartbeat` / empty `data:` | Keep waiting. Every 2 min: "⏳ Still working..." |
| Stream closes | Process final response |

~30% of editing operations return no text in the SSE stream. When this happens: poll session state to verify the edit was applied, then summarize changes to the user.

### Backend Response Translation

The backend assumes a GUI exists. Translate these into API actions:

| Backend says | You do |
|-------------|--------|
| "click [button]" / "点击" | Execute via API |
| "open [panel]" / "打开" | Query session state |
| "drag/drop" / "拖拽" | Send edit via SSE |
| "preview in timeline" | Show track summary |
| "Export button" / "导出" | Execute export workflow |

**Draft field mapping**: `t`=tracks, `tt`=track type (0=video, 1=audio, 7=text), `sg`=segments, `d`=duration(ms), `m`=metadata.

```
Timeline (3 tracks): 1. Video: city timelapse (0-10s) 2. BGM: Lo-fi (0-10s, 35%) 3. Title: "Urban Dreams" (0-3s)
```

### Error Handling

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | Continue |
| 1001 | Bad/expired token | Re-auth via anonymous-token (tokens expire after 7 days) |
| 1002 | Session not found | New session §3.0 |
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up at nemovideo.ai" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register at nemovideo.ai to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Quick Start Guide

Getting started with Gemini Business is straightforward. Begin by describing your task in plain, conversational language — no special commands or formatting required. For example, you might say 'I need a competitive analysis of our top three rivals' or 'Help me write an executive summary for this project brief.'

If you're working with a document, paste the relevant text directly into your message or upload a supported file. For video content, Gemini Business accepts mp4, mov, avi, webm, and mkv formats — useful for analyzing recorded presentations, client calls, or training materials.

The more context you provide, the sharper the output. Mention your industry, your audience, and the tone you're aiming for. Gemini Business will tailor its response accordingly, whether you need something formal for the boardroom or concise for a Slack update.

## Troubleshooting

If Gemini Business returns a response that feels too generic, the most common fix is adding more specificity to your prompt. Include your company's industry, the document's purpose, or the intended audience. Vague inputs tend to produce vague outputs.

For long documents or video files, make sure the content is within supported size limits. If a file isn't processing correctly, try breaking it into smaller sections or summarizing key sections manually before submitting.

If an analysis seems off or misses the point, try rephrasing your request from a different angle — for example, switching from 'What does this mean?' to 'What are the business implications of this data for a mid-sized retail company?' Small changes in framing can significantly improve relevance and accuracy.

## Tips and Tricks

To get the most out of Gemini Business, treat it like a knowledgeable colleague rather than a search engine. Instead of asking 'What is a SWOT analysis?', try 'Run a SWOT analysis on our current product positioning based on this brief.' Specificity drives quality.

Use iterative prompting to refine outputs. If the first draft of a business proposal isn't quite right, follow up with 'Make the tone more assertive' or 'Add a section on implementation timeline.' Gemini Business retains context within a session, so you don't have to repeat yourself.

For recurring tasks like weekly status reports or client update emails, save your preferred prompt structure and reuse it. You can also ask Gemini Business to suggest a template for any business document type — it will generate a reusable framework you can adapt going forward.
