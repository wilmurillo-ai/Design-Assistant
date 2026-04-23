---
name: team-builder
description: Discover, compose, and activate specialist teams from 3 rosters — OpenClaw Core (CEO/Artist), Agency Division (55+ specialists), and Research Lab (autonomous experiment loops via Karpathy's autoresearch). Planner proposes optimal teams; Reviewer validates deliverables.
metadata:
  {
    "openclaw":
      {
        "emoji": "🏗️",
        "requires": { "bins": ["bash"] },
      },
  }
---

# Team Builder

Compose the right team for any job by drawing from three rosters of specialists. The Research Lab uses Karpathy's [autoresearch](https://github.com/karpathy/autoresearch) methodology for autonomous experiment loops.

## Quick Start — Scripts

### 1. Browse available agents

```bash
bash {baseDir}/scripts/roster.sh                     # all 3 rosters
bash {baseDir}/scripts/roster.sh -r agency            # agency only
bash {baseDir}/scripts/roster.sh -d engineering        # one division
bash {baseDir}/scripts/roster.sh -s "frontend"         # search
bash {baseDir}/scripts/roster.sh -v                    # verbose descriptions
bash {baseDir}/scripts/roster.sh -j                    # JSON output
```

### 2. Generate a team proposal

```bash
bash {baseDir}/scripts/plan.sh "Build a portfolio dashboard with pie charts"
bash {baseDir}/scripts/plan.sh --mode sprint "Optimize image generation prompts using autoresearch"
bash {baseDir}/scripts/plan.sh -o proposal.md "Analyze astronomy photos for star classification"
```

The planner auto-detects task domains (engineering, creative, research, marketing, operations, spatial) and proposes the right-sized team (micro/sprint/full).

### 3. Activate a specialist

```bash
bash {baseDir}/scripts/activate.sh --division engineering --agent frontend-developer
bash {baseDir}/scripts/activate.sh --division testing --agent evidence-collector
bash {baseDir}/scripts/activate.sh --division testing --list
bash {baseDir}/scripts/activate.sh --file reference/agency-agents-main/design/design-ui-designer.md
bash {baseDir}/scripts/activate.sh --division engineering --agent ai-engineer --personality-only
```

Outputs the agent's full personality definition for use in delegation prompts.

### 4. Run QA review

```bash
bash {baseDir}/scripts/review.sh --task "Portfolio dashboard"
bash {baseDir}/scripts/review.sh --task "Image pipeline" --criteria criteria.txt --pass evidence
bash {baseDir}/scripts/review.sh --task "LLM training optimization" --pass reality
bash {baseDir}/scripts/review.sh --task "Full product" --pass both -o review.md
```

Generates review checklists (Evidence Collector Pass 1 + Reality Checker Pass 2) and logs to `~/.openclaw/team-reviews/`.

### 5. Run a Research Lab experiment

```bash
bash {baseDir}/scripts/experiment.sh --setup /path/to/project     # initialize experiment
bash {baseDir}/scripts/experiment.sh --run /path/to/project       # run one experiment cycle
bash {baseDir}/scripts/experiment.sh --status /path/to/project    # show ledger
```

See `references/TEAM-RESEARCH.md` for the full autoresearch methodology and working examples.

## The Three Rosters

### 1. Core Team (`references/TEAM-CORE.md`)
The permanent OpenClaw agents. Always available, always running.

| Agent | Role | Workspace |
|-------|------|-----------|
| **CEO** | Leader, orchestrator, final authority | `.openclaw/workspace/` |
| **Artist** | Image generation, visual analysis | `.openclaw/workspace-artist/` |

### 2. Agency Division (`references/TEAM-AGENCY.md`)
55+ specialist agents across 9 divisions. Activated on demand from `reference/agency-agents-main/`.

| Division | Agents | Key Specialists |
|----------|--------|-----------------|
| Engineering | 7 | Frontend Developer, Backend Architect, AI Engineer, DevOps |
| Design | 7 | UI Designer, UX Architect, Image Prompt Engineer |
| Marketing | 8 | Growth Hacker, Content Creator, Social Media |
| Product | 3 | Sprint Prioritizer, Trend Researcher, Feedback Synthesizer |
| Project Management | 5 | Senior PM, Studio Producer, Experiment Tracker |
| Testing | 7 | Evidence Collector, Reality Checker, API Tester |
| Support | 6 | Analytics Reporter, Finance Tracker, Legal Compliance |
| Spatial Computing | 6 | XR Architect, visionOS Engineer |
| Specialized | 7 | Agents Orchestrator, Data Analytics, LSP Engineer |

### 3. Research Lab (`references/TEAM-RESEARCH.md`)
Autonomous experiment loops adapted from Karpathy's [autoresearch](https://github.com/karpathy/autoresearch). Set up a measurable experiment, run it in a fixed time budget, keep improvements, discard failures, loop forever.

Source code reference: `reference/autoresearch-master/` (program.md, train.py, prepare.py)

## Cross-Team Workflow Examples

### Image Analysis + Research Loop
```
Artist (image acquisition) + Research Lab (analysis loop) + AI Engineer (classification)
```

### Visual Content Pipeline
```
Artist (generation) + Image Prompt Engineer (prompts) + Visual Storyteller (narrative)
```

### Dashboard / UI Feature Build
```
Senior PM (scope) + Frontend Developer (build) + Evidence Collector (QA)
```

### Autonomous LLM Training (autoresearch)
```
Research Lab (experiment loop on train.py) + AI Engineer (architecture suggestions)
→ 12 experiments/hour, ~100 overnight, fully autonomous
```

### Full Product Launch
```
CEO (orchestrate) + Engineering (build) + Design (UX) + Marketing (launch) + Testing (validate)
```

## Handoff Protocol

When passing work between specialists:

```
## Handoff
| Field | Value |
|-------|-------|
| From | [Agent Name] |
| To | [Agent Name] |
| Task | [What needs to be done] |
| Priority | [Critical / High / Medium / Low] |

## Context
- Current state: [What's been done]
- Relevant files: [File paths]

## Deliverable
- What is needed: [Specific output]
- Acceptance criteria:
  - [ ] [Criterion 1]
  - [ ] [Criterion 2]

## Quality
- Evidence required: [What proof looks like]
- Reviewer: [Who validates]
```

For complete handoff templates: `reference/agency-agents-main/strategy/coordination/handoff-templates.md`

## NEXUS Pipeline Modes

| Mode | Scale | Agents | Timeline |
|------|-------|--------|----------|
| **Micro** | Single task/fix | 1-3 | Hours-days |
| **Sprint** | Feature or MVP | 5-10 | 1-2 weeks |
| **Full** | Complete product | 10+ | Weeks-months |

## Reference Files

| File | Contents |
|------|----------|
| `SKILL.md` | This file — overview, scripts, quick start |
| `scripts/roster.sh` | Browse and search all agent rosters |
| `scripts/plan.sh` | Generate team proposals from task descriptions |
| `scripts/activate.sh` | Load agent personality definitions |
| `scripts/review.sh` | Generate QA review checklists |
| `scripts/experiment.sh` | Run autoresearch experiment loops |
| `references/TEAM-CORE.md` | CEO/Artist — roles and interactions |
| `references/TEAM-AGENCY.md` | All 55+ Agency specialists indexed by division |
| `references/TEAM-RESEARCH.md` | Autonomous experiment methodology (autoresearch) |
| `references/PLANNER.md` | Job analysis → team proposal workflow (detailed) |
| `references/REVIEWER.md` | QA validation workflow with quality gates |
| `references/PROOF-OF-WORK.md` | Example proposals showing cross-roster teams |
