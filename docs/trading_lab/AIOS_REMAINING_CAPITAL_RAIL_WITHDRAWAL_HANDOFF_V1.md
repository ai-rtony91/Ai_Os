# AIOS Remaining Capital-Rail Withdrawal Handoff (V1)

## Purpose
This document defines the remaining gap in the institutional capital-control layer:
read-only, owner-gated review for bucket purge/rollover/sweep, rail registry curation,
withdrawal cadence planning, and final withdrawal plan assembly.  
Money movement remains manual and never owner-autonomous.

## Remaining Work Only
The next work is to ship four read-only modules and this handoff documentation:

- `capital_bucket_purge_controller_v1`
- `capital_rail_registry_v1`
- `withdrawal_cadence_planner_v1`
- `capital_rail_withdrawal_plan_v1`

This is a TODO-only sequence to keep execution boundaries explicit.

## Institutional Capital-Control Standard
- Segregation of duties.
- Least privilege and fail-closed safety checks.
- No credentials, no sensitive financial values, no automatic API calls.
- Deterministic outputs only; every decision is auditable.
- Explicit owner gate for any withdrawal recommendation.
- Preserve audit history and never destroy historical review state.

## Source Context
The remaining gap is capital-bucket purge/rollover/sweep plus redacted capital rail planning. Money movement remains manual and owner-approved.

## Capital Bucket Model
The bucket model treats capital as conceptual accounts:

- `balance_bucket`
- `profit_bucket`
- `loss_bucket`
- `tax_reserve_bucket`
- `operating_reserve_bucket`
- `withdrawal_bucket`
- `compounding_bucket`
- `pending_withdrawal_bucket`

`withdrawal_bucket` is review-only and never auto-sent.

## Purge / Rollover / Sweep Policy
- **Purge**: archives stale metadata, expired review states, and stale pending actions.
- **Rollover**: closes a review period and carries forward realized values for next review.
- **Sweep**: only proposes movement between conceptual buckets (`proposed_bucket_allocation`).
- No action in this module alters balances or triggers transfers.

## Redacted Rail Registry Policy
- Rails are accepted as redacted metadata only.
- No full account/routing/card/credential data is stored or accepted.
- Same-name proof status is tracked and included as an explicit gate.
- Active + withdrawal-capable + same-name verified rails become eligible.

## Weekly Withdrawal Review Plan
Weekly cadence is considered only when all are true:

- Profit is strong/consistent.
- Fees are low enough.
- No margin or open-risk block.
- Reserves are protected.
- Amount meets minimum threshold.
- Rail proof is present.

## Monthly Withdrawal Review Plan
Monthly is the conservative default for healthy profit and protected reserves.

## Bimonthly Withdrawal Review Plan
Bimonthly is preferred when:

- Fee burden is high for high-frequency review, or
- Profit consistency evidence is thinner than weekly-quality standard.

## No-Withdrawal Condition
- No profit or below threshold.
- Daily loss stop active.
- Drawdown above allowed limit.
- Margin/open-risk block.
- Reserve shortfall.
- Rail same-name proof missing.
- Fee burden too high relative to review value.

## Protected Reserve Rules
- Tax reserve and operating reserve are treated as protected.
- Reserve shortfalls block owner review readiness.
- Protected reserve integrity is surfaced every evaluation.

## Rail Selection Rules
Selection order:

1. Eligibility (active + withdrawal + same-name verified + no sensitive fields).
2. Lowest cost.
3. Fastest processing tie-break.
4. Owner preferred as secondary tie-break.

## OANDA Withdrawal Hierarchy Dependency
- OANDA card/withdrawal context is read-only input only.
- Any final packet states the hierarchy expectations as a policy note only.

## Personal Bank Institution Return Path
- Final output is a review packet only.
- Owner performs outbound movement outside AIOS via approved personal bank workflows.

## Owner Gate
- Only Anthony can approve the manual review step.
- No AIOS execution authorization is issued.

## Manual Execution Only
- `money_movement_allowed` is always `False`.
- `broker_api_allowed` is always `False`.
- `bank_access_allowed` is always `False`.
- Planned output is for review, not execution.

## Sensitive-Data Prohibition
- Sensitive financial values are rejected.
- The planner and registry never echo sensitive payload back in outputs.
- A sensitive payload returns blocked reasons and stays read-only.

## Audit Evidence Model
- Safety record, blockers, stale flags, missing information,
  read-only audit placeholder, and action recommendations are produced for each run.

## Validator Chain
- Syntax validation before tests.
- Pytest execution against new module tests.
- Diff + status sanity checks for this packet’s allowed paths.

## Future Expansion TODOs
- Add optional explicit drawdown policy input from risk layer.
- Add fee-rule templates per rail type and jurisdiction.
- Add stronger audit hash chaining with immutable artifact stores.
