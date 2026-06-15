# AIOS Self-Build One Action Execute Gate

`automation/orchestration/aios_self_build_one_action_execute_gate.py` is the final explicit gate before real one-action local APPLY execution can be enabled.

It emits:

```text
AIOS_SELF_BUILD_ONE_ACTION_EXECUTE_GATE.v1
```

The gate consumes the selected queue item, APPLY approval result, local APPLY executor bridge, single-action executor, one-action execution controller, one-action APPLY runner, APPLY result verifier, execution request, and execute-gate request. It returns gate status, execution decision, selected action, command preview, bounded paths, validators, repair and file-change limits, gate checks, rejection reasons, next safe action, and safety flags.

## v1 Rules

- The gate can arm execution readiness, but it never executes `command_to_run`.
- `command_executed` is always `false`.
- `gate_status` can be `armed` only when `execute_gate_request.requested` is `true`, `execute_gate_request.mode` is `EXPLICIT_ONE_ACTION_EXECUTE_GATE`, `execute_gate_request.approved_by` is `Anthony Meza`, and `execute_gate_request.approval_token_present` is `true`.
- A selected queue item must be present.
- APPLY approval must be `approved`.
- The local APPLY bridge must be `ready`.
- The single-action executor must be `ready` and `command_would_run` must be `true`.
- The one-action execution controller must be `ready` and allow command execution.
- The one-action APPLY runner must be `preview_ready` and allow command execution.
- The selected action must match across all components and requests.
- `command_to_run` must be present as preview evidence.
- Allowed paths must be bounded relative repo paths.
- Any requested or reported path outside `allowed_paths` is rejected.
- Validators must exist.
- `max_files_changed` must be present and no greater than `5`.
- `max_repairs` must be present and no greater than `1`.
- Any protected action request is rejected.
- If the APPLY result verifier is blocked only because no command has executed yet, or because validator evidence is unavailable before execution, the gate may still arm.
- If the verifier is blocked for any other reason, the gate blocks.
- If the verifier fails or rejects, the gate rejects.
- Sandbox `CreateProcessAsUserW failed: 1312` is a local runner blocker, not a code failure.

## Why Separate Approval Exists

Earlier self-build components can prove request shape, approval status, bridge readiness, executor readiness, verifier state, controller readiness, and APPLY runner readiness. The execute gate requires a separate explicit request so arming a real execution path cannot happen accidentally from earlier preview evidence.

## Before Actual Execution

Actual execution requires a later separately approved executor implementation outside v1. That future implementation must preserve this gate result, bounded paths, validators, repair and file-change limits, protected-action blocks, and human approval evidence before any command can run.

## Safety

The gate does not execute commands, write files, write Reports, mutate queues or approvals, activate schedulers or daemons, dispatch workers, launch Codex, call APIs, access the network, stage, commit, push, merge, use broker access, use credentials, place orders, send webhooks, or perform destructive cleanup.
