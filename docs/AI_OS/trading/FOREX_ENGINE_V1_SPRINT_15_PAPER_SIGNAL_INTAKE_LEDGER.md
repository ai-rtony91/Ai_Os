# Forex Engine v1 Sprint 15 - Paper Signal Intake Ledger

## What This Paper Ledger Proves

Sprint 15 adds a deterministic local ledger step after mock signal intake. It shows that a local or mock signal can be evaluated through the existing paper readiness gate and converted into a safe, review-oriented record.

The intake record contains:

- `schema`
- `mode` (always `PAPER_ONLY`)
- `ledger_record_id`
- `signal_id`
- `generated_at_utc`
- `signal_summary`
- `readiness_status`
- `accepted_for_paper`
- `execution_allowed` (always `false`)
- `blocked_actions`
- `reason` and `reasons`
- `risk_flags`
- `safety`
- `next_safe_action`

### Reused components

- `automation.forex_engine.readiness.evaluate_paper_readiness`
- existing `ForexEngineConfig`, `Direction`, and `ForexSignal`
- existing `Direction`, `validate_config`, `validate_signal`, `ConfidenceEngine`, and `RiskEngine` behavior exposed by the readiness module

### Deterministic behavior

- If `generated_at_utc` is supplied, the ledger record is deterministic for the same signal content and `signal_id`.
- If `signal_id` is supplied, that value is used unchanged.
- If `signal_id` is omitted, a deterministic hash is derived from normalized signal fields.

## How to run

From `C:\Dev\Ai.Os`:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python automation/forex_engine/run_paper_signal_intake_demo.py
```

Expected output is deterministic JSON for a demo local signal and returns exit code `0` when paper accepted.

## Safety boundary

This lane is local paper-only and keeps the following paths blocked:

- broker APIs / OANDA
- real webhook execution
- order submission
- live/real market data
- API key/secret reads
- schedulers/daemons
- worker launch
- runtime/telemetry/report mutation
- dashboard changes
- cloudflare changes
- backup sync changes
- commit/push/merge automation

## What remains blocked

No live or real broker path exists in this step. All execution is blocked at the ledger layer with explicit `blocked_actions` and `execution_allowed=false`.

## Next safe Forex step

Use the generated ledger output as an input boundary for the next supervised lane, where paper signals can be routed to a paper review surface and then to follow-on supervised research steps once additional tests are added for drawdown pauses, max-open-paper-trade limits, and confidence floor boundaries.
