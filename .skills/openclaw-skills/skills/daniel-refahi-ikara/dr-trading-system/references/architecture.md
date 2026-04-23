# Architecture

## Layers
1. Provider adapter layer
2. Calculation / strategy layer
3. Execution / approval layer
4. Reporting layer
5. Scheduling layer

## Shared engine modules
- config_loader
- market_schedule_resolver
- market_data_loader or provider adapter bridge
- indicator_engine
- entry_evaluator
- exit_evaluator
- position_sizing_engine
- proposal_builder
- state_manager
- approval_processor
- execution_engine (paper/live by mode)
- performance_calculator
- watchlist_analyzer
- report_generator
- job_runner

## Design rule
Jobs should be configuration only.
No per-job custom engine forks.
