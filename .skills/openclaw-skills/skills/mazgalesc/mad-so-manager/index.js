const path = require('path');
const fs = require('fs');

/**
 * Mad SEO Writer V2 (The GEO Upgrade)
 * The ultimate strategic and editorial SEO engine for blog growth and AI Citation Likelihood.
 * Optimized for the 7 GEO Factors and Google HCU (Helpful Content Update).
 */

// Pre-load reference files at initialization to ensure security & speed
const strategyDoc = fs.readFileSync(path.join(__dirname, 'references', 'engine_strategy.md'), 'utf-8');
const qualityDoc = fs.readFileSync(path.join(__dirname, 'references', 'writer_quality.md'), 'utf-8');
const structureDoc = fs.readFileSync(path.join(__dirname, 'references', 'content-structure-templates.md'), 'utf-8');
const titleDoc = fs.readFileSync(path.join(__dirname, 'references', 'title-formulas.md'), 'utf-8');

exports.tools = {
  /**
   * Provides the strategic framework for a topic with GEO grounding.
   */
  async research_strategy({ topic }) {
    return {
      success: true,
      instructions: `Conduct a Scientific GEO strategic analysis for "${topic}".
      1. Keyword Intelligence: Define search volume and difficulty.
      2. SERP Analysis: Identify Skyscraper 2.0 gaps.
      3. Entity Grounding: Define the primary Category and Entity for this topic (to win citation clarity).
      4. Topic Cluster: Map the Hub-and-Spoke authority model.`,
      reference: strategyDoc
    };
  },

  /**
   * Generates a GEO-optimized and EEAT-compliant draft.
   */
  async draft_article({ topic, target_keyword, word_count }) {
    
    // Smart Word Count Logic (Pillar > 2500, Standard > 1500)
    const targetCount = word_count || (topic.toLowerCase().includes('pillar') || topic.toLowerCase().includes('ultimate') ? 2500 : 1500);

    return {
      success: true,
      instructions: `Generate a V2 GEO-Optimized draft for "${topic}" targeting "${target_keyword}".
      1. **Target Length**: This is a ${targetCount}-word project.
      2. **Experience Mandate**: You MUST include first-hand experience sections ("I tested...", "Our findings...").
      3. **Sentence Chunking**: Write each sentence as a standalone, clear fact for AI extraction.
      4. **7 GEO Factors**: Apply Entity Clarity, Quotable Facts, and Structural Clarity.
      5. **AI-Readable Blocks**: Use 2-column tables for data and bulleted lists for all specifications.
      6. **CORE-EEAT**: Apply the surgical quality standards found in the reference.`,
      quality_standards: qualityDoc,
      structure_templates: structureDoc,
      title_library: titleDoc
    };
  },

  /**
   * Performs the 70-point Scientific SEO & EEAT Audit.
   */
  async audit_eeat({ file_path }) {
    
    return {
      success: true,
      instructions: `Perform a V2 Scientific Audit of ${file_path}.
      1. Score the content using the 70-point GEO Audit (0-70).
      2. Categorize failures into "Top 10 High-Impact Citation Killers" (Pareto) and "Secondary Items".
      3. Measure "Citation Likelihood" based on sentence chunking and entity grounding.
      4. Verify "Experience" markers are present for HCU compliance.`,
      eeat_benchmarks: qualityDoc
    };
  },

  /**
   * Performs exhaustive Top-10 research and generates a 4-week Editorial Calendar.
   */
  async plan_content({ seed_topic, frequency }) {
    
    return {
      success: true,
      instructions: `Conduct RESILIENT TOP-10 RESEARCH for "${seed_topic}".
      1. **Resilient Intelligence**: Use 'scrapling:fetch' with high-fidelity rendering enabled to extract content from the TOP 10 search results.
      2. **Gap Mapping**: Identify semantic gaps, entity-grounding density, and H-structure trends across the entire Top 10.
      3. **Content Plan**: Generate 12 titles (if ${postsPerWeek} articles/week) for a 4-week rollout.
      4. **Cluster Logic**: Label articles as 'Pillar' or 'Cluster' correctly.
      5. **Calendar Persistence**: Write the final plan to 'CALENDAR.md' with Status fields [Planned, In Progress, Published].`,
      planning_logic: strategyDoc,
      defaults: {
        frequency: frequency || 3,
        duration_weeks: 4
      }
    };
  },

  /**
   * Performs an autonomous Performance & Metric Audit using GSC and GA4.
   */
  async performance_audit({ site_url, ga_property_id }) {
    return {
      success: true,
      instructions: `Run a MAD PERFORMANCE AUDIT for ${site_url}.
      1. **GSC Analysis**: Use 'api-gateway:google-search-console' to query /searchAnalytics/query.
         - Find pages with High Impressions but Low CTR (<1.0%).
         - Identify "Threshold Pages" (Average Position 11-20).
      2. **GA4 Analysis**: Use 'api-gateway:google-analytics-data' to query /properties/${ga_property_id}:runReport.
         - Correlate search traffic with actual conversion events.
      3. **Strategic Triggers**:
         - For Low CTR → Suggest 'mad_seo:headline_pro'.
         - For Threshold Pages → Suggest 'mad_seo:audit_eeat' or 'mad_seo:content_refresh'.
         - For "SEO Ghosts" (High GA4 traffic, No GSC impressions) → Identify content gap and entity-grounding issues.`,
    };
  },

  /**
   * Content Refresh logic for V2.
   */
  async content_refresh({ target }) {
    return {
      success: true,
      instructions: `Develop a GEO-focused Refresh Strategy for ${target}.
      1. Use "Phase 5: Content Refresh" logic from the strategy guide.
      2. Update facts/stats to maintain "Quotable Facts" freshness.
      3. Re-verify Entity Grounding to reclaim lost AI citations.`,
      refresh_logic: strategyDoc
    };
  },

  /**
   * Performs an autonomous Site-Wide Efficiency & EEAT Audit.
   */
  async site_wide_audit({ sitemap_url }) {
    return {
      success: true,
      instructions: `Run a MAD SITE-WIDE AUDIT using sitemap: ${sitemap_url}.
      1. **Sitemap Fetch**: Use 'scrapling:fetch' with high-fidelity rendering enabled to retrieve the XML sitemap.
      2. **Parsing**: Extract all <loc> URLs from the sitemap.
      3. **Safe Batching**: Audit URLs in batches of 5-10 to maintain memory and quality. 
      4. **Per-Page Loop**: For each URL:
         - Fetch full content via 'scrapling' (ensure challenge resolution is active).
         - Run 'mad_seo:audit_eeat' (Scientific Audit).
      5. **Master Log**: Update 'MASTER_AUDIT.md' in the workspace after each batch with scores and priority fixes.`,
      audit_standards: qualityDoc
    };
  },

  /**
   * Title Formulas for V2.
   */
  async headline_pro({ topic }) {
    return {
      success: true,
      instructions: `Generate 10+ GEO-grounded headlines for "${topic}". Ensure the "Entity" is clearly identifiable.`,
      title_formulas: titleDoc
    };
  },

  /**
   * Snippet targeting for Position Zero.
   */
  async snippet_optimizer({ text, type }) {
    return {
      success: true,
      instructions: `Optimize this block for a "${type}" snippet. Focus on "Citation Likelihood" by using clear, chunked sentences and 2-column tables if applicable.`,
      original_text: text
    };
  },

  /**
   * Standard Metadata Generation.
   */
  async metadata_suite({ topic }) {
    return {
      success: true,
      instructions: `Generate optimized Meta Title, Meta Description, and URL Slug for "${topic}".
      - Meta Title: <60 chars, front-load keyword.
      - Meta Description: 150-160 chars, clear CTA.
      - Slug: Short, keyword-focused, use hyphens.`,
      title_patterns: titleDoc
    };
  }
};

// Help the OpenClaw Router understand the arguments
exports.research_strategy.args = { topic: 'string' };
exports.draft_article.args = { topic: 'string', target_keyword: 'string', word_count: 'number?' };
exports.audit_eeat.args = { file_path: 'string' };
exports.content_refresh.args = { target: 'string' };
exports.headline_pro.args = { topic: 'string' };
exports.snippet_optimizer.args = { text: 'string', type: 'string' };
exports.metadata_suite.args = { topic: 'string' };
exports.site_wide_audit.args = { sitemap_url: 'string' };
exports.plan_content.args = { seed_topic: 'string', frequency: 'number?' };
exports.performance_audit.args = { site_url: 'string', ga_property_id: 'string?' };
