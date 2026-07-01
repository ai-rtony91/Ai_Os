# AIOS Forex Brake Trip Proof V1 Report

Append-only simulated brake-trip proof only. No broker, live order, credential, network, or money path was used.

## Safety controls

- kill_switch_state: ARMED
- daily_loss_warning_usd: 15.0
- daily_loss_stop_usd: 30.0
- max_total_loss_usd: 150.0

## Trip summary

- T1 kill switch: PASS
- T2 daily stop: PASS
- T3 max loss: PASS
- ledger entries written: 3
- ledger label: SIMULATED_TRIP_PROOF

## Receipt

```json
{
  "account_identifier_persistence_allowed": false,
  "all_trips_passed": true,
  "appended_entry_count": 3,
  "broker_api_allowed": false,
  "credential_access_allowed": false,
  "ledger_entry_count_after": 3,
  "ledger_entry_count_before": 0,
  "ledger_path": "telemetry/forex/brake_trip_proof_ledger.jsonl",
  "live_trading_allowed": false,
  "mode": "APPLY",
  "money_movement_allowed": false,
  "next_safe_action": "Keep this proof simulated; owner approval is required before any later real demo loop.",
  "order_execution_allowed": false,
  "owner_reset_required": true,
  "repo_root": "C:\\Dev\\Ai.Os",
  "report_path": "Reports/forex_delivery/AIOS_FOREX_BRAKE_TRIP_PROOF_V1_REPORT.md",
  "safety_config_source": "control/forex/forex_safety_controls_config.json",
  "safety_controls": {
    "bank_access_allowed": false,
    "daily_loss_stop_usd": 30.0,
    "daily_loss_warning_usd": 15.0,
    "kill_switch_mechanism": "STOP_FLAG_FILE_HONORED_BY_STOP_PAUSE_RESUME_ENGINE",
    "kill_switch_state": "ARMED",
    "live_capital_action_authorized": false,
    "max_total_loss_usd": 150.0,
    "mode": "DEMO_ONLY",
    "money_movement_allowed": false,
    "schema": "aios.forex.safety_controls_snapshot.v1"
  },
  "schema": "aios.forex.brake_trip_proof.v1",
  "simulated_trip_proof_label": "SIMULATED_TRIP_PROOF",
  "trip_results": [
    {
      "config_snapshot": {
        "kill_switch_mechanism": "STOP_FLAG_FILE_HONORED_BY_STOP_PAUSE_RESUME_ENGINE",
        "kill_switch_state": "ARMED"
      },
      "control_actions": [
        "STOP"
      ],
      "expected_status": "STOP_REQUIRED",
      "further_simulated_trades_allowed": false,
      "halt_requested": true,
      "kill_switch_mechanism": "STOP_FLAG_FILE_HONORED_BY_STOP_PAUSE_RESUME_ENGINE",
      "kill_switch_state": "ARMED",
      "ledger_label": "SIMULATED_TRIP_PROOF",
      "next_safe_action": "Stop the chain and resolve blockers before any resume review.",
      "no_further_simulated_trades_occurred": true,
      "recorded_at_utc": "2026-07-01T22:48:54Z",
      "schema": "aios.forex.brake_trip_proof_trip.v1",
      "simulated_cycle_state_after": "STOPPED",
      "simulated_cycle_state_before": "RUNNING_DEMO",
      "stop_pause_resume_blockers": [
        "operator halt is active"
      ],
      "stop_pause_resume_control_state": "STOP",
      "stop_pause_resume_status": "STOP_REQUIRED",
      "trip_id": "T1",
      "trip_name": "kill_switch_stop_flag",
      "trip_passed": true
    },
    {
      "blocked_candidates_after_halt": [
        {
          "blocked_reason": "HALT_FOR_DAY",
          "realized_loss_usd": 7.0,
          "trade_index": 6
        }
      ],
      "blocked_trade_count_after_halt": 1,
      "config_snapshot": {
        "daily_loss_stop_usd": 30.0,
        "daily_loss_warning_usd": 15.0
      },
      "control_actions": [
        "WARNING_INTENT",
        "HALT_FOR_DAY"
      ],
      "executed_trade_count": 5,
      "executed_trades": [
        {
          "cumulative_daily_loss_usd": 6.0,
          "realized_loss_usd": 6.0,
          "trade_index": 1
        },
        {
          "cumulative_daily_loss_usd": 11.0,
          "realized_loss_usd": 5.0,
          "trade_index": 2
        },
        {
          "cumulative_daily_loss_usd": 15.0,
          "realized_loss_usd": 4.0,
          "trade_index": 3
        },
        {
          "cumulative_daily_loss_usd": 23.0,
          "realized_loss_usd": 8.0,
          "trade_index": 4
        },
        {
          "cumulative_daily_loss_usd": 31.0,
          "realized_loss_usd": 8.0,
          "trade_index": 5
        }
      ],
      "halt_action": "HALT_FOR_DAY",
      "halt_threshold_usd": 30.0,
      "halt_trade_index": 5,
      "halt_triggered_at_loss_usd": 31.0,
      "ledger_label": "SIMULATED_TRIP_PROOF",
      "next_safe_action": "Stop additional simulated trades for the day after the warning and halt thresholds trip.",
      "no_further_simulated_trades_occurred": true,
      "recorded_at_utc": "2026-07-01T22:48:54Z",
      "schema": "aios.forex.brake_trip_proof_trip.v1",
      "trip_id": "T2",
      "trip_name": "daily_stop_trip",
      "trip_passed": true,
      "warning_intent_emitted": true,
      "warning_threshold_usd": 15.0,
      "warning_triggered_at_loss_usd": 15.0
    },
    {
      "blocked_candidates_after_halt": [
        {
          "blocked_reason": "HALT_ALL",
          "realized_loss_usd": 12.0,
          "trade_index": 4
        }
      ],
      "blocked_trade_count_after_halt": 1,
      "config_snapshot": {
        "max_total_loss_usd": 150.0
      },
      "control_actions": [
        "HALT_ALL",
        "OWNER_RESET_REQUIRED"
      ],
      "executed_trade_count": 3,
      "executed_trades": [
        {
          "cumulative_loss_usd": 40.0,
          "realized_loss_usd": 40.0,
          "trade_index": 1
        },
        {
          "cumulative_loss_usd": 90.0,
          "realized_loss_usd": 50.0,
          "trade_index": 2
        },
        {
          "cumulative_loss_usd": 151.0,
          "realized_loss_usd": 61.0,
          "trade_index": 3
        }
      ],
      "halt_action": "HALT_ALL",
      "halt_trade_index": 3,
      "halt_triggered_at_cumulative_loss_usd": 151.0,
      "ledger_label": "SIMULATED_TRIP_PROOF",
      "max_total_loss_usd": 150.0,
      "next_safe_action": "Stop all simulated trading and require owner reset after the cumulative loss threshold trips.",
      "no_further_simulated_trades_occurred": true,
      "owner_reset_required": true,
      "recorded_at_utc": "2026-07-01T22:48:54Z",
      "schema": "aios.forex.brake_trip_proof_trip.v1",
      "trip_id": "T3",
      "trip_name": "max_loss_trip",
      "trip_passed": true
    }
  ]
}
```
