# AI_OS Runtime Context Precheck Rule

Purpose:
Define required runtime context checks before any future Night Supervisor or runtime worker start.

## Required Checks

- `USERPROFILE` check
- `pwd` check
- Git root check
- expected worktree check
- Python `Path.cwd()` check
- canonical profile path check or approved fallback
- active lock check
- dirty tree check
- forbidden path dirty check
- mode check

## Known Failure

Paper SOS failed because Python `Path.cwd()` resolved to `C:\Dev\Ai.Os` instead of `C:\Dev\aios-paper-sos-runtime-closeout`.

Future runtime packets must verify the operator directory, shell working directory, Git root, expected worktree, Python current working directory, and profile path before execution.

## Fail-Closed Rule

If any context value mismatches the expected worktree, branch, profile, mode, clean tree, lock state, or forbidden-path policy, runtime must fail closed and produce a recovery report. It must not silently continue in the wrong directory.
