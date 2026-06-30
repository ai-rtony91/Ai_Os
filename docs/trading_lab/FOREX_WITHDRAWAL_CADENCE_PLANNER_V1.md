# FOREX Withdrawal Cadence Planner V1

## Purpose
Compute review cadence policy (`weekly`, `monthly`, `bimonthly`, `no_withdrawal`)
for capital-owner decisions.

## Inputs
- Bucket eligibility and reserve requirements.
- Rail readiness (fees, timing, same-name proof, active eligibility).
- Risk and loss constraints.

## Rules
- Weekly: requires consistency, low fee, no risk blocks, reserves met, threshold met.
- Monthly: conservative fallback when quarterly conditions are absent but profit exists.
- Bimonthly: preferred for higher fees or weaker profit evidence.
- No-withdrawal: default when blockers exist.

## Outputs
- `cadence_candidates`
- `recommended_cadence`
- each cadence plan object with `selection_gate` and reason set.
- explicit `withdrawal_eligibility`, `risk_blocks`, `fee_efficiency`.

## Safety
- Read-only planning only.
- no broker API, no bank access, no money movement.

