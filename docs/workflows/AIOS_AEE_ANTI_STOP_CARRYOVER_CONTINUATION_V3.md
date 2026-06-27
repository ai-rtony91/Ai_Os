# AIOS AEE Anti-Stop Carryover Continuation V3

## Purpose

Prevent premature stops in continuation packets for the `lane/aios-aee-governance-validator-v1` long-campaign lane when approved carryover artifacts are already dirty.

## Scope

This document governs continuation behavior for `aios_aee_governance_validator_v1` carryover and the V3 stopgate layer.

## Exact previous failure

Clean-main preflight was incorrectly treated as a hard stop when the same packet was legitimately running on branch `lane/aios-aee-governance-validator-v1` with approved carryover artifacts.

## Approved carryover continuation rule

- If branch is `lane/aios-aee-governance-validator-v1`
- And dirty worktree is confined to allowed paths
- And dirty files match V1 carryover artifacts or V3 stopgate artifacts
- Then status is `APPROVED_CARRYOVER_CONTINUATION`.

## Dirty worktree classification table

| condition | status |
| --- | --- |
| only allowed carryover artifacts | APPROVED_CARRYOVER_CONTINUATION |
| allowed non-carryover artifacts | RECOVERABLE_LOCAL |
| staged files | HARD_STOP |
| forbidden path dirty | HARD_STOP |

## Branch classification table

| branch | status |
| --- | --- |
| lane/aios-aee-governance-validator-v1 | continuation eligible |
| main | WRONG_PACKET_FOR_CLEAN_MAIN |
| other | HARD_STOP (BRANCH-001/002) |

## 1312 classification table

| mode | event | status |
| --- | --- | --- |
| simulate_1312 + targeted tests passed | deferred validation | DEFERRED_OWNER_VALIDATION |
| simulate_1312 + all remaining blocked | no local safe work | WAITING_FOR_OWNER_POWERSHELL |
| simulate_1312 read-only inspection | sandbox limitation | SANDBOX_LIMITATION |
| broad scan 1312 fallback | explicit path fallback available | MINOR_SCAN_BLOCKED_RECORUABLE |

## Validation-gate classification table

| condition | status |
| --- | --- |
| targeted tests pass + strict cli blocked by 1312 | DEFERRED_OWNER_VALIDATION |
| repairable failures only | RECOVERABLE_LOCAL |
| forbidden boundary failure | HARD_STOP |

## Report/checkpoint continuation rule

- Missing only report or checkpoint is non-fatal; continue after writing the missing artifact.
- Report with pending hardening and no completion stays in `RECOVERABLE_LOCAL`.
- Contradictory completion markers lead to `EVIDENCE_GAP` repair tasks.

## Owner handoff readiness rule

- `HANDOFF-001`: protected action ready but local work remains -> continue.
- `HANDOFF-002`: local work complete -> `OWNER_HANDOFF_READY`.

## stop every minute prevention law

- Continue for:
  - approved carryover continuation
  - sandbox 1312 on read-only paths
  - broad scan failure when explicit-path fallback exists
  - report/checkpoint mismatch with pending work
  - local fixtures/recovery needs
- Stop only when:
  - forbidden path or staged file
  - wrong branch unrelated work
  - credential/broker/trading/money boundaries
  - all remaining work requires blocked process launch

## Prompt interruption rule

If operator text contains `Explain this codebase`, classify as `PROMPT_INTERRUPTION_IGNORE` and continue active AEE packet.

## do not switch branch while dirty rule

Do not propose or execute branch switching while approved carryover dirty work exists.

## do not propose clean-main start rule

Do not propose clean-main execution as continuation state for this lane.

## Continuation decision tree

1. Check branch. If not `lane/aios-aee-governance-validator-v1`, check if main:
   - if main -> `WRONG_PACKET_FOR_CLEAN_MAIN`.
   - else -> `HARD_STOP`.
2. Check staged files. If present -> `HARD_STOP`.
3. Check forbidden paths. If present -> `HARD_STOP`.
4. Check dirty allowed paths:
   - carryover only -> `APPROVED_CARRYOVER_CONTINUATION`.
   - allowed non-carryover -> `RECOVERABLE_LOCAL`.
5. Evaluate 1312 and validation states.
6. Evaluate report/checkpoint consistency.
7. Return status:
   - `OWNER_HANDOFF_READY` only when local completion is explicit.

## Examples

- Approved carryover:
  - branch: `lane/aios-aee-governance-validator-v1`
  - dirty includes `automation/governance/aios_aee_governance_validator_v1.py`
  - result: `APPROVED_CARRYOVER_CONTINUATION`
- Wrong packet:
  - branch: `main`
  - result: `WRONG_PACKET_FOR_CLEAN_MAIN`
- 1312 deferred:
  - strict cli blocked, targeted tests pass
  - result: `DEFERRED_OWNER_VALIDATION`
- Protected handoff:
  - local tasks complete
  - result: `OWNER_HANDOFF_READY`

## Owner PowerShell handoff policy

Owner handoff remains blocked until all local, safe stopgate work is complete.

## Safety statement

This artifact does not authorize broker/API access.  
This artifact does not authorize credential access.  
This artifact does not authorize trading execution.  
This artifact does not authorize money movement.  
This artifact does not authorize commit/push/merge without explicit Human Owner approval.
