# Forex Execution Control Stack V1

This packet is the execution control stack after broker runtime read-only auth proof.

## Purpose and contract

This packet defines the pre-order controls required before supervised demo execution:

- Kill switch definition and active state checks.
- Max daily loss cap definition and enforcement.
- Max trade risk cap definition and enforcement.
- Duplicate-order guard definition and duplicate detection handling.
- Order-intent audit log contract and audit write success.
- Stop-loss requirement.
- Take-profit requirement.

## Guardrails for this packet

- It does not call broker APIs.
- It does not read Bitwarden.
- It does not read credentials.
- It does not read `.env`.
- It does not place orders.
- It does not authorize demo trading.
- It does not authorize live trading.
- It does not call Bitwarden CLI.

## Control decisions

- Default state blocks at supervised demo approval.
- Success moves to `supervised_demo_order_execution`.
- Target path remains: supervised demo -> controlled micro-live exception -> live 22hr/day, 6day/week autonomous execution.

## Output contract

The evaluator emits `ExecutionControlResult` with these fields:

- `control_status`
- `current_stage`
- `next_stage`
- `blockers`
- `order_intent_id`
- `pre_order_decision`
- `kill_switch_state`
- `risk_state`
- `duplicate_guard_state`
- `audit_state`
- `broker_api_called`
- `bitwarden_cli_called`
- `credentials_read`
- `env_file_read`
- `order_execution`
- `demo_authorized`
- `live_authorized`
- `safe_next_action`

The default input for this packet is designed to be safe and ready to move into
supervised demo only after owner demo approval is granted.
