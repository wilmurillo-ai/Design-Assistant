# Agent-Ops-Toolkit

Operational backbone for autonomous OpenClaw agents. Sets up nightly memory extraction, morning briefs, heartbeat monitoring, and autonomous memory decay—all running locally with zero cloud dependency.

---

## What This Skill Does

Builds the infrastructure your agent needs to work autonomously:

- **Nightly Extraction:** Parse daily notes, extract atomic facts into items.json
- **Morning Brief:** Summarize hot/warm facts, deliver each morning
- **Heartbeat Monitoring:** Watch long-running loops, auto-restart on stall
- **Memory Decay:** Age facts autonomously (hot → warm → cold), keep summaries fresh
- **PARA Scaffold:** Directory structure for projects, areas, resources, archives

**Result:** Your agent learns continuously from your work. You check in once a day. Everything else runs autonomously.

---

## Install

```bash
clawhub install ops-toolkit
```

Installs:
- `setup_ops.sh` — Interactive setup wizard
- `heartbeat_tick.py` — Stall detection + auto-restart
- `decay_sweep.py` — Memory aging and summary rewriting
- Reference documentation (6 files)
- Template configurations (3 JSON files + PARA scaffold)

---

## Quick Start (30 Minutes)

### Step 1: Run Setup Wizard (15 min)

```bash
bash setup_ops.sh
```

Prompts you for:
- Timezone (America/New_York, etc.)
- Agent ID (name for this agent)
- Memory path (usually: `memory/`)
- Extraction model (default: Haiku 4.5)
- Delivery channel (optional: Telegram, Slack, file)

**Output:** Sets up `.env`, cron configs, initial heartbeat config.

### Step 2: Activate Cron Jobs (10 min)

```bash
openclaw cron add < nightly-extraction-cron.json
openclaw cron add < morning-brief-cron.json
openclaw cron add < decay-sweep-cron.json
```

Verify:
```bash
openclaw cron list
```

Should show 3 jobs scheduled (or more if you add heartbeat).

### Step 3: Verify (5 min)

Check logs after first run:

```bash
openclaw cron logs nightly-extraction  # Should show successful extraction
openclaw cron logs morning-brief      # Should show brief summary
```

**Done.** Your agent is now running autonomously. Next: Create your first daily note and watch extraction happen.

---

## Components

| Component | Purpose |
|-----------|---------|
| **heartbeat_tick.py** | Monitor tmux sessions for stalls; auto-restart on repeated identical output (hash-based detection) |
| **decay_sweep.py** | Weekly memory aging: classify facts as hot/warm/cold; rewrite summaries; update status fields |
| **setup_ops.sh** | Interactive wizard for initial setup; generates config files and environment setup |
| **memory-schema.md** | Specification for items.json (10 fields, atomic facts, access tracking, provenance) |
| **cron-templates.md** | Documented nightly extraction + morning brief configurations with all fields explained |
| **heartbeat-protocol.md** | Deterministic protocol: when to output `HEARTBEAT_OK`, when to `ALERT`, stall heuristics, restart logic |
| **decay-algorithm.md** | Formal memory lifecycle: hot/warm/cold classification, resistance formula (Kalman-inspired), weekly sweep |
| **research-notes.md** | 4 paper citations (GAM-RAG, SuperLocalMemory, Retrieval Bottleneck, MemPO) with design mappings |

---

## What Gets Created

### Cron Jobs (3 jobs)

1. **nightly-extraction** — 11 PM every night
   - Parses `memory/YYYY-MM-DD.md` (daily notes)
   - Extracts atomic facts into `life/*/items.json`
   - Updates `life/*/summary.md`
   - Commits to git

2. **morning-brief** — 8 AM every morning
   - Summarizes hot/warm facts from knowledge graph
   - Delivers via your chosen channel (Telegram, Slack, file)
   - Shows priorities, risks, upcoming events

3. **decay-sweep** — 2 AM every Sunday
   - Ages facts: hot (< 7d) → warm (8-30d) → cold (30+ days)
   - Applies resistance bonus for frequently-used facts (accessCount > 5)
   - Rewrites summaries, removes cold facts from active summary
   - Keeps all facts in items.json (never deletes, only status changes)

### Directory Structure (PARA)

```
life/
  projects/       — Time-bound deliverables
  areas/          — Ongoing responsibilities
  resources/      — Reference materials
  archives/       — Completed work
  
Each contains:
  - [name].md            — Charter/overview
  - status.md            — Current progress
  - items.json           — Atomic facts about this project/area/resource
  - summary.md           — Auto-generated summary (hot + warm facts only)
```

### Configuration Files

- `.env` — Timezone, agent ID, memory paths
- `heartbeat-config.json` — Managed tmux sessions, state file
- `nightly-extraction-cron.json` — Extraction schedule, model, paths
- `morning-brief-cron.json` — Brief schedule, delivery channel, summary format

---

## Cost Breakdown

**Operational cost: ~$5–10/month**

- **Nightly extraction:** Haiku 4.5 (~$0.10/day = ~$3/month)
- **Morning brief:** Haiku 4.5 (~$0.05/day = ~$1.50/month)
- **Heartbeat:** $0 (pure logic, no LLM)
- **Decay:** $0 (pure logic, no LLM)

**Why so cheap?** Self-managed memory (MemPO, arXiv:2603.00680) eliminates expensive clarification loops. Your agent extracts once per day and summarizes autonomously. No per-interaction cost.

**Compare:** Manual memory (asking agent clarifying questions): $50–100/month

**Savings:** 80–90% reduction vs. interactive memory systems

---

## Research Backing

Every architectural decision is grounded in published research:

- **GAM-RAG (arXiv:2603.01783):** Kalman-inspired decay (fast warm-up for new facts, conservative refinement for stable ones)
- **SuperLocalMemory (arXiv:2603.02240):** Local-first storage (zero cloud dependency, full provenance tracking)
- **Retrieval Bottleneck (arXiv:2603.02473):** Atomic facts over dense summaries (20–40 point quality improvement)
- **MemPO (arXiv:2603.00680):** Self-managed memory (67–73% token reduction)

**See:** `references/research-notes.md` for complete citations and design mappings.

---

## Troubleshooting

### Cron job didn't run

1. Check if it's enabled: `openclaw cron list`
2. Check logs: `openclaw cron logs [job-name]`
3. Check timezone: `timedatectl` (must match config timezone)

### Extraction output looks wrong

1. Check daily note format: `cat memory/YYYY-MM-DD.md`
2. Check items.json: `cat life/*/items.json` (is it valid JSON?)
3. Manually trigger: `openclaw extract --agent [agent-id] --base-path memory/ --model haiku-4.5`

### Heartbeat keeps restarting session

1. Check session logs: `tmux capture-pane -p -t [session-name]`
2. Is the session supposed to keep running? (If it exits normally, heartbeat sees this as a stall)
3. Increase check interval: Edit `check_interval_minutes` in heartbeat-config.json

### Memory is growing too fast

1. Check if decay is running: `openclaw cron logs decay-sweep`
2. Check cold facts are being removed from summaries: `cat life/*/summary.md` (should only show hot + warm)
3. Check fact status distribution: `grep '"status"' life/*/items.json | sort | uniq -c`

---

## What's Next

### Day 1-3
Run the quickstart guide. Your agent will extract facts and deliver morning briefs.

### Week 1-2
Watch the system stabilize. Facts accumulate, summaries become accurate. Confidence builds.

### Month 2+
Customize:
- Add more cron jobs (weekly synthesis, monthly reflection, etc.)
- Tune decay thresholds (7/30 day cutoffs may not match your workflow)
- Integrate external systems (email, calendar, task manager)
- Train your agent on domain-specific extraction

---

## Integration with Other Skills

- **Persona-builder:** Generate your agent's SOUL.md, IDENTITY.md, MEMORY.md
- **Quickstart-guide:** Learn the concepts (this skill implements them)

---

## Support

Questions? Check:
1. **Reference docs** — Each file (heartbeat-protocol.md, decay-algorithm.md, etc.) has detailed explanations
2. **Troubleshooting section above** — Common issues and fixes
3. **Research notes** — Understand the principles behind each decision
4. **ClawHub community** — Discord, GitHub issues, discussion board

---

**You're 30 minutes away from autonomous memory management.**

Install the skill, run the wizard, activate cron jobs. By tomorrow morning, you'll have your first briefing.

The system improves daily. Trust it.
