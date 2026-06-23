# AIOS Forex 20 Percent Maintenance Window Plan V2

## Objective

Define the maintenance side of a future 80 percent forex trading-capable operating model. This plan does not activate scheduled trading, live broker access, automation loops, or 22/5 execution.

## Budget

| Basis | Trading-capable window | Maintenance window |
|---|---:|---:|
| 24-hour day | 19.2 hours | 4.8 hours |
| 5-day forex week | 96 hours | 24 hours |

## Maintenance Windows

| Window | Purpose | Required output |
|---|---|---|
| Sync window | Bring repo, reports, and evidence state current. | Clean state note or blocked state note. |
| Update window | Apply approved local updates only. | Change summary and validator evidence. |
| Upgrade window | Plan approved upgrades without surprise runtime activation. | Upgrade plan or deferred status. |
| Dependency check window | Verify local dependencies and test harness health. | Dependency status and failures. |
| Broker reconciliation window | Review sanitized broker-side evidence if a human-executed trade occurred. | Reconciliation status without account IDs. |
| Trade reconciliation window | Match ticket, fill, stop, take-profit, exit, P/L, and realized R. | Reconciled, blocked, or incident status. |
| Evidence audit window | Confirm evidence is complete, sanitized, and traceable. | Evidence ledger status. |
| Strategy review window | Review expectancy, sample size, walk-forward, drawdown, and profit factor. | Strategy status and blockers. |
| Risk policy review window | Review max loss, daily stop, position limits, kill switch, and incident stops. | Risk gate status. |
| Backup/snapshot window | Preserve approved sanitized outputs. | Backup status or skipped status. |
| Dashboard UX review window | Confirm dashboard remains display-only and readable. | Dashboard review note. |
| Incident review window | Review any failed fill, failed stop, failed exit, failed reconciliation, or evidence gap. | Incident report or no-incident note. |
| Rollback window | Prepare rollback plan for approved local changes only. | Rollback readiness note. |
| Next-session readiness check | Confirm whether the next trading-capable window can be opened. | READY_FOR_REVIEW or BLOCKED. |

## Blocked Condition If Maintenance Is Skipped

If the 20 percent maintenance window is skipped, the next trading-capable window must be marked `BLOCKED_PENDING_MAINTENANCE_REVIEW` until sync, evidence review, risk review, and next-session readiness checks are complete.

## Safety Boundary

- No scheduler, daemon, webhook, or hidden trading loop is authorized.
- No live order, demo order, broker API call, credential read, account identifier read, or deployment is authorized.
- Human approval remains required for protected escalation.

## Current Status

`MAINTENANCE_20_PLAN_CREATED_NOT_ACTIVATED`
