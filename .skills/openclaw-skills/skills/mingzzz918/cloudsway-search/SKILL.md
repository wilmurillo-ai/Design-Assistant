---
name: cloudsway-search
description: "Fast web search for AI agents. Use when: user asks to search, Google something, look up info, find news, research topics. Better Chinese support than Brave/Tavily. Returns snippets + smart excerpts + full content. NOT for: facts AI knows, math, code-only tasks."
homepage: https://www.cloudsway.ai
metadata: { "openclaw": { "emoji": "🌐", "tags": ["search", "web-search", "google", "news", "brave-alternative", "tavily-alternative", "中文搜索"], "requires": { "env": ["CLOUDSWAYS_AK"], "bins": ["curl", "jq"] } } }
---

# Cloudsway Search

🌐 **Fast web search for AI agents** — Simple, reliable, with smart content extraction.

> Brave/Tavily alternative with excellent Chinese language support.

## When to Use

✅ **USE this skill when:**
- "搜索 xxx" / "search xxx" / "Google xxx"
- "查一下 xxx" / "look up xxx"
- "有什么关于 xxx 的信息" / "find info about xxx"
- Real-time information needed
- News and current events
- Fact verification

❌ **DON'T use this skill when:**
- AI already knows the answer
- Math calculations
- Code-only tasks

## Setup

1. Get free API key: https://www.cloudsway.ai
2. Set env: `export CLOUDSWAYS_AK="your-key"`

## Usage

**Simple search:**
```bash
./scripts/search.sh '{"q": "your query"}'
```

**Recent news:**
```bash
./scripts/search.sh '{"q": "topic", "freshness": "Week", "count": 20}'
```

**Deep research:**
```bash
./scripts/search.sh '{"q": "topic", "enableContent": true, "mainText": true, "count": 20}'
```

## Parameters

| Param | Required | Default | Notes |
|-------|----------|---------|-------|
| q | ✅ | - | Search query |
| count | ❌ | 10 | **10/20/30/40/50 only** |
| freshness | ❌ | - | `Day` / `Week` / `Month` |
| enableContent | ❌ | false | Get full page content |
| mainText | ❌ | false | Smart excerpts (needs enableContent) |

## Why Cloudsway?

- ✅ **Smart excerpts** — AI-friendly content extraction
- ✅ **Chinese optimized** — Better than Brave/Tavily for 中文
- ✅ **Free tier** — Get started in 2 minutes
- ✅ **Fast** — Low latency responses

## Links

- 🔑 Get API Key: https://www.cloudsway.ai
- 📖 Docs: https://www.cloudsway.ai/docs
