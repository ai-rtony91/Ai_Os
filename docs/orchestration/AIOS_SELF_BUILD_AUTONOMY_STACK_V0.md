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

Start command:

```powershell
.\automation\orchestration\Start-AiOsSelfBuild.DRY_RUN.ps1
```

The launcher runs only the overnight build controller in `DRY_RUN` mode and forwards explicit arguments when provided.
