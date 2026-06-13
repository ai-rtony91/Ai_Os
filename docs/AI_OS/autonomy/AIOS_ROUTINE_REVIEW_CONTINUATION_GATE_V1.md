# AIOS Routine Review Continuation Gate V1

## Purpose

The routine review continuation gate lets AIOS continue ROUTINE_REVIEW relay items through governed review flow without waking Anthony.

This is a review-only continuation surface. It does not authorize execution, mutation, protected actions, runtime launch, or live trading.

## Gate Behavior

Routine continuation is allowed only when relay operator state reports all of these values:

- `actor_relay_bus_status = NEEDS_HUMAN_REVIEW`
- `sos_escalation_status = ROUTINE_REVIEW`
- `sos_anthony_required = false`
- `sos_routine_review_allowed = true`

When those conditions hold, relay and action recommendation output may expose:

- `routine_review_continuation_allowed = true`
- `routine_review_continuation_reason`
- `routine_review_next_action`

The next action is limited to DRY_RUN/read-only review continuation, currently the resolver/SOS governed review path:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/relay_bus/Resolve-AiOsRelayHumanReview.DRY_RUN.ps1 -OutputJson
```

## SOS Block Behavior

Routine continuation is blocked when either condition is true:

- `sos_escalation_status = SOS_ESCALATION`
- `sos_anthony_required = true`

In that state:

- `routine_review_continuation_allowed = false`
- `next_safe_action` requires Anthony review
- no continuation command is recommended

## Anthony Wake Boundary

Anthony is not required for routine review continuation when the SOS policy classifies the item as ROUTINE_REVIEW and explicitly reports that Anthony is not required.

Anthony is required for SOS escalation, secrets, credentials, broker or live-trading language, destructive repo action language, runtime control language, governance mutation language, security incidents, legal decisions, or any other SOS policy match.

## No-Execution / No-Mutation Guarantee

This gate is DRY_RUN/read-only.

It does not authorize:

- APPLY execution
- queue mutation
- lock mutation
- approval inbox mutation
- auto-approval
- worker launch
- scheduler or daemon start
- runtime start
- telemetry writes
- commit, push, PR, merge, or branch deletion
- broker, OANDA, webhook, order, live trading, or secret paths

Passing the routine continuation gate only allows review flow to continue. It does not approve any later mutation.

## Relationship To Existing Flow

The relay bus identifies actor relay items that need review.

The resolver summarizes the latest relay review item and keeps execution disabled.

The SOS policy classifies whether the item is routine review or SOS escalation.

The relay operator state surfaces the classification and the routine continuation gate.

The action recommendation script uses the same gate to recommend only DRY_RUN/read-only continuation when routine review is allowed.

The campaign registry selects this packet as the next autonomy stage while keeping campaign planning read-only and preserving Human Owner authority for protected actions.

## Corrected Permission Boundary

Only ROUTINE_REVIEW continuation is relaxed.

Execution controls, protected-action controls, approval controls, commit/push/PR/merge controls, runtime controls, queue controls, scheduler controls, daemon controls, broker controls, OANDA controls, webhook controls, order controls, live-trading controls, and secrets controls remain blocked unless a separate explicit approved packet authorizes a safe action inside its own boundary.
