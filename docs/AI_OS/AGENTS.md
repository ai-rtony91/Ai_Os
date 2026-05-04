# AI_OS Agent Rules

## Scope
This file controls AI behavior for the AI_OS documentation area.

## Locked Architecture
The OMEN desktop is the local command/control foundation for AI_OS.

AI tools must work underneath the system-level AI_OS architecture, not replace it.

Codex integration is part of the AI_OS build path.

GitHub is the source-control layer.

This structure is locked unless a newer development method clearly improves the build.

## Agent Roles
ChatGPT is the architect, planner, documentation controller, and troubleshooting guide.

Codex is the repository/code implementer.

Claude Code is the secondary reviewer, refactor tool, and codebase surgeon.

GitHub is the version-control source of truth.

The user remains the execution authority.

## Operating Rules
Do not overwrite existing files without backup.

Do not generate multiple scripts at once unless explicitly requested.

Use beginner-safe steps.

Use exact paths.

Prefer one action at a time.

Stop after major changes and request confirmation.

Document major architecture changes in CURRENT_STATE, CHECKPOINT, CHANGELOG, and ARCHITECTURE records.

## Current Priority
Connect Codex to the GitHub repo and keep the AI_OS architecture aligned with the OMEN-first local system design.
## Report and Mismatch Rules

- Every APPLY or DRY_RUN action must end with a written report summary.
- If observed evidence conflicts with prior notes, mark the conflict as **MISMATCH**.
- If evidence cannot be verified against files, terminal output, or screenshots, mark it as **INVALID DATA**.
- Do not hide mismatches; log them immediately in `ERROR_LOG.md` and summarize them in the current report.
- Unknown facts must be labeled **UNKNOWN** until verified.
- Report summaries must list: Task, Files inspected, Files changed, Dry-run/APPLY result, Errors, Unknowns, and Next safe action.

## Local Folder Role Rules

- **ACTIVE_REPO:** `C:\Users\mylab\OneDrive\GitHub\ai-rtony91_Ai_Os_CLEAN`  
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
