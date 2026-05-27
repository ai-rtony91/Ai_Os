# AI_OS Orchestration Event Schema v0.1

This document defines the first canonical AI_OS orchestration event family in plain English.

This is contract documentation only. It is not executable authority, does not approve work, does not move packets, does not mutate runtime state, does not start services, does not commit or push, and does not grant broker, OANDA, secret, API-key, live-order, or live-trading access.

Events are evidence, not approval. Validator PASS events are evidence only; validator PASS does not approve APPLY, commit, push, merge, deployment, approval mutation, worker execution, broker access, OANDA access, API-key access, or live trading.

## Event Family

The v0.1 orchestration event family is:

- `worker_registered`
- `worker_profile_updated`
- `worker_inbox_item_created`
- `work_packet_created`
- `work_packet_assigned`
- `work_packet_blocked`
- `work_packet_completed`
- `command_queued`
- `approval_requested`
- `approval_granted`
- `approval_rejected`
- `approval_gate_checked`
- `validator_started`
- `validator_passed`
- `validator_failed`
- `commit_package_recommended`
- `lock_acquired`
- `lock_released`
- `runtime_visibility_projected`
- `dashboard_visibility_refreshed`

## Required Event Fields

Every event should include:

- `event_id`: stable unique event identifier.
- `event_type`: one event type from the event family.
- `schema_version`: contract version, starting with `0.1`.
- `source`: producing component, script, validator, packet, or human action reference.
- `created_at`: ISO 8601 timestamp.
- `status`: event status such as `recorded`, `proposed`, `blocked`, `passed`, `failed`, or `superseded`.
- `subject_type`: primary object type such as `worker`, `packet`, `command`, `approval`, `validator`, `commit_package`, `lock`, or `runtime_visibility`.
- `subject_id`: primary object identifier.
- `evidence_paths`: files or records used as evidence.
- `safety`: object describing read-only, approval, mutation, and protected-path boundaries.

## Optional Event Fields

Events may include:

- `packet_id`
- `worker_id`
- `lane`
- `mode`
- `approval_id`
- `validator_id`
- `lock_id`
- `command_id`
- `commit_package_id`
- `correlation_id`
- `parent_event_id`
- `previous_status`
- `next_status`
- `message`
- `warnings`
- `errors`
- `recommendation`
- `next_safe_action`
- `metadata`

## Event Source Rules

- Events should point to existing local-first AI_OS sources such as worker registry files, worker inbox files, work packets, command queue files, approval inbox files, approval gate files, validator output, commit package recommendations, lock files, telemetry ledgers, runtime visibility files, or dashboard visibility projections.
- Events should not claim authority that the source file does not have.
- Events generated from dashboard or runtime visibility are projection evidence only.
- Events generated from validators are validation evidence only.
- Events generated from approvals must preserve Human Owner authority and must not infer approval from silence.

## Event Status Rules

- `recorded`: evidence was observed.
- `proposed`: action is suggested but not authorized.
- `pending_review`: human or validator review is needed.
- `blocked`: action cannot proceed safely.
- `passed`: validator or check passed.
- `failed`: validator or check failed.
- `superseded`: later evidence replaced this event.
- `complete`: lifecycle step is complete.

When statuses conflict, AI_OS should preserve the conflict and stop for review rather than selecting the more convenient state.

## Safety Notes

- No event may authorize autonomous APPLY.
- No event may authorize staging, committing, pushing, merging, or deployment.
- No event may bypass approval gates, validators, locks, or Human Owner authority.
- No event may unlock broker, OANDA, API-key, secret, credential, live-order, or live-trading access.
- Event consumers must treat unknown, stale, ambiguous, or conflicting event state as review-required.
