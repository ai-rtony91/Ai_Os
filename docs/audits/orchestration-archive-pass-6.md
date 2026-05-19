# AI_OS Orchestration Cleanup Pass 6 - Archive Legacy Fallbacks Safely

Date: 2026-05-19

Mode: inspect, classify, and report. No files moved. No files deleted. No APPLY scripts run. No push. No merge.

## Result

No legacy orchestration files were archived in this pass.

Reason: every candidate file still has active references in `automation/orchestration`, `docs/AI_OS/orchestration`, `docs/audits`, or related operator/status scripts. Several files are still used as intentional compatibility fallbacks after canonicalization pass 1.

## Files Inspected

Candidate legacy examples:

- `automation/orchestration/packet_queue.example.json`
- `automation/orchestration/packet_queue_ledger.v1.example.json`
- `automation/orchestration/worker_registry.example.json`
- `automation/orchestration/worker_registry.v1.example.json`
- `automation/orchestration/approval_inbox.example.json`
- `automation/orchestration/approval_inbox.v1.example.json`
- `automation/orchestration/validator_chain.example.json`
- `automation/orchestration/validator_routing_supervisor.v1.example.json`
- `automation/orchestration/commit_package.example.json`
- `automation/orchestration/persistent_worker_supervisor.v1.example.json`
- `automation/orchestration/launch_supervisor.v1.example.json`
- `automation/orchestration/queue_health_supervisor.v1.example.json`
- `automation/orchestration/orchestration_status_snapshot.example.json`
- `automation/orchestration/orchestration_spine_v1.example.json`

Root display scripts:

- `automation/orchestration/show-approval-inbox.ps1`
- `automation/orchestration/show-commit-package.ps1`
- `automation/orchestration/show-dispatcher-queue.ps1`
- `automation/orchestration/show-orchestration-status.ps1`
- `automation/orchestration/show-validator-chain.ps1`
- `automation/orchestration/show-worker-status.ps1`

## Classification

| File | Classification | Reason |
| --- | --- | --- |
| `automation/orchestration/packet_queue.example.json` | KEEP FALLBACK FOR NOW | Still referenced by `clean_state_gate.ps1`, `show-dispatcher-queue.ps1`, `show-worker-status.ps1`, `sync-worker-registry.ps1`, status/spine fallback metadata, and current docs. |
| `automation/orchestration/packet_queue_ledger.v1.example.json` | KEEP ACTIVE | Still read by `show-packet-queue-ledger.ps1` and `show-worker-registry-v1.ps1`; also referenced by Phase 16.12 docs. |
| `automation/orchestration/worker_registry.example.json` | KEEP FALLBACK FOR NOW | Still referenced by status/spine fallback metadata and `sync-worker-registry.ps1`; docs still describe it. |
| `automation/orchestration/worker_registry.v1.example.json` | KEEP ACTIVE | Still read by `show-worker-registry-v1.ps1`; also referenced by Phase 16.12 docs. |
| `automation/orchestration/approval_inbox.example.json` | KEEP FALLBACK FOR NOW | Still used by `show-approval-inbox.ps1` as packet-list fallback and by status/spine fallback metadata; docs still describe it. |
| `automation/orchestration/approval_inbox.v1.example.json` | KEEP ACTIVE | Still read by `show-approval-inbox-v1.ps1`; also referenced by launch/startup docs. |
| `automation/orchestration/validator_chain.example.json` | KEEP FALLBACK FOR NOW | Still used by `show-validator-chain.ps1` as fallback and by status/spine fallback metadata; docs still describe it. |
| `automation/orchestration/validator_routing_supervisor.v1.example.json` | KEEP ACTIVE | Still read by `show-validator-routing-supervisor.ps1`; also referenced by Phase 16.14 docs. |
| `automation/orchestration/commit_package.example.json` | KEEP FALLBACK FOR NOW | Still used by `show-commit-package.ps1` fallback and `daily_snapshot/New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1`; docs still describe it. |
| `automation/orchestration/persistent_worker_supervisor.v1.example.json` | KEEP ACTIVE | Still read by `show-persistent-worker-supervisor.ps1`; referenced by Phase 16.15/16 docs. |
| `automation/orchestration/launch_supervisor.v1.example.json` | KEEP ACTIVE | Still read by `show-launch-supervisor.ps1`; referenced by Phase 16.17/20 docs. |
| `automation/orchestration/queue_health_supervisor.v1.example.json` | KEEP ACTIVE | Still read by `show-queue-health-supervisor.ps1`; referenced by mission/supervisor state and Phase 16.14 docs. |
| `automation/orchestration/orchestration_status_snapshot.example.json` | KEEP ACTIVE | Still read by `show-orchestration-status.ps1`; now contains canonical paths plus legacy fallback fields. |
| `automation/orchestration/orchestration_spine_v1.example.json` | KEEP ACTIVE | Still read by `show-orchestration-spine.ps1`; now contains canonical sources plus legacy source metadata. |

## Root Display Script Classification

| File | Classification | Reason |
| --- | --- | --- |
| `automation/orchestration/show-approval-inbox.ps1` | KEEP ACTIVE | Current compatibility display for canonical approval inbox plus legacy packet-list fallback. |
| `automation/orchestration/show-commit-package.ps1` | KEEP ACTIVE | Current compatibility display for canonical commit package recommendation plus legacy package fallback. |
| `automation/orchestration/show-dispatcher-queue.ps1` | KEEP ACTIVE | Current compatibility display for canonical `work_packets/` folder-state counts plus legacy queue fallback. |
| `automation/orchestration/show-orchestration-status.ps1` | KEEP ACTIVE | Main status display still reads `orchestration_status_snapshot.example.json`. |
| `automation/orchestration/show-validator-chain.ps1` | KEEP ACTIVE | Current compatibility display for canonical validator config plus legacy validator chain fallback. |
| `automation/orchestration/show-worker-status.ps1` | KEEP ACTIVE | Current compatibility display for canonical worker registry and work packet folder state. |

## Files Moved

None.

## Files Intentionally Kept

All candidate legacy files were intentionally kept because each one still has active references.

## Old Fallback References Still Present

The required reference scan still finds old references in:

- `automation/orchestration/clean_state_gate.ps1`
- `automation/orchestration/daily_snapshot/New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1`
- `automation/orchestration/orchestration_status_snapshot.example.json`
- `automation/orchestration/orchestration_spine_v1.example.json`
- `automation/orchestration/show-approval-inbox.ps1`
- `automation/orchestration/show-approval-inbox-v1.ps1`
- `automation/orchestration/show-commit-package.ps1`
- `automation/orchestration/show-dispatcher-queue.ps1`
- `automation/orchestration/show-launch-supervisor.ps1`
- `automation/orchestration/show-orchestration-spine.ps1`
- `automation/orchestration/show-orchestration-status.ps1`
- `automation/orchestration/show-packet-queue-ledger.ps1`
- `automation/orchestration/show-persistent-worker-supervisor.ps1`
- `automation/orchestration/show-queue-health-supervisor.ps1`
- `automation/orchestration/show-validator-chain.ps1`
- `automation/orchestration/show-validator-routing-supervisor.ps1`
- `automation/orchestration/show-worker-registry-v1.ps1`
- `automation/orchestration/show-worker-status.ps1`
- `automation/orchestration/sync-worker-registry.ps1`
- related historical docs under `docs/AI_OS/orchestration/`
- audit docs under `docs/audits/`

## Why No File Was Safe To Move

The pass criteria required that a file only move when no current script needs it as a fallback and no active references remain. The scan showed current scripts still use the candidate files either as primary inputs, compatibility fallbacks, or documented validation fixtures. Moving them now would break display scripts or invalidate existing docs before replacement commands are approved.

## Files Safe To Archive In A Later Pass

None are safe today.

Potential future archive candidates after references are removed:

- root `*.example.json` compatibility fallbacks after all display scripts read canonical subfolder paths without fallback
- `show-*-v1.ps1` displays after a single canonical operator status command replaces them
- root supervisor example JSON files after `supervisor/`, `control/`, and `health_summary/` fully replace them

## Validation Commands Run

```powershell
git status --short --branch
git branch --show-current
rg -n "packet_queue\.example\.json|packet_queue_ledger\.v1\.example\.json|worker_registry\.example\.json|worker_registry\.v1\.example\.json|approval_inbox\.example\.json|approval_inbox\.v1\.example\.json|validator_chain\.example\.json|validator_routing_supervisor\.v1\.example\.json|commit_package\.example\.json|persistent_worker_supervisor\.v1\.example\.json|launch_supervisor\.v1\.example\.json|queue_health_supervisor\.v1\.example\.json|orchestration_status_snapshot\.example\.json|orchestration_spine_v1\.example\.json" automation docs scripts aios services
git status --short
git diff --stat
git diff --name-status
git diff --check
git ls-files | Select-String "\.log$"
git ls-files | Select-String "heartbeat"
```

No PowerShell parser check was required for changed `.ps1` files because this pass did not change PowerShell files.

## Risks

- Archive cleanup cannot proceed until fallback references are removed or replaced.
- Historical docs still describe old root examples, so moving files now would make those docs stale.
- Some old examples remain active display fixtures, not just dead files.

## Next Safe Action

Run a Pass 7 reference-reduction task that updates or retires the remaining fallback consumers one group at a time, starting with:

1. `clean_state_gate.ps1`
2. `daily_snapshot/New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1`
3. `show-*-v1.ps1` display scripts
4. historical Phase 16 docs that still validate old root examples
