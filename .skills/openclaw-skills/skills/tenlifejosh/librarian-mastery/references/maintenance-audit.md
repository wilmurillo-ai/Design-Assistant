# Maintenance & Audit — The Weekly Discipline That Keeps Everything Alive

An organizational memory system that isn't maintained decays into chaos within weeks. Files accumulate
without names. Versions diverge. Status becomes ambiguous. Cross-references break. The Librarian's
weekly maintenance routine is the single most important recurring process in the entire system — it's
what turns a filing system into a living institutional brain.

---

## Table of Contents

1. [Maintenance Philosophy](#maintenance-philosophy)
2. [Friday Weekly Maintenance Routine](#friday-weekly-maintenance-routine)
3. [Monthly Deep Audit](#monthly-deep-audit)
4. [Quarterly Archive Review](#quarterly-archive-review)
5. [Health Scorecard](#health-scorecard)
6. [Automated Maintenance Scripts](#automated-maintenance-scripts)
7. [Maintenance Log Format](#maintenance-log-format)
8. [Escalation Procedures](#escalation-procedures)

---

## Maintenance Philosophy

### Why Friday?
Friday is maintenance day because:
- The week's work is complete — all new assets from the week are ready to process
- Weekend provides a natural break — entering Monday with a clean system
- Creates a reliable rhythm that agents and humans can depend on

### The Three Maintenance Modes

| Mode | Frequency | Duration | Scope |
|------|-----------|----------|-------|
| **Weekly** | Every Friday | 30-60 minutes | Inbox processing, naming check, registry sync |
| **Monthly** | First Friday of month | 2-3 hours | Deep audit, deduplication, dependency validation |
| **Quarterly** | First Friday of quarter | Half-day | Full inventory, archive review, health report |

### Maintenance is Never Optional
Even if "nothing happened this week," the Friday check runs. Entropy is invisible until it's catastrophic.
A quick scan confirming everything is clean takes 10 minutes and prevents weeks of cleanup later.

---

## Friday Weekly Maintenance Routine

### Pre-Flight (5 minutes)
```
□ Open the previous week's maintenance log
□ Check if any follow-up items from last week are still open
□ Note today's date for new log entry
□ Open the source-of-truth registry
```

### Phase 1: Inbox Processing (10-15 minutes)
```
□ Check inbox/ directory for unprocessed files
□ For each file in inbox/:
  □ Determine asset type (prompt, SOP, template, asset, lesson)
  □ Apply naming convention (see naming-conventions.md)
  □ Assign version (V1.0 for new, appropriate increment for updates)
  □ Assign status (DRAFT or ACTIVE based on completeness)
  □ Move to canonical directory location
  □ Create metadata (frontmatter or sidecar file)
  □ Add to source-of-truth registry
  □ Add to master changelog
□ Verify inbox/ is empty when done
```

### Phase 2: Naming Compliance Check (5-10 minutes)
```
□ Scan all directories for files that violate naming conventions:
  □ Files with spaces in names
  □ Files without version numbers
  □ Files without status tags
  □ Files with inconsistent casing
  □ Files with special characters
  □ Files without entity prefixes
□ Fix or flag each violation
□ Log any violations in maintenance report
```

### Phase 3: Version & Status Verification (5-10 minutes)
```
□ Check for dual-active conflicts (two versions of same asset both ACTIVE)
□ Check for DEPRECATED assets past their 30-day grace period → archive them
□ Check for DRAFT assets older than 14 days → flag for review
□ Verify that the version in each filename matches its internal metadata
□ Verify that the status in each filename matches the registry status
```

### Phase 4: Registry Synchronization (5-10 minutes)
```
□ Compare source-of-truth registry against filesystem
  □ Any ghost entries? (in registry, not on disk)
  □ Any orphan files? (on disk, not in registry)
  □ Any path mismatches? (registry path ≠ actual path)
□ Fix all discrepancies
□ Update registry timestamp and counts
```

### Phase 5: Lessons & Actions Check (5 minutes)
```
□ Review any lessons logged this week
  □ Has each lesson progressed through the Failure-to-Rule pipeline?
  □ Are any corrective actions overdue?
□ Check pattern database — any new pattern matches this week?
□ Verify all corrective actions due this week are completed
```

### Phase 6: Index Updates (5 minutes)
```
□ Regenerate _index.md files for any directories that changed this week
□ Update the prompt library index if new prompts were added
□ Update the SOP library index if new SOPs were added
□ Update the template library index if new templates were added
```

### Phase 7: Health Scorecard & Log (5 minutes)
```
□ Generate weekly health scorecard (see format below)
□ Write maintenance log entry
□ Note any items requiring human attention
□ Note any items carried forward to next week
□ Save maintenance log to system/audits/
```

### Post-Flight
```
□ Confirm inbox/ is empty
□ Confirm no critical issues remain unresolved
□ Set reminder for next Friday maintenance
□ If monthly or quarterly maintenance is due, add those items to next week's agenda
```

---

## Monthly Deep Audit

Run on the first Friday of each month, IN ADDITION to the weekly routine.

### Phase M1: Full Deduplication Scan
```
□ Scan all directories for potential duplicates:
  □ Exact duplicates (byte-identical files in different locations)
  □ Near duplicates (>80% similar content)
  □ Version duplicates (same content, different naming)
□ Resolve each duplicate (keep canonical, archive other)
□ Log all deduplication actions
```

### Phase M2: Dependency Validation
```
□ For each SOP in ACTIVE/APPROVED status:
  □ Verify all referenced prompts exist and are current
  □ Verify all referenced templates exist and are current
  □ Verify all external tool references are still valid
  □ Flag any broken dependencies
□ For each prompt in ACTIVE/APPROVED status:
  □ Verify all listed dependents still exist
  □ Verify no undeclared dependents exist
```

### Phase M3: Age and Staleness Check
```
□ List all ACTIVE assets last modified >90 days ago
  □ Flag for freshness review (is the content still current?)
□ List all DRAFT assets >30 days old
  □ Decide: promote, update, or abandon each
□ List all DEPRECATED assets past 30-day grace period
  □ Archive them
```

### Phase M4: Cross-Reference Integrity
```
□ Verify all cross-reference _index.md files are accurate
□ Verify all by-function/ and by-entity/ cross-reference directories are current
□ Check knowledge graph for broken links
□ Rebuild any corrupted index files
```

### Phase M5: Monthly Health Report
```
□ Generate comprehensive monthly health report including:
  - Total assets by type, entity, and status
  - Changes this month (created, updated, archived, deprecated)
  - Compliance metrics (naming, versioning, metadata completeness)
  - Open issues and corrective actions
  - Lessons learned summary
  - Pattern trends
  - Recommendations for improvement
```

---

## Quarterly Archive Review

Run on the first Friday of each quarter, IN ADDITION to monthly and weekly routines.

### Phase Q1: Full Asset Inventory
```
□ Complete filesystem inventory: every file, every directory
□ Complete registry inventory: every entry
□ Full reconciliation: identify all discrepancies
□ Resolve every discrepancy
```

### Phase Q2: Archive Review
```
□ Review all ARCHIVED assets:
  □ Is the archive organized? (by date, by entity)
  □ Are archived assets still accessible if needed?
  □ Is any archived asset being referenced by active assets? (error if so)
  □ Are there archives so old they could be cold-stored?
□ Review archive storage usage
□ Optimize storage if needed
```

### Phase Q3: Taxonomy Review
```
□ Review the categorization taxonomy:
  □ Are all categories still relevant?
  □ Are new categories needed?
  □ Should any categories be merged?
□ Review entity prefix registry:
  □ Any new entities to register?
  □ Any entities to retire?
□ Review tag taxonomy:
  □ Consolidate synonymous tags
  □ Remove unused tags
  □ Add new tags as needed
```

### Phase Q4: System Health Assessment
```
□ Generate quarterly system health report:
  - Quarter-over-quarter trend analysis
  - Growth metrics (new assets, new entities)
  - Maintenance efficiency (time spent, issues found)
  - Failure-to-Rule pipeline effectiveness
  - Recommendations for system improvements
  - Projected scaling needs
```

---

## Health Scorecard

### Weekly Health Scorecard Format

```markdown
# Librarian Health Scorecard — 2025-W12

## Summary
| Metric | Score | Status |
|--------|-------|--------|
| Overall System Health | 94/100 | 🟢 Healthy |
| Naming Compliance | 98% | 🟢 |
| Registry Sync Accuracy | 100% | 🟢 |
| Version Integrity | 96% | 🟢 |
| Status Accuracy | 100% | 🟢 |
| Inbox Processed | Yes | 🟢 |
| Open Corrective Actions | 2 | 🟡 |
| Stale Drafts (>14 days) | 1 | 🟡 |

## Items Requiring Attention
1. [YELLOW] 2 corrective actions from lesson-2025-03-14 still pending
2. [YELLOW] agentreach-session-harvest-prompt stuck in DRAFT since 2025-03-05

## Changes This Week
- New assets: 3 (1 prompt, 1 SOP update, 1 product image)
- Archived: 1 (gnd-cold-email-prompt-V4.0)
- Deprecated: 0
- Lessons logged: 1

## Inbox Status
- Files processed: 2
- Files remaining: 0

## Maintenance Duration
- Start: 14:00
- End: 14:42
- Duration: 42 minutes

## Next Week Focus
- Complete pending corrective actions
- Review stale draft: agentreach-session-harvest-prompt
- Monthly deep audit due (first Friday of April)
```

### Scoring System

```
SCORING RUBRIC:
100 = Perfect — no issues found
95-99 = Healthy — minor issues, all manageable
85-94 = Good — some attention needed
70-84 = Warning — significant issues requiring prompt action
<70 = Critical — system integrity at risk, immediate action required

COMPONENT WEIGHTS:
- Registry Sync Accuracy: 25%
- Naming Compliance: 20%
- Version Integrity: 20%
- Status Accuracy: 15%
- Inbox Clearance: 10%
- Corrective Actions: 10%
```

---

## Automated Maintenance Scripts

### Naming Compliance Scanner
```
ALGORITHM: naming_compliance_scan
FOR each file in [prompts/, sops/, templates/, assets/, lessons/]:
  CHECK: contains entity prefix? → flag if missing
  CHECK: contains version number (V{X}.{Y})? → flag if missing
  CHECK: contains status tag (DRAFT|ACTIVE|APPROVED|ARCHIVED|DEPRECATED)? → flag if missing
  CHECK: no spaces in filename? → flag if spaces found
  CHECK: no special characters? → flag if found
  CHECK: all lowercase except STATUS and VERSION? → flag if violation
  CHECK: length < 80 chars before extension? → flag if too long
RETURN: list of violations with suggested fixes
```

### Registry Sync Check
```
ALGORITHM: registry_sync_check
FOR each entry in source-of-truth-registry:
  CHECK: file exists at canonical_path? → flag as "ghost entry" if missing
  CHECK: filename status matches registry status? → flag as "status mismatch" if different
  CHECK: filename version matches registry version? → flag as "version mismatch" if different
FOR each file in filesystem (excluding archive/ and inbox/):
  CHECK: file has corresponding registry entry? → flag as "orphan file" if missing
RETURN: list of discrepancies with severity ratings
```

### Stale Asset Detector
```
ALGORITHM: stale_asset_detector
FOR each ACTIVE or APPROVED asset:
  CHECK: last_modified > 90 days ago? → flag as "needs freshness review"
FOR each DRAFT asset:
  CHECK: created > 14 days ago? → flag as "stale draft"
FOR each DEPRECATED asset:
  CHECK: deprecated_date > 30 days ago? → flag as "ready for archive"
RETURN: list of stale assets with recommended actions
```

### Dependency Graph Validator
```
ALGORITHM: dependency_validator
FOR each SOP with depends_on_prompts:
  FOR each referenced prompt:
    CHECK: prompt exists and is ACTIVE? → flag if missing or not ACTIVE
FOR each SOP with depends_on_templates:
  FOR each referenced template:
    CHECK: template exists and is ACTIVE? → flag if missing or not ACTIVE
FOR each asset with dependents:
  FOR each listed dependent:
    CHECK: dependent exists? → flag if missing
    CHECK: dependent actually references this asset? → flag if reference is broken
RETURN: list of broken dependencies with suggested fixes
```

---

## Maintenance Log Format

```markdown
# Maintenance Log — 2025-03-21 (Week 12)

## Maintenance Type: Weekly
## Performed by: Librarian Agent
## Duration: 42 minutes (14:00 - 14:42)

## Summary
| Phase | Items Processed | Issues Found | Issues Resolved |
|-------|----------------|--------------|-----------------|
| Inbox Processing | 2 files | 0 | 0 |
| Naming Check | 47 files scanned | 1 violation | 1 fixed |
| Version/Status | 47 entries checked | 0 conflicts | 0 |
| Registry Sync | 47 entries vs filesystem | 0 discrepancies | 0 |
| Lessons Check | 1 new lesson | 0 overdue actions | 0 |
| Index Updates | 2 indexes updated | 0 | 0 |

## Detailed Actions
1. **Inbox**: Processed `gnd-follow-up-email-V1.md` → renamed to 
   `gnd-follow-up-email-prompt-V1.0-DRAFT.md`, filed in prompts/by-entity/gnd/
2. **Inbox**: Processed `cover-update.png` → renamed to 
   `famli-claw-cover-kindle-V3.0-DRAFT.png`, filed in assets/by-entity/famli-claw/images/covers/
3. **Naming**: Fixed `gnd-email V2.md` → `gnd-nurture-email-prompt-V2.0-ACTIVE.md` (removed space)
4. **Index**: Updated prompts/_index.md and assets/_index.md

## Issues Carried Forward
- None

## Next Week Notes
- Monthly deep audit due (April first Friday)
- Review agentreach-session-harvest-prompt (stale draft, 16 days)

## Health Score: 94/100
```

---

## Escalation Procedures

### When to Escalate to Human
1. Two agents disagree on which version is canonical and authority chain can't resolve
2. A critical asset is missing and cannot be recovered
3. A pattern has recurred 5+ times despite systemic fixes
4. A human-created asset needs archival or deprecation (courtesy notification)
5. A system-wide reorganization is being considered

### Escalation Format
```markdown
## Librarian Escalation — [DATE]

**Severity**: [Critical / High / Medium]
**Issue**: [One-sentence summary]
**Context**: [What happened, what was tried]
**Options**: 
  A. [Option A and consequences]
  B. [Option B and consequences]
**Recommendation**: [Librarian's recommendation]
**Decision needed by**: [Date/time]
```
