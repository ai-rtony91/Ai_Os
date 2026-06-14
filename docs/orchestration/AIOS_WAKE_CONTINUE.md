# AIOS Wake Continue

`aios_wake_continue.py` is a bounded wake/continue loop for one local self-build
goal. It reads repo state, detects the existing autonomy executor, selects the
next safe `forex-paper-bot` action, runs only the allowlisted local action when
`--apply` is supplied, writes JSON state, and stops.

The current action sequence is:

- missing Forex paper-bot scaffold: run the autonomy executor for
  `forex-paper-bot`
- existing Forex paper-bot scaffold: run the focused Forex paper-bot pytest
  validator

The loop writes its cycle state to stdout and to a JSON state path. By default,
the state file is written under the operating-system temp directory. Tests can
pass `--state-path` to keep state output inside a temporary workspace.

## Command

```powershell
python automation/orchestration/aios_wake_continue.py --goal forex-paper-bot --apply --max-cycles 3 --max-repairs 1
```

## Safety

This loop does not stage, commit, push, merge, mutate queues, mutate approvals,
dispatch workers, launch runtime, start schedulers, start daemons, use secrets,
connect to brokers, enable live trading, or place real orders. Those actions
remain blocked and require separate human approval where applicable.
