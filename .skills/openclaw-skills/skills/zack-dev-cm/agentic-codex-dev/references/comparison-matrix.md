# Comparison Matrix

Reviewed on 2026-04-22. Use this matrix when judging whether the skill is strong enough for multi-agent software development rather than a generic coding checklist.

| Source | Strong pattern | Risk if copied blindly | Skill response |
| --- | --- | --- | --- |
| OpenAI Codex subagents | Custom roles with model, reasoning, sandbox, and developer instructions | More agents can add cost and coordination failure | Subagents require explicit user intent, role ownership, and parent integration |
| OpenAI Codex concepts | Context isolation and parallel investigation | Delegation can hide the critical path | Parent keeps immediate blockers local and uses agents for side work |
| OpenAI harness engineering | Repo-local memory, docs, tests, and legible state | Prose policy can drift without checks | Task, memory, report ledgers plus public-surface tests |
| openai/symphony | Isolated implementation runs | Workflow engine complexity may exceed need | Use branches/worktrees for writers; do not require a daemon |
| karpathy/autoresearch | Baseline, budget, one metric, keep/discard/crash log | Research framing may not fit product work | Apply evaluator-first discipline only when optimizing behavior |
| forrestchang/andrej-karpathy-skills | Assumptions, tradeoffs, surgical diffs | Too little structure for multi-agent runs | Keep the concise style, add role roster and ledgers only for serious work |
| openevolve | Reproducible evaluator-first evolution, Pareto tradeoffs, cascade checks | Claims can outrun evidence | Require baseline, verifier, result log, and keep/discard decision |
| optillm | Inference-time scaling, verifier passes, multi-agent reasoning | Expensive compute can become default theater | Reserve `gpt-5.4`/`xhigh` and independent reviewers for hard decisions |
| agent-orchestrator | Worktree isolation, CI/review feedback routed to owner | Autonomous fleets need heavy operations | Adopt ownership and feedback routing without requiring its platform |
| gstack | Clear role taxonomy and dispatch tiers | Full role stack for every task slows direct fixes | Scope modes decide when to use Patch vs Multi-Agent |
| paperclip | Goals, budgets, heartbeats, org chart, audit trail | Continuous autonomy can run away | Add owner, budget/risk thinking, stop conditions, and reports |
| openclaw | Local-first assistant, skills, sandbox and channel safety | Broad host access is unnecessary for a methodology skill | Keep bundle instruction-only and public-surface clean |
| rdudov/agents | Analyst, architect, planner, developer, reviewer boundaries | Rigid phase gates can create process drag | Use roles when the task is ambiguous, risky, or parallel |

## Previous Version Weak Points

Version 0.1.2 was useful as a publish-clean patch loop, but it was not enough for the stated goal of multi-agent software development:

- no explicit role roster with model and reasoning policy
- no default use of `gpt-5.4`/`xhigh` for architecture, review, and release decisions
- no system design for orchestration, isolation, ledgers, or reports
- no task ledger, memory ledger, or report artifact
- no real-run eval shape
- no process consistency checks that tie agent outputs to tasks and verification
- no test ratchet for role/model/system-design coverage
- bleed scan omitted Python files

## Target Bar

A release is acceptable only when a reviewer can see:

- the role roster and model policy in `SKILL.md`
- source-by-source comparison in this file
- system design templates in `references/system-design.md`
- real-run acceptance shape in `references/example-run.md`
- automated tests that fail if the public skill regresses to a generic patch loop
- anti-bleed coverage that includes Python test and helper files
