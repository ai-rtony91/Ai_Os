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
