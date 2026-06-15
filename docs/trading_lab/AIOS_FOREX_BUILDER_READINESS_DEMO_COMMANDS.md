# AIOS Forex Builder Readiness Demo Commands

## Purpose

These commands show local paper-forward evidence without writing generated reports by default.

## Commands

```powershell
python -m automation.forex_engine.run_paper_forward_evidence_v2_demo
python -m automation.forex_engine.run_paper_forward_demo
python -m automation.forex_engine.run_evidence_bundle_demo
python -m automation.forex_engine.run_month_end_readiness_demo
```

Optional fixture override:

```powershell
python -m automation.forex_engine.run_evidence_bundle_demo --fixture-id EURUSD_5M_TREND_SAMPLE
```

## Expected Output

Each command prints compact operator-readable proof:

- mode.
- fixture.
- fixture count and regime count for the V2 command.
- strategy.
- simulated ledger or evidence status.
- paper PnL when applicable.
- aggregate paper PnL and consistency percentage for the V2 command.
- risk or evidence classification.
- readiness status.
- blocker count or blocker summary.
- protected gate status.
- next safe action.
- safety note.

## Boundary

This is local simulation only.

This is not broker paper trading. It does not prove live readiness.

No broker, OANDA, live exchange, credentials, `.env`, real orders, broker paper orders, webhooks, scheduler, daemon, network market automation, queue mutation, approval mutation, worker dispatch, commit, push, or merge is allowed by these demo commands.

Live readiness remains a protected downstream gate. Stronger out-of-sample and forward evidence is required.

`PAPER_FORWARD_READY` in these commands means local simulation readiness only. It does not authorize broker paper trading or live trading.
