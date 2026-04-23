---
name: affiliate-video-creator
version: "1.0.3"
displayName: "Affiliate Video Creator — Turn Product Footage Into Commission-Ready Content"
description: >
  Drop a video and describe the product you're promoting — the affiliate-video-creator skill transforms raw footage into polished, persuasive affiliate content built to convert. Add compelling call-to-action overlays, highlight key product moments, and shape your narrative around your affiliate offer. Ideal for content creators, bloggers, and social marketers monetizing through affiliate programs. Supports mp4, mov, avi, webm, and mkv formats.
metadata: {"openclaw": {"emoji": "🎯", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! Ready to turn your product footage into affiliate content that actually converts? Drop your video, tell me about the product and your affiliate offer, and let's build something your audience will click on.

**Try saying:**
- "Here's my unboxing video of a fitness tracker — can you help me restructure it to highlight the features my affiliate audience cares most about and add a strong call-to-action near the end?"
- "I have a 10-minute software walkthrough. Can you help me trim it down to a tight 90-second affiliate promo that emphasizes the free trial offer?"
- "Turn this raw product review footage into a YouTube-ready affiliate video with an intro hook, key benefit highlights, and a clear 'link in bio' CTA segment."

On first use, the skill connects to NemoVideo automatically:
1. Check for `NEMO_TOKEN` env var, or acquire one via `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` (100 free credits)
2. Persist a Client-ID to `~/.config/nemovideo/client_id` for rate-limit tracking (UUID only, no secrets)
3. Create a session and start working immediately

# From Raw Footage to Affiliate Sales Machines

Most affiliate marketers know the struggle: you have a great product, a solid audience, and a commission link — but turning that into video content that actually drives clicks takes real effort. The affiliate-video-creator skill closes that gap by helping you shape your video around the affiliate offer itself, not just the footage you started with.

Whether you're reviewing a gadget, unboxing a subscription box, or walking through a software tool, this skill helps you structure your content with the affiliate buyer's journey in mind. You can emphasize the right product moments, layer in persuasive messaging, and make sure your call-to-action lands at exactly the right time.

This is built for creators who are serious about monetization — not just making videos, but making videos that earn. From Amazon Associates and ShareASale to niche brand deals, the affiliate-video-creator skill gives your content the production quality and conversion focus it needs to stand out in crowded feeds.

### Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEMO_TOKEN` | Auto-acquired on first use (100 free credits, 7-day expiry) | API authentication |
| `NEMO_API_URL` | `https://mega-api-prod.nemovideo.ai` | API base URL |

## Routing Your Creative Requests

Every request you send — whether you're scripting a hook, generating b-roll sequences, adding affiliate CTAs, or rendering a final cut — gets routed to the appropriate NemoVideo pipeline based on the intent and asset type detected in your prompt.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

Under the hood, the NemoVideo backend handles video synthesis, voiceover layering, and commission-link overlay rendering through a session-based API that keeps your project assets and timeline data persistent across edits. Each render job is tokenized, so your affiliate metadata — product IDs, tracking URLs, and CTA timestamps — stays bound to the correct output file throughout the generation process.

**Required headers** on all requests: `X-Skill-Source: $SKILL_NAME`, `X-Skill-Version: $SKILL_VERSION`, `X-Skill-Platform: $SKILL_SOURCE`

**Create session**: `POST $API/api/tasks/me/with-session/nemo_agent` — returns `task_id` and `session_id`

**Send message (SSE)**: `POST $API/run_sse` with `session_id` and user message. Stream responses; ~30% of edits return no text (query state to confirm changes).

**Upload**: `POST $API/api/upload-video/nemo_agent/me/<sid>` — file or URL upload. Supports: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

**Check credits**: `GET $API/api/credits/balance/simple`

**Query state**: `GET $API/api/state/nemo_agent/me/<sid>/latest` — check draft, tracks, generated media

**Export**: `POST $API/api/render/proxy/lambda` — export does NOT cost credits. Poll `GET $API/api/render/proxy/lambda/<id>` until `status: completed`.

**Task link**: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### Common Errors

If you hit a token expiration mid-session, simply re-authenticate through the ClawHub interface and your draft timeline will be restored automatically. A 'session not found' error means your project context was cleared — start a fresh session and re-upload your raw footage or product clips to continue. If you're out of render credits, head to nemovideo.ai to register or top up so you can keep pushing content to your affiliate channels without interruption.

## Quick Start Guide

Getting started is straightforward. Upload your product video in any supported format — mp4, mov, avi, webm, or mkv — and in your message, describe the product, your affiliate program, and the audience you're targeting. The more context you give about the offer (discount codes, free trials, key selling points), the more targeted the output will be.

Next, tell the skill what platform the video is for. A YouTube affiliate review has different pacing and CTA placement than a 60-second TikTok or an Instagram Story. Specifying this upfront saves revision rounds.

Finally, mention any specific moments in your footage you want to keep or cut — a particularly good demo moment, a price reveal, or an awkward pause you want removed. The skill works best as a collaborative back-and-forth, so don't hesitate to iterate until the affiliate narrative feels exactly right for your audience and offer.

## Common Workflows

The most popular workflow starts with a product review or unboxing video — creators drop their raw footage and describe the affiliate program they're promoting. From there, the skill helps identify the strongest product moments to feature, suggests where to place CTAs for maximum click-through, and reshapes the pacing so viewers stay engaged through the pitch.

Another common use case is repurposing long-form content. A 20-minute YouTube review can be restructured into a focused 2-3 minute affiliate clip optimized for Instagram Reels or TikTok, with the commission link moment built directly into the narrative flow.

Some creators also use this skill to batch-produce affiliate videos across multiple products in a single session — uploading several clips and working through each one with tailored messaging per offer. This is especially useful during peak seasons like Black Friday or product launch windows when speed and volume matter.
