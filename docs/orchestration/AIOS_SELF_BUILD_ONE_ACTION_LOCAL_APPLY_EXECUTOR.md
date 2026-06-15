# AIOS Self-Build One Action Local APPLY Executor

`automation/orchestration/aios_self_build_one_action_local_apply_executor.py` is the first execution-capable component in the AIOS self-build one-action chain.

It emits:

```text
AIOS_SELF_BUILD_ONE_ACTION_LOCAL_APPLY_EXECUTOR.v1
```

The executor consumes the selected queue item, APPLY approval result, local APPLY executor bridge, single-action executor, one-action execution controller, one-action APPLY runner, one-action execute gate, APPLY result verifier, execution request, local executor request, executor options, and an optional injected command runner.

## v1 Behavior

- v1 defaults to `executor_mode: DRY_RUN`.
- With `executor_options.execute` missing or `false`, the executor can return `executor_status: dry_run_ready` after all gates pass.
- In DRY_RUN, it does not call the injected command runner.
- In DRY_RUN, `command_executed` is `false`, `command_returncode` is `null`, and stdout/stderr previews are empty.
- With `executor_options.execute: true`, execution may happen only through the injected `command_runner` callable.
- The injected runner receives the exact `command_to_run` and working directory.
- v1 does not directly execute commands itself.
- This packet does not run a real local APPLY command.

## Chain Position

The executor sits after:

- `AIOS_SELF_BUILD_APPLY_APPROVAL_GATE.v1`
- `AIOS_SELF_BUILD_LOCAL_APPLY_EXECUTOR_BRIDGE.v1`
- `AIOS_SELF_BUILD_SINGLE_ACTION_EXECUTOR.v1`
- `AIOS_SELF_BUILD_APPLY_RESULT_VERIFIER.v1`
- `AIOS_SELF_BUILD_ONE_ACTION_EXECUTION_CONTROLLER.v1`
- `AIOS_SELF_BUILD_ONE_ACTION_APPLY_RUNNER.v1`
- `AIOS_SELF_BUILD_ONE_ACTION_EXECUTE_GATE.v1`

It requires every upstream component to report the approved, bounded, ready, preview-safe state before it can become `dry_run_ready` or use an injected runner.

## Before Button Execution

Real execution from the button requires a later separately approved integration that injects a controlled runner, captures post-execution evidence, validates changed files, and preserves all protected-action gates. The button must still stop before staging, committing, pushing, merging, broker access, live trading, credentials, orders, webhooks, scheduler activation, daemon activation, worker dispatch, queue mutation, approval mutation, or destructive cleanup.

## Safety

All protected actions remain blocked. The executor does not write Reports, mutate queues or approvals, activate schedulers or daemons, dispatch workers, launch Codex, call APIs, access the network, stage, commit, push, merge, use broker access, use credentials, place orders, send webhooks, or perform destructive cleanup.
