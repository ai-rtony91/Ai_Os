# AIOS Forex Autonomy Completion Master Orchestrator V1

## Current status
- Repo state is aligned to `main` at commit `f91cab92` (PR #1203 landed).
- Supervised governor component exists and returns strict evidence readiness states.
- Live-money path is in evidence-and-governance prep, not active autonomy.
- No broker credentials, accounts, scheduler, webhook, or API control is enabled by this packet.

## What “Forex completion” means
Forex completion is the controlled transition from evidence-only preparation into a governed, repeatable, and auditable profit cycle that can move from simulation governance to a limited live-money micro-exception workflow only when every gate is explicit.

In this packet, completion includes:
- A deterministic, inspectable state model and bucket policy.
- A capital-aware daily/weekly/hourly operating loop.
- Explicit stop conditions that prevent uncontrolled execution.
- Mandatory owner escalation points.
- No assumptions or forced execution when evidence is incomplete.

## What “live-money autonomy” means
Live-money autonomy means:
- The system can propose and process governed proof states using sanitized evidence.
- A one-trade micro exception path can become review-ready, but only after explicit policy conformance.
- Execution actions remain disabled in this artifact set; this packet defines control logic and evidence requirements only.

## Landed components
- `automation/forex_engine/supervised_autonomy_governor_v1.py`
- Live-money proof prep and owner evidence artifacts in `Reports/forex_delivery/`.
- This packet will add:
  - Master orchestrator
  - Capital bucket policy
  - Hourly/daily/weekly cycle state definition
  - Autonomy completion state model JSON
  - Next-cycle Codex packet scaffold

## Missing components
- Unified lane-level state model and bucket rule set that links evidence gates to execution-readiness state.
- Explicit autonomous stop matrix tied to risk and gate failures.
- A standardized next-packet contract for safe continuation.

## Orchestration control loop
1. Scan
   - Run hourly candidate signal scan against allowed evidence surfaces.
   - Output candidate candidates with timestamps and context IDs.
2. Qualify
   - Reject malformed or stale evidence immediately.
   - Require minimum quality: freshness, risk metric presence, and monitoring readiness.
3. Score
   - Compute evidence score from profitability, sample sufficiency, and risk thresholds.
4. Risk-check
   - Apply stop-loss state, daily stop, max-loss, and open trade constraints.
5. Capital bucket check
   - Resolve active daily bucket limits from the policy file before any execution recommendation.
6. Governor input update
   - Push sanitized fields only into the governor input artifact.
7. Governor rerun
   - Re-run `run_supervised_autonomy_governor_v1`.
8. Owner gate escalation
   - If review gates require human override, capture explicit owner approvals before status transition.
9. Live micro proof path
   - Enter micro exception review only when:
     - Evidence gates pass,
     - kill-switch/daily stop/max-loss are active,
     - owner approvals are present,
     - and a one-order constraint is preserved.
10. Trade monitoring
   - Monitor live state transitions and risk metrics if a micro-trade is authorized in another lane.
11. P/L evidence capture
   - Capture close-time and gate state evidence after every trade event.
12. Daily bucket sweep
   - Close-of-day profit sweep and reset logic for protected bucket bookkeeping.
13. Weekly compounding review
   - Controlled compounding decision only after governance evidence and owner signoff.
14. Next packet generation
   - Emit the next bounded packet for rerun/classification/owner handoff.
15. Stop conditions
   - Hard stop on failed risk checks, failed gates, or max-loss trigger.

## How AIOS progresses without guessing
- If any required evidence field is missing or stale, the state remains `REQUIRE_MORE_EVIDENCE`.
- If a gate changes from pass to fail, execution status is reset to safe state before any proposal update.
- If owner approvals are not complete, status remains `WAIT_OWNER_GATE` and next packet is required.
- If policy target is met, the loop transitions to completed cycle state and stops new scan-to-execute proposals.

## How AIOS avoids uncontrolled live trading
- Explicit booleans disable all execution, broker, credentials, scheduler, daemon, and webhook actions in the completion state model.
- No forced hourly trade scheduling.
- No 22-hour or continuous loops by default.
- No free-form exception path: only the micro exception lane can become review-ready.
- Every state transition requires gate validation and recorded evidence.

## How AIOS escalates to owner only when required
- Owner escalation is required only for:
  - live micro exception transition,
  - kill-switch/daily-stop/max-loss exception interpretation,
  - post-trade evidence approval,
  - weekly compounding mode changes.
- If owner status is `PENDING`, transition stops at the owner-gated node and produces an owner-notification packet.
- No owner approval is implied by policy artifacts; each required field must be explicit.

## Remediation sequence for blockages
- Evidence shortfall -> collect additional sample/survivability evidence, rerun governor.
- Risk breach -> freeze cycle, no new proposals, request risk reset evidence.
- Micro exception not approved -> produce owner approval card and pause the lane.
- Policy change -> regenerate next packet and rerun governor with updated buckets.
- Any unexpected live API signal -> mark invalid state and stop the lane.

## Stop conditions
- `daily_return_target_percent >= 100` or `>= 120` (if stretch review is enabled) AND configured close-of-day sweep completed.
- Any max-loss stop condition or risk gate fail.
- No valid governor output.
- Missing or stale owner-gate fields.
- Validation mismatch between state model and governor evidence snapshot.
- Any instruction that violates hard safety boundaries.
