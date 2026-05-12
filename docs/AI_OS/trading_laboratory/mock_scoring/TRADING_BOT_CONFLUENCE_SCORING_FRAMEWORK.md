# Trading Bot Confluence Scoring Framework

Mock-only. No broker. No OANDA. No API keys. No real orders. No live market data.

## Scoring Model

- Trend alignment: 0-25
- Momentum: 0-20
- Structure/location: 0-20
- Volatility: 0-15
- Risk quality: 0-20

Total: 0-100

## Thresholds

- 70+ = pass mock review
- 55-69 = review only
- <55 = reject

Mock review does not approve broker execution or real orders.

## Confidence Tiers

- very_low
- low
- review_only
- mock_candidate
- strong_mock_candidate

## Rejection Rules

- Risk quality below threshold.
- Trend alignment below threshold.
- Volatility UNKNOWN/unsafe.
- Regime not approved.
- Missing evidence.
- Blocked actions detected.

Blocked actions:
- Broker connection.
- OANDA connection.
- API keys.
- Real orders.
- Live market data.

## Next Safe Action

Score one mock signal, keep execution blocked, then run regime and risk gates.

