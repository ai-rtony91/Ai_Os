# AI_OS Orchestration Schemas

This folder contains v0.1 schema and documentation contracts for the existing local-first AI_OS orchestration spine.

These contracts describe expected shapes for worker registries, worker profiles, worker inbox records, work packets, command queue entries, approval records, approval gates, validator output, commit package recommendations, locks, runtime visibility projections, state projection rules, and orchestration events.

This folder is not runtime authority by itself. Schema files and markdown contracts here do not move packets, approve work, execute commands, validate work, commit, push, deploy, start services, mutate runtime state, claim locks, release locks, alter approvals, or grant live trading/broker/OANDA/secret access.

These files are not wired into dispatcher runtime, dashboard fixtures, worker assignment, approvals, locks, or validators yet.

Current purpose:

- define the planned schema file set
- keep packet, validator, approval, lock, runtime state, read-model, and adapter-report contracts separate
- define read-only orchestration report contracts such as the Overnight Supervisor report
- define read-only runtime aggregation contracts such as the Runtime State Bundle
- define read-only validator confidence evidence for runtime and auto-git decisions
- define one shared orchestration result contract for validators, approval summaries, commit-package planners, recommendations, and supervisor consumption
- define read-only auto-git eligibility contracts without enabling execution
- prepare a safe future migration path

## Auto-Git Policy Schema

`auto_git_policy.schema.json` defines the future decision shape for `SAFE_AUTO_ALLOWED` commit, push, and merge eligibility.

It is decision evidence only. It may classify a candidate as `SAFE_AUTO_ALLOWED`, `HUMAN_REQUIRED`, or `BLOCKED`, and it must include validator requirements, stop conditions, candidate files, review findings, blocked findings, and authority boundaries.

It does not authorize staging, committing, pushing, pull request creation, merging, direct push to `main`, validator bypass, protected-path mutation, broker execution, live trading, secret handling, or credential handling.

## Validator Confidence Schema

`validator_confidence.schema.json` defines the read-only confidence evidence shape for validator chain results.

It may describe overall validator result, confidence score, confidence band, required validator gaps, failed validators, blocked findings, review findings, weighted findings, source reports, SAFE_AUTO_ALLOWED eligibility, and stop conditions.

It is evidence only. It does not authorize APPLY, staging, committing, pushing, merging, approval mutation, packet movement, runtime writes, broker execution, live trading, secret handling, or credential handling.

## Orchestration Result Contract Schema

`orchestration_result_contract.schema.json` defines the shared report object shape for DRY_RUN validators, approval summaries, commit-package planners, recommendation systems, and Overnight Supervisor adapters.

It may normalize status, severity, packet identity, worker identity, validator results, approval requirement, blocked reason, escalation reason, commit-package candidacy, next safe action, stop condition, runtime notes, evidence, and generated timestamp.

It is compatibility evidence only. It does not replace native subsystem schemas, move packets, approve work, run validators, stage files, commit, push, merge, launch workers, schedule loops, mutate runtime, handle credentials, or enable broker/live trading behavior.

## Runtime State Bundle Schema

`runtime_state_bundle.schema.json` defines the future generated evidence shape for AI_OS runtime aggregation.

It may describe packet state, worker state, lock state, validator state, approval state, escalation state, git state, supervisor state, next safe actions, stale conditions, confidence state, validator confidence, auto-git eligibility, blocking signals, human-required signals, source freshness, bundle integrity, and required evidence presence.

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

## v0.1 Event And State Projection Contract Pack

The uppercase files in this folder define the first broad orchestration schema contract pack:

- `EVENT_SCHEMA.md`
- `STATE_PROJECTION_RULES.md`
- `ORCHESTRATION_SCHEMA_INDEX.json`
- `WORKER_REGISTRY_SCHEMA.json`
- `WORKER_PROFILE_SCHEMA.json`
- `WORKER_INBOX_SCHEMA.json`
- `WORK_PACKET_SCHEMA.json`
- `COMMAND_QUEUE_SCHEMA.json`
- `APPROVAL_INBOX_SCHEMA.json`
- `APPLY_APPROVAL_GATE_SCHEMA.json`
- `VALIDATOR_OUTPUT_SCHEMA.json`
- `orchestration_result_contract.schema.json`
- `COMMIT_PACKAGE_SCHEMA.json`
- `LOCK_REGISTRY_SCHEMA.json`
- `RUNTIME_VISIBILITY_SCHEMA.json`

These files are contract documentation and schema scaffolds only. They are intended to make existing AI_OS data boundaries easier to validate later without inventing a second orchestration brain.
