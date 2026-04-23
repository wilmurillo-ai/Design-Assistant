# Google Ads — Skill Manual
## Built from Social Media Agent Master Playbook (March 2026)

> Full Google Ads playbook for 2026. Google Ads has evolved from keyword bidding into an AI-driven ecosystem. Success requires giving the AI the right signals, maintaining control over key levers, and creating a continuous learning loop.

---

## Campaign Types Overview

| Type | Use Case | 2026 Priority |
|------|----------|--------------|
| **Search** | Text ads on Google Search results. Highest intent. | High |
| **Performance Max (PMax)** | AI-driven, cross-channel (Search, YouTube, Display, Discover, Gmail, Maps) | Dominant |
| **Shopping** | Product-specific ads with images and prices | High (e-commerce) |
| **Display** | Visual ads across Google's Display Network | Medium |
| **Video** | YouTube ads | Medium |
| **Demand Gen** | Discovery and social-format ads across Google surfaces | Medium |

---

## Search Campaign Strategy

### Keyword Strategy (2026 Standard)
- **Broad match + Smart Bidding**: Google identifies search intent, not just exact phrases. This is the current standard.
- **Map search intent to readiness to act**: High-intent terms get aggressive bids; informational terms get capped budgets
- **Negative keywords**: Regularly audit search terms report and exclude irrelevant queries
- **Separate brand vs non-brand**: ALWAYS. Different CPC, different bidding, different purpose.

### Match Type Guidance
- Broad Match: Works best with Smart Bidding — gives Google room to find intent
- Phrase Match: Good for controlling relevance while allowing variation
- Exact Match: Use sparingly for highest-intent, specific queries you must control
- Negative Match: Essential — prevents waste on irrelevant queries

### Ad Copy Best Practices
- Use **Responsive Search Ads (RSAs)** with 8-10 unique headlines and 4 description lines
- Pin headlines sparingly — preserve algorithmic optimization flexibility
- Include primary keyword in Headline 1
- Use specific numbers and data: "Save 30%" beats "Save Money"
- Include clear CTAs
- Use ad extensions aggressively:
  - Sitelinks (show additional pages)
  - Callouts (highlight features)
  - Structured snippets (list products/services)
  - Call extensions (show phone number)
  - Location extensions (critical for any local service business)

### Quality Score Optimization
Quality Score determines ad rank and CPC. Optimize all three components:
- **Expected CTR**: Write compelling, relevant ad copy
- **Ad Relevance**: Tight keyword-to-ad alignment (ad speaks directly to what was searched)
- **Landing Page Experience**: Fast, mobile-optimized, relevant to the ad (must match search intent)

**Quality Score tiers:**
- 7-10: Below-average CPC, premium positions
- 4-6: Average CPC
- 1-3: Above-average CPC, limited impressions

---

## Performance Max (PMax) Strategy

PMax is the dominant campaign type in 2026. Properly optimized PMax delivers 30-50% better returns than traditional campaign structures.

### Asset Requirements for Competitive Performance
| Asset Type | Minimum | Target |
|-----------|---------|--------|
| Images | Required | 15-20 (lifestyle, product, branded, text-free mix) |
| Videos | Optional but critical | 6+ at various lengths (15s, 30s, 60s) |
| Headlines | Required | 15 unique headlines |
| Long Headlines | Required | 5 |
| Descriptions | Required | 5 |

**Providing limited assets starves the AI of testing options.** This is the #1 mistake. If no videos are provided, Google auto-generates them — usually poorly.

### Audience Signals (Critical)
Audience signals are technically "optional" but providing none wastes weeks and thousands of dollars:
- Upload customer lists as signals
- Define custom segments based on search behavior
- Include website visitor lists
- Add in-market and affinity audiences relevant to your product
- **These are SIGNALS, not restrictions** — Google will go beyond them

### PMax Campaign Structure
Don't run one massive PMax campaign. Segment by:
- **Product category or service type**
- **Customer acquisition vs remarketing**
- **Margin levels** (optimize toward profitable products)
- **Geographic regions** (if performance varies by location)

### PMax Optimization
- Feed Google real-time conversion data (use Google Ads conversion tag, not GA4 alone)
- Implement value-based bidding when possible
- Review asset performance weekly — replace underperformers
- Check search term insights monthly
- Maintain manual Shopping campaigns alongside PMax for precise control of strategic products

---

## Bidding Strategy Framework

### Progression by Campaign Maturity
| Stage | Conversions | Strategy |
|-------|------------|---------|
| New (0-30 conversions) | Gathering data | Maximize Clicks OR Maximize Conversions |
| Learning phase (30-50 conversions) | Building history | Maximize Conversions (optional CPA target) |
| Mature (50+ conversions/month) | Optimized | Target CPA or Target ROAS |
| Advanced | Scalable | Portfolio bid strategies across campaigns |

**Portfolio bid strategies** provide 19-27% ROAS improvement typical by dynamically reallocating budget across campaigns.

### Budget Rules
- High-intent search: Aggressive funding — marginal returns stay positive longest
- Mid/upper funnel: Capped budgets with clear cost ceilings
- Rebalance weekly based on marginal CPA/ROAS
- A campaign spending 3-5x target CPA with no conversions has a structural problem — pause and audit

### Never Set Aggressive Targets Early
Setting Target CPA or ROAS too aggressively before the algorithm has enough data starves it of the conversions needed to learn. Start permissive, tighten gradually.

---

## Tracking and Measurement Hierarchy

This hierarchy is non-negotiable. Bad tracking = bad optimization.

### Layer 1: Google Ads Conversion Tag (Primary)
- Real-time data for Smart Bidding
- Must be set up correctly before spending significant budget
- Tag fires on the actual conversion action (purchase, lead form submit, etc.)

### Layer 2: GA4 (Complement)
- Behavioral analysis and audience enrichment
- Useful for understanding the full user journey
- Import GA4 goals as secondary conversions in Google Ads

### Layer 3: Enhanced Conversions
- First-party data matching for better attribution
- Hashes customer data (email, phone) and matches to Google accounts
- Improves conversion measurement as cookies deprecate

### Layer 4: Offline Conversion Import
- Connect CRM data for true ROI measurement
- Critical for lead gen campaigns (track which leads actually become customers)
- Allows bidding toward leads that convert, not just any lead

### Attribution
- Use data-driven attribution (not last click)
- Track full funnel: micro-conversions (email signup, add to cart) AND macro-conversions (purchase, lead submit)
- Implement UTM parameters for cross-channel tracking

---

## Google Ads Funnel Role

| Stage | Best Use |
|-------|----------|
| Awareness | Display, YouTube, Demand Gen |
| Consideration | Search (informational queries), Display retargeting |
| Intent | Search (high-intent queries), Shopping |
| Purchase | Search (brand + product queries), Shopping, PMax |
| Retention | Remarketing campaigns |

---

## Key Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| Quality Score | Ad rank and CPC driver | 7+ |
| CPA | Cost Per Acquisition | Set by objective |
| ROAS | Return on Ad Spend | 3x+ (varies by margin) |
| CTR | Click-Through Rate | 5%+ for Search |
| Conversion Rate | Clicks to conversions | Depends on page/offer |
| Impression Share | % of eligible impressions won | 80%+ for brand |
| Search Term Match | Are you appearing for right terms? | Review weekly |

---

## Getting Started (Limited Budget)

If you're new to Google Ads or working with limited budget:

### Priority 1: Install Tracking BEFORE Spending
- Add Google Ads conversion tag to your website — it collects historical data from organic traffic
- Set up GA4 with goal tracking (page views, form submissions, calls)
- Add Enhanced Conversions for better attribution as cookies deprecate
- These accumulate audience data BEFORE you spend a dollar — more data = better launch performance

```html
<!-- Google Ads Conversion Tag — add to <head> of your website -->
<!-- Replace AW-XXXXXXXXX/YYYYYYY with your conversion ID/label from Google Ads -->
<script async src="https://www.googletagmanager.com/gtag/js?id=AW-XXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'AW-XXXXXXXXX');
</script>
```

### Priority 2: Start with Search (High-Intent)
- **Start small**: $10-20/day on Search is enough to learn and generate leads
- **Keywords**: Target high-intent, local searches specific to your service and geography
  - Format: "[your service] + [city/region]" (e.g., "web design [city name]", "website designer [area]")
  - Avoid broad informational keywords ("what is web design") — expensive and low intent
- **Use location extensions immediately** — critical for local service businesses
- **Separate campaigns**: Brand vs non-brand from Day 1

### Priority 3: Build Toward PMax
- Collect creative assets before launching: photos, videos of work, client testimonials, before/after examples
- Build a customer list (even small) to use as audience signals
- PMax performs dramatically better when seeded with real customer data
- Launch PMax only after Search campaigns have generated at least 50 conversions

---

## Commands / Triggers
- **"Create Google search ads for [product/service]"** → Generate RSA headlines (15) and descriptions (4) with keyword optimization
- **"Write a PMax asset group for [product/service]"** → Full asset suite: headlines, descriptions, image prompts, video scripts
- **"Build a keyword list for [business/service]"** → Research and organize keywords by intent tier with match type recommendations
- **"Review my Google Ads performance"** → Audit key metrics, flag issues, recommend optimizations
- **"Plan a Google Ads campaign structure"** → Design full campaign hierarchy: brand, non-brand, PMax
- **"Generate negative keyword list for [industry]"** → Build exclusion list to prevent waste
- **"Set up conversion tracking"** → Step-by-step guide for installing Google Ads tag and Enhanced Conversions
- **"Write ad extensions for [business]"** → Generate sitelinks, callouts, structured snippets, and call extensions
