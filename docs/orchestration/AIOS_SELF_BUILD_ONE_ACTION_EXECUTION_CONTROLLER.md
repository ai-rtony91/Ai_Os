# AIOS Self-Build One Action Execution Controller

`automation/orchestration/aios_self_build_one_action_execution_controller.py` decides whether AIOS is ready to execute exactly one approved bounded local APPLY command.

It emits:

```text
AIOS_SELF_BUILD_ONE_ACTION_EXECUTION_CONTROLLER.v1
```

The controller consumes the selected queue item, APPLY approval result, local APPLY executor bridge, single-action executor, APPLY result verifier, core status, stop report, and an execution request. It returns the controller status, execution decision, selected action, command preview, bounded paths, validators, repair and file-change limits, component statuses, pre-execution checks, rejection reasons, next safe action, and safety flags.

## v1 Rules

- The controller never executes `command_to_run`.
- `command_executed` is always `false`.
- `command_execution_allowed` can be `true` only when `execution_request.requested` is `true`, `execution_request.mode` is `ONE_ACTION_APPLY`, approval is `approved`, the bridge is `ready`, the single-action executor is `ready`, and `command_would_run` is `true`.
- The selected action must match across the queue item, approval gate, local APPLY bridge, and single-action executor.
- Allowed paths must be bounded relative repo paths.
- Any requested or reported path outside `allowed_paths` is rejected.
- Validators must exist.
- Any protected action request is rejected.
- `core_status.can_apply_without_human` must remain `false`.
- If the APPLY result verifier is blocked only because `command_not_executed`, the controller may still report pre-execution readiness.
- If the verifier is blocked for any other reason, the controller blocks.
- If the verifier fails or rejects, the controller rejects.
- Sandbox `CreateProcessAsUserW failed: 1312` is a local runner blocker, not a code failure.

## Statuses

- `ready`: exactly one bounded APPLY command is execution-ready, but still not executed by this controller.
- `blocked`: required request, approval, bridge, executor, verifier, or sandbox readiness is missing.
- `rejected`: protected action, path scope, validator, selected-action, or authority rules failed.

## Safety

The controller does not execute commands, write files, write Reports, mutate queues or approvals, activate schedulers or daemons, dispatch workers, launch Codex, call APIs, access the network, stage, commit, push, merge, use broker access, use credentials, place orders, send webhooks, or perform destructive cleanup.
