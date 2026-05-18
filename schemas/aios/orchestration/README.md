# AI_OS Orchestration Schemas

This folder contains foundation schema stubs for the future canonical AI_OS packet contract.

These files are not wired into dispatcher runtime, dashboard fixtures, worker assignment, approvals, locks, or validators yet.

Current purpose:

- define the planned schema file set
- keep packet, validator, approval, lock, runtime state, read-model, and adapter-report contracts separate
- prepare a safe future migration path

Safety rules:

- no live trading
- no broker connection
- no secrets
- no dispatcher runtime migration from this folder alone
- no dashboard rewiring from this folder alone
- no commit or push without explicit approval

Next safe action: review these schema stubs before approving any adapter or migration work.
