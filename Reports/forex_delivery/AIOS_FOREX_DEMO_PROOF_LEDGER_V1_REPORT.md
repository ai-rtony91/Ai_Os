# AIOS Forex Demo Proof Ledger V1 Report

Packet: AIOS-P26D

Append-only demo proof ledger evidence. No broker, OANDA, network, credential, live, order, bank, or money path was used.

```json
{
  "appended": true,
  "bank_access_allowed": false,
  "followup_notes": [
    "F3-adjacent: wire consecutive profitable demo days into S1/S2 sweep eligibility in a later packet."
  ],
  "followups": [
    "F3-adjacent"
  ],
  "ledger_path": "telemetry/forex/demo_proof_ledger.jsonl",
  "live_capital_action_authorized": false,
  "mode": "APPLY",
  "money_movement_allowed": false,
  "new_entry": {
    "bank_access_allowed": false,
    "consecutive_profitable_days": 2,
    "cumulative_pnl_usd": 250.0,
    "date": "2026-07-01",
    "fills": 5,
    "live_capital_action_authorized": false,
    "losses": 1,
    "mode": "DEMO_ONLY",
    "money_movement_allowed": false,
    "realized_pnl_usd": 125.0,
    "recorded_at_utc": "2026-07-01T09:51:01Z",
    "schema": "aios.forex.demo_proof_ledger.v1",
    "win_rate_pct": 80.0,
    "wins": 4
  },
  "record_demo_day_requested": true,
  "schema": "aios.forex.demo_proof_ledger_receipt.v1",
  "summary": {
    "bank_access_allowed": false,
    "consecutive_profitable_days": 2,
    "cumulative_pnl_usd": 250.0,
    "demo_trading_day_count": 2,
    "ledger_line_count": 3,
    "live_capital_action_authorized": false,
    "min_consecutive_profitable_days_gate": 5,
    "min_gate_met": false,
    "money_movement_allowed": false,
    "schema": "aios.forex.demo_proof_ledger_summary.v1"
  },
  "summary_requested": false
}
```
