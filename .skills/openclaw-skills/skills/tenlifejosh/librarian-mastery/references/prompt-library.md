# Prompt Library Management — Capturing, Versioning, and Retrieving Reusable Prompts

A prompt that works is an asset worth more than the session it was created in. The prompt library ensures
that every effective prompt is captured, named, versioned, tagged, and retrievable — so the company never
rewrites a prompt that already exists and already works.

---

## Table of Contents

1. [Prompt Capture Philosophy](#prompt-capture-philosophy)
2. [Prompt Capture Format](#prompt-capture-format)
3. [Prompt Metadata Schema](#prompt-metadata-schema)
4. [Prompt Categorization Taxonomy](#prompt-categorization-taxonomy)
5. [Prompt Performance Tracking](#prompt-performance-tracking)
6. [Prompt Search and Retrieval](#prompt-search-and-retrieval)
7. [Prompt Evolution and Genealogy](#prompt-evolution-and-genealogy)
8. [Prompt Retirement](#prompt-retirement)
9. [Prompt Library Maintenance](#prompt-library-maintenance)

---

## Prompt Capture Philosophy

### When to Capture a Prompt
Capture a prompt when ANY of these are true:
- It produced a good result and will likely be needed again
- It's a standardized format that multiple agents will use
- It was iterated on more than twice to get right (that iteration is valuable)
- It interfaces with a specific tool or API that requires precise formatting
- A human or agent says "save this prompt" or "this works, keep it"

### When NOT to Capture
- One-off conversational queries that won't be reused
- Simple questions (e.g., "What's the capital of France?")
- Prompts that are already captured in a different, better form

### The 3-Minute Rule
A prompt should be captured within 3 minutes of the decision to save it. If the session ends without
capturing it, it's likely lost forever. Speed of capture > perfection of formatting. Capture fast, format
later during maintenance.

---

## Prompt Capture Format

Every reusable prompt is saved as a Markdown file with YAML frontmatter.

### Standard Prompt File Format

```markdown
---
# PROMPT METADATA
prompt_id: "gnd-cold-email-prompt"
name: "GND Cold Email Prompt"
entity: "gnd"
version: "V5.0"
status: "ACTIVE"
type: "generation"
created: "2025-03-15"
created_by: "Sales Agent"
last_modified: "2025-03-15"
modified_by: "Sales Agent"

# CLASSIFICATION
category: "sales"
subcategory: "cold-outreach"
tags: ["email", "cold-outreach", "B2B", "lead-generation"]

# USAGE
target_model: "claude-opus"
target_agent: "Sales Agent"
use_case: "Generating personalized cold emails for GND prospects"
input_variables:
  - name: "prospect_name"
    description: "Full name of the prospect"
    required: true
  - name: "company_name"
    description: "Prospect's company"
    required: true
  - name: "pain_point"
    description: "Specific pain point identified in research"
    required: true
  - name: "offer"
    description: "Specific offer or CTA"
    required: false
    default: "15-minute strategy call"
output_format: "Email text with subject line"
expected_length: "150-250 words"

# PERFORMANCE
performance_notes: "V5 subject lines average 34% open rate vs V4's 22%"
a_b_test_results: "Pain-point subjects outperform curiosity subjects 3:2"
known_limitations: "Less effective for C-suite prospects; use enterprise variant for VP+"

# VERSION HISTORY
changelog:
  - version: "V5.0"
    date: "2025-03-15"
    change: "New subject line framework based on A/B results"
    author: "Sales Agent"
  - version: "V4.0"
    date: "2025-03-01"
    change: "Restructured for new ICP targeting"
    author: "Sales Agent"

# RELATIONSHIPS
depends_on: []
used_by:
  - "outbound-sequence-sop-V1.0"
  - "cold-outreach-email-template-V2.0"
derived_from: "gnd-cold-email-prompt-V4.0"
---

# GND Cold Email Prompt — V5.0

## System Instructions

You are writing a personalized cold email for GND. The goal is to get a reply, not a sale. 
The email should feel like it was written by a human who did their research, not an AI or mass mailer.

## Prompt

Write a cold email to {{prospect_name}} at {{company_name}}.

**Context:**
- Their pain point is: {{pain_point}}
- Our offer: {{offer}}

**Requirements:**
1. Subject line: Reference their specific pain point in under 8 words
2. Opening: Reference something specific about their company (1 sentence)
3. Bridge: Connect their pain to our solution (2 sentences)
4. Proof: One specific result we've achieved (1 sentence with numbers)
5. CTA: Low-friction ask — suggest a 15-minute call, offer 2 specific times
6. P.S.: Add a relevant social proof element

**Constraints:**
- Total length: 150-200 words (excluding subject line)
- Tone: Peer-to-peer, not salesy
- No buzzwords: no "synergy," "leverage," "revolutionary"
- No false urgency: no "limited time," "act now"

## Example Output

Subject: {{company_name}}'s [pain point] is costing you $X/month

Hi {{prospect_name}},

[Specific reference to their company]...

[Prompt continues with full example...]

## Notes

- For C-suite prospects (VP+), use the enterprise variant: `gnd-cold-email-prompt-enterprise`
- Always A/B test subject lines when sending to >50 prospects
- Pair with the nurture sequence prompt if first email gets no reply after 5 days
```

---

## Prompt Metadata Schema

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `prompt_id` | string | Unique identifier matching filename (without version/status/ext) |
| `name` | string | Human-readable name |
| `entity` | string | Entity prefix from registry |
| `version` | string | Current version (V{X.Y}) |
| `status` | string | DRAFT / ACTIVE / APPROVED / ARCHIVED / DEPRECATED |
| `type` | string | Prompt type (see types below) |
| `created` | date | Creation date |
| `created_by` | string | Creating agent or human |
| `category` | string | Primary category |
| `tags` | array | Searchable tags |
| `use_case` | string | One-sentence description of when to use this prompt |

### Optional but Recommended Fields

| Field | Type | Description |
|-------|------|-------------|
| `target_model` | string | Preferred AI model |
| `target_agent` | string | Which agent typically uses this |
| `input_variables` | array | Variables that need to be filled in |
| `output_format` | string | Expected output format |
| `performance_notes` | string | How well this prompt performs |
| `known_limitations` | string | When this prompt doesn't work well |
| `depends_on` | array | Other prompts this one requires |
| `used_by` | array | SOPs/templates that reference this prompt |
| `derived_from` | string | Parent prompt this was forked/evolved from |

### Prompt Types

| Type | Description | Example |
|------|-------------|---------|
| `generation` | Creates new content from variables | Cold email writer |
| `transformation` | Converts input content to a different format | Blog post → social media thread |
| `extraction` | Pulls specific info from content | Extract action items from meeting notes |
| `analysis` | Evaluates or scores content | Grade a sales email 1-10 |
| `classification` | Categorizes input into buckets | Classify support ticket by urgency |
| `editing` | Improves existing content | Tighten copy to under 200 words |
| `system` | Defines agent behavior/role | Sales Agent persona prompt |
| `chain` | Multi-step prompt that orchestrates sub-prompts | Full campaign generation pipeline |

---

## Prompt Categorization Taxonomy

### Primary Categories

```
prompts/
├── sales/
│   ├── cold-outreach/
│   ├── follow-up/
│   ├── proposals/
│   └── objection-handling/
├── marketing/
│   ├── social-media/
│   ├── email-campaigns/
│   ├── ad-copy/
│   └── content-marketing/
├── product/
│   ├── descriptions/
│   ├── features/
│   └── documentation/
├── operations/
│   ├── data-processing/
│   ├── reporting/
│   └── automation/
├── creative/
│   ├── writing/
│   ├── design-briefs/
│   └── storytelling/
└── system/
    ├── agent-personas/
    ├── tool-interfaces/
    └── workflow-chains/
```

### Tagging Rules
1. Every prompt gets 3-7 tags
2. Tags are lowercase, hyphenated
3. Tags should include: function (what it does), entity (who it's for), channel (where it's used)
4. Common tags: `email`, `social`, `B2B`, `B2C`, `long-form`, `short-form`, `data`, `creative`

---

## Prompt Performance Tracking

### Performance Metadata Block

```yaml
performance:
  last_tested: "2025-03-15"
  test_count: 25
  success_rate: "88%"
  average_quality_score: 8.2  # 1-10 scale
  a_b_tests:
    - test_id: "AB-2025-03-10"
      variants: ["curiosity-subject", "pain-point-subject"]
      winner: "pain-point-subject"
      margin: "12% higher open rate"
      sample_size: 200
  known_failure_modes:
    - "Produces generic output when pain_point variable is vague"
    - "Less effective for technical audiences (engineering, DevOps)"
  optimization_notes:
    - "V5's subject lines significantly outperform V4 — don't roll back"
    - "Adding industry-specific proof points improves reply rate by ~15%"
```

### When to Update Performance Data
- After any batch send using the prompt (email campaigns, outreach sequences)
- After A/B testing with at least 50 sends per variant
- After human quality review of 10+ outputs
- After any reported failure or unexpected result

---

## Prompt Search and Retrieval

### Search Interface
Agents should be able to find prompts by:
1. **Entity**: "Show me all GND prompts"
2. **Category**: "Show me all cold-outreach prompts"
3. **Tag**: "Show me all prompts tagged B2B"
4. **Status**: "Show me all ACTIVE prompts"
5. **Type**: "Show me all generation prompts"
6. **Use case keyword**: "Show me prompts for email subject lines"
7. **Performance**: "Show me prompts with >80% success rate"

### Quick Retrieval Pattern
When an agent needs a prompt:
1. Check the prompt index (`prompts/_index.md`)
2. Search by entity + function (most common retrieval pattern)
3. Verify the returned prompt has ACTIVE or APPROVED status
4. Check the version matches the source-of-truth registry
5. Fill in variables and use

### Prompt Index Auto-Generation
The `prompts/_index.md` file is auto-generated during maintenance:

```markdown
# Prompt Library Index

Last updated: 2025-03-21 | Total prompts: 47 | Active: 32 | Draft: 8 | Archived: 7

## By Entity
| Entity | Active Prompts | Total Prompts |
|--------|---------------|---------------|
| gnd | 12 | 18 |
| famli-claw | 8 | 12 |
| agentreach | 5 | 8 |
| org | 7 | 9 |

## Active Prompts Quick Reference
| Prompt ID | Version | Category | Use Case |
|-----------|---------|----------|----------|
| gnd-cold-email-prompt | V5.0 | sales/cold-outreach | Cold emails for GND prospects |
| famli-claw-product-desc-prompt | V3.0 | product/descriptions | Product descriptions for FC |
| ... | ... | ... | ... |
```

---

## Prompt Evolution and Genealogy

### Genealogy Tracking
Every prompt has a lineage showing how it evolved:

```yaml
genealogy:
  generation: 5  # How many versions deep this is
  origin: "gnd-cold-email-prompt-V1.0"
  evolution_path:
    - version: "V1.0"
      change_type: "creation"
      key_insight: "Basic cold email template"
    - version: "V2.0"
      change_type: "major-rewrite"
      key_insight: "Shifted to outcome-focused messaging"
    - version: "V3.0"
      change_type: "enhancement"
      key_insight: "Added personalization variables"
    - version: "V4.0"
      change_type: "major-rewrite"
      key_insight: "Restructured for new ICP"
    - version: "V5.0"
      change_type: "optimization"
      key_insight: "A/B tested subject lines, pain-point approach wins"
  
  forks:
    - "gnd-cold-email-prompt-enterprise-V1.0"  # Branched for enterprise prospects
  
  inspired_by:
    - "competitor-email-analysis-2025"  # External inspiration
```

### Fork vs Version
- **New version**: Same prompt, improved → increment version
- **Fork**: Same base prompt, different audience or use case → new prompt with `derived_from` link

---

## Prompt Retirement

### When to Retire a Prompt
- The workflow it supports no longer exists
- It's been superseded by a fundamentally different approach (not just a new version)
- The product/entity it serves has been retired
- It's been inactive (unused) for 180+ days
- Performance has degraded and optimization hasn't helped

### Retirement Process
1. Mark as DEPRECATED with reason and replacement pointer
2. Notify any SOPs or templates that reference it
3. Allow 30-day grace period
4. Move to ARCHIVED
5. Update prompt index
6. Keep forever in archive (prompts are never deleted)

---

## Prompt Library Maintenance

### Weekly (Friday Maintenance)
- Process any prompts in inbox/ that need naming and filing
- Update prompt index if new prompts were added
- Check for prompts stuck in DRAFT > 14 days
- Verify ACTIVE prompt count matches source-of-truth registry

### Monthly
- Review performance data for all ACTIVE prompts
- Flag underperforming prompts (success rate < 50%) for review
- Update tags and categories for any recently-added prompts
- Generate prompt library health report

### Quarterly
- Full genealogy review: are prompt families well-organized?
- Retire prompts inactive for 180+ days
- Review and update the categorization taxonomy
- Archive any DEPRECATED prompts past grace period
- Generate prompt library statistics for the quarter

### Prompt Library Health Metrics
| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| % of prompts with complete metadata | >90% | 70-90% | <70% |
| % of ACTIVE prompts tested in last 90 days | >80% | 50-80% | <50% |
| Average prompt age (ACTIVE) | <180 days | 180-365 days | >365 days |
| Prompts stuck in DRAFT > 14 days | <5 | 5-10 | >10 |
| Naming compliance rate | 100% | 95-99% | <95% |
