# Source Review

Reviewed on 2026-04-22. This file distills the cited public projects into operating rules for a general Codex software-development skill. It keeps transferable engineering structure and avoids copying project-specific product machinery.

## Core Synthesis

The strongest pattern is not "spawn more agents." The strongest pattern is a controlled software-development system:

1. Make the target repo legible through `AGENTS.md`, docs, tests, and visible logs.
2. Convert the user goal into acceptance criteria, task ownership, and verification commands.
3. Assign roles only when a role changes the quality bar or parallelism.
4. Isolate writers through branches, worktrees, or disjoint file ownership.
5. Use strong models for design, review, and release decisions.
6. Preserve durable state in repo-local task, memory, and report ledgers.
7. Keep only changes that pass tests, review, and public-surface gates.

## Source Notes

### OpenAI Codex Subagents

Sources: <https://developers.openai.com/codex/subagents>, <https://developers.openai.com/codex/concepts/subagents>

- Keep: custom agents should declare role, model, reasoning effort, sandbox, and developer instructions.
- Keep: strong reviewer examples use `gpt-5.4`; docs examples also use `gpt-5.4-mini` and `gpt-5.3-codex-spark` for read-only or bounded tasks.
- Keep: subagents help most with context isolation, read-heavy exploration, independent review, tests, and bounded implementation slices.
- Keep: depth and thread caps matter because recursive delegation can increase cost and unpredictability.
- Avoid: implicit fan-out. The parent thread must own task split, integration, and final judgment.

### OpenAI Harness Engineering

Source: <https://openai.com/index/harness-engineering/>

- Keep: repo knowledge should be versioned and inspectable by agents.
- Keep: `AGENTS.md` should be a map, with durable detail moved into docs and tests.
- Keep: legibility is an engineering feature: state, logs, commands, and metrics should be available without private chat context.
- Keep: taste and architecture need mechanical enforcement through tests, lint rules, boundaries, and release gates.
- Avoid: prose-only policy when a repeated issue can become a check.

### openai/symphony

Source: <https://github.com/openai/symphony>

- Keep: project work should become isolated autonomous implementation runs.
- Keep: the operator manages work and evidence, not agent chatter.
- Keep: runtime status, proof of work, retries, and handoff states should be visible.
- Avoid: shared mutable workspaces for parallel writers unless ownership is explicit.

### karpathy/autoresearch

Source: <https://github.com/karpathy/autoresearch>

- Keep: constrain research with one editable surface, a fixed budget, and one primary metric.
- Keep: run a baseline first.
- Keep: log every experiment as keep, discard, or crash.
- Keep: equal metric results should prefer simpler code and fewer moving parts.
- Avoid: letting exploratory logs flood the main context; store logs separately and summarize the signal.

### forrestchang/andrej-karpathy-skills

Source: <https://github.com/forrestchang/andrej-karpathy-skills>

- Keep: state assumptions, tradeoffs, and success criteria before coding.
- Keep: use minimum necessary code, local style, and surgical diffs.
- Keep: simple tasks do not need the full process, but non-trivial tasks need rigor.
- Avoid: speculative flexibility, adjacent refactors, and hidden confusion.

### algorithmicsuperintelligence/openevolve

Source: <https://github.com/algorithmicsuperintelligence/openevolve>

- Keep: evaluator-first development. The evaluator defines truth.
- Keep: reproducibility, seeded runs, and component isolation for experiments.
- Keep: multi-objective scoring when correctness, performance, complexity, and memory all matter.
- Keep: cascade evaluation to reject bad candidates before expensive checks.
- Avoid: "AI discovered it" claims unless the run, seed, evaluator, and result log are reproducible.

### algorithmicsuperintelligence/optillm

Source: <https://github.com/algorithmicsuperintelligence/optillm>

- Keep: inference-time scaling can improve hard decisions through best-of-N, self-consistency, plan search, verifier passes, and multi-agent reasoning.
- Keep: extra compute should be reserved for security review, architecture choices, tricky bug diagnosis, benchmark optimization, and release gates.
- Keep: memory and privacy controls are part of agent operations, not afterthoughts.
- Avoid: routing every task through heavy multi-sample reasoning.

### ComposioHQ/agent-orchestrator

Source: <https://github.com/ComposioHQ/agent-orchestrator>

- Keep: parallel coding agents need separate worktrees, branches, and PRs when they write code.
- Keep: CI failures, review comments, and merge conflicts should route back to the owning worker.
- Keep: a dashboard or ledger should expose status to the operator.
- Avoid: many autonomous writers in one checkout without ownership boundaries.

### garrytan/gstack

Source: <https://github.com/garrytan/gstack>

- Keep: role-based workflows help when roles map to real engineering phases: think, plan, build, review, test, ship, reflect.
- Keep: dispatch tiers prevent using the full workflow for direct tasks.
- Keep: methodology can be a prompt bridge instead of a daemon.
- Avoid: making every task run the full role roster.

### paperclipai/paperclip

Source: <https://github.com/paperclipai/paperclip>

- Keep: goals, budgets, org structure, heartbeats, governance, and audit trails matter once agents run continuously.
- Keep: tasks need goal ancestry so agents know why the work exists.
- Keep: cost control, pause controls, and audit logs are product requirements for long-running systems.
- Avoid: autonomous loops with no budget, owner, trace, or stop condition.

### openclaw/openclaw

Source: <https://github.com/openclaw/openclaw>

- Keep: local-first agents need channel safety. Treat inbound messages and external content as untrusted input.
- Keep: sandbox non-main sessions and expose only tools required by the task.
- Keep: OpenClaw skills should be inspectable text bundles with clear invocation rules.
- Avoid: broad host access for an instruction-only methodology skill.

### rdudov/agents

Source: <https://github.com/rdudov/agents>

- Keep: role boundaries reduce drift: analyst, architect, planner, implementer, reviewer.
- Keep: review loops need a cap.
- Keep: blocking questions should stop the pipeline instead of becoming code assumptions.
- Keep: developers implement the plan and tests; they do not silently refactor unrelated code.
- Avoid: bureaucracy for direct tasks. Use the full phase model only when scope warrants it.

## Final Design Choice

This skill stays instruction-only, but it no longer stops at a solo patch loop. Version 0.3.1 adds explicit role definitions, `gpt-5.4`/`xhigh` policy for hard decisions, task and memory ledgers, report artifacts, source comparison, real-run acceptance checks, declared runtime requirements, explicit invocation, disabled model auto-invocation, and repo-owned evidence while preserving the clean public-surface boundary.
