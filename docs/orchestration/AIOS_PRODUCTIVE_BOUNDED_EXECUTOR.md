# AIOS Productive Bounded Executor

`aios_productive_bounded_executor.py` is the first productive compounding
executor for AIOS. It consumes a bounded executor handoff or an explicit
allowlisted action and performs one local paper-only build action.

Current allowlist:

- goal: `forex-paper-bot`
- action: `build_forex_risk_controls`
- writable files:
  - `apps/trading_lab/trading_lab/forex_risk_controls.py`
  - `tests/trading_lab/test_forex_risk_controls.py`
  - `docs/orchestration/AIOS_FOREX_RISK_CONTROLS.md`

Default mode is dry run. `--apply` writes only the allowlisted risk-control
files, runs `tests/trading_lab/test_forex_risk_controls.py`, and reports result,
files written, validators, repair attempts, safety flags, and next safe action.

This executor does not stage, commit, push, merge, launch Codex, call ChatGPT,
dispatch workers, mutate queues or approvals, activate a scheduler or daemon,
touch credentials, call brokers, place real orders, or call webhooks.
