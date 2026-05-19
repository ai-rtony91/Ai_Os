# AI_OS Orchestration Consolidation Plan

Date: 2026-05-19

Mode: planning only. No orchestration files moved or deleted by this plan.

## Problem

`automation/orchestration` remains the largest active cleanup target after reports and Trading Lab documentation were moved to archive. It contains 250 tracked files and mixes dispatcher, approval, worker registry, queue, validator, supervisor, terminal UI, Git/PR gate, health, recovery, and control-panel concepts.

This creates a multiple-brains risk: several files appear to represent the same kind of runtime truth.

## Current Evidence

Tracked files under `automation/orchestration`: 250.

Largest subareas observed:

| Count | Area |
| ---: | --- |
| 21 | `automation/orchestration/workers` |
| 16 | `automation/orchestration/terminal_workstations` |
| 14 | `automation/orchestration/validators` |
| 12 | `automation/orchestration/bootstrap` |
| 11 | `automation/orchestration/work_packets` |
| 9 | `automation/orchestration/supervisor` |
| 7 | `automation/orchestration/locks` |
| 6 | `automation/orchestration/adapters` |
| 6 | `automation/orchestration/commit_packages` |
| 5 | `automation/orchestration/compliance` |
| 5 | `automation/orchestration/mission_control` |
| 5 | `automation/orchestration/reports` |

Reference search showed active references to the old root example files:

- `packet_queue.example.json`
- `worker_registry.example.json`
- `approval_inbox.example.json`
- `orchestration_spine_v1.example.json`
- `show-orchestration-status.ps1`

Reference search also showed newer registry paths under:

- `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`
- `automation/orchestration/workers/WORKER_REGISTRY.json`
- `automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json`

Because these references exist, moving files to `archive/orchestration_legacy` tonight would be premature.

## Proposed Canonical Targets

Choose one canonical file or folder for each control concept before moving anything:

| Concept | Candidate Canonical Home |
| --- | --- |
| Operator front door | `aios.ps1` plus `automation/operator/` |
| Clean-state gate | `automation/orchestration/clean_state/` |
| Work packets | `automation/orchestration/work_packets/` |
| Worker registry | `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json` |
| Worker profiles | `automation/orchestration/workers/AIOS_WORKER_PROFILES.json` |
| Worker inbox | `automation/orchestration/workers/inbox/` |
| Approval inbox | `automation/orchestration/approval_inbox/` |
| Validator recommendation | `automation/orchestration/validators/` |
| Commit package recommendation | `automation/orchestration/commit_packages/` |
| Locks | `automation/orchestration/locks/` |
| Operator status display | one approved `show-*` index or `automation/orchestration/control/` |

## Consolidation Sequence

1. Freeze new orchestration sprawl.
2. Approve canonical source-of-truth paths for registry, queue, approval, validator, commit package, and locks.
3. Update docs to point to canonical paths.
4. Convert older root-level examples into fixtures or archive candidates only after references are updated.
5. Collapse duplicate `show-*` scripts into a single operator status command or documented menu.
6. Decide whether root `scripts/` are wrappers, legacy scripts, or active low-level utilities.
7. Move only proven legacy/generated material to `archive/orchestration_legacy`.
8. Run clean-state and validator checks before any commit.

## Do Not Move Yet

Do not move these until references are updated and reviewed:

- `automation/orchestration/packet_queue.example.json`
- `automation/orchestration/worker_registry.example.json`
- `automation/orchestration/approval_inbox.example.json`
- `automation/orchestration/orchestration_spine_v1.example.json`
- `automation/orchestration/show-orchestration-status.ps1`
- `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`
- `automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json`

## Safe Cleanup Candidates

Candidates for later archive only after reference checks:

- duplicate `.example.json` state snapshots at the orchestration root
- duplicate v1 example files when a canonical version exists
- CSV activity ledgers under `automation/orchestration/reports/`
- root-level `show-*` display scripts that are superseded by a canonical operator status menu
- old queue and registry examples once canonical queue/registry paths are chosen

## Validation For Any Future Orchestration Cleanup

Run:

```powershell
git status --short
git diff --stat
git diff --name-status
git ls-files automation/orchestration | Measure-Object
rg -n "moved-file-name-or-path" .
git diff --check
```

Also confirm:

- no broker/OANDA/live trading/webhook/secrets files touched
- no active app source touched
- no `git add .`
- no commit or push without MAIN CONTROL approval

## Next Safe Action

Approve a source-of-truth map for orchestration before moving files.
