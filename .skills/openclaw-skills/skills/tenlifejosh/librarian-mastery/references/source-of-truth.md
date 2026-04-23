# Source-of-Truth Management — One Version to Rule Them All

The source-of-truth system eliminates the most destructive question in any organization: "Which version
is the right one?" For every asset, there is exactly one canonical copy, in one canonical location, with
one unambiguous status. The source-of-truth registry is the Librarian's master index — the single
document that answers "where is the current version of X?" for any X.

---

## Table of Contents

1. [Source-of-Truth Philosophy](#source-of-truth-philosophy)
2. [The Master Registry](#the-master-registry)
3. [Registry Operations](#registry-operations)
4. [Conflict Detection](#conflict-detection)
5. [Conflict Resolution Protocol](#conflict-resolution-protocol)
6. [Authority Chains](#authority-chains)
7. [Truth Propagation](#truth-propagation)
8. [Fork and Duplicate Management](#fork-and-duplicate-management)
9. [Registry Maintenance](#registry-maintenance)

---

## Source-of-Truth Philosophy

### The Three Guarantees
1. **Existence guarantee**: If an asset is registered, it exists at the registered path
2. **Currency guarantee**: The registered version and status reflect reality
3. **Uniqueness guarantee**: No two registry entries point to the same logical asset

### The Five-Second Rule
Any agent should be able to answer "Where is the current version of X?" within 5 seconds by:
1. Checking the source-of-truth registry
2. Reading the `canonical_path` field
3. Confirming the status is ACTIVE or APPROVED

If it takes longer than 5 seconds, the registry needs improvement.

---

## The Master Registry

### Registry Location
```
system/registries/source-of-truth-registry-V1.0-ACTIVE.json
```

### Registry Schema

```json
{
  "registry_metadata": {
    "version": "V1.0",
    "last_updated": "2025-03-21T14:30:00Z",
    "updated_by": "Librarian Agent",
    "total_assets": 47,
    "by_status": {
      "DRAFT": 8,
      "ACTIVE": 28,
      "APPROVED": 4,
      "ARCHIVED": 5,
      "DEPRECATED": 2
    }
  },
  "entries": [
    {
      "asset_id": "gnd-cold-email-prompt",
      "entity": "gnd",
      "asset_type": "prompt",
      "current_version": "V5.0",
      "current_status": "ACTIVE",
      "canonical_path": "prompts/by-entity/gnd/gnd-cold-email-prompt-V5.0-ACTIVE.md",
      "last_modified": "2025-03-15T10:30:00Z",
      "modified_by": "Sales Agent",
      "registered": "2025-01-15T09:00:00Z",
      "total_versions": 5,
      "branches": [],
      "external_deployments": [],
      "dependents": [
        "outbound-sequence-sop",
        "cold-outreach-email-template"
      ],
      "dependencies": [],
      "next_review": "2025-06-15",
      "tags": ["email", "cold-outreach", "sales", "gnd"]
    }
  ]
}
```

### Registry Entry Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `asset_id` | string | Unique identifier (entity-descriptor format) |
| `entity` | string | Entity prefix |
| `asset_type` | string | prompt, sop, template, asset, skill, config |
| `current_version` | string | The version that's currently canonical |
| `current_status` | string | ACTIVE, APPROVED, DRAFT, DEPRECATED, ARCHIVED |
| `canonical_path` | string | Exact filepath to the canonical copy |
| `last_modified` | datetime | When the asset was last changed |
| `modified_by` | string | Who/what made the last change |

### Registry Entry Optional Fields

| Field | Type | Description |
|-------|------|-------------|
| `registered` | datetime | When the entry was first added to registry |
| `total_versions` | integer | How many versions exist |
| `branches` | array | Active branch names (if any) |
| `external_deployments` | array | Where this asset is deployed externally |
| `dependents` | array | Assets that depend on this one |
| `dependencies` | array | Assets this one depends on |
| `next_review` | date | When this asset should next be reviewed |
| `tags` | array | Searchable tags |
| `notes` | string | Any special notes about this asset |

---

## Registry Operations

### Register a New Asset
When a new asset is created and reaches at least DRAFT status:

```
1. Generate asset_id from entity + descriptor
2. Verify no existing entry with same asset_id
3. Create registry entry with all required fields
4. Verify canonical_path exists and file is accessible
5. Log registration in changelog
```

### Update an Existing Entry
When an asset changes version or status:

```
1. Find entry by asset_id
2. Update version, status, canonical_path, last_modified, modified_by
3. If version changed, increment total_versions
4. If status changed, verify transition is allowed (see status-lifecycle.md)
5. Verify new canonical_path exists
6. Log update in changelog
```

### Remove an Entry
When an asset is permanently archived or deleted:

```
1. Find entry by asset_id
2. Verify all dependents have been updated
3. Move entry to a separate "archived_entries" array (don't delete from registry)
4. Log removal in changelog
5. Archive the actual file (don't delete)
```

### Bulk Registry Update
After a major reorganization, migration, or maintenance cycle:

```
1. Generate a filesystem inventory (list all files)
2. Compare inventory against registry
3. Flag discrepancies:
   - In registry but not on filesystem → CRITICAL: missing file
   - On filesystem but not in registry → WARNING: unregistered asset
   - Path mismatch → ERROR: file moved without registry update
4. Generate reconciliation report
5. Resolve each discrepancy
6. Update registry timestamp
```

---

## Conflict Detection

### Types of Conflicts

| Conflict Type | Description | Severity |
|---------------|-------------|----------|
| **Dual Active** | Two versions of the same asset both marked ACTIVE | Critical |
| **Path Mismatch** | Registry path doesn't match actual file location | High |
| **Version Mismatch** | Registry version doesn't match file's internal version | High |
| **Ghost Entry** | Registry entry for a file that doesn't exist | High |
| **Orphan File** | File exists but has no registry entry | Medium |
| **Stale Reference** | A dependent asset references an old/wrong version | Medium |
| **Status Mismatch** | Registry status doesn't match filename status tag | Medium |
| **Duplicate Entry** | Two registry entries for the same logical asset | Low |

### Automated Conflict Detection Checks

Run during every maintenance cycle:

```
CONFLICT SCAN CHECKLIST:
□ For each registry entry, verify file exists at canonical_path
□ For each registry entry, verify filename status matches registry status
□ For each registry entry, verify filename version matches registry version
□ For each asset_type, verify no duplicate asset_ids
□ For each ACTIVE/APPROVED asset, verify only ONE exists per asset_id
□ For each dependent reference, verify the referenced asset still exists and is current
□ Scan filesystem for files not in registry (orphan detection)
□ Compare registry total_assets against actual filesystem count
```

---

## Conflict Resolution Protocol

### Priority Rules (Who Wins)

When two versions claim to be canonical:

```
CONFLICT RESOLUTION HIERARCHY:

1. Registry says → Registry wins (unless registry is provably wrong)
2. If registry is outdated:
   a. Most recently modified version wins
   b. If same modification date: version created by domain-authority agent wins
   c. If still tied: version in canonical directory wins
   d. If STILL tied: escalate to human decision
3. Never resolve ambiguity by keeping both — ONE must be canonical
4. Document the resolution in lessons-learned
```

### Resolution Workflow

```
CONFLICT DETECTED
     │
     ▼
  CHECK REGISTRY
  Is one version registered as canonical?
     │
     ├── YES → Does the registered file exist?
     │         ├── YES → Registry version wins. Archive the other.
     │         └── NO → The existing file wins. Update registry.
     │
     └── NO → Neither is registered
              │
              ├── Compare modification dates
              │   Latest wins. Register it. Archive the other.
              │
              └── Same date → Check which is in the canonical directory
                  That one wins. Register it. Archive the other.
```

### Post-Resolution Steps
1. Archive the non-canonical version (never delete)
2. Update registry with correct entry
3. Check all dependents — are any still referencing the old/wrong version?
4. Update dependents if needed
5. Log conflict and resolution in lessons-learned
6. Add to changelog

---

## Authority Chains

### Who Has Authority Over What?

| Asset Type | Primary Authority | Secondary Authority | Escalation |
|-----------|------------------|--------------------|----|
| Prompts | Creating agent | Librarian | Human |
| SOPs | Process owner agent | Librarian | Human |
| Templates | Creating agent | Librarian | Human |
| Product assets | Product owner agent | Librarian | Human |
| System configs | Librarian | Human | - |
| Registry itself | Librarian | Human | - |

### Authority Inheritance
- If the creating agent is no longer active, authority passes to the Librarian
- If the Librarian can't resolve, authority passes to human decision
- Human decisions are always final and override all agent decisions

### Authority Override Protocol
When a human overrides the Librarian's determination:
1. Accept the override immediately
2. Log the override with rationale: "Human override: [reason]"
3. Update all systems to reflect the human's decision
4. Do NOT re-override in the next maintenance cycle

---

## Truth Propagation

### What is Truth Propagation?
When the canonical version of an asset changes, all downstream references must be updated. This is
truth propagation — ensuring that a change to the source of truth flows through to everything that
depends on it.

### Propagation Workflow

```
SOURCE-OF-TRUTH CHANGES (e.g., V4 → V5)
     │
     ▼
  IDENTIFY DEPENDENTS
  Check registry for all assets listing this as a dependency
     │
     ▼
  FOR EACH DEPENDENT:
     │
     ├── Does the dependent reference a specific version? (e.g., "uses V4")
     │   └── YES → Update reference to V5
     │
     ├── Does the dependent reference the asset generically? (e.g., "uses gnd-cold-email-prompt")
     │   └── Likely OK — will pick up current version. But verify.
     │
     └── Does the dependent embed content from the old version?
         └── YES → Flag for manual review. Content may need updating.
```

### Propagation Log

```yaml
propagation_log:
  trigger_event: "gnd-cold-email-prompt promoted from V4.0 to V5.0"
  trigger_date: "2025-03-15"
  propagated_by: "Librarian Agent"
  dependents_checked: 3
  dependents_updated: 2
  dependents_flagged_for_review: 1
  details:
    - dependent: "outbound-sequence-sop"
      action: "Updated reference from V4 to V5"
      result: "success"
    - dependent: "cold-outreach-email-template"
      action: "Updated embedded content reference"
      result: "success"  
    - dependent: "weekly-report-template"
      action: "Flagged for review — contains hardcoded example from V4"
      result: "flagged"
```

---

## Fork and Duplicate Management

### Forks vs Duplicates
- **Fork**: An intentional variant of an asset for a different purpose (legitimate)
- **Duplicate**: An unintentional copy of the same asset (illegitimate)

### Managing Legitimate Forks
When a fork is created (e.g., enterprise variant of a prompt):
1. Register as a separate entry with its own asset_id
2. Link to the parent: `forked_from: "gnd-cold-email-prompt-V4.0"`
3. Both can be ACTIVE simultaneously (they serve different purposes)
4. Each has independent version numbering
5. Changes to the parent do NOT automatically propagate to forks (they diverged intentionally)

### Detecting Illegitimate Duplicates
During maintenance, scan for:
- Files with >80% content similarity in different locations
- Files with the same entity+descriptor but different paths and both ACTIVE
- Files where one appears to be a copy-paste of the other with minor edits

### Resolving Duplicates
1. Determine which is canonical (use authority chain)
2. Check if the non-canonical copy has any unique content worth preserving
3. If unique content exists: merge into the canonical version, creating a new version
4. If no unique content: archive the duplicate
5. Update registry
6. Log in lessons-learned

---

## Registry Maintenance

### Real-Time Updates
The registry should be updated in real-time whenever:
- A new asset is created
- An asset changes version
- An asset changes status
- An asset is moved or renamed

### Weekly (Friday) Verification
- Run automated conflict detection scan
- Reconcile registry against filesystem
- Fix any discrepancies found
- Update registry metadata (counts, last_updated)

### Monthly Deep Audit
- Full filesystem inventory vs registry comparison
- Check all dependency links are still valid
- Review next_review dates — flag overdue reviews
- Generate registry health report

### Quarterly Registry Cleanup
- Archive entries for long-dead assets
- Review and consolidate tags
- Check for registry bloat (entries that serve no purpose)
- Generate quarterly registry statistics

### Registry Health Metrics

| Metric | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Registry-filesystem sync accuracy | 100% | 95-99% | <95% |
| Ghost entries (file doesn't exist) | 0 | 1-2 | >2 |
| Orphan files (not in registry) | 0 | 1-5 | >5 |
| Dual-active conflicts | 0 | 0 | ≥1 (always critical) |
| Stale dependency references | 0 | 1-3 | >3 |
| Average time to resolve conflicts | <1 hour | 1-24 hours | >24 hours |
