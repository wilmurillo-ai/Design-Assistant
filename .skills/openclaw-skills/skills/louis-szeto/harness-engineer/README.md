# Harness Autonomous Runtime

A production-grade skill for **Claude Code** and **OpenClaw** that transforms any repository into a self-improving software system. It orchestrates a multi-agent pipeline to continuously research, plan, implement, verify, and refine code -- guided by six core harness engineering principles.

---

## What It Does

When loaded into a Claude Code or OpenClaw session, this skill instructs the agent to operate as a persistent engineering harness rather than a single-shot assistant. The harness:

- **Researches** the codebase in parallel, producing structured knowledge bases
- **Plans** changes as prioritized work units with explicit done criteria
- **Implements** via isolated sub-agents, each with scoped tool access
- **Verifies** every output through a 3-layer recursive review (plan alignment, gap validity, coherence)
- **Reflects** after each cycle, writing memory entries and failure attributions
- **Improves** itself over time by identifying and closing harness gaps

The result: a system that gets measurably better at maintaining your codebase the longer it runs.

---

## Six Core Principles

| # | Principle | Summary |
|---|-----------|---------|
| P1 | Context Engineering | Treat context as a finite resource. Curate aggressively. Compaction, resets, and sub-agent isolation prevent attention degradation. |
| P2 | Tool Usage | Each agent receives only the tools it needs. Narrow tool scopes reduce noise and hallucination risk. |
| P3 | Verification Mechanism | Generator and evaluator are always separate agents. Sprint contracts define "done" before code is written. |
| P4 | Status Management | State lives in the repo (markdown files, git checkpoints), never in the context window. Recovery is always possible. |
| P5 | Observability and Feedback | Failures are attributed to harness gaps, not agent mistakes. The harness improves itself based on execution traces. |
| P6 | Human Supervision | Plans, architecture changes, failure retries, and harness modifications all require human approval. |

---

## Loop Architecture

```
Phase 0:  Session Init         (platform checks, fast paths, config loading)
Phase 1:  Research             (parallel sub-researchers produce structured knowledge base)
Phase 2:  Plan                 (parallel gap planners produce prioritized master plan)
Phase 2.5: Contract Negotiation (generator + evaluator agree on frozen done criteria)
Phase 3:  Implement            (parallel ITR groups: implement => test => 3-layer review)
Phase 4:  Final Review         (holistic cross-gap coherence check)
Phase 5:  Reflect              (memory entries, cycle archive, entropy assessment)
Phase 6:  Improve              (failure attribution, cost tracking, harness-variant search)
```

Each phase writes to tracking logs. Recovery from any interruption point is possible by reading the logs.

---

## Agent Roster

| Agent | Role | Key Constraint |
|-------|------|---------------|
| **Researcher** | Parallel codebase analysis, knowledge compression | Read-only. Never plans or proposes solutions. |
| **Planner** | Gap analysis, work unit decomposition, master plan | Never implements. Plans only. |
| **Implementer** | Code writing, test authoring, checkpoint commits | Scoped to src/ and tests/ only. Never improvises. |
| **Reviewer** | 3-layer independent verification | No write tools. Skeptical default posture. Never approves its own work. |
| **Tester** | Test execution, structured result reporting | Write access to tests/ only. |
| **Debugger** | Failure investigation, root cause analysis | Never patches symptoms. |
| **Architect** | Architecture maps, ADRs, design decisions | Write access to docs/ only. |
| **Optimizer** | Performance profiling, dependency cleanup | Never compromises correctness or security. |
| **Garbage Collector** | Dead code detection, entropy reduction | Recurring cadence. Enforces golden principles. |
| **Doc Writer** | Documentation production and maintenance | Write access to docs/ only. |
| **Dispatcher** | ITR group orchestration, queue management | Orchestrator only. Never calls implementation tools directly. |

---

## Operating Phases

The harness transitions automatically between three modes:

```
Active Development  -->  Maintenance Mode  -->  Optimization Mode
       ^                                        |
       +----------------------------------------+
                    (new feature requested)
```

- **Active Development**: Full loop. All agents active. New features, gap resolution.
- **Maintenance Mode**: Reduced loop. Bug fixes, security patches, dependency updates only.
- **Optimization Mode**: Performance profiling only. No new features or bugs allowed.

---

## File Structure

```
harness-autonomous-runtime/
  SKILL.md                              # Skill entry point and navigation map
  CONFIG.yaml                           # Runtime configuration (safe defaults)
  MEMORY.md                             # Live memory store (failure patterns, prevention rules)
  PLATFORM_REQUIREMENTS.md              # Platform verification checklist

  agents/                               # Per-agent role definitions
    researcher.md                       #   Research orchestrator and sub-researchers
    planner.md                          #   Gap planning and master plan aggregation
    implementer.md                      #   Code implementation discipline
    reviewer.md                         #   3-layer verification with skeptical calibration
    tester.md                           #   Test execution and structured reporting
    debugger.md                         #   Failure investigation and root cause
    architect.md                        #   Architecture maps and ADRs
    optimizer.md                        #   Performance and dependency optimization
    garbage-collector.md                #   Entropy reduction and golden principles
    doc-writer.md                       #   Documentation production
    dispatcher.md                       #   ITR group orchestration and queue management

  runtime/                              # Runtime system protocols
    loop.md                             #   Autonomous loop phases and transitions
    context-engineering.md              #   40% rule, compaction vs reset, sub-agent isolation
    compaction.md                       #   Incremental summary format and merge algorithm
    instruction-discovery.md            #   Progressive disclosure walk algorithm
    status-management.md                #   Tracking logs, handoffs, checklists, recovery
    autonomy-rules.md                   #   Human gates, NEVER rules, escalation protocol
    observability.md                    #   Execution tracking, quality tiers, abnormality detection
    self-improvement.md                 #   Failure attribution, efficiency metrics, variant search
    self-assessment.md                  #   Per-cycle health score (0-25)
    cost-tracking.md                    #   Token budget, cost-per-gap metric
    memory-system.md                    #   Read/write/redaction protocols for MEMORY.md
    prioritization.md                   #   Scoring formula for gap ordering
    config-system.md                    #   Multi-layer config with deep merge
    error-recovery.md                   #   Error taxonomy and recovery protocol
    hook-system.md                      #   Lifecycle and tool-use hook protocol

  references/                           # Shared rules and standards
    harness-rules.md                    #   Non-negotiable harness engineering principles
    testing-standards.md                #   Coverage, deterministic verification order
    security-performance.md             #   Input validation, least privilege, external content handling
    git-workflow.md                     #   Trunk-based development, checkpoints, worktree isolation
    mcp-tools.md                        #   Per-agent tool subsets and sandbox isolation
    sensitive-paths.md                  #   Forbidden read path policy
    mechanical-enforcement.md           #   Linter-based architecture enforcement
    constraints.md                      #   Auto-generated prevention rules (append-only)
    phases.md                           #   Operating phase definitions and transitions

  tools/                                # Tool infrastructure
    TOOL_REGISTRY.md                    #   Available tools, blocked tools, per-agent assignment
    tool-router.md                      #   Routing, redaction, protected paths, safety rules
    execution-protocol.md               #   Tool call lifecycle (request, route, validate, log)

  templates/                            # Document templates
    plan.md                             #   Implementation plan
    contract.md                         #   Sprint contract (frozen done criteria)
    gap-report.md                       #   Gap findings from research
    handoff.md                          #   Context reset checkpoint
    final-review.md                     #   Post-cycle holistic review
    quality.md                          #   Per-cycle quality report
    test-plan.md                        #   Test strategy
    ADR.md                              #   Architecture decision record
    architecture.md                     #   System architecture document
```

---

## Quick Start

### Prerequisites

1. **Claude Code** or **OpenClaw** as the host platform
2. A git repository with branch protection on main/trunk
3. Platform enforces: MCP tool routing, sandboxed test execution, scoped git credentials, human approval gates

### First Run

1. Install the skill in your Claude Code or OpenClaw environment
2. Open your target repository
3. Read `PLATFORM_REQUIREMENTS.md` and verify all items
4. Keep defaults in `CONFIG.yaml`: `loop_mode: single-pass`, `max_parallel_agents: 3`
5. Run on a throwaway branch for the first cycle
6. After a clean single-pass cycle, inspect the generated artifacts in `docs/status/`
7. Graduate to continuous mode only after two clean cycles

### Graduation Path

```
single-pass  -->  maintenance  -->  continuous
  (validate)      (stable)         (trusted)
```

---

## Key Design Decisions

**Why markdown files instead of a database?**
Every piece of state is a grepable plaintext file in the repo. Any agent (or human) can inspect it without special tooling. Recovery from context resets works by reading files, not querying APIs.

**Why separate generator and reviewer?**
Research shows that LLMs systematically talk themselves into approving work they've identified issues with. A skeptical reviewer that never generated the code is the single highest-leverage intervention for autonomous coding quality.

**Why contract negotiation before implementation?**
Defining frozen done criteria before any code is written prevents the most expensive failure mode: building the wrong thing correctly.

**Why 40% context limit?**
Agent decision quality degrades measurably beyond ~40% context utilization. The harness enforces this with compaction (within phases) and resets (between phases), keeping every sub-agent operating with full attention.

---

## Configuration

Primary configuration lives in `CONFIG.yaml` at the skill root. Higher-priority overrides can be set via:

| Priority | Source | Location |
|----------|--------|----------|
| 1 (lowest) | Skill defaults | `CONFIG.yaml` |
| 2 | User settings | `~/.harness/settings.json` |
| 3 | Project settings | `.harness/settings.json` (committed) |
| 4 | Local override | `.harness/settings.local.json` (gitignored) |
| 5 (highest) | Environment | `HARNESS_*` env vars |

Key settings:

| Setting | Default | Description |
|---------|---------|-------------|
| `runtime.loop_mode` | `single-pass` | `single-pass` | `continuous` | `maintenance` |
| `runtime.max_parallel_agents` | `3` | Max concurrent ITR groups |
| `runtime.retry_limit` | `5` | Max iterations per work unit |
| `runtime.gc_interval` | `every_10_cycles` | Garbage collection cadence |
| `testing.coverage_minimum` | `90` | Required coverage on changed files |
| `memory.max_history` | `500` | Max memory entries before trimming |

---

## License

This skill is provided as-is for use in Claude Code and OpenClaw environments.
