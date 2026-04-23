---
name: rsi-loop
description: >
  Recursive Self-Improvement (RSI) loop for EvoClaw agents. Provides a structured
  observe→analyze→synthesize→deploy pipeline that enables agents to detect their own
  failure patterns and generate concrete improvement proposals (new skills, routing fixes,
  SOUL.md updates, memory improvements). Use when: (1) logging a task outcome (success/fail/quality),
  (2) running periodic self-improvement analysis, (3) reviewing or deploying improvement proposals,
  (4) integrating RSI into EvoClaw hub/edge agents via MQTT, (5) checking agent health score,
  (6) any mention of "self-improvement", "recursive improvement", "fix my own mistakes",
  "improvement loop", or "agent evolution". Core EvoClaw primitive.
---

# RSI Loop - Recursive Self-Improvement

Four-stage pipeline: **Observe → Analyze → Synthesize → Deploy**

## Quick Start

```bash
# Log an outcome
uv run python skills/rsi-loop/scripts/rsi_cli.py log \
  --task code_generation --success true --quality 4 --model glm-4.7

# Full cycle (detect patterns + generate + deploy quick wins)
uv run python skills/rsi-loop/scripts/rsi_cli.py cycle

# Status dashboard
uv run python skills/rsi-loop/scripts/rsi_cli.py status
```

## Data Layout

```
skills/rsi-loop/data/
├── outcomes.jsonl       # All logged turn outcomes
├── patterns.json        # Latest analysis output
└── proposals/           # Improvement proposals (one JSON per proposal)
    ├── abc12345.json    # draft/approved/rejected/deployed
    └── ...
```

## Stage 1: Observer — Log Outcomes

Log every significant task at completion. Be honest about quality (1=terrible, 5=perfect).

```bash
# Successful task
uv run python skills/rsi-loop/scripts/rsi_cli.py log \
  --task code_generation --success true --quality 4

# Failed task with issues
uv run python skills/rsi-loop/scripts/rsi_cli.py log \
  --task code_debug --success false --quality 2 \
  --issues skill_gap rate_limit \
  --notes "No Rust-specific debug skill, kept hitting context limits"
```

**Task types:** code_generation, code_debug, code_review, architecture_design, file_ops,
web_search, memory_retrieval, skill_creation, cron_management, api_integration,
data_analysis, message_routing, infrastructure_ops, documentation, general_qa,
trading, monitoring, blockchain, unknown

**Issue types:** rate_limit, model_fallback, tool_error, wrong_output, incomplete_task,
context_loss, memory_miss, skill_gap, bad_routing, slow_response, over_confirmation,
repeated_mistake, missing_tool, wrong_model_tier, compaction_lost_context, other

## Stage 2: Analyzer — Detect Patterns

```bash
uv run python skills/rsi-loop/scripts/analyzer.py --days 7 --top 5
```

Outputs ranked patterns by impact score = (frequency/total) × quality_deficit.
Saves to `data/patterns.json`.

## Stage 3: Synthesizer — Generate Proposals

```bash
# Generate proposals from latest patterns
uv run python skills/rsi-loop/scripts/synthesizer.py generate --top 5

# Review proposals
uv run python skills/rsi-loop/scripts/synthesizer.py list

# Show full proposal detail
uv run python skills/rsi-loop/scripts/synthesizer.py show <proposal_id>

# Approve for deployment
uv run python skills/rsi-loop/scripts/synthesizer.py approve <proposal_id>
```

## Stage 4: Deployer — Apply Improvements

```bash
# Dry run (see what would happen)
uv run python skills/rsi-loop/scripts/deployer.py deploy <id> --dry-run

# Deploy a specific proposal
uv run python skills/rsi-loop/scripts/deployer.py deploy <id>

# Deploy all approved proposals
uv run python skills/rsi-loop/scripts/deployer.py deploy-all
```

**Action types and what they do:**
- `create_skill` → Scaffolds new skill directory via skill-creator
- `update_soul` → Appends lesson to SOUL.md's "Lessons learned"
- `fix_routing` → Prints instructions for updating intelligent-router config
- `update_memory` → Prints HEARTBEAT.md / tiered-memory improvement instructions
- `add_cron` → Prints cron configuration to add

## Full Cycle (Automated)

```bash
# Run full cycle, auto-deploy anything estimated < 20 minutes effort
uv run python skills/rsi-loop/scripts/deployer.py full-cycle \
  --days 7 --auto-approve-below-mins 20

# Or use the CLI shortcut
uv run python skills/rsi-loop/scripts/rsi_cli.py cycle
```

## Cron Job (Weekly RSI)

Set up automated weekly analysis:
```bash
# Every Sunday at 3 AM AEST
openclaw cron add --name "Weekly RSI Cycle" \
  --cron "0 3 * * 0" \
  --tz "Australia/Sydney" \
  --model "anthropic-proxy-4/glm-4.7" \
  --system-event "Run RSI cycle: uv run python skills/rsi-loop/scripts/rsi_cli.py cycle --days 7"
```

## EvoClaw Integration

For fleet-wide RSI across all hub/edge agents, see:
- `references/evoclaw-integration.md` — MQTT topics, Go integration, ClawChain pallet spec
- Phase roadmap: heuristic (now) → LLM synthesis → MQTT aggregation → ClawChain governance

## Proactive Logging Protocol

Log outcomes for every significant task. Rule of thumb:
- Any task > 2 minutes → log it
- Any task that used external tools → log it
- Any task that failed → definitely log it
- Batch similar quick tasks → log once with aggregate quality

This builds the dataset that makes RSI work.
