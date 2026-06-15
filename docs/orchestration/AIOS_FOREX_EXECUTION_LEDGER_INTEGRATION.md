# AIOS Forex Execution Ledger Integration

`apps/trading_lab/trading_lab/forex_execution_ledger_integration.py` connects deterministic paper execution results to a ledger-compatible paper event.

Public function:

```python
build_execution_ledger_record(execution_result, signal, account_snapshot=None, metadata=None, **safety_flags)
```

The integration accepts output from `forex_paper_execution_simulator` and emits a deterministic record for the paper ledger/report chain:

```text
signal -> risk controls -> paper execution simulator -> ledger record -> report/decision
```

Rules:

- blocked execution results become `execution_not_allowed`.
- `hold` creates a `no_fill_hold` paper event.
- buy/sell require `executed == True`, a paper order id, and a fill price.
- unsupported pairs/actions are blocked.
- realized PnL is zero unless a paper `exit_price` is provided in metadata.

This layer is paper/research only. It performs no broker execution, credential use, live trading, real orders, real webhooks, network calls, scheduler activation, daemon activation, worker dispatch, queue mutation, approval mutation, staging, commit, push, or merge.
