# SentiSense API - Skill File for AI Agents

> **SentiSense** gives you institutional-grade market intelligence that competitors charge $70–200/month for — SEC Form 4 insider trading, 13F institutional flows, cluster buy signals, stock sentiment, news analysis, and AI-powered reports — starting **free**.

**Base URL:** `https://app.sentisense.ai`
**Website:** https://sentisense.ai
**API Docs:** https://sentisense.ai/docs/api/
**Authentication:** API key via `X-SentiSense-API-Key` header. Generate keys at Settings > Developer Console.
**SDKs:** Python (`pip install sentisense`), Node.js (`npm install sentisense`)

---

## Authentication

```bash
# Include API key in header
curl -H "X-SentiSense-API-Key: ss_live_YOUR_KEY" \
  "https://app.sentisense.ai/api/v1/..."
```

```python
from sentisense import SentiSenseClient
client = SentiSenseClient(api_key="ss_live_YOUR_KEY")
```

All API endpoints require an API key. Generate one for free at Settings > Developer Console.

### Access Tiers

| Badge | Meaning |
|-------|---------|
| **Public** | Available on all tiers (Free and PRO) |
| **Public (preview)** | Free gets limited preview; PRO gets full data |
| **Quota-gated** | Consumes monthly quota (Free: limited, PRO: unlimited) |
| **PRO only** | Requires PRO subscription |

### Rate Limits

| Tier | Requests/Month | Rate |
|------|----------------|------|
| Free | 1,000 | 15 requests/minute |
| PRO ($15/mo) | 100,000 | 120 requests/minute |

---

## Stocks API (`/api/v1/stocks`)

### GET /api/v1/stocks/price
Real-time stock price. **Public.**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ticker` | string | Yes | Stock ticker (e.g., `AAPL`) |

```bash
curl -H "X-SentiSense-API-Key: ss_live_YOUR_KEY" \
  "https://app.sentisense.ai/api/v1/stocks/price?ticker=AAPL"
```

Response: `{ ticker, currentPrice, change, changePercent, previousClose, volume, timestamp }`

### GET /api/v1/stocks/prices
Batch real-time prices. **Public.**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `tickers` | string | Yes | Comma-separated (e.g., `AAPL,TSLA,NVDA`) |

### GET /api/v1/stocks/chart
Historical OHLCV chart data. **Public.**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `ticker` | string | Yes | Stock ticker |
| `timeframe` | string | No | `1M`, `3M`, `6M`, `1Y` (default: `1M`) |
| `range` | string | No | Alias: `5d`, `1mo`, `3mo`, `6mo`, `1y` (alternative to `timeframe`) |

### GET /api/v1/stocks
List all tracked ticker symbols. **Public.**

### GET /api/v1/stocks/detailed
All stocks with company name, KB entity ID, and URL slug. **Public.**

### GET /api/v1/stocks/popular
Popular stock tickers. **Public.**

### GET /api/v1/stocks/images
Company logo URLs. **Public.**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `tickers` | string | Yes | Comma-separated tickers (max 600) |

### GET /api/v1/stocks/descriptions
Company profiles with branding, sector, market cap. **Public.**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `tickers` | string | Yes | Comma-separated tickers |

### GET /api/v1/stocks/{ticker}/profile
Company profile (CEO, sector, industry). **Public.**

### GET /api/v1/stocks/{ticker}/similar
Peer/similar stocks. **Public.**

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `limit` | int | No | 5 | Max results |

### GET /api/v1/stocks/{ticker}/entities
Related knowledge base entities (CEO, products, partners). **Public.**

### GET /api/v1/stocks/{ticker}/ai-summary
AI-generated stock analysis report. **PRO only.**

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `depth` | string | No | `basic` | `basic` or `deep` |
| `forceRefresh` | boolean | No | false | Generate fresh report |

### GET /api/v1/stocks/{ticker}/metrics/{metricType}/breakdown
Sentiment or mention metrics breakdown by sub-entities. **Public.**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `metricType` | path | Yes | `sentiment` or `mentions` |
| `startTime` | long | Yes | Start time in epoch ms |
| `endTime` | long | Yes | End time in epoch ms |

### GET /api/v1/stocks/market-status
Current market open/closed status. **API key required.**

### GET /api/v1/stocks/fundamentals
Financial statement data. **Public.**

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `ticker` | string | Yes | - | Stock ticker |
| `timeframe` | string | No | `quarterly` | `quarterly` or `annual` |
| `fiscalPeriod` | string | No | - | e.g., `Q4` |
| `fiscalYear` | int | No | - | e.g., `2024` |

### GET /api/v1/stocks/fundamentals/current
Most recent fundamental data snapshot. **Public.**

### GET /api/v1/stocks/fundamentals/periods
Available fiscal periods. **Public.**

### GET /api/v1/stocks/fundamentals/historical/ratios
Historical P/E and financial ratios. **Public.** Note: data availability depends on upstream provider; may return 404 for some tickers.

### GET /api/v1/stocks/fundamentals/historical/revenue
Historical revenue data. **Public.**

### GET /api/v1/stocks/short-interest
Short interest data from FINRA. **Public.**

### GET /api/v1/stocks/float
Float information (shares outstanding, public float). **Public.**

### GET /api/v1/stocks/short-volume
Short volume trading data. **Public.**

---

## Metrics API (`/api/v2/metrics`)

Time series metrics for stocks and entities — mentions, sentiment, social dominance, and more. Computed from serving data with proper entity resolution (tickers are resolved to KB entities automatically).

### GET /api/v2/metrics/entity/{entityId}/metric/{metricType}
Time series metric data for a stock or entity. `mentions` and `social_dominance` are **Public**; `sentiment` and `sentisense` are **PRO only**.

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `entityId` | path | Yes | - | Stock ticker (e.g., `AAPL`) or KB entity ID |
| `metricType` | path | Yes | - | `mentions`, `sentiment`, `sentisense`, `social_dominance` |
| `startTime` | long | No | 7 days ago | Epoch milliseconds |
| `endTime` | long | No | now | Epoch milliseconds |
| `maxDataPoints` | int | No | - | Downsample to N data points |

### GET /api/v2/metrics/entity/{entityId}/distribution/{metricType}
Distribution of a metric across a dimension (e.g., mentions by source). **Public** (same quota rules as above).

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `entityId` | path | Yes | - | Stock ticker or KB entity ID |
| `metricType` | path | Yes | - | Metric type key |
| `dimension` | string | Yes | - | Dimension to slice by (e.g., `source`) |
| `startTime` | long | No | 7 days ago | Epoch milliseconds |
| `endTime` | long | No | now | Epoch milliseconds |

### GET /api/v2/metrics/entity/{entityId}/metric/{metricType}/slices
Available slice dimensions for a metric. **Public.**

### GET /api/v2/metrics/entity/{entityId}/baselines/{metricType}
Historical and peer baselines for a metric. **Public.**

---

## Documents & News API (`/api/v1/documents`)

> **Note:** Document responses include a `url` field but **no headline or title text**. The API provides derived analytics (sentiment, entities, reliability) — not source content. The `sourceName` field identifies the publisher. If your application needs to display titles, the `url` field links to the original source. Any content retrieval from source URLs is your application's independent action, subject to the source platform's terms. See our [API Terms of Service](https://sentisense.ai/agreement/API-Terms-of-Service.pdf).

### GET /api/v1/documents/ticker/{ticker}
News and social posts for a stock with sentiment scores. **Public.**

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `source` | string | No | all | `NEWS`, `REDDIT`, `X`, `SUBSTACK` |
| `days` | int | No | 7 | Lookback in days (1-365) |
| `hours` | int | No | - | Lookback in hours (overrides days) |
| `limit` | int | No | 200 | Max results (capped at 200) |

Response: `{ documents: [...], totalCount, searchTicker, source, startDate, endDate }`. Each document includes: `id`, `url`, `source`, `sourceName`, `published`, `averageSentiment`, `reliability`, `sentiment[]`. Per-entity sentiment classifies each mentioned entity as POSITIVE/NEGATIVE/NEUTRAL.

### GET /api/v1/documents/ticker/{ticker}/range
Documents within a date range. **Public.**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `startDate` | ISO date | Yes | e.g., `2025-01-01` |
| `endDate` | ISO date | Yes | e.g., `2025-01-31` |
| `source` | string | No | Filter by source |
| `limit` | int | No | Max results (capped at 200) |

### GET /api/v1/documents/entity/{entityId}
Documents mentioning a knowledge base entity. **Public.** Use URL-safe format: `kb-person-67` instead of `kb/person/67`.

### GET /api/v1/documents/search
Smart search with natural language queries. **Public.**

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `query` | string | Yes | - | e.g., `AAPL earnings`, `Elon Musk TSLA` |
| `source` | string | No | all | Filter by source |
| `days` | int | No | 7 | Lookback in days |
| `limit` | int | No | 200 | Max results (capped at 500) |

### GET /api/v1/documents/source/{source}
Latest documents from a specific source. **Public.**

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `source` | path | Yes | `NEWS`, `REDDIT`, `X`, `SUBSTACK` |
| `days` | int | No | Lookback in days |
| `limit` | int | No | Max results (capped at 500) |

### GET /api/v1/documents/stories
AI-curated news story clusters. **Public.**

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `limit` | int | No | 20 | Max stories (capped at 50) |
| `days` | int | No | 7 | Lookback in days (max 15) |
| `offset` | int | No | 0 | Pagination offset |

Response: Story objects with `cluster.title`, `cluster.averageSentiment`, `displayTickers`, `impactScore` (0-10), `brokeAt`.

### GET /api/v1/documents/stories/ticker/{ticker}
News stories for a specific stock. **Public.**

---

## Institutional Flows API (`/api/v1/institutional`)

Data from SEC 13F-HR filings. Filer categories: `INDEX_FUND`, `HEDGE_FUND`, `ACTIVIST`, `PENSION`, `BANK`, `INSURANCE`, `MUTUAL_FUND`, `SOVEREIGN_WEALTH`, `ENDOWMENT`, `OTHER`.

**Important:** All institutional endpoints (except `/quarters`) require a `reportDate` parameter. **Always call `GET /quarters` first** to get valid dates — do not hardcode them. Use the `reportDate` from the first (most recent) quarter in subsequent calls.

### GET /api/v1/institutional/quarters
Available 13F reporting quarters. **Public.** Call this first.

Response: array of `{ value, label, reportDate }` objects sorted newest-first. Use the `reportDate` field (e.g., `"2025-12-31"`) when calling other institutional endpoints.

### GET /api/v1/institutional/flows
Aggregate institutional buying/selling per ticker. **Public (preview)** -- Free: top 5, PRO: full data.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `reportDate` | ISO date | Yes | The `reportDate` from `/quarters` (e.g., `2025-12-31`) |
| `limit` | int | No | Max results per direction (default: 50, max: 100) |

Response: `{ isPreview, previewReason, data: { inflows: [...], outflows: [...] } }`. Each flow includes net share changes, new/closed positions, and per-category breakdowns (indexFundNetChange, hedgeFundNetChange, etc.).

### GET /api/v1/institutional/holders/{ticker}
Institutional holders for a stock. **Public (preview)** -- Free: top 5, PRO: full data.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `reportDate` | ISO date | Yes | Quarter end date |

Response includes filer name, category, shares, value, change type (NEW/INCREASED/DECREASED/SOLD_OUT/UNCHANGED).

### GET /api/v1/institutional/activist
Activist investor positions (NEW or INCREASED stakes). **Public (preview)** -- Free: top 3, PRO: full data.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `reportDate` | ISO date | Yes | Quarter end date |

### GET /api/v1/institutional/bonds
Convertible bond flows grouped by base ticker. **Public (preview)** -- Free: top 3, PRO: full data.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `reportDate` | ISO date | Yes | Quarter end date |

### GET /api/v1/institutional/options
Institutional options activity with call/put breakdown. **Public (preview)** -- Free: top 3, PRO: full data.

| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `reportDate` | ISO date | Yes | Quarter end date |

---

## Insider Trading API (`/api/v1/insider`)

SEC Form 4 insider trading data — track buys, sells, awards, and exercises by company officers, directors, and 10%+ shareholders. Updated daily. Includes cluster buy detection (a historically bullish signal).

**Insider relationships:** `OFFICER`, `DIRECTOR`, `TEN_PCT_OWNER`, `OTHER`. Each filer also has independent `officer`, `director`, `tenPctOwner` booleans (a person can be both officer and director).

**Transaction types:** `BUY`, `SELL`, `EXERCISE`, `AWARD`, `GIFT`, `OTHER`.

### GET /api/v1/insider/activity
Market-wide insider buying and selling aggregated by ticker. **Public (preview)** -- Free: top 5, PRO: full data.

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `lookbackDays` | int | No | 90 | Days to look back (1-365) |

Response: `{ buys: [...], sells: [...] }`. Each entry: `ticker`, `companyName`, `tradeCount`, `insiderCount`, `totalShares`, `totalValue`, `latestDate`, `latestInsider`, `latestTitle`.

### GET /api/v1/insider/trades/{ticker}
Insider transactions for a specific stock, newest first. **Public (preview)** -- Free: top 5, PRO: full data.

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `ticker` | path | Yes | - | Stock ticker (e.g., `AAPL`) |
| `lookbackDays` | int | No | 90 | Days to look back (1-365) |

Response: array of trade objects with `insiderName`, `insiderTitle`, `insiderRelation`, `officer`, `director`, `tenPctOwner`, `transactionDate`, `filedDate`, `transactionCode`, `transactionType`, `securityTitle`, `sharesTransacted`, `pricePerShare`, `totalValue`, `sharesOwnedAfter`, `directOwnership`, `rule10b51`.

```python
client = SentiSenseClient(api_key="ss_live_YOUR_KEY")
trades = client.get_insider_trades("AAPL", lookback_days=90)
for t in trades:
    print(f"{t['transactionDate']} {t['insiderName']} {t['transactionType']} {t['sharesTransacted']} shares")
```

### GET /api/v1/insider/cluster-buys
Cluster buy signals — stocks where 3+ distinct insiders purchased recently. **Public (preview)** -- Free: top 3, PRO: full data.

| Param | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `lookbackDays` | int | No | 90 | Days to look back (1-365) |

Response: array of `{ ticker, companyName, insiderCount, tradeCount, totalShares, totalValue, firstBuyDate, lastBuyDate }`.

---

## Market Summary API (`/api/v1/market-summary`)

AI-generated market overview with headline analysis and top active stocks.

### GET /api/v1/market-summary
AI market summary with headline, markdown analysis, and mention data. **Public.** No parameters required.

Response:

| Field | Type | Description |
|-------|------|-------------|
| `totalMentions` | long | Total mentions across all tracked stocks |
| `topActiveStocks` | string[] | Most active tickers by mention volume |
| `lastUpdated` | long | Epoch milliseconds when data was last updated |
| `headline` | string? | 1-2 sentence market punchline |
| `expandedContent` | string? | Full markdown analysis |
| `generatedAt` | long? | Epoch seconds when AI summary was generated |

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 400 | Bad request (missing/invalid parameters) |
| 401 | Unauthorized (invalid or missing API key) |
| 403 | Forbidden (insufficient tier) |
| 404 | Resource not found |
| 429 | Rate limit or quota exceeded |
| 500 | Internal server error |

---

## Getting Started

1. **Sign up** at [app.sentisense.ai](https://app.sentisense.ai) and generate a free API key in Settings > Developer Console
2. **Start calling** -- stock prices, charts, news sentiment, fundamentals (1,000 requests/month on Free)
3. **Upgrade to PRO** ($15/mo) -- full institutional flows, AI reports, unlimited story views, 100K requests/month

### Python SDK

```python
pip install sentisense
```

```python
from sentisense import SentiSenseClient

# Generate a free key at Settings > Developer Console
client = SentiSenseClient(api_key="ss_live_YOUR_KEY")
price = client.get_stock_price("AAPL")

# Same key works for PRO endpoints if subscribed
flows = client.get_institutional_flows("2025-12-31")
```

### Node.js SDK

```bash
npm install sentisense
```

```javascript
import SentiSense from 'sentisense';

const client = new SentiSense({ apiKey: 'ss_live_YOUR_KEY' });
const price = await client.getStockPrice('AAPL');
```

---

> **Note:** This skill file is updated frequently as new features ship. For the latest version, check [sentisense.ai/skill.md](https://sentisense.ai/skill.md).

*SentiSense is a product of Compass AI Data Services, LLC. This data is for informational purposes only -- not investment advice.*
