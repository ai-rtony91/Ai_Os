# Worker Dispatcher Internal Walkie Event Contract V1

## Purpose

The Worker Dispatcher Assignment Executor emits internal walkie events so routine
routing state can be reviewed by the Night Supervisor and Watchdog/Pi5 without
waking Anthony directly.

The operating model is:

```text
Workers -> Dispatcher -> Night Supervisor -> Watchdog/Pi5 -> Anthony only if needed
```

Dispatcher is the traffic-control radio. Night Supervisor is the shift-lead
radio. Watchdog/Pi5 is the emergency walkie to Anthony.

## Event Fields

Each event contains:

- `walkie_event_id`
- `event_type`
- `severity`
- `route_to`
- `source`
- `reason`
- `candidate_id`
- `lane`
- `requires_anthony`
- `safe_next_action`
- `blocked_actions`
- `evidence`
- `zero_external_wake_confirmation`
- `zero_worker_launch_confirmation`

## Event Types

- `DISPATCH_READY`
- `DRY_RUN_ONLY`
- `WAITING_APPROVAL`
- `LOCK_COLLISION`
- `PR_DEPENDENCY_CHANGED`
- `PROTECTED_PATH_BLOCKED`
- `QUEUE_STATE_UNKNOWN`
- `APPROVAL_STATE_UNKNOWN`
- `NO_SAFE_LANE_FOUND`
- `SOS_CANDIDATE`
- `REVIEW_REQUIRED`

## Severity And Routing

- `INFO` routes to `dispatcher_report`.
- `NOTICE` routes to `night_supervisor_review`.
- `ACTION_REQUIRED` routes to `night_supervisor_review` and
  `approval_inbox_evidence`.
- `SAFETY_BLOCK` routes to `night_supervisor_review` and `watchdog_review`.
- `SOS_CANDIDATE` routes to `watchdog_pi5_review`.

## Direct Wake Rule

Dispatcher never wakes Anthony directly. It may set `requires_anthony` to `true`
as a recommendation, but Watchdog/Pi5 remains the external wake gate.

Every event keeps:

- `zero_external_wake_confirmation: true`
- `zero_worker_launch_confirmation: true`

Events are preview-only. They do not send notifications, arm SOS, call ADB, start
Night Supervisor, start scheduler paths, launch workers, approve APPLY, or touch
broker/cloud/live trading paths.
