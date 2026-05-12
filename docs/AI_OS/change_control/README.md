# AI_OS Change Control

This folder defines how future AI_OS changes should be requested, scoped, approved, validated, and packaged for commit.

Purpose: prevent unrelated work from being mixed together.

Basic flow:

1. Write the user goal.
2. Name the exact files allowed.
3. Name the exact files blocked.
4. Assign an owner or agent.
5. Run DRY_RUN first.
6. Wait for APPLY approval.
7. Validate the result.
8. Package only related files for commit.
9. Keep a rollback note.

Default mode is DRY_RUN.

Blocked by default: secrets, installs, broker actions, OANDA, live trading, real API activation, dashboard edits without exact paths, deleting files, moving files, renaming files, `git add .`, mixed commits, commits without approval, and pushes without approval.
