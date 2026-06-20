# AIOS FOREX Position Sizing V1 Report

## Packet

- Packet ID: `FOREX-POSITION-SIZING-V1`
- Branch: `feature/forex-position-sizing-v1`

## Files inspected

- `automation/forex_engine/risk.py`
- `automation/forex_engine/risk_governor.py`
- `automation/forex_engine/paper_trade_lifecycle.py`
- `automation/forex_engine/paper_execution.py`
- `apps/trading_lab/trading_lab/forex_portfolio_state.py`
- `docs/orchestration/AIOS_FOREX_RISK_GOVERNOR.md`
- `docs/orchestration/AIOS_FOREX_PAPER_TRADE_MODEL.md`
- `docs/orchestration/AIOS_FOREX_PORTFOLIO_STATE.md`

## Files changed

- `automation/forex_engine/position_sizing.py`
- `tests/forex_engine/test_position_sizing.py`
- `docs/orchestration/AIOS_FOREX_POSITION_SIZING.md`
- `Reports/forex_delivery/AIOS_FOREX_POSITION_SIZING_V1_REPORT.md`

## Sizing formula

1. `stop_distance = abs(entry_price - stop_loss)`
2. `risk_dollars = explicit risk_dollars or (risk_base * risk_percent / 100)`
3. `raw_units = risk_dollars / (stop_distance * pip_value_per_unit)`
4. `units = rounded(raw_units, rounding_increment, allow_fractional_units policy)`
5. `estimated_loss_at_stop = units * stop_distance * pip_value_per_unit`

## Caps added

- `max_risk_percent`
- `max_risk_dollars`
- `min_units`
- `max_units`
- `rounding_increment`
- `allow_fractional_units`
- `supported_pairs`

## Rejection reasons added

- `invalid_preview`
- `non_paper_mode`
- `invalid_account_state`
- `invalid_balance`
- `missing_balance`
- `invalid_entry_price`
- `missing_entry_price`
- `invalid_stop_loss`
- `missing_stop_loss`
- `invalid_stop_distance`
- `invalid_risk_percent`
- `invalid_risk_dollars`
- `risk_exceeds_cap`
- `min_units_not_met`
- `max_units_exceeded`
- `insufficient_balance`
- `unsupported_pair`
- `invalid_pip_value`
- `invalid_rounding`

## Tests added

- `tests/forex_engine/test_position_sizing.py` with coverage for
  importability, defaults, valid sizing, balance preference, explicit risk override, stop-loss checks,
  balance/account checks, cap/rule checks, pair and pip checks, rounding behavior,
  paper-mode guards, determinism, safety boundary, and source-safety scan.

## Safety boundary

- Paper-only: `paper_only` output always `True`.
- No broker, live trading, credentials, real orders, or network behavior.

## Validators

- Not run by Codex in this task.

## Next human commands

- Run the test module (manual/CI): `python -m pytest tests/forex_engine/test_position_sizing.py`
- Review packet handoff from sizing to order preview hardening.

## Next safe action

- Proceed to `FOREX-ORDER-PREVIEW-HARDENING`.

