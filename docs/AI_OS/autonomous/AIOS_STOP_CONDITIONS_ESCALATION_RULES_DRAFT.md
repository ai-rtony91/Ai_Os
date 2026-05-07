# AIOS Stop Conditions Escalation Rules Draft

Stage: 11.4
Status: Draft planning doc

## Purpose

Define when AI_OS must stop and escalate to the operator.

## Stop Conditions

- Missing approval.
- Protected action detected.
- Secret detected.
- Broker or live trading path detected.
- MISMATCH evidence.
- INVALID DATA.
- Unknown critical path fact.
- Dirty working tree outside approved scope.

## Escalation

Report the blocker, evidence, and exact next safe action.
