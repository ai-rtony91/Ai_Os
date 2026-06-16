# Trading Watchtower V1

Trading Watchtower V1 is a paper-only, read-only ranking and evidence layer for
Trading Lab candidate setups. It consumes caller-supplied or local JSON
candidate data, normalizes the candidates, ranks paper-trade opportunities, and
emits HUD-ready state for review.

It does not approve execution. It does not call broker modules, submit paper or
live orders, use API keys, write reports by default, mutate dashboards, launch
workers, start schedulers, activate daemons, call webhooks, or deploy anything.

## Contract

Implementation:

- `apps/trading_lab/trading_lab/watchtower.py`
- `automation/orchestration/trading/Get-AiOsTradingWatchtower.DRY_RUN.ps1`
- `schemas/aios/trading/AIOS_TRADING_WATCHTOWER_RESULT.v1.schema.json`
- `schemas/aios/trading/AIOS_TRADING_WATCHTOWER_CANDIDATE.v1.schema.json`

The result always emits:

- `execution_allowed=false`
- `broker_allowed=false`
- `order_submission_allowed=false`
- `live_trading_allowed=false`

HUD-ready fields are:

- `market_radar`
- `candidate_targets`
- `priority_targets`
- `market_regime`
- `watchtower_status`
- `next_best_setup`

## States

Watchtower can emit:

- `NO_SETUP`
- `WATCHING`
- `CANDIDATE_FOUND`
- `HIGH_PRIORITY`
- `INVALIDATED`
- `REVIEW_REQUIRED`

`REVIEW_REQUIRED` is fail-closed. It is used when optional security evidence
indicates STOP, SOS, a protected stop, or blocked protected/security scope.

## Ranking

Candidates are normalized, unsafe or invalid candidates are rejected, and the
remaining paper-only candidates are ranked highest score first.

The score weights:

- confidence
- evidence quality
- regime alignment
- stop/invalidation quality
- volatility context
- risk component

Stale, missing, or unknown evidence is penalized. `next_best_setup` is the top
non-invalidated paper candidate only, and it is suppressed when security
integration requires review.

## Security Integration

The watchtower can consume optional Preemptive Security, Dirty Tree, and
Decision Governor evidence. It never bypasses those controls:

- `STOP`, `SOS`, and `REVIEW_REQUIRED` security states force
  `watchtower_status=REVIEW_REQUIRED`.
- `SECURITY_SOS_DIRTY`, `PROTECTED_AUTHORITY_DIRTY`, and unknown dirty state
  force review.
- protected/security blocked reasons and blocked protected actions force
  review.

The output remains display evidence only. It must not be wired to broker
execution, real orders, dashboard mutation controls, schedulers, daemons, or
workers without a separate approved packet and safety review.
