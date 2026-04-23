# Archive & Deletion Logic — Nothing Useful Gets Lost, Nothing Useless Lingers

The Librarian's default is to preserve everything. Deletion is the nuclear option — irreversible and
rarely justified. Archival is the standard retirement path. This reference defines exactly when to
archive, when to delete, and the decision process that ensures nothing useful is ever lost.

---

## Table of Contents

1. [The Preservation Principle](#the-preservation-principle)
2. [Archive vs Delete Decision Tree](#archive-vs-delete-decision-tree)
3. [Archival Process](#archival-process)
4. [Deletion Authorization](#deletion-authorization)
5. [Retention Policies](#retention-policies)
6. [Soft-Delete and Tombstone Records](#soft-delete-and-tombstone-records)
7. [Restore Procedures](#restore-procedures)
8. [Storage Optimization](#storage-optimization)

---

## The Preservation Principle

### Rule: When in Doubt, Archive
If there's ANY question about whether something should be kept, the answer is archive. Disk space
is cheap. Lost institutional knowledge is expensive. The cost of keeping an unnecessary file is
approximately zero. The cost of losing a file you needed is potentially hours or days of rework.

### The Only Valid Reasons to Delete
1. **Exact duplicate**: A byte-identical copy of a file that exists in the canonical location
2. **Test/temp files**: Files explicitly created as temporary and never promoted past that
3. **Corrupted files**: Files that are genuinely corrupted and unreadable (archive metadata still)
4. **Legal requirement**: A legal or compliance obligation requires deletion (rare, document thoroughly)
5. **Security requirement**: File contains credentials or sensitive data that must be purged

Everything else gets archived, not deleted.

---

## Archive vs Delete Decision Tree

```
ASSET CONSIDERED FOR REMOVAL
│
├── Is it an exact byte-identical duplicate of a canonical file?
│   ├── YES → DELETE (but log the deletion)
│   └── NO → Continue ↓
│
├── Is it a temporary/test file that was never promoted to DRAFT or higher?
│   ├── YES → DELETE (but log the deletion)
│   └── NO → Continue ↓
│
├── Is there a legal or security requirement to delete?
│   ├── YES → DELETE with full documentation of the requirement
│   └── NO → Continue ↓
│
├── Is the file corrupted beyond recovery?
│   ├── YES → DELETE the file but ARCHIVE the metadata (so we know it existed)
│   └── NO → Continue ↓
│
├── Is it a personal/opinion file (not an organizational asset)?
│   ├── YES → ASK the human owner. If they say delete, delete.
│   └── NO → Continue ↓
│
└── DEFAULT → ARCHIVE
    Do not delete. Archive with full metadata preservation.
```

### Simplified Rule
```
IF exact_duplicate OR temp_file → DELETE (log it)
ELSE IF legal_or_security_mandate → DELETE (document mandate)
ELSE → ARCHIVE (always)
```

---

## Archival Process

### Step 1: Pre-Archive Checklist
```
□ Verify no ACTIVE dependents still reference this asset
□ If dependents exist, update them first (point to replacement or remove reference)
□ Verify a replacement exists (if this was ACTIVE/APPROVED)
□ Record the archive reason
□ Record the archived_by agent
□ Record the archived_date
```

### Step 2: Update Metadata
Add archival metadata to the asset:

```yaml
archive_metadata:
  archived_date: "2025-03-21"
  archived_by: "Librarian Agent"
  archive_reason: "Superseded by V5.0"
  replaced_by: "gnd-cold-email-prompt-V5.0-ACTIVE.md"
  original_status: "ACTIVE"
  original_path: "prompts/by-entity/gnd/"
  retrievable: true
```

### Step 3: Rename with ARCHIVED Status
```
gnd-cold-email-prompt-V4.0-ACTIVE.md → gnd-cold-email-prompt-V4.0-ARCHIVED.md
```

### Step 4: Move to Archive Directory
```
FROM: prompts/by-entity/gnd/gnd-cold-email-prompt-V4.0-ARCHIVED.md
TO:   archive/by-entity/gnd/gnd-cold-email-prompt-V4.0-ARCHIVED.md
```

Or, for assets with many versions, keep archived versions alongside the active one:
```
prompts/by-entity/gnd/
├── gnd-cold-email-prompt-V5.0-ACTIVE.md      ← Current
├── gnd-cold-email-prompt-V4.0-ARCHIVED.md    ← Previous
├── gnd-cold-email-prompt-V3.0-ARCHIVED.md    ← Older
└── gnd-cold-email-prompt-V2.0-ARCHIVED.md    ← Oldest kept in-place
```

**Choice of archive location** depends on volume:
- **<5 archived versions**: Keep alongside active version in same directory
- **5+ archived versions**: Move older ones (keep latest 2 archived versions in-place) to `archive/`
- **Entity retired**: Move ALL versions to `archive/by-entity/`

### Step 5: Update Registry
- Update source-of-truth registry entry: status → ARCHIVED
- Update canonical_path to archive location
- Preserve all other metadata

### Step 6: Update Changelog
```
[2025-03-21] [gnd-cold-email-prompt] V4.0 status: ACTIVE → ARCHIVED — Superseded by V5.0
```

---

## Deletion Authorization

### Authorization Levels

| Deletion Type | Who Can Authorize | Documentation Required |
|--------------|-------------------|----------------------|
| Exact duplicate removal | Librarian (autonomous) | Log entry in changelog |
| Temp/test file removal | Librarian (autonomous) | Log entry in changelog |
| Corrupted file removal | Librarian (autonomous) | Archive metadata + log entry |
| Any other deletion | Human only | Written authorization + reason + log entry |
| Bulk deletion | Human only | Written authorization + complete file list + reason |

### Deletion Log Format

```yaml
deletion_log:
  - date: "2025-03-21"
    file: "temp-test-output-2025-03-20.txt"
    reason: "Temporary test file, never promoted"
    authorized_by: "Librarian Agent (autonomous — temp file rule)"
    reversible: false
    
  - date: "2025-03-15"
    file: "gnd-email-copy-2.md"
    reason: "Exact byte-identical duplicate of gnd-cold-email-prompt-V5.0-ACTIVE.md"
    authorized_by: "Librarian Agent (autonomous — exact duplicate rule)"
    reversible: false
    
  - date: "2025-03-10"
    file: "old-api-key-config.json"
    reason: "Contains exposed API credentials — security purge"
    authorized_by: "Human — JD (security requirement)"
    reversible: false
    notes: "Credential rotated on same date"
```

### Deletion Confirmation Protocol
Before any deletion:
1. Verify the file matches the deletion criteria
2. Verify the deletion is logged BEFORE the file is removed
3. For non-autonomous deletions, present to human and wait for confirmation
4. After deletion, verify the file is gone and the log is accurate

---

## Retention Policies

### Default Retention by Asset Type

| Asset Type | Active Retention | Archive Retention | Deletion Eligible |
|-----------|-----------------|-------------------|-------------------|
| Prompts | Indefinite while ACTIVE | Indefinite | Never (archive only) |
| SOPs | Indefinite while ACTIVE | Indefinite | Never (archive only) |
| Templates | Indefinite while ACTIVE | Indefinite | Never (archive only) |
| Product assets | Indefinite while ACTIVE | 5 years minimum | After 5 years, human decision |
| Lesson records | Indefinite | Indefinite | Never (institutional memory) |
| System configs | Current version only | 2 years minimum | After 2 years, human decision |
| Audit reports | Current quarter | 2 years | After 2 years, archive to cold storage |
| Changelogs | Current year + 1 prior | 5 years minimum | Never (organizational history) |
| Inbox items | 0 (process immediately) | N/A | N/A |
| Temp/test files | 7 days maximum | N/A | Delete after 7 days |

### Retention Override
Humans can override any retention policy by:
1. Issuing a written retention extension or reduction
2. Documenting the reason
3. The Librarian updating the asset's retention metadata

---

## Soft-Delete and Tombstone Records

### What is a Soft Delete?
Instead of removing a file, mark it as deleted but keep it recoverable for a grace period.

### Soft-Delete Process
1. Move file to `archive/soft-deleted/` directory
2. Create a tombstone record in the deletion log
3. Set hard-delete date (30 days from soft-delete)
4. If not restored within 30 days, hard-delete

### Tombstone Record Format

```yaml
tombstone:
  asset_id: "gnd-cold-email-prompt-V1.0"
  original_path: "prompts/by-entity/gnd/gnd-cold-email-prompt-V1.0-ARCHIVED.md"
  soft_deleted_path: "archive/soft-deleted/gnd-cold-email-prompt-V1.0-ARCHIVED.md"
  soft_deleted_date: "2025-03-21"
  soft_deleted_by: "Librarian Agent"
  reason: "5+ archived versions, oldest moved to soft-delete"
  hard_delete_date: "2025-04-20"
  restored: false
```

### When to Use Soft-Delete vs Direct Archive
- **Soft-delete**: When the asset might be needed in the next 30 days but probably won't
- **Archive**: When the asset is preserved for historical reference (standard retirement path)
- **Hard-delete**: Only for the five valid deletion reasons listed above

---

## Restore Procedures

### Restoring from Archive
1. Locate the archived asset in `archive/` directory
2. Copy (don't move) to the working directory
3. Create a NEW version number (never reactivate the old version number)
4. Set status to DRAFT
5. Update metadata (creation date = today, based_on = archived version)
6. Register in source-of-truth registry as a new version
7. Log the restore in changelog: "V6.0 — Restored from archived V3.0 for [reason]"

### Restoring from Soft-Delete
1. Move file from `archive/soft-deleted/` back to original location
2. Update tombstone record: `restored: true`
3. Re-register in source-of-truth registry
4. Log in changelog

### Restore Request Log
Every restore request is logged:

```yaml
restore_log:
  - date: "2025-03-25"
    asset: "gnd-cold-email-prompt-V3.0"
    requested_by: "Sales Agent"
    reason: "Need to reference the personalization approach from V3"
    action: "Copied from archive, created V6.0-DRAFT based on V3.0 content"
    result: "success"
```

---

## Storage Optimization

### Storage Tiers

| Tier | What Lives Here | Access Speed | Cost |
|------|----------------|-------------|------|
| **Hot** | ACTIVE and APPROVED assets | Instant | Highest |
| **Warm** | DRAFT assets, recently ARCHIVED | Fast | Medium |
| **Cold** | Old archived assets, historical versions | Slow | Lowest |

### Optimization Strategies
1. **Keep hot storage lean**: Only ACTIVE and APPROVED assets in primary directories
2. **Batch archive moves**: Don't move individual files daily; batch during maintenance
3. **Compress cold archives**: Zip/compress archived assets older than 1 year
4. **Metadata stays hot**: Even when assets move to cold storage, their registry entries remain in the hot registry for searchability

### Storage Health Check (Quarterly)
```
□ Total storage usage by tier
□ Growth rate (quarter-over-quarter)
□ Largest assets (identify any unexpectedly large files)
□ Redundant storage (duplicate detection)
□ Cold storage candidates (archived assets >1 year old, not compressed)
□ Projected storage needs for next quarter
```
