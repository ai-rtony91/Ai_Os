# AIOS Forex Supervised Demo Manual Execution Exception Packet V1

## What Anthony Reviews

The Supervised Demo Manual Execution Exception Packet V1 combines the landed owner approval epic with the manual execution exception scope gate and manual-only checklist. It creates a local-only packet for Anthony to review before he decides whether a future demo trade should be manually executed outside Codex.

No broker call was made. No trade placed.

## Owner Approval Summary

- Owner approval status: `SUPERVISED_DEMO_OWNER_APPROVAL_READY_FOR_OWNER_REVIEW`
- Owner approval remains manual-review-only.
- Codex execution remains false.
- Broker action remains false.

## Manual Exception Scope Summary

- Scope status: `DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_VALID_FOR_REVIEW`
- Required phrase confirms Codex is not authorized to execute, call a broker, or place orders.

## Checklist Summary

- Checklist status: `DEMO_MANUAL_EXECUTION_EXCEPTION_CHECKLIST_READY`
- Post-trade evidence is required.
- Feedback routing is required.
- Loss possibility must be understood.

## Proposed Review Details

- Selected strategy: `Supertrend`
- Candidate id: `supertrend-review-ready-sample`
- Instrument: `EUR_USD`
- Direction: `LONG`
- Entry type: `operator_review_market_entry`
- Entry: `1.1000`
- Stop: `1.0950`
- Target: `1.1100`
- Units: `20000`
- Max loss: `100.00`
- Expected reward: `200.00`
- Reward-to-risk: `2`

## Owner Warning

Do not execute unless Anthony explicitly approves.

## Exception Warning

Manual exception review only. Codex is not authorized to execute, call a broker, access credentials, or place orders.

## Required Phrase

`I, Anthony, request manual review of this supervised demo execution exception packet only. I understand Codex is not authorized to execute, call a broker, or place orders.`

## Blocked Actions

- Codex demo execution
- Codex broker call
- Broker action
- Credential access
- Account ID persistence
- Live trading
- Real money
- Compounding
- Bank movement

## Post-Trade Evidence Requirement

Post-trade evidence must be captured after any separately approved, manually supervised demo trade. This packet does not create or fabricate evidence.

## Feedback Routing Requirement

Feedback routing must occur only after sanitized post-trade evidence exists. This packet does not route feedback before evidence exists.

## Permission Status

All protected permissions remain false. A ready exception packet is still only a local review artifact.
