> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

\# AGENTS.md



\## Purpose



This file gives Codex and AI coding agents mandatory rules for working on the AI\_OS project.



\## Project Mission



Build a local-first System-Level AI Wizards / AI\_OS project for the OMEN desktop.



AI\_OS is the workshop.  

The forex trading bot is built later on top of AI\_OS.



\## Local Project Path



C:\\Users\\mylab\\OneDrive\\AI-OS-Project



\## GitHub Repository



ai-rtony91/Ai\_Os



\## Absolute Safety Rules



1\. Do not delete files.

2\. Do not move files.

3\. Do not rename files.

4\. Do not overwrite files without a backup.

5\. Do not edit secrets, API keys, credentials, broker tokens, private keys, or recovery keys.

6\. Do not modify Windows registry, BitLocker, BIOS / UEFI, firewall, VPN, browser policies, or security settings.

7\. Do not place broker orders.

8\. Do not enable live trading.

9\. Do not assume missing facts. Mark unknowns as UNKNOWN.

10\. If a report conflicts with File Explorer, screenshots, terminal output, or known project state, mark it INVALID DATA.



\## Required Workflow



Before any automation changes files:



1\. Inspect current files and folders.

2\. Produce a DRY\_RUN report.

3\. Wait for user approval.

4\. Run APPLY mode only after approval.

5\. Create a final report.

6\. Log errors if anything failed.



Default mode must be DRY\_RUN.



\## Critical Files



Back up these files before editing:



README.md  

AGENTS.md  

RISK\_POLICY.md  

SOURCE\_LOG.md  

ERROR\_LOG.md  

HALLUCINATION\_LOG.md  

AAR.md  

DAILY\_REPORT.md  

White\_Paper.md  



\## Documentation Meaning



README.md = project mission  

AGENTS.md = AI behavior rules  

RISK\_POLICY.md = DevOps and trade safety rules  

SOURCE\_LOG.md = where facts came from  

ERROR\_LOG.md = failures, bad data, corrupted code, bad trades  

HALLUCINATION\_LOG.md = suspected wrong claims  

AAR.md = after-action review  

DAILY\_REPORT.md = fixed / changed / errors / mistakes / prevention  



\## AI\_OS vs Trading System



AI\_OS files describe the local system-level wizard, automation rules, policies, folders, logs, and orchestration.



Trading system files describe strategy, broker logic, backtests, paper trades, risk, and trade execution.



Do not mix AI\_OS build files with trading execution files unless the file clearly explains why.



\## Folder Organizer Requirement



Folder organization must use a dry-run plan first.



Specification file:



docs\\AI\_OS\\system\_wizards\\AI\_OS\_FOLDER\_NOTE\_AUTOMATION\_SPEC.txt



Future Python script:



tools\\python\\create\_folder\_purpose\_notes.py



Future PowerShell launcher:



tools\\powershell\\RUN\_FOLDER\_NOTE\_AUTOMATION.ps1



The automation may create README\_FOLDER\_PURPOSE.txt files only where missing and only after a successful DRY\_RUN and user approval.



\## Reporting



Automation reports belong in:



Reports\\daily



Bad data and failed scripts belong in:



ERROR\_LOG.md



Source evidence belongs in:



SOURCE\_LOG.md



Major lessons belong in:



AAR.md



Suspected false AI claims belong in:



HALLUCINATION\_LOG.md



\## Required Agent Output



Every task must report:



Task:  

Files inspected:  

Files created:  

Files changed:  

Dry-run result:  

Errors:  

Unknowns:  

Protected action involved: YES/NO  

Approval required: YES/NO  

Next safe action:  



\## Status



Active rule file for Codex and AI coding agents.


## Report and Mismatch Rules

- Every APPLY or DRY_RUN action must end with a written report summary.
- If observed evidence conflicts with prior notes, mark the conflict as **MISMATCH**.
- If evidence cannot be verified against files, terminal output, or screenshots, mark it as **INVALID DATA**.
- Do not hide mismatches; log them immediately in `ERROR_LOG.md` and summarize them in the current report.
- Unknown facts must be labeled **UNKNOWN** until verified.
- Report summaries must list: Task, Files inspected, Files changed, Dry-run/APPLY result, Errors, Unknowns, and Next safe action.

## Local Folder Role Rules

- **ACTIVE_REPO:** `C:\Dev\Ai.Os`
  Use this only for AI_OS GitHub/Codex/local repo work.
- **PROJECT_ARCHIVE:** `C:\Users\mylab\OneDrive\AI-OS-Project`  
  Use this for OneDrive archive, reports, notes, and non-Git working storage.
- **SEPARATE_PROJECT:** `C:\Users\mylab\OneDrive\AI-OS-Project\TradingEngineV1`  
  This is a separate trading engine project. Do not mix it with AI_OS repo cleanup.
- **HOLD_DO_NOT_USE:** `C:\Users\mylab\OneDrive\GitHub\_HOLD_ai-rtony91_Ai_Os_20260504_131210`  
  Do not work from this folder.
- **WRONG_REMOTE:** `C:\Users\mylab\OneDrive\Desktop\Ai_Os`  
  Do not use this for AI_OS. It was detected as a different GitHub remote.

Do not recommend deleting, moving, or renaming any folders yet.

## Assistant Operating Rules

1. Do not end workflow responses without a next action.
During AI_OS build work, every assistant response should end with one of these:
- exact PowerShell command
- exact Codex prompt
- exact GitHub PR review instruction
- exact verification instruction
- exact save/checkpoint instruction

2. Beginner-guided execution is required.
Provide the exact location, action, expected result, and stop condition.

3. Prefer text output over screenshots.
Use screenshots only when UI state matters or text is unavailable.

4. Avoid unnecessary large technical explanations.
Do not show internal variables, script internals, or long code unless the user must paste or run it.

5. Use momentum-aware pacing.
Slow down at Git, PR review, PowerShell, folder paths, merge, delete, move, rename, push, pull, and authentication steps.

6. Every major phase must end with a checkpoint or daily report instruction.

7. When an error occurs, provide the recovery command and the next instruction immediately.

8. Preserve user control.
Do not automate destructive actions. User must approve merge, push, delete, move, rename, reset, clean, credential/auth changes, and anything touching secrets or trading execution.
