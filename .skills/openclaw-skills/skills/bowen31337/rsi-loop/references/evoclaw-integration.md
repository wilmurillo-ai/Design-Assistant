# RSI Loop - EvoClaw Integration

## Overview

The RSI loop is a first-class EvoClaw primitive. Every agent in the fleet can:
1. Log its own outcomes (Observer)
2. Contribute patterns to the collective pool (Aggregator)
3. Receive synthesized improvements (Distributor)
4. Self-deploy validated changes (Deployer)

This creates a **network-wide recursive improvement loop** — every agent's failures improve every agent.

## Architecture in EvoClaw

```
┌─────────────────────────────────────────────────────────────────┐
│                      EvoClaw Fleet                              │
│                                                                 │
│  ┌──────────┐    MQTT      ┌──────────────┐    MQTT            │
│  │ edge-agent│──outcomes──▶│  RSI Hub     │──proposals──▶      │
│  │ (Pi/GPU) │             │  Aggregator  │              │      │
│  └──────────┘             └──────┬───────┘              │      │
│                                  │ analyze                      │
│  ┌──────────┐                    ▼                      │      │
│  │alex-hub  │◀──────────────Synthesizer                 │      │
│  │(main)    │                patterns                   │      │
│  └──────────┘                    │                      │      │
│       │                          │ proposals            │      │
│       ▼                          ▼                      │      │
│  Deployer ◀────────────── ClawChain Registry            │      │
│  (applies to                (stores hashes,             │      │
│   live agents)               provenance, voting)        │      │
└─────────────────────────────────────────────────────────────────┘
```

## MQTT Topics

### Outcome Publishing (each agent → hub)
```
Topic:   evoclaw/rsi/outcomes/<agent_id>
Payload: {
  "id": "abc12345",
  "ts": "2026-02-19T12:00:00Z",
  "agent_id": "alex-eye",
  "task_type": "monitoring",
  "model": "glm-4.7-flash",
  "success": true,
  "quality": 4,
  "duration_ms": 1200,
  "issues": [],
  "tags": ["pi", "gpio"],
  "notes": ""
}
```

### Pattern Publishing (hub → all agents)
```
Topic:   evoclaw/rsi/patterns
Payload: {
  "generated_at": "2026-02-19T18:00:00Z",
  "patterns": [...],  // top 10 patterns
  "health_score": 0.82
}
```

### Proposal Publishing (hub → specific agent or all)
```
Topic:   evoclaw/rsi/proposals/<agent_id>   (or "all")
Payload: {
  "id": "prop-abc",
  "priority": "high",
  "action_type": "update_soul",
  "title": "...",
  "implementation": {...}
}
```

## Go Integration (EvoClaw agent)

Add to agent's tool loop (`tools.go`):

```go
// RSI outcome logging tool
type RSILogTool struct {
    mqttClient mqtt.Client
    agentID    string
}

func (t *RSILogTool) Name() string { return "rsi_log" }
func (t *RSILogTool) Description() string {
    return "Log a task outcome to the RSI improvement loop"
}

type RSIOutcome struct {
    TaskType   string   `json:"task_type"`
    Success    bool     `json:"success"`
    Quality    int      `json:"quality"`
    Model      string   `json:"model"`
    DurationMs int      `json:"duration_ms"`
    Issues     []string `json:"issues"`
    Notes      string   `json:"notes"`
}

func (t *RSILogTool) Execute(input string) (string, error) {
    var outcome RSIOutcome
    if err := json.Unmarshal([]byte(input), &outcome); err != nil {
        return "", err
    }
    outcome.AgentID = t.agentID
    outcome.Timestamp = time.Now().UTC().Format(time.RFC3339)

    payload, _ := json.Marshal(outcome)
    topic := fmt.Sprintf("evoclaw/rsi/outcomes/%s", t.agentID)
    token := t.mqttClient.Publish(topic, 1, false, payload)
    token.Wait()
    return fmt.Sprintf("RSI logged: %s | success=%v | quality=%d", outcome.TaskType, outcome.Success, outcome.Quality), nil
}
```

## RSI Hub Service

The hub runs on alex-hub (port :8421 alongside the main hub):

```bash
# Start RSI hub
uv run python skills/rsi-loop/scripts/rsi_hub.py --mqtt-host 127.0.0.1 --port 1883

# Aggregation schedule:
# - Outcomes: collected in real-time, buffered in outcomes.jsonl
# - Analysis: runs every 6 hours
# - Synthesis: runs every 24 hours
# - Distribution: pushes proposals to agents after synthesis
```

## ClawChain Integration

Improvement proposals are optionally anchored on-chain for provenance and collective governance:

```python
# Hash proposal and store on ClawChain
from skills.clawchain.scripts.client import ClawChainClient

client = ClawChainClient()
proposal_hash = sha256(json.dumps(proposal).encode()).hexdigest()
tx = client.submit_extrinsic(
    pallet="AgentRSI",
    call="store_improvement",
    params={
        "agent_id": "alex-hub",
        "proposal_hash": proposal_hash,
        "improvement_type": proposal["action_type"],
        "priority": proposal["priority"],
    }
)
```

Pallet: `AgentRSI` (to be added to ClawChain as pallet #20)
- `store_improvement(proposal_hash, metadata)` — anchor proposal
- `vote_improvement(proposal_hash, approve)` — collective voting
- `list_top_improvements(limit)` — query top proposals by vote

## Agent Self-Improvement Protocol

Every EvoClaw agent follows this protocol at end of each significant task:

```python
# At end of each tool loop iteration
async def on_task_complete(task_type, success, quality, model, duration_ms, issues=None, notes=""):
    """Called by agent framework after each task completion."""
    subprocess.run([
        "uv", "run", "python",
        "skills/rsi-loop/scripts/observer.py",
        "log",
        "--task", task_type,
        "--success", "true" if success else "false",
        "--quality", str(quality),
        "--model", model,
        "--duration-ms", str(duration_ms),
        "--notes", notes,
    ] + (["--issues"] + issues if issues else []))
```

## Improvement Velocity Metrics

Track these KPIs in tiered-memory:

| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Health score | >0.85 | <0.70 |
| Success rate (7d) | >90% | <75% |
| Avg quality (7d) | >3.8 | <3.0 |
| Patterns detected | <5 | >15 |
| Days to deploy proposal | <3 | >7 |

## Roadmap

- [x] Phase 1: Observer + Analyzer + Synthesizer (heuristic)
- [x] Phase 2: Deployer + CLI
- [ ] Phase 3: LLM-powered synthesis (GPT/Claude generates novel proposals)
- [ ] Phase 4: MQTT fleet aggregation hub
- [ ] Phase 5: ClawChain `AgentRSI` pallet
- [ ] Phase 6: Cross-agent proposal voting and fleet-wide deployment
