---
name: auto-skill-extractor
emoji: 🔄
description: Automatically learn from your AI's work and turn repeated subagent tasks into reusable skills
details: |
  **Auto-Skill Extractor v1.0.2** watches your subagents work, detects patterns worth reusing, and creates draft skills automatically.
  
  ## Security Notice
  
  ✅ **No sensitive data persisted** - Only tool counts, scores, and timestamps are stored  
  ✅ **Configurable workspace** - Set `AUTO_SKILL_WORKSPACE` environment variable  
  ✅ **Sanitized metadata** - Session IDs are hashed, transcripts are not written to disk  
  ✅ **Path validation** - All paths checked before file operations  
  ✅ **No raw trigger files** - Recommended usage uses stdin, not file-based input

## What It Does

Your OpenClaw agent runs subagents to do complex tasks. This skill:
1. **Observes** subagent completions (what tools they used, what they accomplished)
2. **Scores** complexity (3+ tool calls? multi-domain work? error recovery?)
3. **Extracts** if the work looks reusable → creates `skills/auto-draft/{name}/`
4. **Promotes** after 3 successful uses → moves to `skills/auto/` (ACTIVE)
5. **Archives** unused drafts after 7 days

## Why Use This

- Stop manually writing skills for every pattern
- Build a library of your actual workflows
- Learn from your agent's own work
- Automate skill lifecycle (draft → test → promote)

## How Complexity Scoring Works

| Factor | Points | Example |
|--------|--------|---------|
| 3 tool calls | 2 pts | read + exec + write |
| 5 tool calls | 4 pts | complex analysis |
| Multi-domain | +2 pts | files + system + web |
| Error recovery | +2 pts | retry on failure |

**Threshold:** 4 points = creates DRAFT skill

## Safety Features

- ✅ Won't overwrite existing skills (collision check)
- ✅ Sanitizes names (no path traversal)
- ✅ Atomic promotions (copy → verify → move)
- ✅ Queue limits (max 50 pending)

## Install

```bash
clawhub install auto-skill-extractor
```

## Setup

1. Create skill directories:
   ```bash
   mkdir -p skills/auto-draft skills/auto skills/manual
   ```

2. Add to AGENTS.md after subagent completion (RECOMMENDED: stdin piping):
   ```python
   import subprocess, json
   
   # Build trigger data (avoid putting sensitive secrets in transcript_summary)
   trigger_data = {
       "completion_status": "success",
       "tool_calls": tool_call_count,
       "session_id": session_key,
       "multi_domain": True,
       "transcript_summary": summary  # Keep brief, avoid secrets
   }
   
   # Pipe via stdin (no file written to disk)
   result = subprocess.run(
       ["python3", "scripts/auto-skill-trigger.py"],
       input=json.dumps(trigger_data),
       capture_output=True,
       text=True
   )
   ```

   Alternative (file-based, less secure - delete file immediately after):
   ```python
   import subprocess, json
   import os
   
   trigger_path = "/tmp/trigger.json"
   with open(trigger_path, "w") as f:
       json.dump(trigger_data, f)
   
   result = subprocess.run(
       ["python3", "scripts/auto-skill-trigger.py", trigger_path],
       capture_output=True
   )
   
   # SECURITY: Delete trigger file immediately after use
   os.remove(trigger_path)
   ```
  
  ## Commands
  
  ```bash
  # List active auto-skills
  python3 scripts/skill-lifecycle.py list
  
  # List drafts under evaluation
  python3 scripts/skill-lifecycle.py drafts
  
  # Process promotions and archives
  python3 scripts/skill-lifecycle.py process
  
  # Manually promote a draft
  python3 scripts/skill-lifecycle.py promote my-skill-name
  ```
  
  ## Directives
  
  - `#skill: extract` — Manually trigger from last subagent
  - `#skill: force` — Force extraction (ignore thresholds)
  
  ## Based On
  
  Hermes Agent by Nous Research — adapted for OpenClaw.
  
  ## See Also
  
  - GitHub: https://github.com/wahajahmed010/openclaw-hermes-adaptation
  - Docs: Full methodology and case study
version: 1.0.2
author: wahajahmed010
homepage: https://github.com/wahajahmed010/openclaw-hermes-adaptation
keywords:
  - skill-learning
  - subagent
  - auto-extract
  - workflow-capture
  - pattern-recognition
  - skill-lifecycle
  - hermes
  - self-improving
---

# Auto-Skill Extractor

**Turn your agent's work into reusable skills. Automatically.**

## When to Use

✅ You run complex subagent tasks repeatedly  
✅ You want to build a skill library without manual authoring  
✅ You run multi-domain tasks (files + system + web)  
✅ You want your agent to learn from its own patterns  

## When NOT to Use

❌ Simple 1-2 tool tasks (not worth skilling)  
❌ One-off exploratory work  
❌ You prefer manually authoring every skill  

## Quick Start

### 1. Install

```bash
clawhub install auto-skill-extractor
```

### 2. Create Directories

```bash
mkdir -p skills/auto-draft skills/auto skills/manual
```

### 3. Wire Into Your Agent

Add to `AGENTS.md` after subagent completion:

```python
# Auto-skill extraction trigger
import subprocess
import json

# Write trigger input
trigger_data = {
    "completion_status": "success",
    "tool_calls": tool_call_count,  # from subagent result
    "transcript_summary": brief_summary,  # Keep brief, avoid secrets
    "session_id": session_key,
    "multi_domain": True  # if applicable
}

# RECOMMENDED: Pipe via stdin (no file on disk)
result = subprocess.run(
    ["python3", "scripts/auto-skill-trigger.py"],
    input=json.dumps(trigger_data),
    capture_output=True,
    text=True
)

# ALTERNATIVE: File-based (delete immediately after)
# with open("/tmp/trigger.json", "w") as f:
#     json.dump(trigger_data, f)
# result = subprocess.run(
#     ["python3", "scripts/auto-skill-trigger.py", "/tmp/trigger.json"],
#     capture_output=True, text=True
# )
# os.remove("/tmp/trigger.json")  # SECURITY: Delete after use

output = json.loads(result.stdout)
if output.get("action") == "extract":
    print(f"🔄 Created DRAFT skill: {output['skill_name']}")
```

### 4. Use It

Run a subagent with complex work:

```
Spawn subagent to analyze codebase...
- Read 5 config files ✓
- Check processes ✓
- Write summary report ✓
```

**Result:** `skills/auto-draft/codebase-analyzer-abc123/` created automatically

## How It Works

### Step 1: Trigger Evaluation

After every subagent completion:

| Check | Must Pass |
|-------|-----------|
| Status | `success` |
| Tool calls | `≥ 3` |
| Complexity | `≥ 4` |

### Step 2: Complexity Scoring

```
Base:    tool_calls × 0.7  (max 5 pts)
          3 tools = 2 pts, 5 tools = 4 pts

Bonus:   +2  multi-domain (files + system + web)
         +2  error recovery (retry logic)
         +1  fail-then-succeed

Threshold: 4 points = extract
```

### Step 3: DRAFT Creation

```
skills/auto-draft/my-skill-abc123/
├── SKILL.md      ← Template with metadata
└── meta.json     ← Invocation tracking
```

### Step 4: Evaluation Period

- Use the DRAFT skill 3 times successfully
- Each use logged in `meta.json`
- After 3rd use → auto-promoted to `skills/auto/`

### Step 5: ACTIVE Status

Promoted skills are:
- Visible in `/skills auto` list
- Ready for manual completion
- Versioned and tracked

## Configuration

Edit `scripts/auto-skill-trigger.py`:

```python
COMPLEXITY_THRESHOLD = 4    # Lower = more drafts, more curation
MAX_QUEUE_SIZE = 50         # Pending extraction limit
PROMOTE_THRESHOLD = 3       # Invocations before promotion
```

## Manual Control

### Force Extraction

Ignore thresholds:

```
#skill: force
```

### List Drafts

```bash
python3 scripts/skill-lifecycle.py drafts
```

### Promote Early

```bash
python3 scripts/skill-lifecycle.py promote my-skill-name
```

### Archive Stale Drafts

```bash
python3 scripts/skill-lifecycle.py process
# Removes drafts unused for 7+ days
```

## Safety

- ✅ **Collision detection** — Won't overwrite existing skills
- ✅ **Path sanitization** — `../../../etc` → blocked
- ✅ **Atomic promotion** — Copy → verify → move → delete
- ✅ **Queue limits** — Max 50 pending extractions
- ✅ **Return value checks** — Errors logged, not silent

## Verification

Check extraction worked:

```bash
# See recent DRAFTs
ls -la skills/auto-draft/

# Check extraction queue
cat scripts/skill-extraction-queue.json

# View specific skill
cat skills/auto-draft/my-skill-abc123/SKILL.md
```

## Pitfalls

| Problem | Cause | Fix |
|---------|-------|-----|
| No DRAFTs created | Threshold too high | Lower `COMPLEXITY_THRESHOLD` |
| Too many DRAFTs | Threshold too low | Raise threshold, manually curate |
| Promotion never happens | Not using DRAFTs | Run `/skills promote` manually |
| Skills not useful | Noise in extraction | Tune thresholds, review DRAFTs weekly |

## Architecture

```
Subagent completes
    ↓
auto-skill-trigger.py
    ↓
Score complexity (0-10)
    ↓
If ≥ 4: Create DRAFT
    ↓
skill-lifecycle.py
    ↓
After 3 uses: PROMOTE → skills/auto/
    ↓
After 7 days: ARCHIVE
```

## Related

- **Hermes Agent** — Original inspiration (Nous Research)
- **Auto-skill pipeline case study** — https://github.com/wahajahmed010/openclaw-hermes-adaptation
- **Skill lifecycle management** — Built into this package

## References

- Hermes Adaptation: https://github.com/wahajahmed010/openclaw-hermes-adaptation
- Original Hermes: https://github.com/NousResearch/Hermes-Agent
