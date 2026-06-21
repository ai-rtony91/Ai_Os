# AIOS FOREX Governed Demo Execution Decision Tree V1

## Scope
This is a planning control diagram captured as text. It documents only allowed/denied governance transitions.

## Allowed Path

- Candidate  
  ↓ (candidate validation evidence)  
- Validation  
  ↓ (validation approval)  
- Review  
  ↓ (review approval)  
- Intent  
  ↓ (intent approved + not stale)  
- Approval  
  ↓ (operator approval present)  
- Protected Demo Execution Consideration

No broker execution is created in this packet.

## Denied Paths
Any direct bypass or skipping transition is blocked:

- Candidate → Execution (bypasses Validation, Review, Intent, Approval)
- Validation → Execution (bypasses Review, Intent, Approval)
- Review → Execution (bypasses Intent, Approval)
- Intent → Execution (bypasses Review, Approval)
- Approval → Execution (with stale/missing preconditions or inactive controls)
- Candidate → Review (if validation incomplete)
- Review → Intent (if validation expired)
- Intent → Approval (if intent duplicate or revoked)
- Any step with Kill-Switch Active → Execution
- Any step with live-mode or endpoint ambiguity → Execution

## Governance Rules for Transition Control
- Every transition requires evidence linkage to predecessor packet IDs.
- Each node requires explicit status values:
  - `READY` only on completion of required predecessor.
  - `BLOCKED` on missing/invalid prerequisites.
- Replayability is required for all transition decisions.
- Any prohibited path is hard-failed with a blocker record.

## Prohibited Transition Types
- Bypass transitions
- Duplicate execution request transitions
- Out-of-order transitions
- Stale-data transitions
- Non-human approved transitions
- Demo/live ambiguous endpoint transitions

## Audit Requirements
- Documented denied transitions include:
  - blocker reason
  - actor
  - timestamp
  - remediation ticket path
- Repeat attempts are tracked with replay hashes.
