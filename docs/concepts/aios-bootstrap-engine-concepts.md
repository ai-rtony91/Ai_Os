# AI_OS Bootstrap Engine Concepts

Status: canonical concept summary extracted from legacy `docs/AI_OS/bootstrap_engine`

Last reviewed: Phase 104 bootstrap engine final blocker clearance

## Purpose

This document preserves the useful bootstrap engine doctrine from legacy AI_OS planning docs. It is a concept reference, not an active bootstrap implementation and not approval to create, move, delete, or overwrite files.

## Core Doctrine

The bootstrap engine concept is a safe project-start and recovery assistant. It may help the operator understand project context and propose missing scaffold files, but it must remain DRY_RUN until explicitly approved.

Useful preserved concepts:

- read approved context packets and visible repo evidence,
- identify repo root, branch, Git remote, folder role notes, README files, reports, and checkpoints,
- infer project identity only from evidence,
- label missing or unverifiable facts as UNKNOWN,
- infer folder ownership and protected files without moving or renaming folders,
- infer allowed and blocked actions as recommendations only,
- detect missing scaffold candidates,
- generate scaffold proposals with target paths, purpose, safety boundaries, approval status, and next safe action,
- recommend validation commands and rollback evidence without running rollback commands.

## Safety Boundaries

Bootstrap engine work must not:

- run autonomous APPLY,
- delete, move, rename, or overwrite files,
- handle secrets, credentials, API keys, or private keys,
- connect to brokers,
- enable OANDA, webhooks, live trading, or real orders,
- push, merge, reset, clean, or checkout protected branches,
- modify governance files from inferred rules,
- self-replicate AI_OS into another repo.

## DRY_RUN To APPLY Boundary

APPLY can be considered only after all required evidence is present:

1. DRY_RUN report.
2. Checkpoint or recovery evidence.
3. Exact target file list.
4. Existing-file collision check.
5. Skipped-existing list.
6. Protected file exclusion check.
7. Rollback recommendation.
8. Explicit human approval.

Missing inputs are UNKNOWN and must block APPLY.

## Inference Model

Bootstrap inference should produce reviewable metadata, not hidden behavior:

- protected files,
- blocked actions,
- approval-required actions,
- allowed read-only actions,
- reporting paths,
- checkpoint paths,
- deployment target assumptions,
- validation rules,
- unknowns.

Inferred rules are not canonical until approved by the operator.

## Scaffold Proposal Review

A scaffold proposal should include:

- target path list,
- file purpose,
- existing file collision result,
- protected action flag,
- expected validator,
- rollback or recovery recommendation,
- human approval status,
- next safe action.

Proposal review does not create files.

## Current Cleanup Status

Phase 103 preserved the concepts here. Phase 104 repointed the bootstrap engine readiness validator to this canonical concept document so the legacy bootstrap engine planning folder could be archived after a clean active-area scan.
