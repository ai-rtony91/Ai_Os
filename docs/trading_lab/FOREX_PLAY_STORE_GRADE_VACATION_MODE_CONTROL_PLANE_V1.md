# Forex Play Store-Grade Vacation Mode Control Plane V1

## Status

Internal product architecture documentation. This document does not claim Play Store readiness, legal/commercial readiness, sale readiness, profit readiness, broker authority, or trade authority.

## Vacation Mode Definition

Vacation Mode is a metadata-only AIOS Forex control plane for owner-visible evaluation. It can evaluate whether a setup is eligible for owner review, classify supervised position metadata, recommend exit review states, create an owner handoff, and score release-candidate readiness.

Vacation Mode does not place trades, close trades, call a broker, call OANDA, read credentials, read account identifiers, send notifications, create background runtimes, move money, or approve repeated attempts.

## Play Store-Grade Product Standard

The Play Store-grade standard is an internal product quality target. It requires clear financial-risk disclosure, privacy/data-safety controls, minimal Android permissions, evidence-backed claims, owner consent, support/escalation paths, shutdown paths, and legal/compliance owner review before public release.

This skeleton is not a store submission and is not store approval.

## Metadata-Only Control-Plane Boundary

The control plane returns structured metadata:

- readiness states.
- blockers.
- owner-visible reasons.
- owner next actions.
- release-candidate blockers.
- hard false safety fields.

The control plane intentionally avoids runtime side effects.

## Entry Authority Gate

`forex_vacation_mode_entry_authority_gate_v1.py` evaluates whether an owner-governed entry recommendation may be prepared. It requires product policy readiness, owner authority metadata, setup signal metadata, risk limits, stop-loss readiness, exit-plan readiness, market/calendar readiness, read-only broker metadata, proof ledger readiness, and safety policy metadata.

The output is an owner-review recommendation only.

## Position Supervision Model

`forex_vacation_mode_position_supervisor_v1.py` evaluates open-position metadata. It can classify hold, exit review, emergency stop review, receipt requirement, owner alert requirement, risk block, market block, and safety block.

It does not alter or close a trade.

## Exit Authority Gate

`forex_vacation_mode_exit_authority_gate_v1.py` evaluates whether exit review is required. It can classify stop-loss, take-profit, market-close, kill-switch, rule-failure, owner-review, or hold states.

The output is an exit recommendation only. It does not close an order.

## Owner Handoff Model

`forex_vacation_mode_owner_handoff_v1.py` creates an owner-facing summary. It includes current phase, owner next action, owner-visible blockers, required evidence, no-live-execution statement, no-profit-guarantee statement, legal/compliance-not-complete statement, not-Play-Store-ready statement, and not-sale-cleared statement.

## Release-Candidate Scorecard

`forex_vacation_mode_release_candidate_scorecard_v1.py` scores the release-candidate policy and control-plane areas:

- product policy readiness.
- financial-risk disclosure readiness.
- privacy/data-safety readiness.
- permissions model readiness.
- store claims policy readiness.
- owner consent readiness.
- entry gate readiness.
- position supervisor readiness.
- exit gate readiness.
- alerting readiness.
- evidence bundle readiness.
- broker receipt readiness.
- realized PnL reconciliation readiness.
- legal/compliance review readiness.
- mobile control-plane readiness.
- release packaging readiness.
- final release-candidate readiness.

Final release-candidate readiness cannot be complete unless all areas are ready.

## No Broker Call

This skeleton makes no broker call and creates no broker connector.

## No Live Execution

This skeleton performs no live execution, demo execution, paper execution, order placement, order close, repeat attempt, or money movement.

## No Profit Guarantee

AIOS Forex must not promise profit, passive income, fixed returns, or outcome certainty. Evidence supports review only.

## No Play Store Readiness Claim

This skeleton does not make AIOS Forex Play Store ready.

## No Legal/Compliance Readiness Claim

This skeleton does not complete legal/compliance review.

## Remaining Blockers

- Owner legal/compliance review.
- Financial-services review.
- Jurisdiction review.
- Broker terms review.
- Privacy/data-safety review.
- Android packaging and permission implementation.
- Store listing copy review.
- User agreement.
- Privacy policy.
- Support/escalation and shutdown process.
- Sanitized external evidence bundle.
- Broker receipt review and redaction.
- Realized PnL reconciliation review.
- Manual protected-action approval for stage, commit, push, and PR creation.

## Next Required PRs

- `AIOS_FOREX_VACATION_MODE_CONTROL_PLANE_INTEGRATION_FIXTURES_V1`
- `AIOS_FOREX_VACATION_MODE_MOBILE_PERMISSION_MAPPING_V1`
- `AIOS_FOREX_VACATION_MODE_OWNER_REVIEW_UI_CONTRACT_V1`
- `AIOS_FOREX_VACATION_MODE_RELEASE_REVIEW_EVIDENCE_BUNDLE_V1`
