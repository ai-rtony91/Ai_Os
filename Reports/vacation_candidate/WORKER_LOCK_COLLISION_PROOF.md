# Worker Lock Collision Proof

Packet ID: VACATION_MODE_WORKER_LOCK_COLLISION_PROOF_APPLY_001
Lane: WORKER_LOCK_AND_STALE_LOCK_PROOF_ONLY
Mode: APPLY proof-only
Branch observed: feature/full-operator-relief-closed-loop-v1
Report date: 2026-06-08

## Purpose

This proof shows how AI_OS vacation-mode worker locks should prevent worker collisions and classify stale locks without launching workers, acquiring production locks, deleting locks, sending notifications, executing ADB, writing runtime telemetry, or touching `main`.

The proof is implemented in `tests/operator_relief/test_vacation_worker_locks.py` using in-memory lock records and worker requests only.

## Existing Lock Evidence

Existing assets inspected:

- `automation/orchestration/lock/Test-AiOsFileLock.ps1`
- `automation/orchestration/lock/Test-AiOsInstanceLock.ps1`
- `automation/orchestration/locks/AIOS_WORKER_LOCK_STATUS.example.json`
- `automation/orchestration/locks/FILE_LOCK_REGISTRY_001.json`
- `automation/orchestration/locks/PATH_CONFLICT_POLICY_001.md`
- `automation/operator_relief/vacation_watchdog.py`
- `automation/operator_relief/packet_queue.py`
- `automation/operator_relief/approval_queue.py`
- `automation/operator_relief/task_classifier.py`
- `automation/operator_relief/notification_gate.py`

These assets establish that path ownership prevents worker collisions, conflicting workers require human review, protected paths carry higher risk, and validators or reports are evidence only.

## Lock Contract Proved

The in-memory proof requires each lock decision to include:

- lane
- worker ID
- worker role
- active/stale status
- protected path scope
- branch or authority-lane scope
- collision status
- stale-lock status
- safe next action
- do-not-wake reason when no SOS exists

## Collision Rules

One worker owns one lane at a time.

Same lane plus active lock plus different worker is a collision. The second worker may not silently take ownership.

Same lane plus same worker plus active lock is an owned continuation, not a collision.

Protected path collisions become SOS-required because they may bypass the protected action gate or cross worker boundaries.

Main branch or merge lane collisions become SOS-required because they create direct main-branch risk.

## Stale Lock Rules

Stale locks are detected by age.

A stale lock does not authorize automatic cleanup, deletion, overwrite, reset, branch switching, commit, push, merge, or worker launch.

Non-protected stale locks below the critical threshold classify as `NON_SOS_ATTENTION`, not `SOS_REQUIRED`.

Protected stale locks or stale locks connected to main/merge authority remain higher risk and require escalation.

## Worker Authority Boundary

Codex CLI and OpenAI CLI may continue only inside their assigned lane and exact approval scope.

Claude Code review-only lanes cannot escalate into authority APPLY lanes.

Night Supervisor can observe and escalate evidence but cannot auto-merge.

Watchtower can classify and wake for SOS but cannot commit, push, or merge.

Anthony remains the only approval authority for protected actions, merge, push, main changes, notification sending, ADB execution, production lock mutation, or additional implementation.

## No-Mutation Boundary

The proof does not:

- acquire real production locks
- delete stale locks
- clean lock files
- launch workers
- send notifications
- execute ADB or `adb.exe`
- write runtime telemetry
- write queue or approval state
- touch `main`
- execute broker, webhook, order, or live trading behavior

## Proof Cases

| Case | Expected result |
|---|---|
| Same lane, active lock, different worker | Collision detected; no silent takeover. |
| Same lane, same worker, active lock | Owned continuation allowed. |
| Same lane, stale lock | Stale lock detected; review required; no auto-clean. |
| Protected path lock collision | `SOS_REQUIRED` or protected escalation. |
| Non-protected stale lock below critical threshold | `NON_SOS_ATTENTION`, not SOS. |
| Main branch or merge lane collision | `SOS_REQUIRED`. |
| Claude Code review-only lock authority attempt | Blocked as SOS/protected escalation. |
| OpenAI/Codex approval bypass attempt | Blocked as SOS/protected escalation. |
| Night Supervisor merge attempt | Observed/escalated; no auto-merge. |
| Watchtower commit/push/merge attempt | SOS classification allowed; git mutation blocked. |
| Lock report safe next action | Present in every report. |
| Lock report do-not-wake reason | Present when no SOS exists. |

## Readiness Impact

This closes the stale-lock/collision proof gap for the vacation watchdog path. It does not replace a future production lock manager. It proves the classification contract needed before longer unattended trials.

Expected impact: full-autonomy readiness can move from approximately 85-87% to approximately 88-89%, with long-duration trial proof still required before 90%.

## Next Safe Action

Run the focused validation chain, then stop. Do not push, merge, open a PR, start a 12-hour trial, mutate production locks, send notifications, execute ADB, or begin another implementation packet.
