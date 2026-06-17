# Approval Model

Status: baseline scaffold, pending human review.

## Default Mode

All agent-driven or script-driven changes default to DRY_RUN.

DRY_RUN may:
- inspect files
- propose changes
- show diffs
- explain risks
- recommend commands

DRY_RUN must not:
- commit
- push
- deploy
- execute broker actions
- persist secrets
- bypass validation

## APPLY Mode

APPLY requires explicit human approval.

Approval should identify:
- intended files
- intended change
- expected validation
- rollback path where applicable

## Single Live Micro-Trade Exception Approval

Any future Single Live Micro-Trade Exception remains governed by `RISK_POLICY.md`.

Human Owner approval for that exception must be explicit, one-shot, non-transferable, and expiring. A stored boolean such as `approved_by_human=true` is not sufficient by itself.

Future approval packets must be bound to:
- packet ID
- approval window
- broker path
- instrument
- side
- units or notional limit
- maximum loss
- daily loss cap
- stop loss
- order type
- evidence bundle
- arming step
- stop point

Approval for a Single Live Micro-Trade Exception does not authorize credentials, commits, pushes, future trades, retry, re-entry, dashboard authority, validator authority, or broker setup unless those actions are separately and explicitly approved.

Dashboards, validators, routers, queues, telemetry, reports, generated evidence, and approval projections are evidence only. They cannot approve, arm, extend, retry, re-enter, or execute the exception.

## Protected Actions

The following require explicit approval:

- modifying root governance files
- modifying CI/security workflows
- modifying execution behavior
- modifying trading/broker-related code
- modifying secret handling
- modifying deployment behavior
- committing
- pushing
- releasing

## Forbidden Without Separate Reviewed Policy

- live trading
- broker execution
- unattended production execution
- credential collection
- secret persistence
- validation bypass
- CI bypass
