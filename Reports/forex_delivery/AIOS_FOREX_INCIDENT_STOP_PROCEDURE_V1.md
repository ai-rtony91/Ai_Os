# AIOS Forex Incident Stop Procedure V1

## Pre-Trade Stop Conditions

- Stop if expectancy proof is not sufficient.
- Stop if take-profit evidence is missing under a packet that requires it.
- Stop if current broker proof is missing.
- Stop if max-loss or daily-stop gates are missing, conflicting, stale, or unknown.
- Stop if credentials, account IDs, raw broker payloads, `.env`, or secret files are requested.
- Stop if dashboard, Codex, an LLM, scheduler, daemon, or webhook is asked to place an order.

## In-Trade Emergency Stop Conditions

- Stop if stop-loss is missing, detached, or mismatched.
- Stop if max-loss cap is breached.
- Stop if daily-stop gate is breached.
- Stop if kill-switch state mismatches the approved state.
- Stop if broker disconnects or broker status becomes unknown.
- Stop if evidence mismatches between ticket, fill, dashboard display, and broker-side confirmation.

## Post-Trade Incident Flags

- failed fill reconciliation
- missing stop-loss record
- missing take-profit or approved no-take-profit record
- spread/slippage outside approved cap
- failed close or unknown open-trade state
- missing sanitized P/L
- missing realized R
- missing post-trade journal note

## Daily Stop Rule

If the daily stop is hit or cannot be verified as clear, no further trade may be armed until a separate review packet clears the condition.

## Max-Loss Breach Rule

If max loss is breached or cannot be measured, stop all escalation and create a sanitized incident report.

## Kill-Switch Rule

If kill-switch state is unavailable, mismatched, or failed, no arming candidate is allowed.

## Broker Disconnect Rule

If broker connection is unavailable, stale, or unverified, stop before execution and require runtime-only human proof intake.

## Evidence Mismatch Rule

If ticket, dashboard, broker-side proof, or reconciliation evidence disagree, preserve sanitized evidence and stop.

## Dashboard Mismatch Rule

The dashboard is display-only. Any dashboard indication that implies order authority is a blocker.

## Reconciliation Failure Rule

Failed reconciliation blocks the next session until a post-trade evidence packet resolves it.

## Maintenance-Window Escalation Rule

If maintenance review is skipped, mark the next trading-capable window `BLOCKED_PENDING_MAINTENANCE_REVIEW`.

## Restart Criteria

Restart review only after expectancy, ticket fields, take-profit policy, broker proof, risk gates, and incident stop evidence are current, deterministic, and sanitized.

## Rollback/Reporting Criteria

Rollback applies only to local code/report changes in a separately approved packet. Trading incidents require sanitized reporting and review, not repo reset or cleanup.
