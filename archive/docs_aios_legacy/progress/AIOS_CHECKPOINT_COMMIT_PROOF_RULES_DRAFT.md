# AI_OS Checkpoint Commit Proof Rules Draft

Status: DRAFT
Phase: Phase 12
Stage: 12.15 - Development Metrics + Completion Dashboard Readiness

## Purpose

Define proof requirements for marking AI_OS work as complete in progress records and future dashboard cards.

## Checkpoint Proof

Completion requires a checkpoint that includes:

- Date
- Mode
- Phase or stage
- Summary
- Safety status
- Next safe action

## Commit Proof

After commit, completion records should include:

- Commit hash
- Branch name
- Git status before commit
- Git status after commit
- Commit message

## Missing Proof Handling

- Missing checkpoint proof: CHECKPOINT_UNKNOWN
- Missing commit proof: COMMIT_UNKNOWN
- Conflicting checkpoint and commit evidence: MISMATCH
- Uncommitted files after APPLY: APPLY_COMPLETE_PENDING_COMMIT

