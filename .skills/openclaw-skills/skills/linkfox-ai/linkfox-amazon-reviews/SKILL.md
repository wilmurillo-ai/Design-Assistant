---
name: linkfox-amazon-reviews
description: 按ASIN获取并分析亚马逊商品评论，支持14个站点按星级筛选评论。当用户提到亚马逊评论、商品评价、买家投诉、差评、好评、星级评分、评论分析、评论情感、产品改良建议、Vine评论、已验证购买评论、竞品评论研究、Amazon reviews, product feedback, negative review analysis, positive review analysis, star rating filter, review sentiment analysis, product improvement insights, Vine reviews, competitor reviews, customer feedback时触发此技能。即使用户未明确说"评论"，只要其需求涉及读取、筛选或分析亚马逊商品的买家评论，也应触发此技能。
---

# Amazon Product Reviews List

This skill guides you on how to fetch and analyze Amazon product reviews, helping Amazon sellers extract actionable insights from customer feedback.

## Core Concepts

This tool retrieves real customer reviews for a given Amazon product (ASIN). You can control how many reviews to fetch per star rating (1-5 stars, up to 100 each), filter by keyword, sort by recency or helpfulness, and restrict to verified purchases or media-containing reviews. Only one ASIN per request is supported; for multiple ASINs, make separate calls.

## Parameter Guide

| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| asin | string | Yes | The Amazon product ASIN to look up | - |
| domainCode | string | No | Amazon marketplace domain code (see Supported Marketplaces) | `ca` |
| star1Num | integer | No | Number of 1-star reviews to fetch (0-100) | 10 |
| star2Num | integer | No | Number of 2-star reviews to fetch (0-100) | 10 |
| star3Num | integer | No | Number of 3-star reviews to fetch (0-100) | 10 |
| star4Num | integer | No | Number of 4-star reviews to fetch (0-100) | 10 |
| star5Num | integer | No | Number of 5-star reviews to fetch (0-100) | 10 |
| filterByKeyword | string | No | Filter reviews containing this keyword | - |
| sortBy | string | No | Sort order: `recent` (newest first) or `helpful` (most helpful first) | `recent` |
| reviewerType | string | No | Reviewer filter: `all_reviews` or `avp_only_reviews` (verified purchases only) | `all_reviews` |
| mediaType | string | No | Media filter: `all_contents` or `media_reviews_only` (reviews with images/videos) | `all_contents` |
| formatType | string | No | Format filter: `current_format` or `all_formats` | `current_format` |

## Supported Marketplaces

| Marketplace | domainCode |
|-------------|------------|
| Canada | `ca` |
| United Kingdom | `co.uk` |
| India | `in` |
| Germany | `de` |
| France | `fr` |
| Italy | `it` |
| Spain | `es` |
| Japan | `co.jp` |
| Australia | `com.au` |
| Brazil | `com.br` |
| Netherlands | `nl` |
| Sweden | `se` |
| Mexico | `com.mx` |
| United Arab Emirates | `ae` |

Default marketplace is **Canada (ca)**. Always confirm the user's intended marketplace and set `domainCode` accordingly.

## API Usage

This tool calls the LinkFox tool gateway API. See `references/api.md` for calling conventions, request parameters, and response structure. You can also execute `scripts/amazon_reviews.py` directly to run queries.

## Usage Examples

**1. Fetch recent negative reviews (1-2 star) for a US product**
```json
{
  "asin": "B08N5WRWNW",
  "domainCode": "co.uk",
  "star1Num": 50,
  "star2Num": 50,
  "star3Num": 0,
  "star4Num": 0,
  "star5Num": 0,
  "sortBy": "recent"
}
```

**2. Get only verified purchase reviews filtered by keyword**
```json
{
  "asin": "B08N5WRWNW",
  "domainCode": "de",
  "filterByKeyword": "quality",
  "reviewerType": "avp_only_reviews"
}
```

**3. Fetch the most helpful 5-star reviews with media**
```json
{
  "asin": "B08N5WRWNW",
  "domainCode": "ca",
  "star1Num": 0,
  "star2Num": 0,
  "star3Num": 0,
  "star4Num": 0,
  "star5Num": 100,
  "sortBy": "helpful",
  "mediaType": "media_reviews_only"
}
```

**4. Balanced review snapshot across all star ratings**
```json
{
  "asin": "B08N5WRWNW",
  "domainCode": "co.jp",
  "star1Num": 20,
  "star2Num": 20,
  "star3Num": 20,
  "star4Num": 20,
  "star5Num": 20
}
```

## Display Rules

1. **Present data clearly**: Show reviews in well-organized tables or grouped by star rating. Include key fields: rating, title, text, date, verified status, and helpful count.
2. **Summarize when appropriate**: When many reviews are returned, provide a summary of common themes and pain points before listing individual reviews.
3. **Highlight actionable insights**: When showing negative reviews, call out recurring complaints. When showing positive reviews, note frequently praised features.
4. **Vine and verified labels**: Clearly indicate whether a review is a Vine Voice review or a verified purchase.
5. **Media indicators**: Note when reviews include images or videos, as these often carry more weight.
6. **Error handling**: When a query fails, explain the reason based on the `statusMessage` field and suggest adjusting parameters (e.g., check ASIN validity, marketplace availability).
7. **Single ASIN limitation**: If the user asks about multiple ASINs, inform them that the tool supports one ASIN per call and make separate requests for each.
## Important Limitations

- **One ASIN per request**: Only a single ASIN can be queried at a time. For multiple ASINs, make separate calls.
- **Per-star cap**: Each star rating can return a maximum of 100 reviews per request.
- **No historical snapshots**: Reviews are fetched in real-time; there is no historical review archive.
- **Review text language**: Reviews are returned in their original language as posted on the marketplace.

## User Expression & Scenario Quick Reference

**Applicable** -- Tasks involving Amazon product reviews:

| User Says | Scenario |
|-----------|----------|
| "Show me the reviews for ASIN B08N5WRWNW" | Direct review lookup |
| "What are customers complaining about" | Negative review analysis |
| "Get me all the 1-star reviews" | Star-filtered retrieval |
| "Any common issues in the bad reviews" | Pain point mining |
| "What do people like about this product" | Positive review analysis |
| "Find reviews mentioning 'battery'" | Keyword-filtered reviews |
| "Show me reviews with photos" | Media-filtered reviews |
| "Verified purchase reviews only" | Reviewer-type filtering |
| "Help me analyze competitor reviews" | Competitor review research |
| "Product improvement suggestions from reviews" | Actionable insight extraction |

**Not applicable** -- Needs beyond product review data:

- ABA search term data / keyword research (use ABA Data Explorer instead)
- Sales estimation or revenue analysis
- Listing copywriting or A+ content creation
- Advertising / PPC strategy
- Pricing strategy or profit margin calculations
- Review manipulation or fake review detection services

**Boundary judgment**: When users say "product research" or "competitor analysis," if it boils down to reading and analyzing customer reviews for specific ASINs, this skill applies. If they are asking about search volume, keyword rankings, sales estimates, or comprehensive market sizing, it does not apply.


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
