# AI_OS Development Telemetry

This folder stores local-only development telemetry for AI_OS build work.

The ledger is for operator review, validation history, and future safe summaries. It must not collect secrets, API keys, broker credentials, webhook payloads, or live trading state.

## Files

- `AIOS_DEVELOPMENT_TELEMETRY_LEDGER.csv`: append-friendly spreadsheet ledger.
- `AIOS_DEVELOPMENT_TELEMETRY_LEDGER.json`: structured mirror for scripts and future reports.

## Allowed Data

- run ID
- worker ID
- branch name
- mode: `DRY_RUN` or `APPLY`
- file type counts
- LOC changed
- validation timing
- error counts
- clean-state result
- next safe action

## Blocked Data

- secrets
- API keys
- broker tokens
- OANDA credentials
- webhook secrets
- live order data
- private keys

Telemetry is report-only. It must not trigger APPLY, staging, commit, push, broker execution, or live trading.
