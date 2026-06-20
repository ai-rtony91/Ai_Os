# AIOS Forex Market Data Normalizer V1 Delivery Report

- Packet ID: FOREX-MARKET-DATA-NORMALIZER-V1
- Working tree path: `C:\Dev\Ai.Os`
- Branch: `feature/forex-market-data-normalizer-v1`

## Inspected Files

- `automation/forex_engine/order_preview.py`
- `automation/forex_engine/risk_governor.py`
- `automation/forex_engine/position_sizing.py`
- `automation/forex_engine/paper_fill_simulator.py`
- `automation/forex_engine/trade_lifecycle_manager.py`
- `automation/forex_engine/balance_compounding.py`
- `docs/orchestration/AIOS_FOREX_ORDER_PREVIEW_HARDENING.md`
- `docs/orchestration/AIOS_FOREX_RISK_GOVERNOR.md`
- `docs/orchestration/AIOS_FOREX_POSITION_SIZING.md`

## Files Changed

- `automation/forex_engine/market_data_normalizer.py`
- `tests/forex_engine/test_market_data_normalizer.py`
- `docs/orchestration/AIOS_FOREX_MARKET_DATA_NORMALIZER.md`
- `Reports/forex_delivery/AIOS_FOREX_MARKET_DATA_NORMALIZER_V1_REPORT.md`

## Normalization Behavior

- Normalizes pair symbols (`EUR_USD` -> `EURUSD`).
- Validates bid/ask positivity and spread logic.
- Computes `mid`, `spread`, `spread_pips`, and `pip_size`.
- Supports optional `timestamp` aging checks and freshness gating.
- Supports both `candle` and `candles` with OHLCV validation.
- Emits normalized payloads for preview/strategy consumers and inline evidence.

## Rejection Reasons Added

- invalid/unsupported market data and pair checks
- non-paper/source-mode rejections
- missing/invalid bid/ask/spread
- stale data and high spread blocks
- missing/invalid timestamps
- missing/invalid candle or OHLCV input
- absolute evidence path rejection

## CANDLE VALIDATION

- OHLCV fields required: `open`, `high`, `low`, `close`, `volume`, `timestamp`
- Checks value positivity and structural constraints (high/low ordering).

## Evidence Behavior

- Evidence returned as returned data only.
- No file writing.
- Evidence path must be a plain relative metadata string.

## Tests Added

- import check and defaults
- pair normalization
- spread and pip-size calculations
- missing/invalid bid/ask behavior
- high spread, stale timestamp, timestamp required behavior
- source mode pass/block tests
- candle/candles validation and normalization
- require-candle behavior
- evidence path block
- deterministic payload shape
- safety dict and blocked-reason checks
- source safety scan

## Safety Boundary

- `PAPER_ONLY` only.
- No broker/live/demo execution, no credential usage, no network, no filesystem write.

## Validators

- Not run by Codex.

## Next Human Commands

- Run `pytest tests/forex_engine/test_market_data_normalizer.py`

## Next Safe Action

- `FOREX-STRATEGY-CANDIDATES`
