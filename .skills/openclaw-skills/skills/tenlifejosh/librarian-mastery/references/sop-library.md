# SOP Library Management — Documenting Every Process So It Never Runs From Scratch

An SOP (Standard Operating Procedure) is the company's operational muscle memory. When a process works,
it gets documented as an SOP so that any agent can execute it perfectly the first time, without guessing,
without asking, without rediscovering what was already figured out.

---

## Table of Contents

1. [SOP Capture Philosophy](#sop-capture-philosophy)
2. [SOP Document Format](#sop-document-format)
3. [SOP Metadata Schema](#sop-metadata-schema)
4. [SOP Categorization by Workflow](#sop-categorization-by-workflow)
5. [Trigger Conditions](#trigger-conditions)
6. [Dependency Mapping](#dependency-mapping)
7. [SOP Review Cycles](#sop-review-cycles)
8. [SOP Retirement](#sop-retirement)
9. [SOP Library Maintenance](#sop-library-maintenance)

---

## SOP Capture Philosophy

### When to Create an SOP
Create an SOP when ANY of these are true:
- A process has been executed successfully 2+ times
- A process involves 3+ steps that must happen in a specific order
- A process interfaces with an external tool or platform (Gumroad, KDP, social media)
- A process was discovered through trial-and-error and the learnings must be preserved
- A human or agent says "document this process" or "save how we did this"
- A failure occurred because a process wasn't documented

### When NOT to Create an SOP
- For one-off tasks that genuinely won't recur
- For trivial processes (1-2 obvious steps)
- When an existing SOP already covers the process (update the existing one instead)

### The Capture Window
SOPs should be documented within 24 hours of a successful process execution. The details are freshest
immediately after the work is done. A quick-capture SOP (even incomplete) is better than no SOP.

### Quick-Capture vs Full SOP
- **Quick-Capture**: Steps listed in order with minimal detail. Status: DRAFT. Takes 5 minutes.
- **Full SOP**: Complete with metadata, prerequisites, decision branches, failure modes, and verification. Status: ACTIVE. Takes 30 minutes.

Always quick-capture first, then flesh out during maintenance.

---

## SOP Document Format

### Standard SOP File Format

```markdown
---
# SOP METADATA
sop_id: "gumroad-publish-sop"
name: "How to Publish a Product to Gumroad"
entity: "org"
version: "V2.1"
status: "APPROVED"
created: "2025-02-01"
created_by: "Ops Agent"
last_modified: "2025-03-21"
modified_by: "Ops Agent"
approved_by: "Human — JD"
approved_date: "2025-03-22"

# CLASSIFICATION
category: "publishing"
subcategory: "e-commerce"
tags: ["gumroad", "publishing", "e-commerce", "product-launch", "digital-products"]

# TRIGGER CONDITIONS
trigger_when:
  - "A new digital product is ready for sale"
  - "An existing product needs to be relisted or updated on Gumroad"
  - "Agent is asked to 'publish to Gumroad' or 'list on Gumroad'"

# PREREQUISITES
prerequisites:
  - "Product file is finalized and in ACTIVE or APPROVED status"
  - "Product description is written and approved"
  - "Pricing has been determined"
  - "Cover image is ready (1280x720 minimum)"
  - "Gumroad account credentials are available"

# DEPENDENCIES
depends_on_sops: []
depends_on_prompts: ["product-description-prompt"]
depends_on_templates: ["gumroad-listing-template"]
tools_required: ["Web browser", "Gumroad account"]

# ESTIMATED TIME
estimated_duration: "15-25 minutes"
difficulty: "low"

# VERSION HISTORY
changelog:
  - version: "V2.1"
    date: "2025-03-21"
    change: "Added step for coupon code setup"
    author: "Ops Agent"
  - version: "V2.0"
    date: "2025-03-01"
    change: "Updated for new Gumroad dashboard UI"
    author: "Ops Agent"
  - version: "V1.0"
    date: "2025-02-01"
    change: "Initial creation after first successful Gumroad publish"
    author: "Ops Agent"
---

# How to Publish a Product to Gumroad — V2.1

## Overview
This SOP covers the end-to-end process of listing a digital product for sale on Gumroad,
from login through to live listing verification.

## Prerequisites Checklist
Before starting, confirm ALL of these:
- [ ] Product file is ready (check assets/ directory, verify ACTIVE status)
- [ ] Product description is finalized (check prompts/ for description prompt)
- [ ] Price is set (check with Strategy Agent if unclear)
- [ ] Cover image is ready (1280x720px minimum, check assets/images/covers/)
- [ ] Gumroad account access is available

## Steps

### Step 1: Access Gumroad Dashboard
1. Navigate to https://gumroad.com
2. Log in with company credentials
3. Navigate to Products → New Product

### Step 2: Configure Product Details
1. **Product Name**: Use the official product name from the asset registry
2. **Price**: Set as determined in pre-requisites
3. **Description**: 
   - Use the approved product description from assets/
   - Format with markdown (Gumroad supports markdown)
   - Include all bullet points and formatting
4. **Cover Image**: Upload the approved cover from assets/images/covers/

### Step 3: Upload Product File
1. Click "Add content"
2. Upload the product file from assets/products/
3. Verify the file uploads completely (check file size matches)
4. Set the file name that customers will see when they download

### Step 4: Configure Settings
1. **URL slug**: Set to entity-product-name format (e.g., `gnd-cold-email-playbook`)
2. **Categories**: Select appropriate Gumroad categories
3. **Ratings**: Enable customer ratings
4. **Refund policy**: Set to "30-day no questions asked" (default)

### Step 5: Set Up Coupon Codes (if applicable)
1. Navigate to product's Discount Codes section
2. Create launch coupon: `LAUNCH20` for 20% off
3. Set coupon expiration to 7 days from launch
4. Note the coupon code in the product's asset registry entry

### Step 6: Preview and Verify
1. Click "Preview" to see the listing as customers will
2. Verify: product name, description, price, cover image, download file
3. Check that the URL is correct
4. Verify mobile display looks acceptable

### Step 7: Publish
1. Click "Publish" to make the listing live
2. Copy the live product URL
3. Verify the page loads correctly in an incognito browser

### Step 8: Post-Publish Verification
1. Complete a test purchase (use a test coupon if available)
2. Verify download works correctly
3. Verify the received file is the correct product file

### Step 9: Update Records
1. Update the asset registry with the Gumroad listing URL
2. Log the publish in the changelog
3. Notify the Marketing Agent that the product is live
4. If this is a new product, create entries for it in the asset index

## Decision Points

### If the product has variants (e.g., basic/premium):
→ Set up each variant as a separate tier within the same product listing
→ Price each tier according to the pricing strategy document

### If the product is an update to an existing listing:
→ Do NOT create a new listing — update the existing one
→ Upload new file version alongside old (Gumroad supports multiple versions)
→ Update the description and cover if changed

## Failure Modes

| Problem | Solution |
|---------|----------|
| Upload fails or times out | Check file size (<5GB limit), try again, try different browser |
| Cover image looks wrong | Verify dimensions (1280x720), check file format (PNG or JPG) |
| Test purchase fails | Check payment settings in Gumroad dashboard |
| URL slug already taken | Add year or version suffix: `gnd-cold-email-playbook-2025` |

## Verification Checklist
After completing all steps, verify:
- [ ] Listing is live and accessible via URL
- [ ] Price is correct
- [ ] Description displays properly
- [ ] Cover image displays properly
- [ ] Download works for test purchase
- [ ] Coupon codes work (if applicable)
- [ ] Asset registry is updated with listing URL
- [ ] Changelog entry is created
```

---

## SOP Metadata Schema

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `sop_id` | string | Unique identifier matching filename |
| `name` | string | Human-readable descriptive name |
| `entity` | string | Entity prefix (or `org` for cross-entity SOPs) |
| `version` | string | Current version |
| `status` | string | DRAFT / ACTIVE / APPROVED / ARCHIVED / DEPRECATED |
| `category` | string | Workflow category |
| `trigger_when` | array | Conditions that trigger this SOP |
| `prerequisites` | array | What must be true before starting |
| `estimated_duration` | string | How long execution takes |

### Required SOP Sections

Every complete (non-DRAFT) SOP must contain:
1. **Overview** — What this SOP accomplishes (1-3 sentences)
2. **Prerequisites Checklist** — What must be ready before starting
3. **Steps** — Numbered, sequential steps with sub-steps as needed
4. **Decision Points** — Branches where the process might diverge
5. **Failure Modes** — Common problems and their solutions
6. **Verification Checklist** — How to confirm the process completed successfully

---

## SOP Categorization by Workflow

### Primary Workflow Categories

```
sops/
├── by-workflow/
│   ├── publishing/         # Getting products to market
│   │   ├── gumroad/
│   │   ├── kdp/
│   │   ├── lulu/
│   │   └── shopify/
│   ├── marketing/          # Promoting products
│   │   ├── email-campaigns/
│   │   ├── social-media/
│   │   └── ad-campaigns/
│   ├── product-creation/   # Building products
│   │   ├── ebooks/
│   │   ├── courses/
│   │   ├── tools/
│   │   └── templates/
│   ├── sales/              # Selling to customers
│   │   ├── outbound/
│   │   ├── inbound/
│   │   └── follow-up/
│   ├── operations/         # Internal processes
│   │   ├── session-management/
│   │   ├── maintenance/
│   │   └── reporting/
│   ├── agent-management/   # Managing the agent system
│   │   ├── skill-creation/
│   │   ├── skill-updates/
│   │   └── agent-onboarding/
│   └── customer-support/   # Post-sale processes
│       ├── refunds/
│       ├── troubleshooting/
│       └── feedback/
```

---

## Trigger Conditions

### What Are Triggers?
Triggers define WHEN an SOP should be executed. They're the "if you see this situation, use this SOP" rules.

### Trigger Format

```yaml
trigger_when:
  - description: "A new digital product is ready for sale"
    trigger_type: "event"
    confidence: "high"
  - description: "Agent is asked to 'publish to Gumroad'"
    trigger_type: "command"
    confidence: "exact"
  - description: "A product listing needs updating"
    trigger_type: "condition"
    confidence: "medium"
```

### Trigger Types
- **event**: Something happens in the workflow (product completed, sale made)
- **command**: An explicit instruction ("publish this," "set up the campaign")
- **condition**: A state is detected (stale listing, broken link, missing asset)
- **schedule**: Time-based trigger (weekly maintenance, quarterly review)

### Trigger Matching
When an agent encounters a situation, it checks SOP triggers:
1. Exact match → execute that SOP
2. Multiple matches → check prerequisites to narrow down
3. Partial match → present options to the requesting agent
4. No match → flag as potential new SOP candidate

---

## Dependency Mapping

### What Dependencies Track
- **Upstream**: What must exist/be done before this SOP can run
- **Downstream**: What this SOP enables or produces
- **Lateral**: Other SOPs that often run alongside this one

### Dependency Map Format

```yaml
dependencies:
  upstream:
    sops: ["product-finalization-sop"]
    prompts: ["product-description-prompt"]
    templates: ["gumroad-listing-template"]
    assets: ["product-file", "cover-image"]
    tools: ["gumroad-account", "web-browser"]
    
  downstream:
    sops: ["marketing-launch-sop", "social-announcement-sop"]
    produces: ["live-gumroad-listing", "product-url"]
    notifies: ["Marketing Agent", "Sales Agent"]
    
  lateral:
    often_paired_with: ["pricing-strategy-sop", "launch-checklist-sop"]
    shared_prerequisites: ["product-finalization-sop"]
```

### Dependency Validation
During maintenance, verify:
- All upstream dependencies still exist and are ACTIVE
- All referenced prompts and templates are current versions
- Tool availability hasn't changed
- Downstream SOPs still expect what this SOP produces

---

## SOP Review Cycles

### Review Triggers
1. **Time-based**: Every SOP reviewed at least every 90 days
2. **Event-based**: After any execution that encountered problems
3. **Change-based**: When a dependency changes (tool updates, template revisions)
4. **Failure-based**: After any failure attributed to an outdated SOP

### Review Checklist

```markdown
## SOP Review — [SOP Name] — [Date]

### Accuracy Check
- [ ] All steps still work as described
- [ ] Screenshots/URLs are current
- [ ] Tool interfaces haven't changed
- [ ] Prerequisites are still valid

### Completeness Check
- [ ] No missing steps discovered during recent executions
- [ ] Decision points cover all known scenarios
- [ ] Failure modes include all known issues
- [ ] Verification checklist catches all important checks

### Dependency Check
- [ ] All referenced prompts are still ACTIVE and current version
- [ ] All referenced templates are still ACTIVE and current version
- [ ] All required tools are still available
- [ ] Downstream SOPs haven't changed their expectations

### Metadata Check
- [ ] Version number is correct
- [ ] Status is correct
- [ ] Tags are complete
- [ ] Changelog is up to date

### Outcome
- [ ] No changes needed — extend review date by 90 days
- [ ] Minor updates needed — increment minor version
- [ ] Major updates needed — increment major version
- [ ] SOP should be deprecated — follow deprecation process
```

---

## SOP Retirement

### When to Retire an SOP
- The workflow it describes no longer exists
- The tool/platform it interfaces with has been abandoned
- It's been superseded by a completely different approach
- The entity/product it serves has been retired
- It hasn't been executed in 180+ days and no future need is anticipated

### Retirement Process
1. Mark as DEPRECATED with reason
2. Identify replacement SOP if one exists
3. Check for downstream dependents and update them
4. 30-day grace period
5. Move to ARCHIVED
6. Update SOP index
7. Keep forever in archive

---

## SOP Library Maintenance

### Weekly (Friday Maintenance)
- Process any quick-capture SOPs from inbox/ (format and file them)
- Check for SOPs executed this week that had issues (log in lessons-learned)
- Update SOP index if new SOPs were added

### Monthly
- Review SOPs for accuracy (any tool/platform changes this month?)
- Flag SOPs approaching 90-day review deadline
- Check dependency maps for broken references
- Generate SOP library health report

### Quarterly
- Full review of all ACTIVE SOPs
- Retire SOPs inactive for 180+ days
- Review categorization taxonomy
- Archive DEPRECATED SOPs past grace period
- Generate SOP library statistics

### SOP Library Health Metrics

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| % of SOPs with complete metadata | >90% | 70-90% | <70% |
| % of SOPs reviewed in last 90 days | >80% | 50-80% | <50% |
| SOPs stuck in DRAFT > 14 days | <3 | 3-7 | >7 |
| SOPs with broken dependencies | 0 | 1-3 | >3 |
| Average SOP age (since last review) | <90 days | 90-180 days | >180 days |
