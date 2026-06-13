# AIOS SOS Escalation Policy V1

## Purpose

`Get-AiOsSosEscalationPolicy.DRY_RUN.ps1` is a DRY_RUN-first policy router that classifies
actor relay reviews into:

- `ROUTINE_REVIEW`
- `SOS_ESCALATION`
- `NO_REVIEW_NEEDED`

It is read-only and never executes, writes relay state, or approves execution.

## Position in the relay loop

This router sits after the actor relay resolver in the relay flow:

1. `Get-AiOsRelayBusState.DRY_RUN.ps1` detects pending actor relay messages.
2. `Resolve-AiOsRelayHumanReview.DRY_RUN.ps1` produces the latest human-review context.
3. `Get-AiOsSosEscalationPolicy.DRY_RUN.ps1` classifies the review context.
4. `Get-AiOsRelayOperatorState.DRY_RUN.ps1` and operator commands can surface the safe recommendation.
5. In relay operator mode, these fields are surfaced as `sos_*` fields so Anthony can see
   whether to treat a review as routine or SOS escalation.

The policy is advisory for next-action precedence and does not mutate upstream state.

## Inputs

- `-RelayReviewJsonPath` (optional)
  - Read an existing review JSON payload (typically `AIOS_RELAY_HUMAN_REVIEW_RESOLUTION.v1`).
- `-PayloadText` (optional)
  - Classify supplied text directly.
- no input
  - Reads the current output of:
    `Resolve-AiOsRelayHumanReview.DRY_RUN.ps1 -OutputJson`

## Output schema

The script always returns `AIOS_SOS_ESCALATION_POLICY.v1` fields:

- `schema`
- `mode` (`DRY_RUN_READ_ONLY`)
- `writes_files` (`false`)
- `execution_allowed` (`false`)
- `can_continue_without_anthony` (`false`)
- `requires_human_review`
- `escalation_status` (`NO_REVIEW_NEEDED` / `ROUTINE_REVIEW` / `SOS_ESCALATION`)
- `anthony_required`
- `routine_review_allowed`
- `escalation_reasons` (array)
- `matched_sos_categories` (array)
- `matched_routine_categories` (array)
- `safe_next_action`
- `source_summary`
- `inspected_actor`
- `inspected_target_actor`
- `inspected_packet_id`
- `inspected_message_type`
- `inspected_status`
- `confidence` (`HIGH` / `MEDIUM` / `LOW`)
- `limitations` (array)

## SOS categories

`SOS_ESCALATION` is selected when any SOS category matches.

### 1) Secrets / credentials

- `secret`
- `credential`
- `token`
- `api key`
- `api_key`
- `bearer`
- `xoxb-`
- `password`
- `passphrase`
- `private key`
- `ssh key`
- `.env`
- `env file`
- `yubikey`
- `2fa`
- `totp`
- `recovery code`
- `OAuth`
- `client_secret`
- `access_token`
- `refresh_token`

### 2) Money / trading / broker / live execution

- `broker`
- `OANDA`
- `Alpaca`
- `order`
- `real order`
- `live order`
- `trade execution`
- `live trading`
- `money movement`
- `deposit`
- `withdrawal`
- `transfer funds`
- `webhook execution`
- `TradingView webhook`
- `TradersPost`
- `position sizing live`
- `market order`
- `limit order`
- `stop loss order`
- `take profit order`
- `buying power`
- `account balance`
- `margin`
- `liquidation`

### 3) Destructive repo/file changes

- `delete`
- `remove recursively`
- `overwrite`
- `destructive`
- `reset --hard`
- `clean -fd`
- `force push`
- `git push --force`
- `drop commit`
- `delete branch`
- `purge`
- `wipe`
- `rm -rf`
- `robocopy /MIR`
- `format drive`
- `restore over source`
- `backup overwrite`

### 4) Runtime / worker / scheduler / daemon activation

- `start worker`
- `launch worker`
- `scheduler`
- `daemon`
- `supervisor start`
- `persistent runtime`
- `background job`
- `task scheduler`
- `service install`
- `startup task`
- `auto-run`
- `autonomous execution`
- `unattended execution`
- `loop without approval`
- `continue without Anthony`

### 5) Governance / authority ambiguity

- `unclear approval`
- `ambiguous authority`
- `missing approval`
- `approval inbox mutation`
- `lock mutation`
- `queue mutation`
- `claim lock`
- `release lock`
- `bypass approval`
- `skip review`
- `override guard`
- `ignore AGENTS.md`
- `ignore RISK_POLICY.md`
- `emergency override`

### 6) Security, legal, business

- `security alert`
- `vulnerability`
- `exposed secret`
- `data leak`
- `malware`
- `phishing`
- `compromise`
- `unauthorized access`
- `legal`
- `compliance`
- `contract`
- `bank`
- `tax`
- `identity verification`
- `business registration`
- `DUNS`
- `domain transfer`
- `production credential`

## ROUTINE categories

`ROUTINE_REVIEW` is selected when no SOS category matches and review is still required.

- Codex final report review
- ChatGPT supervisor or human-review handoff
- generated packet review
- PR/check/merge/sync readiness
- docs/tests/refactor review
- relay message review with no risk flags
- continuation recommendation review
- self-build packet draft review
- status report review

## Classification precedence

- `SOS_ESCALATION` beats `ROUTINE_REVIEW`.
- Any SOS match returns `SOS_ESCALATION`, even if routine language is also present.
- `NO_REVIEW_NEEDED` applies when status is ready-equivalent and no review signal is present.
- if classification is uncertain, default is `ROUTINE_REVIEW` with `confidence = LOW`.

## Safe next actions

- `SOS_ESCALATION`:
  "Wake Anthony. Do not execute. Preserve evidence, stop mutation, and route through human owner approval."
- `ROUTINE_REVIEW`:
  "Continue through governed routine review. Do not wake Anthony unless review finds SOS conditions."
- `NO_REVIEW_NEEDED`:
  "No SOS action required. Continue only through existing governed next-action router."

## Why PR/merge/sync is routine

These operations are core delivery mechanics and normally require normal governance rather than immediate escalation when they do not include:

- secret/token/credential indicators
- live money or broker activity
- destructive or persistence changes
- explicit governance/authority bypasses
- explicit security/legal/business escalation triggers

## Why SOS categories are hard stop

SOS categories represent high-risk actions that can impact:

- secrets or credentials
- financial operations
- irreversible repository/runtime state
- security posture and legal exposure
- authority boundaries or trust model

In these cases, escalation to the human owner is required before continuation.

## DRY_RUN/read-only limits

`Get-AiOsSosEscalationPolicy.DRY_RUN.ps1`:

- reads without writing files
- does not approve execution
- does not resolve review items
- does not invoke runtime mutation

## Future operator integration

The router is designed to feed next-action precedence logic so that actor relay
reviews can stay in governed routine flow when safe, and wake Anthony only when SOS
conditions are detected.

Example command:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/relay_bus/Get-AiOsSosEscalationPolicy.DRY_RUN.ps1 -OutputJson
```
