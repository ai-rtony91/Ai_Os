> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

# AI_OS Documentation Promotion Criteria Draft

## Purpose

This draft defines criteria for promoting a draft document toward authority. Promotion does not happen automatically.

No protected root files are edited by this draft. Human approval is required before any promotion. This file creates no live automation.

## Promotion Criteria

| Criterion | Requirement | Status before promotion |
| --- | --- | --- |
| source evidence | Claims must be traceable to files, terminal output, screenshots, or approved source records. | REQUIRED |
| owner layer | The document must identify whether it belongs to root governance, planning, validation, reports, telemetry, dashboard, or operations. | REQUIRED |
| validator coverage | A DRY_RUN validator should check file presence, path class, required phrases, and parseable structured data where applicable. | REQUIRED |
| conflict check | Conflicts with existing files, protected instructions, or current repo state must be marked REVIEW, BLOCKED, or INVALID DATA. | REQUIRED |
| protected-file impact | Any impact on protected root files must be explicit and approval-gated. | REQUIRED |
| human approval | A human approval checkpoint must identify exact files, actions, and stop conditions. | REQUIRED |
| rollback/backup rule | Any update to existing important files must define backup or rollback handling before APPLY. | REQUIRED |
| commit/push checkpoint | Commit and push must happen only after validator PASS and explicit approval. | REQUIRED |

## Non-Automatic Promotion Rule

Draft documents remain draft until human approval explicitly promotes them. A roadmap, audit, index, or validator draft alone cannot promote authority, activate writers, create startup tasks, approve live automation, or approve trading automation.

## Boundary

This draft does not approve edits to protected root files and does not create no live automation beyond documentation planning.
