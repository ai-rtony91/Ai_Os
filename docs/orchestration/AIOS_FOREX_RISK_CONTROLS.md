# AIOS Forex Risk Controls

`forex_risk_controls.py` is a deterministic paper/research-only risk-control
evaluator for the Forex paper bot.

The public function is:

```python
evaluate_risk_controls(signal, account, limits, **safety_flags)
```

Supported pairs are `EURUSD`, `GBPUSD`, and `USDJPY`. Supported paper actions
are `buy`, `sell`, and `hold`. A hold action is allowed with zero position size
when the account and limits are otherwise safe.

The evaluator blocks invalid pairs, missing or unsupported actions, position
size above the configured maximum, risk percent above the configured maximum,
daily loss limit hits, max-trade limit hits, live execution, broker orders,
credentials, API keys, real orders, webhooks, and network flags.

This component does not connect to brokers, read credentials, place orders, call
webhooks, use the network, mutate queues or approvals, dispatch workers, activate
schedulers or daemons, stage, commit, push, or merge.
