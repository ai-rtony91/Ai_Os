# Orchestration C3 Hard-Cut Manifest 001

## DELETE_NEXT_APPLY

Delete candidates count: 0.

No tracked orchestration file is approved for delete in the next APPLY packet. Reference checks found active script readers or historical audit blockers for the obvious duplicate heads, and `automation/orchestration/README.md` still states that current duplicate-brain cleanup evidence identifies zero safe delete candidates.

## ARCHIVE_NEXT_APPLY

Archive candidates count: 1.

| Path | Why it is a duplicate/legacy head | Canonical replacement | Reference search result | Risk level | Proposed action | Rollback note |
|---|---|---|---|---|---|---|
| `automation/orchestration/README_FOLDER_PURPOSE.txt` | Folder-purpose note is lower authority than `automation/orchestration/README.md` and C1 canonical authority docs. | `automation/orchestration/README.md`; `docs/AI_OS/orchestration_consolidation/ORCHESTRATION_CANONICAL_AUTHORITY_DECISION_001.md` | Exact path was not found as an active reader in the targeted C3 reference scan; generic `README_FOLDER_PURPOSE.txt` tooling exists elsewhere. | Low/Medium | Archive in a future APPLY packet only after confirming folder-purpose validators do not require this exact file. | Restore from Git history or archive path if any folder-purpose coverage validator expects it. |

## DO_NOT_TOUCH_RUNTIME

Do-not-touch count: 18.

These files or folders remain blocked from delete/archive because they are runtime-related, actively referenced, unclear, or safety-sensitive.

| Path | Reason |
|---|---|
| `automation/orchestration/approval_inbox.v1.example.json` | Read by `show-approval-inbox-v1.ps1`; referenced by supervisor/runtime preview scripts. |
| `automation/orchestration/packet_queue_ledger.v1.example.json` | Read by `show-packet-queue-ledger.ps1` and `show-worker-registry-v1.ps1`. |
| `automation/orchestration/worker_registry.v1.example.json` | Read by `show-worker-registry-v1.ps1`; referenced by prior source-of-truth audits. |
| `automation/orchestration/validator_routing_supervisor.v1.example.json` | Read by `show-validator-routing-supervisor.ps1`. |
| `automation/orchestration/session_continuity.v1.example.json` | Read by `show-session-continuity.ps1`; referenced by mission-control export. |
| `automation/orchestration/orchestration_status_snapshot.example.json` | Read by `show-orchestration-status.ps1`; referenced by daily snapshot and prior audits. |
| `automation/orchestration/orchestration_spine_v1.example.json` | Read by `show-orchestration-spine.ps1`; contains legacy source metadata. |
| `automation/orchestration/orchestration_gap_ledger.example.json` | Read by `show-orchestration-gaps.ps1`. |
| `automation/orchestration/assignment_locks.example.json` | Read by `show-worker-status.ps1`, `show-dispatcher-queue.ps1`, `sync-worker-registry.ps1`, and `clean_state_gate.ps1`. |
| `automation/orchestration/assignment_locks.v1.example.json` | Read by `show-worker-registry-v1.ps1` and `show-packet-queue-ledger.ps1`. |
| `automation/orchestration/assignment_lock_controller.v1.example.json` | Read by `show-assignment-lock-controller.ps1`. |
| `automation/orchestration/orchestration_control_state.v1.example.json` | Read by `show-orchestration-control-state.ps1`. |
| `automation/orchestration/persistent_worker_supervisor.v1.example.json` | Read by `show-persistent-worker-supervisor.ps1`; prior audits mark active. |
| `automation/orchestration/launch_supervisor.v1.example.json` | Read by `show-launch-supervisor.ps1`; supervisor launch semantics are safety-sensitive. |
| `automation/orchestration/queue_health_supervisor.v1.example.json` | Read by `show-queue-health-supervisor.ps1`; referenced by supervisor and mission-control examples. |
| `automation/orchestration/recovery_bootstrap.example.json` | Referenced by orchestration status/spine metadata and prior audits. |
| `automation/orchestration/recovery_bootstrap_supervisor.v1.example.json` | Referenced by mission-control export and mission-state example. |
| `automation/orchestration/adapters/LEGACY_PACKET_MAPPING.example.json` | Used by adapter tests and normalization examples. |

## ACTIVE_REFERENCE_BLOCKERS

- Root `show-*` scripts still read many root `*.example.json` and `*.v1.example.json` files directly.
- `automation/orchestration/terminal_workstations/` launchers still print commands that invoke root show scripts.
- `automation/orchestration/mission_control/Export-AiOsMissionState.ps1` references queue health, recovery bootstrap supervisor, and session continuity files.
- `automation/orchestration/supervisor/Get-AiOsOvernightSupervisorPlan.DRY_RUN.ps1` references approval inbox and queue health root files.
- `automation/orchestration/runtime/Get-AiOsRuntimeStateBundle.DRY_RUN.ps1` references the root approval inbox v1 example.
- Prior audit docs explicitly mark several root examples and show scripts as KEEP ACTIVE.

## NEXT_APPLY_PACKET_EXACT_FILE_LIST

Recommended next APPLY packet should not delete files yet.

Exact archive candidate for next APPLY, if Human Owner approves after one more targeted validator pass:

- `automation/orchestration/README_FOLDER_PURPOSE.txt`

Exact delete candidate list:

- none

Exact do-not-touch list:

- all files listed under `DO_NOT_TOUCH_RUNTIME`
- all `automation/orchestration/night_supervisor/`
- all `automation/orchestration/runtime/`
- all `automation/orchestration/locks/`
- all `automation/orchestration/memory/`
- all `automation/orchestration/approval_inbox/`

