PACKET: FOREX-RISK-GOVERNOR-V1
BRANCH: feature/forex-risk-governor-v1
FILES INSPECTED: automation/forex_engine/risk.py, automation/forex_engine/models.py, automation/forex_engine/paper_trade_lifecycle.py, automation/forex_engine/paper_execution.py, apps/trading_lab/trading_lab/forex_portfolio_state.py, docs/orchestration/AIOS_FOREX_PAPER_TRADE_MODEL.md, docs/orchestration/AIOS_FOREX_PORTFOLIO_STATE.md
FILES CHANGED: automation/forex_engine/risk_governor.py, tests/forex_engine/test_risk_governor.py, docs/orchestration/AIOS_FOREX_RISK_GOVERNOR.md, Reports/forex_delivery/AIOS_FOREX_RISK_GOVERNOR_V1_REPORT.md
GOVERNOR ADDED: Added canonical paper-only risk gate and structured preview decision function in `automation/forex_engine/risk_governor.py`.
RISK GATES ADDED: `evaluate_risk_preview(...)` with deterministic checks for mode/paper-only, stop/take requirements, stop distance, unit/risk validity, per-trade cap, daily cap, open risk cap, open trade cap, pair exposure cap, spread cap, stale data, cooldown-after-loss, duplicate setup, and kill switch.
REJECTION REASONS: invalid_preview, invalid_account_state, non_paper_mode, live_trading_blocked, missing_stop_loss, missing_take_profit, invalid_stop_distance, invalid_units, invalid_risk_amount, excessive_risk_per_trade, max_daily_loss_hit, max_open_risk_hit, max_open_trades_hit, max_pair_exposure_hit, spread_too_high, stale_market_data, cooldown_after_loss, duplicate_setup, kill_switch_active
TESTS ADDED: tests/forex_engine/test_risk_governor.py
REPORT CREATED OR SKIPPED: REPORT CREATED
WHAT WAS NOT TOUCHED: risk.py, models.py, paper_trade_lifecycle.py, paper_execution.py, dashboard/orchestrator directories, governance files, and non-allowed scope files.
VALIDATORS RUN: NOT RUN BY CODEX
PROTECTED ACTIONS: BROKER/LIVE/SECRET: none executed in this module, no commit/push/stage, no network/broker code.
BROKER/LIVE/SECRET RISK: safety boundary is enforced in every decision result (`paper_only`, no broker, no live/trading, no credentials, no real_orders, no network_access). No file writes, no credentials, no network imports/calls.
NEXT HUMAN COMMANDS: Run targeted test file execution and, if clean, wire `evaluate_risk_preview` as mandatory guard before paper fill/multi-trade submission.
NEXT SAFE ACTION: Proceed to `FOREX-POSITION-SIZING` or `FOREX-ORDER-PREVIEW-HARDENING` based on repo risk-state.
STATUS: COMPLETE
