# Trustpilot Review Scraper

Extract Trustpilot reviews, ratings, business profiles, and competitor data at scale. Four scraping modes in one actor: bulk review collection, business search, profile extraction, and category browsing.

**Works without a proxy.** No Cloudflare blocking on Trustpilot — this actor uses direct HTTP with browser-fingerprint spoofing, making it fast and reliable.

---

## What you can do

- **Collect all reviews for any business** — paginated, up to thousands of reviews
- **Search businesses by keyword** — find competitors, suppliers, or services on Trustpilot
- **Extract full business profiles** — TrustScore, review count, category, response rates
- **Browse businesses in a category** — e-commerce, SaaS, finance, travel, etc.

---

## Use cases

### Competitor analysis
Pull all reviews for your top 5 competitors. Find what customers love or hate. Feed it into ChatGPT or Claude to generate product improvement reports.

```json
{ "mode": "business_reviews", "businessUrl": "competitor.com", "maxReviews": 500 }
```

### Brand monitoring
Track your own Trustpilot reviews daily. Alert on new 1-star reviews. Monitor review volume trends over time.

```json
{ "mode": "business_reviews", "businessUrl": "yourcompany.com", "maxReviews": 50 }
```

### Market research
Find all SaaS tools in a category with their ratings and review counts. Rank them by TrustScore to identify market leaders and gaps.

```json
{ "mode": "category_browse", "category": "software", "maxResults": 100 }
```

### Lead generation
Search Trustpilot for businesses in your target vertical. Get company names, domains, and contact signals. Export directly to Google Sheets or Airtable via Apify integrations.

```json
{ "mode": "business_search", "searchTerm": "cloud hosting", "maxResults": 50 }
```

### Sentiment analysis pipeline
Scrape → push to dataset → connect to Make.com or n8n → run through LLM → generate weekly sentiment report. Full automation with no code beyond the input config.

---

## Input

| Field | Type | Description | Default |
|-------|------|-------------|---------|
| `mode` | string | Scraping mode (see below) | `business_reviews` |
| `businessUrl` | string | Business domain or Trustpilot slug (e.g. `apple.com`, `amazon.com`) | `apify.com` |
| `searchTerm` | string | Keyword for `business_search` mode | — |
| `category` | string | Category slug for `category_browse` mode (e.g. `software`, `ecommerce`) | — |
| `maxReviews` | integer | Max reviews to collect in `business_reviews` mode | `100` |
| `maxResults` | integer | Max items for `business_search` and `category_browse` modes | `20` |

### Modes

**`business_reviews`** — Collect paginated reviews for a specific business. Returns reviewer name, rating (1–5), title, body, date, and verified purchase flag.

**`business_search`** — Find businesses on Trustpilot by keyword. Returns business name, domain, TrustScore, review count, and category.

**`business_profile`** — Get the full profile of a specific business: TrustScore, rating breakdown (1–5 star distribution), total reviews, categories, and response rate.

**`category_browse`** — List businesses in a Trustpilot category sorted by rating or review count. Useful for building prospect lists or market maps.

---

## Output

### `business_reviews` output
```json
{
  "source": "trustpilot-review-scraper",
  "mode": "business_reviews",
  "totalRecords": 150,
  "business": "Apple",
  "slug": "apple.com",
  "overallRating": 1.5,
  "reviews": [
    {
      "rating": 5,
      "title": "Best laptop I've ever owned",
      "text": "Switched from Windows three years ago and never looked back...",
      "date": "2024-11-20T00:00:00.000Z",
      "author": "Sarah M.",
      "verified": true
    }
  ]
}
```

### `business_profile` output
```json
{
  "business": "Shopify",
  "slug": "shopify.com",
  "trustScore": 2.7,
  "totalReviews": 8420,
  "ratingBreakdown": { "5": 34, "4": 8, "3": 5, "2": 4, "1": 49 },
  "categories": ["E-commerce Platform"]
}
```

---

## Performance

- **Speed**: 25 reviews in ~2 seconds (no Playwright, pure HTTP)
- **Reliability**: Three-layer extraction — `__NEXT_DATA__` JSON → JSON-LD → HTML fallback
- **Pagination**: Automatic — scrapes all pages up to `maxReviews`
- **No bot detection**: Trustpilot does not block standard HTTP with proper headers

---

## Pricing

This actor uses **Pay Per Event** pricing: **$0.05 per successful run**.

One run = one complete scraping job (regardless of how many reviews you collect). Scraping 500 reviews costs the same as scraping 10.

---

## Integrations

Connect this actor to your existing stack with zero code:

- **Google Sheets** — Export reviews directly to a spreadsheet via Apify's Google Sheets integration
- **Make.com / n8n** — Trigger on new reviews, route data to Slack, Notion, Airtable
- **OpenAI / Claude API** — Feed reviews into an LLM for sentiment analysis or summary generation
- **Webhooks** — POST results to any endpoint when the actor finishes

---

## FAQ

**Does this require a proxy?**
No. Trustpilot is accessible without proxies. The actor works out of the box.

**How many reviews can I collect?**
There is no hard cap. Set `maxReviews` to any number. The actor will paginate automatically until it hits your limit or runs out of reviews.

**Can I scrape multiple businesses in one run?**
Currently one business per run. To scrape multiple, use Apify's scheduler or connect multiple tasks in a pipeline.

**How fresh is the data?**
Live — every run fetches directly from Trustpilot at the time of execution.

**What if a business has no reviews?**
The actor returns an empty reviews array with the business profile metadata.

---

## Related actors

Looking for more review data sources?

- [G2 Review Scraper](https://apify.com/ntriqpro/g2-review-scraper) — Software reviews from G2
- [Capterra Review Scraper](https://apify.com/ntriqpro/capterra-review-scraper) — Software reviews from Capterra
