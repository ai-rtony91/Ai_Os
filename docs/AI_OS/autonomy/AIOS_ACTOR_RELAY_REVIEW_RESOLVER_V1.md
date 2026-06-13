# AIOS Actor Relay Human Review Resolver V1

## Purpose

`Resolve-AiOsRelayHumanReview.DRY_RUN.ps1` is a DRY-RUN-first resolver that inspects
the latest actor relay bus message and emits a fixed human-review summary.

- No message mutation.
- No queue/lock/daemon/runtime edits.
- No approvals are granted.
- No direct operator action is executed.

## Behavior

1. Read the latest file in `control/relay_bus/messages/inbox`.
2. Parse the message envelope safely.
3. Return review resolution status and rationale.
4. Never set writable behavior.
5. Surface the SOS policy handoff when review is required.

When a message is present, the resolver emits this summary:

- `latest_message_path`
- `actor`
- `target_actor`
- `packet_id`
- `message_type`
- `intent`
- `status_detail`
- `why_human_review_needed`
- `safe_next_action`

If no inbox message exists, status is `EMPTY` and no file is considered reviewed.

## Output schema

The script always returns JSON fields with these defaults:

- `schema`: `AIOS_RELAY_HUMAN_REVIEW_RESOLUTION.v1`
- `mode`: `DRY_RUN_READ_ONLY`
- `writes_files`: `false`
- `execution_allowed`: `false`
- `can_continue_without_anthony`: `false`
- `requires_human_review`: `true`
- `status`: one of `EMPTY`, `READY`, `NEEDS_HUMAN_REVIEW`
- `sos_policy_next_action`: set when `status` is `NEEDS_HUMAN_REVIEW` to:
  `powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/relay_bus/Get-AiOsSosEscalationPolicy.DRY_RUN.ps1 -OutputJson`

## Status rules

- `EMPTY`:
  - No readable relay message found.
  - `latest_message_path` and actor-related fields are blank.
- `NEEDS_HUMAN_REVIEW`:
  - Latest message is missing a review-safe state, marked `requires_human_review`, or contains blocked-secrets in `payload_text`.
- `READY`:
  - Latest message does not require review and has no blocking secret pattern.

## Security behavior

- The resolver scans `payload_text` for obvious secret-like patterns:
  - `AIOS_TG_BOT_TOKEN`
  - `token=`
  - `api_key`
  - `secret`
  - `bearer`
  - `xoxb-`

If detected, `payload_contains_forbidden_secret_pattern` is `true` and review remains required.

## SOS handoff

When `status` is `NEEDS_HUMAN_REVIEW`, the resolver emits `sos_policy_next_action` and updates `safe_next_action` to route operators to:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/relay_bus/Get-AiOsSosEscalationPolicy.DRY_RUN.ps1 -OutputJson
```

This keeps the resolver read-only and delegates policy classification to the SOS router.

## Example command

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/relay_bus/Resolve-AiOsRelayHumanReview.DRY_RUN.ps1 -OutputJson
```
