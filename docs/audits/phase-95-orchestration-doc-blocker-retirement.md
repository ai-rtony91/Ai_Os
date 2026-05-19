# Phase 95 Orchestration Doc Blocker Retirement

Date: 2026-05-19
Branch: `phase-95-orchestration-doc-blocker-retirement`
Mode: APPLY, reference retirement only

## Purpose

Retire remaining active-area references to `docs/AI_OS/orchestration` so the folder can be archived later if safe. This phase did not move folders and did not run APPLY scripts.

## Search Scope

Exact references searched:

- `docs/AI_OS/orchestration`
- `docs\AI_OS\orchestration`

Active areas searched:

- `apps`
- `automation`
- `scripts`
- `services`
- `schemas`
- `tests`
- `.github`

## References Retired

PowerShell documentation-path checks and planning references:

- `automation/status/Get-AiOsWorkflowState.DRY_RUN.ps1`
- `automation/orchestration/bootstrap/Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1`
- `automation/orchestration/supervisor/Resolve-AiOsSupervisorAssignment.DRY_RUN.ps1`
- `automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1`

JSON metadata, example, state, and historical packet references:

- `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json`
- `automation/orchestration/commit_packages/COMMIT_PACKAGE_MANIFEST_001.json`
- `automation/orchestration/locks/FILE_LOCK_REGISTRY.example.json`
- `automation/orchestration/operator/AIOS_OPERATOR_RULES.json`
- `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`
- `automation/orchestration/work_packets/complete/20260516-064502-rulebook-foundation.json`

Canonical docs updated:

- `docs/concepts/aios-dispatcher-orchestration-concepts.md`

## Replacement Targets Used

- `docs/concepts/aios-dispatcher-orchestration-concepts.md`
- `docs/architecture/aios-system-architecture.md`
- `docs/workflows/aios-operator-workflows.md`
- `docs/audits/phase-92-dispatcher-orchestration-tree-cleanup.md`
- `docs/audits/phase-93-dispatcher-orchestration-reference-retirement.md`

## Remaining Blockers

One remaining active-area reference was intentionally not changed:

- `automation/orchestration/Run-AiOsOperatorLoop.APPLY.ps1`

Reason: the reference is part of APPLY-mode staging behavior, not documentation-path validation. The phase instructions said not to change unclear live runtime behavior and not to run APPLY scripts.

One remaining historical ledger reference was intentionally not changed:

- `automation/orchestration/reports/COMMIT_PACKAGE_ACTIVITY_LEDGER_001.csv`

Reason: CSV report/ledger edits were not in the allowed edit list. Treat as historical evidence unless a later phase explicitly allows report ledger normalization.

## Move Readiness

`docs/AI_OS/orchestration` is not move-ready yet while the APPLY script path matcher remains pointed at `docs/AI_OS/orchestration`.

If the operator approves a focused follow-up, the next safe cleanup should decide whether `Run-AiOsOperatorLoop.APPLY.ps1` should stage canonical docs paths, archived legacy docs paths, or no docs path by default. After that, run the final active-area scan again and stop before moving the folder.

## Validation Plan

Required validation after edits:

- `git status --short -uall`
- `git diff --stat`
- `git diff --name-status`
- `git diff --check`
- PowerShell parser check for changed `.ps1` files.
- JSON parse check for changed `.json` files.
- Confirm no unauthorized files changed.
- Confirm no delete-only entries.

## Result

Phase 95 retired safe orchestration doc references and left behavior-sensitive or out-of-scope references as blockers.

Push: NO
