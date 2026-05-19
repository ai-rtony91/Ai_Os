# PR 180 Repo Consolidation Review Summary

Date: 2026-05-19
PR: #180
Branch: `phase-82-copy-paste-reduction-runner`
Base branch: `main`

## Purpose

PR #180 is a consolidation checkpoint for AI_OS repo cleanup. It moves legacy/generated material out of active paths, records the cleanup rationale in audit docs, and begins reducing competing orchestration and docs source-of-truth surfaces.

This PR should be reviewed as a cleanup boundary, not as final repo cleanup.

## What Changed

Archive moves:

- Moved legacy `Reports/` material to `archive/reports_legacy/`.
- Moved legacy `docs/AI_OS/trading_laboratory/` material to `archive/docs_aios_trading_laboratory_legacy/`.
- Moved generated `docs/AI_OS` folders to `archive/docs_aios_legacy/`.
- Moved selected legacy orchestration fallback examples to `archive/orchestration_legacy/`.
- Removed tracked runtime log `automation/orchestration/workers/logs/validator_worker.log` from Git tracking.

Orchestration canonicalization:

- Documented source-of-truth paths for worker registry, queue/work packets, approval inbox, validator chain, commit package flow, supervisor/control loop, and operator status.
- Updated orchestration status/display scripts to prefer canonical subfolder paths.
- Made legacy root fallback files optional before archiving them.

Fallback retirement:

- Cleared remaining hard references to old orchestration fallback files.
- Archived safe legacy fallback files after final scans.
- Retired automation references to generated `docs/AI_OS/checkpoints`, `progress`, `backfill`, and `morning_brief` folders.

docs/AI_OS summary extraction:

- Added compact canonical summaries under `docs/architecture`, `docs/workflows`, `docs/governance`, `docs/infrastructure`, `docs/roadmap`, and `docs/concepts`.
- Preserved legacy detail in archive instead of deleting it.

Automation reference cleanup:

- Repointed status validators and work intelligence config away from generated docs folders toward canonical summaries and audit docs.
- Kept validators DRY_RUN-only.

## What Did Not Change

This PR was not intended to change active product/runtime behavior.

Areas not intentionally changed:

- `apps/dashboard`
- `apps/trading_lab`
- `services`
- `schemas`
- `tests`
- `.github` workflows
- live trading, broker, OANDA, webhook, or order execution behavior

No API keys, secrets, live broker hooks, or live trading paths were created.

## Risk Surface

Known PR scale:

- 15 commits
- 927 changed files
- 3923 additions
- 206 deletions
- 50 non-archive active-surface files

Non-archive active risk concentration:

- `automation/orchestration`: 18 files
- `automation/status`: 8 files
- `automation/work_intelligence`: 1 file
- `docs/audits`: 15 files
- `docs/concepts`: 2 files
- `docs/architecture`: 1 file
- `docs/workflows`: 1 file
- `docs/governance`: 1 file
- `docs/infrastructure`: 1 file
- `docs/roadmap`: 1 file
- `.gitignore`: 1 file

Main review risk is not app runtime behavior. The main risk is whether path repoints, archive moves, and source-of-truth decisions preserve enough recoverability and do not hide still-active references.

## Reviewer Checklist

- Review orchestration canonical path changes and confirm old root examples are no longer required.
- Review status validator path repoints from generated `docs/AI_OS` folders to compact canonical summaries.
- Confirm `automation/orchestration/workers/logs/validator_worker.log` should remain untracked.
- Confirm the archive-before-delete strategy is acceptable for this cleanup phase.
- Confirm no app/runtime behavior changed unexpectedly.
- Confirm no broker/OANDA/webhook/live trading behavior was introduced.
- Confirm large archive moves are acceptable in PR #180 rather than split into a separate archive-only PR.

## Remaining Cleanup After PR

High-value next cleanup targets:

- `docs/AI_OS/dashboard`
- `docs/AI_OS/dispatcher`
- `docs/AI_OS/orchestration`

Follow-up decisions:

- Whether archived legacy material should stay in Git long term.
- Whether some archive material should be summarized then removed in a later human-approved cleanup.
- Whether remaining `docs/AI_OS` source-of-truth references should be updated to point at compact canonical docs.
- Whether orchestration should continue consolidation toward one controlled operator loop.

## Merge Recommendation

PR #180 is safe to review as a consolidation checkpoint if reviewers are comfortable with archive moves and the non-archive active risk surface.

Do not treat this PR as final cleanup. Do not continue mass archival in the same PR after review starts. Further cleanup should happen in smaller follow-up passes with fresh scans and human review.
