# System Design

Use this reference when a task needs explicit multi-agent coordination, durable memory, or release-grade reporting.

## Control Plane

The parent Codex thread is the control plane. It owns:

- goal restatement and acceptance criteria
- mode selection: Patch, Plan, Review, Harness, Evolve, Publish, or Multi-Agent
- role roster and model choices
- task ledger creation and updates
- agent assignment and isolation plan
- integration of results into one coherent diff
- final review, verification, report, and release decision

Subagents are execution units. They do not own the final answer, final architecture, or publish verdict.

## Artifact Layout

Prefer existing repo conventions. If none exist, use:

```text
docs/agentic/
  tasks.md
  memory.md
  reports/
    <date>-<slug>.md
```

### Task Ledger

```markdown
# Task Ledger

| ID | Owner | Files | Status | Acceptance | Verification | Result | Blocker |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T1 | architect | docs/architecture.md | planned | boundary decision recorded | review only | pending | none |
```

Rules:

- one owner per row
- writable files must be named before implementation
- status is one of `planned`, `active`, `blocked`, `review`, `done`, `discarded`
- verification must be a command, manual check, or reviewer gate
- discarded work needs a reason

### Memory Ledger

```markdown
# Memory Ledger

## Stable Facts

- The public API entry point is `<symbol>`; last verified on `<date>` with `<command>`.

## Decisions

- Use `<approach>` because `<reason>`. Rejected `<alternative>` because `<reason>`.

## Hazards

- Do not touch `<surface>` without running `<check>`.
```

Rules:

- store stable facts, decisions, commands, and hazards
- do not store secrets, private endpoints, local machine paths, raw logs, or copied chat
- include last-verified dates for facts that can decay
- remove stale facts instead of appending contradictions

### Report

```markdown
# Agentic Report: <goal>

## Objective

## Sources

## Tasks

## Changed Files

## Verification

## Review Findings

## Memory Updates

## Residual Risks

## Release Status
```

Rules:

- every completed task has a report entry
- every failed command is named with the reason it failed or the follow-up owner
- final status is one of `not ready`, `ready for PR`, `ready to publish`, or `published`

## Assignment Template

```text
Role: <architect|explorer|implementer|reviewer|qa|memory-curator>
Model: <model id>
Reasoning: <effort>
Sandbox: <read-only|workspace-write>
Owned files: <paths or read-only surface>
Task: <one bounded objective>
Acceptance: <observable done condition>
Verification: <command or check>
Output: <required sections>
Constraints: do not inspect secrets; do not broaden scope; do not edit outside ownership.
```

## Isolation Policy

- Read-only agents may share a checkout.
- Writer agents should use separate branches or worktrees when parallel edits are possible.
- If writers share a checkout, file ownership must be disjoint and recorded in the task ledger.
- CI failures and review comments go back to the owner of the task that introduced the change.
- The parent resolves conflicts and merges, then runs final verification.

## Stop Conditions

Stop and ask the user, or downgrade to a plan-only result, when:

- acceptance criteria cannot be stated
- required secrets, accounts, paid resources, or private dashboards are unavailable
- two agents need to edit the same files without a safe order
- tests cannot run and no credible manual verifier exists
- security or public-surface scan finds unresolved leaks
