# AI_OS Repo Ownership Audit DRY_RUN 2026-05-07 154940

## Task

AI_OS repo ownership + file placement control DRY_RUN.

## Mode

DRY_RUN only. Reports created only under approved paths. No move, delete, rename, overwrite, protected-file edit, implementation code, broker code, telemetry writer, collector, persistence, secrets, `.env`, or GitHub action was performed.

## Files Inspected

- Required output target paths
- Root folder listing
- Requested ownership folders
- Duplicate folder-name scan
- Focus folder file listing via `rg --files`
- `git status --short`

## Folders Inspected

- repo root
- `docs/AI_OS/`
- `automation/`
- `Reports/`
- `apps/`
- `services/`
- `agent/`
- `docs/AI_OS/telemetry/`
- `automation/telemetry/`
- `docs/AI_OS/trading_laboratory/`
- `docs/AI_OS/brokers/`
- `docs/AI_OS/broker_adapters/`
- `docs/AI_OS/legal/`
- `docs/AI_OS/compliance/`
- `docs/AI_OS/monetization/`
- `docs/AI_OS/mobile/`
- `docs/AI_OS/dashboard/`
- `apps/dashboard/`

## Files Created

- `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP_DRY_RUN.md`
- `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES_DRY_RUN.md`
- `docs/AI_OS/audits/AIOS_FOLDER_OWNERSHIP_AUDIT_DRY_RUN.md`
- `Reports/daily/AIOS_REPO_OWNERSHIP_AUDIT_DRY_RUN_2026-05-07_154940.md`

## Files Changed

New DRY_RUN report files only. No existing files were modified.

## Ownership Conflicts Found

- Telemetry ownership overlap: `docs/AI_OS/telemetry/`, `automation/telemetry/`, `docs/AI_OS/trading_laboratory/telemetry/`.
- Checkpoint ownership overlap: `docs/AI_OS/checkpoints/`, `automation/checkpoints/`, `Reports/checkpoints/`.
- Metrics ownership overlap: `docs/AI_OS/metrics/`, `automation/metrics/`, `docs/AI_OS/trading_laboratory/metrics/`.
- Dashboard ownership overlap: `docs/AI_OS/dashboard/` and `apps/dashboard/`.
- Reports ownership overlap: `Reports/` and `docs/AI_OS/trading_laboratory/reports/`.
- Broker planning folders exist and need clear docs-only boundaries to prevent accidental implementation assumptions.

## Duplicate / Overlapping Folder Risks

Observed repeated folder names include telemetry, checkpoints, metrics, reporting, router, sessions, writers, startup, analytics, dashboard, Reports, orchestration, automation, and health.

These are REVIEW risks, not deletion recommendations.

## Proposed Source-Of-Truth Folder Map

- `docs/AI_OS/`: planning, policies, schemas, architecture, boundaries, requirements, drafts.
- `automation/`: scripts only.
- `Reports/`: generated outputs only.
- `apps/dashboard/`: dashboard UI code only.
- `services/`: backend services only, no broker/OANDA until Stage 8 approval.
- `agent/`: future agent instructions/planning unless otherwise approved.
- `docs/AI_OS/telemetry/`: telemetry planning/schemas/privacy only.
- `automation/telemetry/`: future telemetry scripts only after approval.
- `docs/AI_OS/trading_laboratory/`: review-only trading lab planning and templates.
- `docs/AI_OS/brokers/`: broker boundary planning only.
- `docs/AI_OS/broker_adapters/`: adapter interface planning only.
- `docs/AI_OS/legal/`: legal placeholders only.
- `docs/AI_OS/compliance/`: compliance checklists and consent/retention drafts.
- `docs/AI_OS/monetization/`: pricing, packaging, revenue planning only.
- `docs/AI_OS/mobile/`: mobile/PWA/app-store planning only.
- `docs/AI_OS/dashboard/`: dashboard requirements and planning docs only.

## Proposed Blocked-Action Matrix

| Request | Result |
| --- | --- |
| Protected root edit without approval | BLOCK |
| Secrets/API keys/credentials | BLOCK |
| Broker/OANDA code | BLOCK |
| Broker account data | BLOCK |
| Order path/webhook execution | BLOCK |
| Telemetry writer/collector/persistence | BLOCK |
| Planning docs in `automation/` | BLOCK |
| Live code in `docs/AI_OS/` | BLOCK |
| Generated report as canonical source policy | REVIEW |
| Dashboard code in `docs/AI_OS/dashboard/` | BLOCK |
| Payment/billing code in monetization docs | BLOCK |
| Final legal claims in legal placeholders | BLOCK |

## Recommended Next APPLY Batch

Apply ownership docs only after review. Do not edit protected root files.

Recommended APPLY scope:

- create promoted ownership map under `docs/AI_OS/governance/`
- create promoted placement rules under `docs/AI_OS/governance/`
- create a generated daily report under `Reports/daily/`

## git status --short

Captured before final verification; see final assistant response for latest command output.

## Errors

None.

## Unknowns

- UNKNOWN: whether overlapping folder names should later be clarified through README_FOLDER_PURPOSE updates.
- UNKNOWN: whether protected root docs should later reference the ownership map.
- UNKNOWN: whether existing generated Reports should be indexed or left as-is.
- UNKNOWN: whether dashboard React and static preview ownership should receive a separate parity audit.

## Protected Action Involved

NO.

## Approval Required

YES, before APPLY ownership docs.

## Next Safe Action

Review this DRY_RUN and approve ownership docs only.
