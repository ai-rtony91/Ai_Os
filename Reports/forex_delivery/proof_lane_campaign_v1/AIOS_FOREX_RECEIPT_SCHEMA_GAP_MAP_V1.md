# AIOS Forex Receipt Schema Gap Map V1

## 1. Status
`PARTIAL`

## 2. Existing receipt/evidence artifacts
- `Reports/forex_delivery/AIOS_LIVE_MICRO_TRADE_READINESS_GATE_V1.md`
- `Reports/forex_delivery/AIOS_LIVE_MICRO_TRADE_ONE_SHOT_PROTECTED_EXECUTION_PREFLIGHT_V1.md`
- `Reports/forex_delivery/AIOS_LIVE_MICRO_TRADE_ONE_SHOT_PROTECTED_EXECUTION_PACKET_V1_SANITIZED_EVIDENCE.md`
- `docs/forex_delivery/AIOS_PL_TRUTH_LAYER_REQUIREMENTS_V1.md`
- `docs/forex_delivery/AIOS_POST_TRADE_LEDGER_REPLAY_CLOSEOUT_V1.md`
- `scripts/forex_delivery/run_forex_supervised_demo_order_execution_v1.py`
- `automation/forex_engine/metrics.py`
- `tests/trading_lab/test_forex_paper_ledger.py`
- `tests/trading_lab/test_forex_report.py`

These artifacts prove that the repo already knows how to talk about evidence, truth layers, post-trade summaries, and sanitized live-micro boundaries. What they do not yet provide is a single canonical, non-secret receipt schema for the Proof Lane.

## 3. Missing receipt fields
The repository has scattered evidence shapes, but no single authoritative receipt envelope owns the full data set below:

| Field | Current state |
|---|---|
| `receipt_id` | Missing from a canonical proof schema |
| `run_id` | Missing from a canonical proof schema |
| `lane` | Present as a concept, not yet canonical in a receipt envelope |
| `broker` | Present only as a reporting concept, not as proof authority |
| `account_alias_non_secret` | Missing as a normalized non-secret field |
| `symbol` | Present in local trading data, not yet canonical in a receipt schema |
| `side` | Present in local trade data, not yet canonical in a receipt schema |
| `order_type` | Present in local trade data, not yet canonical in a receipt schema |
| `requested_units` | Missing from a canonical proof receipt |
| `filled_units` | Missing from a canonical proof receipt |
| `requested_price` | Missing from a canonical proof receipt |
| `fill_price` | Missing from a canonical proof receipt |
| `stop_loss` | Missing from a canonical proof receipt |
| `take_profit` | Missing from a canonical proof receipt |
| `opened_at_utc` | Missing from a canonical proof receipt |
| `closed_at_utc` | Missing from a canonical proof receipt |
| `broker_order_id_redacted` | Missing as a normalized redacted field |
| `broker_trade_id_redacted` | Missing as a normalized redacted field |
| `realized_pnl` | Present in some evidence flows, not canonical here |
| `fees` | Missing from a canonical proof receipt |
| `spread_observed` | Missing from a canonical proof receipt |
| `slippage_observed` | Missing from a canonical proof receipt |
| `status` | Present in many reports, not yet normalized for proof receipts |
| `raw_receipt_hash` | Missing from a canonical proof receipt |
| `redaction_status` | Missing from a canonical proof receipt |
| `owner_approval_id` | Missing from a canonical proof receipt |
| `validator_status` | Missing from a canonical proof receipt |

## 4. Proposed non-secret receipt envelope
The next schema should treat the following as the required non-secret envelope:

| Field | Handling |
|---|---|
| `receipt_id` | Stable unique receipt key |
| `run_id` | Run correlation key |
| `lane` | Proof-lane name |
| `broker` | Broker label or demo label only |
| `account_alias_non_secret` | Sanitized alias, never raw account ID |
| `symbol` | Instrument symbol |
| `side` | Buy or sell |
| `order_type` | Market, limit, or stop style label |
| `requested_units` | Requested size |
| `filled_units` | Filled size |
| `requested_price` | Requested price |
| `fill_price` | Fill price |
| `stop_loss` | Stop loss value |
| `take_profit` | Take profit value |
| `opened_at_utc` | Open timestamp |
| `closed_at_utc` | Close timestamp |
| `broker_order_id_redacted` | Redacted broker order reference |
| `broker_trade_id_redacted` | Redacted broker trade reference |
| `realized_pnl` | Realized profit/loss |
| `fees` | Fee total |
| `spread_observed` | Observed spread |
| `slippage_observed` | Observed slippage |
| `status` | Final state label |
| `raw_receipt_hash` | Integrity anchor for the raw source |
| `redaction_status` | Indicates sanitized or unsanitized state |
| `owner_approval_id` | Links to the approval record |
| `validator_status` | Links to local validation outcome |

## 5. Broker proof boundary
- Broker proof must remain separate from paper proof.
- Paper receipts can demonstrate deterministic behavior, but they cannot be promoted to broker truth.
- Any broker proof must be sanitized and hashed before it enters repo evidence.
- No broker proof may expose raw identifiers, raw payloads, or secret-bearing fields.

## 6. Demo proof receipt requirements
- Demo receipts must still use the same non-secret envelope.
- Demo receipts must show the demo label, the sanitized account alias, the order intent, the fill result, and the validator state.
- Demo receipts must not rely on private account IDs or raw broker payloads.
- Demo receipts must be explicitly marked as demo proof, not live proof.

## 7. Live proof receipt requirements
- Live proof receipts require the same fields as demo proof, plus stricter redaction discipline.
- Live proof receipts must never store raw account IDs, raw order IDs, raw trade IDs, raw payloads, or credentials.
- Live proof receipts must carry owner approval and validator status so the proof can be audited without exposing live secrets.
- Live proof is not authorized in this campaign.

## 8. Redaction requirements
- Redact account identifiers, tokens, order IDs, trade IDs, endpoints, and raw payloads.
- Keep only non-secret aliases and hashed integrity anchors.
- Ensure the receipt can be audited without reconstructing the live broker message.
- Preserve enough structure for validation, not enough detail to reveal private state.

## 9. No-secret rule
- No receipt in this lane may contain `.env` values, credential strings, private account identifiers, raw broker payloads, or live endpoint addresses.
- If a field cannot be represented safely, the field must be redacted or omitted and the omission must be recorded.
- Sanitized evidence is required by default.

## 10. Next safe implementation packet
- `AIOS_FOREX_PROOF_LANE_RECEIPT_SCHEMA_DRY_RUN_VALIDATOR_V1`
