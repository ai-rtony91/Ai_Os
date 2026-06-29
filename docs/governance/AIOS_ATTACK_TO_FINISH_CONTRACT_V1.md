# AIOS Attack-To-Finish Contract V1

Status: canonical governance contract

## Purpose

This contract standardizes ATTACK-TO-FINISH as a universal AIOS orchestration requirement for every project, lane, packet chain, validator handoff, and completion report.

ATTACK-TO-FINISH prevents vague completion claims. A lane is not finished until it identifies the exact blocker, exact owner file, exact validator or test, exact runner or script, exact missing evidence field, exact unlock status, exact next packet, exact owner action if any, exact stop condition, and exact no-bloat guard.

This contract extends the existing orchestration authority in `automation/orchestration/README.md`, the lifecycle authority in `docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md`, the validator authority in `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md`, and the schema family in `schemas/aios/orchestration/`.

It does not authorize APPLY, commit, push, merge, broker execution, live trading, API-key handling, credential handling, production mutation, worker launch, scheduler creation, daemon creation, or dashboard mutation.

## 1. Definition

ATTACK-TO-FINISH is the required closure contract for AIOS work. It converts a goal, blocker, or partially completed lane into exact finish-line data that another worker, validator, dashboard, or Human Owner can verify without guessing.

Every completion packet must produce a top-level `ATTACK_TO_FINISH` block. The block is evidence and routing metadata only. It is not approval authority.

## 2. Required Attack Fields

Every future completion packet must output:

```text
ATTACK_TO_FINISH:
- blocker_id
- blocker_status
- exact_blocker
- canonical_owner_file
- test_file
- runner_script
- missing_evidence_field
- unlock_status_required
- next_packet_name
- owner_action_required
- stop_condition
- no_bloat_guard
```

Allowed `blocker_status` and `unlock_status_required` values are:

- `PROVEN`
- `PARTIAL`
- `NOT_PROVEN`
- `BLOCKED`
- `REVIEW_REQUIRED`
- `READY_FOR_OWNER_REVIEW`
- `OWNER_APPROVED`
- `COMPLETE`

Use `NONE` only for a string field when no blocker, evidence field, runner, owner action, or next packet is required. Do not omit the field.

## 3. Required Packet Chain Behavior

A packet chain must preserve ATTACK-TO-FINISH state from intake through final report.

Each packet in a chain must:

- inherit unresolved ATTACK-TO-FINISH fields from the prior packet.
- update fields only with repo evidence, validator output, or explicit Human Owner instruction.
- keep unresolved fields visible as `UNKNOWN`, `NONE`, or a specific blocker.
- name the next packet when the current packet cannot finish the lane.
- stop when the next packet cannot be named without guessing.

Packet chains must not replace exact blocker data with broad summaries such as "needs review", "continue work", or "more validation needed" unless the exact owner file, validator, runner, and missing evidence field are also named.

## 4. Required Blocker Taxonomy

Blockers must use the most specific applicable class:

- `BRANCH_MISMATCH`
- `DIRTY_STATE_OUTSIDE_ALLOWED_FILES`
- `MISSING_CANONICAL_OWNER`
- `DUPLICATE_OWNER_RISK`
- `MISSING_VALIDATOR`
- `UNSAFE_RUNNER`
- `CREDENTIAL_API_BROKER_BANK_LIVE_ACTION_RISK`
- `FAILED_VALIDATOR`
- `UNCLEAR_UNLOCK_CONDITION`
- `UNCLEAR_OWNER_APPROVAL_REQUIREMENT`
- `MISSING_EVIDENCE_FIELD`
- `PACKET_CHAIN_GAP`
- `NO_BLOCKER`

`NO_BLOCKER` is valid only when `blocker_status` is `PROVEN`, `READY_FOR_OWNER_REVIEW`, `OWNER_APPROVED`, or `COMPLETE`.

## 5. Required Owner-File Resolution

`canonical_owner_file` must name the single existing owner file that governs the work whenever one exists.

Resolution order:

1. `AGENTS.md` for AI assistant conduct, tokenized packet governance, protected gates, prompt routing, and top-level repo authority.
2. `README.md` for human front-door identity and repo orientation.
3. `docs/governance/source-of-truth-map.md` for owner mapping.
4. `docs/audits/active-system-map.md` for active system dependency mapping.
5. Domain-specific governance, workflow, schema, security, architecture, or audit owner named by those maps.

If no owner file exists, the packet must set:

- `blocker_id: MISSING_CANONICAL_OWNER`
- `blocker_status: BLOCKED`
- `canonical_owner_file: UNKNOWN`
- `stop_condition: missing canonical owner`

Workers must not create a duplicate owner to satisfy this field.

## 6. Required Validator/Runner Resolution

`test_file` must name the exact validator, test file, or validation command that proves the lane state.

`runner_script` must name the exact runner or script required to produce evidence. If no runner is needed, set `runner_script: NONE` and explain the no-runner condition in `exact_blocker` or `no_bloat_guard`.

If validation is required and no validator exists, the packet must set:

- `blocker_id: MISSING_VALIDATOR`
- `blocker_status: BLOCKED`
- `test_file: UNKNOWN`
- `stop_condition: missing validator`

If a runner would touch credentials, API keys, broker paths, bank/payment systems, live trading, real webhooks, production mutation, daemons, schedulers, commit, push, merge, or destructive cleanup without explicit approval, the packet must set:

- `blocker_id: UNSAFE_RUNNER`
- `blocker_status: BLOCKED`
- `stop_condition: unsafe runner`

## 7. Required Evidence-Field Resolution

`missing_evidence_field` must name the exact absent field needed to prove readiness or completion.

Examples:

- `validator_result`
- `owner_approval_id`
- `canonical_owner_file`
- `runner_exit_code`
- `sanitized_evidence_path`
- `unlock_status_required`
- `next_packet_name`
- `NONE`

Workers must not claim `COMPLETE` while `missing_evidence_field` is unknown or required.

## 8. Required Unlock-Status Logic

`unlock_status_required` must state the exact status needed before the next transition.

Valid transition meanings:

- `PROVEN`: Evidence proves the blocker is resolved.
- `PARTIAL`: Some evidence exists, but a named field, validator, or owner action is still missing.
- `NOT_PROVEN`: The claim has not been proven by repo evidence or validation.
- `BLOCKED`: A stop condition prevents continuation.
- `REVIEW_REQUIRED`: A human or validator must review before continuation.
- `READY_FOR_OWNER_REVIEW`: All evidence is present and the Human Owner can review.
- `OWNER_APPROVED`: The Human Owner approved the exact action in scope.
- `COMPLETE`: The lane is finished and no required work remains in scope.

`OWNER_APPROVED` must not be inferred from validator PASS, dashboard status, telemetry, generated reports, or worker output.

## 9. Required Owner-Action Logic

`owner_action_required` must identify exactly what Anthony or the Human Owner must do, if anything.

Allowed forms:

- `NONE`
- `review <file-or-report>`
- `approve APPLY for <exact-file-list>`
- `approve protected action <exact-action>`
- `provide missing field <field-name>`
- `land prerequisite branch <branch-name>`
- `choose canonical owner for <domain>`

Owner action must be `NONE` only when no human decision is required for the next safe step.

## 10. Required No-Bloat Logic

`no_bloat_guard` must state the exact constraint that prevents duplicate authority, redundant files, broad architecture expansion, or scope creep.

Minimum no-bloat rules:

- Reuse existing canonical owners before creating new files.
- Do not create a second source-of-truth map.
- Do not create a second repo memory.
- Do not create a second agent identity system.
- Do not create a second dashboard contract.
- Do not create a broad architecture document when a focused owner-file edit is enough.
- Do not expand a completion packet into unrelated cleanup, runtime, dashboard, trading, or automation work.

## 11. Required Stop Conditions

Codex and AIOS workers must stop instead of continuing when any of these conditions appears:

- branch mismatch.
- dirty state outside allowed files.
- missing canonical owner.
- duplicate owner risk.
- missing validator.
- unsafe runner.
- credential, API, broker, bank, live-action, real-order, real-webhook, production, daemon, scheduler, secret, commit, push, merge, or destructive-action risk.
- failed validator.
- unclear unlock condition.
- unclear owner approval requirement.

The stop report must include the ATTACK-TO-FINISH block with the exact blocker and next safe action.

## 12. Required Final Response Format

Completion reports for future AIOS lanes must include the normal packet final report plus:

```text
ATTACK_TO_FINISH:
- blocker_id: <value>
- blocker_status: <allowed-status>
- exact_blocker: <specific blocker or NONE>
- canonical_owner_file: <path or UNKNOWN>
- test_file: <path/command or UNKNOWN/NONE>
- runner_script: <path/command or UNKNOWN/NONE>
- missing_evidence_field: <field or NONE>
- unlock_status_required: <allowed-status>
- next_packet_name: <name or NONE>
- owner_action_required: <exact action or NONE>
- stop_condition: <condition or NONE>
- no_bloat_guard: <exact guard>
```

The ATTACK-TO-FINISH block must remain visible even when the packet succeeds.

## 13. Required Integration Rule For Future Codex Packets

Every future Codex completion packet must either:

1. include an `ATTACK_TO_FINISH` output block that conforms to `schemas/aios/orchestration/AIOS_ATTACK_TO_FINISH_CONTRACT.v1.schema.json`, or
2. stop with `REVIEW_REQUIRED` and name why the block cannot be completed.

Packet generators, lifecycle reports, validator reports, dashboard projections, and owner handoffs may display ATTACK-TO-FINISH evidence, but they must not treat it as approval authority.

ATTACK-TO-FINISH does not weaken `AGENTS.md`, `RISK_POLICY.md`, protected-action gates, Human Owner approval, validator requirements, commit/push/merge gates, live-trading restrictions, credential restrictions, no-secrets rules, or no-duplicate-authority rules.
