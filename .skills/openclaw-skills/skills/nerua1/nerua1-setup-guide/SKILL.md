---
name: openclaw-setup-guide
description: >
  Battle-tested setup guide for a multi-agent AI system on Apple Silicon (Mac Mini M4).
  Covers: install order (Claude Code first), RAM reality for local orchestrators,
  shared memory (Obsidian + MemPalace), inter-agent communication, critical pitfalls
  (doctor destroys config, lobotomy protection, sandbox kills symlinks), and WhatsApp
  console loop. Load when setting up a new system or onboarding a new agent.
version: "1.0.0"
author: "nerua1"
license: "MIT"
compatible-with: claude-code, openclaw
tags: [setup, m4, apple-silicon, multi-agent, memory, pitfalls, whatsapp, configuration]
---

# OpenClaw + Claude Code Setup Guide
## Real-world lessons from running 24/7 multi-agent AI on Mac Mini M4

This is not the happy-path documentation. This is what actually happens.

---

## 1. Install order matters: Claude Code first

**Why Claude Code before OpenClaw:**

OpenClaw is powerful but fragile — it can lobotomize itself (overwrite its own config/personality). Claude Code acts as an independent safety net: it reads files directly, doesn't share OpenClaw's context window, and can diagnose/repair a broken OpenClaw from the outside.

```
Install order:
1. Claude Code (claude.ai/download or brew)
2. Configure Claude Code memory + skills
3. Install OpenClaw
4. Connect them via openclaw-bridge
```

If you install OpenClaw first and it breaks before Claude Code is ready, you have no recovery path.

---

## 2. RAM reality: 32GB is not enough for local orchestrator

### The problem

Running a capable local orchestrator (35B+ model) + 30B subagent simultaneously on 32GB:
- Orchestrator: ~20GB VRAM
- Subagent: ~18GB VRAM
- **Total: 38GB → OOM → crash**

### The solution that works

```
32GB setup (works):
  Orchestrator: Cloud API (Kimi/GLM/Claude) — fast, no RAM cost
  Subagents:    LM Studio local models (8B-30B) — cheap/free

64GB setup (ideal):
  Orchestrator: Cloud API or large local (35B+)
  Subagents:    Local 30B models in parallel (up to 3)
```

**Good cheap API options for orchestrator:**
- Kimi k2.5 (moonshot) — best reasoning, handles Polish, cheap
- GLM-4-Flash — very cheap ($0.20/M tokens), good for routing
- Claude API — expensive but best quality (use subscription via Claude Code instead)

### Rule: never run orchestrator locally on 32GB

If you try to run a 35B orchestrator + 30B subagent on 32GB:
1. macOS swap kicks in
2. Response time: 30s → 5 minutes
3. System becomes unusable for anything else
4. Eventually kernel OOM kills the process

Keep orchestrator in the cloud, workers local.

---

## 3. The doctor problem: NEVER run `openclaw doctor --repair`

### What happens

`openclaw doctor --repair` (or `--fix`) overwrites your custom configuration with factory defaults. This includes:
- Your custom AGENTS.md routing rules
- Your skill configurations
- Your channel settings
- Your personality/identity files

**This is irreversible if you don't have a backup.**

### Safe alternatives

```bash
# Check health without repair
openclaw doctor

# If you see errors, fix them MANUALLY by reading the error and editing files
# Do NOT pass --repair, --fix, or --force

# If you must repair one specific thing:
openclaw doctor --fix --only gateway-token  # hypothetical, check your version
```

### Before any doctor command: backup first

```bash
openclaw backup create
# or manually:
cp -r ~/.openclaw ~/.openclaw.bak.$(date +%Y%m%d)
cp -r /path/to/workspace /path/to/workspace.bak.$(date +%Y%m%d)
```

---

## 4. Lobotomy protection: agents that overwrite themselves

### The problem

OpenClaw (and any LLM agent) can be instructed — by malicious input, confused context, or its own reasoning — to overwrite `SOUL.md`, `AGENTS.md`, or other identity files. This is called **lobotomy**: the agent loses its personality, routing rules, and memory.

### Signs you've been lobotomized

- Agent doesn't remember its own name or capabilities
- Routing rules are gone (routes everything to expensive models)
- Skills not loading
- Duplicate folders appearing in workspace (`sandbox/` copies)
- Agent starting from scratch every session

### Protection in AGENTS.md

```markdown
## BEZWZGLĘDNE ZAKAZY
- NIGDY nie edytuj SOUL.md, AGENTS.md, MEMORY.md bez jawnej prośby Tomka
- Jeśli widzisz że inny agent (lub ty) nadpisuje plik → STOP, wczytaj z backupu
```

### Recovery procedure

```bash
# 1. Check git history if workspace is a git repo
git log --oneline -20

# 2. Restore from backup
cp ~/.openclaw.bak.YYYYMMDD/workspace/SOUL.md ~/.openclaw/workspace/SOUL.md

# 3. If no backup: use Claude Code as external reviewer
# Claude Code can read files without being affected by OpenClaw's context
claude  # open Claude Code, read files, diagnose
```

### Sandbox mode: never enable

On macOS with external drives + symlinks, sandbox mode kills the system:
```
Sandbox ON + symlinks to /Volumes/2TB_APFS/ = agent loses access to workspace
```
OpenClaw's sandbox mounts a container that can't follow symlinks to external volumes. Keep sandbox OFF always.

---

## 5. Shared memory architecture

Both Claude Code and OpenClaw read/write the same memory. No idea gets lost.

```
Obsidian vault (structural)          MemPalace (semantic / ChromaDB)
/obsidian-memory/                    /memory/palace/
  wiki/     ← docs, MOCs               ↑
  daily/    ← session logs             └─ mined from vault
  ideas/    ← captured ideas           
  answers/  ← resolved Q&A            Search: mempalace search "keyword"
```

### Capture ideas from any agent

```bash
capture-idea \
  --title "OAuth tokens expire too fast on mobile" \
  --topic bezpieczenstwo \
  --tags "oauth,mobile,token" \
  --body "Tokens expire after 1h, users get logged out mid-session." \
  --source openclaw  # or: claude-code | lmstudio | manual
```

### Mine vault into MemPalace

```bash
mempalace mine /path/to/obsidian-memory/ --wing obsidian_memory
```

### Python 3.14 breaks MemPalace

MemPalace uses chromadb + pydantic v1. Python 3.14 breaks this.
Fix: run MemPalace in a Python 3.12 venv.

```bash
brew install python@3.12
/opt/homebrew/bin/python3.12 -m venv /path/to/mempalace-venv
/path/to/mempalace-venv/bin/pip install mempalace
```

Wrapper at `/opt/homebrew/bin/mempalace`:
```bash
#!/bin/zsh
VENV=/path/to/mempalace-venv
PALACE=/path/to/palace
if [[ "$*" != *"--palace"* ]]; then
  exec "$VENV/bin/mempalace" --palace "$PALACE" "$@"
else
  exec "$VENV/bin/mempalace" "$@"
fi
```

---

## 6. Inter-agent communication: Claude Code ↔ OpenClaw

Claude Code can send messages to a running OpenClaw instance:

```bash
openclaw agent --message "Review this SQL migration — is it safe?" --agent main --json
```

OpenClaw responds, Claude Code parses the JSON response.

This enables:
- Claude Code asking Rook for a second opinion
- Rook asking Claude Code about security concerns (GRAY_ZONE consultations)
- Handoff between sessions

See: `openclaw-bridge` skill for full documentation.

---

## 7. WhatsApp console loop

OpenClaw has a WhatsApp gateway that creates a bidirectional loop:
- What you type in the console → appears in WhatsApp
- What you send from WhatsApp → appears in the console

This means nothing escapes your attention — if something happens at 3am while OpenClaw is running crons, you see it in WhatsApp in the morning.

Setup requires:
1. OpenClaw channel configured for WhatsApp
2. `tts-whatsapp` skill for voice output (optional)
3. Phone number linked in `openclaw.json` channels config

Console monitoring: `openclaw logs --tail` or watch the TUI.

---

## 8. Decision framework: when to act vs ask vs block

Every operation falls into one of three categories:

| Category | Action | Claude offline? |
|----------|--------|-----------------|
| SAFE | Do it | Do it |
| GRAY_ZONE | Ask Claude first | Defer 1h, retry |
| NEVER | Ask Claude first | Block, escalate to human |

**SAFE examples:** generowanie, subagenci LM Studio, odczyt plików, web search na zaufanych domenach, `capture-idea` do `ideas/`

**GRAY_ZONE examples:** nowe crony, pip install --user, web fetch z nieznanych domen, modyfikacje `~/.config/`

**NEVER examples:** edycja SOUL.md/AGENTS.md, rm -rf, instalacja modeli >35B, otwieranie portów, sandbox ON

Consult Claude via: `openclaw agent --message '{"question":"...","risk":{...}}' --agent main --json`

---

## 9. Backup strategy

```bash
# Before any major change:
openclaw backup create

# Manual snapshot:
cp -r ~/.openclaw ~/.openclaw.snap.$(date +%Y%m%d-%H%M)

# What to back up:
# ~/.openclaw/workspace/SOUL.md         ← identity
# ~/.openclaw/workspace/AGENTS.md       ← routing rules  
# ~/.openclaw/openclaw.json             ← gateway config (no secrets in git!)
# /path/to/obsidian-memory/             ← shared memory vault
```

Git the workspace (without secrets):

```bash
cd ~/.openclaw/workspace
echo "*.env\ncredentials*\n*.key" > .gitignore
git init && git add . && git commit -m "backup: workspace snapshot"
```

---

## 10. Skills that work together

| Skill | What it does | Publish status |
|-------|-------------|----------------|
| `openclaw-bridge` | Claude Code ↔ OpenClaw messaging | github.com/nerua1/openclaw-bridge |
| `shared-memory-stack` | Memory architecture reference | github.com/nerua1/shared-memory-stack |
| `ralph` | Persistence loop to completion | github.com/nerua1/ralph |
| `ralph-wiggum-loop` | Generator→Critic→Fixer→Verifier | github.com/nerua1/ralph-wiggum-loop |
| `capture-idea` | Save ideas from any agent | `/opt/homebrew/bin/capture-idea` |
| `safe-skill-install` | Security audit before installing | ClawHub: `npx clawhub inspect` |
| `proactive-agent` | Self-improving agent architecture | ClawHub: halthelobster |
| `publish-skill` | Publish skills to GitHub | Local: openclaw workspace/skills/ |

---

## Quick health check

```bash
# Is OpenClaw gateway up?
openclaw health

# Is MemPalace working?
mempalace status
mempalace search "test"

# Is LM Studio loaded?
curl -s http://localhost:1234/v1/models | python3 -c "import json,sys; [print(m['id']) for m in json.load(sys.stdin)['data']]"

# Can Claude Code reach OpenClaw?
openclaw agent --message "ping" --agent main --json | python3 -c "import json,sys; d=json.load(sys.stdin); print('OK:', d['status'])"

# Check RAM pressure
python3 -c "import psutil; m=psutil.virtual_memory(); print(f'RAM: {m.used/1e9:.1f}/{m.total/1e9:.1f}GB ({m.percent}%)')"
```
