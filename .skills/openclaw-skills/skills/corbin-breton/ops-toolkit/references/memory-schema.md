# Memory Schema — items.json Specification

Complete specification for atomic facts stored in `items.json` files across your knowledge graph (PARA structure: Projects, Areas, Resources, Archives).

---

## File Structure

```json
{
  "facts": [
    { /* fact object */ },
    { /* fact object */ }
  ]
}
```

`items.json` contains a single `facts` array. Each element is an atomic fact.

---

## Fact Object Schema

### Required Fields

#### `id` (string)
Unique identifier for this fact. Format: `FACT-NNN` (auto-incremented) or `[category]-[slug]`.

Example: `FACT-001`, `GOAL-SHIP-PRODUCT`, `RISK-BURNOUT`

- Must be unique within the entity (project/area/etc.)
- Used for references and decay tracking
- Never changes after creation

#### `fact` (string)
The atomic fact itself. Single claim. 20–80 words. Plain language.

Examples:
- "Team deploys across 5 regions: US-East, US-West, EU, APAC, CN"
- "Manual region sync is pain point; needs automation"
- "Ship product v1 by Q2 2026"

**Principles:**
- One claim per fact (not compound statements)
- Retrievable independently (other facts don't depend on understanding this one)
- Free of jargon (assume agent retrieves this in isolation)

#### `category` (string)
Classification for retrieval and decay. Enables agent to fetch related facts together.

**Valid values:**
- `identity` — Who the user is
- `preference` — User communication, work, or operational preference
- `decision` — Past decision and reasoning
- `goal` — Target or objective
- `status` — Current state or progress
- `skill` — Agent capability or learned pattern
- `asset` — Resource, tool, or person
- `risk` — Known risk, blocker, or concern
- `schedule` — Availability or timing
- `vision-technical` — Long-term technical direction
- `personal` — Personal context (non-work)
- `business` — Business context (market, competition, customers)
- `branding` — Public identity, tone, reputation

Example: fact about "team size is 5" → category: `status`

#### `timestamp` (ISO 8601 string)
When this fact was created. Format: `YYYY-MM-DDTHH:MM:SSZ` (UTC).

Example: `2026-03-17T10:30:00Z`

- Set at creation time
- Never changes
- Enables time-based queries ("facts created in last 7 days")

#### `source` (string)
Where this fact came from. Enables provenance tracking and debugging.

**Common values:**
- `daily-note-2026-03-17` (from daily notes)
- `interview-block-1` (from persona-builder interview)
- `nightly-extraction` (automated extraction)
- `human-edit` (manually added)
- `agent-observation` (learned by agent during operation)

#### `status` (string)
Lifecycle stage. Updated by decay_sweep.py weekly.

**Valid values:**
- `active` (created ≤ 7 days ago, or accessed recently; prominent in summaries)
- `warm` (created 8–30 days ago, or not accessed in 8+ days; included in summary but lower priority)
- `cold` (created 31+ days ago, or not accessed in 31+ days; removed from summary, kept in storage)
- `superseded` (manually marked as outdated; replaced by newer fact; not used in decay_sweep, only by humans)

**Transition rules:**
- Fresh fact: `active`
- Not accessed in 8 days: `warm` (automatic, via decay_sweep)
- Not accessed in 31 days: `cold` (automatic, via decay_sweep)
- Manually marked obsolete: `superseded` (human decision only)

#### `lastAccessed` (ISO 8601 string)
Most recent time this fact was retrieved or used. Example: `2026-03-17T14:22:00Z`

**Update rule:** Bumped every time fact appears in agent's conversation or is retrieved for context.

- Initialized to same as `timestamp` at creation
- Used by decay algorithm to classify age (hot/warm/cold)
- Enables "recency" queries ("what have I been thinking about this week?")

#### `accessCount` (integer)
How many times this fact has been used/retrieved. Integer ≥ 0.

**Update rule:** Incremented every time fact is used in conversation.

- Initialized to 0 at creation
- Enables "frequently-accessed" prioritization
- Feeds into decay resistance: facts with accessCount > 5 get +14 days before cooling

**Rationale (GAM-RAG, arXiv:2603.01783):** Frequently-accessed facts are "stable" (Kalman-inspired). They resist decay. New facts (low accessCount) age quickly; established facts (high accessCount) stick around.

### Optional Fields

#### `relatedEntities` (array of strings)
Tags linking this fact to related facts or domains. For clustering and navigation.

Example:
```json
"relatedEntities": ["infrastructure", "deployment", "scaling"]
```

**Use cases:**
- Agent fetches all facts tagged "infrastructure" (related query)
- Morning brief highlights facts with tags matching user goals
- Decay algorithm keeps related facts together (don't age one without the others)

#### `supersededBy` (string, optional)
If this fact is superseded, ID of the newer fact that replaces it.

Example: `"supersededBy": "FACT-042"`

**Rules:**
- Only set manually (not by decay_sweep)
- Prevents deletion (old fact stays in storage)
- Enables audit trail ("why was this changed?")
- Decay never sets this field

---

## Access Tracking Rules

When a fact is used (appears in agent's response, retrieval, or conversation):

1. **Bump `lastAccessed`** to current timestamp (ISO 8601, UTC)
2. **Increment `accessCount`** by 1
3. **Save updated `items.json`**

**Implementation (pseudo):**
```python
fact = items_json["facts"][fact_index]
fact["lastAccessed"] = datetime.now().isoformat() + "Z"
fact["accessCount"] += 1
save_items_json()
```

**Cost implication (MemPO, arXiv:2603.00680):** Cheap writes (just bumping two fields). This enables the decay algorithm to work without expensive computation.

---

## Example Facts

### Identity

```json
{
  "id": "IDENTITY-001",
  "fact": "User name is Jordan, founder of a tech startup",
  "category": "identity",
  "timestamp": "2026-03-17T10:00:00Z",
  "source": "interview-block-1-identity",
  "status": "active",
  "lastAccessed": "2026-03-17T10:00:00Z",
  "accessCount": 0,
  "relatedEntities": ["founder", "infrastructure", "ai"]
}
```

### Goal

```json
{
  "id": "GOAL-SHIP-001",
  "fact": "Ship first product version by Q2 2026",
  "category": "goal",
  "timestamp": "2026-03-17T10:05:00Z",
  "source": "interview-block-2-goals",
  "status": "active",
  "lastAccessed": "2026-03-17T10:05:00Z",
  "accessCount": 3,
  "relatedEntities": ["product", "timeline", "q2-2026"]
}
```

### Decision

```json
{
  "id": "DECISION-001",
  "fact": "Chose GraphQL over REST for API (team expertise + faster iteration)",
  "category": "decision",
  "timestamp": "2026-03-16T14:30:00Z",
  "source": "daily-note-2026-03-16",
  "status": "active",
  "lastAccessed": "2026-03-17T08:00:00Z",
  "accessCount": 2,
  "relatedEntities": ["api", "architecture", "graphql"]
}
```

### Risk

```json
{
  "id": "RISK-BURNOUT",
  "fact": "Risk: losing momentum; tendency to overcommit",
  "category": "risk",
  "timestamp": "2026-03-17T10:10:00Z",
  "source": "interview-block-2-fears",
  "status": "active",
  "lastAccessed": "2026-03-17T10:10:00Z",
  "accessCount": 0,
  "relatedEntities": ["health", "pacing"]
}
```

### Status

```json
{
  "id": "STATUS-TEAM",
  "fact": "Team size: 3 engineers + 1 designer. Hiring for 2 more engineers Q2",
  "category": "status",
  "timestamp": "2026-03-15T16:00:00Z",
  "source": "daily-note-2026-03-15",
  "status": "warm",
  "lastAccessed": "2026-03-16T09:00:00Z",
  "accessCount": 1,
  "relatedEntities": ["team", "hiring", "headcount"]
}
```

---

## Decay Classification (decay_sweep.py)

Weekly sweep classifies facts by age:

```
effective_age = days_since_last_access - (14 if accessCount > 5 else 0)

if effective_age < 7:
    status = "active" (hot)
elif effective_age < 30:
    status = "warm"
else:
    status = "cold"
```

**Example:**
- Fact accessed 25 days ago, accessCount = 1
  - effective_age = 25 - 0 = 25
  - status = "warm"
  
- Fact accessed 25 days ago, accessCount = 10
  - effective_age = 25 - 14 = 11
  - status = "active" (resistance bonus prevents cooling)

---

## Retrieval by Category

**Example retrieval query (pseudo):**
```python
goal_facts = [f for f in items_json["facts"] if f["category"] == "goal"]
hot_facts = [f for f in items_json["facts"] if f["status"] == "active"]
infrastructure_facts = [f for f in items_json["facts"] if "infrastructure" in f.get("relatedEntities", [])]
```

**Search strategies:**
1. By category: "get all goals" → all facts with category=`goal`
2. By status: "get hot facts" → all facts with status=`active` (for summary)
3. By tag: "get facts about X" → all facts with X in relatedEntities
4. By recency: "recent facts" → sort by lastAccessed, take top N

---

## Storage and Maintenance

### Location
- Projects: `life/projects/[project-name]/items.json`
- Areas: `life/areas/[domain-name]/items.json`
- Resources: `life/resources/[resource-type]/items.json`
- Archives: `life/archives/[archived-project]/items.json`

### Summary.md Sync
- Rewritten weekly by decay_sweep.py
- Contains hot + warm facts (active status)
- Cold facts are in items.json but not in summary
- Never delete items.json; only update status

### Backup Strategy
- items.json is source of truth
- summary.md is derived and regeneratable
- Commit items.json to git for history

---

## Research Backing

**SuperLocalMemory (arXiv:2603.02240):** Schema includes provenance tracking (`source`, `supersededBy`), trust scoring (status + accessCount), and Bayesian confidence (freshness via lastAccessed). Local-first (never synced to cloud).

**Retrieval Bottleneck (arXiv:2603.02473):** Category field enables hierarchical retrieval. Raw facts (not summaries) are stored, enabling independent retrieval and recombination.

**MemPO (arXiv:2603.00680):** accessCount + lastAccessed enable autonomous decay (cheap updates, no expensive summarization). Agent manages its own memory lifecycle.

**GAM-RAG (arXiv:2603.01783):** accessCount > 5 resistance mirrors Kalman principle: stable facts (high accessCount, certain) resist change; new facts (low accessCount, uncertain) update easily.
