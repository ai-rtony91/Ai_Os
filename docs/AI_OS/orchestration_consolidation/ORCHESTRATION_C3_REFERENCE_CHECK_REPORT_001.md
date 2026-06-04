# Orchestration C3 Reference Check Report 001

## Exact Commands Used

```powershell
rg -n "orchestration_spine_v1\.example\.json|orchestration_gap_ledger\.example\.json|orchestration_status_snapshot\.example\.json|README_FOLDER_PURPOSE\.txt|LEGACY_PACKET_MAPPING\.example\.json|approval_inbox\.v1\.example\.json|packet_queue_ledger\.v1\.example\.json|worker_registry\.v1\.example\.json|validator_routing_supervisor\.v1\.example\.json|session_continuity\.v1\.example\.json" automation docs schemas -g "!docs/AI_OS/orchestration_consolidation/**"
```

```powershell
rg -n "show-approval-inbox|show-dispatcher-queue|show-worker-registry|show-validator-chain|show-orchestration|show-session-continuity|show-packet-queue|show-worker-status" automation docs schemas -g "!docs/AI_OS/orchestration_consolidation/**"
```

```powershell
git ls-files automation/orchestration | rg "(orchestration_spine_v1\.example\.json|orchestration_gap_ledger\.example\.json|orchestration_status_snapshot\.example\.json|README_FOLDER_PURPOSE\.txt|LEGACY_PACKET_MAPPING\.example\.json|approval_inbox\.v1\.example\.json|packet_queue_ledger\.v1\.example\.json|worker_registry\.v1\.example\.json|validator_routing_supervisor\.v1\.example\.json|session_continuity\.v1\.example\.json|show-.*\.ps1)$"
```

```powershell
git ls-files automation/orchestration/*.example.json automation/orchestration/*.v1.example.json automation/orchestration/*.txt
```

```powershell
rg -n "assignment_locks\.example\.json|assignment_locks\.v1\.example\.json|assignment_lock_controller\.v1\.example\.json|launch_supervisor\.v1\.example\.json|persistent_worker_supervisor\.v1\.example\.json|queue_health_supervisor\.v1\.example\.json|recovery_bootstrap\.example\.json|recovery_bootstrap_supervisor\.v1\.example\.json|startup_orchestration\.v1\.example\.json|morning_bootstrap\.example\.json|orchestration_control_state\.v1\.example\.json" automation docs schemas -g "!docs/AI_OS/orchestration_consolidation/**"
```

## Summary Of Reference Findings

- Active readers exist for root approval, packet queue, worker registry, validator routing, session continuity, status snapshot, spine, gap ledger, assignment lock, supervisor, and queue-health files.
- Root `show-*` scripts remain registered or referenced in execution registry, terminal workstation launchers, prior audits, and health-summary tools.
- `LEGACY_PACKET_MAPPING.example.json` is still used by adapter tests and normalization evidence.
- Prior archive-pass audits mark several root files as KEEP ACTIVE, which blocks hard delete without a newer reference-retirement APPLY pass.
- `automation/orchestration/README_FOLDER_PURPOSE.txt` is the only narrow archive candidate, but generic folder-purpose tooling exists, so it still needs one final validator pass before archive.

## Active References Blocking Delete

- `automation/orchestration/show-approval-inbox-v1.ps1` -> `approval_inbox.v1.example.json`
- `automation/orchestration/show-packet-queue-ledger.ps1` -> `packet_queue_ledger.v1.example.json`, `assignment_locks.v1.example.json`
- `automation/orchestration/show-worker-registry-v1.ps1` -> `worker_registry.v1.example.json`, `packet_queue_ledger.v1.example.json`, `assignment_locks.v1.example.json`
- `automation/orchestration/show-validator-routing-supervisor.ps1` -> `validator_routing_supervisor.v1.example.json`
- `automation/orchestration/show-session-continuity.ps1` -> `session_continuity.v1.example.json`
- `automation/orchestration/show-orchestration-status.ps1` -> `orchestration_status_snapshot.example.json`
- `automation/orchestration/show-orchestration-gaps.ps1` -> `orchestration_gap_ledger.example.json`
- `automation/orchestration/show-assignment-lock-controller.ps1` -> `assignment_lock_controller.v1.example.json`
- `automation/orchestration/show-persistent-worker-supervisor.ps1` -> `persistent_worker_supervisor.v1.example.json`
- `automation/orchestration/show-launch-supervisor.ps1` -> `launch_supervisor.v1.example.json`
- `automation/orchestration/show-queue-health-supervisor.ps1` -> `queue_health_supervisor.v1.example.json`
- `automation/orchestration/mission_control/Export-AiOsMissionState.ps1` -> queue health, recovery bootstrap supervisor, session continuity
- `automation/orchestration/supervisor/Get-AiOsOvernightSupervisorPlan.DRY_RUN.ps1` -> approval inbox v1 and queue health
- `automation/orchestration/runtime/Get-AiOsRuntimeStateBundle.DRY_RUN.ps1` -> approval inbox v1

## No-Reference Candidates

No delete-ready candidates were found.

Archive candidate requiring one more exact validator check:

- `automation/orchestration/README_FOLDER_PURPOSE.txt`

## Unclear Candidates

- all root `show-*` scripts.
- root supervisor examples.
- root assignment lock examples.
- adapter example outputs.
- mission-control example state.
- session and terminal workstation examples.

These remain unclear because they may be user-facing compatibility surfaces or runtime-preview evidence.

