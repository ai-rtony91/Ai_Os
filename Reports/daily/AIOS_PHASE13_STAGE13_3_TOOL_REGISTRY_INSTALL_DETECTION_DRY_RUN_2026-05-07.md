# AI_OS Phase 13 Stage 13.3 Tool Registry Install + Detection Readiness DRY_RUN

Date: 2026-05-07
Mode: DRY_RUN
Classification: AI_OS project work only

## Phase

Phase 13 - Dashboard UI Implementation

## Stage

Stage 13.3 - Tool Registry Install + Detection Readiness

## Mission

Plan how the dashboard Tool Registry lane can become a readiness/status system without installing software, connecting accounts, storing secrets, or editing dashboard code during DRY_RUN.

## Precheck

Result: CLEAN

Evidence:

- `git status --short --branch` returned `## main...origin/main`

## Safe Read-Only Detection Performed

No installs, account connections, credential reads, broker calls, API calls, or dashboard edits were performed.

Observed local detection:

- Codex: INSTALLED
  - `where.exe codex` found npm shims under `C:\Users\mylab\AppData\Roaming\npm`
  - `codex --version` returned `codex-cli 0.129.0`
- Git: INSTALLED
  - `git --version` returned `git version 2.54.0.windows.1`
  - repo remote points to `https://github.com/ai-rtony91/Ai_Os.git`
- GitHub CLI: MISSING
  - `gh --version` was not recognized
- Windows PowerShell: READY
  - `$PSVersionTable.PSVersion` returned `5.1.26100.8346`
  - execution policy read-only check returned LocalMachine `Bypass`
- PowerShell 7 / pwsh: MISSING
  - `where.exe pwsh` did not find a path
- Browser command detection: UNKNOWN
  - `Get-Command msedge,chrome,firefox` returned no command entries in this shell context
- OneDrive/repo path: READY
  - `$env:OneDrive` exists
  - active repo path resolved successfully
- Reports module folders: READY
  - Reports/daily exists
  - Reports/checkpoints exists
  - Reports/health exists
  - Reports/progress exists
- Claude local path hints: INSTALLED_OR_CONFIG_PRESENT
  - `%LOCALAPPDATA%\Claude` exists
  - `%APPDATA%\Claude` exists
  - no login automation performed
- ChatGPT app path hint: INSTALLED_OR_CONFIG_PRESENT
  - `%LOCALAPPDATA%\Microsoft\WindowsApps\ChatGPT.exe` exists
  - no login automation performed
- automation/tools folder: MISSING
  - planned APPLY may create it if approved

## Tool Buttons Mapped

- ChatGPT
- Codex
- Claude
- GitHub
- PowerShell
- Web/Research
- Files/OneDrive
- Reports
- Telemetry

## Status Values

- READY
- INSTALLED
- MISSING
- NEEDS_LOGIN
- NEEDS_CONFIG
- BLOCKED
- INTERNAL_MODULE
- NOT_APPLICABLE
- UNKNOWN

## Detection Plan

ChatGPT:

- Detect local app/browser access if available.
- Do not inspect credentials.
- Manual status may be READY or NEEDS_LOGIN.

Codex:

- Run `where.exe codex`.
- Run `codex --version` if command exists.
- Optionally detect npm/global path if available.

Claude:

- Detect desktop/config folder path hints only.
- Do not launch app.
- Do not automate login.
- Manual sign-in status only.

GitHub:

- Run `git --version`.
- Run `gh --version` if available.
- Run `gh auth status` only in a future approved read-only validator if operator accepts the privacy boundary.
- Check repo remote with `git remote -v`.

PowerShell:

- Read `$PSVersionTable`.
- Detect `pwsh` availability.
- Read execution policy only.

Web/Research:

- Detect browser presence only.
- No scraping.
- No external automation.

Files/OneDrive:

- Detect OneDrive path.
- Detect repo root.
- Do not upload/download/sync-trigger files.

Reports:

- Detect Reports folder.
- Detect daily/checkpoints/health/progress subfolders.

Telemetry:

- Detect telemetry report/template folders and health report placeholders.
- Do not connect a live telemetry service.

## Install Readiness Plan

Future APPLY should create a checklist that:

- separates detection from installation
- marks missing tools without installing them
- lists optional install candidates
- requires human approval before any install
- blocks winget/npm/choco installers by default
- requires separate approval for account login or auth checks
- records UNKNOWN instead of guessing

## Auth Boundary Plan

- No passwords, tokens, recovery codes, API keys, or credentials are stored.
- No account connection automation.
- No OAuth/browser login automation.
- `gh auth status` is treated as optional read-only and must be operator-approved before use in APPLY validators.
- ChatGPT, Claude, OpenAI, Azure, GitHub, Bitwarden, and broker accounts remain manual/operator-controlled.

## Dashboard Status Contract

Planned fixture fields:

- tool_id
- label
- category
- desired_status
- detected_status
- installed
- command
- version
- path_hint
- needs_login
- needs_config
- blocked_reason
- last_checked
- notes

The dashboard should render:

- READY
- INSTALLED
- MISSING
- NEEDS_LOGIN
- NEEDS_CONFIG
- BLOCKED
- INTERNAL_MODULE
- NOT_APPLICABLE
- UNKNOWN

## Files To Create On APPLY

- docs/AI_OS/tools/AIOS_TOOL_REGISTRY_STATUS_MODEL_DRAFT.md
- docs/AI_OS/tools/AIOS_TOOL_INSTALL_READINESS_CHECKLIST_DRAFT.md
- docs/AI_OS/tools/AIOS_TOOL_REGISTRY_DASHBOARD_STATUS_CONTRACT_DRAFT.md
- docs/AI_OS/tools/AIOS_TOOL_AUTH_BOUNDARY_RULES_DRAFT.md
- automation/tools/Test-AiOsToolRegistryReadiness.DRY_RUN.ps1
- automation/tools/Get-AiOsToolRegistrySnapshot.DRY_RUN.ps1
- apps/dashboard/mock-data/tool-registry-status-fixture.example.json
- Reports/health/AIOS_TOOL_REGISTRY_HEALTH_TEMPLATE.md

## Progress Ledger Proposal

Do not append during DRY_RUN.

Proposed row:

`2026-05-07,,Phase 13 Stage 13.3,AIOS-P13-S13-3-DRYRUN,Tool Registry Install + Detection Readiness,5,1,20,DRY_RUN_COMPLETE_PENDING_APPLY,false,,Create missing tool registry planning docs and read-only validators after approval,Reports/checkpoints/CHECKPOINT_2026-05-07_PHASE13_STAGE13_3_TOOL_REGISTRY_INSTALL_DETECTION_DRY_RUN.md,d78d609,clean,DRY_RUN only`

## Safety Blocks Confirmed

- No installs.
- No winget installs.
- No Windows settings changes.
- No secrets.
- No credentials.
- No account connections.
- No external APIs.
- No database connection.
- No brokers.
- No live AI API connection.
- No deployment.
- No dashboard HTML/CSS/JS edits.
- No protected root governance file edits.
- No dual Codex / POI / worktree files.

## DRY_RUN Result

DRY_RUN_COMPLETE_PENDING_APPLY

## Next Safe Action

Wait for explicit APPLY approval before creating the planned docs, local fixture, and read-only PowerShell validators.
