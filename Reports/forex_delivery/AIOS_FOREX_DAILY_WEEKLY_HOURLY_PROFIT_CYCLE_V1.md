# AIOS Forex Daily/Weekly/Hourly Profit Cycle V1

## Scope
- Governs evidence-only completion behavior before any live money compounding authority is approved.
- Defines when the lane scans, executes review-only transitions, and stops.

## Hourly scan cycle
- Run an eligibility scan each hour only during configured market operation windows.
- Record setup quality and gate inputs into a sanitized packet artifact.
- Do not generate order intent if `max_trades_per_hour` is already met.

## Daily execution window
- Window opens at cycle start with a completed daily checklist.
- Window closes on explicit stop conditions or day-end sweep.
- No forced hourly entries during any hourly scan.

## Daily start checklist
- Capital bucket is loaded and within fixed starting budget.
- Previous day evidence and stop states are in a clean state.
- Governor input is valid JSON and contains required fields.
- Risk gates: kill-switch, daily stop, and max loss are active.
- No unresolved owner escalation is pending from prior cycle.

## Daily stop checklist
- Daily target reached or stretch target triggered.
- Daily max-loss condition or risk gate fail.
- Daily governor failure or stale evidence flag.
- End-of-day P/L sweep completed.

## End-of-day P/L sweep
- Capture realized and unrealized P/L from the day.
- Classify sweep outcome as `UNDER_TARGET`, `AT_TARGET`, or `OVER_STRETCH`.
- Lock protected bucket until review packet writes evidence for next cycle.

## Weekly evidence review
- Weekly packet review of:
  - evidence freshness,
  - target attainment consistency,
  - risk gate reset quality,
  - post-trade capture integrity.
- Evaluate compounding ladder only if daily evidence indicates stable behavior.

## Escalation conditions
- escalate_to_owner when:
  - governor outputs `LIVE_MICRO_EXCEPTION_REVIEW_READY`,
  - kill-switch/daily stop/max-loss gates change state,
  - max trades cap reached without clear post-trade capture,
  - sweep cannot be completed cleanly.
- escalate to owner review if no explicit micro-exception evidence exists before live-micro progression.

## Fail-closed states
- GOVERNANCE_BLOCKED
- EVIDENCE_STALE
- RISK_GATE_FAIL
- OWNER_GATE_PENDING
- BUCKET_EXHAUSTED
- INVALID_STATE_MODEL

## No-trade states
- NO_SCAN_QUALITY
- NO_LIVE_AUTHORITY
- REQUIRE_MORE_EVIDENCE
- DAILY_TARGET_HOLD
- OWNER_DENIED

## High-quality setup states
- QUALIFIED_SETUP
- PROPOSAL_APPROVED_BY_GOVERNOR
- BUCKET_FIT
- READY_TO_SWEEP
- READY_FOR_REVIEW_PACKET

## Owner notification states
- OWNER_REVIEW_REQUIRED
- OWNER_APPROVAL_CAPTURE_REQUIRED
- OWNER_RECHECK_REQUIRED
- OWNER_TARGET_REVALIDATION_REQUIRED

## Post-trade evidence capture states
- MONITORING_CAPTURE_PENDING
- POST_TRADE_CAPTURE_PENDING
- P_L_CAPTURE_CONFIRMED
- POST_TRADE_STATE_READY

## Completion sequence
1. Run hourly scan.
2. Qualify and score candidate.
3. Validate risk gates and capital bucket.
4. Update sanitized governor input.
5. Rerun governor and classify status.
6. If status is review-ready, escalate owner packet and stop autonomous proposals.
7. Track each trade result in evidence store.
8. Run end-of-day sweep and reset counters.
9. Run weekly review for compounding ladder transitions.
10. Emit next execution-safe packet and preserve stop conditions.
