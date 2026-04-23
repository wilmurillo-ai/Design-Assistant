# Migration & Onboarding — From Chaos to Order, From Zero to Productive

Migration is the process of importing existing unorganized assets into the Librarian system.
Onboarding is the process of teaching new agents and humans how to use the system. Both are
critical — migration because most organizations start with a mess, and onboarding because the
best system in the world fails if nobody knows how to use it.

---

## Table of Contents

1. [Migration Philosophy](#migration-philosophy)
2. [Migration Assessment](#migration-assessment)
3. [The Migration Pipeline](#the-migration-pipeline)
4. [Bulk Rename Workflows](#bulk-rename-workflows)
5. [Directory Restructuring](#directory-restructuring)
6. [Post-Migration Verification](#post-migration-verification)
7. [Agent Onboarding](#agent-onboarding)
8. [Human Onboarding](#human-onboarding)
9. [System Documentation](#system-documentation)
10. [Quick-Reference Cards](#quick-reference-cards)

---

## Migration Philosophy

### Principle 1: Don't Boil the Ocean
Migrate in phases. Start with the most-used, most-important assets. Get them named, versioned, and
filed correctly. Then work outward to less critical assets. A partial migration with high-value
assets properly organized is infinitely better than an incomplete attempt to organize everything at once.

### Principle 2: Preserve Before Organizing
Before renaming or moving ANYTHING, create a complete snapshot of the current state. If migration goes
wrong, you need to be able to restore the original chaos. Chaos is better than data loss.

### Principle 3: One-Way Door Awareness
Renaming files can break references. Moving files can break links. These operations are soft one-way
doors — reversible in theory, painful in practice. Plan renames before executing them.

### Principle 4: Progress Over Perfection
A file that's 80% correctly named and in roughly the right directory is 100x more useful than a
file that's perfectly named but still sitting in the "organize later" pile. Move fast, refine later.

---

## Migration Assessment

### Step 1: Inventory the Current State

Before migrating, create a complete inventory:

```markdown
# Pre-Migration Inventory — [DATE]

## Source Locations
List every place where organizational files currently live:
- [ ] Local directories (which ones?)
- [ ] Google Drive folders
- [ ] Shared drives
- [ ] Email attachments
- [ ] Chat history (prompts that worked but were never saved)
- [ ] Agent memory/context (knowledge that exists only in conversation)
- [ ] External platforms (Gumroad, KDP, social media accounts)

## File Count by Type (Approximate)
| Type | Approximate Count | Current Organization Level |
|------|-------------------|---------------------------|
| Prompts | ? | None / Partial / Good |
| SOPs / Process docs | ? | None / Partial / Good |
| Templates | ? | None / Partial / Good |
| Product files | ? | None / Partial / Good |
| Images / Covers | ? | None / Partial / Good |
| Documents | ? | None / Partial / Good |
| Other | ? | None / Partial / Good |

## Naming Assessment
- Are files consistently named? YES / NO / PARTIALLY
- Do files have version numbers? YES / NO / PARTIALLY
- Do files have status indicators? YES / NO / PARTIALLY
- Are there obvious duplicates? YES / NO / UNKNOWN

## Priority Assessment
Which assets are used most frequently? (These migrate first)
1. ___
2. ___
3. ___
```

### Step 2: Triage into Migration Waves

| Wave | Priority | Contents | Timeline |
|------|----------|----------|----------|
| **Wave 1** | Critical | Most-used prompts, active SOPs, current product files | Day 1 |
| **Wave 2** | High | All remaining active/current assets | Day 2-3 |
| **Wave 3** | Medium | Historical versions, archived assets | Week 1 |
| **Wave 4** | Low | Everything else (old files, uncertain assets) | Week 2+ |

---

## The Migration Pipeline

For each asset being migrated:

```
ASSET IN ORIGINAL STATE
     │
     ▼
  1. IDENTIFY
  What is this? (prompt, SOP, template, asset, lesson, unknown)
  What entity does it belong to?
  Is it current or historical?
     │
     ▼
  2. CLASSIFY
  Assign asset type
  Assign entity prefix (create new prefix if needed)
  Assign category and tags
     │
     ▼
  3. NAME
  Generate compliant filename:
  {entity}-{descriptor}-V{X.Y}-{STATUS}.{ext}
  If unsure about version, start at V1.0
  If unsure about status, use DRAFT
     │
     ▼
  4. VERSION
  Is this the only version? → V1.0
  Are there multiple versions? → Number them chronologically
  Which is current? → That one gets ACTIVE status
     │
     ▼
  5. PLACE
  Move to canonical directory location
  Create directory structure if it doesn't exist
     │
     ▼
  6. METADATA
  Add YAML frontmatter (for text files) or sidecar metadata (for binary)
  Include at minimum: asset_id, entity, version, status, created date, tags
     │
     ▼
  7. REGISTER
  Add entry to source-of-truth registry
  Add to relevant _index.md files
     │
     ▼
  8. LOG
  Record the migration action in the changelog
  Record in migration log (old path → new path)
```

### Migration Log Format

```markdown
# Migration Log — Wave 1 — [DATE]

| # | Original Name | Original Location | New Name | New Location | Type | Notes |
|---|--------------|-------------------|----------|-------------|------|-------|
| 1 | email v3 FINAL.md | /docs/ | gnd-cold-email-prompt-V3.0-ACTIVE.md | prompts/by-entity/gnd/ | prompt | Determined V3 based on content analysis |
| 2 | product desc.docx | /content/ | famli-claw-product-desc-V1.0-ACTIVE.md | prompts/by-entity/famli-claw/ | prompt | Converted from docx to md |
| 3 | Cover.png | /images/ | famli-claw-cover-kindle-V1.0-ACTIVE.png | assets/by-entity/famli-claw/images/covers/ | image | Added metadata sidecar |
| 4 | how to gumroad.txt | /notes/ | gumroad-publish-sop-V1.0-DRAFT.md | sops/by-workflow/publishing/ | sop | Incomplete — needs expansion |
```

---

## Bulk Rename Workflows

### Phase 1: Generate Rename Plan
NEVER rename files directly. First, generate a rename plan and review it.

```markdown
# Rename Plan — [DATE]

## Rules Applied
- Entity prefixes from entity-prefix-registry
- Naming convention: {entity}-{descriptor}-V{X.Y}-{STATUS}.{ext}
- Status assigned based on: content completeness, apparent currency

## Proposed Renames
| Current Name | Proposed Name | Confidence | Notes |
|-------------|--------------|------------|-------|
| email v3 FINAL.md | gnd-cold-email-prompt-V3.0-ACTIVE.md | HIGH | Clear content, obvious version |
| new prompt.md | gnd-unknown-prompt-V1.0-DRAFT.md | LOW | Can't determine purpose from content |
| asdf.txt | SKIP — empty file | N/A | Will be deleted as temp file |

## Items Needing Human Decision
1. `new prompt.md` — Can't determine entity or purpose. Need human clarification.
2. `important.docx` — Appears to be a strategy doc. Is this a template or an asset?

## Estimated Impact
- Files to rename: 23
- Files to skip (already compliant): 5
- Files needing human decision: 2
- Files to delete (temp/empty): 3
```

### Phase 2: Execute Rename Plan
After plan is reviewed and approved:
1. Create backup/snapshot of current state
2. Execute renames in order
3. Verify each rename succeeded
4. Update all cross-references
5. Log all renames in changelog

### Phase 3: Verify
After all renames:
1. Run naming compliance scanner
2. Verify no broken references
3. Verify source-of-truth registry is accurate
4. Spot-check 20% of renamed files

---

## Directory Restructuring

### When Starting From a Flat Mess
Many organizations start with all files in one or two directories. The restructuring process:

```
BEFORE (flat mess):
/files/
├── email v3.md
├── Cover.png
├── how to gumroad.txt
├── product desc.docx
├── old email.md
├── notes.txt
├── template.html
└── ... (50 more files)

AFTER (structured):
company-root/
├── prompts/by-entity/gnd/
│   ├── gnd-cold-email-prompt-V3.0-ACTIVE.md
│   └── gnd-cold-email-prompt-V2.0-ARCHIVED.md
├── sops/by-workflow/publishing/
│   └── gumroad-publish-sop-V1.0-DRAFT.md
├── templates/email/
│   └── cold-outreach-email-template-V1.0-ACTIVE.html
├── assets/by-entity/famli-claw/
│   ├── images/covers/
│   │   └── famli-claw-cover-kindle-V1.0-ACTIVE.png
│   └── documents/
│       └── famli-claw-product-desc-V1.0-ACTIVE.md
├── inbox/
│   └── notes.txt (unclassified — needs human review)
└── system/registries/
    └── source-of-truth-registry-V1.0-ACTIVE.json
```

### Restructuring Steps
1. Create the full directory tree (see directory-architecture.md)
2. Classify each file by type
3. Rename each file according to conventions
4. Move to canonical location
5. Create _index.md files for each directory with 3+ files
6. Create the source-of-truth registry
7. Verify the structure

### Incremental Restructuring
If a full restructuring isn't possible at once:
1. Create the top-level directories
2. Move the most critical assets first (Wave 1)
3. Leave everything else in `inbox/` for processing during maintenance
4. Process 10-20 inbox items per maintenance cycle until inbox is empty

---

## Post-Migration Verification

### Verification Checklist

```markdown
## Post-Migration Verification — [DATE]

### Completeness
- [ ] All Wave 1 (critical) assets migrated
- [ ] All migrated assets have compliant names
- [ ] All migrated assets have version numbers
- [ ] All migrated assets have status labels
- [ ] All migrated assets are in canonical directories
- [ ] Source-of-truth registry contains all migrated assets

### Accuracy
- [ ] Spot-check 20% of files: name matches content
- [ ] Version numbers are historically accurate (V1 is oldest, highest is newest)
- [ ] Status labels are correct (ACTIVE for current, ARCHIVED for old)
- [ ] Entity prefixes match the entity-prefix registry

### Integrity
- [ ] No files were lost during migration (compare count: before vs after)
- [ ] No duplicate files created
- [ ] Original backup/snapshot is preserved
- [ ] Migration log is complete

### System Health
- [ ] Source-of-truth registry sync check passes
- [ ] Naming compliance scanner returns 0 violations
- [ ] All _index.md files are populated
- [ ] All cross-references are accurate
```

---

## Agent Onboarding

### How Agents Learn the System

When a new agent joins the organization (or an existing agent gets upgraded with Librarian awareness):

#### Level 1: Awareness (Required for ALL Agents)
Every agent must know:
1. **Where to find things**: The directory structure and how to navigate it
2. **Where to put things**: Files go in `inbox/` if unsure; the Librarian processes them
3. **How to ask for things**: Request by asset_id, entity+function, or description
4. **The naming convention exists**: Don't create files without names; if you must, put them in `inbox/`
5. **Version awareness**: Always check which version is current before using an asset

#### Level 2: Participation (Required for Agents That Create/Modify Assets)
Agents that create content, modify files, or execute workflows must also know:
1. **How to name files**: The full naming convention (or put in `inbox/` for Librarian to name)
2. **How to version**: When to increment major vs minor
3. **How to status**: When to use DRAFT vs ACTIVE
4. **How to log lessons**: When something goes wrong, capture it immediately
5. **Where to find SOPs**: Before starting a workflow, check if an SOP exists

#### Level 3: Mastery (The Librarian Agent)
The Librarian agent knows everything in this skill system and operates the full maintenance cycle.

### Agent Quick-Start Message

When onboarding a new agent, send this briefing:

```markdown
## Welcome to the Organizational Memory System

### The 5 Things You Need to Know:

1. **Everything has a home.** Prompts → prompts/. SOPs → sops/. Templates → templates/.
   Assets → assets/. If you're not sure → inbox/.

2. **Everything has a name.** Format: entity-descriptor-V{X.Y}-STATUS.ext
   Example: gnd-cold-email-prompt-V5.0-ACTIVE.md

3. **One version is current.** Check the source-of-truth registry if you're unsure
   which version to use. Look for ACTIVE or APPROVED status.

4. **Don't duplicate. Reference.** If you need a file, reference it by path.
   Don't copy it to a new location. Copies create version conflicts.

5. **When something goes wrong, log it.** Put a quick note in lessons/
   or tell the Librarian. We turn every mistake into a prevention rule.

### Need to Find Something?
- Ask the Librarian: "Where is the current [entity] [descriptor]?"
- Browse: prompts/, sops/, templates/, assets/
- Registry: system/registries/source-of-truth-registry

### Need to Save Something?
- Put it in inbox/ with a descriptive filename
- The Librarian will name it, version it, and file it during Friday maintenance
- Or, if you know the conventions, name and file it yourself
```

---

## Human Onboarding

### For Humans Who Will Use the System

```markdown
## Your Organization's Memory System — Quick Guide

### What Is This?
An organized system where every prompt, process, template, product file, and lesson learned is:
- Named consistently (so you can find it)
- Versioned (so you know which is current)
- Filed in one place (so there's no confusion)

### How to Find Things
1. **Browse by category:** prompts/, sops/, templates/, assets/
2. **Browse by project:** Inside each category, look under by-entity/{project-name}/
3. **Ask the Librarian agent:** "Where is the current [thing I need]?"
4. **Check the registry:** system/registries/source-of-truth-registry

### How to Add Things
Drop files in the inbox/ folder. The Librarian will:
- Give it a proper name
- Assign a version number
- File it in the right place
- Add it to the registry

### Status Labels — What They Mean
- 🟡 DRAFT = Work in progress, don't use yet
- 🟢 ACTIVE = Current version, safe to use
- 🔵 APPROVED = Reviewed and signed off
- ⚪ ARCHIVED = Old version, kept for reference
- 🔴 DEPRECATED = Being phased out, don't use

### Friday Maintenance
Every Friday, the Librarian:
- Processes the inbox
- Checks everything is organized
- Updates the registry
- Generates a health report
```

---

## System Documentation

### System Documentation Artifacts to Create

| Document | Purpose | Location | Audience |
|----------|---------|----------|----------|
| `README.md` | System overview and quick-start | `company-root/` | Everyone |
| `NAMING-GUIDE.md` | Naming convention reference | `system/docs/` | Agents and humans |
| `DIRECTORY-MAP.md` | Full directory tree with explanations | `system/docs/` | Everyone |
| `STATUS-GUIDE.md` | Status labels and lifecycle explanation | `system/docs/` | Everyone |
| `MAINTENANCE-SCHEDULE.md` | Maintenance calendar and checklists | `system/docs/` | Librarian |
| `ENTITY-REGISTRY.md` | All entity prefixes and their meanings | `system/docs/` | Everyone |
| `SOP-INDEX.md` | Master index of all SOPs | `sops/` | Agents |
| `PROMPT-INDEX.md` | Master index of all prompts | `prompts/` | Agents |

### Documentation Maintenance
System documentation is maintained alongside the assets it describes:
- Update `README.md` when the system structure changes
- Update guides when conventions change
- Review all documentation quarterly

---

## Quick-Reference Cards

### The Librarian Quick-Reference Card

```
╔══════════════════════════════════════════════════════════╗
║           THE LIBRARIAN — QUICK REFERENCE                ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  NAMING:  entity-descriptor-V{X.Y}-STATUS.ext            ║
║  EXAMPLE: gnd-cold-email-prompt-V5.0-ACTIVE.md           ║
║                                                          ║
║  STATUS:  DRAFT → ACTIVE → APPROVED → ARCHIVED           ║
║                                      ↑                    ║
║                            DEPRECATED─┘                   ║
║                                                          ║
║  VERSION: V{major}.{minor}                                ║
║           Major = rewrite  |  Minor = tweak               ║
║                                                          ║
║  FIND:    prompts/ | sops/ | templates/ | assets/         ║
║  SAVE:    inbox/ (Librarian processes Fridays)            ║
║  TRUTH:   system/registries/source-of-truth-registry      ║
║                                                          ║
║  RULE #1: Nothing useful gets deleted                     ║
║  RULE #2: One source of truth per asset                   ║
║  RULE #3: Name it, version it, status it, file it         ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```

### Friday Maintenance Quick Card

```
╔══════════════════════════════════════════════════════════╗
║         FRIDAY MAINTENANCE — CHECKLIST                    ║
╠══════════════════════════════════════════════════════════╣
║                                                          ║
║  □ Process inbox/ (name, version, file everything)        ║
║  □ Naming compliance scan (fix violations)                ║
║  □ Version/status check (no dual-active, no stale)        ║
║  □ Registry sync (registry matches filesystem)            ║
║  □ Lessons check (pipeline moving, actions on track)      ║
║  □ Update indexes (_index.md files)                       ║
║  □ Generate health scorecard                              ║
║  □ Log maintenance completion                             ║
║                                                          ║
║  Monthly (1st Friday): + dedup + dependency + age check   ║
║  Quarterly (1st of Q):  + full inventory + archive review ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
```
