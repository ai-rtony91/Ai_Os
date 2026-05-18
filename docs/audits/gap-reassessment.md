# AI_OS Gap Reassessment

Status: foundation draft.

Purpose: record repo-aware documentation and infrastructure gaps found during the documentation foundation pass.

## Inspection Summary

Observed root areas include:

- `.github/`
- `agent/`
- `aios/`
- `apps/`
- `automation/`
- `docs/`
- `Reports/`
- `scripts/`
- `services/`
- `telemetry/`
- `tests/`
- `validation/`
- `work_packets/`

The repository already contains extensive AI_OS and Trading Lab documentation under `docs/AI_OS/`, plus root security and compliance scaffolds. The requested top-level foundation folders under `docs/` were missing before this pass.

## Key Findings

- Documentation is broad but fragmented across root docs, `docs/security/`, `docs/AI_OS/`, `Reports/`, and automation-adjacent notes.
- CI and Dependabot configuration exist, but GitHub-side settings such as branch protection and secret scanning are UNKNOWN.
- Automation folders are extensive, including DRY_RUN validators and APPLY scripts, but their canonical owner map is not centralized.
- Trading Lab appears to have paper-only modules, reports, validators, and docs, but any real broker boundary must remain blocked.
- Dashboard, services, telemetry, work packets, and reports exist as separate infrastructure surfaces.
- Infrastructure-as-code is not present in the observed foundation path and should not be introduced before documentation stabilizes.

## Documentation Gaps

- Canonical infrastructure map was missing at the requested top-level `docs/infrastructure/` path.
- Top-level operating doctrine was missing at `docs/governance/`.
- Continuous improvement workflow was missing at `docs/workflows/`.
- Architecture and prompt foundation directories were missing at the top-level `docs/` path.
- The relationship between root docs, `docs/security/`, `docs/AI_OS/`, and `Reports/` is not yet indexed.
- Canonical report ownership and retention rules are incomplete.
- Canonical validator chain per subsystem is not fully defined.
- Worker role boundaries are partly documented in nested docs, but not yet consolidated at the top level.

## Unknowns

- UNKNOWN: current default branch protection settings.
- UNKNOWN: current GitHub secret scanning state.
- UNKNOWN: which automation scripts are approved operator entry points.
- UNKNOWN: which generated reports are authoritative.
- UNKNOWN: whether orchestrator and dashboard services are actively run together.
- UNKNOWN: whether any external cloud infrastructure exists outside this repository.
- UNKNOWN: whether Claude Code is currently installed and available in the operator environment.

## Manual Steps Needing Documentation

- Starting a normal AI_OS session.
- Selecting a phase, stage, workload pack, and task ID.
- Choosing DRY_RUN versus APPLY.
- Selecting and running validators.
- Reviewing generated reports.
- Preparing a selective commit when requested.
- Confirming Trading Lab paper-only boundaries.
- Reviewing GitHub CI and repository settings.

## Future IaC Candidates

Do not implement yet.

- GitHub repository policy documentation and possible settings automation.
- Local dev environment bootstrap after manual setup is documented.
- Dashboard and orchestrator run configuration after ownership is clear.
- Validator chain manifest after subsystem validation rules are consolidated.
- Telemetry storage map after retention and privacy rules are reviewed.

## Automation Candidates That Should Wait

- Documentation index generation.
- Report index generation.
- Validator orchestration.
- Worker queue routing expansion.
- Claude Code worker handoff automation.
- Dashboard telemetry visualizations.
- GitHub branch or PR automation.
- Any Terraform, CloudFormation, CI/CD expansion, or deployment tooling.

## Documentation Authority and Labeling Gaps

These gaps were identified in the 2026-05-18 consolidation pass:

### Unlabeled Documentation

- UNKNOWN: how many files under `docs/AI_OS/` carry a status label (DRAFT, CURRENT,
  HISTORICAL, SUPERSEDED). The majority appear unlabeled.
- UNKNOWN: how many files under `Reports/` are canonical versus generated examples.
- Gap: no systematic labeling pass has been done across `docs/AI_OS/` to distinguish
  active standards from historical planning artifacts.

### Historical Trading and OANDA Language

- The AI_OS whitepaper (`docs/AI_OS_White_Paper.md`, `docs/White_Paper.md`) contains
  language referencing live trading, OANDA integration, and broker execution as planned
  or active capabilities.
- Status of these documents: UNKNOWN — not yet reviewed against current trading boundary policy.
- Risk: agents or workers that read these files without a HISTORICAL label may treat the
  language as current policy.
- Required action: label these files HISTORICAL or SUPERSEDED before any agent references them.
  This action requires operator review and approval before editing protected or near-protected docs.

### Orchestration Document Proliferation

- `docs/AI_OS/orchestration/` contains approximately 40 documents.
- UNKNOWN: which of these are active standards versus historical planning drafts.
- Gap: no index or canonical document distinguishes the active orchestration model from
  historical phase-specific planning files.
- The new `AI_OS_ORCHESTRATION_MODEL.md` is the intended canonical reference going forward.
  Prior orchestration docs should be reviewed and labeled.

### Claude Delegation Standard

- Gap: no standard existed for structuring Claude Code task packets before 2026-05-18.
- Created: `docs/AI_OS/claude/CLAUDE_DELEGATION_STANDARD.md`.
- UNKNOWN: whether existing ad-hoc Claude invocations during prior sessions followed
  equivalent boundaries.

### Worker Interface Standard

- Created: `docs/AI_OS/interface/AI_OS_WORKER_INTERFACE_SPECIFICATION_DRAFT.md`.
- Gap: existing worker outputs in Reports/ and orchestration docs do not uniformly follow
  the 7-region layout. Adoption requires a separate standardization pass.

### New Gaps Added to Watch List

| Gap | Severity | Status |
|-----|----------|--------|
| Historical trading/OANDA docs not yet labeled | High | UNKNOWN — review required |
| docs/AI_OS/ files without status labels | Medium | UNKNOWN — no systematic audit yet |
| Orchestration doc proliferation — active vs historical | Medium | UNKNOWN |
| Reports/ canonical vs generated distinction | Medium | UNKNOWN |
| Existing Claude invocations without delegation packets | Low | UNKNOWN — prior sessions |

## Recommended Next Reassessment

Perform a docs index consolidation pass that maps:

- root governance docs
- `docs/security/`
- `docs/AI_OS/`
- Trading Lab docs
- report directories
- validator locations

Priority during that pass:
1. Identify and label historical trading/OANDA whitepaper language.
2. Triage `docs/AI_OS/orchestration/` into active vs historical.
3. Apply status labels to unlabeled docs/AI_OS/ files.

Stop before creating automation.
