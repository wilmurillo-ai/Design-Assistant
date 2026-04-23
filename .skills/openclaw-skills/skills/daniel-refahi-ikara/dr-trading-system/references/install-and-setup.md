# Install and Setup

This file explains how to **enable** and **use** `dr-trading-system` in a local workspace.

---

## What you get from this skill

The skill provides:
- reusable engine modules
- provider adapter contract
- example provider adapter
- example strategy config
- example watchlist/job/report configs
- paper-first workflow design
- daily assessment mode pattern

The skill does **not** provide a fully configured live deployment out of the box.

---

## Enable the skill

### 1. Install the skill into the workspace
Install `dr-trading-system` in the target workspace.

### 2. Start the conversational wizard
After installation, tell the agent:

**Use `dr-trading-system` and guide me through the setup wizard.**

The agent should then ask setup questions one at a time and generate local deployment files.

### 3. Read the key references if needed
Before or during deployment, read:
- `references/overview.md`
- `references/architecture.md`
- `references/provider-adapter-contract.md`
- `references/usage-patterns.md`
- `references/wizard-v1.md`
- `references/wizard-question-flow.md`

### 3. Decide your deployment mode
Choose one:
- **Daily Assessment Mode** — for diagnostics while validating provider quality
- **Trusted Paper Mode** — only after provider freshness is proven reliable

For a new deployment, start with:
- **Daily Assessment Mode**

---

## Use the skill in a workspace

### 1. Copy the examples into your local workspace structure
Use these examples as starting points:
- `references/examples/trend_breakout_v1.yml`
- `references/examples/watchlist.example.yml`
- `references/examples/job.example.yml`
- `references/examples/provider.example.yml`
- `references/examples/daily_assessment_report_v1.yml`

### 2. Create local configs
Create local deployment files for:
- provider config
- strategy config(s)
- watchlist config(s)
- job config(s)
- report template config(s)

### 3. Keep local-only items outside the skill
Do **not** put these inside the reusable skill package:
- secrets
- credentials
- provider session info
- runtime state
- generated reports
- real schedules
- machine-specific paths

### 4. Create local runtime folders
Each local job should have local state/report folders for:
- pending proposals
- open positions
- closed positions
- performance summary
- watchlist summary
- approvals log
- generated reports

### 5. Configure the provider locally
The provider connection config should stay local and contain things like:
- host
- port
- interpreter/runtime path
- provider-specific connection values

### 6. Run daily assessment first
Before trusting signals:
- run the system in daily assessment mode
- confirm provider freshness/status is acceptable
- confirm stale or permission-blocked data is clearly reported
- confirm report output matches expectations

### 7. Only then trust paper proposals
Paper proposals should only become meaningful after the provider data path is proven healthy.

---

## Recommended first rollout

Use a small first rollout:
- 1 strategy
- 1 market
- 2 watchlists
- paper mode only
- approvals required for buys and sells

This keeps troubleshooting manageable.

---

## Safe operating rule

Do not assume:
- provider reachable = provider good

You must validate:
- freshness
- permissions
- data completeness
- report sanity

before trusting strategy outputs.
