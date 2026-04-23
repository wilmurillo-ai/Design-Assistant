# Example Run

This is the minimum shape for a real eval of the skill. It is intentionally concrete enough to review and general enough to run on any public repository.

## Scenario

Goal: upgrade an instruction-only Codex skill from a generic patch workflow into a multi-agent software-development operating loop.

Acceptance:

- `SKILL.md` includes system design, role roster, model policy, task ledger, memory ledger, report ledger, consistency gates, and real-run eval guidance.
- Source comparison covers all cited public projects.
- Custom agent configs declare models and reasoning effort.
- Public-surface tests fail if role/model/system-design coverage is removed.
- Anti-bleed scan includes Python files.
- Local verification passes, with any CI or publish blocker named explicitly.

## Role Roster Used

| Role | Model | Reasoning | Purpose |
| --- | --- | --- | --- |
| Orchestrator | `gpt-5.4` | `xhigh` | own requirements, source synthesis, implementation, final report |
| Architect | `gpt-5.4` | `xhigh` | validate system design and role boundaries |
| Implementer | `gpt-5.4` | `high` | edit skill, references, docs, tests, metadata |
| Reviewer | `gpt-5.4` | `xhigh` | check correctness, public surface, test coverage, publish risk |
| Memory Curator | `gpt-5.4-mini` | `medium` | update durable docs after verification |

## Task Ledger Sample

| ID | Owner | Files | Status | Acceptance | Verification | Result | Blocker |
| --- | --- | --- | --- | --- | --- | --- | --- |
| T1 | architect | `SKILL.md`, `references/system-design.md` | done | system design and role roster are explicit | public-surface tests | pending until local run | none |
| T2 | implementer | `tests/test_public_surface.py` | done | Python files are scanned for bleed | unit tests | pending until local run | none |
| T3 | reviewer | public repo surface | review | no private paths, tokens, local URLs, stale version claims | anti-bleed and AntiRot | pending until local run | CI workflow depends on token scope |

## Memory Ledger Sample

Stable facts:

- Runtime skill files are text-only and publish through ClawHub.
- `.clawhubignore` excludes repo harness files from the public skill bundle.
- GitHub Actions workflow creation may require token scope outside the normal repo push permission.

Decisions:

- Keep the skill instruction-only. Add templates and tests rather than a daemon.
- Use `gpt-5.4`/`xhigh` for architecture and reviewer roles; use faster models only for reviewed, read-only work.

Hazards:

- Do not claim CI enforcement unless the workflow exists in the remote repository.
- Do not let public examples include private paths, local URLs, tokens, or copied chat logs.

## Report Sample

Objective: release version 0.3.1 with multi-agent operating structure, declared runtime requirements, explicit invocation, disabled model auto-invocation, and repo-owned real-run evidence.

Sources: OpenAI Codex subagents, OpenAI harness engineering, optillm, openevolve, autoresearch, symphony, paperclip, gstack, OpenClaw, Andrej Karpathy skills, agent-orchestrator, rdudov agents.

Changed files:

- `SKILL.md`
- `references/source-review.md`
- `references/comparison-matrix.md`
- `references/system-design.md`
- `references/example-run.md`
- `.codex/agents/*.toml`
- `tests/test_public_surface.py`

Verification:

- `python3 -m unittest discover -s tests`
- `python3 -m antirot.cli lint SKILL.md --strict`
- `python3 -m codex_harness audit . --strict --min-score 90`
- `clawhub inspect agentic-codex-dev --files` after publish

Residual risks:

- CI cannot be considered enforced until the remote repository has a workflow.
- Any future source review must re-check the public URLs because repository behavior can change.
