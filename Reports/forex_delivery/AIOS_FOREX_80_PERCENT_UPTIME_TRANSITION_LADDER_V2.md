# AIOS Forex 80 Percent Uptime Transition Ladder V2

## Objective

Define the future ladder from single live micro-trade proof toward an 80 percent trading-capable operating model. This document does not activate live automated trading, 22/5 trading, scheduler control, daemon control, webhook control, broker routing, credential persistence, self-approval, or LLM live order authority.

## Definition

80 percent uptime means AIOS targets 19.2 trading-capable hours per day and 4.8 maintenance hours per day. Across a 5-day forex week this means 96 trading-capable hours and 24 maintenance hours.

This is an operational availability target, not a profit guarantee.

During trading-capable windows, AIOS may prepare, validate, size, check risk, draft tickets, monitor evidence, reconcile, alert, and report. Human approval remains required for protected escalation until a separate future governance packet changes authority.

During the 20 percent maintenance window, AIOS uses time for sync, updates, upgrades, broker reconciliation, log review, evidence review, strategy refresh, risk refresh, patching, backup, dashboard review, and incident recovery.

AIOS must not become uncontrolled fully autonomous execution.

## Required Ladder Stages

| Stage | Gate | Required evidence before moving forward |
|---|---|---|
| 1 | Single live micro-trade evidence capture | One Human Owner-approved live micro-trade with sanitized evidence and no credential/account persistence. |
| 2 | Post-trade reconciliation | Closed trade, reconciled state, sanitized P/L, realized R, and incident status. |
| 3 | Paper expectancy expansion | Larger paper sample with non-rejected expectancy, profit factor, drawdown, and replay proof. |
| 4 | Demo expectancy expansion | Demo evidence that matches paper assumptions and survives reconciliation. |
| 5 | Broker reliability evidence | Broker connectivity and status evidence without persisting credentials or account IDs. |
| 6 | Latency evidence | Time-to-quote, time-to-submit, and time-to-confirm evidence from approved proof runs. |
| 7 | Spread/slippage evidence | Spread and slippage records proving caps are realistic. |
| 8 | Drawdown evidence | Drawdown bounds across paper/demo/live micro evidence. |
| 9 | Daily-loss lockout | Demonstrated daily-stop behavior in safe proof context. |
| 10 | Max-position governor | Demonstrated maximum open position enforcement. |
| 11 | Kill-switch exercise | Demonstrated kill-switch behavior and fail-closed behavior. |
| 12 | Monitoring and alerting | Operator-visible status, incident, and reconciliation alerts. |
| 13 | Incident stop procedure | Written stop path and recovery workflow for failed fills, missing stops, failed closes, or evidence gaps. |
| 14 | Human approval gate | Explicit Human Owner approval for next governed step. |
| 15 | 10-trade governed micro batch | Ten approved micro trades with complete evidence and reconciliation. |
| 16 | 25-trade governed micro batch | Twenty-five approved micro trades with stable evidence and incident review. |
| 17 | 50-trade governed micro batch | Fifty approved micro trades with drawdown, spread, slippage, and strategy robustness evidence. |
| 18 | Reduced-touch operator workflow | Reduced-touch process only after documented human gates and stop controls remain effective. |
| 19 | 80 percent uptime readiness review | Formal review of availability, maintenance, risk, broker, evidence, and incident readiness. |
| 20 | Separate future approval packet for any 22/5 or higher-automation model | New Human Owner-approved packet required before any 22/5 or higher automation model. |

## Forbidden Activation In This Packet

- No live automated loop.
- No scheduler.
- No daemon.
- No webhook.
- No hidden execution.
- No self-approval.
- No credential persistence.
- No LLM in the live order path.
- No continuous 22/5 trading activation.

## Current Status

`UPTIME_80_TRANSITION_LADDER_CREATED_NOT_ACTIVATED`

The ladder is available for planning only. Current evidence does not authorize 80 percent uptime activation.
