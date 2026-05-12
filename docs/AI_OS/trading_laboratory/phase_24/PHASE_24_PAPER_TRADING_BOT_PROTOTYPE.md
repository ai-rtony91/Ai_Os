# Phase 24 Paper Trading Bot Prototype

## Purpose

This prototype makes AI_OS behave like a basic local paper trading bot without enabling live trading.

Workflow:

TradingView-style signal fixture -> AI_OS paper signal intake -> validation decision -> paper route preview -> paper result -> visible bot status output

## Runner

Runner path:

`apps/trading_lab/trading_lab/bot/paper_trading_bot.py`

The runner loads a local paper signal fixture and calls the Phase 21 paper signal intake logic. It writes:

- `apps/trading_lab/trading_lab/results/bot/PAPER_TRADING_BOT_STATUS_001.json`
- `apps/trading_lab/trading_lab/results/bot/PAPER_TRADING_BOT_LEDGER_001.json`
- `apps/dashboard/mock-data/paper-trading-bot-status.example.json`

## Decision Values

The bot decision is one of:

- ACCEPT
- REJECT
- REVIEW

ACCEPT means the local paper signal passed validation and produced a paper route preview. It does not mean execution is allowed.

## Safety Boundary

This prototype is paper-only and local-only.

Blocked:

- live trading
- broker
- OANDA
- Webull
- API keys
- secrets
- real orders
- real webhooks
- live market data
- account connection
- autonomous execution

## Validation

Run:

```powershell
python -m compileall apps/trading_lab/trading_lab
powershell -ExecutionPolicy Bypass -File automation/trading_lab/Test-AiOsPaperTradingBot.DRY_RUN.ps1
```

Next safe action: review the paper bot status output and keep all execution paths blocked.
