# Safe Rollback Guide

Rollback means recovering from a bad change.

AI_OS rollback must be scoped and approved.

Allowed planning:

- Identify the exact files that would need to be restored.
- Name the commit or backup source if known.
- Explain the risk of rollback.
- Ask for approval before changing files.

Blocked by default:

- `git reset --hard`
- `git clean`
- deleting files
- moving files
- renaming files
- broad checkout of unrelated files
- touching `.codex_backups/` without approval

Dock player example:

If a dock player repair is wrong, rollback should name only the approved dashboard dock player files. It must not reset the whole repo or remove unrelated dashboard work.
