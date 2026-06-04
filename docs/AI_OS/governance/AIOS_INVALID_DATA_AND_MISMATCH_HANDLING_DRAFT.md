> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

# AI_OS INVALID DATA and Mismatch Handling Draft

## Purpose

This draft defines how AI_OS should handle missing files, duplicate docs, stale docs, conflicting instructions, protected-file conflicts, failed validators, unknown repo state, network/GitHub push failures, and credential-manager-core warning output.

No protected root files are edited by this draft. Human approval is required before adopting this as authoritative. This file creates no live automation.

## Required Labels

- PASS
- REVIEW
- NEEDS_REFACTOR
- BLOCKED
- INVALID DATA

## Handling Rules

| Situation | Required label | Handling |
| --- | --- | --- |
| missing files | REVIEW or BLOCKED | Stop if required target files are missing before validation can pass. Report exact paths. |
| duplicate docs | REVIEW | Preserve both files unless explicit approval exists to consolidate. Do not delete, move, rename, or overwrite. |
| stale docs | REVIEW | Mark the stale evidence and request validation before promotion. |
| conflicting instructions | BLOCKED | Follow the stricter safety rule and ask for human approval if needed. |
| protected-file conflicts | BLOCKED | Do not edit protected root files without explicit approval and required backup handling. |
| failed validators | BLOCKED | Do not commit or push until failures are resolved or explicitly waived by human approval. |
| unknown repo state | INVALID DATA | Stop until branch, status, and target paths are verified by terminal output. |
| network/GitHub push failures | REVIEW | Report the failure, preserve the local commit, and retry only with approved network access if needed. |
| credential-manager-core warning | REVIEW | Report the warning if push still succeeds; treat as BLOCKED only if authentication or push fails. |

## Mismatch Rule

Mismatches must be reported, not hidden. If observed files, terminal output, screenshots, or known repo state conflict with prior notes, mark the conflict as MISMATCH or INVALID DATA and stop if the conflict affects safety.

## Boundary

This draft does not grant human approval, does not edit protected root files, and creates no live automation.
