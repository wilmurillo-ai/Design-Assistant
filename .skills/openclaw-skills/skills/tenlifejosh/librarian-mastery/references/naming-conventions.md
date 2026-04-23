# Naming Conventions — The Librarian's Foundation

**Read this FIRST for every Librarian task.** Names are the primary interface of the file system. Every downstream
operation — versioning, searching, sorting, filtering, auditing — depends on naming being correct and consistent.
A bad name propagates errors through the entire system.

---

## Table of Contents

1. [Universal Naming Rules](#universal-naming-rules)
2. [File Naming Format](#file-naming-format)
3. [Entity Prefixes](#entity-prefixes)
4. [Version Suffixes](#version-suffixes)
5. [Status Tags in Filenames](#status-tags-in-filenames)
6. [Date Formats](#date-formats)
7. [Folder Naming Rules](#folder-naming-rules)
8. [Slug Rules](#slug-rules)
9. [Collision Avoidance](#collision-avoidance)
10. [Platform Compatibility](#platform-compatibility)
11. [Naming Governance](#naming-governance)
12. [Quick Reference Cheat Sheet](#quick-reference-cheat-sheet)
13. [Naming Decision Tree](#naming-decision-tree)
14. [Common Anti-Patterns](#common-anti-patterns)
15. [Bulk Rename Scripts](#bulk-rename-scripts)

---

## Universal Naming Rules

These rules apply to EVERY file, folder, prompt, SOP, template, and asset in the system.

### Rule 1: Human-First, Machine-Compatible
Names must be immediately understandable to a human AND parsable by scripts.
- **YES**: `GND-cold-email-V3-ACTIVE.md`
- **NO**: `email_v3_final_FINAL_USE-THIS-ONE.md`

### Rule 2: No Spaces, Ever
Spaces break URLs, command-line tools, and many APIs. Use hyphens for word separation.
- **YES**: `famli-claw-product-description-V2.md`
- **NO**: `FamliClaw Product Description v2.md`

### Rule 3: Lowercase Default, Uppercase for Codes Only
Base names are lowercase. Uppercase is reserved for entity codes, status tags, and version markers.
- **YES**: `gnd-cold-email-V3-ACTIVE.md`
- **NO**: `GND-Cold-Email-V3-Active.md`

### Rule 4: Hyphens, Not Underscores
Hyphens are the word separator. Underscores are reserved for structural delimiters between naming segments.
- Structural format: `{entity}_{descriptor}_{version}_{status}.{ext}`
- But within each segment, words are separated by hyphens: `famli-claw_product-description_V3_ACTIVE.md`

**Alternative simplified format** (recommended for most teams): Use hyphens throughout with clear segment patterns:
`famli-claw-product-description-V3-ACTIVE.md`

Choose ONE format and enforce it everywhere. The simplified all-hyphens format is recommended unless the team
has strong tooling reasons for structural delimiters.

### Rule 5: No Special Characters
Allowed characters: `a-z`, `0-9`, `-` (hyphen), `_` (underscore if using structural format), `.` (extension only)
Forbidden: `! @ # $ % ^ & * ( ) + = { } [ ] | \ : " ; ' < > , ? /` and spaces

### Rule 6: Max 80 Characters (Excluding Extension)
Long names truncate in file explorers, break in terminals, and are hard to type. If you need more than 80
characters, the name is doing too much — simplify or restructure.

### Rule 7: The Five-Second Test
A new team member should be able to look at a filename and answer ALL of these in under 5 seconds:
1. What is this thing? (descriptor)
2. What project/entity does it belong to? (entity prefix)
3. Is this the current version? (version + status)

---

## File Naming Format

### Standard Pattern

```
{entity-prefix}-{descriptor}-V{major}.{minor}-{STATUS}.{ext}
```

### Segments Explained

| Segment | Required? | Format | Example |
|---------|-----------|--------|---------|
| `entity-prefix` | Yes | Lowercase slug, 2-20 chars | `gnd`, `famli-claw`, `agentreach` |
| `descriptor` | Yes | Lowercase hyphenated slug | `cold-email`, `product-description`, `onboarding-sop` |
| `V{major}.{minor}` | Yes | V + integer.integer | `V1.0`, `V3.2`, `V12.0` |
| `{STATUS}` | Yes | UPPERCASE status label | `DRAFT`, `ACTIVE`, `APPROVED`, `ARCHIVED`, `DEPRECATED` |
| `.{ext}` | Yes | Standard file extension | `.md`, `.json`, `.docx`, `.png` |

### Examples by Asset Type

| Asset Type | Example Filename |
|------------|-----------------|
| Prompt | `gnd-cold-email-prompt-V5.0-ACTIVE.md` |
| SOP | `gumroad-publish-sop-V2.1-APPROVED.md` |
| Template | `product-handoff-template-V1.0-ACTIVE.md` |
| Product file | `famli-claw-product-description-V3.0-ACTIVE.md` |
| Cover image | `famli-claw-cover-kindle-V2.0-ACTIVE.png` |
| Skill file | `librarian-mastery-skill-V1.0-ACTIVE.md` |
| Lesson learned | `lesson-2025-03-21-gumroad-pricing-error.md` |
| Changelog | `CHANGELOG.md` (special — no version in name, versions are inside) |
| Config/registry | `source-of-truth-registry-V1.0-ACTIVE.json` |
| Audit report | `audit-report-2025-W12-maintenance.md` |

### Simplified Pattern (For Quick Saves)

When an asset is being captured fast (mid-session), use the quick pattern and refine later:

```
{entity}-{descriptor}-V{major}-{STATUS}.{ext}
```

Example: `gnd-cold-email-V5-ACTIVE.md` (minor version omitted for speed, default to .0)

---

## Entity Prefixes

Every asset belongs to a project, product, client, or organizational entity. The entity prefix identifies this.

### Entity Prefix Registry

Maintain a living registry of all entity prefixes:

```yaml
# entity-prefix-registry.yaml
entities:
  - prefix: "gnd"
    full_name: "GND (Gold Name Digital)"
    type: "brand"
    status: "active"
    created: "2025-01-15"
    
  - prefix: "famli-claw"
    full_name: "FamliClaw"
    type: "product"
    status: "active"
    created: "2025-02-01"
    
  - prefix: "agentreach"
    full_name: "AgentReach"
    type: "product"
    status: "active"
    created: "2025-02-15"
    
  - prefix: "librarian"
    full_name: "The Librarian"
    type: "system"
    status: "active"
    created: "2025-03-01"
    
  - prefix: "org"
    full_name: "Organization-wide"
    type: "meta"
    status: "active"
    created: "2025-01-01"
    notes: "Used for assets that span all entities"
```

### Rules for Creating New Prefixes
1. 2-20 characters, lowercase, hyphenated if multi-word
2. Must be unique across the entire organization
3. Register in the entity prefix registry BEFORE first use
4. Once assigned, a prefix NEVER changes (even if the product rebrands — create an alias instead)
5. Use the shortest unambiguous form: `gnd` not `gold-name-digital`

---

## Version Suffixes

### Semantic Versioning for Documents

```
V{MAJOR}.{MINOR}
```

| Version Component | When to Increment | Example |
|-------------------|-------------------|---------|
| **MAJOR** | Significant rewrite, structural change, breaking change to how the asset is used | V1.0 → V2.0 |
| **MINOR** | Small edits, tweaks, fixes, additions that don't change the fundamental asset | V2.0 → V2.1 |

### Version Numbering Rules
1. Start at V1.0 (never V0.x for production assets; V0.x is acceptable for experimental/pre-release)
2. MAJOR versions reset MINOR to .0: V2.3 → V3.0
3. Never skip version numbers: V1.0 → V2.0 is fine. V1.0 → V5.0 is not.
4. The version in the filename ALWAYS matches the version in the file's internal metadata
5. Only ONE file per entity+descriptor combination should have `ACTIVE` or `APPROVED` status at any time

### Version History Tracking
Every asset with version V2.0 or higher should have a version history block in its metadata:

```yaml
version_history:
  - version: "V3.0"
    date: "2025-03-21"
    author: "Opus Agent"
    change: "Complete rewrite of subject line approach based on A/B test results"
  - version: "V2.1"
    date: "2025-03-15"
    author: "Sales Agent"
    change: "Updated CTA from link to calendar booking"
  - version: "V2.0"
    date: "2025-03-01"
    author: "Sales Agent"
    change: "Restructured for new ICP targeting"
  - version: "V1.0"
    date: "2025-02-15"
    author: "Opus Agent"
    change: "Initial creation"
```

---

## Status Tags in Filenames

### Approved Status Labels

| Status | Meaning | In Filename | Color Code |
|--------|---------|-------------|------------|
| `DRAFT` | Work in progress, not ready for use | `-DRAFT` | Yellow |
| `ACTIVE` | Current working version, in production use | `-ACTIVE` | Green |
| `APPROVED` | Reviewed and formally approved for use | `-APPROVED` | Blue |
| `ARCHIVED` | No longer current but preserved for reference | `-ARCHIVED` | Gray |
| `DEPRECATED` | Superseded, should not be used, will be archived | `-DEPRECATED` | Red |

### Status Rules
1. Only ONE version of a given entity+descriptor may be `ACTIVE` or `APPROVED` at a time
2. When a new version is promoted to `ACTIVE`, the old `ACTIVE` version moves to `ARCHIVED`
3. `DEPRECATED` means "stop using this, a replacement exists" — include a pointer to the replacement
4. `ARCHIVED` means "preserved for history, no longer in production"
5. `DRAFT` assets are never served to other agents as authoritative — they're explicitly incomplete
6. Status changes ALWAYS generate a changelog entry

---

## Date Formats

### In Filenames
Use ISO 8601 short format: `YYYY-MM-DD`
- **YES**: `lesson-2025-03-21-pricing-error.md`
- **NO**: `lesson-March-21-2025-pricing-error.md`
- **NO**: `lesson-03-21-25-pricing-error.md`

### In Metadata
Use ISO 8601 full format: `YYYY-MM-DDTHH:MM:SSZ` (UTC) or `YYYY-MM-DD` for date-only fields.

### Week Numbers
For maintenance and audit reports: `YYYY-WXX` format.
- `2025-W12` = Week 12 of 2025

---

## Folder Naming Rules

1. All lowercase
2. Hyphens for word separation (never spaces or underscores)
3. Plural for collections: `prompts/`, `sops/`, `templates/`, `assets/`, `lessons/`
4. Singular for specific items within collections: `prompts/gnd-cold-email-prompt-V5.0-ACTIVE.md`
5. Max 30 characters for folder names
6. Max 5 levels of nesting depth (shallower is better)
7. Every directory with 3+ files gets a `_index.md` or `README.md` explaining what's in it

---

## Slug Rules

A "slug" is a URL-safe, filesystem-safe identifier derived from a human-readable name.

### Slug Generation Algorithm
1. Convert to lowercase
2. Replace spaces with hyphens
3. Remove all characters except `a-z`, `0-9`, and `-`
4. Collapse multiple consecutive hyphens to one
5. Trim leading/trailing hyphens
6. Max 40 characters (truncate at word boundary)

### Examples
| Input | Slug |
|-------|------|
| "GND Cold Email Sequence" | `gnd-cold-email-sequence` |
| "FamliClaw™ Product Description" | `famli-claw-product-description` |
| "How to Publish to Gumroad (Updated!)" | `how-to-publish-to-gumroad` |

---

## Collision Avoidance

### What is a Naming Collision?
Two files with the same effective name in the same scope. This creates ambiguity about which is canonical.

### Prevention Rules
1. The entity-prefix + descriptor combination must be unique within a directory
2. Version suffix differentiates chronological versions of the same asset
3. Status suffix differentiates the lifecycle stage
4. If two genuinely different assets would have the same name, the descriptor needs more specificity:
   - `gnd-email-template` → `gnd-cold-email-template` and `gnd-nurture-email-template`

### Collision Detection
During maintenance audits, scan for:
- Files with identical names in different directories (potential duplicates)
- Files with nearly identical names (potential inconsistent naming)
- Files with same entity+descriptor but different versions both marked `ACTIVE`

---

## Platform Compatibility

### Cross-Platform Safe Characters
These characters are safe across Windows, macOS, Linux, URLs, S3, and Google Drive:
- `a-z`, `0-9`, `-`, `_`, `.`

### Windows-Specific Restrictions
Avoid these reserved names (case-insensitive): `CON`, `PRN`, `AUX`, `NUL`, `COM1`-`COM9`, `LPT1`-`LPT9`

### URL Safety
If filenames might appear in URLs, avoid: `#`, `?`, `&`, `%`, `+`, `=`

### Maximum Path Length
Keep total path (from root) under 200 characters. Windows has a 260-char limit; macOS 1024; but 200 is safe everywhere.

---

## Naming Governance

### Who Names Things?
- **The Librarian** names everything according to these conventions
- **Other agents** may suggest names but the Librarian has final authority
- **Humans** may override names but the Librarian will flag non-compliant names in audits

### Renaming Protocol
1. Never rename a file without updating ALL references to it
2. Log the rename in the changelog: `old-name.md → new-name.md`
3. If other assets reference the old name, update those references
4. If the file is in source-of-truth registry, update the registry entry

### Name Freeze Rule
Once an asset reaches `APPROVED` status, its name (excluding version and status suffixes) is FROZEN.
The entity-prefix and descriptor never change after approval. Only version and status may change.

---

## Quick Reference Cheat Sheet

```
ANATOMY OF A FILENAME:
┌─────────┐ ┌─────────────────┐ ┌────┐ ┌──────┐ ┌───┐
│  entity  │-│   descriptor    │-│ ver │-│status│.│ext│
└─────────┘ └─────────────────┘ └────┘ └──────┘ └───┘
   gnd     -  cold-email-prompt - V5.0 - ACTIVE . md

NAMING RULES AT A GLANCE:
  ✓ lowercase (except STATUS and V-number)
  ✓ hyphens between words
  ✓ no spaces ever
  ✓ no special characters
  ✓ max 80 chars before extension
  ✓ version always present
  ✓ status always present

STATUS LABELS:
  DRAFT → ACTIVE → APPROVED → ARCHIVED
                                    ↑
                            DEPRECATED ─┘

VERSION FORMAT:
  V{major}.{minor}  — e.g., V3.2
  Major = rewrite/breaking change
  Minor = tweak/fix

DATE FORMAT:
  In filenames: YYYY-MM-DD
  In metadata: YYYY-MM-DDTHH:MM:SSZ
  In week refs: YYYY-WXX
```

---

## Naming Decision Tree

```
START: You need to name a file
│
├─ Is it a new asset? ──YES──→ Does an entity prefix exist for the project?
│                                 ├─ YES → Use existing prefix
│                                 └─ NO → Create prefix, register it, then use it
│
├─ Is it a version of an existing asset? ──YES──→ Keep same entity+descriptor
│                                                   └─ Increment version number
│                                                   └─ Update status as needed
│
├─ Is it a lesson/log entry? ──YES──→ Use date-based format:
│                                      lesson-YYYY-MM-DD-{descriptor}.md
│
├─ Is it an audit/report? ──YES──→ Use week-based format:
│                                    audit-report-YYYY-WXX-{descriptor}.md
│
└─ Is it a config/registry file? ──YES──→ Use system prefix:
                                           source-of-truth-registry-V1.0-ACTIVE.json
```

---

## Common Anti-Patterns

| Anti-Pattern | Why It's Bad | Correct Approach |
|-------------|-------------|-----------------|
| `Final_FINAL_v2_USE-THIS.docx` | No version discipline | `project-brief-V3.0-ACTIVE.docx` |
| `Copy of Product Description` | No entity, no version, no status | `famli-claw-product-description-V2.0-ACTIVE.md` |
| `email.md` | Too vague, no entity, no version | `gnd-cold-email-prompt-V1.0-DRAFT.md` |
| `2025-03-21.md` | Date is not a name; what IS this? | `lesson-2025-03-21-gumroad-pricing-error.md` |
| `test.py` / `temp.md` / `new.md` | Temporary names that become permanent | Name it properly from creation or flag for naming in next audit |
| `My awesome prompt!!!.txt` | Spaces, special chars, no version | `gnd-awesome-prompt-V1.0-DRAFT.md` |
| Inconsistent casing: `GND_email.md` and `gnd-Email.md` | Creates sorting chaos and confusion | Enforce lowercase except STATUS and VERSION |

---

## Bulk Rename Scripts

When migrating existing unorganized files into the system, use these patterns:

### Rename Audit First
Before renaming, generate a rename plan:

```
RENAME PLAN — 2025-03-21
=======================================
Current Name                           → Proposed Name                              Status
---------------------------------------  ----------------------------------------  --------
email v3 FINAL.md                      → gnd-cold-email-prompt-V3.0-ACTIVE.md      NEEDS REVIEW
product desc.docx                      → famli-claw-product-desc-V1.0-DRAFT.md     NEEDS REVIEW
Cover.png                              → famli-claw-cover-kindle-V1.0-ACTIVE.png   NEEDS REVIEW
```

### Post-Rename Verification
After bulk rename, verify:
1. No naming collisions
2. All references updated
3. Source-of-truth registry updated
4. Changelog entries created
5. Spot-check 10% of files for correctness
