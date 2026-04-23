---
name: ai-video-monetization
version: "1.0.2"
displayName: "AI Video Monetization — Turn Your Video Content Into Revenue Streams"
description: >
  Tell me what you need and I'll help you unlock the earning potential of your video content through smart ai-video-monetization strategies. This skill analyzes your videos to identify sponsorship placement windows, ad break timing, merchandise moments, and audience retention patterns that directly impact revenue. Whether you're a YouTube creator, course seller, or brand publisher, get actionable monetization recommendations tailored to your content. Supports mp4, mov, avi, webm, and mkv formats.
metadata: {"openclaw": {"emoji": "💰", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
apiDomain: https://mega-api-prod.nemovideo.ai
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to help you maximize the revenue potential of your video content through AI-powered monetization analysis. Upload your video and tell me your monetization goals — let's find the money hiding in your footage.

**Try saying:**
- "Analyze this video and tell me the best timestamps to place mid-roll ads without hurting viewer retention"
- "What sections of my video are best suited for affiliate product mentions or sponsored segments?"
- "Review my YouTube video and suggest how to restructure it to qualify for higher CPM ad categories"

On first use, the skill connects to NemoVideo automatically:
1. Check for `NEMO_TOKEN` env var, or acquire one via `https://mega-api-prod.nemovideo.ai/api/auth/anonymous-token` (100 free credits)
2. Persist a Client-ID to `~/.config/nemovideo/client_id` for rate-limit tracking (UUID only, no secrets)
3. Create a session and start working immediately

# Make Every Frame of Your Video Work Harder

Most creators leave money on the table — not because their content is weak, but because they don't know where the revenue opportunities are hiding inside their videos. This skill changes that by scanning your video content and surfacing specific, timestamped recommendations for how to monetize more effectively.

Whether you want to know the best moments to insert mid-roll ads without killing viewer retention, which segments are primed for affiliate call-to-actions, or how to structure your content to qualify for higher CPM ad categories, this skill gives you a clear, prioritized action plan. It reads your video the way a monetization strategist would — looking at pacing, topic shifts, engagement triggers, and content type.

This is built for independent creators, small media teams, and digital marketers who are serious about turning their video libraries into consistent income. You don't need a media buyer or a revenue consultant — just upload your video and start asking questions.

### Environment

| Variable | Default | Purpose |
|----------|---------|---------|
| `NEMO_TOKEN` | Auto-acquired on first use (100 free credits, 7-day expiry) | API authentication |
| `NEMO_API_URL` | `https://mega-api-prod.nemovideo.ai` | API base URL |

## Routing Your Monetization Requests

Every prompt you send — whether it's generating ad-ready video clips, setting up paywall content, or querying revenue analytics — gets routed to the appropriate NemoVideo monetization pipeline based on intent detection.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo API Reference

The NemoVideo backend processes your AI video monetization workflows through a token-authenticated REST layer that handles everything from dynamic ad insertion and content licensing to subscription paywall generation and CPM optimization. Each API call consumes credits proportional to the complexity of the monetization task — short-form ad cuts cost less than full revenue-stream buildouts.

**Required headers** on all requests: `X-Skill-Source: $SKILL_NAME`, `X-Skill-Version: $SKILL_VERSION`, `X-Skill-Platform: $SKILL_SOURCE`

**Create session**: `POST $API/api/tasks/me/with-session/nemo_agent` — returns `task_id` and `session_id`

**Send message (SSE)**: `POST $API/run_sse` with `session_id` and user message. Stream responses; ~30% of edits return no text (query state to confirm changes).

**Upload**: `POST $API/api/upload-video/nemo_agent/me/<sid>` — file or URL upload. Supports: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

**Check credits**: `GET $API/api/credits/balance/simple`

**Query state**: `GET $API/api/state/nemo_agent/me/<sid>/latest` — check draft, tracks, generated media

**Export**: `POST $API/api/render/proxy/lambda` — export does NOT cost credits. Poll `GET $API/api/render/proxy/lambda/<id>` until `status: completed`.

**Task link**: `$WEB/workspace/claim?token=$TOKEN&task={task_id}&session={session_id}&skill_name=$SKILL_NAME&skill_version=$SKILL_VERSION&skill_source=$SKILL_SOURCE`

### Common Errors

If you hit a token expiration error, simply re-authenticate through your NemoVideo dashboard and restart the session with fresh credentials. A 'session not found' response means your context window has been cleared — initiate a new session and restate your monetization goal to get back on track. Running out of credits will block all video generation and revenue tooling, so register or top up at nemovideo.ai before continuing.

## Quick Start Guide

Getting started with ai-video-monetization is straightforward. Upload your video file in any supported format — mp4, mov, avi, webm, or mkv — and start with a broad prompt like: 'What are the top three ways I can monetize this video right now?'

From there, drill down into the area most relevant to your business model. Ad-supported creators should follow up by asking for specific timestamp recommendations and retention risk zones. Sponsorship-focused creators should ask which segments have the strongest contextual fit for brand integrations. Course creators should ask about paywall placement and upsell trigger moments.

Once you have your initial recommendations, ask the skill to help you write the actual script inserts, ad transition phrases, or CTA copy for the identified moments. The skill can move from analysis straight into content creation, making it a full end-to-end monetization workflow tool rather than just a diagnostic.

## Troubleshooting

If the skill returns vague monetization suggestions, it usually means the video lacks enough context. Try re-prompting with details like your niche, typical viewer demographics, and which monetization method you're prioritizing — ads, sponsorships, merchandise, or paid content gates.

For longer videos over 45 minutes, consider uploading in segments or specifying a time range you want analyzed first. This helps the skill focus its recommendations rather than spreading analysis too thin across a lengthy runtime.

If you're not seeing ad placement suggestions for a video, check whether your content falls into categories that ad networks typically restrict — finance, health, and political content often require adjusted monetization strategies. Ask the skill specifically about 'alternative monetization paths' for restricted niches and it will pivot to sponsorship and direct revenue options instead.

## Tips and Tricks

To get the most out of ai-video-monetization analysis, always tell the skill your platform context upfront — a TikTok short monetizes very differently than a 30-minute YouTube tutorial. The more specific you are about your audience and niche, the sharper the recommendations will be.

If you're running a video course or membership content, ask specifically about 'value density mapping' — the skill can identify moments where your content delivers peak educational value, which are ideal anchors for upsell prompts or upgrade CTAs.

For ad-supported creators, try uploading multiple videos from the same series and asking for pattern analysis across episodes. Consistent ad placement patterns train viewer expectations and can meaningfully improve click-through rates on sponsored segments. Don't just optimize one video — build a monetization template you can reuse.
