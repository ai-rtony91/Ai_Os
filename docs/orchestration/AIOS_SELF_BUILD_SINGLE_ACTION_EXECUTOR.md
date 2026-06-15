# AIOS Self-Build Single Action Executor

`automation/orchestration/aios_self_build_single_action_executor.py` is the v1 single-action execution gate for AIOS self-build.

It emits:

```text
AIOS_SELF_BUILD_SINGLE_ACTION_EXECUTOR.v1
```

The executor consumes a selected queue item, apply approval, local APPLY executor bridge, core status, and stop report. It decides whether exactly one bounded local APPLY command would run.

## v1 Rules

- The executor never executes `command_to_run`.
- `command_executed` is always `false`.
- `command_would_run` can be `true` only when approval is `approved`, the local apply bridge is `ready`, selected actions match, allowed paths are bounded, validators exist, and protected actions remain blocked.
- Missing approval returns `blocked`.
- A non-ready bridge returns `blocked`.
- Protected action requests return `rejected`.
- Paths outside allowed scope return `rejected`.
- Missing validators return `rejected`.
- Sandbox `CreateProcessAsUserW failed: 1312` is a local runner blocker, not a code failure.

## Safety

The executor does not execute commands, write files, access the network, launch Codex, call APIs, mutate queues or approvals, activate schedulers or daemons, dispatch workers, stage, commit, push, merge, use broker access, use credentials, place orders, send webhooks, or perform destructive cleanup.
