# AI_OS TERMINAL ECOSYSTEM — FULL DIAGNOSTIC AUDIT
**Date:** 2026-05-22  
**Auditor:** Claude (Read-Only / Report-Only mode)  
**Scope:** Windows terminal ecosystem, launcher chain, repo locations, Git worktree state  
**Mode:** ZERO state changes. No files edited. No scripts executed. No registry touched.

---

## EXECUTIVE SUMMARY

The environment has **one root structural problem** that cascades into every other issue:

> **The dead repo path `C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN` is hardcoded across the entire worktree and launcher chain.** That path no longer exists. Everything that points to it is broken or unreachable at launch time.

The canonical target — `C:\Dev\Ai.Os` — is **not accessible via any mounted OneDrive path** and was not auditable from this session. Its existence could not be confirmed from here.

There are **no corrupted files, no encoding issues, no .download/.lnk pollution** in the core repo chain. The problems are structural, not file-level.

---

## SECTION 1 — REPO LOCATION INVENTORY

### 1A. Live Repos Found (OneDrive/GitHub)

| Folder | Type | Status |
|--------|------|--------|
| `GitHub/AIOS_CLAUDE_01` | Git worktree | ⚠️ STALE — `.git` points to dead parent |
| `GitHub/AIOS_CODEX_01` | Git worktree | ⚠️ STALE — `.git` points to dead parent |
| `GitHub/AIOS_CODEX_02` | Git worktree | ⚠️ STALE — `.git` points to dead parent |
| `GitHub/AI_OS_V2_OLD_DO_NOT_USE` | Full git repo | ✅ Real repo — remote: `ai-rtony91/Ai_Os.git` — correctly labelled DO_NOT_USE |
| `GitHub/_HOLD_ai-rtony91_Ai_Os_20260504_131210` | Full git repo | ✅ Real repo — same remote — correctly in HOLD |
| `GitHub/Ai_Os` | Empty folder | ⛔ EMPTY — no `.git`, no content. Shell only. |
| `GitHub/AIOS_LOCAL_SCRATCH_BACKUP` | Folder | Non-git scratch backup |
| `GitHub/aios-worker-*` (12 folders) | Git worktrees | ⚠️ ALL STALE — all `.git` files point to dead parent |

### 1B. The Dead Parent Repo
Every worktree folder (`AIOS_CLAUDE_01`, `AIOS_CODEX_01`, `AIOS_CODEX_02`, all 12 `aios-worker-*` folders) contains a `.git` **file** (not a directory), pointing to:

```
gitdir: C:/Users/mylab/OneDrive/GitHub/ai-rtony91_Ai_Os_CLEAN/.git/worktrees/<name>
```

**`ai-rtony91_Ai_Os_CLEAN` does not exist anywhere on the filesystem.** This means all 15 worktree folders are currently **git-broken** — they cannot run `git status`, `git log`, `git add`, or any git command without a fatal error.

### 1C. Target Canonical Repo
`C:\Dev\Ai.Os` — **not accessible via the OneDrive mount used in this audit session.** Could not confirm existence, git status, or remote. This must be verified manually.

### 1D. Old AI-OS-Project Location
`C:\Users\mylab\OneDrive\AI-OS-Project` is a **non-git project archive** — scripts, reports, docs, backups. It is healthy as a workspace folder. It is NOT a git repo. That is correct per design.

---

## SECTION 2 — POWERSHELL PROFILE AUDIT

| Profile | Path | Status |
|---------|------|--------|
| PS5.1 `Microsoft.PowerShell_profile.ps1` | `Documents\WindowsPowerShell\` | **EXISTS but 0 bytes — EMPTY** |
| PS5.1 `profile.ps1` (AllHosts) | `Documents\WindowsPowerShell\` | NOT FOUND |
| PS7 `Microsoft.PowerShell_profile.ps1` | `Documents\PowerShell\` | NOT FOUND |
| PS7 `profile.ps1` (AllHosts) | `Documents\PowerShell\` | NOT FOUND |
| AllUsers PS5.1 profile | `C:\Windows\System32\WindowsPowerShell\v1.0\` | NOT AUDITABLE (outside mount) |
| AllUsers PS7 profile | `C:\Program Files\PowerShell\7\` | NOT AUDITABLE (outside mount) |

**Findings:**
- No active PowerShell profile is loading any AI_OS paths, environment variables, or launchers. This is clean but also means **no `$env:AIOS_ROOT` or automatic `cd` to canonical repo** is configured.
- PS7 has a `Modules` folder with `Microsoft.PowerToys.Configure 0.99.1.0` — this is a normal PowerToys module, not AI_OS related.
- The empty PS5.1 profile file was last touched **2026-05-17** — likely created intentionally as a placeholder.

---

## SECTION 3 — LAUNCHER CHAIN AUDIT

### 3A. `AI_OS_MORNING.cmd` — **CRITICAL FAILURE**
Found in three repo copies: `AIOS_CLAUDE_01`, `AIOS_CODEX_01`, `AIOS_CODEX_02`

```cmd
@echo off
cd /d C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN
powershell.exe -ExecutionPolicy Bypass -File ".\automation\windows_workstation\Launch-AiOsMorningWorkspace.ps1"
```

**Status: DEAD ON ARRIVAL.** The `cd /d` target does not exist. This command silently fails the directory change, then attempts to run the `.ps1` from whatever the current directory happens to be. **Every morning launch via this CMD file has been failing silently or erroring.**

### 3B. `Launch-PR-Helper.bat` — **STALE**
Found on Desktop in `AI_OS_TOOLS/` and `Ai_Os shortcut tools/`

```cmd
cd /d C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN
```

**Status: STALE.** Same dead path. Would fail immediately on `cd`.

### 3C. `AIOS_Codex_Launch_v1.ps1` — **WORKING but points to wrong repo**
Launches Codex pointed at `C:\Users\mylab\OneDrive\AI-OS-Project` — the archive folder, not a git repo. Codex launched here would have no git context.

### 3D. `start_ai_os.ps1` — **WORKING but points to archive folder**
Opens Explorer windows and PowerShell sessions rooted at `C:\Users\mylab\OneDrive\AI-OS-Project`. Functional for file browsing. Not useful for git work.

### 3E. `AI_OS_MAIN_CONTROL.ps1` — **STALE**
Points to `C:\Users\mylab\OneDrive\GitHub\AIOS_CLAUDE_01` — which is a broken worktree. The script reads clean but the repo it targets cannot run git commands.

### 3F. Desktop `.lnk` files
| Shortcut | Target |
|----------|--------|
| `AI_OS_MAIN_CONTROL.lnk` | Likely points to the `.ps1` above — stale |
| `AI-OS_MORNING_EXECUTION_PACKET.md - Shortcut.lnk` | Points to AI-OS-Project archive |
| `AlgoTradez AI-OS.lnk` | Unknown target — not auditable from this session |
| `AlgoTradez WORKFLOW Launch.lnk` | Unknown target — not auditable from this session |

---

## SECTION 4 — GIT WORKTREE STATE

### The Core Problem (Structural)

The entire worktree family was originally created from a parent repo called `ai-rtony91_Ai_Os_CLEAN`. That parent no longer exists. The result:

```
AIOS_CLAUDE_01/.git  → "gitdir: .../ai-rtony91_Ai_Os_CLEAN/.git/worktrees/AIOS_CLAUDE_01"
AIOS_CODEX_01/.git   → "gitdir: .../ai-rtony91_Ai_Os_CLEAN/.git/worktrees/AIOS_CODEX_01"
AIOS_CODEX_02/.git   → "gitdir: .../ai-rtony91_Ai_Os_CLEAN/.git/worktrees/AIOS_CODEX_02"
aios-worker-* (×12)  → all point to .../ai-rtony91_Ai_Os_CLEAN/.git/worktrees/<name>
```

**All 15 folders are orphaned worktrees.** Any `git` command run inside them will throw:
```
fatal: not a git repository: .../ai-rtony91_Ai_Os_CLEAN/.git/worktrees/<name>
```

### Live Repos with Working Git

| Repo | Remote | Last Commit |
|------|--------|-------------|
| `AI_OS_V2_OLD_DO_NOT_USE` | `github.com/ai-rtony91/Ai_Os.git` | `caef8db` — Merge codex-observability |
| `_HOLD_ai-rtony91_Ai_Os_20260504_131210` | `github.com/ai-rtony91/Ai_Os.git` | `b331181` — PR #1 merge |

Both point to the same GitHub remote. Both are correctly labelled as deprecated/hold.

---

## SECTION 5 — STALE PATH CONTAMINATION IN AIOS_CLAUDE_01

Even though `AIOS_CLAUDE_01` is a broken worktree, its **file contents** are readable. The stale path `C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN` appears in at least **35+ files** across the repo:

### Highest-Risk Stale References (would cause runtime failures)

| File | Type | Nature |
|------|------|--------|
| `automation/operator/Start-AIOSCodexWorkers.*.ps1` (×4) | Script | `$Repo =` hardcoded to dead path |
| `automation/operator/Start-AIOSGovernedWorkerLauncher*.ps1` (×2) | Script | Same |
| `automation/operator/Start-AIOSMultiCodexWorkers.ps1` | Script | Same |
| `automation/operator/AIOS_CORE_WORKER_REGISTRY.v2.json` | Config | `"folder": "ai-rtony91_Ai_Os_CLEAN"` (×3) |
| `automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json` | Config | Full dead path |
| `automation/orchestration/terminal_workstations/AIOS_WORKTREE_LANE_REGISTRY.json` | Config | Dead path in 7 lanes |
| `automation/windows_workstation/AI_OS_MORNING.cmd` | Launcher | Dead `cd /d` target |
| `automation/orchestration/runtime/Invoke-AiOsRuntimePacketAdvancement.ps1` | Script | `$repoRoot =` dead path |
| `automation/orchestration/mission_control/Export-AiOsMissionState.ps1` | Script | `$repoRoot =` dead path |
| `automation/orchestration/terminal_workstations/Show-AiOsLauncherPreflight.ps1` | Script | `$repoPath =` dead path |
| `automation/orchestration/terminal_workstations/Show-AiOsOperatorMenu.ps1` | Script | Same |
| `automation/orchestration/terminal_workstations/Start-AiOsBuildEngine.ps1` | Script | Same |
| `automation/orchestration/bootstrap/Test-AiOsWorkspaceBootstrap.DRY_RUN.ps1` | Script | Asserts dead path |

### Lower-Risk Stale References (example/template files — informational)

| File | Nature |
|------|--------|
| `apps/dashboard/mock-data/*.example.json` | Example data |
| `automation/orchestration/**/*.example.json` | Example configs |
| `automation/operator/startup_reports/WORKER_LAUNCH_REPORT_001.md` | Historical report |
| `automation/operator/legacy_imports/LEGACY_SCRIPT_MIGRATION_QUEUE.md` | Legacy queue doc |

### AGENTS.md — Partially Fixed
`AGENTS.md` line 388 now correctly reads: `C:\Dev\Ai.Os`  
However the rest of the file and all scripts above remain on the old path.

---

## SECTION 6 — WINDOWS TERMINAL

Windows Terminal `settings.json` was **not accessible** from the OneDrive mount. The standard AppData location (`AppData\Local\Packages\Microsoft.WindowsTerminal*`) is under the user's local profile (`C:\Users\mylab\AppData\`) which is not exposed via the current OneDrive mount. This file must be inspected directly.

---

## SECTION 7 — ENVIRONMENT VARIABLES & PATH

No `.ps1` profile files contain `$env:PATH` modifications pointing to AI_OS paths. No `AIOS_ROOT`, `AI_OS_PATH`, or similar environment variables were found in any profile. The PATH is clean from an AI_OS contamination standpoint (as far as accessible files show).

---

## RISK REGISTER

| # | Risk | Severity | Impact |
|---|------|----------|--------|
| R1 | ALL 15 worktree repos are git-broken (dead parent) | 🔴 CRITICAL | No git ops work in any worktree folder |
| R2 | `AI_OS_MORNING.cmd` launches to wrong path silently | 🔴 CRITICAL | Morning workflow launches broken |
| R3 | All `Start-AIOS*` worker launcher scripts point to dead `$Repo` | 🔴 CRITICAL | Multi-worker launch fails on first line |
| R4 | `AIOS_WORKTREE_LANE_REGISTRY.json` — all 7 lanes stale | 🔴 CRITICAL | Orchestration lane routing broken |
| R5 | `C:\Dev\Ai.Os` not auditable — existence unconfirmed | 🟠 HIGH | Canonical target may not exist or may not be a git repo |
| R6 | `AIOS_CLAUDE_01` is a worktree — not a standalone repo | 🟠 HIGH | Cannot be the canonical root; needs a working parent |
| R7 | `Launch-PR-Helper.bat` stale | 🟡 MEDIUM | PR workflow dead |
| R8 | No PowerShell profile configures AIOS_ROOT or repo path | 🟡 MEDIUM | Every session must manually `cd` to repo |
| R9 | Windows Terminal settings.json not audited | 🟡 MEDIUM | Terminal profile paths unknown |
| R10 | `GitHub/Ai_Os` is an empty folder with no git | 🟡 MEDIUM | Misleading — looks like a repo, is nothing |
| R11 | 35+ script/config files in AIOS_CLAUDE_01 still reference dead path | 🟡 MEDIUM | Systematic script failure when these are run |
| R12 | `AIOS_CODEX_LAUNCH_v1.ps1` launches Codex in non-git archive folder | 🟢 LOW | Codex works but has no git context |

---

## SECTION 8 — WHAT IS CLEAN

- No corrupted files detected in any scanned location
- No `.download` or partial files in repo folders
- No encoding anomalies observed
- PS5.1 and PS7 profiles do not load malicious or conflicting paths
- `AGENTS.md` governance rules are well-written and conservative
- `RISK_POLICY.md` and `COMPLIANCE_BASELINE.md` exist and are intact
- `AI_OS_V2_OLD_DO_NOT_USE` and `_HOLD_*` are correctly labelled
- The `AI-OS-Project` archive folder structure is clean and well-organized
- Desktop shortcut folder is messy but contains no dangerous scripts

---

## SECTION 9 — RECOMMENDED NEXT ACTIONS (Ordered)

> These are OBSERVATIONS and RECOMMENDATIONS only. No action taken. All actions require operator approval.

**Step 1 — Confirm `C:\Dev\Ai.Os` exists and is a valid git repo.**  
Open a terminal, run: `git -C "C:\Dev\Ai.Os" status` and `git -C "C:\Dev\Ai.Os" remote -v`  
If it does not exist, create it from `_HOLD_ai-rtony91_Ai_Os_20260504_131210` as the clean baseline.

**Step 2 — Decide: is `AIOS_CLAUDE_01` being retired or repaired?**  
Since it's an orphaned worktree, it cannot be the canonical repo. Options:  
(a) Let it be superseded by `C:\Dev\Ai.Os` (preferred per your stated goal)  
(b) Repair by re-attaching it to a working parent repo

**Step 3 — Update `AI_OS_MORNING.cmd` in all copies.**  
Change `cd /d C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN` to `cd /d C:\Dev\Ai.Os`  
Affected files: `AIOS_CLAUDE_01`, `AIOS_CODEX_01`, `AIOS_CODEX_02` copies

**Step 4 — Update all `Start-AIOS*` launcher scripts `$Repo =` lines.**  
14 files in `automation/operator/` and `automation/orchestration/terminal_workstations/`  
Replace dead path with `C:\Dev\Ai.Os`  
Scope these as a single Codex APPLY workload packet with dry-run gate.

**Step 5 — Update `AIOS_WORKTREE_LANE_REGISTRY.json`.**  
All 7 lane path entries need updating to `C:\Dev\Ai.Os`

**Step 6 — Update `Launch-PR-Helper.bat`.**  
Both Desktop copies need the `cd /d` path updated.

**Step 7 — Add a PS7 profile entry for `$AIOS_ROOT`.**  
Create `Documents\PowerShell\Microsoft.PowerShell_profile.ps1` with:  
`$env:AIOS_ROOT = "C:\Dev\Ai.Os"` and optionally `Set-Location $env:AIOS_ROOT`  
This eliminates manual `cd` on every session open.

**Step 8 — Inspect Windows Terminal settings.json directly.**  
Manually open: `%LOCALAPPDATA%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json`  
Check `startingDirectory` on all profiles for stale paths.

**Step 9 — Delete or repurpose the empty `GitHub/Ai_Os` folder.**  
It is confusing. Either make it the canonical repo clone location or remove it.

---

## APPENDIX — FILESYSTEM LOCATION MAP

```
C:\Users\mylab\OneDrive\
├── GitHub\
│   ├── AIOS_CLAUDE_01\          ← BROKEN worktree (dead parent ref)
│   ├── AIOS_CODEX_01\           ← BROKEN worktree (dead parent ref)
│   ├── AIOS_CODEX_02\           ← BROKEN worktree (dead parent ref)
│   ├── AI_OS_V2_OLD_DO_NOT_USE\ ← Real git repo — correctly labelled DEPRECATED
│   ├── _HOLD_ai-rtony91_*\      ← Real git repo — correctly in HOLD
│   ├── Ai_Os\                   ← EMPTY FOLDER — no git, no content
│   ├── AIOS_LOCAL_SCRATCH_BACKUP\ ← Non-git scratch backup
│   └── aios-worker-* (×12)\    ← ALL BROKEN worktrees (dead parent ref)
│
├── AI-OS-Project\               ← Non-git archive/scripts folder (healthy)
│
└── Desktop\
    ├── AI_OS_TOOLS\             ← Launch-PR-Helper.bat (STALE)
    └── Ai_Os shortcut tools\    ← Mixed shortcuts, AHK files, audit copies

C:\Dev\Ai.Os\                    ← CANONICAL TARGET (NOT AUDITABLE via this session)
```

---

*Report generated: 2026-05-22 | Read-only audit | No files changed | No scripts run*
