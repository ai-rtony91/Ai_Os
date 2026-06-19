# AIOS Forex Read-Only Live Data Bridge V1

## Status

Status: READ_ONLY_IMPLEMENTATION_CONTRACT

Packet ID: AIOS-FOREX-READ-ONLY-LIVE-DATA-BRIDGE-V1

Zone: FOREX_LIVE_OPS_READ_ONLY

Human Owner: Anthony Meza

## Scope

This document defines the implemented read-only data bridge beneath the live-capable readiness bridge.

The bridge may produce sanitized dashboard/read-model truth from fixture fallback or from explicitly enabled OANDA read-only runtime inputs. It does not authorize live trading, BUY, SELL, close trade, order placement, broker write calls, secret printing, account identifier printing, order identifier printing, transaction identifier printing, commits, pushes, PR creation, or merge activity.

## What Data Is Read

Default mode reads no broker data. It returns fixture/readiness fallback.

When all runtime gates are present:

- `AIOS_FOREX_READONLY_LIVE_ENABLE=1`
- `AIOS_FOREX_BROKER=oanda`
- `OANDA_API_TOKEN` present at runtime
- `OANDA_ACCOUNT_ID` present at runtime
- `OANDA_ENVIRONMENT` set to `practice` or `live`, defaulting to `practice`

the bridge may perform GET-only OANDA reads for:

- account summary/details
- open positions
- open trades
- pending orders summary
- current pricing snapshot for selected instruments
- read-only transaction/history summary when available

All returned data is sanitized before report or dashboard consumption.

## What Is Blocked

The bridge blocks:

- POST, PUT, PATCH, DELETE
- order placement
- order modification
- order cancellation
- trade close
- position close
- broker write calls
- browser-side broker calls
- live execution
- automatic arming
- secret or account ID display
- raw broker response persistence

## Secret Handling

Environment variables are runtime inputs only. The bridge reports only presence or missing status.

The bridge must never print, persist, fixture, report, or dashboard-display:

- API token values
- account IDs
- raw authorization headers
- raw broker payloads
- order IDs
- transaction IDs
- private broker identifiers

## Fixture Dry Run

Run:

```powershell
python scripts/forex_delivery/run_read_only_live_data_bridge.py
```

Expected result:

- source type: `fixture`
- source label: `FIXTURE_NOT_LIVE`
- `LIVE_READY: false`
- live execution blocked
- sanitized report written to `Reports/forex_delivery/AIOS_FOREX_READ_ONLY_LIVE_DATA_BRIDGE_DRY_RUN_V1.md`

## Broker Read-Only Mode

Use only after the Human Owner has set runtime credentials outside the repo and chat.

Example runtime controls:

```powershell
$env:AIOS_FOREX_READONLY_LIVE_ENABLE='1'
$env:AIOS_FOREX_BROKER='oanda'
$env:OANDA_ENVIRONMENT='practice'
python scripts/forex_delivery/run_read_only_live_data_bridge.py
```

The command requires `OANDA_API_TOKEN` and `OANDA_ACCOUNT_ID` to already be present in the local runtime environment. Do not paste their values into Codex, docs, reports, screenshots, or GitHub.

## Dashboard Consumption

The dashboard consumes sanitized read-model status only.

Current dashboard code does not call OANDA or any broker endpoint from the browser. If no generated read-model is available, it displays:

- `READ_ONLY`
- `LIVE_READY: false`
- `SOURCE: FIXTURE_NOT_LIVE` or `NO_READ_MODEL_AVAILABLE`
- next safe action: run read-only live data bridge
- blocked reason

## Why Execution Is Still Blocked

Read-only data can improve operational truth, but it is not execution authority.

Live execution still requires:

- paper signal execution loop
- expected-edge evidence
- risk governor approval
- exit plan before entry
- trading history writeback
- kill switch
- Human Owner arming gate
- separate approval for broker/API write behavior

## Next Stage

Next packet:

```text
AIOS-FOREX-PAPER-SIGNAL-EXECUTION-LOOP-V1
```

That stage proves signal, risk, exit, and writeback behavior in paper mode before any live micro-trade arming gate.
