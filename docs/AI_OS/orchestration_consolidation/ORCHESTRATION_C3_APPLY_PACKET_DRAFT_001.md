# C3 Apply Packet Draft: Delete/Archive Confirmed Heads

```text
CODEX-ONLY PROMPT

AI_OS BOOTSTRAP REQUIRED: YES
AI_OS EXECUTION TOKEN: START_THIS_CODEX_TASK

IDENTITY MARKER
AI_OS_ORCHESTRATION_C4_APPLY_ARCHIVE_CONFIRMED_HEADS

SUPERVISOR IDENTITY
AI_OS_MANAGER_CONTROL

PACKET ID
AIOS-ORCH-C4-APPLY-ARCHIVE-CONFIRMED-HEADS-001

TITLE
C4 - APPLY Archive Confirmed Legacy Orchestration Head

LANE
APPLY archive lane

MODE
APPLY

ZONE
AI_OS_ORCHESTRATION_CONTROL_LAYER

WORKER IDENTITY
Codex orchestration archive worker

WORKTREE
C:\Dev\Ai.Os

BRANCH
main

APPROVAL AUTHORITY
Human approval required before APPLY. This draft is not approval.

MISSION
Archive only the confirmed ARCHIVE_NEXT_APPLY file from the C3 manifest. Delete no files.

PRECHECK
1. git status --short --branch
2. Confirm branch is main.
3. Confirm working tree is clean.
4. Confirm C3 manifest is on main.
5. Confirm no active locks.
6. Confirm target file still exists:
   automation/orchestration/README_FOLDER_PURPOSE.txt
7. Run exact reference check for the target file.
8. STOP if any active runtime or validator dependency is found.

ALLOWED PATHS
- automation/orchestration/README_FOLDER_PURPOSE.txt
- archive/orchestration_legacy/
- docs/AI_OS/orchestration_consolidation/

FORBIDDEN PATHS
- automation/orchestration/night_supervisor/
- automation/orchestration/runtime/
- automation/orchestration/locks/
- automation/orchestration/memory/
- automation/orchestration/approval_inbox/
- telemetry/
- control/
- broker/
- OANDA files
- live trading files
- Pi GPIO/motor files
- secret files
- .env files
- package files
- dashboard UI files

DO
1. Archive only:
   automation/orchestration/README_FOLDER_PURPOSE.txt
2. Delete no files.
3. Preserve file history through git move if approved.
4. Validate no runtime files touched.
5. Stop before push.

DO NOT
Delete files.
Move any file not explicitly named.
Touch DO_NOT_TOUCH_RUNTIME files.
Touch Night Supervisor runtime.
Touch telemetry/control/approval inbox state.
Touch broker/OANDA/live trading.
Touch Pi GPIO/motor.
Push.

VALIDATION
1. git status --short --branch
2. Confirm only approved archive file path changed.
3. Confirm no runtime files touched.
4. Confirm no Night Supervisor runtime touched.
5. Confirm no forbidden paths touched.
6. Confirm clean-state verifier after archive.
7. Stop before push.

FINAL REPORT
AI_OS ORCHESTRATION C4 APPLY ARCHIVE RESULT
1. Precheck
2. File archived
3. Files deleted
4. Runtime files touched
5. Night Supervisor touched
6. Final git status
```

## Draft Boundary

This draft intentionally archives only one low/medium-risk candidate and deletes nothing. The broader hard cut is blocked until root show-script and root example references are retired.

