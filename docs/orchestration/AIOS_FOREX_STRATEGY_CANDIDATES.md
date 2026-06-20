# AIOS Forex Strategy Candidates Engine

## Purpose

`strategy_candidates.py` is the canonical paper-only strategy module for Forex paper trading. It converts normalized market snapshots into deterministic trade candidates (or explicit no-trade rejections) before order preview.

## Paper-Only Boundary

- Mode is `PAPER_ONLY`.
- `paper_only=False` is rejected.
- Live/demo/broker-like source modes are blocked.
- No broker API calls, no credentials, no live execution, and no network activity.
- This module only emits candidate payloads and metadata evidence.

## Input

`generate_strategy_candidates(normalized_market_data, strategies=None, limits=None, now_timestamp=None, evidence_path=None, metadata=None)`

- `normalized_market_data` can be a full normalized market snapshot or a `normalized_for_strategy` dict.
- Required:
  - `pair`
  - `candles` or `candle` (at least one)
  - `timestamp`/`data_timestamp`
  - `paper_only=True`
  - `spread_pips`
  - `source_mode`

## Strategy Set

- Default strategies: `moving_average_trend`, `breakout`
- Unsupported strategy names are returned as rejected candidates.

### moving_average_trend

- Uses close prices.
- `short_window` and `long_window` defaults: 3 and 5.
- Buy signal: `short_ma > long_ma` and latest close above prior close.
- Sell signal: `short_ma < long_ma` and latest close below prior close.
- Otherwise no-trade.

### breakout

- Uses prior candle high/low from prior candles.
- Buy signal: latest close above prior high.
- Sell signal: latest close below prior low.
- Otherwise no-trade.

## Candidate Output

Each candidate includes:

- `candidate_id`
- `strategy_name`
- `pair`
- `direction`
- `entry_type` (`market`)
- `entry_price`
- `stop_loss`
- `take_profit`
- `risk_percent`
- `score`
- `reasons`
- `rejection_reasons`
- `source_mode`
- `timestamp`
- `spread_pips`
- `data_timestamp`
- `normalized_snapshot`
- `paper_only`

Stop/take placement:

- Buy: stop below entry, take above entry.
- Sell: stop above entry, take below entry.

Score defaults to deterministic values for signal quality and is filtered by `min_score` (default 50).

## Rejection Behavior

- Invalid market, unsupported pair/mode, missing candles/data, invalid candle data, insufficient candles, no signal, stale data, spread too high, score below threshold, unsupported strategy.

## Output Shape

- `allowed`, `decision`, `blocked_reason`, `blocked_reasons`, `warnings`, `paper_only`, `mode`, `pair`, `strategy_count`, `candidates`, `rejected_candidates`, `selected_count`, `rejected_count`, `no_trade_count`, `safety`, `evidence`, `evidence_path`, `next_safe_action`, `metadata`.

## Integration

- Input is expected from `market_data_normalizer.py`.
- Candidate output is compatible with subsequent `order_preview.py` selection flow.

## No Trade Execution

- This module does not place trades or call any live/demo/broker systems. It only creates candidates.

## Next Safe Packet

- `FOREX-MULTI-TRADE-QUEUE`
