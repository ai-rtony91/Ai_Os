# AIOS Forex Builder Broker-Paper Sandbox Readiness Contract

This is a readiness contract only. It does not connect to a broker, does not need credentials, does not place broker paper orders, does not place live orders, and does not authorize live trading.

## Purpose

The contract checks whether local paper-forward evidence is strong enough to consider a future protected broker-paper sandbox adapter packet. It reads local evidence only:

- fixture coverage
- regime coverage
- simulated paper-forward ledger count
- risk-governor result
- stress result
- out-of-sample result
- combined stress/OOS gate
- safety boundaries

## Statuses

Allowed statuses:

- `NOT_READY`
- `WATCHLIST`
- `CONTRACT_READY_FOR_PROTECTED_BROKER_PAPER_SANDBOX_PACKET`

Forbidden statuses:

- `LIVE_READY`
- `BROKER_READY`
- `ORDER_READY`
- `AUTO_TRADE_READY`

`WATCHLIST` means local evidence is promising but still has a material blocker. Current stress/OOS evidence can hold the contract at WATCHLIST when disaster stress reveals a boundary. That is intentional. The contract must not lower thresholds to make the result look better.

`CONTRACT_READY_FOR_PROTECTED_BROKER_PAPER_SANDBOX_PACKET` means only that a future protected adapter-stub contract can be considered. It still does not approve broker integration or order execution.

## Current Boundaries

The contract always keeps these fields false:

- `live_trade_ready`
- `real_order_ready`
- `broker_integration_active`
- `credentials_required_now`

The contract always keeps:

- `protected_gate_required: true`

## Future Protected Approvals

A later packet would need separate Human Owner approval for:

- broker selection approval
- credentials handling approval
- paper account approval
- network/API approval
- order intent to broker-paper translation approval
- kill switch approval
- audit log approval
- max loss / daily stop approval
- human owner confirmation

Those approvals are not granted by this contract.

## Demo

```powershell
python -m automation.forex_engine.run_broker_paper_sandbox_readiness_demo
```

Expected output includes readiness status, broker-paper contract readiness, live ready false, real order ready false, broker integration active false, credentials required now false, protected gate required true, blockers, next safe action, and safety.

## Interpretation

If the result is `WATCHLIST`, the next safe packet is stress repair. If the result is contract-ready, the next safe packet is a protected adapter-stub contract. Live trading remains blocked regardless.
