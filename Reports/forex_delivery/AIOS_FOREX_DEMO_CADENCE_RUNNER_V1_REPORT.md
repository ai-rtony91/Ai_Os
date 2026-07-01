# AIOS Forex Demo Cadence Runner V1 Report

Packet: AIOS-P26C

Demo/mock cadence receipt only. No scheduler, daemon, broker, OANDA, network, credential, live, order, or money path was used.

```json
{
  "bank_access_allowed": false,
  "broker_used": false,
  "bucket_feed_receipt": {
    "cumulative_bucket_feed_usd": 119.5,
    "s2_mutated": false,
    "would_consume_keys": [
      "profit_bucket",
      "min_profit_to_sweep",
      "realized_profit_month"
    ]
  },
  "cycles_requested": 3,
  "daemon_started": false,
  "followup_notes": [
    "F3: wire S2 to consume the emitted bucket-feed in a later packet that owns S2."
  ],
  "followups": [
    "F3"
  ],
  "live_capital_action_authorized": false,
  "mode": "APPLY",
  "money_movement_allowed": false,
  "network_used": false,
  "oanda_used": false,
  "runtime_objective": "22_HOURS_PER_DAY_6_DAYS_PER_WEEK",
  "runtime_objective_aligned": true,
  "runtime_objective_observed": "22_HOURS_PER_DAY_6_DAYS_PER_WEEK",
  "scheduler_registered": false,
  "schema": "aios.forex.demo_cadence_runner.v1",
  "windows": [
    {
      "bucket_feed_usd": 34.25,
      "close_at_utc": "2026-07-02T07:51:01Z",
      "cumulative_bucket_feed_usd": 34.25,
      "cycle": 1,
      "fill_count": 2,
      "mock_fills": [
        {
          "fill_id": "MOCK-FILL-001",
          "outcome": "WIN",
          "realized_demo_pnl": 42.5,
          "symbol": "EUR_USD"
        },
        {
          "fill_id": "MOCK-FILL-002",
          "outcome": "LOSS",
          "realized_demo_pnl": -8.25,
          "symbol": "GBP_USD"
        }
      ],
      "open_at_utc": "2026-07-01T09:51:01Z",
      "realized_demo_pnl": 34.25,
      "rest_until_utc": "2026-07-02T09:51:01Z",
      "trading_day_index": 1,
      "window_status": "DEMO_WINDOW_CLOSED"
    },
    {
      "bucket_feed_usd": 29.5,
      "close_at_utc": "2026-07-03T07:51:01Z",
      "cumulative_bucket_feed_usd": 63.75,
      "cycle": 2,
      "fill_count": 2,
      "mock_fills": [
        {
          "fill_id": "MOCK-FILL-002",
          "outcome": "LOSS",
          "realized_demo_pnl": -8.25,
          "symbol": "GBP_USD"
        },
        {
          "fill_id": "MOCK-FILL-003",
          "outcome": "WIN",
          "realized_demo_pnl": 37.75,
          "symbol": "USD_JPY"
        }
      ],
      "open_at_utc": "2026-07-02T09:51:01Z",
      "realized_demo_pnl": 29.5,
      "rest_until_utc": "2026-07-03T09:51:01Z",
      "trading_day_index": 2,
      "window_status": "DEMO_WINDOW_CLOSED"
    },
    {
      "bucket_feed_usd": 55.75,
      "close_at_utc": "2026-07-04T07:51:01Z",
      "cumulative_bucket_feed_usd": 119.5,
      "cycle": 3,
      "fill_count": 2,
      "mock_fills": [
        {
          "fill_id": "MOCK-FILL-003",
          "outcome": "WIN",
          "realized_demo_pnl": 37.75,
          "symbol": "USD_JPY"
        },
        {
          "fill_id": "MOCK-FILL-004",
          "outcome": "WIN",
          "realized_demo_pnl": 18.0,
          "symbol": "AUD_USD"
        }
      ],
      "open_at_utc": "2026-07-03T09:51:01Z",
      "realized_demo_pnl": 55.75,
      "rest_until_utc": "2026-07-04T09:51:01Z",
      "trading_day_index": 3,
      "window_status": "DEMO_WINDOW_CLOSED"
    }
  ],
  "written": false
}
```
