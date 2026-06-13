# AIOS SOS Escalation Policy V1

## Purpose

`Get-AiOsSosEscalationPolicy.DRY_RUN.ps1` is a DRY-RUN-first router that classifies
actor relay review output into one of three escalation states:

- `ROUTINE_REVIEW`
- `SOS_ESCALATION`
- `NO_REVIEW_NEEDED`

It does not mutate relay files, queues, locks, approval inbox state, runtime state,
or execution paths. It only summarizes risk posture and recommends the next safe action.

## Routing behavior

`Get-AiOsSosEscalationPolicy.DRY_RUN.ps1` reads one of the following inputs:

- `-RelayReviewJsonPath` (optional): existing relay review JSON to classify.
- `-PayloadText` (optional): override text to classify directly.
- no input (default): it invokes `Resolve-AiOsRelayHumanReview.DRY_RUN.ps1 -OutputJson`
  and classifies that output.

Output schema is always:

- `schema = AIOS_SOS_ESCALATION_POLICY.v1`
- `mode = DRY_RUN_READ_ONLY`
- `writes_files = false`
- `execution_allowed = false`
- `can_continue_without_anthony = false`
- `escalation_status`
- `escalation_reasons`
- `safe_next_action`
- `anthony_required`
- `routine_review_allowed`

## ROUTINE vs SOS distinction

Use `ROUTINE_REVIEW` for normal operating handoff that does not raise a safety risk:

- normal Codex report review
- normal generated packet review
- normal PR/check/merge/sync readiness
- ordinary doc/test/refactor review messages
- relay review that needs human read-through but has no SOS trigger

Use `SOS_ESCALATION` for high-signal risk:

- secret/token/API key/credential/secret pattern
- broker/OANDA/webhook/order/live trading/money movement
- destructive `delete`/`overwrite`/`reset`/`force push`/`truncate` language
- runtime/worker/scheduler/daemon launch
- approval inbox mutation
- lock/queue mutation without explicit packet scope
- failed recovery or ambiguous authority
- security alert
- legal or business decision requiring Anthony

Use `NO_REVIEW_NEEDED` when resolver status is `READY` and no SOS triggers exist,
or when no review payload/state exists in this pass.

## Anthony wake vs governed continuation

- `SOS_ESCALATION`: Anthony should be woken and review explicitly before any continuation.
- `ROUTINE_REVIEW`: continue in governed actor relay review flow without forced Anthony escalation.
- `NO_REVIEW_NEEDED`: continue normal flow; no escalation signal is required.

## DRY-RUN/read-only limits

- never execute commands
- never write files
- never approve or resolve relay messages
- never mutate relay or runtime state

## Connection to actor relay review resolver

The policy router consumes the relay review summary and decides whether that review
can stay in routine operator flow or must be escalated as an SOS condition.

Example command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/relay_bus/Get-AiOsSosEscalationPolicy.DRY_RUN.ps1 -OutputJson
```
