# AIOS Self-Build Local APPLY Executor Bridge

`automation/orchestration/aios_self_build_local_apply_executor_bridge.py` prepares a local APPLY execution plan for an approved self-build queue item.

It emits:

```text
AIOS_SELF_BUILD_LOCAL_APPLY_EXECUTOR_BRIDGE.v1
```

The bridge consumes a selected queue item, local apply preview, apply approval result, core status, and stop report. It returns the selected action, working directory, command to run, allowed paths, validators, repair and file-change limits, approval state, execution status, rejection reasons, next safe action, and safety flags.

## v1 Rules

- Approval must already be `approved`.
- `local_allowlisted_apply_allowed` must be `true`.
- The selected action must match the queue action.
- Preview paths must stay inside queue `allowed_paths`.
- Validators must be present.
- Protected action requests are rejected.
- If all gates pass, the bridge returns `ready` with `command_to_run`.
- `command_to_run` is never executed in v1.
- Sandbox `CreateProcessAsUserW failed: 1312` is a local runner blocker, not a code failure.

## Safety

The bridge does not execute commands, write files, write Reports, mutate queues or approvals, launch Codex, call APIs, access the network, activate schedulers or daemons, dispatch workers, stage, commit, push, merge, use broker access, use credentials, place orders, send webhooks, or perform destructive cleanup.
