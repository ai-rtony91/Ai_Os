# AIOS Forex Paper Execution Simulator

`apps/trading_lab/trading_lab/forex_paper_execution_simulator.py` provides deterministic paper-only execution simulation for the Forex proof target.

Public function:

```python
simulate_paper_execution(signal, risk_result, market, config=None, **safety_flags)
```

Supported pairs:

- `EURUSD`
- `GBPUSD`
- `USDJPY`

Supported paper actions:

- `buy`
- `sell`
- `hold`

The simulator never contacts a broker, reads credentials, submits real orders, dispatches webhooks, opens network connections, starts runtimes, or writes files. Any live, broker, credential, real-order, webhook, or network safety flag blocks the simulation.

Execution is deterministic:

- `buy` fills at ask plus configured slippage.
- `sell` fills at bid minus configured slippage.
- `hold` remains allowed but does not execute.
- paper order IDs are derived from pair, action, units, and fill price.

This component is research and paper-state only. Staging, commit, push, merge, scheduler activation, daemon activation, worker dispatch, queue mutation, approval mutation, broker/live trading, credentials, real orders, and real webhooks remain human-approved or blocked by AIOS governance.
