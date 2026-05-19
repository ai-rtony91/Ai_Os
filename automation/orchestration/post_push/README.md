# AI_OS Post-Push Verification DRY_RUN

This folder contains a read-only post-push verification scaffold.

Purpose:

- Help MAIN CONTROL verify that a pushed commit looks safe after pushing to `main`.
- Show current branch, latest commit hash, latest commit message, and local `origin/main` alignment.
- Show clean or dirty git status.
- Warn if GitHub checks are unknown or need review.

Safety rules:

- DRY_RUN only.
- No commits.
- No pushes.
- No dispatcher edits.
- No runtime integration.
- No dashboard edits.
- Do not touch `clean_state`.

Example:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\post_push\Test-AiOsPostPushVerification.DRY_RUN.ps1
```

JSON output:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\post_push\Test-AiOsPostPushVerification.DRY_RUN.ps1 -OutputJson
```

Next safe action: run after MAIN CONTROL pushes to `main`, then review any REVIEW or BLOCKED result before declaring the push complete.
