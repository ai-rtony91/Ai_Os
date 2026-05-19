# AI_OS Dashboard Operator Action Map Draft

Status: Draft
Mode: Static dashboard action classification
Date: 2026-05-08

## Purpose

Map visible static dashboard controls and `data-action` values to operator intent, safety category, and future command-center readiness boundaries.

## Action Categories

Informational: read-only status or context display.

Navigation: changes visible dashboard focus or mock selected area.

Fixture-display: reads local fixture/mock data only.

Mock-only: changes local preview text or visual state only.

Approval-required future action: may become a local automation action only after a separate DRY_RUN, approval, validator, and checkpoint.

Blocked: must not execute from the static dashboard.

## Status Strip Controls

| Control | Action | Category | Notes |
| --- | --- | --- | --- |
| Work Table | `work-table` | Navigation | Selects Work Table mock context. |
| Reports | `reports` | Navigation | Selects reports mock context. |
| Telemetry | `telemetry` | Navigation | Selects telemetry mock context. |
| Admin | `admin` | Navigation | Selects admin mock context. |
| System Status | `system-status` | Informational | Updates static assistant/console text only. |
| Run Diagnostics | `diagnostics` | Approval-required future action | Current behavior is mock text only. Real diagnostics require approval. |
| Theme selector | none | Mock-only | Applies local visual preference via approved body classes only. |

## Status Panel Tabs

| Panel | Category | Notes |
| --- | --- | --- |
| Status | Fixture-display | Read-only local fixture/fallback status. |
| Progress | Fixture-display | Read-only local fixture/fallback progress. |
| Validator | Fixture-display | Read-only local fixture/fallback validator summary. |
| Checkpoint | Fixture-display | Read-only local fixture/fallback checkpoint summary. |
| Safety | Fixture-display | Read-only local fixture/fallback safety summary. |
| AI Assistance | Fixture-display | Placeholder fixture display only. |
| Work Table AI | Fixture-display | Placeholder fixture display only. |
| Next Action | Fixture-display | Read-only local fixture/fallback next action. |

## App Dock Controls

| Control | Action | Category | Notes |
| --- | --- | --- | --- |
| Work Table | `work-table` | Navigation | Opens static Work Table context. |
| App Store | `app-store` | Navigation | Shows static app registry context. |
| Connectors | `connectors` | Navigation | Mock connector context only; no account connections. |
| Calendar | `calendar` | Navigation | Mock future app context only. |
| Notes | `notes` | Navigation | Mock future app context only. |
| Build Queue | `build-queue` | Navigation | Mock future queue context only. |

## Work Table Cards

| Card | Action | Category | Notes |
| --- | --- | --- | --- |
| Project Brief | `project-brief` | Informational | Static project brief context. |
| Prompt Stack | `prompt-stack` | Informational | Static approved-prompt context. |
| Build Instructions | `build-instructions` | Informational | Static instruction context. |
| Tool Output | `tool-output` | Informational | Static terminal/report context. |
| Approval Gate | `approval-gate` | Informational | Displays approval boundary context only. |
| Validation Queue | `validation-queue` | Informational | Displays validation queue context only. |

## Work Table AI

Work Table AI fixture cards, safe mock actions, blocked actions, source references, and approval flags are fixture-display only.

No card, chip, or label executes code.

Future AI-assisted actions require:

- DRY_RUN.
- Human approval.
- Validator coverage.
- Checkpoint report.
- Explicit no-secrets/no-trading boundary.

## Tool Registry Buttons

| Tool | Action | Category | Notes |
| --- | --- | --- | --- |
| ChatGPT | `tool-chatgpt` | Informational | Planning/review lane only. |
| Codex | `tool-codex` | Informational | Approved repo work lane only. |
| Claude | `tool-claude` | Informational | Future review/planning lane only. |
| GitHub | `tool-github` | Approval-required future action | Commits/pushes still require explicit approval. |
| PowerShell | `tool-powershell` | Approval-required future action | Validators only after approval. |
| Web/Research | `tool-web` | Approval-required future action | Public research only after approval. |
| Files/OneDrive | `tool-files` | Approval-required future action | Approved local file inspection only. |
| Reports | `tool-reports` | Approval-required future action | Report writing requires approval. |
| Telemetry | `tool-telemetry` | Approval-required future action | Future telemetry writer remains blocked. |

## App Registry Cards

| App | Action | Category | Notes |
| --- | --- | --- | --- |
| Calendar App | `app-calendar` | Informational | Static app example only. |
| Notes App | `app-notes` | Informational | Static app example only. |
| Reports App | `app-reports` | Approval-required future action | Future report writer requires approval. |
| Telemetry App | `app-telemetry` | Approval-required future action | Future telemetry writer requires approval. |

## Assistant Rail Send Control

Control: `send-message`

Category: mock-only.

Current behavior: replaces the local input value with preview text and updates local mock output only.

It does not send prompts, call live AI, write files, connect accounts, or persist messages.

## Blocked Behavior

The static dashboard must not:

- Call APIs.
- Connect accounts.
- Read or store secrets.
- Install software.
- Deploy.
- Connect brokers.
- Place trades.
- Enable trading execution.
- Run live AI execution.
- Perform destructive file operations.

## Next Action Map Gap

The next validation gap is a command-center readiness validator that confirms the expected control areas, safe labels, and Stage 29-30 docs exist without modifying files.
