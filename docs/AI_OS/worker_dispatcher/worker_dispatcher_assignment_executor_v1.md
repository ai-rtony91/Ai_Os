# AI_OS Worker Dispatcher Assignment Executor DRY_RUN V1

## Purpose

The assignment executor is the next read-only layer on top of Worker Dispatcher
Control Plane V1. It reads current AI_OS worker, queue, lock, approval, work
packet, and PR backlog surfaces, then produces a dispatcher decision report and
non-executable dispatch packet previews.

It does not launch workers, start the scheduler, start Night Supervisor, arm SOS,
call ADB, send notifications, touch broker/cloud/live trading, handle secrets,
commit, push, or merge.

## State Interpretation

- `automation/orchestration/work_packets/active/` is the canonical active work
  packet queue when present.
- `automation/orchestration/queue/DISPATCHER_QUEUE.json` is read but treated as
  `HISTORICAL_REFERENCE` when its status is `HISTORICAL`.
- An empty `automation/orchestration/locks/FILE_LOCK_REGISTRY.json` is valid and
  reports `NO_ACTIVE_LOCKS`.
- `automation/orchestration/approval_inbox/` is the active approval authority
  surface, but completed authority-repair records and pending gates do not
  approve future APPLY.
- Validator PASS is evidence only. It does not approve APPLY, launch, commit,
  push, or merge.
- Anthony remains the only approval authority.

## Output

The executor returns a structured DRY_RUN report with:

- `repo_state`
- `worker_state`
- `queue_state`
- `lock_state`
- `approval_state`
- `work_packet_state`
- `pr_backlog_state`
- `active_state_contracts`
- `collision_findings`
- `recommended_lanes`
- `dispatch_packet_previews`
- `internal_walkie_events`
- `blockers`
- `zero_launch_confirmation`

Dispatch previews are draft-only and do not contain an execution token.
Internal walkie events are also preview-only. They route routine dispatcher
state toward Night Supervisor or Watchdog/Pi5 review by contract, but the
Dispatcher never wakes Anthony directly and never launches workers.
PR backlog state may be read from a local fixture; fixture ingestion is
deterministic and never approves merge, APPLY, or worker launch.

## Next Step

Use this executor as a cockpit input before any later controlled worker launch
lane. Controlled launch remains blocked until queue, locks, approval, validation,
SOS, and scheduler-readiness gates are explicitly proven and approved.
