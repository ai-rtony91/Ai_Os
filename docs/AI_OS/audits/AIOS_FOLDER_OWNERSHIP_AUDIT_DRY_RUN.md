# AI_OS Folder Ownership Audit DRY_RUN

## Purpose

This audit inspects repo ownership boundaries and identifies folder placement risks before future agents or scripts write files.

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

## Files Inspected

Inspection used directory listings, target output existence checks, duplicate folder-name scans, `rg --files` for the requested focus folders, and `git status --short`.

## Ownership Conflicts Found

| Conflict | Evidence | Risk | Recommended correction |
| --- | --- | --- | --- |
| Telemetry appears in multiple roles | `docs/AI_OS/telemetry/`, `automation/telemetry/`, `docs/AI_OS/trading_laboratory/telemetry/` | Schemas may be confused with scripts or trading lab telemetry | Define `docs/AI_OS/telemetry/` as planning, `automation/telemetry/` as future scripts, trading lab telemetry as review-only lab artifacts |
| Checkpoints appear in docs, automation, Reports | `docs/AI_OS/checkpoints/`, `automation/checkpoints/`, `Reports/checkpoints/` | Generated checkpoint outputs may be confused with checkpoint planning/scripts | Define docs as planning, automation as script generation, Reports as generated outputs |
| Metrics appears in docs, automation, trading lab | `docs/AI_OS/metrics/`, `automation/metrics/`, `docs/AI_OS/trading_laboratory/metrics/` | Product metrics may be confused with trading lab metrics | Add ownership labels before new metrics files |
| Dashboard appears in docs and apps | `docs/AI_OS/dashboard/`, `apps/dashboard/` | Requirements may be mixed with UI code | Keep planning in docs; code in app |
| Reports appears as root and trading lab subfolder | `Reports/`, `docs/AI_OS/trading_laboratory/reports/` | Generated reports may be confused with templates | Root Reports owns generated outputs; trading lab reports owns templates/planning |
| Broker planning folders now exist | `docs/AI_OS/brokers/`, `docs/AI_OS/broker_adapters/` | Future agents may assume implementation approval | Mark docs-only and block services/broker code |

## Duplicate / Overlapping Folder Risks

Observed overlapping folder names:

- `telemetry`
- `checkpoints`
- `metrics`
- `reporting`
- `router`
- `sessions`
- `writers`
- `startup`
- `analytics`
- `dashboard`
- `Reports`
- `orchestration`
- `automation`
- `health`

These are not automatically invalid, but each needs clear owner category and write rules.

## Proposed Source-Of-Truth Folder Map

| Domain | Source-of-truth folder | Notes |
| --- | --- | --- |
| AI_OS planning and policies | `docs/AI_OS/` | Planning source root |
| Governance proposals | `docs/AI_OS/governance/` | Does not replace protected root files without approval |
| Audit docs | `docs/AI_OS/audits/` | Audit source docs |
| Generated reports | `Reports/` | Output only |
| Automation scripts | `automation/` | Scripts only |
| Dashboard requirements | `docs/AI_OS/dashboard/` | No live UI code |
| Dashboard code | `apps/dashboard/` | UI code only |
| Backend services | `services/` | No broker/OANDA until approved |
| Agent planning/runtime | `agent/` | No autonomous execution without approval |
| Telemetry planning | `docs/AI_OS/telemetry/` | No collectors/writers |
| Telemetry scripts | `automation/telemetry/` | Future scripts only after approval |
| Trading lab review | `docs/AI_OS/trading_laboratory/` | No live broker execution |
| Broker planning | `docs/AI_OS/brokers/` | No API clients |
| Adapter planning | `docs/AI_OS/broker_adapters/` | No implementation |
| Legal placeholders | `docs/AI_OS/legal/` | Not legal advice |
| Compliance placeholders | `docs/AI_OS/compliance/` | No enforcement code |
| Monetization planning | `docs/AI_OS/monetization/` | No payment code |
| Mobile/PWA planning | `docs/AI_OS/mobile/` | No production publishing |

## Proposed Blocked-Action Matrix

| Area | Blocked action |
| --- | --- |
| Protected root | Edits without explicit approval and backup |
| `docs/AI_OS/` | Secrets, live execution code, broker API clients |
| `automation/` | Final source-of-truth reports, unapproved broker execution, secrets |
| `Reports/` | Canonical source policy, implementation code, secrets |
| `apps/dashboard/` | Broker execution, hardcoded keys, live trading buttons, unapproved telemetry persistence |
| `services/` | Broker/OANDA code before Stage 8 approval, secrets, live execution |
| `docs/AI_OS/telemetry/` | Collectors, writers, persistence |
| `automation/telemetry/` | Private/broker data capture without approval |
| `docs/AI_OS/trading_laboratory/` | Live broker execution, credentials, order paths |
| `docs/AI_OS/brokers/` | API clients, credentials, execution |
| `docs/AI_OS/broker_adapters/` | Adapter implementation, broker classes, order submission |
| `docs/AI_OS/legal/` | Final legal claims |
| `docs/AI_OS/compliance/` | Enforcement code |
| `docs/AI_OS/monetization/` | Payment/billing code |
| `docs/AI_OS/mobile/` | App-store submission, production publishing |

## Current Status

The repo has a broad planning architecture with many DRY_RUN/APPLY docs. The main risk is not missing folders anymore; the main risk is overlapping folder names and agents assuming similarly named folders have the same write rules.

## Recommended Correction

Promote a governance ownership map and placement rules after review. Do not edit protected root files yet. Do not move/delete/rename existing folders. Do not consolidate duplicate folder names without a separate DRY_RUN plan.

## Recommended Next APPLY Batch

Apply ownership docs only:

- `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md`
- `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md`
- optional generated report under `Reports/daily/`

Protected root files remain untouched.

## DRY_RUN Result

PASS with REVIEW items. No implementation code, move, delete, rename, overwrite, protected-file edit, broker code, telemetry writer, or Git action is approved.
