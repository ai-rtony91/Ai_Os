# AIOS Emergency Stop Rules Draft

Status: Draft planning doc
Stage: 12.8

## Stop Conditions

- secret detected
- broker path detected
- live trading path detected
- protected file change requested
- MISMATCH evidence
- INVALID DATA
- unapproved destructive action
- unknown critical fact

## Response

Stop, report evidence, mark unknowns, and provide next safe action.
