# Phase 16.6 Commit Package Builder

## Purpose

Phase 16.6 adds a read-only commit package display for AI_OS orchestration work.

The commit package display helps an operator review:

- approved files for a future selective commit
- blocked files that must not be staged
- the proposed commit message
- packet IDs included in the package

## Files Added

- `automation/orchestration/commit_package.example.json`
- `automation/orchestration/show-commit-package.ps1`
- `docs/AI_OS/orchestration/PHASE_16_6_COMMIT_PACKAGE_BUILDER.md`
- `Reports/checkpoints/CHECKPOINT_PHASE_16_6_COMMIT_PACKAGE_BUILDER.md`

## Script Behavior

`show-commit-package.ps1` reads:

- `automation/orchestration/commit_package.example.json`

It prints:

- package name and approval state
- proposed commit message
- packet IDs
- approved files for future commit
- blocked files
- safety rules

## Safety Boundary

This phase is display-only.

It does not:

- stage files
- run `git add`
- create commits
- push changes
- modify files
- create approval state
- launch packets
- launch workers
- edit dashboard files
- connect to a broker
- connect to OANDA
- use API keys
- place orders
- enable live trading

## Validation

Run:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File automation/orchestration/show-commit-package.ps1
git status --short --branch
```

Expected result:

- The script prints approved files, blocked files, and the proposed commit message.
- The script completes without staging files or creating a commit.
- Git status shows the Phase 16.6 created files plus any previously untracked work.

## Next Safe Action

Review the commit package display and checkpoint, then decide whether to approve a separate selective staging or selective commit prompt.
