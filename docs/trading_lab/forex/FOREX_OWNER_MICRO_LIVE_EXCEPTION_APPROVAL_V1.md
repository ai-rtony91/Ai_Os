# Forex Owner Micro-Live Exception Approval V1

## Purpose

This packet is the owner approval gate before `controlled_micro_live_exception`.
It verifies owner confirmation and micro-live readiness after clean supervised-demo evidence.

`owner_micro_live_exception_approval` is a repo-safe decision gate.

## Scope

- Micro-live means real-money live trading risk.
- This packet does not place live orders.
- This packet does not move money.
- This packet does not call broker APIs.
- This packet does not call Bitwarden CLI.
- This packet does not read credentials.
- This packet does not read `.env`.
- This packet does not start 22hr/day, 6day/week autonomous runtime.
- This packet does not start scheduler, daemons, or webhooks.
- This packet does not start autonomous runtime.
- This packet does not call broker APIs.
- This packet does not read Bitwarden, credentials, or `.env`.
- This packet advance to controlled_micro_live_exception_runner.
- Approval only advances to `controlled_micro_live_exception_runner`.

## Input required

- `supervised_demo_evidence_clean`
- `supervised_demo_order_created`
- `demo_order_status_code`
- `demo_order_redaction_verified`
- `max_one_demo_order_verified`
- `owner_micro_live_exception_approval`
- `owner_understands_live_money_risk`
- `owner_confirms_micro_size_only`
- `owner_confirms_max_one_live_order`
- `owner_confirms_no_autonomous_runtime`
- `owner_confirms_kill_switch_ready`
- `owner_confirms_daily_loss_cap_ready`
- `owner_confirms_trade_risk_cap_ready`
- `owner_confirms_audit_log_ready`
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

- `SUPERVISED_DEMO_EVIDENCE_REQUIRED`
- `OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED`
- `OWNER_LIVE_RISK_ACK_REQUIRED`
- `MICRO_LIVE_CONTROL_CONFIRMATION_REQUIRED`
- `PROTECTED_BOUNDARY_VIOLATION`
- `OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED`

## Expected behavior

- Default status is `OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_REQUIRED` until all owner approvals and control confirmations are true.
- When all required checks pass, the packet returns `OWNER_MICRO_LIVE_EXCEPTION_APPROVAL_GRANTED`.
- On granted status, `next_stage` is `controlled_micro_live_exception_runner`.
- The packet keeps real-money boundaries static for this stage:
  - `live_order_execution` is false
  - `money_movement` is false
  - `broker_api_called` is false
  - `bitwarden_cli_called` is false
  - `credentials_read` is false
  - `env_file_read` is false
  - `scheduler_started` is false
  - `daemon_started` is false
  - `webhook_started` is false

## Target handoff

- Stage destination on grant:
  - `controlled_micro_live_exception_runner`
- Future runner constraints are controlled by later stages and must remain:
  - micro-live max one order
  - owner-approved minimum size policy
  - kill-switch and risk caps
  - audited and redacted evidence
