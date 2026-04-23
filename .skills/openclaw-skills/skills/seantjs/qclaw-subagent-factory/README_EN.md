# qclaw-subagent-factory

> One-click creation of independent sub-agents for QClaw - Auto-detect paths, generate configs, register agents

[中文](README.md) | English

---

## Features

| Command | Description |
|---------|-------------|
| **create** | Interactively create new sub-agent |
| **list** | View all agents and their status |
| **setup-memory** | Initialize agent memory system |
| **summarize** | Summarize important memories from all agents |

---

## Installation

### Option 1: Copy to Skills Directory

```bash
# macOS/Linux
cp -r qclaw-subagent-factory ~/.qclaw/skills/

# Windows
xcopy /E /I qclaw-subagent-factory %USERPROFILE%\.qclaw\skills\
```

### Option 2: Using SkillHub

```bash
skillhub install qclaw-subagent-factory
```

---

## Quick Start

### Create New Agent

```bash
# Command line arguments
python scripts/create_agent.py "Data Analyst" "data-analyst" "Data processing and analysis" "stock_analysis,data_viz"

# Interactive mode
python scripts/create_agent.py
```

### List Agents

```bash
python scripts/list_agents.py
```

Output:
```
==================================================
QClaw Agent List
==================================================

✓ main [default]
   Name: Coordinator
   Memory: ✓ | Daily Log: ✓

✓ ai-director
   Name: AI Tech Director
   Memory: ✓ | Daily Log: ✓
```

### Summarize Memories

```bash
python scripts/summarize_memory.py
```

---

## Auto-Detection

| Detection | Description |
|-----------|-------------|
| QClaw Path | Auto-detect `~/.qclaw` or `AppData/QClaw` |
| Agent Dir | `~/.qclaw/agents/` |
| Workspace | `~/.qclaw/workspace/` |

Cross-platform support: Windows, macOS, Linux.

---

## Created Structure

```
~/.qclaw/agents/{agent_id}/
├── agent/
│   └── models.json       # Model config
└── workspace/
    ├── SOUL.md           # Role definition
    ├── AGENTS.md         # Collaboration protocol
    ├── USER.md           # User info
    ├── MEMORY.md         # Long-term memory
    ├── TOOLS.md          # Tools config
    ├── memory/
    │   └── YYYY-MM-DD.md # Daily log
    ├── reports/          # Report files
    └── projects/        # Project files
```

---

## Architecture

```
User Message → Coordinator (main)
                  ↓
           sessions_spawn
    ┌────────┼────────┐
    ↓        ↓        ↓
 ai-dir  invest-dir  misc-dir
 (AI Tech) (Investment) (Misc)
```

---

## Notes

1. **Restart Required**: Restart QClaw after creating agents
2. **Unique ID**: Agent ID must be unique
3. **Memory Limitation**: `memory_search` tool not available in sub-agent environment, use local search instead

---

## License

MIT License - See [LICENSE](LICENSE)
