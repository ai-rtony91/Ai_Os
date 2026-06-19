# AIOS Forex Paper Signal Execution Loop V1

## Status

Status: PAPER_SIMULATION_IMPLEMENTATION_CONTRACT

Packet ID: AIOS-FOREX-PAPER-SIGNAL-EXECUTION-LOOP-V1

Zone: FOREX_EXECUTION_SIMULATION

Human Owner: Anthony Meza

## Scope

This packet implements the first complete governed paper forex loop:

```text
signal -> risk gate -> paper entry -> exit plan -> paper close/reconcile -> trading history writeback
```

It does not authorize live trading, live order placement, live close behavior, broker write calls, secret reads, account identifier handling, transaction identifier handling, package changes, commits, pushes, PR creation, or merge activity.

## What The Paper Loop Does

The loop creates a deterministic `PAPER_SIMULATION` result for a selected pair, defaulting to `EUR_USD`.

The aggregate result includes:

- selected pair
- signal side: `BUY`, `SELL`, or `NONE`
- strategy name
- confidence
- signal reason
- spread/slippage status
- risk approval result
- paper entry record
- exit plan status
- paper close/reconcile status
- realized paper P/L
- sanitized trading history row
- evidence path
- `live_execution_allowed: false`
- next safe action

The default fixture run uses `paper_fixture_expectancy_probe_v1`. It is evidence that the workflow can execute in paper mode, not evidence of guaranteed profit.

## Why This Is Required Before Live Arming

Live-capable trading requires more than dashboard buttons. AIOS must prove that signal, risk, exit, reconciliation, and history writeback work together before any Human Owner live arming gate can be reviewed.

This stage proves the mechanical loop in a bounded paper environment. It supports later risk-adjusted expectancy review, but it does not approve live execution.

## What Is Simulated

The implementation simulates:

- deterministic paper signal selection
- hard paper risk gate
- paper entry record
- required stop-loss, take-profit, and max-time exit plan
- paper close/reconcile
- realized paper P/L calculation
- sanitized trading history writeback evidence

All identifiers are local paper simulation identifiers only. No broker payload or real order reference is recorded.

## What Is Still Blocked

Blocked by this packet:

- live trading
- live order placement
- live close behavior
- broker write calls
- broker API mutation endpoints
- secret reads or prints
- account identifier display
- real order identifiers
- transaction identifiers
- browser-side broker API calls

`live_execution_allowed` remains `false` in the aggregate result and report.

## Trading History Evidence

The paper loop writes sanitized evidence to:

```text
Reports/forex_delivery/AIOS_FOREX_PAPER_SIGNAL_EXECUTION_LOOP_DRY_RUN_V1.md
```

The paper history row includes:

- pair
- side
- units
- entry time
- exit time
- duration
- entry price
- exit price
- realized paper P/L
- exit reason
- strategy
- risk approved
- source label
- evidence status

The row records only paper evidence. It must not contain secrets, account identifiers, real order identifiers, transaction identifiers, raw broker payloads, or credential material.

## How To Run

Run from the repo root:

```powershell
python scripts/forex_delivery/run_paper_signal_execution_loop.py
```

The script writes the sanitized report and prints a JSON summary. It requires no secrets, no network access, and no broker connection.

## Next Stage

Next packet after paper evidence review:

```text
AIOS-FOREX-LIVE-MICRO-TRADE-ARMING-GATE-V1
```

That stage may only prepare a Human Owner arming gate after paper loop evidence is reviewed for risk-adjusted expectancy. It still must not place a live trade unless a later packet separately approves the exact broker/API write behavior.
