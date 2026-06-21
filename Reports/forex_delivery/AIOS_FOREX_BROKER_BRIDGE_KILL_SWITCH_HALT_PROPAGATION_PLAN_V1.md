# AIOS FOREX BROKER BRIDGE KILL SWITCH / HALT PROPAGATION PLAN V1

## Overview

All broker-bridge actions must stop immediately on any halt event and remain in a safe blocked state until explicit operator review resumes activity.

## Halt Types

- Global kill switch
- Broker bridge halt
- Endpoint halt
- Credential halt
- Account halt
- Intent halt
- Review halt
- Approval halt
- Execution halt
- Stale evidence halt
- Replay failure halt

## Halt Precedence (Highest to Lowest)

1. Global kill switch
2. Replay failure halt
3. Stale evidence halt
4. Credential halt
5. Account halt
6. Approval halt
7. Review halt
8. Endpoint halt
9. Intent halt
10. Execution halt
11. Broker bridge halt

If any higher-precedence halt is active, all lower-precedence transitions remain denied regardless of lower-level state.

## Halt Propagation

- A halt in one domain is emitted to all downstream readiness nodes.
- Downstream nodes recompute state as `BLOCKED` and emit blocked attempt evidence.
- Handoff nodes require explicit clear signal from an equal-or-higher authority layer before resume.
- Propagation includes `kill_switch_state` and halt reason in evidence references.
- Replay and reconciliation nodes must receive the same halt reason, with deterministic deduplicated blocker signatures.

## Halt Audit

Each halt event writes to:
- Halt event record (timestamp, correlation id, halt type, source authority)
- Correlated blocker evidence
- Replay trace marker
- Next-safe-action
- Recovery precondition checklist

## Halt Recovery

Recovery requires:
- Halt reason resolved and cleared at the originating layer
- Revalidation pass for all dependent readiness gates
- Replay and evidence recheck
- Operator review re-affirmation where needed
- `final_disarm_required` and `kill-switch` conditions re-established true

## Required Operator Review Before Resume

- Must confirm:
  - root cause is remediated
  - evidence consistency restored
  - no unsafe flags are true
  - endpoint still demo-only
  - credential/account boundaries still enforced
  - timeout/one-shot window remains valid
- Operator review reissue required for intent/review/approval records before resume of future attempt phases.
