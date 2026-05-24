# AIOS Stage 2 Classification Summary

Source inventory: AIOS_inventory_2026-05-04_16-21-31.csv

Rows classified: 295

## Safety

This is a classification plan only. No user files were moved, deleted, edited, or renamed.

## Proposed Action Counts

- KEEP_READ_ONLY_ARCHIVE: 97
- KEEP_AS_GITHUB_WORKING_REPO: 50
- REVIEW_DUPLICATE_WORKING_COPY: 30
- REVIEW_FOR_CANONICAL_DOCS: 26
- KEEP_REPORT_ARCHIVE: 18
- DELETE_CANDIDATE_AFTER_BACKUP: 12
- KEEP_ACTIVE_CONTEXT_PACK: 10
- MOVE_CANDIDATE_BRANDING: 9
- KEEP_ACTIVE_PROJECT_FILE: 8
- KEEP_ACTIVE_DOCS: 8
- KEEP_ACTIVE_TRADING_ENGINE: 6
- KEEP_SECURITY_REFERENCE: 6
- KEEP_PRIVATE_DO_NOT_UPLOAD: 5
- MOVE_CANDIDATE_TO_INBOX: 4
- KEEP_OR_RECREATE_SHORTCUT_LATER: 3
- MOVE_CANDIDATE_TO_AI_OS_PROJECT: 2
- KEEP: 1

## Risk Counts

- MEDIUM: 172
- LOW: 115
- HIGH: 8

## Target Zone Counts

- BACKUP_ARCHIVE: 97
- GITHUB_REPO_CLEAN: 50
- ACTIVE_PROJECT_ROOT: 34
- DESKTOP_WORKING_COPY: 30
- REPORTS_DAILY: 18
- WINDOWS_METADATA: 12
- SYSTEM_WIZARDS: 10
- BRANDING_ASSETS: 9
- AI_OS_DOCS: 8
- TRADING_ENGINE_V1: 6
- SECURITY_YUBIKEY: 6
- SECRETS_CONFIG: 5
- DOWNLOADS_AI_OS: 3
- DESKTOP_SHORTCUTS: 3
- DESKTOP_LOOSE_AI_OS: 2
- TOOLS_INVENTORY: 1
- DOCUMENTS_AI_OS: 1

## Stage 3 Recommendation

Create a no-delete scaffold/organizer script that creates missing folders only: _INBOX, _ARCHIVE, docs/AI_OS/branding, docs/AI_OS/inventory, docs/AI_OS/policies, docs/AI_OS/prompts, Reports/daily, tools/powershell, tools/python. Do not move files until the classification plan is reviewed.

## Hard Safety Stops

- Do not move or upload `.env` files.
- Do not delete `desktop.ini` yet; mark only as delete candidate after backup.
- Do not merge Desktop Ai_Os, GitHub clean repo, and OneDrive AI-OS-Project until a diff report exists.
- Treat `ai-rtony91_Ai_Os_CLEAN` as the likely GitHub/Codex repo copy, but do not overwrite it from OneDrive blindly.