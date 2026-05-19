# AI_OS Commit Package Recommendation DRY_RUN

This folder contains commit package review material.

`New-AiOsCommitPackageRecommendation.DRY_RUN.ps1` reads git status and recommends selective staging commands without staging anything.

Safety rules:

- DRY_RUN only.
- Do not use `git add .`.
- No commits.
- No pushes.
- No dispatcher edits.
- No runtime integration.
- No dashboard edits.
- Do not touch `approval_runner`.

The recommender checks:

- changed files
- new files
- protected path risk
- generated and example files
- worker lane ownership from the current branch
- commit message suggestion
- files to exclude

Example:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\commit_packages\New-AiOsCommitPackageRecommendation.DRY_RUN.ps1
```

JSON output:

```powershell
powershell -ExecutionPolicy Bypass -File automation\orchestration\commit_packages\New-AiOsCommitPackageRecommendation.DRY_RUN.ps1 -OutputJson
```

Next safe action: review the recommended `git add -- <file>` commands and only run selective staging after explicit approval.
