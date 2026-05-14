# Codex Window Snapshot Bootstrap

This document defines a manual morning bootstrap for recreating the AI_OS Codex worker-window setup.

Goal:

Avoid manually naming and arranging worker windows every morning.

The bootstrap is manual-approved. It does not create startup tasks, scheduled tasks, Windows settings changes, APPLY actions, staging, commits, or pushes.

Worker set:

| Worker | Label |
| --- | --- |
| AIOS-01 | ORCHESTRATION CORE |
| AIOS-02 | PACKET LOCK RUNTIME |
| AIOS-03 | RECOVERY HEARTBEATS |
| AIOS-04 | VALIDATOR ROUTING |
| AIOS-05 | APPROVAL COMMIT ROUTING |
| AIOS-06 | STATUS OUTPUTS |
| AIOS-07 | WORKER LAUNCH SUPERVISOR |
| AIOS-08 | QUEUE MONITORING |
| AIOS-09 | REPO SCOUT |
| AIOS-10 | INTEGRATOR MERGER |

Morning flow:

1. Open PowerShell at the repo root.
2. Run `git status --short --branch`.
3. Run the snapshot launcher without `-Launch`.
4. Review the worker list and dirty repo summary.
5. If the list is correct, rerun the launcher with `-Launch`.
6. Each worker reads its window title and next safe action.
7. Workers remain in DRY_RUN until a human approves APPLY.

Snapshot fields:

- `worker_id`
- `worker_label`
- `last_task`
- `last_status`
- `next_safe_action`
- `repo_branch`
- `dirty_files_summary`
- `timestamp`

Safety rules:

- No auto-APPLY.
- No auto-stage.
- No auto-commit.
- No auto-push.
- No startup task.
- No scheduled task.
- No Windows settings changes.
- Dirty repo state is `REVIEW_REQUIRED`.
- Human approval is required before any APPLY, commit, or push.

