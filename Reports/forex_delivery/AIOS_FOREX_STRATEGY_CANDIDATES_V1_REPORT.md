# AIOS Forex Strategy Candidates V1 Delivery Report

- Packet ID: FOREX-STRATEGY-CANDIDATES-V1
- Branch: `feature/forex-strategy-candidates-v1`

## Inspected Files

- `automation/forex_engine/market_data_normalizer.py`
- `automation/forex_engine/order_preview.py`
- `automation/forex_engine/risk_governor.py`
- `automation/forex_engine/position_sizing.py`
- `automation/forex_engine/paper_fill_simulator.py`
- `automation/forex_engine/trade_lifecycle_manager.py`
- `automation/forex_engine/balance_compounding.py`
- `docs/orchestration/AIOS_FOREX_MARKET_DATA_NORMALIZER.md`
- `docs/orchestration/AIOS_FOREX_ORDER_PREVIEW_HARDENING.md`

## Changed Files

- `automation/forex_engine/strategy_candidates.py`
- `tests/forex_engine/test_strategy_candidates.py`
- `docs/orchestration/AIOS_FOREX_STRATEGY_CANDIDATES.md`
- `Reports/forex_delivery/AIOS_FOREX_STRATEGY_CANDIDATES_V1_REPORT.md`

## Strategies Added

- `moving_average_trend`
- `breakout`

## Candidate Fields Added

- Deterministic paper candidate payload including `candidate_id`, strategy name, pair, direction, entry details, stop/take, score, reason lists, source and timestamp metadata, and `paper_only` flag.

## Rejection Reasons

- invalid market data/mode/pair
- missing/insufficient/invalid candle data
- no-trade signal
- unsupported strategy
- score below threshold
- stale data
- spread too high
- evidence path invalid

## Tests Added

- Import/constants
- valid buy/sell candidates per strategy
- no-trade and insufficient candle paths
- missing fields and invalid candle data
- unsupported strategy handling
- score threshold path
- mode gating and paper_only gating
- stale and spread blocks
- deterministic candidate IDs
- safety and source-scan tests

## Safety Boundary

- PAPER_ONLY only.
- No broker/live/demo execution, no credentials, no network, no filesystem writes.

## Validators

- Not run by Codex.

## Next Human Commands

- Run `pytest tests/forex_engine/test_strategy_candidates.py`

## Next Safe Action

- `FOREX-MULTI-TRADE-QUEUE`
