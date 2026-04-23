# Directory Architecture — Where Everything Lives and Why

The directory structure is the physical map of institutional memory. A well-designed tree makes every asset
self-locating — you can find anything by navigating the tree, even without search. A badly designed tree
hides assets, creates duplicates, and forces everyone to ask "where does this go?"

---

## Table of Contents

1. [Master Directory Tree](#master-directory-tree)
2. [Directory Design Principles](#directory-design-principles)
3. [Top-Level Directory Definitions](#top-level-directory-definitions)
4. [Second-Level Organization Patterns](#second-level-organization-patterns)
5. [README and Index Files](#readme-and-index-files)
6. [Directory Scaffolding Templates](#directory-scaffolding-templates)
7. [Anti-Patterns](#anti-patterns)
8. [Migration: Restructuring an Existing Mess](#migration-restructuring-an-existing-mess)
9. [Growth Scaling Rules](#growth-scaling-rules)

---

## Master Directory Tree

This is the canonical directory structure for the organization. Every file in the system lives
somewhere in this tree.

```
company-root/
│
├── prompts/                          # All reusable prompts
│   ├── _index.md                     # Index: what's in this directory
│   ├── by-entity/                    # Organized by entity/project
│   │   ├── gnd/
│   │   │   ├── gnd-cold-email-prompt-V5.0-ACTIVE.md
│   │   │   ├── gnd-cold-email-prompt-V4.0-ARCHIVED.md
│   │   │   └── gnd-follow-up-prompt-V2.0-ACTIVE.md
│   │   ├── famli-claw/
│   │   │   └── famli-claw-product-desc-prompt-V3.0-ACTIVE.md
│   │   └── agentreach/
│   │       └── agentreach-session-harvest-prompt-V1.0-ACTIVE.md
│   └── by-function/                  # Cross-references by function (symlinks or index)
│       ├── cold-outreach/
│       ├── product-descriptions/
│       ├── social-media/
│       └── internal-operations/
│
├── sops/                             # All standard operating procedures
│   ├── _index.md
│   ├── by-workflow/                  # Organized by workflow domain
│   │   ├── publishing/
│   │   │   ├── gumroad-publish-sop-V2.1-APPROVED.md
│   │   │   ├── kdp-publish-sop-V1.0-ACTIVE.md
│   │   │   └── lulu-publish-sop-V1.0-DRAFT.md
│   │   ├── marketing/
│   │   │   ├── email-campaign-launch-sop-V1.0-ACTIVE.md
│   │   │   └── social-post-sop-V1.0-ACTIVE.md
│   │   ├── product-creation/
│   │   │   ├── ebook-creation-sop-V2.0-APPROVED.md
│   │   │   └── course-creation-sop-V1.0-DRAFT.md
│   │   ├── operations/
│   │   │   ├── agentreach-session-harvest-sop-V1.0-ACTIVE.md
│   │   │   └── weekly-maintenance-sop-V1.0-ACTIVE.md
│   │   └── sales/
│   │       └── outbound-sequence-sop-V1.0-ACTIVE.md
│   └── by-entity/                    # Cross-references by entity
│       ├── gnd/
│       ├── famli-claw/
│       └── agentreach/
│
├── templates/                        # All reusable templates
│   ├── _index.md
│   ├── handoff/
│   │   └── agent-handoff-template-V1.0-ACTIVE.md
│   ├── email/
│   │   ├── cold-outreach-email-template-V2.0-ACTIVE.html
│   │   └── nurture-sequence-email-template-V1.0-ACTIVE.html
│   ├── documents/
│   │   ├── product-brief-template-V1.0-ACTIVE.md
│   │   └── project-kickoff-template-V1.0-ACTIVE.md
│   └── reports/
│       ├── weekly-report-template-V1.0-ACTIVE.md
│       └── audit-report-template-V1.0-ACTIVE.md
│
├── assets/                           # All product files and deliverables
│   ├── _index.md
│   ├── by-entity/
│   │   ├── gnd/
│   │   │   ├── products/
│   │   │   │   ├── ebooks/
│   │   │   │   ├── courses/
│   │   │   │   └── tools/
│   │   │   ├── images/
│   │   │   │   ├── covers/
│   │   │   │   ├── social/
│   │   │   │   └── marketing/
│   │   │   └── documents/
│   │   │       ├── sales-pages/
│   │   │       └── descriptions/
│   │   ├── famli-claw/
│   │   │   ├── products/
│   │   │   ├── images/
│   │   │   └── documents/
│   │   └── agentreach/
│   │       ├── products/
│   │       ├── images/
│   │       └── documents/
│   └── shared/                       # Cross-entity shared assets
│       ├── logos/
│       ├── brand-kit/
│       └── fonts/
│
├── lessons/                          # Lessons learned and failure log
│   ├── _index.md
│   ├── by-date/
│   │   ├── 2025/
│   │   │   ├── 2025-Q1/
│   │   │   │   ├── lesson-2025-01-15-kdp-formatting-error.md
│   │   │   │   └── lesson-2025-02-20-pricing-strategy-miss.md
│   │   │   └── 2025-Q2/
│   │   └── 2026/
│   └── by-category/                  # Cross-references by failure category
│       ├── technical/
│       ├── process/
│       ├── strategy/
│       └── communication/
│
├── skills/                           # All agent skill files
│   ├── _index.md
│   ├── active/
│   │   ├── sales-mastery/
│   │   ├── graphic-design-mastery/
│   │   └── librarian-mastery/
│   └── archived/
│
├── system/                           # Librarian system files
│   ├── _index.md
│   ├── registries/
│   │   ├── source-of-truth-registry-V1.0-ACTIVE.json
│   │   ├── entity-prefix-registry-V1.0-ACTIVE.yaml
│   │   └── status-registry-V1.0-ACTIVE.json
│   ├── changelogs/
│   │   ├── CHANGELOG-2025.md
│   │   └── CHANGELOG-2026.md
│   ├── audits/
│   │   ├── audit-report-2025-W12-maintenance.md
│   │   └── health-scorecard-2025-W12.md
│   ├── configs/
│   │   ├── naming-conventions-config-V1.0-ACTIVE.yaml
│   │   └── lifecycle-rules-config-V1.0-ACTIVE.yaml
│   └── backups/
│       └── snapshots/
│
├── archive/                          # Cold storage for archived assets
│   ├── _index.md
│   ├── by-date-archived/
│   │   └── 2025-Q1/
│   └── by-entity/
│
└── inbox/                            # Unsorted incoming files awaiting processing
    ├── _index.md                     # Contains processing instructions
    └── (files dropped here get processed in next maintenance cycle)
```

---

## Directory Design Principles

### Principle 1: Category First, Then Entity
Top-level directories represent WHAT something is (prompt, SOP, template, asset).
Second-level directories organize by WHO or WHICH entity it belongs to.

Why? Because when you're looking for "a cold email prompt," you think category-first:
"It's a prompt → it's in prompts/ → it's for GND → prompts/by-entity/gnd/"

### Principle 2: Maximum 5 Levels Deep
```
Level 1: company-root/
Level 2: prompts/
Level 3: by-entity/
Level 4: gnd/
Level 5: gnd-cold-email-prompt-V5.0-ACTIVE.md  ← FILE LIVES HERE
```

If you need level 6+, the structure needs flattening or rethinking.

### Principle 3: Every Directory Justifies Its Existence
A directory must contain (or will contain within 30 days) at least 3 items.
If it has fewer than 3 items, the contents should live in the parent directory.
Exception: entity directories (e.g., `famli-claw/`) which exist for organizational clarity even with 1 file.

### Principle 4: Plural for Collections, Singular in Names
- Directory names: `prompts/`, `sops/`, `templates/`, `assets/`, `lessons/`
- File names within: `gnd-cold-email-prompt-V5.0-ACTIVE.md` (singular in the descriptor)

### Principle 5: The Inbox Pattern
The `inbox/` directory is a buffer for unprocessed files. New files land here first. During maintenance,
the Librarian processes inbox items: names them, versions them, and moves them to their canonical location.
The inbox should be empty after every Friday maintenance cycle.

### Principle 6: Cross-Reference, Don't Duplicate
When an asset logically belongs to two categories (e.g., a GND prompt that's also a cold-outreach prompt),
it lives in ONE canonical location and gets cross-referenced from the other:
- Canonical: `prompts/by-entity/gnd/gnd-cold-email-prompt-V5.0-ACTIVE.md`
- Cross-ref: `prompts/by-function/cold-outreach/_index.md` lists it with a path reference

Never copy a file to a second location. That creates version divergence.

---

## Top-Level Directory Definitions

| Directory | Purpose | What Goes Here | What Does NOT Go Here |
|-----------|---------|----------------|----------------------|
| `prompts/` | Reusable prompt text that can be fed to AI agents | Prompt files with metadata | One-off conversation messages |
| `sops/` | Step-by-step procedures for recurring workflows | Process documentation | General knowledge articles |
| `templates/` | Reusable structural formats for outputs | Boilerplate with fill-in sections | Completed documents (those are assets) |
| `assets/` | Final deliverables and product files | Products, images, documents, covers | Drafts and works-in-progress (use DRAFT status) |
| `lessons/` | Post-incident learnings and failure logs | Specific incidents with analysis | General notes or ideas |
| `skills/` | Agent skill files and configurations | SKILL.md files and reference bundles | Human-facing documentation |
| `system/` | Librarian infrastructure files | Registries, configs, changelogs, audits | User-facing content |
| `archive/` | Cold storage for retired/historical assets | Anything moved out of active directories | Active or draft assets |
| `inbox/` | Unsorted incoming files | Anything not yet processed | Anything that's been named and filed |

---

## Second-Level Organization Patterns

### Pattern A: By-Entity (Primary for prompts, assets)
```
prompts/
├── by-entity/
│   ├── gnd/
│   ├── famli-claw/
│   └── agentreach/
└── by-function/    ← cross-reference index
```

### Pattern B: By-Workflow (Primary for SOPs)
```
sops/
├── by-workflow/
│   ├── publishing/
│   ├── marketing/
│   ├── product-creation/
│   └── operations/
└── by-entity/      ← cross-reference index
```

### Pattern C: By-Type (Primary for templates)
```
templates/
├── handoff/
├── email/
├── documents/
└── reports/
```

### Pattern D: By-Date (Primary for lessons, audits)
```
lessons/
├── by-date/
│   └── 2025/
│       ├── 2025-Q1/
│       └── 2025-Q2/
└── by-category/    ← cross-reference index
```

---

## README and Index Files

### Every Directory Gets an Index

Every directory with 3+ files should contain a `_index.md` file that explains:

```markdown
# [Directory Name] — Index

## Purpose
What this directory contains and why.

## Contents
| File | Description | Status | Last Updated |
|------|-------------|--------|-------------|
| file-name-V1.0-ACTIVE.md | Brief description | ACTIVE | 2025-03-21 |
| file-name-V2.0-DRAFT.md  | Brief description | DRAFT  | 2025-03-20 |

## Naming Convention
Files in this directory follow: {entity}-{descriptor}-V{X.Y}-{STATUS}.{ext}

## Maintenance
Last reviewed: 2025-W12
Next review: 2025-W13
```

### The Root README
`company-root/README.md` is the entry point for anyone new to the system. It contains:
- System overview
- How to find things
- How to add new things
- Where to go for help
- Link to naming conventions
- Link to the Librarian's maintenance schedule

---

## Directory Scaffolding Templates

### New Entity Scaffold
When a new product/project entity is created, scaffold these directories:

```bash
# Template for creating a new entity's directory presence
prompts/by-entity/{entity}/
assets/by-entity/{entity}/
  ├── products/
  ├── images/
  └── documents/
sops/by-entity/{entity}/          # cross-ref only
```

### New Workflow Scaffold
When a new workflow type is identified:

```bash
sops/by-workflow/{workflow-name}/
templates/{workflow-relevant-type}/  # if templates are needed
```

---

## Anti-Patterns

| Anti-Pattern | Why It's Bad | Correct Approach |
|-------------|-------------|-----------------|
| `misc/` or `other/` directory | Becomes a junk drawer | Create specific directories or use `inbox/` temporarily |
| Nesting deeper than 5 levels | Files become unfindable | Flatten or restructure |
| Entity-first top level (`gnd/prompts/`, `gnd/sops/`) | Scatters similar assets | Category-first: `prompts/by-entity/gnd/` |
| No `_index.md` files | Nobody knows what's in a directory | Add index files during maintenance |
| Duplicate files in multiple dirs | Version divergence guaranteed | Single canonical location + cross-references |
| Empty directories lingering | Noise and confusion | Remove or scaffold during maintenance |
| Flat directory with 50+ files | Impossible to scan visually | Add subdirectory structure |

---

## Migration: Restructuring an Existing Mess

### Step 1: Inventory
List every existing file with its current location, name, and apparent purpose.

### Step 2: Classify
Assign each file to a top-level category (prompt, SOP, template, asset, lesson, system, archive, unknown).

### Step 3: Rename
Apply naming conventions to each file (see naming-conventions.md).

### Step 4: Place
Move each file to its canonical location in the new tree.

### Step 5: Cross-Reference
Create index files and cross-references.

### Step 6: Verify
Run a full audit to confirm:
- No orphaned files
- No broken cross-references
- All indexes accurate
- Inbox is empty

### Step 7: Document
Create a migration log recording what was moved, renamed, and why.

---

## Growth Scaling Rules

### When to Split a Directory
- More than 20 files in a single directory → add subdirectories
- More than 5 entities → consider archiving inactive entities

### When to Add a New Top-Level Directory
Almost never. The current top-level set (prompts, sops, templates, assets, lessons, skills, system, archive, inbox)
covers virtually all organizational needs. If something truly doesn't fit, discuss before creating a new top-level.
Bad top-level proliferation is worse than slightly imperfect categorization.

### When to Create a New Entity Prefix
When a new product, brand, or project reaches the point of having 3+ dedicated assets. Before that,
use the `org` prefix for organization-wide items.
