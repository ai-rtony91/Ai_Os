# Forex Runtime Calendar Status And Maintenance Mode V1

This packet is the calendar-aware runtime job router for AIOS Forex work.

AIOS can supervise as close to 24/7 as the host and runtime allow. Calendar status still does not authorize execution by itself. Trade eligibility remains gated by declared broker/market calendar state, owner Vacation Mode posture, kill switch, risk gates, drawdown and daily loss gates, proof, receipts, runtime permission, and broker/session availability.

## Product Semantics

Vacation Mode ON requests governed operation. It does not bypass the owner gate, market calendar, kill switch, proof, risk, receipts, runtime permission, broker/session boundary, or credential boundary.

Vacation Mode OFF means AIOS should stop new trade seeking while still allowing safe review, reporting, cleanup, and maintenance work.

The kill switch is separate from Vacation Mode. It is an emergency hard stop, blocks new trades, and requires owner attention.

## Router Postures

- `ACTIVE_SUPERVISION`: market is open and not degraded. Primary lane: `supervise_runtime`.
- `CLOSE_PROTECTION`: close is approaching. Primary lane: `protect_close`.
- `CLOSED_MAINTENANCE`: market is closed. Primary lane: `maintain_evidence`.
- `REOPEN_PREPARATION`: reopen is approaching. Primary lane: `prepare_next_session`.
- `WEEKEND_HEAVY_MAINTENANCE`: weekend closure. Primary lane: `weekend_audit`.
- `HOLIDAY_DEGRADED_MAINTENANCE`: holiday/degraded market. Primary lane: `degraded_market_safety`.
- `LOW_LIQUIDITY_MAINTENANCE`: low-liquidity/degraded market. Primary lane: `degraded_market_safety`.
- `VACATION_MODE_YEAR_ROUND_REVIEW`: maturity review. Primary lane: `vacation_mode_maturity_review`.
- `BLOCKED`: metadata, profit claim, autonomy drift, sensitive data, or banking focus failed.

## Job Lanes

Market open jobs include risk status check, kill-switch state check, spread/slippage watch, receipt capture watch, owner alert readiness, candidate metadata refresh, and proof continuity check.

Close protection jobs include no-new-risk review, open-intent receipt check, close boundary protection, owner attention for unreviewed receipts, and post-close maintenance prep.

Closed and night maintenance jobs include receipt review, PnL review, evidence compaction, report cleanup, replay validation, next-session candidate prep, backup snapshot review, and PR landing prep.

Reopen preparation jobs include next-session candidate prep, spread/slippage policy refresh, market open readiness review, and owner attention readiness.

Weekend heavy maintenance jobs include weekly expectancy review, drawdown review, trade quality review, evidence compaction, strategy retirement review, walk-forward review, risk policy review, backup snapshot review, report cleanup, and PR landing prep.

Holiday and low-liquidity degraded windows route to safety and maintenance work, not active execution.

## Cadence Terms

Daily, weekly, and monthly are review cadence terms. Yearly means Vacation Mode and year-round operating maturity. None of these terms promises trade frequency or profit frequency.

Yearly maturity is not a yearly profit promise. Daily, weekly, monthly, yearly, 22h/6d, 24/7, and Vacation Mode language must remain tied to supervision, maintenance, proof, and owner-governed readiness.

## Safety Boundary

This packet creates no scheduler, daemon, webhook, dashboard runtime, broker call, credential access, trade, bank routing, withdrawal work, transfer work, or money movement.

Banking, withdrawal, routing, transfer, and money movement are deferred only. This router blocks those as active work.

## Next Product Lane

The Vacation Mode maturity route now points to:

`AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1`

This keeps the final product centered on owner-visible Vacation Mode ON/OFF operation state instead of treating calendar maturity as live execution approval.
