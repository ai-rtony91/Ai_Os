# AIOS FOREX Order Preview Hardening V1 Report

## Packet

- Packet ID: `FOREX-ORDER-PREVIEW-HARDENING-V1`
- Branch: `feature/forex-order-preview-hardening-v1`

## Files inspected

- `automation/forex_engine/risk_governor.py`
- `automation/forex_engine/position_sizing.py`
- `automation/forex_engine/paper_trade_lifecycle.py`
- `apps/trading_lab/trading_lab/forex_portfolio_state.py`
- `services/orchestrator/forexPaperOrderPreview.js`
- `docs/orchestration/AIOS_FOREX_RISK_GOVERNOR.md`
- `docs/orchestration/AIOS_FOREX_POSITION_SIZING.md`
- `docs/orchestration/AIOS_FOREX_PAPER_TRADE_MODEL.md`
- `docs/orchestration/AIOS_FOREX_PORTFOLIO_STATE.md`

## Files changed

- `automation/forex_engine/order_preview.py`
- `tests/forex_engine/test_order_preview.py`
- `docs/orchestration/AIOS_FOREX_ORDER_PREVIEW_HARDENING.md`
- `Reports/forex_delivery/AIOS_FOREX_ORDER_PREVIEW_HARDENING_V1_REPORT.md`

## Preview fields added

- `preview_id`
- `dollar_risk`
- `percent_risk`
- `reward_estimate`
- `risk_reward`
- `spread`
- `data_freshness`
- `sizing_result`
- `risk_governor_result`
- `approval_state`
- `evidence_path`

## Sizing integration

- Composes candidate through `calculate_position_size(...)` in `automation.forex_engine.position_sizing`.
- Propagates `units` and `raw_units` from sizing result.
- Uses sizing limits and pair config through `limits` passthrough fields.

## Risk governor integration

- Composes preview through `evaluate_risk_preview(...)` in `automation.forex_engine.risk_governor`.
- Propagates spread and `data_timestamp`.
- Uses `data_age_seconds` as `data_freshness`.

## Rejection reasons added

- `invalid_candidate`
- `invalid_account_state`
- `non_paper_mode`
- `live_trading_blocked`
- `missing_pair`
- `missing_direction`
- `missing_entry_price`
- `missing_stop_loss`
- `missing_take_profit`
- `missing_account_state`
- `sizing_blocked`
- `risk_blocked`
- `missing_sizing_result`
- `missing_risk_result`
- `invalid_preview`
- `evidence_path_invalid`

## Tests added

- `tests/forex_engine/test_order_preview.py` with coverage for imports, positive preview path, result shape, safety metadata, candidate mode/paper guards, required fields, sizing/risk blocking propagation, approval-state gating, deterministic `preview_id`, spread/freshness propagation, evidence_path validation, and source-safety scan.

## Safety boundary

- Paper-only output safety is always returned.
- No broker/live/credential/network behavior in module or tests.

## Validators

- Not run by Codex per task instruction.

## Next human commands

- Run tests for order preview:
  - `python -m pytest tests/forex_engine/test_order_preview.py`
- Proceed to `FOREX-PAPER-FILL-SIMULATOR` implementation when happy with deterministic gate behavior.

## Next safe action

- Wire canonical preview payload consumption in orchestrator/dashboard without creating dashboard truth.

