# AI_OS Orchestration Consolidation Plan

Date: 2026-05-19

Mode: approved planning only. No orchestration files moved or deleted by this plan.

## Approved Canonical Ownership Defaults

These defaults are approved for planning and future cleanup sequencing only. They do not approve cleanup, file moves, deletes, renames, JSON state mutation, runtime changes, commit, or push.

| Concept | Approved canonical owner | Current safe default |
| --- | --- | --- |
| Root launcher | `aios.ps1` | Keep as root launcher; do not rewrite in cleanup |
| Orchestration | `automation/orchestration/` and `automation/orchestration/README.md` | Keep as canonical orchestration layer |
| Worker registry | `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json` | Keep other registries until dependency review |
| Worker inbox | `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json` | Protect active inbox state |
| Work packets | `automation/orchestration/work_packets/` | Protect active, blocked, and complete packet state |
| Command queue | `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json` | Keep active unless a later packet retires it |
| Approval authority | `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json` and `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json` | Treat as APPLY checkpoint |
| Validator chain | `automation/orchestration/validators/` | Validator output is evidence only |
| Commit package flow | `automation/orchestration/commit_packages/` | No commit/push without explicit approval |
| Operator status display | `automation/orchestration/control/Get-AiOsOperatorControlLoop.DRY_RUN.ps1` | Keep root display scripts until reroute and reference checks pass |
| Runtime/generated state | runtime state under orchestration and `telemetry/runtime/` | Protected evidence until retention policy exists |
| Operator layer | `automation/operator/` | Active launcher/legacy-mixed; do not clean until dependency review |

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

## Approved Canonical Targets

Use one canonical file or folder for each control concept before moving anything:

| Concept | Candidate Canonical Home |
| --- | --- |
| Operator front door | `aios.ps1`; `automation/operator/` remains active launcher/legacy-mixed until dependency review |
| Clean-state gate | `automation/orchestration/clean_state/` |
| Work packets | `automation/orchestration/work_packets/` |
| Worker registry | `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json` |
| Worker profiles | `automation/orchestration/workers/AIOS_WORKER_PROFILES.json` |
| Worker inbox | `automation/orchestration/workers/inbox/` |
| Approval inbox | `automation/orchestration/approval_inbox/` |
| Validator recommendation | `automation/orchestration/validators/` |
| Commit package recommendation | `automation/orchestration/commit_packages/` |
| Locks | `automation/orchestration/locks/` |
| Operator status display | `automation/orchestration/control/Get-AiOsOperatorControlLoop.DRY_RUN.ps1` |

## Consolidation Sequence

1. Freeze new orchestration sprawl.
2. Record approved canonical source-of-truth paths for registry, queue, approval, validator, commit package, and locks.
3. Update docs and display references to point to canonical paths.
4. Convert older root-level examples into fixtures or archive candidates only after references are updated.
5. Collapse duplicate `show-*` scripts into a single operator status command or documented menu.
6. Decide whether root `scripts/` are wrappers, legacy scripts, or active low-level utilities.
7. Move only proven legacy/generated material to `archive/orchestration_legacy` after reference checks.
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

Run a reference update pass before moving files. Cleanup remains blocked until reference checks and validators pass.
