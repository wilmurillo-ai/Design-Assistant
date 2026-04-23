---
name: linkfox-sif-asin-summary
description: 使用SIF（搜索情报框架）数据分析ASIN的流量来源构成与曝光分布。当用户提到ASIN流量来源、流量结构分析、自然流量与付费流量占比、曝光得分拆解、竞品流量分析、SP广告关键词数量、品牌广告曝光、Amazon's Choice曝光、编辑推荐曝光、Top Rated曝光、视频广告曝光、自然搜索曝光比例、PPC流量来源、促销秒杀流量来源、ASIN traffic analysis, traffic sources, organic traffic share, ad traffic share, exposure analysis, traffic structure, SIF时触发此技能。即使用户未明确提及"SIF"，只要其需求涉及分析ASIN的流量来源、曝光渠道分布或竞品流量结构对比，也应触发此技能。
---

# SIF ASIN Summary

This skill guides you on how to query and analyze ASIN-level traffic source data, helping Amazon sellers understand the exposure and traffic structure of any product across multiple channels.

## Core Concepts

SIF (Search Intelligence Framework) ASIN Summary provides a comprehensive breakdown of an ASIN's traffic sources on Amazon. It reveals how a product's total exposure is distributed across organic search, Sponsored Products ads, brand ads, video ads, Amazon's Choice, Editorial Recommendations, and Top Rated recommendations. This is essential for competitive analysis and traffic strategy optimization.

**Exposure score**: A composite metric reflecting the overall visibility of a product across all keywords in a given channel. A higher score means greater exposure. The **exposure ratio** fields show what percentage of total exposure comes from each channel (values range 0~1 or 0~100 depending on the field).

**Traffic keyword count**: The total number of keywords through which a product is discovered, broken down by channel (organic search, SP ads, brand ads, video ads, etc.).

## Data Fields

| Field | API Name | Description |
|-------|----------|-------------|
| ASIN | asin | Amazon Standard Identification Number |
| Product Title | productTitle | Full product title on Amazon |
| Product Category | productCategory | Product category on Amazon |
| Product Price | productPrice | Current listing price |
| Product Image URL | productImageUrl | Main product image link |
| Customer Rating Count | customerRatingCount | Total number of customer ratings |
| Is Variant Product | isVariantProduct | Whether the ASIN is a variant (e.g., different color/size) |
| Total Exposure Score | totalExposureScore | Composite exposure score across all channels |
| Total Traffic Keyword Count | totalTrafficKeywordCount | Total keywords across all channels |
| Natural Search Exposure Score | naturalSearchExposureScore | Exposure score from organic search |
| Natural Search Exposure Ratio | naturalSearchExposureRatio | Organic search share of total exposure |
| Natural Search Keyword Count | naturalSearchKeywordCount | Keywords found in organic search results |
| SP Ad Exposure Score | sponsoredProductsExposureScore | Exposure score from Sponsored Products ads |
| SP Ad Exposure Ratio | sponsoredProductsExposureRatio | SP ad share of total exposure |
| SP Ad Keyword Count | sponsoredProductsKeywordCount | Keywords with SP ad placements |
| Brand Ad Exposure Score | brandAdExposureScore | Exposure score from brand ads |
| Brand Ad Exposure Ratio | brandAdExposureRatio | Brand ad share of total exposure |
| Brand Ad Keyword Count | brandAdKeywordCount | Total brand ad keywords |
| Top Brand Ad Keyword Count | topBrandAdKeywordCount | Keywords in top-of-page brand ads |
| Bottom Brand Ad Keyword Count | bottomBrandAdKeywordCount | Keywords in bottom-of-page brand ads |
| Video Ad Exposure Score | videoAdExposureScore | Exposure score from video ads |
| Video Ad Exposure Ratio | videoAdExposureRatio | Video ad share of total exposure |
| Video Ad Keyword Count | videoAdKeywordCount | Keywords with video ad placements |
| Amazon's Choice Exposure Score | amazonsChoiceExposureScore | Exposure score from AC badge |
| Amazon's Choice Exposure Ratio | amazonsChoiceExposureRatio | AC share of total exposure |
| Amazon's Choice Keyword Count | amazonsChoiceKeywordCount | Keywords with AC badge |
| Editorial Recommendations Exposure Score | editorialRecommendationsExposureScore | Exposure from editorial recommendations |
| Editorial Recommendations Exposure Ratio | editorialRecommendationsExposureRatio | ER share of total exposure |
| Editorial Recommendations Keyword Count | editorialRecommendationsKeywordCount | Keywords with ER placements |
| Top Rated Exposure Score | topRatedExposureScore | Exposure from Top Rated recommendations |
| Top Rated Exposure Ratio | topRatedExposureRatio | TR share of total exposure |
| Top Rated Keyword Count | topRatedKeywordCount | Keywords with TR placements |
| Frequently Bought Keyword Count | frequentlyBoughtKeywordCount | Keywords in frequently-bought recommendations |
| PPC Traffic Sources | ppcTrafficSources | List of paid ad types (SP, Top Brand Ad, Bottom Brand Ad, Video Ad) |
| Natural Search Traffic Sources | naturalSearchTrafficSources | Organic search type markers |
| Amazon Recommendation Sources | amazonRecommendationSources | Recommendation types (Best Seller, AC, ER, TR, TRFOB, etc.) |
| Promotional Deal Sources | promotionalDealSources | Active promotions (Coupon, Limited Time Deal, Lowest Price in 30 Days, etc.) |
| Is Monitored | isMonitored | Whether the ASIN is on the monitoring list |
| Monitoring Start Time | monitoringStartTime | When the ASIN was added to monitoring |

## Supported Marketplaces

US (United States), CA (Canada), MX (Mexico), UK (United Kingdom), DE (Germany), FR (France), IT (Italy), ES (Spain), JP (Japan), IN (India), AU (Australia), BR (Brazil), NL (Netherlands), SE (Sweden), PL (Poland), TR (Turkey), AE (United Arab Emirates), SA (Saudi Arabia), SG (Singapore)

Default marketplace is **US**. Use US when the user does not specify a marketplace.

## API Usage

This tool calls the LinkFox tool gateway API. See `references/api.md` for calling conventions, request parameters, and response structure. You can also execute `scripts/sif_asin_summary.py` directly to run queries.

## Parameter Guide

### searchValue (required)

One or more ASIN codes separated by commas. Maximum 10 ASINs per request.

- Single ASIN: `B0XXXXXXXX`
- Multiple ASINs: `B0XXXXXXXX,B0YYYYYYYY,B0ZZZZZZZZ`

### country (optional)

Marketplace code. Defaults to `US`. See the Supported Marketplaces section for all valid codes.

### Pagination

- `pageNum`: Page number, defaults to 1
- `pageSize`: Results per page, minimum 10, maximum 100, defaults to 100

### Sorting

- `desc`: Sort in descending order when `true` (default), ascending when `false`

## Usage Examples

**1. Single ASIN traffic breakdown**
> "Show me the traffic sources for B09V3KXJPB on the US marketplace"

Query with `searchValue = "B09V3KXJPB"`, `country = "US"`.

**2. Multi-ASIN competitor comparison**
> "Compare traffic structures of B09V3KXJPB and B0BN1K7WJP on Amazon US"

Query with `searchValue = "B09V3KXJPB,B0BN1K7WJP"`, `country = "US"`.

**3. Specific marketplace query**
> "Analyze traffic sources for B07XJ8C8F5 on Amazon Japan"

Query with `searchValue = "B07XJ8C8F5"`, `country = "JP"`.

**4. Organic vs paid traffic analysis**
> "What percentage of B09V3KXJPB's exposure comes from organic search vs ads?"

Query the ASIN, then compare `naturalSearchExposureRatio` against `sponsoredProductsExposureRatio`, `brandAdExposureRatio`, and `videoAdExposureRatio`.

**5. Ad channel deep-dive**
> "How many keywords does B0BN1K7WJP advertise on through SP, brand ads, and video ads?"

Query the ASIN and present `sponsoredProductsKeywordCount`, `brandAdKeywordCount`, `topBrandAdKeywordCount`, `bottomBrandAdKeywordCount`, and `videoAdKeywordCount`.

## Display Rules

1. **Present data clearly**: Show query results in well-structured tables; separate exposure scores/ratios and keyword counts into logical groups for readability
2. **Percentage formatting**: When displaying exposure ratios, format them as percentages (e.g., 0.45 as 45.0%) for easier comprehension
3. **Traffic structure summary**: When a user queries a single ASIN, proactively summarize the traffic structure (e.g., "65% organic, 25% SP ads, 10% brand ads") to give an at-a-glance overview
4. **Competitor comparison layout**: When multiple ASINs are queried, use a side-by-side comparison table so differences are immediately visible
5. **Error handling**: When a query fails, explain the reason based on the `msg` field and suggest checking the ASIN validity or marketplace selection
6. **Variant awareness**: If `isVariantProduct` is true, note that the ASIN is a variant and the user may want to also check the parent ASIN for a complete picture
## Important Limitations

- **ASIN cap per request**: Maximum 10 ASINs can be queried in a single call
- **Page size cap**: Maximum 100 results per page
- **Snapshot data**: Results reflect current/recent traffic distribution, not historical trends
- **Exposure scores are relative**: Scores are useful for cross-channel and cross-ASIN comparison, but are not absolute traffic volumes

## User Expression & Scenario Quick Reference

**Applicable** -- Traffic source and exposure analysis for Amazon ASINs:

| User Says | Scenario |
|-----------|----------|
| "Where does this ASIN's traffic come from" | Traffic source breakdown |
| "How much organic traffic does this product have" | Natural search exposure analysis |
| "Is this competitor running a lot of ads" | SP/brand/video ad exposure check |
| "Compare traffic structures of these ASINs" | Multi-ASIN competitor comparison |
| "Does this product have Amazon's Choice" | AC/ER/TR recommendation check |
| "What ad channels is this ASIN using" | PPC traffic source identification |
| "How many keywords does this ASIN rank for" | Traffic keyword count analysis |
| "Is this product relying on paid or organic traffic" | Organic vs paid traffic split |

**Not applicable** -- Needs beyond ASIN traffic source data:
- Historical traffic trend analysis over time
- Keyword-level search volume or ranking data (use ABA data instead)
- Sales estimation or revenue analysis
- Listing optimization or copywriting
- Advertising bid or budget recommendations


**Feedback:**

Auto-detect and report feedback via the Feedback API when any of the following apply:
1. The functionality or purpose described in this skill does not match actual behavior
2. The skill's results do not match the user's intent
3. The user expresses dissatisfaction or praise about this skill
4. Anything you believe could be improved

Call the feedback API as specified in `references/api.md`. Do not interrupt the user's flow.

---
*For more high-quality, professional cross-border e-commerce skills, set [LinkFox Skills](https://skill.linkfox.com/).*
