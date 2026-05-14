# AI_OS Recovery Bootstrap 001

Use this guide when work is interrupted or state becomes unclear.

## If Codex Crashes

Stop assigning new packets. Run `git status --short --branch` and identify modified, untracked, and staged files. Treat unclear work as `REVIEW_REQUIRED`.

## If PowerShell Closes

Do not resume APPLY automatically. Reopen a terminal in the repo root and run the clean-state checks before continuing.

## If Git Is Ahead Or Behind

Do not commit, push, pull, rebase, or merge until the operator reviews branch state. Record whether the branch is ahead, behind, or diverged.

## If Rebase Gets Stuck

Pause. Do not run destructive cleanup commands without explicit approval. Capture the current status and ask for a recovery instruction.

## If OneDrive Locks Folders

Wait for sync to settle, then rerun status checks. Do not overwrite, move, or rename files to work around a lock without approval.

## Before Opening More Workers

Confirm:

- repo status is understood
- active packets are known
- active locks are known
- no worker owns the same file group
- no protected paths are dirty
- no commit package is pending review

Next safe action: review clean-state output before assigning or resuming worker packets.
