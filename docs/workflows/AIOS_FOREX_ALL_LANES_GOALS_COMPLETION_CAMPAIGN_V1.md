# AIOS Forex All-Lanes Goals Completion Campaign V1

## Purpose

This workflow converts repo-derived Forex lanes, reports, modules, schemas, tests, branch signals, and handoff artifacts into explicit goal states.

## Scope

Allowed campaign paths:

- `automation/forex_engine/`
- `scripts/forex_delivery/`
- `tests/forex_engine/`
- `tests/fixtures/forex_delivery/`
- `docs/workflows/`
- `docs/governance/programs/epics/`
- `schemas/aios/forex/`
- `Reports/forex_delivery/`

## Route

1. Build the all-lanes goal manifest.
2. Classify each gap.
3. Route repo-actionable closure separately from owner, external, broker, live, and safety boundaries.
4. Project operating readiness as dashboard-safe local status only.
5. Enforce owner boundary language.
6. Compose the final bundle and owner handoff.
7. Stop before protected GitHub, broker, credential, account, demo/live, money, production, scheduler, daemon, or webhook actions.

## Safety Boundary

This workflow is local-only. It does not authorize broker/API access, credential access, account access, demo/live trading, order placement, order closure, money movement, production activation, autonomous trading readiness, profitable trading readiness, commit, push, PR creation, check watch, merge, or branch deletion.

## Validation

Required local validation:

- `python -m py_compile` for the seven campaign modules, seven CLI scripts, and campaign test file.
- `python -m pytest tests/forex_engine/test_forex_all_lanes_goals_completion_campaign_v1.py -q`
- all seven all-lanes CLI scripts with `--write-report --strict`
- `python -m pytest tests/forex_engine -q`
- `git diff --check`

## Stop Point

Stop at `DEFERRED_OWNER_VALIDATION`.
