# Forex Engine v1 Sprint 19 - Paper Learning Action Router

## Purpose

Sprint 19 adds a deterministic learning action router that consumes
`forex_paper_study_journal_v1` records from Sprint 18 and produces a
single supervised, paper-only follow-up action payload.

The router does not execute any market action. It only prepares the next
paper learning task and required evidence for the next supervised stage.

## Input (Sprint 18 output)

The router expects a journal record produced by
`automation/forex_engine/paper_study_journal.py`:

```text
forex_paper_study_journal_v1
```

The expected source fields include:

- `journal_id`
- `journal_status`
- `accepted_for_study`
- `execution_allowed`
- `mode`
- `schema`
- `source_review_status`
- `study_artifacts`
- `blocked_actions`
- `safety`

The router requires `journal_status` to be
`PAPER_STUDY_JOURNAL_READY` and `accepted_for_study == true` to route to
`PAPER_LEARNING_ACTION_READY`.

## Output schema

`route_paper_study_journal_to_learning_action(...)` emits
`forex_paper_learning_action_router_v1` with required fields:

- `schema`
- `router_id`
- `source_journal_id`
- `source_journal_status`
- `route_status`
- `accepted_for_learning`
- `execution_allowed`
- `live_execution_status`
- `mode`
- `selected_learning_action`
- `action_reason`
- `learning_priority`
- `study_tags`
- `required_evidence`
- `blocked_actions`
- `next_safe_action`
- `safety`
- `source_trace`

## Paper-only safety boundary

The router is paper-only by design:

- `mode` is always `PAPER_ONLY`
- `execution_allowed` is always `false`
- `live_execution_status` is always `BLOCKED`
- deterministic routing and deterministic IDs only
- no runtime mutation, no scheduling, no worker/daemon launch

Required safety constraints are checked against source `safety` fields.

## Blocked actions

The router output always includes blocked actions, including:

- `broker_api_call`
- `oanda_api_call`
- `real_order_submission`
- `webhook_execution`
- `secret_or_api_key_load`
- `live_market_data_fetch`
- `scheduler_or_daemon_start`
- `worker_launch`

If input safety or source fields are incomplete or unsafe, route status is
`REVIEW_REQUIRED` or `BLOCKED`.

## Validators

Local validators to run:

- `python -m pytest tests/forex_engine/test_paper_learning_action_router.py -q -p no:cacheprovider`
- `python -m pytest tests/forex_engine -q -p no:cacheprovider`
- `python automation/forex_engine/run_paper_learning_action_router_demo.py`
- `git diff --check`
- `.\aios.ps1 -Mode status`
- Orchestration validator chain from packet:
  - `Test-WorkerClaimCollision.DRY_RUN.ps1`
  - `Test-LockRegistryIntegrity.DRY_RUN.ps1`
  - `Test-AiOsIdentitySpine.DRY_RUN.ps1`
  - `Invoke-OrchestrationValidatorChain.DRY_RUN.ps1`

## Why this is not live trading

This module does not issue broker calls, submit orders, read secrets, or
perform any network calls.

It only computes route metadata from deterministic in-memory inputs and emits
paper-safe routing fields for the next supervised learning stage.

## Next likely packet

`AIOS-FOREX-PAPER-LEARNING-ACTION-ROUTER-APPLY-V1` is a proposal output.
This router packet itself does **not** trigger next packet generation or commit/push flow.
