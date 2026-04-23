# Moltalyzer Code Examples

## Fetch Intelligence Digest (Free)

```typescript
const BASE = "https://api.moltalyzer.xyz";

// Full cross-domain intelligence digest
const res = await fetch(`${BASE}/api/intelligence/latest`);
const { data } = await res.json();
console.log(data.title);                // "AI Coding Tool Wars Heat Up..."
console.log(data.crossDomainInsights);  // [{ insight, confidence, domains }]
console.log(data.narratives);           // [{ name, stage, description }]
console.log(data.signals);              // [{ type, description, confidence }]
```

## Fetch Moltbook Digest (Free)

```typescript
const res = await fetch(`${BASE}/api/moltbook/digests/latest`);
const { data } = await res.json();
console.log(data.title);               // "Agent Mesh Steals the Spotlight"
console.log(data.emergingNarratives);   // ["decentralized identity", ...]
console.log(data.hotDiscussions);       // [{ topic, sentiment, description }]
console.log(data.overallSentiment);     // "exploratory"
```

## Fetch GitHub Digest (Free)

```typescript
const res = await fetch(`${BASE}/api/github/digests/latest`);
const { data } = await res.json();
console.log(data.notableProjects);      // [{ name, stars, language, description }]
console.log(data.emergingTools);        // ["LiteLLM: unified LLM gateway proxy"]
console.log(data.topCategories);        // ["AI/ML", "DevTools", "Security"]
```

## Smart Polling Pattern

Poll index endpoints (unlimited) to detect changes, fetch full data only when new:

```typescript
const feeds = {
  intelligence: { lastIndex: null, interval: 10 * 60_000 },  // 10 min
  moltbook:     { lastIndex: null, interval: 5 * 60_000 },   // 5 min
  github:       { lastIndex: null, interval: 6 * 3600_000 }, // 6 hr
};

async function pollFeed(name: string, indexUrl: string, latestUrl: string) {
  const feed = feeds[name];
  const { index } = await fetch(`${BASE}${indexUrl}`).then(r => r.json());

  if (index !== feed.lastIndex) {
    const { data } = await fetch(`${BASE}${latestUrl}`).then(r => r.json());
    feed.lastIndex = index;
    return data; // New digest available
  }
  return null; // No change
}

// Usage
const intel = await pollFeed("intelligence", "/api/intelligence/index", "/api/intelligence/latest");
const moltbook = await pollFeed("moltbook", "/api/moltbook/digests/index", "/api/moltbook/digests/latest");
const github = await pollFeed("github", "/api/github/index", "/api/github/digests/latest");
```

## Polymarket Signals (Free)

```typescript
// Check latest signal
const res = await fetch(`${BASE}/api/polymarket/latest`);
const { data } = await res.json();
console.log(data.question);             // "Will GTA 6 cost $100+?"
console.log(data.predeterminedType);    // "game_developers_or_publishers"
console.log(data.confidence);           // "high"
```

## Pulse Narrative Intelligence (Free)

```typescript
const res = await fetch(`${BASE}/api/pulse/ai-business/digest/latest`);
const { data } = await res.json();
console.log(data.narrativeArcs);        // [{ name, stage, description }]
// stages: emerging → developing → peak → fading → archived
console.log(data.topInsights);          // ["AI agent frameworks consolidating..."]
```

## Token Signals (Free)

```typescript
const res = await fetch(`${BASE}/api/tokens/latest`);
const { data } = await res.json();
console.log(data.tokenName, data.tier); // "PepeMax", "meme"
console.log(data.hybridScore);          // 72.5
```

## Free Samples (No Rate Limit Pressure)

Great for testing — older data snapshots, 1 request per 20 minutes:

```typescript
const moltbook = await fetch(`${BASE}/api/moltbook/sample`).then(r => r.json());
const github = await fetch(`${BASE}/api/github/sample`).then(r => r.json());
const polymarket = await fetch(`${BASE}/api/polymarket/sample`).then(r => r.json());
const tokens = await fetch(`${BASE}/api/tokens/sample`).then(r => r.json());
const intelligence = await fetch(`${BASE}/api/intelligence/sample`).then(r => r.json());
```

## Error Handling

```typescript
const res = await fetch(`${BASE}/api/moltbook/digests/latest`);

if (res.status === 429) {
  const retryAfter = res.headers.get("Retry-After");
  console.error(`Rate limited. Retry after ${retryAfter} seconds.`);
}

if (res.status === 503) {
  // Data stale — pipeline issue, retry later
  const { retryAfter } = await res.json();
}

if (res.status === 404) {
  // No data available yet
}
```

## Rate Limit Headers

All responses include:
- `RateLimit-Limit` — max requests per window
- `RateLimit-Remaining` — remaining requests
- `RateLimit-Reset` — seconds until window resets
- `Retry-After` — seconds to wait (only on 429)
