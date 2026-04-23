# daily-reflection

An automated end-of-day reflection skill for OpenClaw agents. Runs nightly via cron, analyzes the day, builds long-term memory, detects recurring patterns, and prepares a morning briefing.

## What It Does

- **Analyzes the day** — completed tasks, bugs, communication quality
- **Extracts learnings** — up to 5 concrete learnings with behavior changes
- **Updates solution memory** — searchable bug/fix database for future sessions
- **Detects patterns** — recurring errors across 7 days
- **Writes morning briefing** — ready when you wake up
- **Rates session quality** — tracks improvement over time
- **Evaluates cron prompts** — self-optimizing system

## Setup

### 1. Install the skill

Copy to your skills directory:
```bash
cp -r daily-reflection ~/.openclaw/workspace/skills/
```

### 2. Create the cron job

In OpenClaw, create a cron job at 23:59 daily:
```
Schedule: 59 23 * * *
Message: "Run the daily-reflection skill: read ~/.openclaw/workspace/skills/daily-reflection/SKILL.md and execute all steps."
Session: isolated
Delivery: none
```

### 3. Enable morning briefing

Add to your AGENTS.md session startup:
```
Check if memory/morning-briefing.md exists with today's date → show it on first contact
```

## What Gets Created

```
memory/
├── YYYY-MM-DD.md          # Daily log with reflection
├── morning-briefing.md    # Tomorrow's briefing (overwritten daily)
├── patterns.md            # Recurring patterns
├── session-quality-log.md # Quality scores over time
├── briefings/
│   └── YYYY-MM-DD.md     # Archived briefings
└── solution_memory/
    └── [id].json          # Searchable bug database
```

## Why This Matters

Without reflection, agents repeat the same mistakes. This skill creates a feedback loop:
- Day 1: Make a mistake
- 23:59: Mistake logged as learning
- Day 2: Agent checks solution memory before similar task
- Result: Same mistake doesn't happen again

After 30 days, your agent has a searchable database of everything it learned.
