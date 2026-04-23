# Wizard v1

Wizard v1 is the **minimum viable conversational setup flow** for local deployment.

## Goal
Capture enough information to generate:
- provider config
- strategy selection
- watchlist configs
- job configs
- report mode selection
- runtime state scaffold
- optional schedule plan

## Wizard state
Track at least:
- deployment_mode
- provider_id
- provider_connection
- market
- strategy_id
- strategy_version
- watchlists
- overlap_allowed
- jobs
- risk_defaults
- approvals_required
- report_mode
- schedule_mode
- schedule_details
- confirmation_status

## Output rule
Generate **local deployment files only**.
Do not modify the reusable skill package.

## Scope note
Use `wizard-question-flow.md` for question order.
Use `wizard-outputs.md` for file/output targets.
Use `conversational-wizard.md` for interaction style and defaults.
