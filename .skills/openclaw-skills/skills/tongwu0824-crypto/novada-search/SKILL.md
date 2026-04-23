---
name: novada-search
description: "AI Agent search platform with 9 engines, Google 13 sub-types, vertical scene search, and intelligent auto/multi/extract modes. Designed for LLM and AI agent consumption."
---

# Novada Search v2.0

> Multi-engine AI search — 9 engines, 13 Google types, 9 vertical scenes, smart agent modes.
> Powered by [Novada Scraper API](https://novada.com).

**Get started in 30 seconds:**

1. Get your free API key → [novada.com](https://novada.com)
2. Set the key: `export NOVADA_API_KEY="your_key"` (or add to `~/.openclaw/.env`)
3. Search: `python3 {baseDir}/scripts/novada_search.py --query "coffee Berlin" --scene local`

---

## Real-World Example

**Query:** `--query "dessert Düsseldorf" --scene local`

**Output:**

### 🍰 Düsseldorf TOP 5 Dessert Shops

| Rank | Shop | Rating | Reviews | Address |
|:----:|:-----|:------:|:-------:|:--------|
| 🥇 | [donecake](https://www.google.com/maps/search/?api=1&query=donecake%20Graf-Adolf-Stra%C3%9Fe%2068) | 4.8★ | 3,500 | Graf-Adolf-Straße 68 |
| 🥈 | [SugArt Factory](https://www.google.com/maps/search/?api=1&query=SugArt%20Factory%20Schlo%C3%9Fstra%C3%9Fe%2076-78) | 4.8★ | 423 | Schloßstraße 76-78 |
| 🥉 | [Eiscafe Pia](https://www.google.com/maps/search/?api=1&query=Eiscafe%20Pia%20Kasernenstra%C3%9Fe%201) | 4.7★ | 2,100 | Kasernenstraße 1 |
| 4 | [Unbehaun Eis](https://www.google.com/maps/search/?api=1&query=Unbehaun%20Eis%20Aachener%20Str.%20159) | 4.6★ | 5,000 | Aachener Str. 159 |
| 5 | [Aux Merveilleux de fred](https://www.google.com/maps/search/?api=1&query=Aux%20Merveilleux%20de%20fred%20Kasernenstra%C3%9Fe%2015) | 4.6★ | 626 | Kasernenstraße 15 |

> Click any shop name to open in Google Maps. This is the default `enhanced` output — actionable links, no extra flags needed.

---

## Architecture

```
  Layer 3  │  AI Agent    │  auto · multi · extract
  Layer 2  │  Scenes      │  shopping · local · jobs · academic · video · news · travel · finance · images
  Layer 1  │  Engines     │  google · bing · yahoo · duckduckgo · yandex · youtube · ebay · walmart · yelp
           │              │  + Google: shopping · local · news · scholar · jobs · flights · finance · patents · videos · images · play · lens
```

---

## Layer 1 — Engines

### 9 Engines

| Engine | Strength | Example |
|--------|----------|---------|
| `google` | General + 13 sub-types | `--engine google` |
| `bing` | Web, news | `--engine bing` |
| `yahoo` | Finance | `--engine yahoo` |
| `duckduckgo` | Privacy | `--engine duckduckgo` |
| `yandex` | Russian web | `--engine yandex` |
| `youtube` | Video | `--engine youtube` |
| `ebay` | E-commerce | `--engine ebay` |
| `walmart` | US retail | `--engine walmart` |
| `yelp` | Local reviews | `--engine yelp` |

### 13 Google Sub-Types

Use `--engine google --google-type <type>`:

| Type | What it searches | Type | What it searches |
|------|-----------------|------|-----------------|
| `search` | Web (default) | `shopping` | Products & prices |
| `local` | Google Maps | `news` | Latest headlines |
| `scholar` | Academic papers | `jobs` | Job listings |
| `flights` | Airlines | `finance` | Stocks & markets |
| `videos` | Video content | `images` | Pictures |
| `patents` | IP / patents | `play` | Android apps |
| `lens` | Visual search | | |

```bash
python3 {baseDir}/scripts/novada_search.py --query "MacBook Pro M4" --engine google --google-type shopping
python3 {baseDir}/scripts/novada_search.py --query "transformer attention" --engine google --google-type scholar
python3 {baseDir}/scripts/novada_search.py --query "python developer remote" --engine google --google-type jobs
python3 {baseDir}/scripts/novada_search.py --query "SFO to NRT" --engine google --google-type flights
python3 {baseDir}/scripts/novada_search.py --query "NVIDIA" --engine google --google-type finance
```

---

## Layer 2 — Scenes

Scenes auto-combine the best engines for each use case. Use `--scene <name>`:

| Scene | Engines combined | Use case |
|-------|-----------------|----------|
| 🛒 `shopping` | Google Shopping + eBay + Walmart | Cross-platform price comparison |
| 📍 `local` | Google Local + Yelp | Local business with ratings & maps |
| 💼 `jobs` | Google Jobs | Structured job listings |
| 🎓 `academic` | Google Scholar | Research papers & citations |
| 🎬 `video` | YouTube + Google Videos | Video tutorials & reviews |
| 📰 `news` | Google News + Bing | Multi-source news aggregation |
| ✈️ `travel` | Google Flights | Flight search & pricing |
| 💰 `finance` | Google Finance + Yahoo | Stock data & market info |
| 🖼️ `images` | Google Images | Image search |

```bash
python3 {baseDir}/scripts/novada_search.py --query "MacBook Pro" --scene shopping
python3 {baseDir}/scripts/novada_search.py --query "ramen Tokyo" --scene local
python3 {baseDir}/scripts/novada_search.py --query "react hooks tutorial" --scene video
python3 {baseDir}/scripts/novada_search.py --query "AI startup funding" --scene news
```

### Scene Output Example — Shopping

**Query:** `--query "AirPods Pro" --scene shopping --format agent-json`

```json
{
  "query": "AirPods Pro",
  "scene": "shopping",
  "engines_used": ["google:shopping", "ebay", "walmart"],
  "result_counts": { "shopping": 15, "organic": 6 },
  "shopping_results": [
    { "title": "Apple AirPods Pro 2nd Gen", "price": "$189.99", "seller": "Walmart", "rating": 4.8 },
    { "title": "Apple AirPods Pro 2 - New", "price": "$179.00", "seller": "eBay", "rating": 4.9 },
    { "title": "AirPods Pro (2nd generation)", "price": "$249.00", "seller": "Apple", "rating": 4.7 }
  ]
}
```

---

## Layer 3 — Agent Modes

Use `--mode <auto|multi|extract>`:

### Auto — Smart intent detection

Analyzes your query and auto-selects the best scene:

```bash
python3 {baseDir}/scripts/novada_search.py --query "buy Nike Air Max" --mode auto
#  → detects "shopping" → uses eBay + Walmart + Google Shopping

python3 {baseDir}/scripts/novada_search.py --query "best pizza near me" --mode auto
#  → detects "local" → uses Google Maps + Yelp

python3 {baseDir}/scripts/novada_search.py --query "latest AI news" --mode auto
#  → detects "news" → uses Google News + Bing
```

Intent keywords (EN/DE): buy/kaufen, near me/in der nähe, job/stelle, paper/forschung, video/tutorial, news/nachrichten, flight/flug, stock/aktie, image/bild

### Multi — Parallel engines + dedup

Search multiple engines simultaneously, deduplicate by URL:

```bash
python3 {baseDir}/scripts/novada_search.py --query "web scraping tools" --mode multi --engines google,bing,duckduckgo

# Colon syntax for Google sub-types
python3 {baseDir}/scripts/novada_search.py --query "coffee maker" --mode multi --engines ebay,walmart,google:shopping
```

### Extract — URL content for LLM

Pull clean text from any URL:

```bash
python3 {baseDir}/scripts/novada_search.py --url "https://example.com/article" --mode extract
```

---

## Output Formats

Default is `enhanced` (clickable links). Override with `--format <name>`:

| Format | Output type | Best for |
|--------|------------|----------|
| `enhanced` **(default)** | Markdown + clickable Maps/website links | Daily use |
| `ranked` | Readable markdown with ratings | Quick overview |
| `agent-json` | Structured JSON for AI agents | LLM integration |
| `table` | Side-by-side comparison table | Comparing options |
| `action-links` | Shell `open` commands | Automation |
| `raw` | Full API response | Debugging |

---

## Full Command Reference

```
python3 {baseDir}/scripts/novada_search.py
  --query "search terms"                          # required (unless extract mode)
  --engine google|bing|yahoo|duckduckgo|yandex|youtube|ebay|walmart|yelp
  --google-type search|shopping|local|news|scholar|jobs|flights|finance|videos|images|patents|play|lens
  --scene shopping|local|jobs|academic|video|news|travel|finance|images
  --mode auto|multi|extract
  --engines google,bing,ebay                      # for multi mode (colon syntax: google:shopping)
  --url "https://..."                             # for extract mode
  --format enhanced|ranked|agent-json|table|action-links|raw
  --max-results 1-20                              # default: 10
  --fetch-mode static|dynamic                     # static = fast, dynamic = JS pages
```

**Priority:** `--mode auto` overrides everything. `--scene` overrides `--engine`. Direct `--engine` is the fallback.

---

## vs Tavily

| Feature | Novada Search | Tavily |
|---------|:------------:|:------:|
| Search engines | **9** | 1 |
| Google sub-types | **13** | 0 |
| Vertical scenes | **9** | 0 |
| Shopping (eBay+Walmart+Google) | **Yes** | No |
| Local (Maps+Yelp) | **Yes** | No |
| Video (YouTube) | **Yes** | No |
| Jobs / Academic / Travel | **Yes** | No |
| Multi-engine parallel | **Yes** | No |
| Auto intent detection | **Yes** | No |
| Content extraction | Yes | Yes |
| Agent JSON output | Yes | Yes |

---

**[Get your API key →](https://novada.com)** · [GitHub](https://github.com/NovadaLabs/novada-search) · Powered by Novada Scraper API v2.0
