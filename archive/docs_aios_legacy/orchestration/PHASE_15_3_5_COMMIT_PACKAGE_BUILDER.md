# Phase 15.3.5 Commit Package Builder

The commit package builder gives AI_OS a review layer between approved worker output and Git staging.

It exists because AI_OS can have multiple Codex workers producing changes at the same time. A clean commit must include only the files that were approved for that package, not every dirty file in the repository.

## Why This Exists

Commit packages make the commit boundary explicit.

Each package records:

- packet IDs included in the package
- files approved for staging
- files excluded from staging
- validator status
- approval gate status
- final Git status requirement
- draft commit message

The package is not a commit. It is a human-review artifact that prepares exact-file staging.

## How It Prevents Accidental Commits

The package uses an allowlist. Only files in `files_to_stage` may be staged for that commit package.

Broad staging is blocked:

- no `git add .`
- no `git add -A`
- no wildcard staging
- no unrelated dirty files

The dry-run preview prints exact `git add -- <file>` commands for review. It never stages, commits, or pushes.

## How It Supports Multiple Codex Workers

Workers can produce separate approved outputs without mixing their changes.

The package builder groups completed worker outputs by packet ID and approved file list. This lets the operator review one commit boundary at a time, even when other worker files are still dirty or waiting for approval.

## Preparation For Later Automation

This phase creates only rules, a manifest, dry-run validators, a dry-run preview, and an activity ledger.

Later automation may generate manifests from approved packets, but it must preserve the same safety model:

- exact-file staging only
- human review before staging
- human review before commit
- human review before push
- no live trading, broker, OANDA, API key, webhook, or real order behavior

