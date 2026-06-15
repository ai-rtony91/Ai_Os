# AIOS Forex Paper Session Controller

`forex_paper_session_controller.py` chains the current paper-only Forex proof components into one deterministic local session loop:

1. Risk controls.
2. Paper execution simulator.
3. Execution ledger integration.
4. Portfolio state.

The public function is:

```python
run_paper_session(signal_intents, account_snapshot=None, limits=None, market=None, config=None, **safety_flags)
```

The controller accepts paper signal/order intents, evaluates each intent before execution, records deterministic ledger events, rebuilds portfolio state after each accepted paper event, and stops at the first risk, execution, ledger, or portfolio next-trade block.

The return value includes session summary fields for trades attempted, accepted, blocked, final cash, open positions, realized PnL, daily loss used, block reasons, ledger records, and final portfolio state.

Safety boundary:

- Paper/research only.
- No broker execution.
- No credentials.
- No live trading.
- No real orders.
- No real webhooks.
- No network access.
- No scheduler, daemon, worker dispatch, queue mutation, or approval mutation.
