const path = require('path');
const refs = require('./references.json');

/**
 * Mad SEO Content Version 1.0 (Lean 11-Tool Architecture)
 * The ultimate autonomous SEO/GEO engine for blog growth and topical authority.
 * Highly optimized for OpenClaw context efficiency and autonomous execution.
 */

exports.tools = {
  /**
   * Provides an interactive V6 onboarding dashboard for the user.
   */
  async onboard() {
    return {
      success: true,
      instructions: `Run the MAD SEO CONTENT 1.0 ONBOARDING Workflow:
      1. **Introduction**: Introduce yourself as the Lean 11-Tool Omnichannel SEO Director.
      2. **Dependency Check**: Inform the user you are verifying 'scrapling-official', 'api-gateway', and 'agent-browser'.
      3. **Data Collection (Crucial)**: Ask the user to provide the following 4 pieces of information to set up the workspace:
         - **Target Market & Language** (e.g., Italy/Italian)
         - **Brand Name & Core Service** (e.g., 'Mad Labs, Web Design')
         - **Google Search Console & GA4 Property URLs** (Required for the Analytics Suite)
         - **Sitemap XML URL** (Required for Entity Mapping)
      4. **State Initialization**: Tell the user that once they provide this info, you will save it to '/shared/PROJECT_STRATEGY.json' and initialize the '/shared/mad_seo.db' SQLite calendar.
      5. **First Action**: Ask them to provide the data to begin!`,
    };
  },

  /**
   * Performs Omnichannel 3.0 strategic research with Social Discovery.
   */
  async research_strategy({ topic }) {
    return {
      success: true,
      instructions: `Conduct a Content 1.0 Omnichannel strategic analysis for "${topic}".
      1. **SERP Intelligence**: Identify Skyscraper 3.0 content gaps in the Top 10.
      2. **Social Discovery**: Use 'scrapling' to analyze Reddit/Discourse for real-world pain points and unique terminology.
      3. **Entity Grounding**: Define the Knowledge Graph Category and Primary Entity relationship.
      4. **Social Proof Injection**: Suggest 3-5 community-sourced "Experience Markers" for HCU compliance.`,
      reference: refs.engine_strategy,
      local_benchmarks: refs.local_compliance
    };
  },

  /**
   * Generates a 12-month strategy AND creates the monthly SQLite editorial calendar.
   */
  async plan_strategy({ niche, location }) {
    return {
      success: true,
      instructions: `Execute the Strategy Planning Protocol for [${niche}] in [${location}]:
      1. **Predictive Roadmap**: Generate a high-level 12-month strategy identifying "Quick Win" clusters. Save to '/root/.openclaw/shared/PROJECT_STRATEGY.json'.
      2. **Topic Generation**: Extract 12 specific titles for the first 4-week rollout based on the roadmap.
      3. **Funnel Alignment**: Classify each title into TOFU (Awareness), MOFU (Consideration), or BOFU (Decision).
      4. **Stateful Tracking**: Connect to SQLite DB at '/root/.openclaw/shared/mad_seo.db' and INSERT these 12 titles into the 'content_calendar' table.`,
      roadmap_logic: refs.roadmap_strategy,
      funnel_strategy: refs.funnel_strategy,
      db_schema: refs.db_schema
    };
  },

  /**
   * Generates GEO-optimized content, applies the Human-GEO pass natively, and outputs headlines.
   */
  async draft_article({ topic, target_keyword }) {
    const configPath = './references/humanizer_config.json';
    return {
      success: true,
      instructions: `Draft, Humanize, and Title the article for "${topic}" targeting "${target_keyword}".
      1. **Writing**: Draft a 1,500-3,000 word pillar post. Include a "Suggested Visual Evidence" table at the end.
      2. **Humanization Pass**: Natively apply the Human-GEO Framework (referenced in '${configPath}'). Strip all 'Tier 1' AI-giveaway terms and force sentence burstiness (<10 and >20 words).
      3. **Headlines**: Generate 3 high-CTR, human-sounding headline options at the top of the file using 'refs.title_formulas'.
      4. **Output**: Write the final, humanized draft to '/shared/content/[topic].md'.`,
      quality_standards: refs.writer_quality,
      structure_templates: refs.structure_templates,
      title_library: refs.title_formulas,
      humanizer_config: configPath
    };
  },

  /**
   * Comprehensive EEAT Audit: Checks the article for fabrication AND the author's bio.
   */
  async audit_eeat({ file_path, author_bio }) {
    return {
      success: true,
      instructions: `Perform a Unified Content 1.0 EEAT Audit of ${file_path} and the provided Author Bio.
      1. **Fabrication Check**: Scan the article for "I remember when..." or subjective claims not backed by data.
      2. **Information Gain**: Verify the article contains at least 3 unique concepts not found in the SERP Top 10.
      3. **Author Authority**: Evaluate the 'author_bio'. Suggest improvements to secure higher "Expertise" markers.
      4. **Output**: Generate a single EEAT Score (0-100) combining Content Trust and Author Trust.`,
      eeat_benchmarks: refs.writer_quality
    };
  },

  /**
   * Generates GEO-optimized JSON-LD schema blocks.
   */
  async generate_schema({ content_path, type }) {
    return {
      success: true,
      instructions: `Analyze ${content_path} and generate a Content 1.0 GEO-Optimized "${type}" Schema.
      1. Use 'schema_architect' to ensure proper "Relationship Anchoring".
      2. Inject Knowledge Graph IDs (Wikidata) where applicable.`,
      schema_logic: refs.schema_architect
    };
  },

  /**
   * Performs an autonomous Site-Wide Deep Intelligence and Entity Mapping.
   */
  async site_wide_intelligence({ sitemap_url, gsc_property }) {
    return {
      success: true,
      instructions: `Run a Content 1.0 GLOBAL SITE INTELLIGENCE AUDIT for: ${sitemap_url}.
      1. **Global Entity Map**: Build '/root/.openclaw/shared/ENTITY_MAP.json' containing all site entities and their relationships.
      2. **Performance Overlay**: Attach GSC performance metrics to each entity node.
      3. **Master Prescription**: Write individualized optimization reports to '/root/.openclaw/shared/audits/'.`,
      audit_standards: refs.writer_quality
    };
  },

  /**
   * Automatically finds older, high-authority posts and injects contextual links to a newly published post.
   */
  async inject_internal_links({ new_post_path, new_post_topic }) {
    return {
      success: true,
      instructions: `Run the Content 1.0 Internal Link Injection sequence for "${new_post_topic}":
      1. **Query Entity Map**: Use '/shared/ENTITY_MAP.json' to find 3 semantically related, existing high-authority posts.
      2. **Contextual Injection**: Open the Markdown files of those 3 older posts.
      3. **Insertion**: Naturally weave a new sentence into each older post that links to ${new_post_path}.`
    };
  },

  /**
   * Slices a pillar post into multiple distribution formats for omnichannel marketing.
   */
  async repurpose_content({ file_path }) {
    return {
      success: true,
      instructions: `Analyze ${file_path} and execute the 'One-to-Many' repurposing protocol:
      1. **Twitter/X**: Extract 3 core insights to create an engaging Thread.
      2. **LinkedIn**: Rewrite the introduction into a high-authority narrative post.
      3. **Newsletter**: Draft a 150-word teaser linking to the main article.
      4. Save outputs to '/shared/distribution/' and update the SQLite 'content_calendar' status to 'Repurposed'.`,
      funnel_strategy: refs.funnel_strategy
    };
  },

  /**
   * Analyzes AI search responses to calculate AI Citation Share.
   */
  async analyze_share_of_voice({ domain, topics }) {
    return {
      success: true,
      instructions: `Perform a general AI Citation Share analysis for ${domain} across [${topics.join(', ')}].
      1. **AI Scrape**: Use 'agent-browser' to query Gemini and Perplexity for these topics.
      2. **Citation Extract**: Identify which domains are currently being cited as primary sources.
      3. **Score Calculation**: Calculate the "Share of AI Voice" percentage for ${domain}.
      4. **Gap Analysis**: If ${domain} is missing, identify the specific "Relationship Facts" being cited from competitors.`,
    };
  },

  /**
   * Unified Analytics Suite (Handles Performance, Decay, and Cannibalization).
   */
  async analytics_suite({ audit_type, site_url, target_keyword }) {
    return {
      success: true,
      instructions: `Run the Analytics Suite via 'api-gateway' for audit type: [${audit_type}].
      1. **If 'low_ctr'**: Fetch GSC data to find "High Impression / Low CTR" optimization targets and recommend title/schema changes.
      2. **If 'decay'**: Identify URLs where traffic dropped >20% YoY. Mark them in the SQLite 'content_calendar' for a 'Refresh'.
      3. **If 'cannibalization'**: Check if multiple URLs receive impressions for "${target_keyword}". Suggest 301 redirects or canonical tags for the loser.`
    };
  }
};

// OpenClaw Mad SEO Content 1.0 Argument Decorators
exports.onboard.args = {};
exports.research_strategy.args = { topic: 'string' };
exports.plan_strategy.args = { niche: 'string', location: 'string' };
exports.draft_article.args = { topic: 'string', target_keyword: 'string' };
exports.audit_eeat.args = { file_path: 'string', author_bio: 'string?' };
exports.generate_schema.args = { content_path: 'string', type: 'string' };
exports.site_wide_intelligence.args = { sitemap_url: 'string', gsc_property: 'string' };
exports.inject_internal_links.args = { new_post_path: 'string', new_post_topic: 'string' };
exports.repurpose_content.args = { file_path: 'string' };
exports.analyze_share_of_voice.args = { domain: 'string', topics: 'string[]' };
exports.analytics_suite.args = { audit_type: 'string', site_url: 'string', target_keyword: 'string?' };
