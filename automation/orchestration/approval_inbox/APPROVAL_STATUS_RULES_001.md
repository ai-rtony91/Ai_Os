# Approval Status Rules 001

## Purpose

The approval inbox separates DRY_RUN planning from APPLY execution.

Plain rule:

DRY_RUN can propose. APPLY requires approval. COMMIT requires clean validation. PUSH requires final human review.

## Status Values

### draft

The approval item is being prepared. It is not ready for review and cannot authorize APPLY.

### pending_review

The approval item is waiting for human review. APPLY remains blocked.

### approved_for_apply

A human reviewer approved the specific APPLY request. The approval applies only to the listed packet, allowed paths, validators, and risk notes.

### rejected

The requested action was rejected. The packet must not run APPLY unless a new approval item is created and approved.

### blocked

The request is unsafe, incomplete, conflicted, or outside allowed paths. The next safe action must be review or correction, not APPLY.

### expired

The approval item is too old or no longer matches current repo/runtime state. A new review is required.

### completed

The approved action was completed and validation results were recorded. This status does not authorize future APPLY, commit, or push work.

## Commit And Push Boundary

Approval for APPLY does not approve commit.

Commit requires:

- clean validation
- exact-file commit package
- human review of changed files
- no unrelated dirty files in the package

Push requires final human review after commit readiness is confirmed.
