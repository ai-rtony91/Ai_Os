# AIOS Preemptive Security Layer V1

Status: read-only security scanner and evidence contract.

## Purpose

The Preemptive Security Layer detects risky repo and orchestration conditions before mutation. It outputs machine-readable evidence for the decision governor and future HUD display. It does not approve APPLY, write reports by default, launch workers, call webhooks, connect to brokers, trade, mutate dashboards, deploy production, or handle secrets.

## Event Categories

- `CANARY_TRIP`
- `SECRET_EXPOSURE_RISK`
- `BROKER_AUTHORITY_RISK`
- `LIVE_TRADING_RISK`
- `REAL_ORDER_RISK`
- `WEBHOOK_RISK`
- `PRODUCTION_DEPLOY_RISK`
- `DASHBOARD_MUTATION_RISK`
- `SCHEDULER_DAEMON_RISK`
- `WORKER_LAUNCH_RISK`
- `PROTECTED_AUTHORITY_RISK`
- `UNKNOWN_SECURITY_RISK`

## State Model

- `CLEAR`: no security event found. DRY_RUN and APPLY may continue only through existing approval gates.
- `WATCH`: safe generated evidence or report mentions security risk without enablement, secret exposure, executable authority, or live action. READ_ONLY/DRY_RUN may continue; APPLY is blocked.
- `REVIEW_REQUIRED`: unknown or mixed-risk evidence needs human review before APPLY.
- `STOP`: protected action, production, webhook, scheduler, daemon, worker-launch, dashboard mutation, or protected-authority risk blocks mutation.
- `SOS`: canary, secret exposure, broker authority, live trading, or real-order risk requires escalation without printing secret-like values.

## Dirty Tree Integration

The scanner consumes Dirty Tree Classifier output. It does not replace dirty-tree classification. Generated safety reports that merely mention broker, live-trading, webhook, production, or real-order risk are downgraded to `WATCH` unless they imply enablement, executable authority, secret exposure, or live action.

Dirty APPLY remains blocked. Safe `WATCH` permits only READ_ONLY/DRY_RUN routing.

## Governor Integration

The autonomy decision governor reads the security state before ranking normal work:

- `SOS` becomes the first stop candidate.
- `STOP` or `REVIEW_REQUIRED` blocks APPLY and requires review.
- `WATCH` creates a DRY_RUN-only continuation route and blocks APPLY candidates.
- `CLEAR` leaves existing governance, dirty tree, validator, approval, and protected-action gates in force.

## HUD-Ready Output

The state contract includes:

- `shield_state`
- `vault_lock_state`
- `radar_events`
- `tripwire_events`
- `boss_alert`
- `blocked_actions`
- `next_safe_action`

These fields are display-only. This layer does not add UI, buttons, dashboard mutation controls, or live response controls.

## Schemas

- `schemas/aios/security/AIOS_PREEMPTIVE_SECURITY_EVENT.v1.schema.json`
- `schemas/aios/security/AIOS_PREEMPTIVE_SECURITY_STATE.v1.schema.json`

## Local DRY_RUN Command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/security/Get-AiOsPreemptiveSecurityState.DRY_RUN.ps1 -OutputJson
```

The command is read-only and stdout-only by default.
