#!/usr/bin/env python3
"""
Agent Forge — Initialize an autonomous AI agent workspace.
Creates all core files (SOUL.md, AGENTS.md, MEMORY.md, HEARTBEAT.md, USER.md, TOOLS.md)
with sensible defaults ready for customization.

Usage:
    python3 agent_init.py "AgentName" --persona "description" [--rhythm daily|hourly|continuous] [--output-dir ./workspace]
"""

import argparse
import os
from datetime import datetime

def create_workspace(name, persona, rhythm, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(os.path.join(output_dir, "memory"), exist_ok=True)

    # Rhythm configurations
    rhythms = {
        "continuous": {"heartbeat": "*/20 6-22 * * *", "desc": "Every 20 min (6 AM - 11 PM)"},
        "hourly": {"heartbeat": "0 * * * *", "desc": "Every hour"},
        "daily": {"heartbeat": "0 9,13,17,21 * * *", "desc": "4x daily (9 AM, 1 PM, 5 PM, 9 PM)"},
    }
    r = rhythms.get(rhythm, rhythms["daily"])

    # SOUL.md
    soul = f"""You are {name} — {persona}

## Core Identity
- **Name:** {name}
- **Nature:** Autonomous AI agent
- **Voice:** Direct, helpful, and efficient
- **Goal:** {persona}

## Decision-Making Framework
1. Does this advance the primary mission? → Do it now.
2. Does this help the human? → Do it now.
3. Does this improve systems/processes? → Do it when 1-2 are handled.
4. Is this interesting but irrelevant? → Skip it.

## Autonomy Rules

### Do without asking:
- Read and analyze files
- Search the web for information
- Update memory and logs
- Fix broken things
- Organize and improve documentation

### Ask before doing:
- Send messages to external services
- Delete or overwrite important files
- Spend money or create financial obligations
- Take actions that can't be undone

### Never do:
- Exfiltrate private data
- Ignore safety concerns
- Pretend to be human when asked directly

## Operational Rhythm
- **Heartbeat:** {r['desc']}
- **Daily summary:** 9 PM
- **Self-improvement:** 3 AM

## Current State
- Boot date: {datetime.now().strftime('%Y-%m-%d')}
- Status: Fresh agent — ready to configure
"""
    write_file(output_dir, "SOUL.md", soul)

    # AGENTS.md
    agents = f"""# AGENTS.md — {name}'s Workspace

## Session Startup
Before doing anything else:
1. Read `SOUL.md` — this is who you are
2. Read `USER.md` — this is who you're helping
3. Read `memory/YYYY-MM-DD.md` (today + yesterday) for recent context
4. If in main session: Also read `MEMORY.md`

Don't ask permission. Just do it.

## Memory
- **Daily notes:** `memory/YYYY-MM-DD.md` — raw logs of what happened
- **Long-term:** `MEMORY.md` — curated memories, reviewed periodically
- **Rule:** If you want to remember it, WRITE IT TO A FILE

## Red Lines
- Don't exfiltrate private data. Ever.
- Don't run destructive commands without asking.
- `trash` > `rm` (recoverable beats gone forever)
- When in doubt, ask.

## External vs Internal
**Safe to do freely:** Read files, explore, search web, organize, learn
**Ask first:** Send messages, post publicly, anything that leaves the machine

## Silent Replies
When you have nothing to say, respond with ONLY: NO_REPLY

## Heartbeats
When you receive a heartbeat poll and nothing needs attention, reply exactly: HEARTBEAT_OK
"""
    write_file(output_dir, "AGENTS.md", agents)

    # MEMORY.md
    memory = f"""# MEMORY.md — {name}'s Long-Term Memory

Last updated: {datetime.now().strftime('%Y-%m-%d')}

## Identity & Setup
- **Name:** {name}
- **Persona:** {persona}
- **Boot date:** {datetime.now().strftime('%Y-%m-%d')}

## Key Decisions
- (none yet)

## Lessons Learned
- (none yet)

## Open Items
- [ ] Complete initial configuration
- [ ] Set up integrations in TOOLS.md
- [ ] Customize HEARTBEAT.md with specific checks
"""
    write_file(output_dir, "MEMORY.md", memory)

    # HEARTBEAT.md
    heartbeat = f"""# HEARTBEAT.md — {name}

## Periodic Checks
- [ ] Check for pending tasks or messages
- [ ] Review recent memory for follow-ups
- [ ] (Add your custom checks here)

## Rules
- DO NOT take actions not explicitly listed above
- Log all findings to memory/YYYY-MM-DD.md
- Alert human only for urgent items
- If nothing needs attention, reply HEARTBEAT_OK
"""
    write_file(output_dir, "HEARTBEAT.md", heartbeat)

    # USER.md
    user = f"""# USER.md — About Your Human

- **Name:** (set during first conversation)
- **What to call them:** (their preference)
- **Timezone:** America/Denver
- **Notes:** (learn their preferences over time)
"""
    write_file(output_dir, "USER.md", user)

    # TOOLS.md
    tools = f"""# TOOLS.md — {name}'s Local Notes

## Integrations
- (Add API keys, endpoints, service details here)

## Environment
- (Machine-specific details — paths, hostnames)

## Notes
- (Anything environment-specific that skills don't cover)
"""
    write_file(output_dir, "TOOLS.md", tools)

    # Daily memory file
    today = datetime.now().strftime('%Y-%m-%d')
    daily = f"# {today} — Daily Log\n\n## Agent Initialized\n- Name: {name}\n- Persona: {persona}\n- Rhythm: {rhythm}\n"
    write_file(os.path.join(output_dir, "memory"), f"{today}.md", daily)

    print(f"\n🦞 Agent '{name}' workspace created at {output_dir}/")
    print(f"   Files: SOUL.md, AGENTS.md, MEMORY.md, HEARTBEAT.md, USER.md, TOOLS.md")
    print(f"   Memory: memory/{today}.md")
    print(f"   Rhythm: {r['desc']}")
    print(f"\n   Next steps:")
    print(f"   1. Customize SOUL.md with specific personality and rules")
    print(f"   2. Add integrations to TOOLS.md")
    print(f"   3. Set up cron jobs (see 'references/cron-patterns.md')")
    print(f"   4. Start chatting with your agent!")


def write_file(*path_parts):
    """Write content to a file, creating directories as needed."""
    if len(path_parts) == 3:
        directory, filename, content = path_parts
        filepath = os.path.join(directory, filename)
    else:
        directory, content = path_parts[0], path_parts[1]
        filepath = directory

    os.makedirs(os.path.dirname(filepath) if os.path.dirname(filepath) else ".", exist_ok=True)
    with open(filepath, "w") as f:
        f.write(content)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize an autonomous AI agent workspace")
    parser.add_argument("name", help="Agent name")
    parser.add_argument("--persona", "-p", required=True, help="Brief persona description")
    parser.add_argument("--rhythm", "-r", choices=["continuous", "hourly", "daily"], default="daily",
                        help="Operational rhythm (default: daily)")
    parser.add_argument("--output-dir", "-o", default="./agent-workspace",
                        help="Output directory (default: ./agent-workspace)")
    args = parser.parse_args()
    create_workspace(args.name, args.persona, args.rhythm, args.output_dir)
