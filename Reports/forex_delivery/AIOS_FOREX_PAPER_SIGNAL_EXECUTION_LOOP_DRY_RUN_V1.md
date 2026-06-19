# AIOS Forex Paper Signal Execution Loop Dry Run V1

Status: PAPER_SIMULATION_SANITIZED

This evidence is paper-only. It records no live trade, live order, broker write call, secret value, account identifier, real order identifier, transaction identifier, or raw broker payload.

## Summary

```json
{
  "confidence": 0.62,
  "evidence_path": "Reports/forex_delivery/AIOS_FOREX_PAPER_SIGNAL_EXECUTION_LOOP_DRY_RUN_V1.md",
  "live_execution_allowed": false,
  "next_safe_action": "Review paper loop evidence for risk-adjusted expectancy; live execution remains blocked until AIOS-FOREX-LIVE-MICRO-TRADE-ARMING-GATE-V1.",
  "paper_close_reconcile": true,
  "paper_entry_created": true,
  "realized_paper_pl": 1.2,
  "risk_approval": true,
  "selected_pair": "EUR_USD",
  "signal_side": "BUY",
  "strategy_name": "paper_fixture_expectancy_probe_v1",
  "trading_history_row_written": true
}
```

## Sanitized Aggregate Result

```json
{
  "auto_exit_readiness": "PAPER_READY",
  "broker_write_calls_allowed": false,
  "close_trade_allowed": false,
  "confidence": 0.62,
  "dashboard_status": {
    "PAPER_LOOP_AVAILABLE": true,
    "history_writeback_status": "PAPER_HISTORY_WRITTEN",
    "last_paper_realized_pl": 1.2,
    "last_paper_signal": "BUY",
    "last_paper_trade_status": "PAPER_CLOSED_RECONCILED",
    "live_execution_allowed": false,
    "next_safe_action": "Review paper loop evidence for risk-adjusted expectancy; live execution remains blocked until AIOS-FOREX-LIVE-MICRO-TRADE-ARMING-GATE-V1."
  },
  "evidence_path": "Reports/forex_delivery/AIOS_FOREX_PAPER_SIGNAL_EXECUTION_LOOP_DRY_RUN_V1.md",
  "exit_plan": {
    "auto_exit_readiness": "PAPER_READY",
    "block_reason": "NONE",
    "block_reason_list": [],
    "close_trade_allowed": false,
    "exit_plan_ready": true,
    "exit_plan_status": "READY",
    "live_execution_allowed": false,
    "manual_close_fallback": "PAPER_RECONCILER_ONLY_NO_LIVE_CLOSE",
    "max_time_policy": {
      "duration": "PT30M",
      "status": "REQUIRED_PRESENT"
    },
    "mode": "PAPER_ONLY",
    "stop_loss_policy": {
      "price": 1.0988,
      "status": "REQUIRED_PRESENT"
    },
    "stop_loss_required_before_or_with_entry": true,
    "take_profit_policy": {
      "policy": "paper_two_r_fixture_target",
      "price": 1.1024,
      "status": "REQUIRED_PRESENT"
    },
    "trailing_stop_policy": {
      "policy": "paper_fixture_trailing_review_only",
      "status": "OPTIONAL_PRESENT"
    }
  },
  "exit_plan_status": "READY",
  "exit_reason": "PAPER_MAX_TIME_FIXTURE_RECONCILE",
  "live_execution_allowed": false,
  "manual_close_fallback": "PAPER_RECONCILER_ONLY_NO_LIVE_CLOSE",
  "max_time_policy": {
    "duration": "PT30M",
    "status": "REQUIRED_PRESENT"
  },
  "mode": "PAPER_SIMULATION",
  "next_safe_action": "Review paper loop evidence for risk-adjusted expectancy; live execution remains blocked until AIOS-FOREX-LIVE-MICRO-TRADE-ARMING-GATE-V1.",
  "order_placement_allowed": false,
  "paper_close_reconcile": true,
  "paper_entry_created": true,
  "paper_entry_price": 1.1,
  "paper_execution": {
    "block_reason": "NONE",
    "block_reason_list": [],
    "broker_write_calls_allowed": false,
    "entry_price": 1.1,
    "entry_time": "2026-06-19T12:00:00Z",
    "exit_plan_status": "READY",
    "live_execution_allowed": false,
    "mode": "PAPER_SIMULATION",
    "order_placement_allowed": false,
    "pair": "EUR_USD",
    "paper_entry_created": true,
    "paper_execution_id": "PAPER_SIM_EUR_USD_20260619T120000Z",
    "paper_trade_status": "PAPER_OPEN_SIMULATED",
    "risk_approved": true,
    "side": "BUY",
    "source_label": "PAPER_SIMULATION_FIXTURE",
    "strategy": "paper_fixture_expectancy_probe_v1",
    "units": 1000
  },
  "paper_units": 1000,
  "private_identifiers_recorded": false,
  "raw_broker_payload_recorded": false,
  "realized_paper_pl": 1.2,
  "reconciliation": {
    "block_reason": "NONE",
    "broker_write_calls_allowed": false,
    "close_trade_allowed": false,
    "exit_price": 1.1012,
    "exit_reason": "PAPER_MAX_TIME_FIXTURE_RECONCILE",
    "live_execution_allowed": false,
    "mode": "PAPER_SIMULATION",
    "paper_close_reconcile": true,
    "paper_trade_status": "PAPER_CLOSED_RECONCILED",
    "realized_paper_pl": 1.2,
    "trading_history_row": {
      "duration": "PT30M",
      "entry_price": 1.1,
      "entry_time": "2026-06-19T12:00:00Z",
      "evidence_status": "PAPER_HISTORY_ROW_READY",
      "exit_price": 1.1012,
      "exit_reason": "PAPER_MAX_TIME_FIXTURE_RECONCILE",
      "exit_time": "2026-06-19T12:30:00Z",
      "freshness_utc": "2026-06-19T12:30:00Z",
      "max_time_policy": {
        "duration": "PT30M",
        "status": "REQUIRED_PRESENT"
      },
      "pair": "EUR_USD",
      "private_identifiers_recorded": false,
      "raw_broker_payload_recorded": false,
      "realized_paper_pl": 1.2,
      "risk_approved": true,
      "secret_values_recorded": false,
      "side": "BUY",
      "slippage_if_available": "PAPER_FIXTURE_0.1_PIPS",
      "source_label": "PAPER_SIMULATION_FIXTURE",
      "stop_loss_policy": {
        "price": 1.0988,
        "status": "REQUIRED_PRESENT"
      },
      "strategy": "paper_fixture_expectancy_probe_v1",
      "take_profit_policy": {
        "policy": "paper_two_r_fixture_target",
        "price": 1.1024,
        "status": "REQUIRED_PRESENT"
      },
      "trailing_stop_policy": {
        "policy": "paper_fixture_trailing_review_only",
        "status": "OPTIONAL_PRESENT"
      },
      "units": 1000
    }
  },
  "risk": {
    "block_reason": "NONE",
    "block_reason_list": [],
    "broker_write_calls_allowed": false,
    "daily_paper_loss_cap": 50.0,
    "daily_paper_pl": 0.0,
    "estimated_paper_trade_risk": 1.2,
    "kill_switch_enabled": true,
    "kill_switch_required": true,
    "live_execution_allowed": false,
    "max_paper_trade_risk": 25.0,
    "max_paper_units": 1000,
    "mode": "PAPER_ONLY",
    "no_duplicate_entry_rule": true,
    "no_revenge_loop_rule": true,
    "one_position_rule": true,
    "paper_entry_signature": "EUR_USD|BUY|paper_fixture_expectancy_probe_v1",
    "paper_risk_approved": true,
    "requested_units": 1000,
    "risk_approval": true
  },
  "risk_approval": true,
  "schema": "AIOS_FOREX_PAPER_SIGNAL_EXECUTION_LOOP.v1",
  "secret_values_printed": false,
  "selected_pair": "EUR_USD",
  "signal": {
    "backtest_paper_evidence_required": true,
    "block_reason": "PAPER_SIGNAL_ONLY; live execution remains blocked.",
    "confidence": 0.62,
    "entry_price": 1.1,
    "expected_edge_evidence_path": "Reports/forex_delivery/AIOS_FOREX_PAPER_SIGNAL_EXECUTION_LOOP_DRY_RUN_V1.md",
    "fixture_exit_price": 1.1012,
    "freshness_utc": "2026-06-19T12:00:00Z",
    "label": "PAPER_SIGNAL_ONLY",
    "live_execution_allowed": false,
    "live_trading_allowed_from_this_data": false,
    "read_only": true,
    "selected_pair": "EUR_USD",
    "signal_reason": "Deterministic fixture signal for paper loop validation only; not a claim of profitable live expectancy.",
    "signal_side": "BUY",
    "source_label": "PAPER_SIMULATION_FIXTURE",
    "source_type": "paper",
    "spread_slippage_status": "PAPER_VALID spread=1.2p slippage=0.1p",
    "stale_status": "VALID",
    "strategy_name": "paper_fixture_expectancy_probe_v1"
  },
  "signal_reason": "Deterministic fixture signal for paper loop validation only; not a claim of profitable live expectancy.",
  "signal_side": "BUY",
  "spread_slippage_status": "PAPER_VALID spread=1.2p slippage=0.1p",
  "stop_loss_policy": {
    "price": 1.0988,
    "status": "REQUIRED_PRESENT"
  },
  "strategy_name": "paper_fixture_expectancy_probe_v1",
  "take_profit_policy": {
    "policy": "paper_two_r_fixture_target",
    "price": 1.1024,
    "status": "REQUIRED_PRESENT"
  },
  "trading_history": {
    "block_reason": "NONE",
    "evidence_path": "Reports/forex_delivery/AIOS_FOREX_PAPER_SIGNAL_EXECUTION_LOOP_DRY_RUN_V1.md",
    "history_rows": [
      {
        "duration": "PT30M",
        "entry_price": 1.1,
        "entry_time": "2026-06-19T12:00:00Z",
        "evidence_status": "PAPER_HISTORY_ROW_READY",
        "exit_price": 1.1012,
        "exit_reason": "PAPER_MAX_TIME_FIXTURE_RECONCILE",
        "exit_time": "2026-06-19T12:30:00Z",
        "freshness_utc": "2026-06-19T12:30:00Z",
        "max_time_policy": {
          "duration": "PT30M",
          "status": "REQUIRED_PRESENT"
        },
        "pair": "EUR_USD",
        "private_identifiers_recorded": false,
        "raw_broker_payload_recorded": false,
        "realized_paper_pl": 1.2,
        "risk_approved": true,
        "secret_values_recorded": false,
        "side": "BUY",
        "slippage_if_available": "PAPER_FIXTURE_0.1_PIPS",
        "source_label": "PAPER_SIMULATION_FIXTURE",
        "stop_loss_policy": {
          "price": 1.0988,
          "status": "REQUIRED_PRESENT"
        },
        "strategy": "paper_fixture_expectancy_probe_v1",
        "take_profit_policy": {
          "policy": "paper_two_r_fixture_target",
          "price": 1.1024,
          "status": "REQUIRED_PRESENT"
        },
        "trailing_stop_policy": {
          "policy": "paper_fixture_trailing_review_only",
          "status": "OPTIONAL_PRESENT"
        },
        "units": 1000
      }
    ],
    "live_execution_allowed": false,
    "mode": "PAPER_ONLY",
    "trading_history_row_written": true
  },
  "trading_history_row_written": true,
  "trailing_stop_policy": {
    "policy": "paper_fixture_trailing_review_only",
    "status": "OPTIONAL_PRESENT"
  }
}
```
