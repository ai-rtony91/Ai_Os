> Historical/reference-only legacy AI_OS document.
>
> This file is not active AI_OS authority. Current operating authority is `AGENTS.md`; current front-door authority is `README.md`; current source-of-truth mapping lives in `docs/governance/source-of-truth-map.md`; current active-system mapping lives in `docs/audits/active-system-map.md`.
>
> Preserve this file for historical context and durable-rule extraction only. Do not follow stale repo paths, CLEAN-era ACTIVE_REPO references, or `docs/AI_OS` authority claims unless a future approved canonical document explicitly promotes them.

# AI_OS Source-of-Truth Mapping Draft

## Purpose

This draft maps source-of-truth layers for AI_OS documentation, validators, reports, and future outputs. Protected root files remain authoritative until explicit human approval promotes another file.

No protected root files are edited by this draft. Human approval is required before changing authority. This file creates no live automation.

## Source-of-Truth Layers

| Layer | authority_level | allowed_change_mode | approval_required | examples | boundary_notes |
| --- | --- | --- | --- | --- | --- |
| protected root governance files | Highest current authority | Explicit approval only | YES | `README.md`, `AGENTS.md`, `RISK_POLICY.md`, `SOURCE_LOG.md`, `ERROR_LOG.md`, `DAILY_REPORT.md`, `AAR.md` | These files remain authoritative until a human-approved promotion changes project governance. |
| docs/AI_OS draft planning files | Draft planning authority | DRY_RUN-governed creation or approval-gated APPLY | YES | `docs/AI_OS/index/*.md`, `docs/AI_OS/audits/*.md`, `docs/AI_OS/roadmap/*.md` | Draft files help navigation and planning but do not override protected root files. |
| automation DRY_RUN validators | Validation evidence layer | DRY_RUN only unless separately approved | YES | `automation/status/Test-AiOs*.DRY_RUN.ps1` | Validators may inspect and report, but must not write files unless separately approved. |
| Reports/health checkpoint reports | Checkpoint evidence layer | DRY_RUN-governed creation or approval-gated APPLY | YES | `Reports/health/*.txt` | Health reports summarize stage evidence and safety boundaries. |
| Reports/daily progress outputs | Progress reporting layer | Approval-gated output | YES | `Reports/daily/*.md`, `Reports/daily/*.txt` | Daily reports must identify changes, errors, unknowns, and prevention steps. |
| future telemetry outputs | Future runtime evidence layer | Future approval-gated output only | YES | Future telemetry files or databases | No telemetry writer is active; no private data, secrets, or broker data may be collected without governance. |
| future dashboard outputs | Future operator display layer | Future approval-gated output only | YES | Future dashboard static preview or UI output | No dashboard writer is active; dashboard output must not trigger trading or hidden automation. |

## Promotion Boundary

Promotion does not happen automatically. Any source-of-truth change requires evidence, conflict review, protected-file impact review, and human approval. This draft creates no live automation and does not approve protected root file edits.
