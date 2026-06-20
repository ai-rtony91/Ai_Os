# AIOS FOREX Order Preview Hardening (V1)

## Purpose

`automation/forex_engine/order_preview.py` is the canonical paper-only order preview gate for Trading Lab. It composes:

- candidate intake/validation
- `calculate_position_size(...)` from `automation.forex_engine.position_sizing`
- `evaluate_risk_preview(...)` from `automation.forex_engine.risk_governor`

No paper fill, queueing, submission, or execution logic is performed here.

## Paper-only boundary

- `ORDER_PREVIEW_MODE = "PAPER_ONLY"`
- Output safety metadata always:

```python
{
    "paper_only": True,
    "broker": False,
    "live_trading": False,
    "credentials": False,
    "real_orders": False,
    "network_access": False,
}
```

- No broker SDKs
- No network imports/calls
- No credentials/account-id/secret access
- No file I/O

## Required inputs

Candidate is dict-like and must satisfy:

- `paper_only` must not be `False`
- `mode` must not be `live`, `demo`, `broker`
- `pair` required
- `direction` required, `buy` or `sell`
- `entry_type` optional, defaults to `market`
- `entry_price` required positive
- `stop_loss` required positive
- `take_profit` required positive
- `risk_percent` optional (falls back to limits/default behavior)
- `spread`/`data_timestamp` carried through to risk checks

Account state is passed to sizing and risk gates (required for deterministic paper-risk checks except where explicit risk override paths allow).  

## Result shape

`build_order_preview(...)` returns:

- `allowed`
- `decision`
- `preview_id`
- `blocked_reason`
- `blocked_reasons`
- `warnings`
- `paper_only`
- `mode`
- `pair`
- `direction`
- `entry_type`
- `entry_price`
- `stop_loss`
- `take_profit`
- `units`
- `raw_units`
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
- `safety`
- `next_safe_action`
- `metadata`

## Composition behavior

- `approval_state` is `"paper_preview_ready"` only when both sizing and risk checks return `allowed`.
- Otherwise `approval_state` is `"blocked"`.
- `reward_estimate = abs(take_profit - entry_price) * units`
- `risk_reward = reward_estimate / dollar_risk` when `dollar_risk > 0`, else `0`.
- `data_freshness` is forwarded from risk governor output (typically `data_age_seconds`).

## Rejection reasons

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

## Why this does not execute trades

This module only builds/validates preview metadata and risk inputs. It does not create orders, fills, queue records, broker interactions, live execution, or portfolio mutation.

## Dashboard / orchestrator relationship

- Existing `services/orchestrator/forexPaperOrderPreview.js` is intentionally untouched in this packet.
- Downstream dashboard/orchestrator integration should consume this canonical preview payload directly.
- Dashboard must only display the preview result as truth and must not create trade truth.

## Next packet

`FOREX-PAPER-FILL-SIMULATOR`

