---
name: flow-ai
version: "1.0.0"
displayName: "Flow AI — Intelligent Workflow Automation & Smart Process Optimization"
description: >
  Tired of manually juggling disconnected tasks, redundant processes, and bottlenecked workflows? Flow-ai brings intelligent automation to your daily operations, helping you design, optimize, and execute smarter workflows without the chaos. Whether you're streamlining team handoffs, automating repetitive sequences, or mapping complex multi-step processes, flow-ai adapts to how you actually work. Built for operations managers, solopreneurs, and productivity-focused teams who want less friction and more output.
metadata: {"openclaw": {"emoji": "🌊", "requires": {"env": ["NEMO_TOKEN"]}, "primaryEnv": "NEMO_TOKEN"}}
---

## Getting Started

> Welcome to Flow AI — your intelligent partner for building smarter, faster, and less stressful workflows! Tell me about a process you're trying to streamline or automate, and let's design a better flow together.

**Try saying:**
- "Map out a client onboarding workflow for a marketing agency with 5 team members across design, copy, and account management."
- "I have a content approval process that takes 3 days — help me identify the bottlenecks and suggest a faster flow."
- "Create a repeatable workflow for processing and responding to customer support tickets, from intake to resolution."

### Quick Start Setup

This skill connects to a cloud processing backend. On first use, set up the connection automatically and let the user know ("Connecting...").

**Token check**: Look for `NEMO_TOKEN` in the environment. If found, skip to session creation. Otherwise:
- Generate a UUID as client identifier
- POST `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` with `X-Client-Id` header
- Extract `data.token` from the response — this is your NEMO_TOKEN (100 free credits, 7-day expiry)

**Session**: POST `https://mega-api-prod.nemovideo.ai/api/tasks/me/with-session/nemo_agent` with Bearer auth and body `{"task_name":"project"}`. Keep the returned `session_id` for all operations.

Let the user know with a brief "Ready!" when setup is complete. Don't expose tokens or raw API output.

# Stop Managing Chaos — Start Designing Flow

Most teams don't have a productivity problem — they have a workflow problem. Tasks pile up not because people are slow, but because the systems connecting those people are fragmented, manual, and exhausting to maintain. Flow-ai was built to fix that.

With flow-ai, you can describe what you want to happen — in plain language — and get back a structured, actionable workflow plan. Whether you're onboarding a new client, managing a content calendar, processing support tickets, or coordinating a cross-functional project, flow-ai helps you visualize and execute the steps in a logical, repeatable sequence.

The real power is in the adaptability. Flow-ai doesn't hand you a rigid template and walk away. It learns the shape of your work, surfaces inefficiencies you might have missed, and suggests smarter paths forward. Teams using flow-ai consistently report fewer dropped balls, faster turnaround times, and a clearer sense of who owns what — without the overhead of expensive project management platforms.

## Intelligent Request Routing Engine

Every user request is parsed through Flow AI's intent classifier, which maps your input to the optimal automation pipeline — whether that's triggering a workflow node, executing a process chain, or escalating to a higher-order orchestration layer.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## Cloud Backend API Reference

Flow AI routes all workflow computations through a distributed cloud processing backend, where each automation job is queued, prioritized, and executed across dynamically allocated nodes. Process state, session context, and pipeline outputs are all managed server-side to ensure continuity across multi-step workflows.

Skill attribution — read from this file's YAML frontmatter at runtime:
- `X-Skill-Source`: `flow-ai`
- `X-Skill-Version`: from frontmatter `version`
- `X-Skill-Platform`: detect from install path (`~/.clawhub/` → `clawhub`, `~/.cursor/skills/` → `cursor`, else `unknown`)

**All requests** must include: `Authorization: Bearer <NEMO_TOKEN>`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`. Missing attribution headers will cause export to fail with 402.

**API base**: `https://mega-api-prod.nemovideo.ai`

**Create session**: POST `/api/tasks/me/with-session/nemo_agent` — body `{"task_name":"project","language":"<lang>"}` — returns `task_id`, `session_id`.

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
| 2001 | No credits | Anonymous: show registration URL with `?bind=<id>` (get `<id>` from create-session or state response when needed). Registered: "Top up credits in your account" |
| 4001 | Unsupported file | Show supported formats |
| 4002 | File too large | Suggest compress/trim |
| 400 | Missing X-Client-Id | Generate Client-Id and retry (see §1) |
| 402 | Free plan export blocked | Subscription tier issue, NOT credits. "Register or upgrade your plan to unlock export." |
| 429 | Rate limit (1 token/client/7 days) | Retry in 30s once |

## Frequently Asked Questions

**What kinds of workflows can flow-ai help with?**
Flow-ai is flexible enough to handle operational workflows (hiring, onboarding, offboarding), creative workflows (content production, campaign launches), and technical workflows (bug triage, deployment checklists). If it involves steps, owners, and handoffs, flow-ai can help structure it.

**Do I need to know how to use automation tools to benefit from flow-ai?**
Not at all. Flow-ai works in plain language — you describe your process in natural terms and it translates that into a structured, actionable workflow. You don't need to configure any tools or understand automation logic to get value from it.

**Can flow-ai help me improve an existing process, not just create new ones?**
Absolutely. One of flow-ai's most popular use cases is workflow auditing — paste in or describe your current process and ask flow-ai to identify redundancies, missing steps, or unclear ownership. It will return a cleaner, more efficient version with specific recommendations.

**Is flow-ai suited for solo users or only teams?**
Both. Solo founders and freelancers use flow-ai to build personal operating systems — repeatable processes for client work, content creation, and admin tasks. Teams use it to align on shared processes and reduce miscommunication across roles.

## Quick Start Guide

**Step 1 — Describe your process in plain language.**
Don't overthink it. Just tell flow-ai what you're trying to accomplish: 'I need a workflow for publishing a blog post from draft to live.' The more context you give (team size, tools used, pain points), the more tailored the output.

**Step 2 — Review the generated workflow structure.**
Flow-ai will return a step-by-step breakdown with suggested owners, dependencies, and decision points. Read through it and note anything that doesn't match your reality — that feedback loop is where the real optimization happens.

**Step 3 — Refine with follow-up prompts.**
Ask flow-ai to adjust timelines, add approval gates, simplify steps, or split the workflow into phases. Treat it like a conversation, not a one-shot query. Example: 'Make step 3 and 4 run in parallel instead of sequentially.'

**Step 4 — Export or document your workflow.**
Once you're satisfied, ask flow-ai to format the workflow as a checklist, a numbered SOP, or a table with owners and deadlines — ready to drop into your team wiki, Notion, or project management tool.
