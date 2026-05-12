# Trading Lab Agent Runtime Bridge

Runtime means a local control layer that decides which safe work packet should happen next.

Orchestration means routing work to the right file, agent, and validator.

A validator is a safety check that looks for broken rules before work is saved.

## Current Trading Lab Chain

signal intake
-> latency
-> regime
-> risk gate
-> paper decision
-> paper result
-> scorecard
-> replay review
-> strategy ranking
-> next action

## What The Runtime Adds

The runtime adds:

- Task ownership
- Queue
- Gap routing
- Validation
- Summary
- Next-action control

## Future Next Builds

Future builds can be routed through the runtime:

- Local paper bot runner
- Local chart panel
- TradingView external handoff
- TradersPost external handoff
- Validator chain
- Dashboard status panel

All of these remain paper-only or local-planning-only until the user approves a separate APPLY step.

