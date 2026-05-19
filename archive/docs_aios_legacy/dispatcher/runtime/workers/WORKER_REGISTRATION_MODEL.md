# Worker Registration Model

Worker registration creates a traceable runtime identity before a worker claims packets or locks.

## Source Of Truth

Registration status belongs in:

`Reports/dispatcher/runtime/workers/worker_registration_status.json`

## Required Registration Fields

| Field | Purpose |
| --- | --- |
| `worker_id` | Stable worker number. |
| `worker_label` | Human-readable worker label. |
| `launch_session_id` | Unique launch session. |
| `assigned_role` | Worker runtime role. |
| `terminal_window_name` | Visible terminal title. |
| `repo_path` | Confirmed repository path. |
| `branch` | Git branch at registration time. |
| `registration_time` | Registration timestamp. |
| `registration_status` | `REGISTERED`, `BLOCKED`, or `REVIEW_REQUIRED`. |
| `duplicate_identity_status` | Duplicate ID check result. |
| `next_safe_action` | Safe operator instruction. |

## Registration Blocking Rules

Registration blocks when:

- worker ID is already active
- launch session ID is already active
- terminal window name is already active
- repo path is not the canonical AI_OS repo
- recovery state is unresolved
- protected or live trading safety rules are missing

Blocked registration does not auto-close a worker. It marks the session `REVIEW_REQUIRED`.

