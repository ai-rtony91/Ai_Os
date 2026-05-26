# AI_OS Orchestration Schemas

This folder contains foundation schema stubs for the future canonical AI_OS packet contract.

These files are not wired into dispatcher runtime, dashboard fixtures, worker assignment, approvals, locks, or validators yet.

Current purpose:

- define the planned schema file set
- keep packet, validator, approval, lock, runtime state, read-model, and adapter-report contracts separate
- define read-only orchestration report contracts such as the Overnight Supervisor report
- define read-only runtime aggregation contracts such as the Runtime State Bundle
- define read-only auto-git eligibility contracts without enabling execution
- prepare a safe future migration path

## Auto-Git Policy Schema

`auto_git_policy.schema.json` defines the future decision shape for `SAFE_AUTO_ALLOWED` commit, push, and merge eligibility.

It is decision evidence only. It may classify a candidate as `SAFE_AUTO_ALLOWED`, `HUMAN_REQUIRED`, or `BLOCKED`, and it must include validator requirements, stop conditions, candidate files, review findings, blocked findings, and authority boundaries.

It does not authorize staging, committing, pushing, pull request creation, merging, direct push to `main`, validator bypass, protected-path mutation, broker execution, live trading, secret handling, or credential handling.

## Runtime State Bundle Schema

`runtime_state_bundle.schema.json` defines the future generated evidence shape for AI_OS runtime aggregation.

It may describe packet state, worker state, lock state, validator state, approval state, escalation state, git state, supervisor state, next safe actions, stale conditions, and confidence state.

It is read-only evidence only. It does not authorize runtime writes, heartbeat writes, packet movement, lock release, worker launch, router enforcement, escalation persistence, APPLY, commit, push, merge, broker execution, live trading, secret handling, or runtime persistence.

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
