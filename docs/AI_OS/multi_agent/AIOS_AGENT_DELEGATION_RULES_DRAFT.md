# AIOS Agent Delegation Rules Draft

Status: Draft scaffold

## Purpose

Define safe delegation rules for multiple AI agents working on AI_OS.

## Delegation Rules

- Assign only bounded tasks with clear files or folders.
- Require DRY_RUN before APPLY for file-changing automation.
- Keep protected actions under human approval.
- Require each agent to report inspected files, changed files, skipped files, errors, and unknowns.
- Mark unverified claims as UNKNOWN.
- Mark conflicting evidence as MISMATCH.

## Human Checkpoints

- Before APPLY.
- Before Git commit.
- Before push or PR.
- Before broker, credential, or trading-related work.
- Before protected root governance edits.
