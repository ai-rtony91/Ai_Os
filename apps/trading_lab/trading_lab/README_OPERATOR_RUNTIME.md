# AI_OS Trading Lab Operator Runtime

This is the local paper-only runtime for the AI_OS Trading Lab.

## Start the local server

From the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File automation/trading_lab/Start-AiOsPaperTradingLab.ps1
```

Expected result:

```text
AI_OS Trading Lab Local Paper Runtime
Paper Only: YES
Live Trading: BLOCKED
URL: http://127.0.0.1:8765
Press Ctrl+C to stop
```

Leave that PowerShell window open. Press Ctrl+C to stop the server.

## Send a fake paper signal

Open a second PowerShell window from the repo root:

```powershell
powershell -ExecutionPolicy Bypass -File automation/trading_lab/Send-AiOsFakeSignal.ps1
```

The fake signal uses the local paper fixture and updates the alert time before sending it to the local server.

## Run the runtime test

With the server still running:

```powershell
powershell -ExecutionPolicy Bypass -File automation/trading_lab/Test-AiOsPaperRuntime.ps1
```

The test checks that the server is reachable, the ledger is readable, live execution is blocked, stale signals reject, and future clock-skewed signals reject.

## Ledger location

The paper bot ledger lives here:

```text
apps/trading_lab/trading_lab/results/bot/PAPER_TRADING_BOT_LEDGER_001.json
```

The paper bot status lives here:

```text
apps/trading_lab/trading_lab/results/bot/PAPER_TRADING_BOT_STATUS_001.json
```

## What BLOCKED means

BLOCKED means the local runtime did not enable live trading, broker access, real orders, API keys, secrets, real webhooks, OANDA, or Webull.

## Why this is paper-only

This runtime accepts local fake paper signals, validates them, writes local JSON results, and keeps all real execution fields blocked. It is for local operator testing only.

## Next stage

The next stage should keep this one-command local workflow stable while improving review visibility and operator reporting.
