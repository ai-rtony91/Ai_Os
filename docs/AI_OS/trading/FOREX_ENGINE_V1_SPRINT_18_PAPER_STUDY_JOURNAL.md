# Forex Engine v1 Sprint 18 - Paper Study Journal

## What This Proves

Sprint 18 adds a deterministic paper study journal builder that consumes the Sprint 17 continuity review output and
materializes an auditable study record for Anthony approval.

The study journal record includes:

- `schema: forex_paper_study_journal_v1`
- `mode: PAPER_ONLY`
- `journal_id`
- `source_review_status`
- `source_review_status_from`
- `source_decision_id`
- `source_ledger_record_id`
- `signal_id`
- `generated_at_utc`
- `journal_status: PAPER_STUDY_JOURNAL_READY` or `PAPER_STUDY_JOURNAL_BLOCKED`
- `accepted_for_study`
- `execution_allowed`
- `review_summary`
- `reason` and `reasons`
- `risk_flags`
- `blocked_actions`
- `safety`
- `study_artifacts`
- `next_safe_action`

## Input Surface (Sprint 18)

The builder expects a continuity review payload from:

- `automation/forex_engine/paper_continuity_review.py`
- `evaluate_decision_for_continuity_review(...)`

It requires:

- `review_status == PAPER_REVIEW_READY`
- `decision == PAPER_ACCEPT`
- `accepted_for_paper == True`
- `execution_allowed == False`
- all required blocked actions:
  - `broker_api_call`
  - `oanda_api_call`
  - `real_order_submission`
  - `webhook_execution`
  - `secret_or_api_key_load`
- all required safety blocks remain `True`
- IDs for `source_decision_id`, `source_ledger_record_id`, and `signal_id`

## Deterministic Behavior

- Returns a stable `journal_id` when all deterministic inputs are fixed.
- Keeps paper-only controls by always returning `execution_allowed: false`.
- Adds `study_artifacts` to indicate expected evidence anchors for downstream review.

## Human Safety Surface

Sprint 18 remains paper-only and does not execute any external operations.

- no broker/OANDA traffic
- no secret/API loading
- no webhook execution
- no live order routing
- no network or scheduler/runtime/daemon operations
- no worker launch
- no runtime/telemetry/dashboard/report mutation
- no merge/daemon/approval automation
- no Cloudflare or backup sync

## How to Run

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
python automation/forex_engine/run_paper_study_journal_demo.py
```

Expected result:

- Exit `0` on `journal_status == PAPER_STUDY_JOURNAL_READY`
- Exit `1` otherwise

## Validation

- `git diff --check`
- `python -m pytest tests/forex_engine/test_paper_study_journal.py -q -p no:cacheprovider`
- `python -m pytest tests/forex_engine -q -p no:cacheprovider`
- `python automation/forex_engine/run_paper_study_journal_demo.py`
- `.\aios.ps1 -Mode status`
