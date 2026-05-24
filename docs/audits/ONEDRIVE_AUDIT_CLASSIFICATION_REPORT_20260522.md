# AI_OS — OneDrive Audit & Classification Report
**Document Type:** DRY RUN — Pre-Migration Audit  
**Date:** 2026-05-22  
**Author:** AI_OS CTO Infrastructure Layer  
**Scope:** `C:\Users\mylab\OneDrive\AI-OS-Project\`  
**Mode:** READ-ONLY — No files moved, modified, or deleted  
**Status:** AWAITING APPROVAL BEFORE ANY APPLY  

---

## Executive Summary

A full directory scan and governance-compliance read of the OneDrive AI-OS-Project folder has been completed. Six governance documents were read and treated as binding operational doctrine throughout this audit. The folder contains **501 items** across 21 top-level directories. The contamination is significant: operational scripts, live automation, and canonical documentation are all co-mingled in a cloud-sync folder that should contain archives and exports only.

This report classifies every file into five categories, identifies five governance conflicts, and defines the exact migration target for each asset. No apply has occurred. No files have been touched.

---

## Governance Documents Read (Source-of-Truth Constraints)

Before any classification was performed, the following governance files were read in full and treated as binding constraints on every decision in this report:

| Document | Location | Key Rule Extracted |
|---|---|---|
| `AGENTS.md` | OneDrive root | Do not delete, move, rename, or overwrite without backup. DRY_RUN first. |
| `README.md` | OneDrive root | Canonical sources: AGENTS.md, docs\AI_OS\00_START_HERE |
| `RISK_POLICY.md` | OneDrive root | No moves without dry-run, approval, and rollback path |
| `White_Paper.md` | OneDrive root | Governed by AGENTS.md and docs\AI_OS\02_RULES |
| `docs\AI_OS\02_RULES\AIOS_MASTER_RULES.md` | docs tree | 10 core rules including inventory-before-action and backups-before-deletion |
| `docs\AI_OS\02_RULES\AIOS_NO_TOUCH_RULES.md` | docs tree | Blocked: mass delete, mass overwrite, blind merge, moving to GitHub without review |

All classification decisions, move targets, and conflict flags below are derived from these six documents as primary authority.

---

## Governance Conflicts Discovered

These conflicts must be reported before any apply, per AGENTS.md workflow requirement.

### CONFLICT C1 — AIOS_MASTER_RULES Rule 6 vs. Current Compartment Doctrine
**Severity:** 🔴 HIGH  
**Location:** `docs\AI_OS\02_RULES\AIOS_MASTER_RULES.md`, Rule 6  
**Text of conflicting rule:** *"OneDrive is for documents, scripts, reports, and project files."*  
**Conflict:** The new compartment architecture established in this session explicitly classifies OneDrive as archive/export only. Scripts and operational files must leave OneDrive. Rule 6 directly contradicts this.  
**Resolution required:** Rule 6 must be updated in the canonical repo version of AIOS_MASTER_RULES.md to reflect the new three-layer compartment doctrine. The OneDrive copy is considered superseded. Do NOT update the OneDrive copy — update the repo version at `C:\Dev\Ai.Os\docs\AI_OS\02_RULES\AIOS_MASTER_RULES.md` after migration.

---

### CONFLICT C2 — AGENTS.md Lists Stale Canonical Path
**Severity:** 🔴 HIGH  
**Location:** `AGENTS.md`, section "Local Project Path"  
**Text of conflicting field:** `C:\Users\mylab\OneDrive\AI-OS-Project`  
**Conflict:** The canonical repo is `C:\Dev\Ai.Os`. AGENTS.md still points all agents to the OneDrive path as the project root, which is the root cause of the entire contamination problem.  
**Resolution required:** After migration, update `C:\Dev\Ai.Os\AGENTS.md` to set `Local Project Path = C:\Dev\Ai.Os`. The OneDrive copy of AGENTS.md becomes an archive snapshot only.

---

### CONFLICT C3 — Cannot Determine Repo Doc State Without Runtime Comparison
**Severity:** 🟡 MEDIUM  
**Explanation:** This audit cannot verify whether `C:\Dev\Ai.Os\docs\` already contains newer or identical versions of the documents identified for migration. Blind copy would risk overwriting newer repo versions with older OneDrive versions.  
**Resolution:** The migration script must compare file timestamps and checksums at runtime. Any target that already exists in the repo gets the OneDrive version saved with suffix `_ONEDRIVE_COPY_20260522` before any decision is made. No blind overwrites under any circumstance.

---

### CONFLICT C4 — TradingEngineV1 Has Its Own .git Folder
**Severity:** 🟡 MEDIUM  
**Location:** `TradingEngineV1\.git\`  
**Explanation:** TradingEngineV1 is a separate repository nested inside the OneDrive project folder. It must not be migrated into `C:\Dev\Ai.Os`. Moving it would corrupt its git history, create repo-within-repo conflicts, and violate the no-git-history-rewrite rule.  
**Resolution:** TradingEngineV1 is classified as MANUAL REVIEW. It is not touched by any automated migration script.

---

### CONFLICT C5 — 29 AIOS_Stage Scripts — Active Launcher References Unknown
**Severity:** 🟡 MEDIUM  
**Location:** OneDrive root, files `AIOS_Stage3_*.ps1` through `AIOS_Stage31_*.ps1`  
**Explanation:** These 29 scripts were generated by a previous Codex automation session (timestamped May 4). It is unknown whether any active launcher in `C:\Dev\Ai.Os\automation\` still references them by path. Moving them to the repo without checking could silently break a referenced automation chain.  
**Resolution:** The migration script must grep `C:\Dev\Ai.Os\automation\` for any reference to these filenames before moving. If references exist, move + patch. If no references, classify as archive-eligible.  
**This group requires a decision from you before the apply script is written — see Decision Point at end of report.**

---

## Full File Classification

### 🔴 CLASS 1 — Stale Operational Scripts (OneDrive Root)
**What they are:** Active PowerShell automation sitting loose in cloud sync. These violated the compartment rule the moment they were created here.  
**Action:** Move to correct permanent location. Backups taken first.  
**Count:** 43 scripts

#### Subgroup A — AIOS_Stage pipeline scripts (29 files, May 4)
Generated by a Codex automation session. Purpose was repo consolidation/migration planning. Timestamped May 4 — all are pre-current-architecture.

```
AIOS_Stage3_Create_Safe_Zones_v1.ps1
AIOS_Stage4_Register_Current_State_v1.ps1
AIOS_Stage5_Create_Rules_ContextPack_v1.ps1
AIOS_Stage6_Generate_MoveMerge_ReviewPlan_v1.ps1
AIOS_Stage7_Create_Approval_Worksheet_v1.ps1
AIOS_Stage8_Split_Approval_Worksheet_v1.ps1
AIOS_Stage9_Create_NoTouch_Locklist_v1.ps1
AIOS_Stage10_Duplicate_Review_v1.ps1
AIOS_Stage11_Canonical_Archive_Review_v1.ps1
AIOS_Stage12_Folder_Authority_Map_v1.ps1
AIOS_Stage13_Execution_Readiness_Report_v1.ps1
AIOS_Stage14_Rebuild_Full_Folder_Authority_Map_v1.ps1
AIOS_Stage15_Master_Checkpoint_Index_v1.ps1
AIOS_Stage16_Phase2_Folder_Decision_Packet_v1.ps1
AIOS_Stage17_GitHub_Codex_Repo_Review_v1.ps1
AIOS_Stage18_Duplicate_vs_GitHubRepo_Comparison_v1.ps1
AIOS_Stage19_Proposed_Duplicate_Resolution_Plan_v1.ps1
AIOS_Stage20_Archive_Delete_Candidate_Review_v1.ps1
AIOS_Stage21_Final_Human_Approval_Packet_v1.ps1
AIOS_Stage22_Phase2_Checkpoint_Index_v1.ps1
AIOS_Stage23_Phase3_Preflight_Review_v1.ps1
AIOS_Stage24_Hold_Items_Evidence_Snapshot_v1.ps1
AIOS_Stage25_Human_Decision_Guide_v1.ps1
AIOS_Stage26_Approved_Action_Blocker_Audit_v1.ps1
AIOS_Stage27_Phase3_Review_Checkpoint_v1.ps1
AIOS_Stage28_Codex_Handoff_Packet_v1.ps1
AIOS_Stage29_Codex_Allowed_Blocked_Actions_v1.ps1
AIOS_Stage30_Codex_Drive_Scope_Map_v1.ps1
AIOS_Stage31_Codex_Task_Prompt_Checkpoint_v1.ps1
```
**Decision required (A/B/C) — see Decision Point at end of report.**

#### Subgroup B — Migration and inventory scripts (7 files, May 4)
```
AIOS_Controlled_Migration_Final_Verify_v1.ps1
AIOS_Controlled_Migration_Queue_v1.ps1
AIOS_Inventory_Collision_Review_v2.ps1
AIOS_Inventory_Move_NoCollision_v1.ps1
AIOS_Inventory_Only_v1.ps1
AIOS_Prompts_To_ContextPack_Move_v1.ps1
AIOS_UCI_Text_Search_Report_v1.ps1
```
**Target:** `C:\Dev\Ai.Os\automation\` (post-archive review)

#### Subgroup C — Phase workorder scripts (3 files, May 4–13)
```
AIOS_Phase2_Run_Stages19_to_22_ReportOnly_v1.ps1
AIOS_Phase3_Run_Stages24_to_27_ReportOnly_v1.ps1
AIOS_WorkOrder_Stages28_to_31_CodexPrep_ReportOnly_v1.ps1
AIOS_Codex_Launch_v1.ps1
```
**Target:** `C:\Dev\Ai.Os\automation\`

#### Subgroup D — Active control scripts (2 files, May 22)
```
AI_OS_MAIN_CONTROL.ps1      → C:\Dev\Ai.Os\automation\orchestration\
```

#### Subgroup E — Gate scripts (4 files, May 22) — already handled
```
GATE0_EXECUTE.ps1           → D:\AIOS_TERMINAL\scripts\ (via RELOCATE_SCRIPTS.ps1)
GATE0_PROFILE_FINALIZE.ps1  → D:\AIOS_TERMINAL\scripts\ (via RELOCATE_SCRIPTS.ps1)
GATE1_LAZYGIT_INSTALL.ps1   → D:\AIOS_TERMINAL\scripts\ (via RELOCATE_SCRIPTS.ps1)
RELOCATE_SCRIPTS.ps1        → Self-removes after execution
```

#### Subgroup F — scripts\ subfolder scripts (5 files)
```
scripts\Ai_Os_Reorganize.ps1              → C:\Dev\Ai.Os\automation\
scripts\Create-MainControlShortcut.ps1    → C:\Dev\Ai.Os\automation\
scripts\Deployable PS1\deploy_readme.ps1  → C:\Dev\Ai.Os\automation\
scripts\Install-WezTerm.ps1               → D:\AIOS_TERMINAL\scripts\
scripts\start_ai_os.ps1                   → C:\Dev\Ai.Os\automation\
scripts\morning brief\                    → Review
tools\powershell\RUN_SYSTEM_WIZARD_V0_1.ps1 → C:\Dev\Ai.Os\automation\
```

#### Subgroup G — Scratch backup scripts (3 files, May 18)
```
scratch_backups\...\AI_OS_MAIN_CONTROL.ps1       → Archive — do not move
scratch_backups\...\Show-AiOsMainControl.ps1     → Archive — do not move
scratch_backups\...\Update-AiOsSessionState.ps1  → Archive — do not move
```

#### Subgroup H — Staging (1 file)
```
staging\AIOS_profile.ps1  → Remove ONLY after confirming D:\AIOS_TERMINAL\configs\powershell\AIOS_profile.ps1 exists
```

---

### 🟠 CLASS 2 — Canonical Governance Docs (OneDrive Root)
**What they are:** The root governance files that define how AI_OS operates. These are the documents all agents read. They belong version-controlled in `C:\Dev\Ai.Os`.  
**Action:** COPY to repo. Preserve OneDrive copy as archive snapshot. Do NOT delete until repo copy confirmed.

| File | Size | Last Modified | Repo Target |
|---|---|---|---|
| `AGENTS.md` | 3.7 KB | May 4 | `C:\Dev\Ai.Os\AGENTS.md` |
| `README.md` | 631 B | May 5 | `C:\Dev\Ai.Os\README.md` |
| `RISK_POLICY.md` | 822 B | May 5 | `C:\Dev\Ai.Os\RISK_POLICY.md` |
| `White_Paper.md` | 536 B | May 5 | `C:\Dev\Ai.Os\docs\White_Paper.md` |
| `AAR.md` | 473 B | May 5 | `C:\Dev\Ai.Os\docs\AAR.md` |
| `DAILY_REPORT.md` | 478 B | May 5 | `C:\Dev\Ai.Os\docs\DAILY_REPORT.md` |
| `ERROR_LOG.md` | 522 B | May 5 | `C:\Dev\Ai.Os\docs\ERROR_LOG.md` |
| `HALLUCINATION_LOG.md` | 604 B | May 5 | `C:\Dev\Ai.Os\docs\HALLUCINATION_LOG.md` |
| `SOURCE_LOG.md` | 449 B | May 5 | `C:\Dev\Ai.Os\docs\SOURCE_LOG.md` |

**Note:** All of these are listed in AGENTS.md as Critical Files requiring backup before editing. This migration IS the backup. Repo becomes canonical. OneDrive becomes archive snapshot.

---

### 🟠 CLASS 2B — Current-Session Operational Docs (OneDrive Root, May 22)
**What they are:** Documents generated during this session that capture live infrastructure state. Canonical.

| File | Size | Last Modified | Repo Target |
|---|---|---|---|
| `AUDIT_REPORT_TERMINAL_ECOSYSTEM_20260522.md` | 15.5 KB | May 22 | `C:\Dev\Ai.Os\docs\audits\` |
| `RECOVERY_APPLY_REPORT_20260522.md` | 8.1 KB | May 22 | `C:\Dev\Ai.Os\docs\audits\` |
| `CODEX_TERMINAL_MIGRATION_PACKET.txt` | 19.6 KB | May 22 | `C:\Dev\Ai.Os\docs\` |
| `CODEX_FIX_STALE_REPO_REFS.txt` | 6.2 KB | May 22 | `C:\Dev\Ai.Os\docs\` |
| `CODEX_TASK.txt` | 328 B | May 15 | `C:\Dev\Ai.Os\docs\` (verify if still active) |

---

### 🟡 CLASS 3 — Canonical Operational Doc Tree (docs\ folder)
**What they are:** The entire `docs\AI_OS\` subtree is a deeply structured, timestamped operational documentation system. Clearly built as canonical. It belongs version-controlled in the repo.  
**Action:** COPY entire tree to `C:\Dev\Ai.Os\docs\`. Compare timestamps before any overwrite.

| Subfolder | Contents | File Count (approx) | Priority |
|---|---|---|---|
| `docs\AI_OS\00_START_HERE\` | Master index, phase checkpoints, READ_ME_FIRST | 5 | CRITICAL |
| `docs\AI_OS\01_CURRENT_STATE\` | State snapshots (timestamped May 4) | 4 | HIGH |
| `docs\AI_OS\02_RULES\` | MASTER_RULES, NO_TOUCH_RULES, data integrity, checkpoint rules | 5+ | CRITICAL — governance |
| `docs\AI_OS\03_CONTEXT_PACK\` | Codex handoff packets, startup prompts, daily upload order | 8+ | HIGH |
| `docs\AI_OS\04_SCAFFOLD_BLUEPRINT\` | Blueprint, folder tree proposals, file purpose matrix, README | 5 | HIGH |
| `docs\AI_OS\04_INVENTORY\` | Inventory summaries, migration reviews | 4 | MEDIUM |
| `docs\AI_OS\05_SOURCE_LOG\` | Structure maps | 1 | MEDIUM |
| `docs\AI_OS\06_APPROVALS\` | All stage approval gates (required by AIOS_MASTER_RULES) | 10+ | CRITICAL — workflow |
| `docs\AI_OS\07_MOVE_PLANS\` | All stage move plans, hold item evidence | 15+ | HIGH |
| `docs\AI_OS\08_ARCHIVE\` | Stage source backups (.txt) | 8 | MEDIUM |
| `docs\AI_OS\09_REPORTS\` | All stage run reports (27 reports + migration finals) | 30+ | HIGH |
| `docs\AI_OS\system_wizards\` | Context pack docs, agent roles, architecture lock, guardrails | 9 | HIGH |
| `docs\AI_OS\DAILY_CONTEXT_PACK\` | Daily report | 1 | LOW |
| `docs\AI_OS\inventory\` | Inventory summary | 1 | LOW |
| `docs\AI_OS\startup_audit\` | Startup audit + disabled startup backups | 3 | ARCHIVE |
| `docs\AI_OS\_DO_NOT_TOUCH\` | No-touch locklist | 1 | CRITICAL — preserve as-is |

**Additional docs-level files:**

| File | Target |
|---|---|
| `docs\AI-OS_MASTER_GUIDELINES.md` | `C:\Dev\Ai.Os\docs\` |
| `docs\AIOS_TERMINAL_ARCHITECTURE_PLAN.md` | `C:\Dev\Ai.Os\docs\` |
| `docs\LAYER2_IMPLEMENTATION_PLAN.md` | `C:\Dev\Ai.Os\docs\` |
| `docs\PS_PROFILE_MIGRATION_PLAN.md` | `C:\Dev\Ai.Os\docs\` |
| `docs\SITREP_AI_OS_Consolidation_2026-05-02.md` | `C:\Dev\Ai.Os\docs\` |
| `docs\PROFILE_BACKUP_PRE_MIGRATION.ps1` | STAY in OneDrive — this is a backup artifact |

---

### 🟢 CLASS 4 — Legitimate OneDrive Archives (Correct Location — Leave in Place)
**What they are:** These files are correctly placed in cloud storage. They serve as backups, exports, or historical references. They should not be moved.

| File / Folder | Size | Reason to Keep in OneDrive |
|---|---|---|
| `BACKUP_Ai_Os_before_v2_cleanup.zip` | 37 MB | Pre-cleanup full backup — correct in cloud |
| `AlgoTradez_GPT_Sources.zip` | 1.2 MB | External reference archive |
| `12345files.zip` | 15 KB | Archive |
| `files.zip` | 5.4 KB | Archive |
| `Reports_ARCHIVE_DO_NOT_USE\` | — | Already labeled archive — leave in place |
| `scratch_backups\` | — | Timestamped scratch session records |
| `backups\` | — | Backup root folder — correct location |
| `docs\AI_OS\startup_audit\disabled_startup_backups\` | — | CSV startup backups — archive value |
| `docs\AI_OS\08_ARCHIVE\STAGE_SOURCE_BACKUPS\` | — | Script source backups — archive value |
| `docs\PROFILE_BACKUP_PRE_MIGRATION.ps1` | — | Pre-migration profile backup — correct here |
| `logo.icons\` | — | Design assets |
| `00_AI_OS_CONTEXT_PACKET\` | — | Context packet reference — archive/copy target |

---

### 🔵 CLASS 5 — Manual Review Required (Do Not Move Without Decision)
**What they are:** Files or folders where automated classification is unsafe. Human judgment required before any action is taken.

| File / Folder | Issue | Recommended Action |
|---|---|---|
| `TradingEngineV1\` | Contains `.git` — separate repo entirely | DO NOT TOUCH — treat as standalone repo |
| `Ai_Os Node\HTML\` | Legacy UI prototype — unclear if referenced | Review against repo before moving |
| `Ai_Os Robot\` | Appears empty — legacy placeholder | Review and document |
| `_REVIEW\Desktop_Ai_Os_Stale\` | Stale desktop artifacts with JSON configs | Review against current repo state |
| `src\ai_os\system_wizard\` | Source code — needs repo comparison | Diff against repo version before moving |
| `approvals\approved\`, `pending\`, `rejected\` | Active approval workflow | Copy to repo, preserve OneDrive copy |
| `control\` | Mixed: AAR, EOD prompts, MarkDown README | Subfolder-by-subfolder review |
| `daily-progress\` | Daily progress records (May 4) | Archive — copy to repo docs if relevant |
| `backtest_results\` | Trading backtest data | Trading layer — not AI_OS core, separate concern |
| `logs\` | Operational logs | Archive — do not migrate to repo |
| `tools\browser_policy\`, `power_automate\` | Browser + Power Automate tooling | Review purpose before moving |
| `tools\task_scheduler\` | Task scheduler configs | Review before moving |
| `Yubikey\` | Security key material — folder present | DO NOT TOUCH — security adjacent |
| `CODEX_TASK.txt` | May be an active Codex task file | Verify if still active before archiving |
| `fixes_changes\DASHBOARD_FIXES.md` | Dashboard fix notes | Copy to repo docs |
| `scratch_backups\tomorrow_packet_queue_*` | Proposed packet queue JSON | Review — copy if still relevant |

---

## Migration Target Architecture Summary

```
BEFORE (current contaminated state):
  OneDrive\AI-OS-Project\
    ├── AGENTS.md                    ← governance doc in wrong layer
    ├── AIOS_Stage3...Stage31.ps1    ← 29 scripts in wrong layer
    ├── AI_OS_MAIN_CONTROL.ps1       ← launcher in wrong layer
    ├── GATE0_*.ps1, GATE1_*.ps1     ← operational scripts in wrong layer
    ├── docs\AI_OS\                  ← canonical docs in wrong layer
    └── [37 MB backup zip]           ← ✓ correct
    └── [archive folders]            ← ✓ correct

AFTER (target clean state):
  C:\Dev\Ai.Os\                      ← canonical operational truth
    ├── AGENTS.md                    ← governance (migrated, updated)
    ├── README.md                    ← (migrated, updated)
    ├── RISK_POLICY.md               ← (migrated)
    ├── automation\                  ← scripts migrated here
    └── docs\
        ├── AI_OS\                   ← full docs tree migrated
        ├── audits\                  ← audit + recovery reports
        └── White_Paper.md

  D:\AIOS_TERMINAL\                  ← portable terminal layer
    ├── scripts\                     ← Gate scripts (already moved/pending)
    └── configs\                     ← tool configs

  OneDrive\AI-OS-Project\            ← archive and export ONLY
    ├── BACKUP_Ai_Os_*.zip           ← ✓ stays
    ├── Reports_ARCHIVE_DO_NOT_USE\  ← ✓ stays
    ├── scratch_backups\             ← ✓ stays
    ├── backups\                     ← ✓ stays
    └── docs\                        ← becomes archive snapshot only
```

---

## Validation Checklist (Post-Apply)

- [ ] `C:\Dev\Ai.Os` git status returns clean (no broken state from migration)
- [ ] `pwsh` opens and `$env:AIOS_ROOT` is set correctly
- [ ] `$PROFILE` loader stub still resolves to `D:\AIOS_TERMINAL\configs\powershell\AIOS_profile.ps1`
- [ ] `lazygit -p C:\Dev\Ai.Os` opens without error
- [ ] No operational `.ps1` scripts remain in `OneDrive\AI-OS-Project\` root
- [ ] `C:\Dev\Ai.Os\docs\AI_OS\02_RULES\AIOS_MASTER_RULES.md` updated (Rule 6 + Local Path)
- [ ] `C:\Dev\Ai.Os\AGENTS.md` updated (Local Project Path field)
- [ ] All archive/backup files confirmed still in OneDrive
- [ ] `TradingEngineV1\` untouched
- [ ] `Yubikey\` untouched

---

## Rollback Readiness

All migration operations will use Copy-then-remove (not Move) to ensure:

- Source file in OneDrive is not removed until destination write is confirmed
- If destination write fails, source is preserved and error is logged
- OneDrive copies of governance docs remain as archive snapshots — they are never the primary rollback path, but they are present

**Rollback time estimate:** Under 5 minutes. All original files remain on OneDrive until post-migration validation passes.

---

## Decision Point Required Before Apply

**The apply script cannot be written until you answer this:**

**Regarding the 29 AIOS_Stage\*.ps1 scripts in the OneDrive root:**

> **Option A** — Move to `C:\Dev\Ai.Os\automation\legacy\stage_scripts\`  
> Treats them as historical automation — versioned, accessible, but clearly marked legacy.
>
> **Option B** — Archive within OneDrive to `docs\AI_OS\08_ARCHIVE\stage_scripts_20260504\`  
> Keeps them in cloud as historical record. Removes them from the root but keeps them in OneDrive.
>
> **Option C** — Leave in place for now  
> Skip this group entirely in the first migration pass. Tackle separately.

All other classifications are ready to apply on your approval. This is the only open decision.

---

## Required Approval Format

Per AGENTS.md workflow, an approval record is required before any apply. When ready, confirm with:

```
APPROVED: ONEDRIVE_AUDIT_CLASSIFICATION_REPORT_20260522.md
Stage scripts decision: [A / B / C]
```

---

*DRY RUN COMPLETE — 2026-05-22 | AI_OS CTO Infrastructure Layer*  
*No files moved. No files deleted. No files overwritten. Awaiting approval.*
