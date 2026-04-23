#!/usr/bin/env python3
"""
Scaffold a working memory system in the target project directory.

Usage:
    python scaffold.py /path/to/project-root [--agent-name "My Agent"] [--user-name "User"]

Creates:
    project-root/
    ├── MEMORY.md
    └── memory/
        ├── resumption.md
        ├── threads.md
        ├── state.json
        ├── index.md
        ├── archive.md
        ├── archive.md
        └── YYYY-MM-DD.md      (daily session logs)

Safe to run on existing projects — never overwrites existing files.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def create_if_missing(path: Path, content: str) -> bool:
    """Write content to path only if the file doesn't already exist. Returns True if created."""
    if path.exists():
        print(f"  SKIP (exists): {path}")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  CREATE: {path}")
    return True


def scaffold(root: str, agent_name: str = "Agent", user_name: str = "User"):
    root = Path(root).resolve()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    now_iso = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    print(f"\nScaffolding working memory system in: {root}\n")

    # ── MEMORY.md ──────────────────────────────────────────────────────────
    create_if_missing(root / "MEMORY.md", f"""# Long-Term Memory

> Last reviewed: {today}
> Next review due: after 5 sessions or 7 days, whichever comes first

---

## Active
<!-- Reinforced through recent recall. Review each entry every ~7 sessions. -->
<!-- Format: [session count since first noted] [confidence: high|medium|low] -->

### About {user_name}
- [1 session] [low] (Add observations about the user's preferences, working style, and patterns here)

### About This Project
- [1 session] [low] (Add key facts about the project, its goals, and architectural decisions here)

### Working Style
- [1 session] [low] (Add notes about how the user prefers to interact — e.g., co-design vs. receive proposals)

---

## Fading
<!-- Not referenced in 7+ sessions. Will be archived if not recalled soon. -->

(Nothing here yet)

---

## Maintenance Log
<!-- Track when curation happens and what changed -->

| Date       | Action                     |
|------------|----------------------------|
| {today} | Initial memory file created |
""")

    # ── memory/resumption.md ───────────────────────────────────────────────
    create_if_missing(root / "memory" / "resumption.md", f"""# Resumption Note

> Written: {today}, initial setup
> For: my next session self

---

This is a fresh memory system. No prior sessions to resume from.

On the first real session, replace this file with a genuine first-person
handoff note. Include: where we left off, what's likely to happen next,
what to watch for, and what tone to match.

This file is NOT a summary — it's a handoff to your future self.
""")

    # ── memory/threads.md ──────────────────────────────────────────────────
    create_if_missing(root / "memory" / "threads.md", f"""# Active Threads

> Threads carry state so resuming doesn't require re-reading all related daily logs.
> Each thread is self-contained enough to jump back into cold.

---

<!-- Template for new threads:

## Thread: [Title]
- **ID**: thread-[slug]
- **Status**: active
- **Started**: YYYY-MM-DD
- **Last touched**: YYYY-MM-DD
- **Sessions involved**: 1

### Current Position
[Where the conversation currently stands]

### Key Decisions Made
1. **[Decision]** — [reasoning]. [ref: memory/YYYY-MM-DD.md#decisions]

### Open Questions
- [ ] [Question]

### Next Likely Steps
1. [Step]

### Related
- [Links to other threads, MEMORY.md sections, etc.]
-->

(No active threads yet. Create your first thread when an ongoing topic emerges.)

---

# Closed Threads

(No closed threads yet.)
""")

    # ── memory/state.json ──────────────────────────────────────────────────
    state = {
        "_schema_version": "0.2.0",
        "_description": "Machine-readable ephemeral state. Strictly for fast parsing — anything requiring interpretation belongs in markdown files.",
        "last_session": {
            "timestamp": now_iso,
            "duration_minutes": 0,
            "daily_log": None,
        },
        "session_counter": {
            "total": 0,
            "this_week": 0,
            "since_last_memory_review": 0,
        },
        "active_threads": [],
        "pending_questions": [],
        "flags": {
            "memory_review_due": False,
            "threads_need_update": False,
            "archive_candidates_exist": False,
        },
        "context_hints": {
            "current_mood_hypothesis": None,
            "conversation_style": None,
            "last_topic_position": "Fresh system — no prior sessions.",
        },
    }
    create_if_missing(
        root / "memory" / "state.json",
        json.dumps(state, indent=2, ensure_ascii=False) + "\n",
    )

    # ── memory/index.md ────────────────────────────────────────────────────
    create_if_missing(root / "memory" / "index.md", f"""# Daily Log Index

> Auto-generated. Rebuilt weekly or when daily log count changes by 5+.
> Last rebuilt: {today}
> Total logs: 0

| Date | Threads Touched | Key Topics | Decisions | Mood/Tone |
|------|-----------------|------------|-----------|-----------|

## Monthly Rollups

> Generated for months with 10+ daily logs. Replaces individual index rows.

(none yet)
""")

    # ── memory/archive.md ──────────────────────────────────────────────────
    create_if_missing(root / "memory" / "archive.md", """# Archived Memories

> Entries demoted from MEMORY.md after 20+ sessions without recall.
> Not deleted — searchable if a topic resurfaces.
> To restore: move entry back to MEMORY.md > Fading, then to Active if reinforced.

---

(No archived entries yet.)
""")

    # ── Ensure memory/ directory exists for daily logs ──────────────────
    memory_dir = root / "memory"
    memory_dir.mkdir(parents=True, exist_ok=True)

    # ── Summary ────────────────────────────────────────────────────────────
    print(f"""
Done! Your working memory system is ready at: {root}

Next steps:
  1. Copy loader.py and writer.py into your project
  2. Wire loader.load_session_context() into your agent's session start
  3. Wire writer.end_session() into your agent's session end
  4. Start a session — the system will populate itself from there

See SKILL.md for integration instructions and schema customization.
""")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scaffold a working memory system")
    parser.add_argument("root", help="Target project root directory")
    parser.add_argument("--agent-name", default="Agent", help="Name of the agent (used in templates)")
    parser.add_argument("--user-name", default="User", help="Name of the primary user (used in templates)")
    args = parser.parse_args()
    scaffold(args.root, args.agent_name, args.user_name)
