# Forex Engine v1 Sprint 16 - Paper Risk Decision Router

## What This Proves

Sprint 16 adds a deterministic paper-only risk decision router between paper intake and any downstream paper workflow.

The router consumes a `paper_signal_intake` ledger record and returns a formal decision record with:

- `schema: forex_paper_risk_decision_v1`
- `mode: PAPER_ONLY`
- `decision_id`
- `source_ledger_record_id`
- `signal_id`
- `generated_at_utc`
- `readiness_status`
- `decision` (`PAPER_ACCEPT` or `PAPER_REJECT`)
- `accepted_for_paper`
- `execution_allowed`
- `reason` and `reasons`
- `risk_flags`
- `blocked_actions`
- `safety`
- `next_safe_action`

## Relationship to Sprint 14 and Sprint 15

- It uses the Sprint 15 intake ledger output (`paper_signal_intake` record).
- It does not re-run broker/risk engines; it performs a deterministic decision policy on top of the existing
  `readiness_status`, `accepted_for_paper`, `execution_allowed`, `risk_flags`, `safety`, and `blocked_actions`.
- It enforces strict paper-only gatekeeping:
  - accepts only `PAPER_READY` records
  - requires `accepted_for_paper` true
  - requires `execution_allowed` false
  - requires all safety block flags to be present and true
  - requires zero risk flags
  - requires the blocked action set to include broker/OANDA/webhook/order/secret entries
- Rejection reasons are explicit and deterministic.

## How Anthony Runs It

From `C:\Dev\Ai.Os`:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python automation/forex_engine/run_paper_risk_decision_demo.py
```

The script prints JSON and returns exit code:

- `0` when decision is `PAPER_ACCEPT`
- `1` otherwise

To validate focused coverage:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python -m pytest tests/forex_engine -q -p no:cacheprovider
```

## What Remains Blocked

Sprint 16 remains paper-only and does not unlock:

- broker or OANDA calls
- webhook execution
- real orders
- live market data
- secret/API key reads
- scheduler/daemon/worker launch
- runtime/telemetry/report writes
- dashboard/Cloudflare changes
- backup sync paths
- commit/push/merge automation

## Next Safe Forex Step After Sprint 16

After this router is stable, the next safe step is to route `PAPER_ACCEPT` decisions into a supervised review step
under human approval, then build the next bounded lane for paper-only continuation decisions with additional evidence
framing. This should continue to use:

- deterministic local fixtures
- strict rule-based gating
- explicit blocked action lists
- no external network or live execution paths
