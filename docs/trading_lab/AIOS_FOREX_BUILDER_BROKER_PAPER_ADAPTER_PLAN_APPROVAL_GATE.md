# AIOS Forex Builder Broker-Paper Adapter Plan Approval Gate

This packet adds the approval gate that follows `PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-EVIDENCE-GATE-V1`.

It is a planning approval gate only. It does not implement a broker SDK, connect to a broker, read credentials, read `.env`, call a network API, translate an order into a broker request, place broker-paper orders, or place live orders.

## Required Source Evidence

The gate requires the existing broker-paper dry-run replay evidence gate to be `DRYRUN_REPLAY_EVIDENCE_READY`.

The source evidence must still show:

- local in-memory evidence only
- false broker SDK, network/API, credential, broker-paper order, and live-order flags
- an armed kill switch
- accepted and rejected dry-run replay paths
- aggregate max loss no higher than the local daily cap

## Required Approval Fields

The approval artifact must be plan-only and must not contain real broker credential material, tokens, keys, passwords, or account IDs.

Required fields:

- `approval_scope: broker_paper_adapter_plan_only`
- `plan_mode: PLAN_ONLY`
- `broker_selection_approval: true`
- `external_auth_boundary_approval: true`
- `paper_account_boundary_approval: true`
- `network_api_plan_approval: true`
- `order_intent_translation_approval: true`
- `kill_switch_approval: true`
- `audit_log_approval: true`
- `max_loss_daily_stop_approval: true`
- `human_owner_confirmation: true`
- `approved_by_human_owner: Anthony Meza`

Forbidden approval artifact fields include `api_key`, `access_token`, `refresh_token`, `token`, `password`, `secret`, `private_key`, `credential`, `credentials`, `account_id`, `account_number`, and `live_account_id`.

## What Approval Allows

A passing result emits `ADAPTER_PLAN_APPROVAL_READY`.

That allows only paper/demo adapter planning under a future separately approved packet. It does not allow adapter implementation, broker SDK installation, broker connection, credential loading, network/API calls, broker-paper order execution, real order routing, or live trading.

## Safety Boundary

These fields remain false even when the gate passes:

- `adapter_implementation_allowed`
- `broker_sdk_allowed`
- `network_api_allowed`
- `credentials_allowed`
- `env_secret_read_allowed`
- `broker_paper_orders_allowed`
- `live_orders_allowed`
- `would_place_order`
- `order_placed`
- `broker_request_sent`
- `network_used`
- `credentials_used`
- `live_ready`
- `live_trade_ready`
- `real_order_ready`

The gate must never emit `LIVE_READY`, `BROKER_READY`, `ORDER_READY`, or `AUTO_TRADE_READY`.

## Demo

```powershell
python -m automation.forex_engine.run_broker_paper_adapter_plan_approval_gate_demo
```

Expected output includes `ADAPTER_PLAN_APPROVAL_READY`, source evidence ready true, approval complete true, paper/demo adapter planning allowed true, and all broker SDK, network/API, credential, broker-paper order, and live-order permissions false.

## Stop Point

After this gate passes, the next action is to stop for a separate Human Owner-approved broker-paper adapter implementation packet.

Broker SDKs, credentials, network/API, broker-paper orders, and live trading remain blocked.
