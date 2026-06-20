# AIOS FOREX SELF IMPROVEMENT REVIEW

## Purpose

The self-improvement review engine is the canonical paper-only analyzer for
forex run outcomes. It reads replay/evidence/supervisor outputs and proposes exactly one
bounded improvement for the next engineering iteration.

## Paper-only boundary

- Inputs and outputs are treated as paper-only artifacts.
- No live trading action is taken and no broker/demo endpoint is called.
- No credentials are loaded or used.
- No order submission and no network calls are made in runtime analysis.
- No filesystem writes occur in runtime module; outputs are returned as in-memory dicts.

## Accepted inputs

- `session_replay`: canonical replay summary-like dict.
- `evidence_summary`: canonical evidence summary-like dict.
- `supervisor_summary`: long-run cycle summary-like dict.
- `requested_change`: optional free text describing the next intended change.
- `limits`: optional reviewer thresholds, including `min_trades` (default 10).

## Evidence quality gate

The engine marks evidence as insufficient when either:
- `trades_closed` is below threshold (default 10), or
- required metrics are missing (`wins`, `losses`, `breakeven`, `net_pnl`).

When insufficient, the recommendation is deterministically:
- `collect_more_paper_evidence`.

## One-improvement rule

If evidence is sufficient, the engine returns exactly one `recommended_improvement` from a fixed safe set:
- tighten spread cap
- improve stale-data rejection
- reduce risk multiplier on drawdown
- improve no-trade filter
- add missing rejection regression test
- add duplicate setup blocker regression

Only one improvement is returned per invocation.

## Protected-action blocking

If `requested_change` mentions any protected action, the decision becomes
`requires_approval` and the engine does not generate paper-logic tuning recommendations.

Protected terms include: live, broker, credentials, api key, account id, order submit,
oanda submit, real trade, leverage, martingale, recovery sizing, risk increase.

The result includes:
- `protected_action_detected`
- `approval_required`
- `approval_reason`
- `no_live_setting_change = True`

## Output

The review result includes:
- evidence quality snapshot
- win/loss/breakeven counts
- win rate, net P/L, max drawdown
- risk failure summaries
- winning/losing trade summaries
- strategy and risk performance metrics
- exactly one recommended improvement and scope
- list of proposed regression tests
- `safety` metadata

## Regression tests

All recommended improvements include deterministic test names intended for the next
iteration, for example:
- stale-market-data rejection tests
- spread-cap tests
- duplicate setup blockers
- risk-drawdown reduction tests

## Relation to other modules

- `session_replay.py`: consumes session replay summaries.
- `evidence_ledger.py`: uses evidence summaries and rejection metrics.
- `long_run_paper_supervisor.py`: reads supervisor summaries for trade and rejection counts.
- `next_action_engine.py`: uses this review to derive safe next operational packet suggestions.

## Safety posture

The module produces recommendations only. It does not execute changes and does not alter
dashboard truth.

## Next safe packet

- `FOREX-DEMO-CONNECTOR-READONLY` when paper evidence is stable and mature enough.
