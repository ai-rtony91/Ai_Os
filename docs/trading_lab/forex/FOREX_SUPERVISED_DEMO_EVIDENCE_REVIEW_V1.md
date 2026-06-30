# Forex Supervised Demo Evidence Review V1

## Purpose

This lane reviews the first supervised demo order evidence created by the practice demo execution path and determines whether it is clean enough to advance.

- Current focus: prove `supervised_demo_order_execution` evidence quality.
- Current stage: `demo_evidence_review`.
- Current result target: `owner_micro_live_exception_approval`.

## Scope

- Does not call broker APIs in this packet.
- Does not read Bitwarden.
- No Bitwarden CLI calls are made.
- Does not read credentials.
- Does not read `.env`.
- Does not start schedulers.
- Does not start daemons.
- Does not start webhooks.

## Required review signals

The following input fields are evaluated:

- `supervised_demo_order_attempted`
- `supervised_demo_order_success`
- `order_status`
- `order_status_code`
- `demo_order_execution`
- `live_order_execution`
- `money_movement`
- `broker_api_called`
- `redaction_verified`
- `max_one_order_verified`
- `state_report_present`
- `order_endpoint_redacted`
- `token_redacted`
- `account_id_redacted`
- `scheduler_started`
- `daemon_started`
- `webhook_started`

## Statuses

- `DEMO_ORDER_EVIDENCE_MISSING`: required evidence was not supplied.
- `DEMO_ORDER_NOT_CREATED`: order was not created successfully.
- `REDACTION_REVIEW_REQUIRED`: endpoint/token/account redaction is incomplete.
- `PROTECTED_BOUNDARY_VIOLATION`: protected runtime boundary flags were triggered.
- `SUPERVISED_DEMO_EVIDENCE_CLEAN`: evidence is clean and ready for approval progression.

## Decision rule

- If a protected boundary flag is present, status is `PROTECTED_BOUNDARY_VIOLATION`.
- If order evidence is missing, status is `DEMO_ORDER_EVIDENCE_MISSING`.
- If order did not reach status `created` with code `201`, status is `DEMO_ORDER_NOT_CREATED`.
- If redaction is incomplete or one-order verification fails, status is `REDACTION_REVIEW_REQUIRED`.
- If all checks pass, status is `SUPERVISED_DEMO_EVIDENCE_CLEAN`.

## Next stage

- On `SUPERVISED_DEMO_EVIDENCE_CLEAN`, the lane moves to `owner_micro_live_exception_approval`.
- Otherwise, remain in `demo_evidence_review` for owner review and evidence correction.

### Safety rule

- Reviewed evidence must be redacted for endpoint, token, and account identifiers.
- No live order execution and no money movement is allowed at this stage.

## Report and state

- This packet writes:
  - `Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_EVIDENCE_REVIEW_V1_STATE.json`
  - `Reports/forex_delivery/AIOS_FOREX_SUPERVISED_DEMO_EVIDENCE_REVIEW_V1_REPORT.md`
- Reports are redaction-safe and contain only sanitized signal and evidence summaries.
