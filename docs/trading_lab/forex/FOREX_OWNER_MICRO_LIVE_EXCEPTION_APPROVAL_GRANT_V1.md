# Forex Owner Micro-Live Exception Approval Grant V1

## Purpose

This packet records owner approval for the next controlled micro-live exception runner build after PR #1254 landed the owner micro-live exception approval gate.

This is the owner grant stage for the same lane:

- `current_stage`: `owner_micro_live_exception_approval_grant`
- `next_stage_after_success`: `controlled_micro_live_exception_runner`

## Scope and safety

- This packet approval is limited to a future max-one-live-micro-order runner.
- Micro-live means real-money live trading risk.
- This packet is an owner approval grant packet only.
- This packet does not place live orders.
- This packet does not move money.
- This packet does not call broker APIs.
- This packet does not call Bitwarden.
- This packet does not read Bitwarden.
- This packet does not read credentials.
- This packet does not read `.env`.
- This packet does not start 22h/6d runtime.
- This packet does not start scheduler, daemon, or webhook services.
- This packet does not start any autonomous runtime.
- Future runner is constrained to:
  - owner-approved minimum size policy,
  - max-one-live-micro-order,
  - no-autonomous-runtime.
- Success advances to `controlled_micro_live_exception_runner`.
- advance to controlled_micro_live_exception_runner.

## Required input fields

- `prior_approval_gate_landed`
- `supervised_demo_evidence_clean`
- `supervised_demo_order_created`
- `demo_order_status_code`
- `owner_micro_live_exception_approval`
- `owner_understands_live_money_risk`
- `owner_confirms_micro_size_only`
- `owner_confirms_max_one_live_order`
- `owner_confirms_no_autonomous_runtime`
- `owner_confirms_kill_switch_ready`
- `owner_confirms_daily_loss_cap_ready`
- `owner_confirms_trade_risk_cap_ready`
- `owner_confirms_audit_log_ready`
- `owner_confirms_future_runner_only`
- `live_order_execution`
- `money_movement`
- `broker_api_called`
- `bitwarden_cli_called`
- `credentials_read`
- `env_file_read`
- `scheduler_started`
- `daemon_started`
- `webhook_started`

## Required status outcomes

- `PRIOR_GATE_REQUIRED`
- `SUPERVISED_DEMO_EVIDENCE_REQUIRED`
- `OWNER_MICRO_LIVE_APPROVAL_CONFIRMATION_REQUIRED`
- `OWNER_LIVE_RISK_CONFIRMATION_REQUIRED`
- `MICRO_LIVE_CONTROL_CONFIRMATION_REQUIRED`
- `PROTECTED_BOUNDARY_VIOLATION`
- `OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED`

## Expected behavior

- Default status is `OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED` when all required owner confirmations and control checks are true and protected-boundary fields are false.
- The packet sets `live_order_execution`, `money_movement`, `broker_api_called`, `bitwarden_cli_called`, `credentials_read`, `env_file_read`, `scheduler_started`, `daemon_started`, and `webhook_started` to `false` in output.
- When protected flags are set, status is `PROTECTED_BOUNDARY_VIOLATION`.
- If `prior_approval_gate_landed` is false, status is `PRIOR_GATE_REQUIRED`.
- If supervised demo evidence is not clean, status is `SUPERVISED_DEMO_EVIDENCE_REQUIRED`.
- If owner approval is not collected, status is `OWNER_MICRO_LIVE_APPROVAL_CONFIRMATION_REQUIRED`.
- If live-risk acknowledgments are incomplete, status is `OWNER_LIVE_RISK_CONFIRMATION_REQUIRED`.
- If control confirmations are incomplete, status is `MICRO_LIVE_CONTROL_CONFIRMATION_REQUIRED`.
- On `OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED`, next stage is `controlled_micro_live_exception_runner`.
