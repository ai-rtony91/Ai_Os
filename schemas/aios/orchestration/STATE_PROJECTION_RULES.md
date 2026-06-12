# AI_OS Orchestration State Projection Rules v0.1.1

This document defines how AI_OS should project orchestration state from existing local-first files without inventing a new brain.

This is contract documentation only. It does not execute work, mutate runtime state, approve APPLY, move packets, claim locks, release locks, commit, push, deploy, start services, or grant broker, OANDA, secret, API-key, live-order, or live-trading access.

## Source Precedence

AI_OS state projection should prefer direct local evidence in this order:

1. Human Owner direction in the active packet or approval record.
2. `AGENTS.md`, `RISK_POLICY.md`, and applicable governance authority.
3. Approval inbox and apply approval gate records.
4. Work packet files and worker inbox records.
5. Worker registry and worker profile records.
6. Validator output and validator recommendations.
7. Commit package recommendation records.
8. Lock/path-conflict records.
9. Command queue records.
10. Telemetry and runtime visibility projections.
11. Dashboard visibility examples or API projections.

Lower-precedence generated projections must not override higher-precedence authority.

## Current Reality Aliases

The v0.1.1 schema reconciliation recognizes current AI_OS file shapes and aliases:

- `items` and `commands` both represent command queue entries depending on source age.
- `created_utc` and `updated_utc` are current packet timestamps; `created_at` and `updated_at` remain supported newer aliases.
- `approval_gate_id`, `approval_status`, and timestamp placeholder fields are current approval gate fields; `gate_id`, `gate_status`, and `created_at` remain supported newer aliases.
- `activePackets`, `failedPackets`, and `backpressure` are dashboard/runtime visibility fields; `packets` and `overall_status` remain supported projection aliases.

Schema reconciliation does not change runtime authority. These aliases only let read-only validators and future adapters understand current evidence without mutating runtime state.

## Frontend-Safe Display Contract

Future dashboard, GUI, UE5, VR, AR, and other visual state readers must consume projected state through a display-only envelope before rendering it as an action, card, node, world object, alert, lane, or command.

Every frontend-safe projection should expose these fields:

| Field | Meaning | Safe default |
|---|---|---|
| `display_state` | Human-readable state to render, such as `READY`, `REVIEW`, `BLOCKED`, `UNKNOWN`, or `DISPLAY_ONLY` | `UNKNOWN` |
| `authority_state` | Whether the object is authority or evidence, such as `CANONICAL_AUTHORITY`, `EVIDENCE_ONLY`, `DISPLAY_ONLY`, `LEGACY_REFERENCE`, or `NON_CANONICAL` | `DISPLAY_ONLY` |
| `source_path` | Primary local source path or API route used for the projection | Exact path or `UNKNOWN` |
| `source_type` | Source class, such as `canonical`, `generated_projection`, `fixture`, `example`, `archive`, `legacy`, `api_read_model`, or `git_status` | `generated_projection` |
| `freshness` | Timestamp/TTL/staleness evidence when available | `is_stale=true` when unknown |
| `blocked_actions` | Actions the frontend must not expose as direct controls | Include protected git, APPLY, approval mutation, lock mutation, worker launch, runtime mutation |
| `next_safe_action` | Operator-readable next review step | Review evidence before protected action |
| `approval_required` | Whether mutation/execution of this object would require explicit Human Owner approval | `true` for any protected action |
| `execution_allowed` | Whether this projection allows execution | `false` |
| `mutation_allowed` | Whether this projection allows state mutation | `false` |
| `stale_or_legacy` | Whether the source is stale, legacy, example, archived, or unverified | `true` when uncertain |
| `safe_for_frontend_display` | Whether the object can be shown to a frontend as display-only data | `true` only when execution and mutation are false |

Frontend readers must treat missing envelope fields as `NEEDS_REVIEW`, not as implicit permission. Visual affordances should default to review, inspect, or copy-only behavior. Buttons that stage files, commit, push, merge, mutate approvals, move packets, claim locks, launch workers, start runtimes, schedule tasks, touch broker/live trading, or access secrets are outside this display contract.

## Source Type Defaults

- `automation/orchestration/work_packets/active`, `blocked`, and `complete` are canonical packet lifecycle evidence; only `active` should be rendered as live work without an explicit state filter.
- `automation/orchestration/work_packets/proposed`, `deferred`, `rejected`, `templates`, and `examples` are non-live display/reference material.
- root `work_packets/**` is protected historical evidence, not active queue authority.
- `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json` and `APPLY_APPROVAL_GATE_001.json` are canonical approval authority evidence, but they still do not authorize a frontend to mutate approval state.
- root `approvals/**`, `relay/approvals/**`, `telemetry/approvals/**`, and archived approval inbox files are evidence/projection/reference only unless separately promoted by Human Owner.
- `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json` and dispatcher queue read models are compatibility or runtime queue evidence; active work routing should prefer work packets plus the campaign registry unless a specific queue mutation packet says otherwise.
- dashboard mock data and API projections are display sources only; they must never override source-of-truth authority.

## Worker State Projection

Worker state should be projected from:

- `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`
- `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`
- `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json`
- relevant work packet assignments
- lock/path-conflict evidence

Projected worker state may describe availability, claimed packet, lane, allowed paths, blocked paths, assignment status, and review requirements. It must not launch a worker or claim execution authority.

## Packet State Projection

Packet state should be projected from work packet files, approval records, worker inbox assignments, validator output, and completion evidence.

Known states may include `PROPOSED`, `PENDING_OPERATOR_APPROVAL`, `APPROVED`, `ASSIGNED`, `ACTIVE`, `BLOCKED`, `NEEDS_REVIEW`, `COMPLETE`, `REJECTED`, and `EXPIRED`.

If packet state conflicts across sources, projection must return `NEEDS_REVIEW` or `BLOCKED` with evidence paths.

## Command Queue State Projection

Command queue state should be projected from `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json` and related approval or packet evidence.

Queued commands are requests, compatibility records, or previews unless an explicit governed approval authorizes the next step. A queue item must not execute itself, and future frontends must not render queue rows as executable controls.

## Approval State Projection

Approval state should be projected from approval inbox records and apply approval gate records.

Approval projection must preserve Human Owner authority. A missing approval is not approval. A validator PASS is not approval. A dashboard status is not approval.

## Validation State Projection

Validation state should be projected from validator outputs and validator chain recommendations.

Validator output may support `PASS`, `WARN`, `FAIL`, `BLOCKED`, or `NEEDS_REVIEW`. It is evidence only and does not authorize APPLY, commit, push, merge, deployment, or protected-path mutation.

## Commit Package Recommendation State

Commit package state should be projected from commit package recommendation records and git evidence.

A recommendation may identify candidate files, excluded files, risk findings, and a suggested message. It must not stage, commit, push, create PRs, merge, or bypass protected main.

## Lock And Path-Conflict State

Lock state should be projected from lock registry files, path-conflict records, worker assignments, and active packet scope.

Any overlapping write ownership should project as `NEEDS_REVIEW` or `BLOCKED` until the conflict is resolved by approved workflow.

## Runtime Visibility State

Runtime visibility state should be projected from telemetry, runtime visibility files, validator evidence, worker state, packet state, approvals, locks, and command queue evidence.

Runtime visibility is generated/evidence state only. It must not become command authority.

## Dashboard Visibility State

Dashboard visibility should be projected from runtime visibility and documented API/read-model contracts.

Dashboard state is display evidence only. It must not approve work, move packets, launch workers, mutate approvals, bypass validators, or execute commands.

## Conflict Handling

When sources disagree:

- Preserve all conflicting evidence paths.
- Prefer explicit Human Owner approval over generated projection.
- Prefer approval gate records over dashboard projection.
- Prefer current packet state over stale telemetry.
- Stop for review when protected paths, approval, locks, or runtime status are ambiguous.

## Stale State Handling

State is stale when timestamps, branch, packet IDs, or evidence paths no longer match current repo reality.

Stale state should project as `NEEDS_REVIEW` unless a newer source supersedes it with clear evidence.

## Unknown Or Ambiguous State

Unknown or ambiguous state should not be guessed. The safe projection is `NEEDS_REVIEW`, with a next safe action to inspect the relevant source files.

## Stop Condition

Stop projection-driven routing when:

- approval state is unclear
- lock/path ownership conflicts
- packet state conflicts
- validator output fails or is missing for required paths
- source files are missing or malformed
- generated state contradicts higher authority
- protected trading, broker, OANDA, secret, credential, live-order, or API-key paths appear in scope
