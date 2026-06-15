# AIOS Self-Build DRY_RUN Driver

`aios_self_build_dry_run_driver.py` connects the one-click self-build launcher to the current wake/continue readiness path.

The driver runs:

```powershell
python automation/orchestration/aios_wake_continue.py --goal forex-paper-bot --apply --max-cycles 3 --max-repairs 1 --emit-continuation-controller
```

It intentionally omits `--write-resume-state` and `--write-control-plane-status`, so no Reports output is required by default.

The driver then parses wake JSON, extracts `self_build_loop_readiness`, feeds that status into the self-build autonomy stack v0, and returns one JSON report with wake status, queue selection, packet preview, local apply preview, stop report, SOS policy, `core_status`, `apply_approval`, and next safe action.

Default behavior stops at review. Passing:

```powershell
.\automation\orchestration\Start-AiOsSelfBuild.DRY_RUN.ps1 --preview-approved-scope self-build-core
```

allows preview of one bounded self-build core queue item only. Completed queue items are skipped. Once the status reader, run summary view, and APPLY approval gate exist, the next preview item is `integrate_self_build_apply_approval_gate`; after that integration is complete, the queue may preview `build_self_build_local_apply_executor_bridge`.

`core_status` is produced by `AIOS_SELF_BUILD_CORE_STATUS_READER.v1`. It summarizes wake validation, readiness, the selected queue item, packet preview, local apply preview, stop report, and SOS policy. In v0, `core_status.can_apply_without_human` remains `false`.

`apply_approval` is produced by `AIOS_SELF_BUILD_APPLY_APPROVAL_GATE.v1`. Optional CLI arguments can ask the driver to evaluate explicit Anthony approval:

```powershell
.\automation\orchestration\Start-AiOsSelfBuild.DRY_RUN.ps1 --preview-approved-scope self-build-core --approved-by "Anthony Meza" --approval-token "ANTHONY_APPROVED_LOCAL_APPLY" --approve-action integrate_self_build_apply_approval_gate
```

When the approval is valid, `apply_approval.approval_status` may be `approved`, but v0 still does not execute local APPLY. `can_apply_without_human`, `safety.local_apply_executed`, and `safety.generated_commands_executed` remain false.

The driver still does not launch Codex, execute local apply commands, mutate queues, mutate approvals, activate a scheduler or daemon, dispatch workers, stage, commit, push, merge, access broker systems, use credentials, place orders, send webhooks, access the network, or delete files.
