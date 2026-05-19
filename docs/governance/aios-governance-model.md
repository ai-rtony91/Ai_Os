# AI_OS Governance Model

Status: canonical summary extracted from legacy `docs/AI_OS`

## Purpose

This document summarizes AI_OS governance doctrine from legacy `docs/AI_OS` governance, operator, security, and orchestration files. It is a compact active reference, not an approval to automate.

## Current Doctrine

Primary rule:

Document infrastructure first. Automate second. Scale third.

Every significant task must define:

- role,
- purpose,
- allowed paths,
- blocked paths,
- DRY_RUN or APPLY mode,
- validation,
- stop point,
- commit status,
- push status,
- next safe action.

## Human Approval Gates

Human approval is required before:

- APPLY changes,
- protected root edits,
- file delete/move/rename,
- overwrite of existing files when not explicitly scoped,
- commit,
- push,
- merge,
- PR approval,
- deployment,
- credential or secret handling,
- broker/OANDA/webhook/live trading work.

## Source-of-Truth Doctrine

Root governance files have highest authority. Canonical `docs/governance`, `docs/workflows`, `docs/infrastructure`, `docs/security`, and `docs/decisions` should supersede old subsystem drafts once reviewed.

Rules:

- Reports and archives are evidence/history, not active instruction sources.
- Drafts are not authoritative until promoted.
- Unknown facts remain `UNKNOWN`.
- Conflicting evidence must be marked `MISMATCH` or `INVALID DATA`.
- Source docs should be compact, current, and easy for operators to scan.

## Trading and Broker Boundary

Current policy:

- no live trading,
- no broker connection,
- no OANDA integration,
- no API keys or secrets,
- no real orders,
- no real webhook execution,
- paper-only Trading Lab work only when explicitly scoped.

Any old document suggesting live broker execution is treated as historical or unreviewed until MAIN CONTROL says otherwise.

## Archive-Before-Delete Rule

Cleanup should prefer:

1. document current state,
2. extract useful doctrine,
3. move legacy material to archive,
4. review archive,
5. only then consider deletion.

Deletion is never the default cleanup operation.

## Planned/Future Ideas

- Documentation promotion criteria.
- Canonical decision records.
- Validator-backed governance checks.
- Better source-of-truth maps for reports, runtime state, and worker lanes.

## Human-Review Items

- Which legacy `docs/AI_OS` docs become `CURRENT`.
- Which generated docs become `HISTORICAL`.
- Which root-level governance drafts are worth promoting.
- Whether old trading/productization language needs explicit supersession labels.
