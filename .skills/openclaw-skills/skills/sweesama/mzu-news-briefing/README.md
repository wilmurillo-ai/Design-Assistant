# Mzu News Briefing

> Multi-source AI/Tech news aggregator with intelligent daily briefings. Covers AI, technology, finance, and world events — with hot/cold ranking and source attribution.
>
> Supports **Twitter/X** (via bird CLI) **or Grok API** as primary search backend. No API key required for Twitter route.

---

## What It Does

When triggered, this skill:

1. Searches across **7 dimensions** (A: Newsletters, B: Community heat, C: AI models/big tech, D: Chinese media, E: Finance/funding, F: Policy/regulation, G: Market events)
2. Runs **8+ searches** per session, in serial (Brave Free concurrent limit = 1)
3. Cross-validates: 3+ sources → confirmed hot, dig deeper
4. Deduplicates and merges overlapping stories
5. Ranks by heat: 🔥 High → ⚡ Medium → 💤 Low/discard
6. Outputs structured briefing: **10-15 items**, high-heat items get deep analysis paragraphs

Output is **Chinese-first** with English technical terms on first use.

---

## Content Priority

| Tier | Weight | Coverage |
|------|--------|----------|
| 🥇 Core | 50% | AI / LLM / Agent / tools / research / funding |
| 🥈 Extended | 30% | Tech industry · big tech · product launches |
| 🥉 Supplementary | 20% | Finance · stocks · commodities · monetary policy |
| 🌍 Background | 10% | World events · geopolitics · major breaking news |

> Military news: rare, only when it directly impacts tech supply chains, energy markets, or AI industry structure.

---

## Installation

### Step 1: Install agent-reach

```bash
python -m venv ~/.agent-reach-venv
source ~/.agent-reach-venv/bin/activate  # Windows: .\.agent-reach-venv\Scripts\activate
pip install agent-reach
```

### Step 2: Configure search backend (pick one)

#### Option A: Twitter/X (recommended, free)

```bash
# Install bird CLI
npm install -g @steipete/bird

# Export cookies from Chrome
# 1. Log in to x.com in Chrome
# 2. Press F12 → Application → Cookies → x.com
# 3. Copy auth_token and ct0 values

# Save to file
echo "AUTH_TOKEN=your_auth_token_value" > ~/.agent-reach-twitter.env
echo "CT0=your_ct0_value" >> ~/.agent-reach-twitter.env

# Verify
bird --auth-token your_auth_token --ct0 your_ct0 whoami
```

**Load auth before each session:**
```bash
# Linux/macOS
export $(cat ~/.agent-reach-twitter.env | xargs)

# Windows (PowerShell)
Get-Content ~\.\.agent-reach-twitter.env | ForEach-Object { $kvp = $_.Split('=',2); [Environment]::SetEnvironmentVariable($kvp[0], $kvp[1], 'Process') }
```

#### Option B: Grok API

```bash
# 1. Get free API key at https://x.ai/api
# 2. Save it
echo "your_grok_api_key" > ~/.grok-api-key

# Grok is used directly in workflow — no extra CLI needed
```

### Step 3: Set up daily briefing (optional)

```bash
# 08:00 morning briefing
openclaw cron add "0 8 * * *" "请按 F:\\path\\to\\skills\\mzu-news-briefing\\SKILL.md 生成今日简报" --announce

# 22:00 evening briefing
openclaw cron add "0 22 * * *" "请按 F:\\path\\to\\skills\\mzu-news-briefing\\SKILL.md 生成今日简报" --announce
```

---

## Search Dimensions

| Dim | Topic | Key Sources |
|-----|-------|------------|
| A | Weekly newsletters | NeuralBuddies, gtmaipodcast, labla.org |
| B | Community heat | Hacker News, Reddit r/MachineLearning, GitHub Trending |
| C | AI models / big tech | Twitter/X (bird), releasebot.io, Grok API |
| D | Chinese media | 36kr, jiqizhixin.com, 1baijia.com |
| E | Finance / funding | aifundingtracker.com, Bloomberg AI |
| F | Policy / regulation | Reuters AI, Politico, NYT AI |
| G | Market events | (supplemental, triggered by major moves) |

**Minimum: 8 searches before output. Run serially, ≥2s between searches.**

---

## Output Format

```
📰 Mzu Daily Briefing YYYY-MM-DD HH:MM

Items: XX | Searches: XX | Dimensions: A/B/C/D/E/F
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 High Heat

1. [Title](URL)
   Source: Name | Date | Tags: #AI #Agent
   Summary: (50 chars)

   ▶ Why This Matters
   · Point 1
   · Point 2

⚡ Medium Heat

2. [Title](URL)
   Source: Name | Date | Tags: #Tech #Product
   Summary: (with key data)

💤 Low Heat (if any)

3. [Title](URL)
   Source: ...

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Dimension coverage: A(X) B(X) C(X) D(X) E(X) F(X)
Next briefing: HH:MM
```

---

## Source Priority

1. X/Twitter — official announcements, fastest
2. Reuters/BBC — breaking hard facts
3. Hacker News — developer community heat
4. 36Kr / jiqizhixin / 1baijia — Chinese tech press
5. The Verge / Wired / TechCrunch
6. MIT Tech Review
7. Newsletters

---

## Anti-Patterns

❌ `"AI news today"` → SEO noise
❌ Exact date ("2026-03-23") → forecast/analysis articles instead of news
❌ Fewer than 8 searches → <30% coverage

✅ Use "this week" / "latest"
✅ At least 8 searches before writing

---

## Notes

- HTTPS links only
- Paywalled content → mark "Subscription required"
- Objective tone only, no editorializing
- 10-15 items total, 3-5 high-heat
- All sources cited, every item traceable

---

## Troubleshooting

**bird: "Missing auth_token"**
→ Reload auth: `export $(cat ~/.agent-reach-twitter.env | xargs)` (Linux) or re-run the PowerShell load command

**Twitter auth expired**
→ Chrome: F12 → Cookies → x.com → copy new auth_token + ct0 → update `~/.agent-reach-twitter.env`

**Brave rate limited**
→ Wait 5 seconds between searches. Brave Free Plan allows 1 concurrent request.

**No Grok key**
→ Use Twitter route (free) or Brave search as fallback
