---
name: dr-trading-system
description: Reusable framework skill for designing and setting up strategy-job trading systems with shared engine logic, config-driven jobs, pluggable market-data providers, paper-first execution, approval-gated buy/sell workflow, and daily assessment reporting. Use when creating, installing, extending, or auditing a local trading-system deployment, especially when the user wants a conversational setup wizard, provider configuration, watchlists, strategy/job configs, paper-trading flows, or daily assessment reports.
---

# dr-trading-system

Treat this as a **framework skill**, not a ready-to-trade bot.

Use it to help the user set up or refine a local trading-system deployment with:
- provider configuration
- watchlists
- strategy configs
- job configs
- paper-mode execution flows
- approval-gated buy/sell handling
- daily assessment reports

## Default workflow

1. Confirm whether the user wants a new setup, an edit, or an audit.
2. If setup is needed, run the conversational wizard one question at a time.
3. Summarize the planned deployment before generating files.
4. Generate local deployment files from the examples and references.
5. Keep secrets, credentials, runtime state, generated reports, schedules, and deployment-specific configs outside the reusable skill package.
6. Default to paper-first and approval-gated operation unless the user explicitly asks otherwise.

## Conversational wizard

If the user asks to set up the system, guide them through the setup conversationally.

Use this exact activation phrase when helpful:

`Use dr-trading-system and guide me through the setup wizard.`

The wizard is conversation-driven. There is no separate UI or `/wizard` command.

Ask questions one at a time. At minimum, cover:
- market and broker/provider
- deployment goal
- strategy count and first strategy type
- watchlists
- daily assessment vs trusted paper mode
- approval rules for buys and sells
- local file/output locations

Before generating files, provide a short deployment summary and get confirmation if the setup has material risk or ambiguity.

## Recommended first rollout

For a first deployment, prefer:
- 1 strategy
- 1 market
- 2 watchlists
- paper mode only
- buy and sell approval required
- daily assessment mode first

## Reference map

Read only what is needed:
- `references/install-and-setup.md` — install/use flow and local deployment boundaries
- `references/overview.md` — high-level scope and operating model
- `references/architecture.md` — reusable engine structure and responsibilities
- `references/provider-adapter-contract.md` — provider adapter interface and expectations
- `references/conversational-wizard.md` — how to run the setup conversation
- `references/wizard-v1.md` — wizard structure and setup scope
- `references/wizard-question-flow.md` — question order and branching
- `references/wizard-outputs.md` — expected local files/artifacts
- `references/usage-patterns.md` — safe operating patterns
- `references/examples/` — example provider, strategy, watchlist, job, and report configs

## Boundaries

Keep these local to the deployment, not in the reusable skill:
- secrets
- provider credentials
- provider session info
- runtime state
- generated reports
- local schedules
- machine-specific paths
- deployment-specific watchlists/jobs

Do not present paper or live outputs as trustworthy until provider freshness, permissions, completeness, and report sanity have been validated.
