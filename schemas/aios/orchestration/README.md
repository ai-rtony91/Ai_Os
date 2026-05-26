# AI_OS Orchestration Schemas

This folder contains foundation schema stubs for the future canonical AI_OS packet contract.

These files are not wired into dispatcher runtime, dashboard fixtures, worker assignment, approvals, locks, or validators yet.

Current purpose:

- define the planned schema file set
- keep packet, validator, approval, lock, runtime state, read-model, and adapter-report contracts separate
- define read-only orchestration report contracts such as the Overnight Supervisor report
- prepare a safe future migration path

## Overnight Supervisor Schema

`overnight_supervisor.schema.json` defines the future report shape for read-only Overnight Supervisor output.

It is report-oriented only. It may describe supervisor status, repo health, stale packets, validator recommendations, escalation items, next safe actions, packet draft previews, morning brief content, mode, generated timestamp, and authority boundary.

It does not authorize APPLY, packet movement, queue mutation, worker launch, commit, push, merge, broker execution, live trading, secret handling, or runtime persistence.

Safety rules:

- no live trading
- no broker connection
- no secrets
- no dispatcher runtime migration from this folder alone
- no dashboard rewiring from this folder alone
- no commit or push without explicit approval

Next safe action: review these schema stubs before approving any adapter or migration work.
