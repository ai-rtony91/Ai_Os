# Forex Runtime Maintenance Workload Execution Plan V1

## Purpose

This packet defines a metadata-only workload planner for Forex runtime maintenance windows. It answers what AIOS should prioritize when the market is closed, degraded, in post-close, in weekend or holiday posture, in low-liquidity maintenance, or moving through close/reopen transition windows.

The planner does not execute work. It routes safe maintenance focus only.

## Why Maintenance Windows Are Productive

Closed and degraded market windows are useful because AIOS can review proof, receipts, PnL, replay evidence, reports, backup snapshots, next-session readiness, and owner review queues without touching broker execution. This lets the system preserve evidence continuity and reduce next-session friction while keeping runtime actions blocked.

## Compatible Runtime Postures

The planner accepts only maintenance-compatible calendar postures:

- `CLOSED_MAINTENANCE`
- `HOLIDAY_DEGRADED_MAINTENANCE`
- `LOW_LIQUIDITY_MAINTENANCE`
- `WEEKEND_HEAVY_MAINTENANCE`
- `CLOSE_PROTECTION`
- `REOPEN_PREPARATION`

Active supervision without a maintenance recommendation blocks by calendar and routes back to the runtime calendar packet.

## Priority Order

1. Risk review for kill switch, daily loss stop, or drawdown breach.
2. Receipt review.
3. PnL review and reconciliation.
4. Evidence compaction.
5. Replay validation.
6. Report cleanup.
7. Backup snapshot review.
8. Next-session prep.
9. Owner review.
10. PR landing prep as metadata only.
11. Clean maintenance plan ready.

## Risk Review

Risk review is the highest priority. A kill switch, daily loss stop, or drawdown breach does not create runtime action. It routes to owner/risk review and keeps execution blocked.

## Receipt Review

Unreviewed receipts route to receipt review before PnL, replay, report cleanup, or PR landing prep. Raw receipts must remain sanitized and must not be echoed.

## PnL Review

Pending PnL review routes to post-execution review after receipt priority is clean. The planner blocks fake PnL and profit guarantees.

## Evidence Compaction

Evidence compaction is allowed only as metadata-only work when the policy says compaction is safe and no higher-priority receipt or PnL work exists.

## Replay Validation

Replay validation is metadata evidence work only. It does not mutate strategies, call live market data, or create execution payloads.

## Report Cleanup

Report cleanup means metadata review and repair. It does not delete files, clean the repo, stage changes, commit, push, open a PR, or merge.

## Backup Snapshot Review

Backup snapshot review is inspection only. It does not restore, delete, promote, or overwrite files.

## Next-Session Prep

Next-session prep is a metadata handoff for later packet work. It does not create runtime permission, order instructions, broker instructions, or market-data calls.

## PR Landing Prep

PR landing prep is metadata only and appears only after higher-priority receipts, PnL, evidence, replay, and reports are clean. It does not stage, commit, push, create a PR, or merge.

## Owner Review

Owner review items are queued when no higher-priority maintenance work is pending. Runtime execution still requires a separate owner-approved packet.

## Blocked Runtime Jobs

The planner always blocks new trades, demo execution, live execution, close-trade work, broker calls, credential reads, money movement, withdrawal work, bank routing, scheduler creation, daemon creation, strategy mutation, file deletion, Git mutation, PR creation, and profit promises.

## No Scheduler Or Daemon

This packet creates no scheduler, daemon, webhook, dashboard runtime, or autonomous runtime loop.

## No Broker, Trade, Credential, Or Money Work

This packet does not call brokers, import broker SDKs, read credentials, read `.env`, store secrets, move money, build banking, build withdrawals, build transfers, build ACH, build wire, build card, or build deposits.

## No File Deletion Or Repo Cleanup

This planner does not delete files, clean untracked files, restore snapshots, or perform repo cleanup.

## No Stage, Commit, Push, PR, Or Merge

This planner does not stage, commit, push, create a PR, merge, or approve any protected repo action.

## False-Positive Banking Guard

The banking scan is token-aware. Fields such as `close_approaching`, `reopen_approaching`, and `maintenance_window` do not count as ACH, banking, withdrawal, transfer, card, deposit, or money-movement focus.

## Next Safe Packets

- `AIOS_FOREX_NEXT_SESSION_PREP_AND_CANDIDATE_REFRESH_V1`
- `AIOS_FOREX_PROOF_PIPELINE_PAUSE_AND_CONTINUE_V1`
- `AIOS_FOREX_MULTI_PAIR_BURST_RECEIPT_AND_POST_BURST_REVIEW_V1`
- `AIOS_FOREX_POST_EXECUTION_REVIEW_LOOP_V1`
- `AIOS_FOREX_PROFIT_REPEATABILITY_EVIDENCE_V1`
- `AIOS_FOREX_COMPLETION_CAMPAIGN_REVIEW_REPAIR_V1`
- `AIOS_DAILY_AUTOMATION_SNAPSHOT_REVIEW_V1`
- `AIOS_FOREX_COMPLETION_CAMPAIGN_PART3_OWNER_VALIDATION_AND_PR_LANDING_V1`
- `AIOS_FOREX_VACATION_MODE_OWNER_TOGGLE_AND_OPERATION_STATE_V1`
- `AIOS_FOREX_RISK_SCALE_DOWN_REVIEW_V1`
