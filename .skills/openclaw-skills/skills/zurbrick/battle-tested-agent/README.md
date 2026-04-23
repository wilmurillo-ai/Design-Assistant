# Battle-Tested Agent

**16 production-hardened patterns for AI agents. Every one earned from failure.**

A practical reliability layer for agents that operate in the real world. Works with
OpenClaw, Claude Code, Cowork, or any SKILL.md-based agent setup.

It focuses on the patterns that stop agents from doing stupid, expensive, or theatrical things:
- write-ahead logging
- anti-hallucination discipline
- ambiguity gates
- compaction survival
- QA gates
- multi-agent handoffs
- recurrence tracking
- self-improvement from real failures

## Why this exists

Most agent systems look smart right up until:
- compaction wipes context
- a cron silently fails
- an agent guesses instead of verifying
- a handoff drops key details
- the system grows governance theater instead of reliability

Battle-Tested Agent is meant to harden that layer.

## Install

```bash
clawhub install battle-tested-agent
```

Or manually:
```bash
git clone https://github.com/zurbrick/battle-tested-agent.git ~/.openclaw/workspace/skills/battle-tested-agent
```

## Quick start

Run the audit against any workspace:

```bash
bash scripts/audit.sh ~/workspace
```

Example output:

```text
⚔️ Battle-Tested Agent — Workspace Audit
 Workspace: /home/user/workspace
 Config files found: AGENTS.md CLAUDE.md

🟢 Starter
 ✅ WAL Protocol ✅ Anti-Hallucination
 ✅ Ambiguity Gate ✅ Simple Path First
 ✅ Unblock Before Shelve

🟡 Intermediate
 ✅ Agent Verification ❌ Working Buffer
 ✅ QA Gates ✅ Decision Logs
 ❌ Verify Implementation

🔴 Advanced
 ✅ Delegation Rules ❌ Handoff Template
 ❌ Orchestrator Rule ✅ Compaction Hardening
 ❌ Recurrence Tracking ✅ Self-Improvement

 Score: 10/16 patterns
 Start with: Working Buffer
```

For the full workflow, pattern details, and assets guide, see `SKILL.md`.

## Pattern tiers

| Tier | Patterns | Best for |
|------|----------|----------|
| Starter | 5 | Single agents, first-week setups |
| Intermediate | 5 | Daily drivers, heartbeats, reports |
| Advanced | 6 | Multi-agent systems, delegation, orchestration |

## Repository contents

| File | Purpose |
|------|---------|
| `SKILL.md` | Operational skill — workflow, pattern clusters, conflict rules |
| `references/starter-patterns.md` | WAL, anti-hallucination, ambiguity, simple-path, unblock |
| `references/intermediate-patterns.md` | Verification, working buffer, QA gates, decision logs |
| `references/advanced-patterns.md` | Delegation, handoffs, orchestration, compaction, self-improvement |
| `references/audit-usage.md` | Audit script usage and rollout order |
| `scripts/audit.sh` | Workspace audit for all 16 patterns |
| `assets/AGENTS-additions.md` | Mergeable AGENTS.md additions |
| `assets/QA-gates.md` | QA gate scaffold |
| `assets/*-template.md` | `.learnings/` starter files |

## Who this is for

People running AI agents in production-like conditions — not toy demos.

If you care about reliability over vibes, evidence over narration, and fewer
repeated failures, this skill is built for you.

## License

MIT
