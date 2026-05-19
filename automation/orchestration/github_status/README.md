# AI_OS GitHub Status Check Reader DRY_RUN

This folder contains a read-only GitHub status check reader.

Purpose:

- Show the current branch.
- Show the current commit SHA.
- Show local `origin/main` SHA when available.
- Check whether GitHub CLI exists.
- Check whether GitHub CLI auth appears usable.
- Read GitHub check runs for the current commit when possible.
- Give a safe fallback when GitHub CLI is unavailable.

Safety rules:

- DRY_RUN only.
- No commits.
- No pushes.
- No dispatcher edits.
- No runtime integration.
- No dashboard edits.
- No secrets.
- Do not print tokens.

Example:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\github_status\Get-AiOsGitHubStatusCheck.DRY_RUN.ps1
```

JSON output:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\github_status\Get-AiOsGitHubStatusCheck.DRY_RUN.ps1 -OutputJson
```

Next safe action: use this after a push when AI_OS needs to know whether GitHub checks are passing, pending, failed, or unavailable.
