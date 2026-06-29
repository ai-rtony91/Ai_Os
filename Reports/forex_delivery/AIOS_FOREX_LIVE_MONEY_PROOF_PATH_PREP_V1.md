# AIOS Forex Live Money Proof Path Prep V1

## Current status
- Governor state target: move `AIOS_FOREX_SUPERVISED_AUTONOMY_GOVERNOR_V1` from `REQUIRE_MORE_EVIDENCE` to `LIVE_MICRO_EXCEPTION_REVIEW_READY`.
- Current working branch context: `main` on active repo path `C:\Dev\Ai.Os`.
- Current reference commit: `f91cab92` (Supervised Autonomy Governor V1 landed via PR #1203).
- Live-money proof path is **evidence-only** at this stage.

## Landed governor status
- Landed component: `automation/forex_engine/supervised_autonomy_governor_v1.py`.
- Current landed governor output pattern (from current evidence): `REQUIRE_MORE_EVIDENCE`.
- `live_trading_allowed` is expected to remain `false` until every live micro-gate is explicit and verified.

## Current blockers
- `profitability_evidence_status` is not `READY`.
- `sample_size` below `30`.
- `walk_forward_windows` below `2`.
- `max_drawdown` above `0.15`.
- `profit_factor` below `2.00`.
- `expectancy` below `0.50`.
- `live_bridge_eligibility` is false.
- `evidence_age_days` above `14`.
- `kill_switch_state`, `daily_stop_state`, `max_loss_state` must be validated as active (ARMED/READY/ENABLED) and currently lack verified status in the new prep report.
- Broker/manual owner evidence is still incomplete for live micro exception review.

## Exact evidence needed for live micro exception review
Use the following exact fields in sanitized input:
- `profitability_evidence_status`: `READY`
- `sample_size`: `>= 30`
- `walk_forward_windows`: `>= 2`
- `max_drawdown`: `<= 0.15`
- `profit_factor`: `>= 2.00`
- `expectancy`: `>= 0.50`
- `broker_readiness`: `true`
- `live_bridge_eligibility`: `true` and supported by manual broker evidence
- `kill_switch_state`: `ARMED` (or `READY`/`ENABLED`)
- `daily_stop_state`: `ARMED` (or `READY`/`ENABLED`)
- `max_loss_state`: `ARMED` (or `READY`/`ENABLED`)
- `order_count_last_24h`: `<= 10`
- `tp_sl_present`: `true`
- `monitoring_ready`: `true`
- `evidence_age_days`: `<= 14`
- `owner_approval_status`: `APPROVED` or `APPROVED_FOR_LIVE_MICRO`
- `live_exception_requested`: `true`
- `live_bridge_external_evidence`: `true`
- `owner_live_micro_exception_approved`: `true`
- `realized_broker_evidence`: `false` for now (capture only after profitable trade closure if required by future review policy)

## Exact owner approvals needed
- Approve the live-micro exception review packet.
- Confirm one live micro trade only and micro-size policy.
- Confirm live kill-switch, daily stop, and max-loss preconditions before any execution attempt.
- Confirm take-profit and stop-loss are configured at both plan and broker policy level.
- Confirm no 22-hour free-run path is permitted in this exception.
- Confirm post-trade evidence capture workflow and reporting format.

## Broker manual verification checklist
1. Confirm broker account identity mapping (owner-only action, manual only).
2. Confirm live bridge readiness evidence is available for the specific broker endpoint.
3. Confirm micro-size limits are enabled and enforceable.
4. Confirm kill-switch can disable immediately from operator path.
5. Confirm daily stop gate is active and visible.
6. Confirm max loss gate is active and value is bounded.
7. Confirm order_count_last_24h limit is tracked.
8. Confirm TP/SL parameters are set and editable before any execution path.
9. Confirm monitoring feed is operational and operator-visible.
10. Confirm evidence artifacts are updated within freshness window.
11. Confirm owner acknowledgement fields (below) are all explicitly set.

## Risk gates required
- Live bridge eligibility gate
- Kill switch state gate
- Daily stop state gate
- Max loss gate
- Order-count safety gate
- TP/SL presence gate
- Monitoring readiness gate
- Evidence freshness gate
- Owner approval gate

## Kill switch required
- Must be in `ARMED`/`READY`/`ENABLED` state in the sanitized input and owner-confirmed prior to review.

## Daily stop required
- Must be in `ARMED`/`READY`/`ENABLED` state in the sanitized input and owner-confirmed prior to review.

## Max loss required
- Must be in `ARMED`/`READY`/`ENABLED` state in the sanitized input and owner-confirmed prior to review.

## TP/SL required
- `tp_sl_present` must be `true` in sanitized evidence and manually confirmed for broker side policy.

## Monitoring required
- `monitoring_ready` must be `true` in sanitized evidence.
- Operator must have a clear kill path and visibility on live-micro exception state.

## Evidence freshness requirement
- All evidence must be within `14` days (`evidence_age_days <= 14`) before governor can move to review-ready state.

## No credentials used
- Do not read `.env`, do not read credentials, and do not store account identifiers in repo files.

## No broker API used
- Do not connect to broker APIs in this proof-prep stage.

## No order execution
- No demo/live orders are allowed during proof preparation and review.

## No live authorization
- Do not authorize execution or arming from this packet.
