# Status & Lifecycle Management — Tracking Every Asset's Journey

Status labels are the traffic lights of the organizational file system. They tell every agent and human,
at a glance, whether an asset is safe to use, still in progress, or retired. Without clear status, every
file is Schrödinger's document — simultaneously current and obsolete until someone investigates.

---

## Table of Contents

1. [Status Label Definitions](#status-label-definitions)
2. [Lifecycle State Machine](#lifecycle-state-machine)
3. [Promotion Rules & Gates](#promotion-rules-and-gates)
4. [Status Registry Format](#status-registry-format)
5. [Status Badges in Filenames](#status-badges-in-filenames)
6. [Lifecycle Audit Trail](#lifecycle-audit-trail)
7. [Bulk Status Operations](#bulk-status-operations)
8. [Edge Cases & Special Statuses](#edge-cases-and-special-statuses)

---

## Status Label Definitions

### The Five Core Statuses

| Status | Emoji | Meaning | Can Be Used in Production? | In Filename |
|--------|-------|---------|---------------------------|-------------|
| **DRAFT** | 🟡 | Work in progress. Not yet ready for use. May be incomplete, untested, or awaiting review. | NO | `-DRAFT` |
| **ACTIVE** | 🟢 | Current working version. Ready for and in production use. This is the version agents should use. | YES | `-ACTIVE` |
| **APPROVED** | 🔵 | Formally reviewed and approved. Higher authority than ACTIVE — used when formal sign-off is required. | YES (preferred over ACTIVE) | `-APPROVED` |
| **ARCHIVED** | ⚪ | No longer current. Preserved for historical reference. Not in production use. | NO (reference only) | `-ARCHIVED` |
| **DEPRECATED** | 🔴 | Actively being phased out. A replacement exists. Should not be used for new work. Will be archived. | NO (stop using immediately) | `-DEPRECATED` |

### Status Hierarchy
```
APPROVED > ACTIVE > DRAFT > DEPRECATED > ARCHIVED
```

When an agent asks for "the current version" of an asset:
1. Return APPROVED version if it exists
2. Return ACTIVE version if no APPROVED exists
3. Return DRAFT version only if explicitly asked for drafts
4. Never return DEPRECATED or ARCHIVED unless specifically requested

### One Active Rule
For any given asset (same entity + descriptor), there must be exactly ONE version with ACTIVE or APPROVED
status at any time. Multiple DRAFTs are fine. Multiple ARCHIVEDs are fine. But only one production version.

---

## Lifecycle State Machine

### Standard Lifecycle

```
                    ┌───────────────────────────────┐
                    │                               │
                    ▼                               │
    ┌────────┐   ┌────────┐   ┌──────────┐   ┌──────────┐
    │ DRAFT  │──▶│ ACTIVE │──▶│ APPROVED │──▶│ ARCHIVED │
    └────────┘   └────────┘   └──────────┘   └──────────┘
                    │              │               ▲
                    │              │               │
                    ▼              ▼               │
              ┌─────────────┐                     │
              │ DEPRECATED  │─────────────────────┘
              └─────────────┘
```

### Allowed Transitions

| From | To | Trigger | Requirements |
|------|----|---------|-------------|
| DRAFT | ACTIVE | Asset is ready for production | Content complete, naming compliant, version set |
| DRAFT | ARCHIVED | Draft abandoned, not needed | Log reason for abandonment |
| ACTIVE | APPROVED | Formal review completed | Reviewer sign-off recorded |
| ACTIVE | DEPRECATED | Newer version supersedes this | Replacement identified, deprecation notice created |
| ACTIVE | ARCHIVED | Asset retired from use | No dependents still referencing it |
| APPROVED | ARCHIVED | Asset retired from use | Approval authority agrees to retirement |
| APPROVED | DEPRECATED | Newer version supersedes | Replacement identified |
| DEPRECATED | ARCHIVED | Grace period elapsed (30 days) | All dependents updated to use replacement |
| ARCHIVED | ACTIVE | Rollback or reactivation needed | Creates new version number (never reactivates old version number) |

### Forbidden Transitions

| From | To | Why Forbidden |
|------|----|--------------|
| ARCHIVED | DRAFT | Archived assets don't go back to draft; create a new version instead |
| DEPRECATED | ACTIVE | Deprecated assets don't un-deprecate; create a new version |
| DEPRECATED | DRAFT | Same — create a new asset |
| Any | DELETED | Deletion is a separate process, not a status (see archive-deletion.md) |

---

## Promotion Rules and Gates

### Gate: DRAFT → ACTIVE

**Pre-conditions** (ALL must be true):
- [ ] File naming follows conventions (entity-descriptor-version-status.ext)
- [ ] File is in canonical directory location
- [ ] Version number is set (V1.0 for first release, appropriate increment for updates)
- [ ] Internal metadata matches filename (version, status)
- [ ] Content is complete (no TODOs, no placeholders, no "[INSERT X HERE]")
- [ ] If replacing a previous ACTIVE version, that version is ready to be ARCHIVED

**Actions on promotion**:
1. Rename file: change `-DRAFT` to `-ACTIVE`
2. If replacing previous ACTIVE: rename old file to `-ARCHIVED`
3. Update source-of-truth registry
4. Update master changelog
5. Update any dependent asset cross-references

### Gate: ACTIVE → APPROVED

**Pre-conditions** (ALL must be true):
- [ ] All DRAFT → ACTIVE conditions met
- [ ] Reviewed by an authority (human or designated review agent)
- [ ] Reviewer sign-off recorded in metadata
- [ ] No known issues or pending changes

**Actions on promotion**:
1. Rename file: change `-ACTIVE` to `-APPROVED`
2. Add `approved_by` and `approved_date` to metadata
3. Update source-of-truth registry
4. Update master changelog

### Gate: Any → DEPRECATED

**Pre-conditions**:
- [ ] Replacement asset identified (or explicit decision that no replacement is needed)
- [ ] `deprecated_reason` documented
- [ ] `replaced_by` pointer set (if applicable)
- [ ] Deprecation notice added to the file's header

**Actions on deprecation**:
1. Rename file: change status to `-DEPRECATED`
2. Add deprecation header to file content:
   ```
   ⚠️ DEPRECATED as of 2025-03-21
   Reason: Superseded by V5.0 with new subject line framework
   Replacement: gnd-cold-email-prompt-V5.0-ACTIVE.md
   Archive date: 2025-04-21 (30-day grace period)
   ```
3. Update source-of-truth registry
4. Update master changelog
5. Trigger deprecation cascade check (see version-control.md)
6. Schedule archive date (30 days from deprecation)

---

## Status Registry Format

A central registry tracking the current status of all assets. This is the Librarian's master index.

### Registry Structure (JSON)

```json
{
  "registry_version": "V1.0",
  "last_updated": "2025-03-21T14:30:00Z",
  "updated_by": "Librarian Agent",
  "assets": [
    {
      "asset_id": "gnd-cold-email-prompt",
      "entity": "gnd",
      "descriptor": "cold-email-prompt",
      "asset_type": "prompt",
      "current_version": "V5.0",
      "current_status": "ACTIVE",
      "canonical_path": "prompts/by-entity/gnd/gnd-cold-email-prompt-V5.0-ACTIVE.md",
      "last_modified": "2025-03-15",
      "modified_by": "Sales Agent",
      "total_versions": 5,
      "has_branches": false,
      "dependents": ["outbound-sequence-sop", "cold-outreach-email-template"],
      "dependencies": [],
      "next_review_date": "2025-06-15",
      "tags": ["email", "cold-outreach", "sales"]
    },
    {
      "asset_id": "gumroad-publish-sop",
      "entity": "org",
      "descriptor": "gumroad-publish-sop",
      "asset_type": "sop",
      "current_version": "V2.1",
      "current_status": "APPROVED",
      "canonical_path": "sops/by-workflow/publishing/gumroad-publish-sop-V2.1-APPROVED.md",
      "last_modified": "2025-03-21",
      "modified_by": "Ops Agent",
      "total_versions": 3,
      "has_branches": false,
      "dependents": [],
      "dependencies": ["gumroad-api-template"],
      "next_review_date": "2025-06-21",
      "tags": ["publishing", "gumroad", "e-commerce"]
    }
  ]
}
```

### Registry Maintenance
- Updated every time an asset changes status
- Verified against filesystem during weekly maintenance
- Any mismatch between registry and filesystem is flagged as a critical error

---

## Status Badges in Filenames

### Filename Anatomy with Status

```
gnd-cold-email-prompt-V5.0-ACTIVE.md
                              ^^^^^^
                              Status badge
```

### Status Badge Rules
1. Status is ALWAYS the last segment before the file extension
2. Status is ALWAYS uppercase
3. Status is separated from version by a hyphen
4. The status in the filename MUST match the status in the internal metadata
5. If you see a file without a status badge, it's a naming violation — flag in next audit

---

## Lifecycle Audit Trail

Every status transition generates an audit record.

### Audit Record Format

```yaml
audit_trail:
  - timestamp: "2025-03-21T14:30:00Z"
    asset_id: "gnd-cold-email-prompt"
    transition: "ACTIVE → DEPRECATED"
    from_version: "V4.0"
    to_version: "V4.0"  # Same version, status change only
    triggered_by: "Sales Agent"
    reason: "Superseded by V5.0 with new subject line framework"
    replacement: "gnd-cold-email-prompt-V5.0-ACTIVE.md"
    changelog_entry: "CHANGELOG-2025.md#2025-03-21"
```

### Querying the Audit Trail
The audit trail should support answering:
- "When was this asset last promoted/demoted?"
- "Who approved this?"
- "What's the complete history of status changes for this asset?"
- "How many assets were deprecated in the last 30 days?"
- "Are there any assets stuck in DRAFT for more than 14 days?"

---

## Bulk Status Operations

### Bulk Deprecation
When an entire entity is deprecated (e.g., a product is retired):
1. List all assets with that entity prefix
2. Set all to DEPRECATED with reason "Entity retired: [entity-name]"
3. Set replacement pointers if applicable
4. Trigger cascade checks for all
5. Log bulk operation in changelog
6. Schedule bulk archive for 30 days

### Bulk Archive
When performing quarterly cleanup:
1. List all DEPRECATED assets past their grace period
2. Move all to ARCHIVED status
3. Move files to archive/ directory
4. Update registries
5. Generate bulk archive report

### Quarterly Status Review
Every quarter, generate a status health report:
- Count of assets by status (DRAFT, ACTIVE, APPROVED, ARCHIVED, DEPRECATED)
- Assets stuck in DRAFT > 30 days (flag for review)
- Assets in ACTIVE > 180 days without review (flag for freshness check)
- DEPRECATED assets past grace period (archive them)
- Orphaned assets (in filesystem but not in registry)

---

## Edge Cases and Special Statuses

### Contested Status
When two agents disagree on whether an asset should be ACTIVE or DEPRECATED:
1. The source-of-truth registry is the authority
2. If the registry is unclear, escalate to human decision
3. Temporarily mark as `ACTIVE-CONTESTED` in the registry (not in filename)
4. Resolve within 48 hours

### Emergency Revert
When an ACTIVE asset causes a problem and needs immediate rollback:
1. Change current ACTIVE to DEPRECATED immediately (no 30-day grace period)
2. Create a new version with the previous content, mark ACTIVE
3. Log as emergency revert in changelog with incident details
4. Add to lessons-learned log

### Seasonal Assets
Some assets are cyclical (e.g., holiday email templates):
- Use `ACTIVE` during season, `ARCHIVED-SEASONAL` during off-season
- Never delete seasonal assets — they'll be needed next cycle
- Note the season in metadata: `season: "Q4-holiday"`
- Reactivate by creating a new version (reviewing for updates) when season returns

### Template Status
Templates follow the same lifecycle but have an additional consideration:
- A template in ACTIVE status means "this is the approved format to use"
- Assets CREATED FROM a template inherit the template's version in their metadata
- When a template is updated, assets created from the old template don't auto-update (they were snapshots)
