# AIOS Forex Continuous Bridge-to-Profit Controller V1

## Identity

- Program: `AIOS_FOREX_CONTINUOUS_BRIDGE_TO_PROFIT_CONTROLLER_V1`
- Scope: remaining governed Forex execution flow after protected demo-order final rehearsal.
- Worker boundary: local repo control only.

## Purpose

The controller lets AIOS move the remaining Forex work through a single deterministic loop:

- CONTINUE the next safe flow.
- PAUSE and record checkpoints when manual owner control is required.
- STOP with explicit unresolved blocker report.
- BRIDGE missing islands instead of stopping with vague failure states.

## Ownership Intent

Owner live-capital intent is **$1,000**.

## Baseline Rule

The baseline is owner supplied or broker snapshot derived.

The value **$10,000 is not required** as a hardcoded baseline.

`hardcoded_10000_baseline_forbidden` is enforced by controller defaults.

## Flow Continuity

The remaining flow set is compressed to three packets:

- `FLOW_1_EXECUTION_AUTHORITY_TARGET_COUNTDOWN_RUNTIME_SOS_GATE`
- `FLOW_2_SUPERVISED_DEMO_EXECUTION_EVIDENCE_AND_COUNTDOWN_CAPTURE`
- `FLOW_3_PROFIT_LOOP_LIVE_WEEK_VACATION_MODE_ACTIVATION_GATE`

## Evidence Gate

The controller must keep:

- demo-only controls,
- evidence-based promotion,
- no autonomous execution,
- and all broker/API, credential, order, money movement, and live gates blocked.

## Guardrails

- supervised demo proof required before any live capital claim.
- live profitable week is a target status, not proven.
- 22h/6d vacation mode is a target status, not active.
- SOS alerts required before vacation target status.

## Exit Conditions for this Packet

Local artifacts and host validation script generation are complete when:

- controller status and mode are generated,
- missing island map exists for unresolved blockers,
- run artifacts are written to `Reports/forex_delivery`,
- scripts and tests are in place in the approved scope.

## Blocked Items

This packet does not approve:

- live trading,
- 22h/6d runtime activation,
- vacation mode activation,
- autonomous execution,
- live broker connection,
- execution command activation.

## Next Step

Publish handoff to owner-hosted validation is blocked until local validation passes.
