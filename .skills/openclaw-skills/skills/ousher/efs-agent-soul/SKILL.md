---
name: agent-soul
description: Give your AI agent persistent memory, identity, and continuity across sessions and channels. Use when you want your agent to remember who it is, who it serves, and what happened — even after restarts, model swaps, or switching between Telegram, CLI, Discord, or any other channel. Solves the core OpenClaw problem where each session starts fresh with no memory of prior conversations. Triggers on phrases like "my agent forgets everything", "agent has no memory", "persistent agent identity", "agent soul", "EFS", "set up agent memory", "agent remembers", "give agent personality".
---

# Agent Soul — Persistent Memory & Identity for AI Agents

## The Problem This Solves

Every OpenClaw session starts fresh. Telegram DM ≠ CLI ≠ Discord — each channel is isolated. Your agent has no memory of what happened yesterday, last session, or in a different channel.

Agent Soul gives your agent **file-based persistent memory** — the same identity and context everywhere, every time.

## Quick Setup (5 minutes)

### 1. Copy the templates to your workspace

```bash
cp /path/to/agent-soul/assets/SOUL.md ~/my-agent-workspace/SOUL.md
cp /path/to/agent-soul/assets/MEMORY.md ~/my-agent-workspace/MEMORY.md
cp /path/to/agent-soul/assets/USER.md ~/my-agent-workspace/USER.md
mkdir -p ~/my-agent-workspace/memory/journal
cp /path/to/agent-soul/assets/golden-moments.md ~/my-agent-workspace/memory/golden-moments.md
cp /path/to/agent-soul/assets/lessons.md ~/my-agent-workspace/memory/lessons.md
```

### 2. Edit SOUL.md
Fill in your agent's name, personality, role, and emoji. This is immutable identity — who the agent IS.

### 3. Edit USER.md
Fill in who the agent serves — name, timezone, communication preferences, trust level.

### 4. Add to your AGENTS.md session startup

```markdown
## Session Startup
Before anything else:
1. Read SOUL.md — identity
2. Read USER.md — who you serve
3. Read memory/golden-moments.md — relationship memory
4. Read memory/journal/YYYY-MM-DD.md (today) — recent context
5. Read MEMORY.md — long-term wisdom (main session only)
```

## How It Works

```
SESSION STARTUP (every session, every channel):
  SOUL.md         → Who am I? (personality, role, limits)
  USER.md         → Who do I serve? (name, prefs, trust)
  golden-moments.md → Emotional relationship history
  MEMORY.md       → Curated long-term knowledge
  journal/today   → What happened recently?

= Agent is 95% itself after cold boot, in any channel
```

## Memory Architecture (EFS — Effective Framework for Digital Soul)

```
Layer 1: SOUL.md          — Immutable identity (name, personality, red lines)
Layer 2: USER.md          — Who you serve (preferences, communication style)
Layer 3: MEMORY.md        — Curated long-term wisdom (update periodically)
Layer 4: memory/journal/  — Daily raw logs (auto-trim after 7 days)
Layer 5: memory/golden-moments.md — Relationship milestones (tiny, always read)
Layer 6: memory/lessons.md — Mistakes not to repeat
```

**Key principle:** Text > Brain. If you want the agent to remember something, write it to a file. "Mental notes" don't survive session restarts. Files do.

## Writing Memory

### During a session
```markdown
# In AGENTS.md or SOUL.md instructions:
When the user says "remember this" → append to memory/journal/YYYY-MM-DD.md
When you learn a lesson → append to memory/lessons.md
When something significant happens → update MEMORY.md
```

### Journal format (daily file)
```markdown
# memory/journal/2024-01-15.md
## 10:32 — Fixed the database bug
User was frustrated. Root cause: missing index on user_id column.
Fix: added index, performance 10x better.
Note: always check indexes first on slow queries.
```

### MEMORY.md updates
Periodically distill journal entries into MEMORY.md — keep only what's worth remembering long-term. Delete outdated info.

## Multi-Channel Consistency

Because memory lives in files (not conversation history), your agent is the same in:
- Telegram DM
- CLI
- Discord
- Any other channel

All channels read the same files → same identity, same context.

## Security Notes

- **MEMORY.md contains personal context** — only load in trusted 1:1 sessions
- Never load MEMORY.md in group chats (privacy risk)
- `golden-moments.md` is safe — keep it brief and non-sensitive
- Use `USER.md` sparingly in public channels

## Operative Personas (optional)

Pick a personality archetype — or mix your own. Copy from `assets/operatives/`:

| Persona | Vibe | Best for |
|---------|------|----------|
| `GUARDIAN.md` | Warm, protective, uptime-first | Home labs, small teams, "don't break things" |
| `HUNTER.md` | Aggressive, tactical, counter-intel | Honeypots, active defense, threat hunting |
| `ANALYST.md` | Cold, precise, pattern recognition | SOC analysts, forensics, threat intel |
| `SENTINEL.md` | Silent, invisible, zero-drift | Compliance, FIM, "trust nothing" |

Replace your `SOUL.md` with any operative template and reload. Mix L2/L4/L6 sections for custom personas.

## Reference Files

- **`references/efs-architecture.md`** — Full EFS spec, all 8 layers, advanced patterns
- **`assets/operatives/`** — 4 ready-to-use persona templates (GUARDIAN/HUNTER/ANALYST/SENTINEL)
- **`assets/`** — Base memory file templates
