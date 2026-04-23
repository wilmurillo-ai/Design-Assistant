# Planner — Job Analysis & Team Proposal

The Planner receives a task, classifies its domain, and proposes the optimal team composition from all three rosters. This is the first step in any team-builder workflow.

Draws from: Agency's **Senior Project Manager** (spec-to-task methodology) and **Sprint Prioritizer** (prioritization framework).

## Planner Workflow

### Step 1: Classify the Domain

Read the task and identify which domains it touches:

| Domain | Indicators | Primary Roster |
|--------|-----------|----------------|
| Engineering / Code | Build, implement, fix, API, database, frontend | Core (CEO pipeline) + Agency Engineering |
| Visual / Creative | Image, design, generate, logo, chart, photo | Core (Artist) + Agency Design |
| Research / Optimization | Experiment, optimize, tune, analyze, iterate | Research Lab + relevant specialists |
| Marketing / Growth | Launch, campaign, content, social, audience | Agency Marketing |
| Operations / Support | Monitor, report, compliance, finance | Agency Support |
| Spatial / Immersive | AR, VR, XR, Vision Pro, spatial | Agency Spatial Computing |
| Multi-domain | Complex project touching 3+ domains | CEO orchestrates, mix all rosters |

### Step 2: Propose the Team

For each classified domain, select the right specialists:

#### Small Task (1-3 agents, Micro mode)
- One primary specialist from the relevant division
- Evidence Collector or Reality Checker for review
- CEO oversight if cross-domain

#### Medium Task (5-10 agents, Sprint mode)
- Domain specialist team (2-4 from relevant divisions)
- Senior PM for scoping
- Evidence Collector + Reality Checker for QA
- CEO as orchestrator

#### Large Project (10+ agents, Full mode)
- Full NEXUS pipeline activation
- Agents Orchestrator or CEO as controller
- Specialists from multiple divisions
- Complete QA team
- Support division for operations

### Step 3: Define the Activation Order

Specialists activate in phases, not all at once:

```
Phase 1: SCOPE
  → Senior PM breaks the task into sub-tasks with acceptance criteria
  → Sprint Prioritizer orders by impact and dependencies

Phase 2: BUILD
  → Domain specialists execute sub-tasks
  → Dev↔QA loops: specialist implements → Evidence Collector validates
  → Maximum 3 retries per sub-task before escalation

Phase 3: REVIEW
  → Evidence Collector does first-pass QA on each deliverable
  → Reality Checker does final production-readiness assessment
  → CEO gives final sign-off

Phase 4: DELIVER
  → Results compiled and presented
  → Experiment ledger saved (if Research Lab was involved)
  → Lessons learned documented
```

### Step 4: Output the Team Roster

Format the proposal as:

```
## Team Proposal

### Task
[One-line task description]

### Classification
- Domain: [domains identified]
- Mode: [Micro / Sprint / Full]
- Estimated effort: [time estimate]

### Proposed Team

| Role | Agent | Roster | Phase |
|------|-------|--------|-------|
| Leader | CEO | Core | 1-SCOPE |
| [Role] | [Agent] | [Roster] | [Phase] |
...

### Execution Plan
1. [Step 1]
2. [Step 2]
...

### Handoff Chain
[Agent] (task) → [Agent] (task) → [Agent] (task)
```

### Step 5: Activate the Team

Use the team-builder scripts to load agent personalities:

```bash
# List available agents in a division
bash {baseDir}/scripts/activate.sh --division engineering --list

# Load a specific agent's personality
bash {baseDir}/scripts/activate.sh --division engineering --agent frontend-developer

# Or generate the full proposal automatically
bash {baseDir}/scripts/plan.sh "Your task description here"
```

## Research Lab Integration

When the task involves optimization or iterative improvement:

1. Identify the metric (what are we optimizing?)
2. Identify the in-scope target (what file/config can we modify?)
3. Set the time budget (how long per experiment?)
4. Activate Research Lab with the autoresearch loop protocol
5. Pair with a domain specialist (AI Engineer, Image Prompt Engineer, etc.)

See `TEAM-RESEARCH.md` for the full autoresearch methodology and working examples.
