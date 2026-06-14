# AIOS Autonomy Execute

`aios_autonomy_execute.py` is a bounded local executor for one safe AIOS
wake-build cycle. It accepts a supported goal, applies one local build action,
runs the focused validator, attempts a bounded repair when requested, and emits
a JSON report.

The first supported goal is `forex-paper-bot`. In apply mode, the executor
materializes a paper-only Forex scaffold:

- `apps/trading_lab/trading_lab/forex_paper_bot.py`
- `tests/trading_lab/test_forex_paper_bot.py`
- `docs/orchestration/AIOS_FOREX_PAPER_BOT.md`

The generated Forex bot supports EURUSD, GBPUSD, and USDJPY, validates buy and
sell paper directions, requires a stop loss, limits paper risk, calculates a
mock position size, and returns a paper decision only.

## Command

```powershell
python automation/orchestration/aios_autonomy_execute.py --goal forex-paper-bot --apply --max-repairs 1
```

The command is local-only. It does not stage, commit, push, merge, mutate queues,
mutate approvals, launch workers, launch runtime, start schedulers, start
daemons, use secrets, connect to brokers, place live trades, route real orders,
or call real webhooks.

## Safety Boundary

Human approval remains required for protected actions: staging, commit, push,
merge, destructive Git or filesystem actions, secrets, broker/live trading,
scheduler activation, queue mutation, approval mutation, and worker dispatch.

The executor is not a production runtime. It is a one-goal local build helper
that keeps live execution blocked while proving AIOS can select, write, validate,
repair once, and report a safe paper-only scaffold.
