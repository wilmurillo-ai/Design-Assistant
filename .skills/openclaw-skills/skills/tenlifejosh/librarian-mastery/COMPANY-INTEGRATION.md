# COMPANY-INTEGRATION.md — Librarian Mastery
## Bridge: Ten Life Creatives ↔ librarian-mastery Skill
### Created: 2026-03-21 | Owner: Librarian | Version: 1.0

---

## Purpose

This file bridges the Librarian's role charter (`company/LIBRARIAN-SYSTEM.md`) to the 14 reference domains in the `librarian-mastery` skill. When the Librarian receives a task, this document tells it exactly where things live, what naming rules apply, and what to do first.

---

## 1. Role Mapping — Charter Areas to the 14 Reference Files

The `references/` folder contains 14 domain files. Each maps to one or more of Librarian's 16 managed categories:

| Reference File | Charter Categories Covered |
|---|---|
| `version-control.md` | Version Logs, all document versioning across 16 categories |
| `naming-conventions.md` | All 16 categories — file naming governs everything |
| `directory-architecture.md` | Source of Truth locations for all 16 categories |
| `source-of-truth.md` | Governs which file is canonical when duplicates exist |
| `prompt-library.md` | Prompt Library (Category 6) |
| `sop-library.md` | SOPs (Category 4) |
| `asset-archive.md` | Approved Brand Assets (8), Design Systems (9), Templates (7) |
| `status-lifecycle.md` | All 16 categories — Draft/Active/Approved/Archived/Deprecated |
| `lessons-learned.md` | Lessons Learned (Category 15) |
| `knowledge-graph.md` | Cross-category relationships, cross-agent dependencies |
| `maintenance-audit.md` | Monthly Librarian Audit (all 16 categories) |
| `archive-deletion.md` | Archived Projects (13), Deprecated Systems (16) |
| `migration-onboarding.md` | New agent onboarding, system migrations |

---

## 2. Our Specific Directory Structure

Where things actually live at Ten Life Creatives:

```
/workspace-main/
├── MEMORY.md                    # Hutch's long-term memory (KEEP UNDER 18KB)
├── AGENTS.md                    # Workspace operating rules
├── SOUL.md                      # Hutch's identity
├── USER.md                      # About Joshua (J)
├── TOOLS.md                     # Environment-specific tool notes
├── IDENTITY.md                  # COO identity definition
│
├── company/                     # Operating system
│   ├── INDEX.md                 # Master document directory
│   ├── CONSTITUTION.md          # Governing law (Category 1)
│   ├── ORG-CHART.md             # All 14 agent roles (Category 2)
│   ├── LIBRARIAN-SYSTEM.md      # Librarian charter (Category 2)
│   ├── roles/                   # Agent role charters (Category 3)
│   ├── SOPs/                    # Standard operating procedures (Category 4)
│   ├── library/
│   │   ├── prompts/             # Approved prompt library (Category 6)
│   │   ├── brand/               # Brand assets (Category 8)
│   │   ├── design/              # Design systems (Category 9)
│   │   ├── offers/              # Current offers (Category 10)
│   │   ├── priorities/          # Current priorities (Category 11)
│   │   ├── projects/
│   │   │   ├── active/          # Active project briefs (Category 12)
│   │   │   └── archived/        # Completed projects (Category 13)
│   │   ├── qa-logs/             # QA checklists (Category 14)
│   │   ├── lessons/             # Lessons learned (Category 15)
│   │   └── deprecated/          # Retired systems (Category 16)
│   └── templates/               # Output templates (Category 7)
│
├── skills/                      # All installed agent skills
│   ├── architect-engineer/
│   ├── sentinel-qa/
│   ├── guardian-devops/
│   ├── navigator-pm/
│   ├── scout-growth/
│   ├── scribe-docs/
│   ├── graphic-design-mastery/
│   ├── sales-mastery/
│   ├── steward-ops/
│   └── librarian-mastery/       # This skill
│
├── projects/
│   ├── revenue/
│   │   └── products/            # All built products (KDP, Gumroad, Etsy, Stripe)
│   ├── content/                 # Content pipeline
│   │   ├── librarian-mastery/   # Source package (installation origin)
│   │   └── prayful-tiktok/      # TikTok video pipeline
│   ├── sales/                   # Closer briefs
│   ├── ops/                     # Daily briefings
│   ├── gnd/                     # Good Neighbor Design
│   ├── myfirstjob/              # MyFirstJob platform
│   ├── prayful/                 # Prayful.ai
│   ├── vail/                    # Vail essay
│   └── agentreach/              # AgentReach open source tool
│
├── memory/                      # Daily session logs
│   ├── YYYY-MM-DD.md            # Daily raw logs (one per day)
│   ├── archive/                 # Historical memory (pre-month)
│   │   └── pre-march-2026.md    # Archived Feb 2026 and earlier entries
│   └── heartbeat-state.json     # Heartbeat check tracking
│
├── autoimprove/                 # AutoImprove self-improvement loops
│   ├── baselines/               # Active prompt baselines (PRIMARY source of truth for prompts)
│   ├── experiments/             # A/B tests in flight
│   └── proposals/               # Pending improvements awaiting J approval
│
├── leads/gnd/                   # GND lead data + prospecting scripts
├── systems/                     # Proprietary internal systems (AgentMemory, etc.)
└── tools/                       # Utility scripts
```

---

## 3. Naming Conventions

Following the `references/naming-conventions.md` domain, here are TLC-specific rules:

### General
- **Format:** `kebab-case` for all files and directories
- **No spaces, no underscores** (except legacy scripts: `nimble_prospect.py`, `batch_dated.py`)
- **No CamelCase** for files (reserved for class names in code only)

### Date-Prefixed Files (use when order/history matters)
```
YYYY-MM-DD.md          # Daily memory logs: 2026-03-21.md
YYYY-MM-DD-topic.md    # Dated topic files: 2026-03-21-audit-report.md
```

### Version Suffixes (for archived versions)
```
filename-v1.md         # Archived version 1
filename-v1.1.md       # Archived minor version
filename-v2.0.md       # Major version archive
```

### Company Document Naming Patterns
```
UPPER-KEBAB.md         # Company operating docs (CONSTITUTION.md, ORG-CHART.md)
SKILL.md               # Always uppercase in skill packages
COMPANY-INTEGRATION.md # Always uppercase in skill packages
lower-kebab.md         # References, daily files, project files
```

### Product Files
```
projects/revenue/products/[product-slug]/
  interior.pdf
  cover-full-wrap.pdf
  build_journal.py       (exception: legacy scripts use underscores)
```

---

## 4. Version Control Rules

Following `references/version-control.md`:

### When to Version (create archived copy)
- Any `company/` document receiving major revision
- Any `autoimprove/baselines/` prompt being superseded
- Any SOP being replaced
- Any skill SKILL.md receiving significant update

### When to Overwrite (no archive needed)
- Daily memory files (`memory/YYYY-MM-DD.md`) — append-only, no versions
- `MEMORY.md` — curated long-term memory, edit in place (but archive old sections to `memory/archive/`)
- Heartbeat state JSON — ephemeral operational state
- Build scripts / utility tools — track in git, not manual versioning

### Version Number Logic
- `v1.0 → v1.1` — minor edit, wording update, small addition
- `v1.x → v2.0` — structural change, major rewrite, new sections

### Archive Location Pattern
```
company/[category]/archived/[filename]-v[N].md
```

---

## 5. Prompt Library Location

**Primary location:** `autoimprove/baselines/`

This is where our **active, approved prompts** live. These are the source of truth for every AutoImprove loop:

| Loop | Baseline File | Schedule |
|---|---|---|
| Agent SOUL.md | `autoimprove/baselines/soul-baseline.md` | Nightly 2 AM |
| GND Email | `autoimprove/baselines/gnd-email-baseline.md` | Tuesdays 2 AM |
| Prayful Content | `autoimprove/baselines/prayful-content-baseline.md` | Wednesdays 2 AM |
| MFJ Curriculum | `autoimprove/baselines/mfj-curriculum-baseline.md` | Thursdays 2 AM |
| Agent Briefs | `autoimprove/baselines/agent-briefs-baseline.md` | Saturdays 2 AM |
| Revenue System | `autoimprove/baselines/revenue-baseline.md` | Sundays 11 PM |

**Secondary (future):** `company/library/prompts/` — for formally approved, multi-agent prompts.

**Librarian's prompt duties:**
- Ensure `autoimprove/baselines/` files match current approved versions
- When J says "apply [loop]", confirm the baseline is updated after apply
- Flag any baselines that haven't been reviewed in 90+ days
- Prevent duplicate prompts (same function, different file)

---

## 6. Memory Maintenance

### The Problem
`MEMORY.md` is Hutch's long-term curated memory. The startup system truncates at **~18KB**. The file is currently **24KB** — meaning **~26% is cut off at every session start**. This is a critical issue: Hutch wakes up without the last quarter of his own memory.

### The Rule
**MEMORY.md must stay under 18KB.** This is a hard constraint.

### What MEMORY.md Contains (keep these)
- Identity section
- Key Milestones (most recent only — archive old dated entries)
- Active Projects (current status only)
- Technical Notes (evergreen)
- Preferences & Patterns (evergreen)
- TODO section

### What to Archive (move to `memory/archive/`)
- Dated session entries older than the current rolling 30 days
- Completed build sessions (MFJ rebuild, Prayful sprint, etc.) — done and not actionable
- Redundant content duplicated elsewhere (credentials → `.secrets/`, cron IDs → `cron/`)
- Full detail entries where a 1-2 line summary suffices

### Archive Destination
```
memory/archive/pre-march-2026.md    # Feb 2026 and earlier entries
memory/archive/[month]-[year].md    # Rolling monthly archives going forward
```

### Librarian's Monthly Maintenance Checklist (MEMORY.md)
1. Check `wc -c MEMORY.md` — if over 16KB, begin pruning
2. Move completed/historical dated entries to archive
3. Compress active project entries to 2-3 lines each
4. Remove cron IDs (they live in `~/.openclaw/cron/` — not needed in MEMORY.md)
5. Remove API keys / credentials (they live in `.secrets/` — never in MEMORY.md)
6. Verify final size under 18KB

---

## 7. Priority First Task — MEMORY.md Maintenance

**MEMORY.md is truncating.** This is Librarian's highest-priority first action.

Current state: **24,796 bytes** (target: under 18,000 bytes, ideally under 16,000).

Steps:
1. Read `MEMORY.md` in full
2. Identify all February 2026 dated entries and completed build sessions
3. Move them to `memory/archive/pre-march-2026.md`
4. Keep in MEMORY.md: March 2026+ entries, evergreen sections (Identity, Active Projects, Technical Notes, Preferences)
5. Compress verbose active project entries to essential status only
6. Verify `wc -c MEMORY.md` is under 18,000 bytes
7. Report size before/after to Hutch

**This is already done as part of the librarian-mastery installation.** See the archive at `memory/archive/pre-march-2026.md`.

---

## Quick Reference — Librarian's Frequent Lookups

| Question | Answer |
|---|---|
| Where is the current MEMORY.md? | `/workspace-main/MEMORY.md` |
| Where are archived memory entries? | `/workspace-main/memory/archive/` |
| Where are daily session logs? | `/workspace-main/memory/YYYY-MM-DD.md` |
| Where are active prompts? | `/workspace-main/autoimprove/baselines/` |
| Where are company SOPs? | `/workspace-main/company/SOPs/` |
| Where are installed skills? | `/workspace-main/skills/` |
| Where is the company index? | `/workspace-main/company/INDEX.md` |
| Where are built products? | `/workspace-main/projects/revenue/products/` |
| Where are agent role charters? | `/workspace-main/company/roles/` |
| What's the approved model? | `anthropic/claude-sonnet-4-6` |
| What's the primary comms channel? | Telegram (J = @tenlifejosh) |

---

*Last updated: 2026-03-21 | Version 1.0 | Owner: Librarian — Governed by Hutch (COO)*
