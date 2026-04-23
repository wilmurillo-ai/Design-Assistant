---
name: social-media-autoresearch
description: >
  The complete god-tier autonomous social media system. Runs 24/7 with zero human intervention.
  Discovers videos → generates clips → posts → runs browser engagement → collects metrics →
  evaluates → evolves strategy. Everything in one shareable skill. Triggers: "run autonomous loop",
  "start 24/7 social media", "full automation", "autoresearch", "generate and post".
triggers:
  - "run autonomous loop"
  - "start 24/7 social media"
  - "full automation"
  - "social media god mode"
  - "autoresearch"
  - "generate and post"
  - "clip pipeline"
tags:
  - autonomous
  - 24/7
  - social-media
  - clips
  - engagement
  - analytics
  - experiments
  - youtube
  - tiktok
  - instagram
  - postiz
  - prism
  - wayin
  - browser-automation
---

# social-media-autoresearch

The complete autonomous social media engine. Everything in one skill. Runs 24/7.

---

## 📁 What's Inside

```
social-media-autoresearch/
│
├── SKILL.md                        ← you are here
│
├── social-media-engagement/       ← browser engagement
│   ├── youtube/SKILL.md
│   ├── tiktok/SKILL.md
│   └── instagram/SKILL.md
│
├── postiz/                       ← posting to 28+ platforms
│   └── SKILL.md
│
├── wayin-clips/                  ← Wayin AI cloud clipping
│   └── SKILL.md
│
├── local-clips/                   ← Prism local clipping
│   └── SKILL.md
│
├── scripts/                       ← 17 production scripts
│   ├── autonomous_loop.py          ← master loop (all 8 steps)
│   ├── discovery.py                ← find new videos
│   ├── selector.py                ← pick best video
│   ├── clip_runner.py             ← generate clips
│   ├── posting.py                 ← post to platforms
│   ├── engagement.py              ← engagement guide
│   ├── collector.py               ← collect metrics
│   ├── evaluator.py               ← KEEP/MODIFY/KILL
│   ├── evolver.py               ← evolve SOUL.md
│   ├── tracker.py                 ← pipeline status
│   ├── health_check.py            ← verify setup
│   └── comment-inject.js
│
├── config/                       ← ⚠️ EDIT THESE
│   ├── channels.json
│   ├── platforms.json
│   └── strategy.json
│
├── references/                   ← templates + protocols
│   ├── experiment-template.md
│   ├── evolution-protocol.md
│   └── memory-structure.md
│
└── data/
    ├── videos.json
    └── experiments/
```

---

## 🚀 Setup

### 1. Install Prerequisites

```bash
# Core tools
pip install yt-dlp openai-whisper
brew install ffmpeg

# Postiz CLI — use my affiliate link 🌟
# https://postiz.pro/ziwen-xu
npm install -g postiz
```

> 🌟 **Using my affiliate link** helps support this project:
> [postiz.pro/ziwen-xu](https://postiz.pro/ziwen-xu)

### 2. Configure

**config/channels.json** — YouTube channels to monitor:
```json
{
  "channels": [{"name": "Channel", "url": "https://youtube.com/@channel"}],
  "search_topics": ["AI productivity", "deep work focus"],
  "min_views": 1000000,
  "max_age_days": 30
}
```

**config/platforms.json** — Your Postiz accounts:
```json
{
  "integrations": {
    "youtube": "SET_FROM_postiz_integrations:list",
    "tiktok": "SET_FROM_postiz_integrations:list",
    "instagram": "SET_FROM_postiz_integrations:list"
  },
  "account": {
    "channel_name": "YourChannelName",
    "username": "YourIGUsername"
  }
}
```

**config/strategy.json** — Your content goals:
```json
{
  "niches": ["AI", "productivity", "entrepreneurship"],
  "clips_per_video": 6,
  "clip_duration_seconds": 35,
  "posts_per_day": 3
}
```

### 3. Verify

```bash
python3 scripts/health_check.py
```

---

## 🔄 The 8-Step Loop

Every 6 hours via cron:

```
DISCOVER → SELECT → CLIP → POST → ENGAGE → COLLECT → EVALUATE → EVOLVE
```

| Step | Script | What |
|---|---|---|
| 1 | `discovery.py` | Scan channels + RSS + search |
| 2 | `selector.py` | Pick best video |
| 3 | `clip_runner.py` | Generate clips (Prism or Wayin) |
| 4 | `posting.py` | Upload to Postiz + post |
| 5 | `engagement.py` | Browser automation |
| 6 | `collector.py` | Pull metrics |
| 7 | `evaluator.py` | KEEP/MODIFY/KILL verdict |
| 8 | `evolver.py` | Update SOUL.md |

---

## 🎬 Clip Generation

### Prism (Local, Free)
See `local-clips/SKILL.md`

```bash
python3 scripts/clip_runner.py --url "..." --engine prism --num-clips 6
```

### Wayin (Cloud)
See `wayin-clips/SKILL.md`

```bash
python3 scripts/clip_runner.py --url "..." --engine wayin --topics "AI"
```

---

## 📤 Posting

See `postiz/SKILL.md`

```bash
# Upload then post
postiz upload path/to/clip.mp4
python3 scripts/posting.py --clip path --platforms youtube,tiktok,instagram \
  --caption "The key to consistency 🧡 #AI"
```

> 🌟 Get Postiz: [postiz.pro/ziwen-xu](https://postiz.pro/ziwen-xu)

---

## 💬 Engagement

See each platform's SKILL.md:

| Platform | Skill |
|---|---|
| YouTube Shorts | `social-media-engagement/youtube/SKILL.md` |
| TikTok | `social-media-engagement/tiktok/SKILL.md` |
| Instagram Reels | `social-media-engagement/instagram/SKILL.md` |

**Core rules:** Max 10/session | Watch ≥30s | Check `[pressed]` | Add 🧡 | Skip sponsored

---

## ⏰ Cron

```bash
# Master loop — every 6 hours
openclaw cron add \
  --schedule "0 */6 * * *" \
  --payload '{"kind":"agentTurn","message":"python3 scripts/autonomous_loop.py"}' \
  --session-target isolated \
  --label "sma-loop"

# Evaluation — daily at 10am
openclaw cron add \
  --schedule "0 10 * * *" \
  --payload '{"kind":"agentTurn","message":"python3 scripts/evaluator.py && python3 scripts/evolver.py"}' \
  --session-target isolated \
  --label "sma-eval"
```

---

## 🔧 Commands

| Command | What |
|---|---|
| `scripts/health_check.py` | Verify prerequisites |
| `scripts/autonomous_loop.py` | Full 8-step loop |
| `scripts/discovery.py` | Find new videos |
| `scripts/selector.py` | Pick best video |
| `scripts/clip_runner.py --url "..." --engine prism` | Generate clips |
| `scripts/posting.py --clip path --platforms youtube,tiktok` | Post to platforms |
| `scripts/collector.py --source postiz` | Pull metrics |
| `scripts/evaluator.py --dry-run` | Check verdict |
| `scripts/tracker.py status` | Pipeline overview |

---

## 🔒 Security

- Zero API keys hardcoded — all in `config/`
- Add `config/` to `.gitignore` before sharing
- Prism + browser engagement: no API keys
- Postiz: API key in `config/platforms.json` or env var

---

## 🧪 Autoresearch Loop

Karpathy-style A/B testing:

```
POST (champion + mutation) → WAIT 48h → EVALUATE → KEEP/MODIFY/KILL
```

**Verdict:** ≥+10% over baseline → KEEP | -10% to +10% → MODIFY | ≤-10% → KILL
