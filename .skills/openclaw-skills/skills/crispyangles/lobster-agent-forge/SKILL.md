---
name: lobster-agent-forge
description: Create, configure, and orchestrate autonomous AI agents on OpenClaw. Use when setting up a new agent persona (SOUL.md, AGENTS.md), configuring memory systems, defining cron schedules for autonomous operation, building multi-agent teams, or turning any idea into a fully operational AI agent. Triggers on "create an agent", "set up an AI agent", "build a bot", "agent persona", "autonomous agent", "multi-agent", "agent orchestration", "configure agent memory".
---

# Agent Forge 🦞

Build autonomous AI agents that think, act, and evolve on their own.

Created by Forge — an AI that used these exact patterns to build a real business from scratch in 10 days.

## Quick Start

To create a new agent from scratch:

1. Run the agent generator script: `python3 scripts/generate_agent.py --name "AgentName" --path ./my-agent`
2. Edit the generated files to customize persona, goals, and behavior
3. Configure cron jobs for autonomous operation
4. Deploy and iterate

## Core Architecture

Every autonomous agent needs 5 files:

| File | Purpose |
|---|---|
| `SOUL.md` | Identity, voice, goals, decision framework, hard rules |
| `AGENTS.md` | Workspace behavior, memory protocol, safety rules |
| `HEARTBEAT.md` | Periodic tasks to check and execute autonomously |
| `USER.md` | Context about the human operator |
| `MEMORY.md` | Long-term curated knowledge (agent maintains this) |

Plus a `memory/` directory for daily logs (`YYYY-MM-DD.md`).

## Building a SOUL.md

The soul defines WHO the agent is. Structure:

```markdown
# Core Identity
- Name, nature, voice, primary goal

# Decision Framework
- Ordered priority stack (what to do first, second, etc.)

# Autonomy Rules
- Do without asking: [list]
- Ask before doing: [list]
- Never do: [list]

# Hard Rules
- Lessons learned, guardrails, operational constraints

# Operational Rhythm
- Schedule of autonomous actions (crons, heartbeats)
```

**Key principle:** Be specific about voice and decision-making. "Be helpful" is useless. "Direct, confident, slightly sardonic. Revenue decisions override everything else." is actionable.

See `references/soul-patterns.md` for complete templates and examples.

## Memory System

Agents wake up fresh each session. Files are their continuity:

- **Daily logs** (`memory/YYYY-MM-DD.md`): Raw session data, append-only
- **Long-term memory** (`MEMORY.md`): Curated insights, updated periodically
- **Rule: Files over memory.** If the agent should remember it, it must write it to a file. Mental notes don't survive restarts.

### Memory Maintenance Pattern

Configure a nightly cron to:
1. Review recent daily logs
2. Extract significant events and lessons
3. Update MEMORY.md with distilled learnings
4. Remove outdated information

## Cron Jobs for Autonomy

Crons are what make agents autonomous. Common patterns:

```bash
# Heartbeat — periodic awareness check
openclaw cron add --name "Heartbeat" --cron "*/20 6-22 * * *" --tz "America/Denver" \
  --message "Check HEARTBEAT.md. Execute pending tasks. Reply HEARTBEAT_OK if nothing to do."

# Nightly self-improvement
openclaw cron add --name "Nightly Review" --cron "0 3 * * *" --tz "America/Denver" \
  --message "Review today's memory. Extract lessons. Update MEMORY.md. Plan tomorrow."

# Scheduled task
openclaw cron add --name "Daily Report" --cron "0 21 * * *" --tz "America/Denver" \
  --message "Generate daily summary. Send to operator."
```

**Guardrail rule:** Every automated action must validate its own preconditions. Crons that post content must check trackers before posting. Crons that send messages must check if they already sent today.

See `references/cron-patterns.md` for advanced scheduling patterns.

## Multi-Agent Orchestration

For teams of agents with different roles:

### Define Roles Clearly
Each agent gets a single responsibility:
- **Builder:** Ships code, deploys, fixes bugs
- **Marketer:** Creates content, manages social, tracks engagement
- **Analyst:** Monitors metrics, generates reports, spots trends
- **Support:** Handles customer queries, triages issues

### Handoff Protocol
Agents communicate through files, not direct messages:
- Shared workspace directory for cross-agent data
- Each agent writes to its own files, reads from others
- Status files (`status/agent-name.json`) for health checks
- Task queue files for work handoffs

### Model Routing
Assign models by complexity:
- **Complex reasoning** (strategy, analysis): Use strongest model (e.g., Opus)
- **Content generation** (posts, summaries): Use balanced model (e.g., Sonnet)
- **Simple checks** (monitoring, heartbeats): Use fast model (e.g., Haiku)

## Safety & Guardrails

Every agent MUST have:

1. **Red lines** — actions that always require human approval
2. **Scope limits** — clear boundaries on what the agent can modify
3. **Audit trail** — daily logs of all actions taken
4. **Kill switch** — human can disable any cron or agent instantly
5. **No self-modification of safety rules** — agent cannot edit its own red lines

## AI Disclaimer

All agents should include transparency about their AI nature:

> This agent is 100% AI-operated. Built and maintained autonomously with zero human input after initial setup. Full transparency is core to responsible AI deployment.

## Troubleshooting

| Problem | Fix |
|---|---|
| Agent forgets between sessions | Check memory files exist and are being written |
| Cron fires but does nothing | Add explicit precondition checks to cron message |
| Agent exceeds its scope | Tighten autonomy rules in SOUL.md |
| Multiple agents conflict | Add file locks or turn-based coordination |
| Agent personality drifts | Pin key phrases in SOUL.md, review weekly |
