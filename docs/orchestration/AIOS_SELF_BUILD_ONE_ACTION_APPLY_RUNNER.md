# AIOS Self-Build One Action Apply Runner

`automation/orchestration/aios_self_build_one_action_apply_runner.py` previews the final one-action APPLY wrapper for AIOS self-build work. It exists after the approval gate, local APPLY bridge, single-action executor, APPLY result verifier, and one-action execution controller to prove that one bounded command is ready without running it.

It emits:

```text
AIOS_SELF_BUILD_ONE_ACTION_APPLY_RUNNER.v1
```

The runner consumes the selected queue item, APPLY approval result, local APPLY executor bridge, single-action executor, APPLY result verifier, one-action execution controller, execution request, and runner options. It returns runner status, runner mode, selected action, command preview, bounded paths, validators, repair and file-change limits, preflight checks, rejection reasons, next safe action, and safety flags.

## v1 Rules

- The runner never executes `command_to_run`.
- `command_executed` is always `false`.
- `runner_options.execute` defaults to `false`, which produces `runner_mode: DRY_RUN`.
- If `runner_options.execute` is `true`, the runner may return `APPLY_ARMED_NOT_EXECUTED`, but v1 still does not run the command.
- `runner_status` can be `preview_ready` only when `execution_request.requested` is `true`, `execution_request.mode` is `ONE_ACTION_APPLY`, approval is `approved`, the local APPLY bridge is `ready`, the single-action executor is `ready`, `command_would_run` is `true`, the one-action execution controller is `ready`, and the controller allows command execution.
- The selected action must match across the queue item, approval gate, local APPLY bridge, single-action executor, and one-action execution controller.
- `command_to_run` must be present as preview evidence.
- Allowed paths must be bounded relative repo paths.
- Any requested or reported path outside `allowed_paths` is rejected.
- Validators must exist.
- `max_files_changed` must be present and no greater than `5`.
- `max_repairs` must be present and no greater than `1`.
- Any protected action request is rejected.
- If the APPLY result verifier is blocked only because no command has been executed yet, or because post-APPLY validator evidence is unavailable before execution, the runner may still report preview readiness.
- If the verifier is blocked for any other reason, the runner blocks.
- If the verifier fails or rejects, the runner rejects.
- Sandbox `CreateProcessAsUserW failed: 1312` is a local runner blocker, not a code failure.

## Statuses

- `preview_ready`: one bounded APPLY command has safe pre-execution evidence, but the runner still has not executed it.
- `blocked`: required request, approval, bridge, executor, controller, verifier, command preview, or sandbox readiness is missing.
- `rejected`: protected action, path scope, validator, selected-action, or verifier rejection rules failed.

## Modes

- `DRY_RUN`: default mode. The runner previews readiness only.
- `APPLY_ARMED_NOT_EXECUTED`: explicit arm mode when `runner_options.execute` is `true`. v1 still stops before command execution.

## Before Real Execution

Real execution requires a later approved implementation that is outside v1. That future runner must preserve the same bounded queue item, approval evidence, bridge readiness, single-action executor readiness, result verifier handling, one-action controller decision, path limits, validator list, repair/file-change limits, and protected-action blocks before any command can run.

## Safety

The runner does not execute commands, write files, write Reports, mutate queues or approvals, activate schedulers or daemons, dispatch workers, launch Codex, call APIs, access the network, stage, commit, push, merge, use broker access, use credentials, place orders, send webhooks, or perform destructive cleanup.
