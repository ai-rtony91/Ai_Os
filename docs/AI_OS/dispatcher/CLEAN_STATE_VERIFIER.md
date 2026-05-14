# Clean-State Verifier

The Clean-State Verifier prevents AI_OS from applying or committing unsafe changes.

## Purpose

Before apply, commit, push, or system execution, AI_OS checks:

- current branch status
- changed files
- blocked file patterns
- packet allowed file scope
- protected areas

## Behavior

- Clean tree: allowed
- Only packet-scoped changes: review/apply may continue
- Blocked files changed: block
- Out-of-scope files changed: block
- Unknown changes: block until reviewed

## Default Blocked Patterns

- `.env`
- `Reports/security/*`

## PowerShell Check

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validation/Invoke-AIOSCleanStateCheck.ps1
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/validation/Invoke-AIOSCleanStateCheck.ps1 -AllowedFiles "services/dispatcher/*","services/approvals/*","docs/AI_OS/dispatcher/*"
