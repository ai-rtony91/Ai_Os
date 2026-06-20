# AIOS Forex Trade Lifecycle Manager V1 Delivery Report

- Packet ID: FOREX-TRADE-LIFECYCLE-MISSING-ARTIFACT-REPAIR-V1
- Working tree alignment: inspected against required allowed files and repaired missing artifacts.

## Files Inspected

- `automation/forex_engine/trade_lifecycle_manager.py`
- `tests/forex_engine/test_trade_lifecycle_manager.py`
- `docs/orchestration/AIOS_FOREX_TRADE_LIFECYCLE_MANAGER.md`
- `Reports/forex_delivery/AIOS_FOREX_TRADE_LIFECYCLE_MANAGER_V1_REPORT.md`

## Files Changed

- `tests/forex_engine/test_trade_lifecycle_manager.py`
- `docs/orchestration/AIOS_FOREX_TRADE_LIFECYCLE_MANAGER.md`
- `Reports/forex_delivery/AIOS_FOREX_TRADE_LIFECYCLE_MANAGER_V1_REPORT.md`

## Close Behaviors

- Active buy and sell trades close deterministically by stop-loss/take-profit direction rules.
- Manual close, kill switch, and expiry paths are supported and return explicit `close_reason`.

## P/L Formula

- Buy: `(exit_price - entry_price) * units`
- Sell: `(entry_price - exit_price) * units`

## Lifecycle Integration

- Transition calls to canonical lifecycle utilities are used to return deterministic lifecycle status updates in-band.

## Evidence Behavior

- Evidence is returned as structured in-memory data.
- No file writes, no broker calls, and no filesystem persistence performed here.

## Tests Added

- import constants and modes
- active no-close monitoring
- buy/sell stop-loss and take-profit closes
- manual close, expiry, kill-switch closes
- inactive/mode/paper-only/evidence path failure paths
- deterministic P/L and safety/evidence assertions
- source-safety token scan

## Safety Boundary

- Paper-only mode only; no broker, live trading, credentials, real orders, or network behavior introduced.

## Validators

- Not run by Codex (per packet instruction).

## Next Human Commands

- Verify full packet test set passes:
  - `pytest tests/forex_engine/test_trade_lifecycle_manager.py`

## Next Safe Action

- Proceed to `FOREX-BALANCE-COMPOUNDING` once these tests pass.
