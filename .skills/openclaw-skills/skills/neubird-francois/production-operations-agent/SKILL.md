---
name: neubird-ops-agent
description: "Give your assistant production ops superpowers via NeuBird. Use when asked about infrastructure health, cloud costs, incidents, latency, error rates, deployment risk, silent failures, blast radius, or anything happening in production right now. Covers all 9 NeuBird capabilities: health check, cost analysis, investigation, performance, risk prediction, deep dive, silent failures, change risk, and blast radius. Requires the neubird CLI to be installed and authenticated."
tags: [production, sre, incidents, kubernetes, cloud, cost, performance, observability]
homepage: https://neubird.ai
metadata: {"neubird": {"emoji": "🔍"}, "openclaw": {"emoji": "🔍", "requires": {"bins": ["neubird"]}}}
---

# NeuBird Ops Agent

Production ops superpowers, powered by [NeuBird](https://neubird.com) — the AI SRE that lives in your terminal.

## When to Use

✅ **USE this skill when the user asks about anything in production:**

| They say... | Use this capability |
|---|---|
| "Any issues right now?" / "Is prod healthy?" | `health` |
| "Are we wasting money?" / "What's our cloud spend?" | `cost` |
| "Why is X broken?" / "Any 403s?" / "What's causing errors?" | `investigate` |
| "Why is the API slow?" / "Find latency outliers" | `performance` |
| "What could blow up tonight?" / "Any risk on the horizon?" | `predict` |
| "Give me the full picture" / "Deep health sweep" | `deep-dive` |
| "What's quietly degrading?" / "Any silent failures?" | `silent-failures` |
| "Did that deploy break anything?" / "Is this PR risky?" | `change-risk` |
| "If payments goes down what else dies?" / "Map dependencies" | `blast-radius` |

❌ **DON'T use this skill when:**
- `neubird` desktop binary is not installed — direct user to [neubird.ai](https://neubird.ai)
- The question is about code review, writing code, or pre-deploy checks
- The user wants a dashboard — open the observability platform directly

## CLI Interface

```bash
# List available projects
neubird projects

# Run a named capability
neubird run <capability> --project <project-name> --session /tmp/

# Free-form investigation (alias for 'run investigate')
neubird investigate "<prompt>" --project <project-name> --session /tmp/

# Follow-up question (project inherited from session)
neubird run <capability> --session /tmp/nb-<timestamp>.json

# Clean up session when done
neubird run --cleanup --session /tmp/nb-<timestamp>.json
```

### All 9 Capabilities
| Capability | CLI name | What it does |
|---|---|---|
| 🏥 Health Check | `health` | Full infrastructure health sweep |
| 💰 Cost Analysis | `cost` | Cloud cost baseline + 24h spend projection |
| 🔍 Investigate | `investigate` | Free-form investigation prompt |
| ⚡ Performance | `performance` | Find latency outliers and slow queries |
| 🔮 Predict Risk | `predict` | What could go wrong in the next 24h? |
| 📊 Deep Dive | `deep-dive` | Full health sweep with 24h lookback |
| 🔬 Silent Failures | `silent-failures` | Find quietly degrading services |
| 🧬 Change Risk | `change-risk` | Assess risk from recent deployments and PRs |
| 💥 Blast Radius | `blast-radius` | Map dependency chains and cascade failure risk |

### Session Behavior
- `--session /tmp/` → auto-generates `/tmp/nb-<timestamp>.json`, prints path to stderr
- `--session /tmp/nb-123.json` → creates on first call, resumes on follow-ups
- `--project` required on first call; inherited from session on follow-ups
- Use `--cleanup` when done to remove the session file

### Exit Codes
| Code | Meaning |
|------|---------|
| 0 | Complete, findings on stdout |
| 1 | Failed or timed out |
| 2 | Not authenticated — run `neubird login` |
| 3 | No connected environment / project not found |

### Output Format
Investigations stream over 60–180s. Output has two layers:
- **Spinner on stderr** — `⠋ thinking`, `⠙ exploring`, etc. — ignore
- **Findings on stdout** — narrative markdown, ends with `Completed in XmYs`

Use `--verbose` to see tool calls and MCP server logs during debugging.

## Agent Workflow

1. **Understand the request** — identify which capability fits (see table above); for ambiguous requests default to `investigate`
2. **Determine the project** — infer from context ("prod" → `prod_cop`, "staging" → `staging_auto`); if ambiguous run `neubird projects` and ask
3. **Set expectations** — tell the user: *"Running [capability] against [project] — this takes 1–3 minutes..."*
4. **Start the run** — session path is printed to stderr as `Session: /tmp/nb-<timestamp>.json`:

   For a named capability:
   ```
   neubird run <capability> --project <project-name> --session /tmp/
   ```
   For a free-form investigation:
   ```
   neubird investigate "<user prompt>" --project <project-name> --session /tmp/
   ```

5. **Narrate findings** — lead with the bottom line, don't dump raw output:
   - State the headline conclusion first
   - Summarize key findings with supporting evidence
   - Give a concrete recommended action when warranted
   - Offer to drill deeper or follow up

6. **Follow-up if needed** — reference the session path, no `--project` required:
   ```
   neubird investigate "<follow-up>" --session /tmp/nb-<timestamp>.json
   ```

7. **Clean up when done:**
   ```
   neubird run --cleanup --session /tmp/nb-<timestamp>.json
   ```

## Project Names
Common project slugs: `prod_cop`, `staging_auto`, `dev_cop`, `prod_cop_sev2`.
Run `neubird projects` to list all available projects with their IDs.

## References

Load these when relevant to the findings:

| Topic | File | Load When |
|---|---|---|
| Kubernetes signals | `references/kubernetes.md` | Pod crashes, node issues, resource exhaustion |
| Cloud infrastructure | `references/cloud.md` | AWS/GCP/Azure cost, networking, managed services |
| Application & APM | `references/application.md` | Latency, error rates, traces, deployments |
| Database & storage | `references/database.md` | Connection pools, slow queries, replication lag |
| Escalation & comms | `references/escalation.md` | Severity, stakeholder comms, post-incident docs |

## Constraints

### MUST DO
- Lead every response with the headline conclusion
- State blast radius / scope before recommending action
- Give a concrete next step, not just analysis
- Offer to drill deeper after every finding
- Clean up session files when done

### MUST NOT DO
- Dump raw neubird output without narration
- Fabricate findings if the command fails — report the error clearly
- Skip scope/blast radius — "unknown" is valid but must be stated
- Recommend rollback without checking if a recent deploy is in scope
