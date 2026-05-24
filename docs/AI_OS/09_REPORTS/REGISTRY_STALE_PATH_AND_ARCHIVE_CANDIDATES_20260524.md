# Registry Stale Path and Archive Candidates Report

Date: 2026-05-24
Lane: `audit/registry-stale-paths-archive`
Worker: Codex Agent 4 - Stale Path and Archive Candidate Auditor
Mode: APPLY, report-only

## Executive Summary

This pass found 9 grouped stale-path findings and 8 archive candidates. No immediate delete candidate is recommended from this report-only lane because several legacy-looking files are still referenced by the execution registry, active-system map, fallback compatibility scripts, or historical audit trails.

The highest-risk stale references are CLEAN-era repo tokens and old OneDrive launcher/worktree paths. The active terminal audit already states that `C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN` was a dead repo path hardcoded across the launcher chain, and later recovery evidence shows some launcher `$Repo` values were corrected to `C:\Dev\Ai.Os`. Remaining stale tokens still exist in task generators, work packets, Trading Lab generation scripts, historical reports, and archived telemetry.

The safest next work is not deletion. It is a small PR sequence: first register current owners for ambiguous legacy scripts, then retire fallback references only where canonical orchestration paths are already proven, then archive explicitly legacy operator imports and older launcher variants.

## Search Commands Used

Read-only commands used:

```powershell
Get-Content -Path C:\Dev\Ai.Os\AGENTS.md -TotalCount 260
Get-Content -Path C:\Dev\Ai.Os\README.md -TotalCount 220
if (Test-Path -LiteralPath C:\Dev\Ai.Os\docs\governance\AI_OS_REPO_MEMORY.md) { Get-Content -Path C:\Dev\Ai.Os\docs\governance\AI_OS_REPO_MEMORY.md -TotalCount 220 }
git -C C:\Dev\Ai.Os-agent4-registry-cleanup-report status --short --branch
Test-Path -LiteralPath C:\Dev\Ai.Os-agent4-registry-cleanup-report\docs\AI_OS\09_REPORTS\REGISTRY_STALE_PATH_AND_ARCHIVE_CANDIDATES_20260524.md
rg --files C:\Dev\Ai.Os-agent4-registry-cleanup-report\docs\AI_OS\09_REPORTS
rg -n "REGISTRY_STALE_PATH|STALE_PATH|ARCHIVE_CANDIDATE|archive candidate|stale path" C:\Dev\Ai.Os-agent4-registry-cleanup-report\docs C:\Dev\Ai.Os-agent4-registry-cleanup-report\automation C:\Dev\Ai.Os-agent4-registry-cleanup-report\scripts
rg -n "OneDrive|AI_OS_V2|AIOS_CLAUDE_01|AI-OS-Project|ai-rtony91_Ai_Os_CLEAN|C:\\Users\\mylab" C:\Dev\Ai.Os-agent4-registry-cleanup-report
rg -n "legacy_imports|legacy|backup|stage|launcher|OLD_DO_NOT_USE|superseded|deprecated" C:\Dev\Ai.Os-agent4-registry-cleanup-report\automation C:\Dev\Ai.Os-agent4-registry-cleanup-report\scripts C:\Dev\Ai.Os-agent4-registry-cleanup-report\docs
rg --files C:\Dev\Ai.Os-agent4-registry-cleanup-report\automation\operator\legacy_imports
rg --files C:\Dev\Ai.Os-agent4-registry-cleanup-report\scripts
rg -n "ai-rtony91_Ai_Os_CLEAN|Start-AIOS|AI_OS_MAIN_CONTROL|dead repo path|launcher chain|worker launcher" C:\Dev\Ai.Os-agent4-registry-cleanup-report\automation C:\Dev\Ai.Os-agent4-registry-cleanup-report\scripts C:\Dev\Ai.Os-agent4-registry-cleanup-report\docs\audits\AUDIT_REPORT_TERMINAL_ECOSYSTEM_20260522.md C:\Dev\Ai.Os-agent4-registry-cleanup-report\docs\CODEX_TERMINAL_MIGRATION_PACKET.txt
rg -n "legacyQueuePath|legacyRegistryPath|legacyInboxPath|legacyPackagePath|legacy_validator|legacy_worker|legacy_queue|legacy approval|legacy packet_queue|legacy commit_package" C:\Dev\Ai.Os-agent4-registry-cleanup-report\automation\orchestration
rg -n "Start-AIOSMultiCodexWorkers|Start-AIOSCodexWorkers|Start-AIOSGovernedWorkerLauncher|Start-AiOsMorningOperations|Open-AiOsWorkerWindowLayout|Open-AiOsWorkerSwarm|Open-AiOsWorkerWindow" C:\Dev\Ai.Os-agent4-registry-cleanup-report\automation C:\Dev\Ai.Os-agent4-registry-cleanup-report\scripts C:\Dev\Ai.Os-agent4-registry-cleanup-report\docs
rg -n "write-worker-heartbeat|detect-stale-workers|heartbeat-loop|show-dispatcher-queue|seed-dispatcher-queue|assign-next-queue-item|claim-packet-lock|release-packet-lock" C:\Dev\Ai.Os-agent4-registry-cleanup-report\automation C:\Dev\Ai.Os-agent4-registry-cleanup-report\scripts C:\Dev\Ai.Os-agent4-registry-cleanup-report\docs
rg -n "TradeMode\.LEGACY|AM_workflow\.LEGACY|LEGACY_SCRIPT_MIGRATION_QUEUE|OPERATOR_CONSOLIDATION_STATUS" C:\Dev\Ai.Os-agent4-registry-cleanup-report
rg -l "ai-rtony91_Ai_Os_CLEAN" C:\Dev\Ai.Os-agent4-registry-cleanup-report
rg -l "C:\\Users\\mylab\\OneDrive|C:\\Users\\mylab\\Documents|C:\\Users\\mylab\\AppData|C:\\Users\\mylab\\AI_OS_MAIN_CONTROL" C:\Dev\Ai.Os-agent4-registry-cleanup-report
```

Some PowerShell inventory commands hit a sandbox spawn error and were replaced with `rg --files` or narrower `rg` searches.

## Stale Path Findings

| # | Finding | Evidence | Current owner or likely replacement | Recommendation |
|---|---|---|---|---|
| 1 | Dead CLEAN repo path remains as a stale token. | `docs/audits/AUDIT_REPORT_TERMINAL_ECOSYSTEM_20260522.md` says `C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN` is a dead repo path hardcoded across launcher chain. `rg -l "ai-rtony91_Ai_Os_CLEAN"` still returns active and archive files. | Active repo path authority is `C:\Dev\Ai.Os`; worktree lane uses `C:\Dev\Ai.Os-agent4-registry-cleanup-report`. | REGISTER cleanup owner before edits. |
| 2 | Broken historical worktree references remain in audit evidence. | Terminal audit lists `AIOS_CLAUDE_01`, `AIOS_CODEX_01`, `AIOS_CODEX_02`, and worker folders whose `.git` files pointed to CLEAN-era worktree gitdirs. | Current worktree registry under `automation/orchestration/terminal_workstations/` and current Git worktrees. | KEEP audit evidence; do not treat as live path without verification. |
| 3 | Terminal migration packet preserves obsolete active repo instructions. | `docs/CODEX_TERMINAL_MIGRATION_PACKET.txt` contains `ACTIVE_REPO = C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN` and launcher checks involving `AI_OS_MAIN_CONTROL.ps1`. | Current terminal/workstation authority appears split between `automation/window_identity/`, `automation/windows_workstation/`, and active repo docs. | ARCHIVE or supersede after terminal authority PR. |
| 4 | Goal intake still seeds CLEAN-era repo name. | `automation/intake/Invoke-AiOsGoalIntake.ps1` contains `-Repo "ai-rtony91_Ai_Os_CLEAN"`. | Goal intake should use active repo identity from governance or path registry. | REGISTER for a focused goal-intake fix PR. |
| 5 | Task generator still seeds CLEAN-era repo name. | `automation/orchestration/task_generator/New-AiOsTaskFromNextStep.DRY_RUN.ps1` contains `$repo = "ai-rtony91_Ai_Os_CLEAN"`. | Orchestration task generator should use canonical repo metadata. | REGISTER for orchestration metadata PR. |
| 6 | Active and blocked work packets preserve stale repo tokens. | `automation/orchestration/work_packets/active/*.json` and `blocked/*.json` include `"repo": "ai-rtony91_Ai_Os_CLEAN"`. | Work packet lifecycle under `automation/orchestration/work_packets/`. | KEEP as runtime/evidence unless packet migration is approved. |
| 7 | Trading Lab generation scripts expect the CLEAN root name. | `automation/trading_lab/New-AiOsTradingLab*.ps1` files contain `$ExpectedRootName = "ai-rtony91_Ai_Os_CLEAN"`. | Trading Lab current owner is `apps/trading_lab/` and `automation/trading_lab/`; live broker execution remains blocked. | REGISTER; do not edit in this report lane. |
| 8 | Old OneDrive project paths remain throughout historical inventories and move plans. | `docs/AI_OS/04_INVENTORY`, `05_CLASSIFICATION`, `06_APPROVALS`, `07_MOVE_PLANS`, and `inventory` files contain many `C:\Users\mylab\OneDrive\AI-OS-Project\...` rows. | Archive/migration evidence under `docs/AI_OS` and `archive/ONEDRIVE_SNAPSHOTS_20260522`. | KEEP historical evidence; archive only after authority extraction. |
| 9 | Hardcoded user-profile paths remain in local workstation/terminal docs and shortcut tooling. | `automation/Create-MainControlShortcut.ps1`, `docs/PS_PROFILE_MIGRATION_PLAN.md`, `docs/LAYER2_IMPLEMENTATION_PLAN.md`, and terminal packet references include `C:\Users\mylab\...` paths. | Workstation-local tooling and terminal setup docs. | REGISTER local-machine boundary; not repo-global authority. |

## Legacy / Archive Candidates

| Path | Evidence | Likely replacement/current owner | Risk if kept | Risk if removed | Recommendation |
|---|---|---|---|---|---|
| `automation/operator/legacy_imports/AM_workflow.LEGACY.ps1` | `rg --files` lists it under `legacy_imports`; active system map marks `automation/operator/legacy_imports/` as `ARCHIVE ONLY`; execution registry includes this exact path. | `automation/operator/Start-AiOsMorningOperations.ps1`, `automation/session/Start-AiOsDailyFlow.ps1`, and orchestration runtime flow. | Legacy APPLY behavior may confuse launcher ownership. | Could remove source evidence before operator consolidation is complete. | ARCHIVE |
| `automation/operator/legacy_imports/TradeMode.LEGACY.ps1` | Same `legacy_imports` evidence; execution registry includes exact path. | Paper-only Trading Lab and current operator flow; live broker execution blocked. | Name implies trading mode and may invite unsafe reuse. | Could lose historical context for trading-mode migration. | ARCHIVE |
| `automation/operator/legacy_imports/LEGACY_SCRIPT_MIGRATION_QUEUE.md` | Terminal audit and recovery report call it a legacy queue doc, not a launcher. | Active migration tracking should live in docs/audits or governance queue docs. | Duplicate queue can mislead future cleanup. | Could remove migration notes before absorbed. | ARCHIVE |
| `automation/operator/legacy_imports/OPERATOR_CONSOLIDATION_STATUS.md` | References both `.LEGACY.ps1` files; lives in `legacy_imports`. | `docs/audits/active-system-map.md` and operator consolidation audit docs. | Duplicate status source. | Could lose rationale for consolidation decisions. | ARCHIVE |
| `automation/operator/Start-AIOSCodexWorkers.Conhost.ps1` | Execution registry describes it as an older operator worker launcher candidate; recovery report says `$Repo` was fixed from dead path to `C:\Dev\Ai.Os`. | `automation/orchestration/swarm/Open-AiOsWorkerSwarm.DRY_RUN.ps1` and `automation/orchestration/workers/launcher/Open-AiOsWorkerWindow.DRY_RUN.ps1`. | Older launcher remains available beside current swarm/window launchers. | Could break a manual operator fallback if still used. | ARCHIVE |
| `automation/operator/Start-AIOSCodexWorkers.Positioned.ps1` | Execution registry describes it as older positioned worker launcher candidate; recovery report includes it in fixed launcher set. | Current window identity layout: `automation/window_identity/Open-AiOsWorkerWindowLayout.ps1`. | Duplicate positioned launcher path. | Could remove a layout fallback before window-identity flow is fully accepted. | ARCHIVE |
| `automation/operator/Start-AIOSCodexWorkers.Profile.ps1` | Execution registry describes it as older profile worker launcher candidate; recovery report includes it in fixed launcher set. | Current worker profiles: `automation/orchestration/workers/AIOS_WORKER_PROFILES.json` plus window identity registry. | Parallel profile launcher may diverge from current registry. | Could remove a profile workflow still referenced by operator notes. | ARCHIVE |
| `automation/operator/Start-AIOSGovernedWorkerLauncher.Positioned.ps1` | Execution registry describes positioned governed launcher; recovery report includes it in fixed launcher set. | `automation/window_identity/Open-AiOsWorkerWindowLayout.ps1` and `automation/orchestration/swarm/Open-AiOsWorkerSwarm.DRY_RUN.ps1`. | Maintains a second governed launcher path with similar purpose. | Could remove a still-used operator layout command. | ARCHIVE |

## Delete Candidates

No immediate `DELETE_CANDIDATE` recommendation is made in this pass.

Reason: the legacy-looking files either live under archive/evidence paths, are named in the execution registry, are referenced by active system maps, or preserve migration history. A later delete PR should only follow after owner registration, reference retirement, backup confirmation, and validation.

## Keep-But-Register Candidates

| Path | Evidence | Why keep for now | Registration need | Recommendation |
|---|---|---|---|---|
| `automation/operator/Start-AIOSMultiCodexWorkers.ps1` | Execution registry lists it; terminal audit and recovery report identify it as a worker launcher with prior stale `$Repo` repair. | May still be an operator fallback; active session flow now calls orchestration swarm. | Register whether it is fallback, deprecated, or active. | REGISTER |
| `automation/operator/Start-AIOSGovernedWorkerLauncher.ps1` | Active dependency validation says `automation/operator/startup_reports/` has an active writer from this script; startup report references it. | It still writes evidence and may be active operator tooling. | Register as active, fallback, or archive candidate after dependency check. | REGISTER |
| `automation/operator/worker_queue/` | Active system map marks it `NEEDS USER DECISION`. | Could overlap with orchestration inbox but not proven dead. | Decide whether operator queue survives or migrates into orchestration workers/inbox. | REGISTER |
| `scripts/write-worker-heartbeat.ps1` | Active system map marks it legacy/simple and `NEEDS USER DECISION`; phase-3 dependency validation blocks heartbeat relocation. | Heartbeat ownership is unresolved. | Register heartbeat owner against orchestration worker heartbeat model. | REGISTER |
| `scripts/detect-stale-workers.ps1` | Same active system map section marks it `NEEDS USER DECISION`. | Could still be useful for worker health checks. | Register or replace with orchestration health/status owner. | REGISTER |
| `automation/orchestration/show-dispatcher-queue.ps1` | Archive pass 6 marks it `KEEP ACTIVE`; fallback-removal audits name it in canonicalization work. | Compatibility display still bridges canonical work packets and legacy queue fallback. | Register fallback retirement condition. | KEEP |
| `automation/orchestration/packet_queue.example.json` | Archive pass 6 says `KEEP FALLBACK FOR NOW`; fallback-removal pass identifies it as not yet removable. | Still read by compatibility scripts. | Register final retirement criteria. | KEEP |
| `automation/trading_lab/New-AiOsTradingLab*.ps1` | Stale expected root token remains in Trading Lab APPLY/DRY_RUN generators. | Trading Lab is high-sensitivity, paper-only, and outside this report write boundary. | Register Trading Lab root-name correction under trading safety lane. | REGISTER |

## Recommended Next PRs

1. Registry owner PR: mark legacy operator imports and older launcher variants with explicit active/fallback/archive status in the execution registry.
2. Stale repo-token PR: replace CLEAN-era repo metadata in goal intake, task generator, and Trading Lab generation scripts with canonical repo identity, with Trading Lab safety validation.
3. Work packet migration PR: decide whether active/blocked packet JSON should preserve historical repo tokens or be migrated through a governed packet-state update.
4. Terminal authority PR: supersede `docs/CODEX_TERMINAL_MIGRATION_PACKET.txt` with current terminal/workstation authority or archive it as historical.
5. Operator launcher consolidation PR: retire older `Start-AIOSCodexWorkers*` and positioned governed launcher variants after confirming current swarm/window launchers cover the workflow.
6. Fallback retirement PR: remove legacy queue/registry/inbox/package fallback paths only after `orchestration-fallback-removal-readiness` gates pass.

## Stop Point

Report created only. No registry JSON edited. No scripts edited. No files deleted, moved, staged, committed, pushed, launched, or executed.

Summary counts:

- Stale path findings: 9
- Archive candidates: 8
- Delete candidates: 0
