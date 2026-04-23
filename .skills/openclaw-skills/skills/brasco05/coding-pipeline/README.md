# ⚙️ Coding Pipeline

**Stop AI agents from blind-patching. Make them plan, fix, verify, and escalate — in that order.**

Most AI coding agents have one failure mode: they edit, run the build, see an error, edit again, see another error, and spiral into a retry loop. They patch symptoms instead of causes. They bundle five fixes into one PR. They try the same thing eight times and give up without documenting anything.

This skill enforces a **disciplined 4-phase pipeline** for every non-trivial coding task. No shortcuts. No phase skipping. Hypothesis before code, verification before completion, escalation before thrashing.

---

## What It Does

Forces every bug fix, feature, refactor, or error investigation through 4 phases:

| Phase | Job | Exit When |
|-------|-----|-----------|
| **1. Planner** | Understand + form hypothesis | Hypothesis + scope + success criteria written |
| **2. Coder** | Apply one focused change | One fix, full files, no scope creep |
| **3. Validator** | Verify root cause, not symptom | Build ✓, types ✓, hypothesis proven correct |
| **4. Debugger** | Bounded debugging | Fixed (→ Phase 2) OR 3 attempts → escalate |

## Why It Matters

Without this pipeline, agents:

- **Patch symptoms** instead of root causes (you'll see the same bug again next week)
- **Bundle multiple fixes** into one change (nobody knows which one worked)
- **Retry the same fix** with minor variations (wastes tokens, burns context)
- **Skip validation** — "it compiles, ship it" (ships broken code)
- **Debug forever** — 12 attempts, no log, no escalation

With this pipeline, agents:

- **Write a hypothesis** before touching code
- **Apply one fix at a time** — each one testable, reviewable, revertable
- **Verify cause, not symptom** — does the root issue actually resolve?
- **Max 3 attempts** in debug mode, then escalate to human

## How It Triggers

Activate automatically when the task is a **bug fix**, **feature**, **refactor**, **error investigation**, **test failure**, or **deployment issue**. Skip only for trivial edits (typos, formatting, one-line config) and explicit exploratory work.

## Core Rules

- **Always start at Phase 1** — no shortcuts
- **One fix at a time** — three unrelated improvements = three cycles
- **Phase 3 verifies the cause** — not just that the symptom disappeared
- **Phase 4 caps at 3 attempts** — after that, escalate to the user
- **Document every failed attempt** — pattern recognition matters

## Works With

- ✅ **Claude Code** — hooks via `.claude/settings.json`
- ✅ **OpenClaw** — workspace injection at session start
- ✅ **Codex CLI** — hooks via `.codex/settings.json`
- ✅ **GitHub Copilot** — manual activation via `.github/copilot-instructions.md`
- ✅ **Any agent that reads markdown** — the 4 phases are text, not tooling

## Quick Start

**OpenClaw (recommended):**

```bash
clawdhub install coding-pipeline
```

**Manual:**

1. Copy this folder into your skills directory
2. The skill activates via its description when non-trivial tasks arrive
3. Optionally enable the `UserPromptSubmit` hook for automatic phase reminders (see `references/hooks-setup.md`)

## What You Get

```
coding-pipeline/
├── SKILL.md                   # 4-phase pipeline definition
├── assets/                    # Copy-paste templates
│   ├── PHASE-1-planner-template.md
│   ├── PHASE-2-coder-checklist.md
│   ├── PHASE-3-validator-checklist.md
│   └── PHASE-4-debugger-log.md
├── references/                # Deep-dives per phase + anti-patterns + integration
├── scripts/                   # activator.sh, phase-check.sh
└── hooks/openclaw/           # OpenClaw hook manifest
```

## Integration with Other Skills

- **`systematic-debugging`** — Phase 4 handoff for complex investigations
- **`self-improving-agent`** — Log failed attempts to `.learnings/ERRORS.md`
- **`root-cause-analysis`** — Escalation when Phase 3 is ambiguous
- **`test-driven-development`** — Phase 1 success criteria pair with failing test first

See `references/integration.md` for pairing patterns.

## Why This Matters

Disciplined work beats fast work. An agent that takes 3 minutes to write a hypothesis and then fixes the root cause in one attempt beats an agent that jumps straight to code and spends 30 minutes in a retry loop. This skill is the structure that keeps agents in the first category.

**Plan first. Fix once. Verify the cause. Escalate when stuck.**

---

*Built for OpenClaw. Compatible with all major AI coding agents.*
