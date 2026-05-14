# Commit Package Rules 001

Commit packages exist so AI_OS can turn approved worker outputs into clean, reviewable commits.

Workers may inspect, plan, and prepare outputs, but commit packaging is the control point between completed work and Git staging. A package lists the exact files allowed to be staged and the exact files that must stay out.

## Why Commits Must Be Packaged

AI_OS uses multiple worker windows. Without a commit package, unrelated dirty files can be mixed into a commit by accident.

A commit package records:

- the phase and stage
- the packet IDs included
- the approved files
- the blocked files
- the files allowed for staging
- the files excluded from staging
- validator status
- approval gate status
- the required final Git status check
- the draft commit message

## Why `git add .` Is Blocked

`git add .` stages every changed file under the current directory. In a multi-worker repo, that can include unrelated edits, operator files, reports, security notes, or files that were never approved.

AI_OS blocks broad staging commands:

- `git add .`
- `git add -A`
- wildcard staging
- folder-wide staging unless the folder is explicitly approved as the package scope

The safe strategy is exact-file staging only.

## How Approved Files Become A Commit Package

1. A worker completes DRY_RUN.
2. Human approval is recorded for APPLY.
3. APPLY changes are validated.
4. The package builder lists exact approved files in `files_to_stage`.
5. Excluded or unrelated files are listed in `files_not_to_stage`.
6. A dry-run preview prints exact `git add -- <file>` commands only for approved files.
7. A human reviews the preview before any staging happens.

## How Unrelated Files Stay Out

Unrelated files stay out because the manifest is an allowlist. If a file is not listed in `files_to_stage`, it must not be staged by this package.

Untracked files not in the package require review before commit packaging continues.

## Human Review Required

Human review is required before:

- staging files
- creating a commit
- pushing to a remote
- adding a dirty or untracked file to a package
- overriding validator warnings
- including any protected or blocked path

Commit package tooling may preview exact commands, but it must not stage, commit, or push.

