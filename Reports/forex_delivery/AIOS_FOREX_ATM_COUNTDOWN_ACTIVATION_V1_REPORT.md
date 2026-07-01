# AIOS Forex ATM Countdown Activation V1 Report

Packet: AIOS-P26A

The ATM milestone countdown is activated from owner baseline equity. This report is evidence only; it moves no money and authorizes no broker, bank, live, or order path.

```json
{
  "bank_access_allowed": false,
  "baseline_equity_usd": 1000.0,
  "contract_active_literal": "COUNTDOWN_ACTIVE",
  "countdown_off_baseline_required": true,
  "countdown_status_after": "COUNTDOWN_ACTIVE",
  "countdown_status_before": "BASELINE_EQUITY_REQUIRED",
  "explanation": "Band-floor 100 percent means 1x return achieved; owner 101 percent sits in-band.",
  "flow1_active_literal_observed": "COUNTDOWN_ACTIVE",
  "followup_notes": [],
  "followups": [],
  "generated_at": "2026-07-01T09:50:36Z",
  "live_capital_action_authorized": false,
  "min_profit_to_sweep_usd": 200.0,
  "mode": "APPLY",
  "money_movement_allowed": false,
  "schema": "aios.forex.atm_countdown_activation.v1",
  "status": "COUNTDOWN_ACTIVATED",
  "target_profit_usd": 1000.0,
  "target_return_band": "100_TO_120_PERCENT",
  "target_return_band_high_pct": 120.0,
  "target_return_band_low_pct": 100.0,
  "written": false
}
```
