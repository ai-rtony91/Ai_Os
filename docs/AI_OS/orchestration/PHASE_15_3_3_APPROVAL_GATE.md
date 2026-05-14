# Phase 15.3.3 Approval Gate

## Purpose

The approval gate creates the first explicit boundary between DRY_RUN planning and APPLY execution in AI_OS.

DRY_RUN work can inspect, propose, and report. APPLY work can change files only after a human approves the exact packet, scope, paths, and validator requirements.

## Why The Gate Exists

Parallel workers can produce useful plans, but file changes create risk when state is dirty, ownership is unclear, or paths overlap.

The approval inbox gives each risky action a local record with:

- requested action
- approval status
- human approval flag
- allowed paths
- blocked paths
- validator requirements
- commit package requirement
- push block

## DRY_RUN And APPLY Separation

DRY_RUN can propose changes and validation steps.

APPLY requires:

- approval status that allows APPLY
- `approved_by_human` set to true
- explicit allowed paths
- explicit blocked paths
- validator chain required
- commit package required

If approval is missing, stale, rejected, blocked, or expired, APPLY must not run.

## Commit And Push Boundary

APPLY approval is not commit approval.

Commit requires clean validation and an exact-file commit package.

Push requires final human review after commit readiness is confirmed.

## Future Semi-Automation

This gate supports future semi-automation by making approvals machine-readable while preserving human authority.

Automation may later read approval records, but it must still block unsafe states and must never approve itself.

## Safety Limits

This layer does not enable:

- live trading
- broker execution
- OANDA integration
- API key handling
- real webhooks
- real orders
- installs
- scheduled tasks
- startup tasks
- external calls
- commits
- pushes

## Next Safe Action

Run the approval gate validators and review their output before approving any APPLY work.
