# AI_OS Infrastructure Map

Status: foundation draft.

Purpose: record what infrastructure is known from the repository before adding or changing automation.

Doctrine: document infrastructure first. Automate second.

## Scope

This map covers infrastructure and operating surfaces visible in the repository as of this reassessment. It does not claim production readiness.

## Known Infrastructure

| Area | Observed path | Current role | Notes |
|---|---|---|---|
| Local repo workspace | repository root | AI_OS source, governance, docs, validation, reports, automation drafts | Active repo for Codex and GitHub work. |
| Documentation | `docs/` | Project docs, security docs, AI_OS subsystem docs, Trading Lab docs | Existing docs are broad and unevenly organized. |
| Security docs | `docs/security/` | Threat model, approval model, audit logging, secret prevention, repo hygiene | Baseline scaffolds exist. Human review status is not fully proven. |
| Root governance | `AGENTS.md`, `RISK_POLICY.md`, `SECURITY.md`, `COMPLIANCE_BASELINE.md` | Agent rules, risk policy, security policy, compliance baseline | Protected or review-sensitive files. |
| GitHub checks | `.github/workflows/ci.yml` | Basic CI validation on pull requests and pushes to `main` | This is CI, not deployment tooling. |
| Dependency update config | `.github/dependabot.yml` | Weekly dependency update config for GitHub Actions, npm, and pip | Operational status in GitHub settings is UNKNOWN. |
| Dashboard app | `apps/dashboard/` | Browser-based dashboard surface | React/Vite project observed. `apps/dashboard/assets/` is protected by local rules. |
| Trading Lab app | `apps/trading_lab/` | Trading Lab / Forex application code and tests | Default paper/simulation behavior; live broker execution remains blocked by policy unless separately governed. |
| Core Python modules | `aios/` | AI_OS Python modules, including trader-related paper components | Exact production boundary is UNKNOWN. |
| Agent runtime | `agent/` | Local execution agent/runtime area | Detailed runtime activation path is UNKNOWN. |
| Services | `services/` | Approvals, dispatcher, orchestrator, policy, runtime, telemetry, validation | Service deployment target is UNKNOWN. |
| Orchestrator service | `services/orchestrator/` | Workflow state, dispatch, approvals, audit logs | Node package observed. Runtime status is UNKNOWN. |
| Automation scripts | `automation/`, `scripts/` | Existing DRY_RUN/APPLY validators, launchers, status, telemetry, trading lab scripts | No new automation should be created in this foundation pass. |
| Work packets | `work_packets/` | Queue schemas, examples, state examples | Active operational source of truth is UNKNOWN. |
| Reports | `Reports/` | Operator, telemetry, roadmap, trading lab, work intelligence reports | Some appear example or generated. Canonical report flow is partly UNKNOWN. |
| Telemetry | `telemetry/`, `Reports/telemetry/`, `automation/telemetry/` | Local telemetry surfaces and reporting artifacts | Collection boundary and retention policy need consolidation. |
| Validation | `validation/`, `scripts/validation/`, `automation/*Test*.ps1`, tests | Validation scripts and tests | Validator ownership and required chain are not yet centralized. |

## Unknown Infrastructure

- Whether any service is currently running outside local development.
- Whether GitHub branch protection, secret scanning, and required checks are enabled in repository settings.
- Whether CI is passing on the current default branch.
- Whether dashboard builds are currently required for every change.
- Whether `services/orchestrator/` is a prototype, local service, or planned production component.
- Whether `agent/` is active runtime infrastructure or a scaffold.
- Which report directories are canonical versus historical.
- Which automation scripts are approved for operator use and which are drafts.
- Whether external cloud accounts exist for AI_OS. No cloud deployment configuration was created or changed in this pass.
- Whether Claude Code is already installed or only planned as a specialist worker.

## Manual Steps Currently Implied

- Human approval before APPLY work.
- Human review before protected governance file changes.
- Human decision before commit, push, merge, delete, move, rename, credential changes, or trading execution changes.
- Manual selection of the current phase, stage, workload pack, task ID, mode, validator chain, and stop point.
- Manual review of generated reports before they are treated as evidence.
- Manual confirmation that Trading Lab / Forex stage labels match the approved default-execution or broker-readiness state.
- Manual GitHub settings verification for branch protection, secret scanning, and required checks.

## Future IaC Candidates

These are candidates only. Do not implement until architecture and governance are approved.

- GitHub repository settings documentation, then possible policy-as-code for branch protection where supported.
- Local development environment bootstrap documentation, then possible setup script.
- Dashboard dev and preview environment documentation, then possible standard task runner.
- Orchestrator local service runbook, then possible service wrapper.
- Validation chain manifest, then possible validator runner.
- Telemetry storage and retention map, then possible local telemetry bootstrap.
- Report directory ownership map, then possible report index generator.

## Automation Candidates That Should Wait

- Folder and documentation index generators.
- Validator chain orchestration.
- Worker launchers and queue dispatch expansion.
- Dashboard telemetry heatmap generation.
- GitHub PR packaging or selective commit helpers.
- Trading Lab paper route replay automation beyond documented safe paths.
- Any cloud, deployment, or IaC automation.

## Infrastructure Rules

- Document the current state before changing it.
- Mark unverified facts as UNKNOWN.
- Keep live broker execution blocked.
- Keep LLMs out of live order execution paths.
- Prefer local-only telemetry unless a reviewed policy says otherwise.
- Treat automation as an output of stable documentation, not a substitute for it.

## Stop Point

Stop after this foundation is created and validated with `git diff --check`.
