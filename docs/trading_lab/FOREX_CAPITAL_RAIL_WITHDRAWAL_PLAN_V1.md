# FOREX Capital Rail Withdrawal Plan V1

## Purpose
Combine bucket-control output, redacted rail registry, OANDA funding rail context, and cadence recommendation into one owner-gated withdrawal review packet.

This module is **read-only**. It does not move money, does not call broker or bank APIs, and does not require credentials.

## Inputs
- Bucket controller payload (`capital_bucket_purge_controller_v1`)
- Rail registry payload (`capital_rail_registry_v1`)
- Cadence planner payload (`withdrawal_cadence_planner_v1`)
- OANDA funding rail readiness payload (if available)

## Evaluation Sequence
1. Validate no sensitive financial keys are present.
2. Summarize:
   - protected bucket constraints,
   - reserve health,
   - rail proof state,
   - cadence readiness,
   - risk blockers.
3. Resolve one final `withdrawal_plan_status`:
   - `READY_FOR_OWNER_REVIEW`
   - `BLOCKED_BY_RISK`
   - `BLOCKED_BY_RAIL`
   - `BLOCKED_BY_RESERVE`
   - `BLOCKED_BY_SENSITIVE_DATA`
4. Emit owner-gated instruction package with no execution authority.

## Owner Gate
- `owner_name = Anthony`
- `approval_required = True`
- `approval_scope = manual external withdrawal review only`
- `execution_allowed = False`

## Withdrawal Review Policy
- Default posture: review only.
- If all gates pass, packet can be presented as `READY_FOR_OWNER_REVIEW`.
- If any gate is blocked, status remains blocked with explicit reason(s).

## Sensitive-Data Rule
- If sensitive fields (routing/account/card/token/credential/etc.) are present in input, this packet returns `BLOCKED_BY_SENSITIVE_DATA`.
- Sensitive values are never echoed.

## No Money Movement
Hard guarantees for this layer:
- `money_movement_allowed = False`
- `bank_access_allowed = False`
- `broker_api_allowed = False`
- `manual_execution_only = True`

## Safe Controls Included in Output
- `safety` flags and `audit_record`
- `blocked_reasons` and `missing_information`
- manual evidence handoff reminders

## Source Mapping to System Goals
- Helps answer: eligibility, rail proof status, reserve sufficiency, cadence choice, and manual next step.
- Does not produce instructions for bank/broker transfer.

