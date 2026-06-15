# AIOS Self-Build DRY_RUN Driver

`aios_self_build_dry_run_driver.py` connects the one-click self-build launcher to the current wake/continue readiness path.

The driver runs:

```powershell
python automation/orchestration/aios_wake_continue.py --goal forex-paper-bot --apply --max-cycles 3 --max-repairs 1 --emit-continuation-controller
```

It intentionally omits `--write-resume-state` and `--write-control-plane-status`, so no Reports output is required by default.

The driver then parses wake JSON, extracts `self_build_loop_readiness`, feeds that status into the self-build autonomy stack v0, and returns one JSON report with wake status, queue selection, packet preview, local apply preview, stop report, SOS policy, and next safe action.

Default behavior stops at review. Passing:

```powershell
.\automation\orchestration\Start-AiOsSelfBuild.DRY_RUN.ps1 --preview-approved-scope self-build-core
```

allows preview of one bounded self-build core queue item only. It still does not launch Codex, execute local apply commands, mutate queues, mutate approvals, activate a scheduler or daemon, dispatch workers, stage, commit, push, merge, access broker systems, use credentials, place orders, send webhooks, access the network, or delete files.
