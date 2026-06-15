# AIOS Self-Build DRY_RUN Driver

`aios_self_build_dry_run_driver.py` connects the one-click self-build launcher to the current wake/continue readiness path.

The driver runs:

```powershell
python automation/orchestration/aios_wake_continue.py --goal forex-paper-bot --apply --max-cycles 3 --max-repairs 1 --emit-continuation-controller
```

It intentionally omits `--write-resume-state` and `--write-control-plane-status`, so no Reports output is required by default.

The driver then parses wake JSON, extracts `self_build_loop_readiness`, feeds that status into the self-build autonomy stack v0, and returns one JSON report with wake status, queue selection, packet preview, local apply preview, stop report, SOS policy, `core_status`, `apply_approval`, `local_apply_executor_bridge`, `single_action_executor`, `apply_result_verifier`, `one_action_execution_controller`, `one_action_apply_runner`, `one_action_execute_gate`, `one_action_local_apply_executor`, and next safe action.

Default behavior stops at review. Passing:

```powershell
.\automation\orchestration\Start-AiOsSelfBuild.DRY_RUN.ps1 --preview-approved-scope self-build-core
```

allows preview of one bounded self-build core queue item only. Completed queue items are skipped. Once the status reader, run summary view, APPLY approval gate, approval-gate driver integration, local APPLY executor bridge, single-action executor, apply result verifier, one-action execution controller, one-action APPLY runner, one-action execute gate, and one-action local APPLY executor exist, the next preview item is `build_self_build_one_action_execution_result_collector`.

`core_status` is produced by `AIOS_SELF_BUILD_CORE_STATUS_READER.v1`. It summarizes wake validation, readiness, the selected queue item, packet preview, local apply preview, stop report, and SOS policy. In v0, `core_status.can_apply_without_human` remains `false`.

`apply_approval` is produced by `AIOS_SELF_BUILD_APPLY_APPROVAL_GATE.v1`. Optional CLI arguments can ask the driver to evaluate explicit Anthony approval:

```powershell
.\automation\orchestration\Start-AiOsSelfBuild.DRY_RUN.ps1 --preview-approved-scope self-build-core --approved-by "Anthony Meza" --approval-token "ANTHONY_APPROVED_LOCAL_APPLY" --approve-action integrate_self_build_apply_approval_gate
```

When the approval is valid, `apply_approval.approval_status` may be `approved`, but v0 still does not execute local APPLY. `can_apply_without_human`, `safety.local_apply_executed`, and `safety.generated_commands_executed` remain false.

`local_apply_executor_bridge` is produced by `AIOS_SELF_BUILD_LOCAL_APPLY_EXECUTOR_BRIDGE.v1`. After valid Anthony approval for the selected queue item, it can return `bridge_status: ready` with a prepared `command_to_run`, but `execution_status` remains `prepared_not_executed` and the driver does not run the command.

`single_action_executor` is produced by `AIOS_SELF_BUILD_SINGLE_ACTION_EXECUTOR.v1`. After valid Anthony approval and a ready local apply bridge, it can report `command_would_run: true`, but `command_executed` remains `false` and the driver still does not run the command.

`apply_result_verifier` is produced by `AIOS_SELF_BUILD_APPLY_RESULT_VERIFIER.v1`. In the current DRY_RUN flow, it reports `verifier_status: blocked` with `command_not_executed` and may also report `validators_missing` because no bounded APPLY command has actually run and no post-APPLY validator evidence exists. The driver does not mark post-APPLY verification passed before execution.

`one_action_execution_controller` is produced by `AIOS_SELF_BUILD_ONE_ACTION_EXECUTION_CONTROLLER.v1`. The driver passes explicit preview evidence with `one_action_execution_request.requested: true` and `mode: ONE_ACTION_APPLY` when a queue item is selected. With valid Anthony approval, a ready bridge, a ready single-action executor, and a verifier blocked only by pre-execution evidence gaps, the controller may report `controller_status: ready`, `execution_decision: execute_one_action_allowed`, and `command_execution_allowed: true`. It still reports `command_executed: false`, and the driver still does not execute `command_to_run`.

`one_action_apply_runner` is produced by `AIOS_SELF_BUILD_ONE_ACTION_APPLY_RUNNER.v1`. The driver passes `runner_options.execute: false` by default. With valid Anthony approval, a ready bridge, a ready single-action executor, a ready one-action controller, bounded paths, validators, and verifier state blocked only by pre-execution evidence gaps, the runner may report `runner_status: preview_ready` and `runner_mode: DRY_RUN`. It still reports `command_executed: false` and `commands_executed: false`, and the driver still does not execute `command_to_run`.

`one_action_execute_gate` is produced by `AIOS_SELF_BUILD_ONE_ACTION_EXECUTE_GATE.v1`. The driver passes explicit preview evidence with `execute_gate_request.requested: true`, `mode: EXPLICIT_ONE_ACTION_EXECUTE_GATE`, `approved_by: Anthony Meza`, and `approval_token_present: true` when a queue item is selected. With valid Anthony approval, a ready bridge, ready single-action executor, ready one-action controller, and preview-ready apply runner, the gate may report `gate_status: armed` and `execution_gate_decision: one_action_execution_armed`. It still reports `command_executed: false`, and the driver still does not execute `command_to_run`.

`one_action_local_apply_executor` is produced by `AIOS_SELF_BUILD_ONE_ACTION_LOCAL_APPLY_EXECUTOR.v1`. The driver passes explicit preview evidence with `local_executor_request.requested: true`, `mode: ONE_ACTION_LOCAL_APPLY_EXECUTOR`, `approved_by: Anthony Meza`, and `approval_token_present: true` when a queue item is selected. The driver passes `executor_options.execute: false` by default and does not pass a real `command_runner`. With the full approved gate chain aligned, the executor may report `executor_status: dry_run_ready` and `executor_mode: DRY_RUN`. It still reports `command_executed: false` and `command_returncode: null`, and the driver still does not execute `command_to_run`.

The driver still does not launch Codex, execute local apply commands, mutate queues, mutate approvals, activate a scheduler or daemon, dispatch workers, stage, commit, push, merge, access broker systems, use credentials, place orders, send webhooks, access the network, or delete files.
