# Forex Engine v1 Sprint 14 - Paper Readiness Gate

## Status

Paper-only, simulation-only, local-only readiness gate.

This document does not authorize broker APIs, OANDA, real orders, real webhooks, real market data, secrets, scheduler behavior, daemon behavior, worker launch, runtime mutation, telemetry mutation, dashboard mutation, Cloudflare work, commit, push, merge, or unattended trading.

## What The Gate Proves

The Sprint 14 readiness gate proves that AI_OS can evaluate a deterministic mock Forex signal through existing paper-only engine components and return safe review evidence.

The gate uses:

- existing `ForexEngineConfig` paper-only validation.
- existing `validate_signal` structural checks.
- existing deterministic `ConfidenceEngine` scoring.
- existing `RiskEngine` paper trade allowance checks.
- local fixture-style mock signal data.

The readiness result includes:

- `status`: `PAPER_READY` or `PAPER_REJECTED`.
- `reason` and `reasons`.
- `risk_flags`.
- `blocked_actions`.
- `next_safe_action`.
- signal summary.
- validation, confidence, and risk evidence.
- safety booleans proving external execution paths stayed disabled.

`PAPER_READY` means the mock signal is acceptable for supervised paper review only. It does not mean live trading readiness.

## What Remains Blocked

The following remain blocked:

- broker API calls.
- OANDA calls.
- real order submission.
- real webhook execution.
- real market data fetches.
- secret or API key loading.
- account data.
- scheduler or daemon startup.
- worker launch.
- runtime or telemetry mutation.
- dashboard or Cloudflare implementation.
- unattended or live trading.

## How Anthony Can Run It

From `C:\Dev\Ai.Os`:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python -m automation.forex_engine.run_readiness_demo
```

The direct script form is also supported from repo root:

```powershell
python automation/forex_engine/run_readiness_demo.py
```

To run the focused tests:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python -m pytest tests/forex_engine -q -p no:cacheprovider
```

The demo prints deterministic JSON to the terminal. It does not write files, start services, launch workers, call a network, load secrets, send webhooks, or place orders.

## What AI_OS Can Build Next

The next safe Forex Engine work is to expand the paper-only lane around this gate:

- add more local mock signal fixtures.
- add negative fixtures for low confidence, drawdown pause, and max open paper trades.
- connect readiness output to paper-only report wording.
- keep all broker, OANDA, webhook, secrets, live market data, scheduler, daemon, and worker-launch paths blocked.

Future APPLY work should mutate only explicitly approved paper-engine, test, and documentation files, with validators run before any commit.
