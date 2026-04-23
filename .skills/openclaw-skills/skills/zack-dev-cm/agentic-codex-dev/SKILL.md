---
name: agentic-codex-dev
description: Use when planning, implementing, reviewing, coordinating, or publishing agentic software development work with Codex, GitHub, and OpenClaw/ClawHub. Provides a production-grade multi-agent operating loop with role roster, model policy, task ledger, memory ledger, report artifacts, verification gates, and anti-bleed public-surface review.
version: 0.3.1
user-invocable: true
disable-model-invocation: true
metadata: {"openclaw":{"homepage":"https://github.com/zack-dev-cm/agentic-codex-dev-skill","requires":{"bins":["git","python3","clawhub"]},"tags":["codex","github","clawhub","agentic-development"]}}
---

# Agentic Codex Dev

Operate Codex like a disciplined software team: clear goal, explicit roles, scoped ownership, evidence, tests, review, report.

## When to Use

Use this skill for:

- coding tasks where Codex should inspect, modify, test, and report on a GitHub repo
- turning a rough product or bug request into scoped implementation work
- setting up repo-local `AGENTS.md`, `.codex/agents/`, or skill instructions
- reviewing agent-generated code for correctness, tests, security, and public-surface leaks
- preparing a GitHub repo or ClawHub skill for open-source publication
- coordinating explicit parallel/subagent work with role ownership and integration control

Do not use it for one-line answers, pure brainstorming, or tasks that only need a command output.

## Runtime Requirements

ClawHub requirement metadata for this skill declares `git`, `python3`, and `clawhub`, following the ClawHub skill metadata format at <https://github.com/openclaw/clawhub/blob/main/docs/skill-format.md>.

- Local plan, review, and implementation modes may work with the tools already available in the host.
- Verification and publish modes expect the declared binaries plus optional Python modules such as `antirot` and `codex_harness`.
- This skill should not request, print, or store credentials. GitHub and ClawHub publishing must use existing local authenticated CLI sessions, or the user must authenticate manually outside the prompt.
- Do not run `git push`, `clawhub publish`, or other remote-changing commands unless the user asked for publish or remote update work.

## Core Loop

1. Restate the goal and name the verification step before editing.
2. Read the repo map: `AGENTS.md`, README, package config, tests, and the files closest to the task.
3. Define concrete success criteria that would let a reviewer say "done".
4. Make the narrowest defensible change. Match local style. Avoid speculative abstractions.
5. Run the highest-signal local check. Add a focused smoke test when behavior changed.
6. Review the diff for bugs, regressions, secrets, private paths, and public-surface bleed.
7. Report what changed, how it was verified, and any residual risk.

If the task is unclear, stop early and name the ambiguity. Prefer one precise question over guessing.

## Operating Rules

- Treat repository files as the source of truth. If knowledge matters later, put it in repo docs.
- Keep `AGENTS.md` short. Use it as an index to durable docs, not a giant prompt.
- Prefer boring, inspectable code over opaque magic. Agents compound what they can read.
- Touch only files required for the goal. Mention unrelated problems; do not fix them unless asked.
- Use structured APIs, tests, and parsers where available. Avoid fragile string tricks.
- Convert repeated review feedback into checks, docs, or templates.
- Keep logs and long command output out of the main narrative; summarize the signal.
- Avoid asking an agent to read undeclared secret files or sync credentials as part of a skill.

## Scope Modes

Pick the mode that fits the risk:

- **Patch**: one bug or one focused feature. Read close code, edit, test, review.
- **Plan**: ambiguous or multi-file work. Write a short acceptance plan before editing.
- **Review**: findings first, with emphasis on correctness, regressions, security, tests, and leaks as summarized in [source review](references/source-review.md).
- **Harness**: improve repo legibility: docs, CI, local scripts, custom agents, or audit gates.
- **Evolve**: metric-driven optimization. One variable per experiment, fixed budget, log keep/discard.
- **Publish**: GitHub/ClawHub release readiness, metadata, license, docs, and verification.
- **Multi-Agent**: explicit role roster, task ledger, isolation plan, review gates, memory update, and final report.

Prefer Patch unless the task shows it needs more structure. Use Multi-Agent only when the user explicitly asks for subagents, delegation, or parallel agent work.

## System Design

For non-trivial or multi-agent work, set up a control plane before coding:

- **Orchestrator**: the main Codex thread owns requirements, task split, agent selection, integration, final review, and user communication.
- **Role agents**: subagents are optional workers with declared purpose, model, reasoning effort, sandbox, file ownership, and output schema.
- **Artifacts**: use repo-local ledgers so work survives context loss and can be reviewed without private chat history.
- **Isolation**: prefer branches or worktrees per writer when multiple agents edit. If one checkout is shared, assign disjoint file ownership.
- **Gates**: no task is done until its acceptance criteria, verification command, diff review, public-surface scan, and report entry are complete.

When this structure is overkill, keep a solo Patch flow and still preserve the same verification discipline.

## Task, Memory, and Report Ledgers

Create or update these artifacts when work is multi-agent, multi-turn, risky, or intended for publication:

- `docs/agentic/tasks.md`: task id, owner role, goal, owned files, status, acceptance criteria, verification, result, blocker.
- `docs/agentic/memory.md`: stable repo facts, architecture decisions, commands that actually work, hazards, rejected approaches, last-verified date. Do not store secrets, tokens, private paths, or raw logs.
- `docs/agentic/reports/<date>-<slug>.md`: final objective, source links, task outcomes, changed files, tests, review findings, unresolved risks, release or PR status.

If the target repo already has equivalent docs, use the local convention instead of inventing new paths.

## Role Roster

Use this roster as the default multi-agent team. The parent thread stays responsible for coordination and final judgment.

| Role | Default model | Reasoning | Scope | Required output |
| --- | --- | --- | --- | --- |
| Orchestrator | `gpt-5.4` | `xhigh` for critical design/release, `high` otherwise | Owns task split, integration, report | plan, assignments, final decision |
| Analyst | `gpt-5.4` | `high` | Turns vague request into requirements and risks | assumptions, open questions, acceptance criteria |
| Architect | `gpt-5.4` | `xhigh` | System design, boundaries, dependency choices | design note, rejected options, invariants |
| Planner | `gpt-5.4` | `high` | Breaks design into ordered tasks | task ledger rows with owners and gates |
| Explorer | `gpt-5.4-mini` or `gpt-5.3-codex-spark` | `medium` | Read-only code mapping and evidence gathering | files, symbols, execution path, uncertainty |
| Implementer | `gpt-5.4` for risky code, `gpt-5.3-codex-spark` for bounded edits | `high` or `medium` | Writes only owned files | patch summary, tests, residual risks |
| Reviewer | `gpt-5.4` | `xhigh` | Correctness, security, regressions, tests, public surface | findings first, file/line evidence, verdict |
| QA/CI Analyst | `gpt-5.4` | `high` | Reproduction, failing checks, browser or CLI evidence | exact command, observed failure, fix owner |
| Memory Curator | `gpt-5.4-mini` | `medium` | Updates durable docs after decisions land | memory entries, stale entries removed |

## Subagents

Only use subagents when the user explicitly asks for subagents, delegation, or parallel agent work.

Good delegation targets:

- read-heavy codebase mapping
- independent test or CI-log analysis
- independent review categories such as security, test gaps, or docs correctness
- disjoint implementation slices with clearly separate file ownership

Bad delegation targets:

- the immediate blocker for your next local step
- tightly coupled edits in the same files
- vague "go improve the code" work
- recursive fan-out with no cap

When delegating, give each agent a bounded task, a clear output shape, and explicit ownership. Keep the main thread focused on requirements, decisions, integration, and final review. Keep `agents.max_depth = 1` unless the user explicitly accepts recursive delegation risk; this matches the Codex subagent configuration surface documented at <https://developers.openai.com/codex/subagents>.

Delegation prompt shape:

```text
Role: reviewer
Model: gpt-5.4
Reasoning: xhigh
Ownership: read-only review of <files or branch>
Task: find correctness, security, regression, test, and public-surface risks.
Output: findings first with file/line evidence, then open questions, then verdict.
Do not edit files. Do not inspect secrets. Do not broaden scope.
```

## Model Policy

- Use `gpt-5.4` with `xhigh` reasoning for architecture, security review, release decisions, and ambiguous multi-agent coordination; Codex custom-agent examples document `gpt-5.4` reviewer roles at <https://developers.openai.com/codex/subagents>.
- Use `gpt-5.4` with `high` reasoning for implementation where correctness or cross-module behavior matters; model selection follows the Codex custom-agent configuration surface at <https://developers.openai.com/codex/subagents>.
- Use `gpt-5.4-mini` or `gpt-5.3-codex-spark` for read-only exploration, docs checks, and bounded cleanup where speed matters and the output will be reviewed; both model families appear in Codex custom-agent examples at <https://developers.openai.com/codex/subagents>.
- Do not use a budget model for final architecture, security, or publish verdicts.
- Use extra compute selectively: best-of-N, independent reviewer passes, or verifier checks only when the decision is expensive to reverse; optillm documents inference-time scaling techniques at <https://github.com/algorithmicsuperintelligence/optillm>.

## Implementation Discipline

Before editing:

- inspect the existing patterns
- identify the likely tests or smoke command
- check dirty git state and avoid touching unrelated user changes
- state the planned edit in one or two sentences

While editing:

- keep the diff surgical
- add tests when behavior, contracts, or public output changes
- avoid new dependencies unless they clearly reduce risk or complexity
- keep comments rare and useful

After editing:

- run the named verification
- inspect the diff, not just test output
- update docs only when user-facing behavior or workflow changed
- do not call work published until the public surface is clean

## Review Checklist

Review every non-trivial result for:

- Does every changed line trace to the stated goal?
- Are edge cases covered by tests or a clear smoke path?
- Did the change preserve existing public APIs and CLI behavior?
- Did docs/examples drift from actual behavior?
- Did any secret-like string, local path, private URL, copied dashboard, or stale release note enter the repo?
- Did the final diff remove avoidable complexity from the first draft, as recommended in [source review](references/source-review.md)?

## Consistency and Effectiveness Gates

For multi-agent work, verify the process itself:

- Every task has an owner, owned files, acceptance criteria, verification command, and result.
- Every subagent output is mapped to a task or explicitly discarded with a reason.
- No writer agent edits outside its assigned ownership without parent approval.
- At least one reviewer pass is read-only and independent of the implementer.
- The final report names changed files, commands run, failed checks, source links, residual risk, and release status.
- Memory updates contain stable facts only; do not store raw chat, secrets, local credentials, or transient logs.
- If a metric-driven change is attempted, record baseline, candidate, verifier, result, and keep/discard decision.

## Real Example Eval

For a serious workflow eval, run this skill against a real repo task and archive the result in the report ledger. A valid eval has:

- baseline repo state and user goal
- role roster used, including model and reasoning choices
- task ledger rows with owners and file boundaries
- at least one implementation or review task with verification output
- public-surface scan for private paths, local URLs, tokens, and stale claims
- final report with changed files, tests, residual risks, and follow-up blockers

Use [example run](references/example-run.md) as the minimum acceptance shape.

## GitHub and ClawHub Publish Gate

Before publishing:

- README or skill summary says what it does, when to use it, and what it does not do.
- License is compatible with the target surface. ClawHub publishes skills under MIT-0.
- `SKILL.md` has frontmatter `name`, `description`, and `version`.
- The skill folder contains only text-based files needed at runtime.
- No hidden install scripts, credential readers, service restarts, or local machine assumptions.
- Public repo has security, contribution, support, CI, and release/audit checks when applicable.
- Run the repo's public-surface gate before pushing or publishing to a registry.

For this skill's source analysis, read `references/source-review.md` and `references/comparison-matrix.md`.
For multi-agent artifacts and templates, read `references/system-design.md`.
For release commands and manual checks, read `references/publish-checklist.md`.
