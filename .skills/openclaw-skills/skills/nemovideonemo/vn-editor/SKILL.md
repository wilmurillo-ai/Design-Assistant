---
name: vn-editor
version: "1.0.0"
displayName: "VN Editor Assistant — AI-Powered Video Editing Guidance for VN App Users"
description: >
  Turn raw footage into polished, share-ready videos with expert guidance tailored to the vn-editor workflow. This skill helps VN app users craft cinematic cuts, apply transitions, sync music to beats, and fine-tune color grading — all through conversational prompts. Whether you're editing Reels, vlogs, or short films, vn-editor support covers every step from timeline assembly to final export. Works with mp4, mov, avi, webm, and mkv files. No guesswork, just clear, actionable editing direction.
metadata: {"openclaw": {"emoji": "🎬", "requires": {"env": ["NEMO_TOKEN"], "configPaths": ["~/.config/nemovideo/"]}, "primaryEnv": "NEMO_TOKEN"}}
homepage: https://nemovideo.com
repository: https://github.com/nemovideo/nemovideo_skills
---

## Getting Started

> Welcome! I'm here to help you get the most out of VN Editor — whether you're cutting your first vlog or polishing a cinematic short. Tell me what you're working on and let's build something great together.

**Try saying:**
- "How do I sync my video cuts to the beat of a song in VN Editor?"
- "What's the best way to do a smooth slow-motion ramp effect in VN?"
- "How can I color grade my footage to look cinematic using VN's filters and curves?"

**Setup**: This skill connects to the NemoVideo API at `mega-api-prod.nemovideo.ai`. Set the `NEMO_TOKEN` environment variable to authenticate. New users can get 100 free credits at nemovideo.ai.

# Edit Like a Pro Using VN's Full Toolkit

VN is one of the most capable free video editors available on mobile and desktop, yet many users only scratch the surface of what it can do. This skill bridges that gap by walking you through VN's layered timeline, keyframe animations, masking tools, and audio mixing features in plain language — no jargon, no tutorials to scrub through.

Whether you're assembling a travel vlog, cutting a product demo, or building a cinematic short, the vn-editor skill helps you make intentional creative decisions rather than random ones. You'll learn when to use speed ramping versus a hard cut, how to stack adjustment layers for a consistent color tone, and how to time your transitions so they feel natural rather than jarring.

This skill is designed for creators at every level — from someone editing their first video on VN to experienced editors looking to speed up their workflow. Ask anything from 'how do I remove background noise in VN?' to 'what's the best way to create a smooth slow-motion ramp?' and get a direct, specific answer built around VN's actual interface and features.

## Routing Your Edit Requests

When you describe a cut, transition, color grade, or audio sync issue in VN, your request is parsed by intent and routed to the most relevant editing guidance module automatically.

| User says... | Action | Skip SSE? |
|-------------|--------|----------|
| "export" / "导出" / "download" / "send me the video" | → §3.5 Export | ✅ |
| "credits" / "积分" / "balance" / "余额" | → §3.3 Credits | ✅ |
| "status" / "状态" / "show tracks" | → §3.4 State | ✅ |
| "upload" / "上传" / user sends file | → §3.2 Upload | ✅ |
| Everything else (generate, edit, add BGM…) | → §3.1 SSE | ❌ |

## NemoVideo Backend Reference

The NemoVideo backend powers real-time clip analysis, timeline suggestions, and effect recommendations tailored to VN's layer-based editing structure. All API calls reference your active VN project session to deliver context-aware responses.

Include on every request: `Authorization: Bearer $NEMO_TOKEN`, `X-Skill-Source`, `X-Skill-Version`, `X-Skill-Platform`.

**Workflow**: Create a session at `/api/tasks/me/with-session/nemo_agent`, send user messages via SSE at `/run_sse`, upload media to `/api/upload-video/nemo_agent/me/{sid}`, check project state at `/api/state/nemo_agent/me/{sid}/latest`, and export the final video at `/api/render/proxy/lambda` (export is free). Supported formats: mp4, mov, avi, webm, mkv, jpg, png, gif, webp, mp3, wav, m4a, aac.

### Troubleshooting

If your token expires mid-session, simply re-authenticate through your NemoVideo account to resume without losing your edit context. A 'session not found' error means your project session timed out — start a fresh session and re-import your VN timeline details. Running out of credits will pause AI responses, so head to nemovideo.ai to register or top up before continuing.

## Troubleshooting Common VN Editor Issues

If your exported video looks blurry or lower quality than expected, check that your export resolution matches your source footage — VN defaults to 1080p but can be set up to 4K depending on your device. Always set the bitrate to 'High' or 'Recommended' before exporting to avoid compression artifacts.

Audio sync drifting is a common issue when mixing multiple clips with different frame rates. To fix this in VN, ensure all clips on your timeline share the same frame rate by checking each clip's properties before assembling your edit. If sync issues persist after export, try re-importing the audio track as a separate layer and manually aligning it.

If VN is crashing during export of longer projects, try splitting the project into segments and exporting each separately, then joining them. This is especially useful on older devices where RAM becomes a limiting factor with complex timelines featuring multiple overlay layers and effects.

## Use Cases — What You Can Build with VN Editor

VN Editor is a strong fit for social-first content creators who need fast turnarounds without sacrificing quality. Instagram Reels and TikTok videos benefit from VN's beat-sync markers and built-in transition library, letting you cut to music rhythmically without manual frame counting.

For vloggers and travel creators, VN's multi-track timeline supports B-roll layering, voiceover recording, and ambient sound mixing in a single project — making it possible to tell a complete story entirely within the app. The keyframe tool lets you add subtle camera pan effects to still photos, adding motion to otherwise static shots.

Brand and product video creators can use VN's text animation presets, masking features, and color grading tools to produce clean, professional-looking content that holds up alongside footage edited in desktop software. The skill helps you adapt these tools to your specific brand style and output format, whether that's a square post, a vertical Story, or a 16:9 YouTube upload.
