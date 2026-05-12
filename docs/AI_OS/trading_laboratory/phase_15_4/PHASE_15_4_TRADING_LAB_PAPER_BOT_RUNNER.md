# Phase 15.4 Trading Lab Paper Bot Runner

Phase 15.4 adds the first local paper-only Trading Lab bot runner.

## Flow

signal fixture -> candle fixture -> latency stamp -> stale signal check -> regime check -> risk gate -> paper decision -> paper result -> scorecard -> validator report -> next action

## Safety Boundary

- Paper-only.
- Local fixture-only.
- No broker.
- No external account connection.
- No API keys.
- No secrets.
- No real webhooks.
- No real orders.
- No live market data.
- No package install.

## Runner

The runner is `apps/trading_lab/trading_lab/runner/paper_bot_runner.py`.

It loads local fixtures from `apps/trading_lab/trading_lab/fixtures/paper_runner/`, calls the existing paper risk gate, and writes outputs to `apps/trading_lab/trading_lab/results/paper_runner/`.

The only valid paper decisions are `BLOCKED` and `PAPER_SIMULATED`.

## Validator

Run:

`powershell -ExecutionPolicy Bypass -File automation/trading_lab/Test-AiOsTradingLabPaperRunner.DRY_RUN.ps1`

## Next Safe Action

Review the paper result ledger and scorecard. Add more local fixture cases only after a separate approved APPLY.
