# AIOS Self-Build Autonomy Stack v0

This stack adds preview-only self-build control tools for AIOS. It prepares the shape of a one-click self-build run while keeping all protected actions blocked.

Included contracts:

- `AIOS_OVERNIGHT_BUILD_CONTROLLER.v1`
- `AIOS_SELF_BUILD_WORK_QUEUE.v1`
- `AIOS_NEXT_ACTION_SELECTOR.v1`
- `AIOS_CODEX_PACKET_FROM_QUEUE.v1`
- `AIOS_BOUNDED_LOCAL_APPLY_RUNNER.v1`
- `AIOS_STOP_REPORT_RESUME.v1`
- `AIOS_SOS_WAKE_POLICY.v1`
- `Start-AiOsSelfBuild.DRY_RUN.ps1`

The v0 stack is DRY_RUN / preview-only. It does not execute commands, launch Codex, call APIs, mutate repo queues, mutate approvals, activate a scheduler or daemon, dispatch workers, stage files, commit, push, merge, touch broker systems, use credentials, submit orders, send webhooks, access the network, or perform destructive cleanup.

The current proof target remains `forex-paper-bot`, with the latest validated Forex chain ending at `forex_paper_session_controller`. Forex feature expansion is paused; these tools are generic self-build readiness infrastructure for future AIOS modes.

## Queue Completion Detection

The self-build work queue is an in-memory preview model. It detects completed items generically: if every path in a queue item's `allowed_paths` already exists in the repo, the item is returned with:

```text
status: completed
reason_code: completed_allowed_paths_exist
```

Completed queue items remain visible for auditability, but the next-action selector skips them because only `ready` items are selectable.

The current self-build-core preview sequence is:

1. `build_self_build_core_status_reader`
2. `build_self_build_run_summary_view`
3. `build_self_build_apply_approval_gate`
4. `integrate_self_build_apply_approval_gate`
5. `build_self_build_local_apply_executor_bridge`
6. `build_self_build_single_action_executor`
7. `build_self_build_apply_result_verifier`
8. `build_self_build_one_action_execution_controller`

The APPLY approval gate evaluates whether explicit Anthony approval matches a selected queue item. It can report `approved`, but v0 still does not execute local APPLY or allow apply without human control.

The local APPLY executor bridge can prepare a `command_to_run` after valid Anthony approval, but it does not execute that command in v1.

The single-action executor can report that one approved bounded command would run, but it does not execute that command in v1.

The apply result verifier checks post-APPLY evidence after execution. In the current DRY_RUN driver flow, execution remains disabled, so verifier readiness is reported as blocked with `command_not_executed`.

The one-action execution controller is the next preview-only self-build-core queue item. It is not built by the queue or driver.

Start command:

```powershell
.\automation\orchestration\Start-AiOsSelfBuild.DRY_RUN.ps1
```

The launcher runs the self-build DRY_RUN driver and forwards explicit arguments when provided.
