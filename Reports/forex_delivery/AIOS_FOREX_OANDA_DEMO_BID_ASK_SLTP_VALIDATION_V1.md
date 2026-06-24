# AIOS Forex OANDA Demo Bid Ask SLTP Validation V1

## 1. Prior Failure Pattern

Two owner-run OANDA practice/demo attempts reached the broker and produced sanitized transaction
evidence, but both canceled before fill with the same broker-side reason:

```text
TAKE_PROFIT_ON_FILL_LOSS
```

Captured pattern:

- first owner run: order create transaction `313`, order cancel transaction `314`
- corrected future owner run: order create transaction `315`, order cancel transaction `316`
- HTTP status code observed on corrected future owner run: 201
- no `orderFillTransaction` observed
- no fill evidence captured
- no profit evidence captured
- no `120%` claim supported

## 2. Why Reference Price Failed

The corrected future packet used a static owner-supplied reference price and validated this BUY
relationship:

```text
stop_loss < reference_price < take_profit
```

That local static check was insufficient. A market order is evaluated against the executable side of
the current spread, not a stale reference price. The repeated `TAKE_PROFIT_ON_FILL_LOSS` cancel
shows that future validation must evaluate TP and SL against current bid/ask evidence immediately
before command construction.

## 3. Bid/Ask Validation Standard

This packet adds a broker-call-free local validation gate:

- module: `automation/forex_engine/oanda_demo_bid_ask_sltp_validation_v1.py`
- CLI wrapper: `scripts/forex_delivery/run_oanda_demo_bid_ask_sltp_validation_v1.py`
- test coverage: `tests/forex_engine/test_oanda_demo_bid_ask_sltp_validation_v1.py`

The validator accepts only sanitized, non-secret operator or upstream supplied numeric inputs:

- `--instrument EUR_USD`
- `--direction BUY` or `SELL`
- `--bid`
- `--ask`
- `--stop-loss`
- `--take-profit`
- `--min-distance-pips`
- `--pip-size`

It does not fetch broker quotes, read live market data, read credentials, read account IDs, read
Windows Vault, read environment variables, read `.env`, call OANDA, place orders, create schedulers,
create daemons, create webhooks, stage, commit, or push.

## 4. BUY Executable Side Rule

For BUY validation:

- executable entry side is `ask`
- stop loss must be below the current `bid`
- stop loss must be at least the configured minimum distance below `bid`
- take profit must be above the current `ask`
- take profit must be at least the configured minimum distance above `ask`
- take profit at or below `ask` is blocked as loss-side risk

BUY side blockers:

- `BLOCKED_BY_BUY_STOP_LOSS_NOT_BELOW_BID`
- `BLOCKED_BY_BUY_TAKE_PROFIT_NOT_ABOVE_ASK`
- `BLOCKED_BY_MIN_DISTANCE`

## 5. SELL Executable Side Rule

For SELL validation:

- executable entry side is `bid`
- stop loss must be above the current `ask`
- stop loss must be at least the configured minimum distance above `ask`
- take profit must be below the current `bid`
- take profit must be at least the configured minimum distance below `bid`
- take profit at or above `bid` is blocked as loss-side risk

SELL side blockers:

- `BLOCKED_BY_SELL_STOP_LOSS_NOT_ABOVE_ASK`
- `BLOCKED_BY_SELL_TAKE_PROFIT_NOT_BELOW_BID`
- `BLOCKED_BY_MIN_DISTANCE`

## 6. Minimum Distance Rule

Minimum distance is calculated locally:

```text
minimum_distance = min_distance_pips * pip_size
```

The default intended EUR/USD example is:

```text
min_distance_pips: 2
pip_size: 0.0001
minimum_distance: 0.0002
```

The validator blocks zero, negative, non-numeric, missing, placeholder, or side-incompatible values.
It also blocks an `ask` value that is not above `bid`.

## 7. No Broker Call Boundary

This packet is local validation only. It does not authorize:

- broker network calls
- broker quote fetches
- order placement
- live endpoint use
- credential reads
- account ID reads
- Windows Vault reads
- environment variable reads
- `.env` reads
- schedulers, daemons, webhooks, or unattended trading paths

Sanitized output explicitly reports all broker, order, secret, quote-lookup, and market-data access
flags as false.

## 8. Corrected Future Packet Dependency

Any future corrected runtime packet must consume bid/ask SLTP validation evidence, not only static
reference-price evidence.

The future command package should require current bid/ask evidence immediately before command
construction and must reject stale, missing, placeholder, invalid, or side-incompatible TP/SL values.

## 9. Next Safe Packet

Next safe packet:

```text
AIOS-FOREX-OANDA-DEMO-BID-ASK-CORRECTED-RUNTIME-PACKET-V1
```

That packet should build a sanitized corrected runtime command package from current bid/ask
validation evidence only. It must not call OANDA, place an order, read credentials, read account IDs,
read Windows Vault, read environment variables, read `.env`, create automation, stage, commit, or
push unless a separate explicit approval packet authorizes those actions.
