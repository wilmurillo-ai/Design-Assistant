# Mad SEO Content 1.0: Technical Tool Specification

Mad SEO Content provides a lean, hyper-efficient suite of 11 strategic and editorial tools optimized for 2026-level content growth, AI visibility (GEO), and HCU compliance.

## 📊 Strategic Planning & AI Visibility

### `mad_seo:onboard`
Initializes the Content 1.0 environment and verifies required skill dependencies (`api-gateway`, `scrapling`, `agent-browser`).
- **returns**: Interactive onboarding instructions and dependency status report.

### `mad_seo:research_strategy`
Conducts **Omnichannel 3.0** research, merging traditional SERP data with social community sentiment.
- **topic** (string): The target keyword or concept.
- **returns**: A comprehensive strategic brief including "Social Proof" markers and entity relationship maps.

### `mad_seo:analyze_share_of_voice` [RESTORED]
Queries Gemini and Perplexity via the browser agent to calculate AI citation rates.
- **domain** (string): Your target website domain.
- **topics** (array of strings): Niche topics to search for.
- **returns**: A Share of Voice percentage and missing citation gaps.

### `mad_seo:plan_strategy`
Generates both the 12-month persistent roadmap and the monthly SQLite execution calendar.
- **niche** (string): The industry or specialized vertical.
- **location** (string): Target geography.
- **returns**: `PROJECT_STRATEGY.json` and SQLite inserts into `content_calendar` mapped to TOFU/MOFU/BOFU.

---

## ✍️ High-Authority Content Workflows

### `mad_seo:draft_article`
A single-pass generator that drafts the article, natively applies the **Human-GEO Framework** (burstiness injection/vocabulary sanitization), and outputs 3 high-CTR headline options.
- **topic** (string): Topic or strategic brief.
- **target_keyword** (string): Primary SEO target.
- **returns**: A fully formatted, humanized Markdown draft with Multimodal placeholders and title options.

### `mad_seo:audit_eeat`
Unified Scientific Audit verifying "Information Gain", detecting hallucinated claims, and evaluating Author Bio authority.
- **file_path** (string): Absolute path to the content file.
- **author_bio** (string, optional): Author's biography string.
- **returns**: Unified EEAT Score (0-100), Information Gain verification, and Bio GAP analysis.

### `mad_seo:site_wide_intelligence`
Global audit overlaying sitemap structure with GSC/GA4 performance metrics.
- **sitemap_url** (string): XML sitemap URL.
- **gsc_property** (string): GSC property URL.
- **returns**: Persistent **ENTITY_MAP.json** and prioritized list of optimization prescriptions.

### `mad_seo:inject_internal_links`
Automatically modifies existing, semantically-related markdown posts to inject contextual links to a newly published article.
- **new_post_path** (string): Absolute path to the newly published markdown file.
- **new_post_topic** (string): The core entity/topic of the new post.
- **returns**: Status list of the 3 modified older posts with injected PageRank links.

---

## 🛠️ Specialized Helpers

### `mad_seo:generate_schema`
Generates GEO-optimized JSON-LD schema with Knowledge Graph relationship anchoring.
- **content_path** (string): Path to the target article.
- **type** (string): Schema type (e.g., 'Article', 'FAQ', 'HowTo').
- **returns**: Structured JSON-LD block ready for injection.

### `mad_seo:repurpose_content`
Slices a pillar post into multiple distribution formats.
- **file_path** (string): Path to the finalized pillar post.
- **returns**: A bundle of distribution assets (Twitter thread, LinkedIn post, Newsletter intro) saved to `/shared/distribution/`.

### `mad_seo:analytics_suite`
A unified analytics router querying GA4/GSC via the API Gateway to diagnose traffic leaks.
- **audit_type** (string): Must be one of `['low_ctr', 'decay', 'cannibalization']`.
- **site_url** (string): GSC property URL.
- **target_keyword** (string, optional): Only required if audit_type is 'cannibalization'.
- **returns**: JSON report with explicit resolution instructions (e.g., SQLite calendar refresh marks, 301 redirects).

---
*Created with surgical precision by Mad Labs. Optimized for OpenClaw Content 1.0 Ecosystem.*
