# Reports Storage Policy (Hybrid)

## Purpose

This policy defines what report artifacts are stored in GitHub versus archive-only storage.

## GitHub (tracked)

Track curated, reviewable markdown artifacts in GitHub, including:

- Curated markdown summaries
- Checkpoints
- Mismatch reports
- Incident summaries
- Policy documents

## OneDrive archive-only (not tracked in GitHub)

Keep raw and bulky report artifacts in OneDrive archive-only storage, including:

- Raw inventory dumps
- Full filesystem scans
- Bulky logs
- Host-specific TXT exports

## Raw data exception handling

If raw report data is needed in GitHub context, do **not** commit the raw dump.
Commit a short, sanitized markdown summary instead.

## Enforcement via `.gitignore`

The repository should ignore raw report artifact patterns such as inventory and dry-run TXT dumps under `Reports/daily`.

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
