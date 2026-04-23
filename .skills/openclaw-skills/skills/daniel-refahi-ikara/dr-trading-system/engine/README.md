# Engine Modules

Reusable engine modules for `dr-trading-system`.

## Included reusable modules
- `config-loader.mjs`
- `state-manager.mjs`
- `indicator-engine.mjs`
- `entry-evaluator.mjs`
- `exit-evaluator.mjs`
- `position-sizing-engine.mjs`
- `proposal-builder.mjs`
- `paper-execution-engine.mjs`
- `approval-processor.mjs`
- `performance-calculator.mjs`
- `watchlist-analyzer.mjs`
- `report-generator.mjs`
- `job-runner.mjs`
- `provider-utils.mjs`
- `providers/moomoo-opend.mjs`

## Notes
- These are framework modules.
- Deployment-specific watchlists, jobs, state, schedules, and credentials stay outside the skill.
- The provider layer is separate from the calculation / strategy layer.
