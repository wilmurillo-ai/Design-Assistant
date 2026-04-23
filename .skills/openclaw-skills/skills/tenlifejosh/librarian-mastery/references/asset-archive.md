# Asset & Template Archive — Managing Every Deliverable and Reusable Format

Assets are the tangible outputs of the company's work — products, images, covers, documents, skill files,
and every other deliverable. Templates are the reusable structural formats that produce those assets.
Together, they represent the company's productive capacity. The Librarian ensures every asset is findable,
versioned, and never confused with an outdated copy.

---

## Table of Contents

1. [Asset Management Philosophy](#asset-management-philosophy)
2. [Asset Metadata Schema](#asset-metadata-schema)
3. [Asset Categorization](#asset-categorization)
4. [Asset Status Tracking](#asset-status-tracking)
5. [Template Library Management](#template-library-management)
6. [Template Metadata Schema](#template-metadata-schema)
7. [Template Versioning](#template-versioning)
8. [Deduplication Logic](#deduplication-logic)
9. [Asset Retrieval Patterns](#asset-retrieval-patterns)
10. [Asset Library Maintenance](#asset-library-maintenance)

---

## Asset Management Philosophy

### What is an Asset?
Anything the company intentionally created that has persistent value:
- Product files (ebooks, courses, tools, downloads)
- Images (covers, social media graphics, marketing images, logos)
- Documents (sales pages, product descriptions, legal docs)
- Skill files (agent configurations, SKILL.md bundles)
- Data files (spreadsheets, databases, exports)
- Media files (audio, video if applicable)

### What is NOT an Asset?
- Temporary files created during processing
- Conversation logs (unless explicitly marked as lessons/insights)
- Duplicate copies (the canonical copy is the asset; copies are waste)
- Test outputs that weren't adopted

### The Asset Lifecycle
```
Created → Named → Versioned → Filed → Indexed → Maintained → (Updated | Archived)
```

Every step matters. An asset that's created but not named is lost. An asset that's filed but not indexed
is hidden. An asset that's not maintained becomes stale.

---

## Asset Metadata Schema

### Metadata Block (YAML Frontmatter for Documents, Sidecar for Binary Files)

For markdown/text assets, metadata lives in YAML frontmatter.
For binary files (images, PDFs, etc.), metadata lives in a sidecar file: `{filename}.meta.yaml`

```yaml
# ASSET METADATA
asset_id: "famli-claw-cover-kindle"
name: "FamliClaw Kindle Cover Image"
entity: "famli-claw"
version: "V2.0"
status: "ACTIVE"
asset_type: "image"
file_format: "png"
created: "2025-03-01"
created_by: "Design Agent"
last_modified: "2025-03-15"
modified_by: "Design Agent"

# CLASSIFICATION
category: "images"
subcategory: "covers"
tags: ["cover", "kindle", "ebook", "famli-claw"]

# SPECIFICATIONS
specifications:
  dimensions: "1600x2560px"
  file_size: "2.4MB"
  color_space: "sRGB"
  resolution: "300dpi"
  
# USAGE
used_in:
  - "KDP listing for FamliClaw ebook"
  - "Gumroad listing for FamliClaw bundle"
requirements_met:
  - "KDP cover requirements (1600x2560, 300dpi)"
  - "Gumroad cover requirements (1280x720 minimum)"
  
# RELATIONSHIPS
depends_on: []
used_by_sops: ["kdp-publish-sop", "gumroad-publish-sop"]
part_of_bundle: "famli-claw-product-bundle"
related_assets:
  - "famli-claw-cover-social-V1.0"  # Social media variant
  - "famli-claw-cover-print-V1.0"   # Print variant

# VERSION HISTORY
changelog:
  - version: "V2.0"
    date: "2025-03-15"
    change: "Complete redesign for KDP requirements"
    author: "Design Agent"
  - version: "V1.0"
    date: "2025-03-01"
    change: "Initial creation"
    author: "Design Agent"
```

### Sidecar Metadata Files
For binary files that can't contain YAML frontmatter:

```
assets/by-entity/famli-claw/images/covers/
├── famli-claw-cover-kindle-V2.0-ACTIVE.png        # The actual image
├── famli-claw-cover-kindle-V2.0-ACTIVE.meta.yaml   # Metadata sidecar
├── famli-claw-cover-kindle-V1.0-ARCHIVED.png       # Previous version
└── famli-claw-cover-kindle-V1.0-ARCHIVED.meta.yaml # Previous metadata
```

---

## Asset Categorization

### Primary Asset Categories

| Category | Subcategories | File Types |
|----------|--------------|------------|
| `products` | ebooks, courses, tools, downloads, templates-for-sale | .pdf, .epub, .zip, .docx |
| `images` | covers, social, marketing, logos, screenshots | .png, .jpg, .svg, .webp |
| `documents` | sales-pages, descriptions, legal, contracts | .md, .docx, .pdf |
| `skills` | active-skills, archived-skills | .md (SKILL.md bundles) |
| `data` | spreadsheets, exports, databases | .xlsx, .csv, .json |
| `media` | audio, video (if applicable) | .mp3, .mp4 |
| `code` | scripts, tools, automations | .py, .js, .sh |

### Directory Placement Rules
- Assets always live under `assets/by-entity/{entity}/`
- Within entity, organized by category: `products/`, `images/`, `documents/`
- Within category, organized by subcategory if needed: `images/covers/`, `images/social/`

---

## Asset Status Tracking

### Asset Status Registry
The source-of-truth registry tracks every asset's current status. For assets specifically:

```json
{
  "asset_id": "famli-claw-cover-kindle",
  "current_version": "V2.0",
  "current_status": "ACTIVE",
  "canonical_path": "assets/by-entity/famli-claw/images/covers/famli-claw-cover-kindle-V2.0-ACTIVE.png",
  "external_locations": [
    {
      "platform": "KDP",
      "url": "https://kdp.amazon.com/...",
      "version_deployed": "V2.0",
      "last_synced": "2025-03-15"
    },
    {
      "platform": "Gumroad",
      "url": "https://gumroad.com/...",
      "version_deployed": "V2.0",
      "last_synced": "2025-03-15"
    }
  ]
}
```

### External Deployment Tracking
When assets are deployed to external platforms, track:
- Which version is deployed where
- When it was last synced
- Whether the deployed version matches the current canonical version
- Flag: if canonical version is V3.0 but KDP still has V2.0 → "OUT OF SYNC"

---

## Template Library Management

### What is a Template?
A template is a reusable structural format with fill-in sections. It defines the SHAPE of an output
without being the output itself.

Examples:
- Agent handoff template (structure for how agents pass work to each other)
- Email template (HTML structure for marketing emails)
- Product brief template (structure for defining a new product)
- Report template (structure for weekly/monthly reports)

### Template vs Prompt vs SOP
| Asset Type | Purpose | Contains |
|-----------|---------|----------|
| **Prompt** | Instructions for AI to generate content | Instructions, variables, examples |
| **SOP** | Step-by-step process for executing a workflow | Steps, decisions, verification |
| **Template** | Reusable structural format for outputs | Sections, placeholders, formatting |

### Template File Format

```markdown
---
template_id: "agent-handoff-template"
name: "Agent-to-Agent Handoff Template"
entity: "org"
version: "V1.0"
status: "ACTIVE"
template_type: "document"
created: "2025-02-15"
created_by: "Ops Agent"

# USAGE
use_case: "Structured handoff between agents for any multi-agent task"
fill_in_fields:
  - field: "from_agent"
    description: "Name of the agent handing off"
    required: true
  - field: "to_agent"
    description: "Name of the receiving agent"
    required: true
  - field: "task_summary"
    description: "What the task is"
    required: true
  - field: "assets_included"
    description: "List of files/assets being passed"
    required: true
  - field: "next_steps"
    description: "What the receiving agent should do next"
    required: true
  - field: "blockers"
    description: "Any known issues or blockers"
    required: false
output_format: "markdown"
---

# Agent Handoff — {{task_summary}}

## From: {{from_agent}}
## To: {{to_agent}}
## Date: {{date}}

### Task Summary
{{task_summary}}

### Assets Included
{{assets_included}}

### Context & Background
[Provide relevant context the receiving agent needs]

### Next Steps
{{next_steps}}

### Blockers / Known Issues
{{blockers}}

### Definition of Done
[What does successful completion look like?]

### Deadline
[If applicable]
```

---

## Template Metadata Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `template_id` | string | Yes | Unique identifier |
| `name` | string | Yes | Human-readable name |
| `template_type` | string | Yes | document, email, report, handoff, product-brief |
| `fill_in_fields` | array | Yes | Fields that need to be populated when using |
| `output_format` | string | Yes | What format the completed template produces |
| `use_case` | string | Yes | When to use this template |
| `example_output` | string | No | Link to an example of a completed template |

---

## Template Versioning

Templates follow the same versioning rules as all assets, with one addition:

### Template-Asset Relationship
When a template is used to create an asset, the asset records which template version it was created from:

```yaml
# In the asset's metadata
created_from_template:
  template_id: "agent-handoff-template"
  template_version: "V1.0"
```

### Template Update Impact
When a template is updated (new version):
- Existing assets created from the old version are NOT automatically updated
- The Librarian can generate a report: "These assets were created from template V1.0; V2.0 is now current"
- Decision to update old assets is a human/strategy decision, not a Librarian decision

---

## Deduplication Logic

### What is a Duplicate?
Two files with substantially similar content in different locations, where it's ambiguous which is canonical.

### Deduplication Detection
During audits, check for:
1. **Exact duplicates**: Files with identical content (byte-level comparison for binary, text comparison for documents)
2. **Near duplicates**: Files with >80% similar content but different names/locations
3. **Version duplicates**: Same content but one is V2.0-ACTIVE and another is unnamed in a different directory
4. **Stale copies**: Files that were copied for a specific purpose but never cleaned up

### Deduplication Resolution

```
Duplicate detected:
│
├── Are they literally the same file? (byte-identical)
│   ├── YES → Keep the one in the canonical location, delete the other
│   └── NO → Go to "near duplicate" handling
│
├── Is one named properly and one not?
│   ├── YES → The properly-named one is canonical. Archive or delete the other.
│   └── NO → Neither is properly named. Name the better-located one, archive the other.
│
├── Are they both named properly?
│   ├── YES → Which is in the canonical directory?
│   │   ├── One is → That one wins. Archive the other.
│   │   └── Neither or both → Check source-of-truth registry.
│   └── NO → Name one properly, archive the other.
│
└── Are they different versions of the same asset?
    ├── YES → Ensure version numbers are correct, archive the older one
    └── NO → They're actually different assets that need different descriptors
```

### Prevention
The best deduplication is prevention:
- Always check if an asset exists before creating a new one
- Always use the canonical location for edits (never copy-edit-save-elsewhere)
- During handoffs between agents, reference assets by path, don't copy them

---

## Asset Retrieval Patterns

### Pattern 1: By Entity + Type
"Give me the FamliClaw cover image"
→ `assets/by-entity/famli-claw/images/covers/` → find ACTIVE version

### Pattern 2: By Use Case
"I need the email template for cold outreach"
→ `templates/email/` → find ACTIVE version matching "cold outreach"

### Pattern 3: By Registry Lookup
"What's the current version of the GND sales page?"
→ Check source-of-truth registry → get canonical path → return asset

### Pattern 4: By Dependency
"What assets does the Gumroad publish SOP need?"
→ Check SOP's `depends_on` metadata → retrieve each listed asset

### Pattern 5: By Tag Search
"Show me everything tagged 'launch'"
→ Search all asset metadata for `tags` containing "launch"

---

## Asset Library Maintenance

### Weekly (Friday)
- Process inbox/ assets (name, version, file them)
- Check for deployment sync issues (canonical vs deployed versions)
- Verify new assets added this week are properly indexed

### Monthly
- Run deduplication scan
- Check for orphaned sidecar metadata files (metadata without an asset)
- Check for assets without metadata (asset without a sidecar)
- Review template usage (which templates are being used, which aren't)

### Quarterly
- Full asset inventory reconciliation (registry vs filesystem)
- Archive unused assets (not referenced in 180+ days)
- Review and update asset categorization
- Generate asset library statistics
- Check storage usage and identify optimization opportunities

### Asset Library Health Metrics

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| % of assets with complete metadata | >90% | 70-90% | <70% |
| Duplicate assets detected | 0 | 1-5 | >5 |
| Assets without version numbers | 0 | 1-3 | >3 |
| Deployment sync mismatches | 0 | 1-2 | >2 |
| Orphaned metadata files | 0 | 1-3 | >3 |
| Template usage rate (used in last 90 days) | >70% | 40-70% | <40% |
