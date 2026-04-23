# MAD SEO CONTENT 🚀 (Version 1.0.2)

**Mad SEO Content** is the ultimate autonomous content and authority engine for OpenClaw. Built for the **2026 SEO/GEO Landscape**, it transforms the standard SEO writing process into a director-level management workflow oriented toward **Omnichannel Authority**, **Multimodal Attribution**, and **Human-GEO Content Synthesis**.

Version 1.0.1 introduces the **Lean 11-Tool Architecture**, merging overlapping tools to ensure lightning-fast context efficiency, zero hallucination rates, and flawless autonomous execution.

---

## 🛠️ The Lean 11-Tool Suite

### 1. `mad_seo:onboard`
Triggers the interactive Content 1.0 onboarding workflow to verify dependencies and ask for your **Target Market and Language** (e.g., Italy/Italian) for localized research.
*Trigger: "Onboard me to MAD SEO CONTENT"*

### 2. `mad_seo:research_strategy`
Performs **Omnichannel 3.0 Analysis**. It crawls SERP Top-10 AND community sentiment from platforms like Reddit to find unique "experience-based" insights.
*Trigger: "Omnichannel research for [Topic]"*

### 3. `mad_seo:analyze_share_of_voice` [RESTORED]
Analyzes AI search responses (Gemini, Perplexity) to calculate your brand's **AI Citation Score**.
*Trigger: "Analyze share of voice"*

### 4. `mad_seo:plan_strategy` [MERGED]
*Replaces generate_roadmap & plan_content.*
Generates the 12-month strategic roadmap and specifically creates the next 4 weeks of titles, classifying them by Funnel Stage (TOFU/MOFU/BOFU) and saving them to the SQLite `mad_seo.db`.
*Trigger: "Plan my strategy"*

### 5. `mad_seo:draft_article` [MERGED]
*Replaces draft_article, humanize_content & headline_pro.*
A single-pass powerhouse. The agent drafts a 1,500-3,000 word article, **natively applies the Human-GEO Framework** (bypassing AI detectors with statistical burstiness), and generates 3 high-CTR headline options at the top of the file.
*Trigger: "Draft an article"*

### 6. `mad_seo:audit_eeat` [MERGED]
*Replaces audit_eeat & audit_author.*
Performs a unified Scientific Audit. It checks the article for "Information Gain" (ensuring 3 unique concepts not found in Top 10), flags hallucinations, AND evaluates the Author's bio to secure "Expertise" markers.
*Trigger: "Audit eeat"*

### 7. `mad_seo:generate_schema`
Generates GEO-optimized JSON-LD (Article, FAQ, HowTo) with Knowledge Graph relationship anchoring (Wikidata).
*Trigger: "Generate schema"*

### 8. `mad_seo:site_wide_intelligence`
Deep audit linking Sitemap URLs to GSC performance. It builds a **Global Entity Map** for optimal internal linking architecture.
*Trigger: "Run site intelligence"*

### 9. `mad_seo:inject_internal_links` [NEW]
Automatically opens existing, high-authority markdown posts and injects natural, contextual sentences linking to a newly published article to instantly pass PageRank.
*Trigger: "Inject internal links"*

### 10. `mad_seo:repurpose_content`
Executes the 'One-to-Many' workflow, slicing a pillar post into Twitter threads, LinkedIn posts, and Newsletter teasers.
*Trigger: "Repurpose content"*

### 11. `mad_seo:analytics_suite` [MERGED]
*Replaces performance_audit, content_decay & cannibalization.*
A unified analytics engine that talks to GA4/GSC via API. It handles 3 specific audit types:
- `low_ctr`: Finds pages with high impressions but no clicks.
- `decay`: Finds old pages losing traffic to schedule a refresh.
- `cannibalization`: Finds URLs fighting each other for the same keyword.
*Trigger: "Run analytics suite"*

---

## 🧠 The Human-GEO Framework
Built directly into the drafting tool, it bypasses detection via:
1. **Burstiness Injection**: Mixes sentence lengths to match human linguistic flow.
2. **Vocabulary Sanitization**: Automatically strips "AI giveaway" terms (e.g., *Delve, Tapestry*).
3. **Significance Inflation Removal**: Replaces fluffy, hyperbolic language with direct facts.
4. **Social Proof Anchoring**: Injects specific community findings from Reddit/Forums.

## 🧩 Dependencies
> [!IMPORTANT]
> To unlock Version 1.0 features, the following skills are required:
> 1. **`api-gateway`** — GSC/GA4 Data access.
> 2. **`scrapling-official`** — Social discovery (Reddit/Forums).
> 3. **`agent-browser`** — Live AI search analysis.
