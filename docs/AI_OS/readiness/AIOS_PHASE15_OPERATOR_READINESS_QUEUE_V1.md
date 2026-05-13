# AI_OS Phase 15 Operator Readiness Queue v1

## Purpose

The Phase 15 Operator Readiness Queue tracks whether the AI_OS operator and local workspace are ready before advanced actions, paper-routing workflows, or future execution workflows continue.

This queue is paper-only. It is a readiness checkpoint, not an execution system.

## Boundary

Allowed:

- Static readiness contract documentation.
- Mock-data readiness records.
- DRY_RUN-only validation.
- Console-output-only checks.
- Paper-only operator status review.

Blocked:

- Dashboard UI edits.
- JavaScript dashboard edits.
- Installs.
- Startup tasks.
- Secrets handling.
- Credential handling.
- Broker access.
- OANDA access.
- API key handling.
- Real orders.
- Live execution.
- Commits.
- Pushes.

## Required Readiness Fields

Every Phase 15 operator readiness record must include:

- `readiness_record_id`
- `workspace_mode`
- `operator_mode`
- `dashboard_state`
- `validator_status`
- `latency_system_status`
- `risk_gate_status`
- `regime_filter_status`
- `signal_queue_status`
- `unresolved_alerts`
- `approval_required`
- `blocked_reason`
- `readiness_score`
- `readiness_status`
- `checked_at`

## Recommended Field Meaning

- `readiness_record_id`: Unique readiness record identifier.
- `workspace_mode`: Must be `paper_only` for this scaffold.
- `operator_mode`: Human operator state, such as `review_required`.
- `dashboard_state`: Current dashboard display readiness, not UI permission.
- `validator_status`: Current DRY_RUN validator state.
- `latency_system_status`: Paper latency condition.
- `risk_gate_status`: Paper risk gate condition.
- `regime_filter_status`: Market regime review condition.
- `signal_queue_status`: Signal queue readiness condition.
- `unresolved_alerts`: List of unresolved blockers or warnings.
- `approval_required`: Must be true when readiness is not fully clear.
- `blocked_reason`: Plain-English reason advanced action remains blocked.
- `readiness_score`: Numeric readiness score from 0 to 100.
- `readiness_status`: Operator-readable status, such as `BLOCKED_REVIEW`.
- `checked_at`: Timestamp for the readiness record.

## Safety Gates

- `workspace_mode` must remain `paper_only`.
- `approval_required` must remain true unless a later approved contract defines a safe exception.
- `readiness_score` must be between 0 and 100.
- `blocked_reason` must be present when `readiness_status` is not ready.
- Live execution, broker access, OANDA access, API key handling, and real orders must remain blocked.
- The queue must not create orders, route orders, send webhooks, install dependencies, start services, or read credentials.

## Readiness Status Guidance

Recommended v1 statuses:

- `READY_FOR_REVIEW`: Paper-only state appears ready for human review.
- `REVIEW_REQUIRED`: Human review is required before continuation.
- `BLOCKED_REVIEW`: One or more blockers prevent continuation.
- `UNKNOWN`: Evidence is missing or cannot be verified.

This scaffold starts with `BLOCKED_REVIEW` because unresolved alerts and approval requirements are expected during Phase 15 planning.

## Validator Expectations

The validator should:

- Parse the mock JSON.
- Confirm every required readiness field exists.
- Confirm `workspace_mode` is `paper_only`.
- Confirm `approval_required` is true.
- Confirm `readiness_score` is numeric and between 0 and 100.
- Confirm `blocked_reason` is not blank.
- Confirm blocked safety statuses remain blocked.
- Confirm no prohibited live, broker, OANDA, API key, credential, or real order enablement fields are present.

## Non-Approval Statement

This document does not approve dashboard UI changes, JavaScript changes, installs, startup tasks, broker access, OANDA access, API key handling, real orders, live execution, commits, or pushes.
