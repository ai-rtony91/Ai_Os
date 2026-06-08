# AI_OS Local Hooks

Status: subordinate workflow.

This workflow explains the opt-in local hook template created for AI_OS governance validation. It does not auto-install hooks and does not approve commit or push.

Run a preview from the repo root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/hooks/Install-AiOsGitHooks.ps1 -Mode DRY_RUN
```

What it changes:

- `DRY_RUN`: prints the planned hook source and target only.
- `APPLY`: copies `.githooks/pre-commit` to `.git/hooks/pre-commit` only when no existing hook is present.

What it refuses:

- It refuses to overwrite an existing hook.
- It does not install dependencies.
- It does not commit, push, merge, deploy, trade, or read secrets.

Validation:

```powershell
python automation/validators/aios_governance_validator.py --sample-check
git diff --check
```

