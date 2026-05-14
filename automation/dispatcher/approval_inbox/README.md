# Dispatcher Approval Inbox

The approval inbox is where workers submit APPLY requests.

Workers may inspect and plan in DRY_RUN mode, but they must not edit files until a human approves the APPLY request.

Required approval fields:

- `packet_id`
- `worker_id`
- `requested_changes`
- `files_to_change`
- `validation_summary`
- `risk_summary`
- `approval_status`
- `approved_by_human`
- `approval_timestamp`
- `next_safe_action`

Approval statuses:

- `PENDING`
- `APPROVED`
- `REJECTED`
- `REVIEW_REQUIRED`

Approval rule:

If `approved_by_human` is not true, APPLY is blocked.

