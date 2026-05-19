# AI_OS Worker Branch And Lane Rules

Status: canonical workflow
Source: `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md`

## Purpose

This document defines branch and lane metadata rules for supervised AI_OS worker activity. It supports isolation and collision prevention; it does not create branches, worktrees, commits, pushes, or merges.

## Branch Naming

Recommended branch pattern:

```text
worker/<lane>/<phase>-<short-task>
```

Branch names must be lowercase, short, descriptive, and free of secrets, tokens, account identifiers, or private data.

## Required Lane Metadata

Before APPLY review, each lane should declare:

- worker ID.
- worker lane.
- branch name.
- base branch.
- worktree path.
- allowed paths.
- blocked paths.
- report path.
- validation commands.

## Path Ownership

Workers must stay inside declared allowed paths and must not edit:

- protected root files.
- files outside their assigned lane.
- secrets, credentials, API keys, broker tokens, private keys, or recovery keys.
- dashboard files unless assigned to a dashboard lane.
- trading execution logic.
- broker, OANDA, webhook, live execution, or real order paths.

## Collision Handling

If two workers declare the same planned file, the conflict is blocked until the operator assigns ownership. Stale worker state must be reviewed before resuming.

