# Phase 5F High-Value Source Extraction Plan

Status: extraction planning only
Branch: `v2/aios`
Source audit: `docs/audits/phase-5e-docs-aios-leftover-classification.md`

This plan inspects selected CLEAN-era source docs and identifies V2-safe content worth promoting later. It does not edit source docs, canonical docs, runtime, orchestration, dashboard, trading, telemetry, launchers, archive, or protected paths.

## Executive Summary

The inspected CLEAN-era sources contain useful operational doctrine, but most should be promoted as compact canonical sections, not copied wholesale.

Highest-value extraction themes:

- Change request fields and scoped change packages.
- Safe APPLY checklist details.
- Commit package rules.
- API, connector, dashboard, UI, and Trading Lab change boundaries.
- Problem classification, collision handling, repair flow, rollback limits, and validator routing.
- Codex execution discipline that aligns with existing AGENTS/workflow rules.

Primary canonical targets:

- `docs/workflows/OPERATOR_WORKFLOW.md`
- `docs/workflows/APPLY_ROUTING_CHAIN.md`
- `docs/workflows/PARALLEL_CODEX_WORKFLOW.md`
- proposed new `docs/workflows/CHANGE_CONTROL.md`
- proposed new `docs/workflows/SAFE_REPAIR_WORKFLOW.md`
- `docs/security/approval-model.md`
- `docs/governance/operational-doctrine.md`
- `docs/governance/FILE_PLACEMENT_RULES.md`

Do not promote old repo paths, `docs/AI_OS` authority wording, CLEAN-era active repo identity, dashboard-specific dock-player examples as general doctrine, or any approval bypass language.

## Source 1: Rules And Guardrails

| Field | Detail |
|---|---|
| Exact source path | `docs/AI_OS/system_wizards/05_RULES_AND_GUARDRAILS.md` |
| Proposed canonical target | `docs/governance/operational-doctrine.md`; selected overlap already covered by `AGENTS.md` |
| Exact section to create/update later | Add or update `## Evidence And Quality Gates` |
| Risk level | low |
| Recommendation | partially promote later |

### Useful Content Found

- Use exact paths.
- Keep actions bounded and auditable.
- Mark unknown facts as `UNKNOWN`.
- Mark conflicting evidence as `INVALID DATA`.
- Prefer one major action at a time.
- Verify outputs before proceeding.
- Avoid redundant regeneration of unchanged content.
- Keep AI_OS system docs separate from trading execution logic unless explicitly justified.
- Completion gates: scope check, architecture lock, protected-action check, report format.

### What NOT To Copy

- Do not copy broad "no file deletion/renaming/moving" as an absolute if a later user-approved move/archive pass exists.
- Do not copy "architecture lock" wording without defining current V2 architecture authority.
- Do not duplicate AGENTS.md safety rules verbatim.

### Unsafe/Stale Wording

- Any implication that this CLEAN-era file is the active guardrail source.
- Any wording that conflicts with approved APPLY or explicitly approved move/delete/rename passes.

### Later Promotion Shape

Promote as a concise quality-gate subsection:

- exact-path requirement
- UNKNOWN/INVALID DATA handling
- bounded action requirement
- output verification before next step
- system-docs versus trading-execution separation

## Source 2: Codex Orchestration Playbook

| Field | Detail |
|---|---|
| Exact source path | `docs/AI_OS/codex/AIOS_CODEX_ORCHESTRATION_PLAYBOOK.md` |
| Proposed canonical target | `AGENTS.md`; `docs/workflows/OPERATOR_WORKFLOW.md`; `docs/security/approval-model.md` |
| Exact section to create/update later | `AGENTS.md` `## Core Workflow`; `docs/workflows/OPERATOR_WORKFLOW.md` `## Standard Loop`; `docs/security/approval-model.md` `## Protected Actions` |
| Risk level | medium |
| Recommendation | partially promote later |

### Useful Content Found

- Plan first.
- DRY_RUN preferred.
- Human approval before APPLY.
- Validate outputs before commit.
- Preserve evidence and reports.
- Maintain rollback capability.
- Validation types: path validation, file existence validation, protected-file validation, JSON parse validation, Markdown/report validation, git clean-state validation.
- Forbidden behaviors: silent overwrites, unverified deletes, hidden automation activation, unauthorized startup tasks, LLM placement in live trading path.

### What NOT To Copy

- Do not copy the standard chain as mandatory push/commit sequence. V2 separates commit and push approval.
- Do not copy `Active repo: C:\Dev\Ai.Os`.
- Do not copy CLEAN-era repo identity.
- Do not copy wording that implies all work must proceed to commit/push.

### Unsafe/Stale Wording

- The active repo path points to the prior CLEAN identity, not `AI_OS_V2`.
- The chain includes `Git push`; V2 requires explicit separate approval and this prompt does not authorize push.

### Later Promotion Shape

Promote validation-type checklist into `docs/workflows/OPERATOR_WORKFLOW.md` or `docs/security/approval-model.md`:

- path validation
- file existence validation
- protected-file validation
- JSON parse validation when JSON changes
- Markdown/report validation when docs/reports change
- git status/diff validation before commit approval

## Source 3: Parallel Codex Workflow

| Field | Detail |
|---|---|
| Exact source path | `docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md` |
| Proposed canonical target | `docs/workflows/PARALLEL_CODEX_WORKFLOW.md` |
| Exact section to create/update later | `## Worker Report Contract`; `## Validation`; optional `## Legacy Launcher Notes` if retained |
| Risk level | medium |
| Recommendation | partially promote later |

### Useful Content Found

- DRY_RUN workers may run at the same time.
- APPLY work must run one worker at a time.
- Validation after each APPLY.
- Commit only after whole batch validates cleanly.
- Push only after explicit operator approval.
- Worker report fields: worker number, label, lane, allowed paths, blocked paths, report target, DRY_RUN rules, prompt seed, stop condition.
- Codex launch config defaults disabled/UNKNOWN with instruction-window fallback.
- Do not hardcode local Codex path.
- Validator checks exactly 8 workers, disabled launch config, allowed/blocked paths, prompt seed, report conflicts, no deletes, no protected root files.

### What NOT To Copy

- Do not copy hardcoded 8-worker model as universal V2 rule.
- Do not copy `docs/AI_OS/trading_laboratory/...` lane paths as canonical V2 destinations.
- Do not copy launcher commands as active run instructions unless current automation is validated.
- Do not copy `Reports/` paths as canonical report authority without output/retention review.

### Unsafe/Stale Wording

- Worker lanes for TradingView, TradersPost, Latency, and Git QC may not match current allowed lane list.
- Source references `AIOS_PARALLEL_WORKER_REGISTRY.json` without confirming current path.
- Source mentions launchers; current task forbids launcher edits.

### Later Promotion Shape

Update canonical `docs/workflows/PARALLEL_CODEX_WORKFLOW.md` only with:

- instruction-window fallback principle
- "do not hardcode local Codex path"
- extra worker report fields if missing
- push once only after explicit approval

Leave launcher commands and old lane paths out unless separately validated.

## Source 4: APPLY Approval Workflow Draft

| Field | Detail |
|---|---|
| Exact source path | `docs/AI_OS/operator/AIOS_APPLY_APPROVAL_WORKFLOW_DRAFT.md` |
| Proposed canonical target | `docs/workflows/APPLY_ROUTING_CHAIN.md`; `docs/security/approval-model.md` |
| Exact section to create/update later | `docs/security/approval-model.md` `## APPLY Approval Checklist`; optional `docs/workflows/APPLY_ROUTING_CHAIN.md` `## Approval Review` |
| Risk level | low |
| Recommendation | promote later |

### Useful Content Found

- Read DRY_RUN.
- Confirm file list.
- Confirm no protected action.
- Approve APPLY with exact prompt.
- Verify APPLY report.
- Stop if unknowns affect safety.

### What NOT To Copy

- Do not copy draft status.
- Do not duplicate existing APPLY chain fields if target already covers them.
- Do not imply APPLY approval covers commit, push, merge, or protected actions outside named scope.

### Unsafe/Stale Wording

- None material. It is short, but incomplete.

### Later Promotion Shape

Promote as a compact checklist in `docs/security/approval-model.md`:

- DRY_RUN reviewed
- exact file list confirmed
- protected actions checked
- exact APPLY prompt/scope approved
- APPLY report verified
- safety-affecting unknowns block approval

## Source 5: change_control/

| Field | Detail |
|---|---|
| Exact source path | `docs/AI_OS/change_control/` |
| Proposed canonical target | proposed new `docs/workflows/CHANGE_CONTROL.md`; `docs/security/approval-model.md`; `docs/governance/FILE_PLACEMENT_RULES.md` |
| Exact section to create/update later | New `docs/workflows/CHANGE_CONTROL.md` with `## Change Request Fields`, `## Scope Rules`, `## Boundary Rules`, `## Commit Package Rules`, `## Safe APPLY Checklist` |
| Risk level | medium |
| Recommendation | promote later |

### Useful Content Found

Files inspected:

- `README.md`
- `CHANGE_REQUEST_TEMPLATE.md`
- `CHANGE_SCOPE_RULES.md`
- `SAFE_APPLY_CHECKLIST.md`
- `COMMIT_PACKAGE_RULES.md`
- `API_CHANGE_BOUNDARY.md`
- `CONNECTOR_CHANGE_BOUNDARY.md`
- `DASHBOARD_CHANGE_BOUNDARY.md`
- `UI_CHANGE_BOUNDARY.md`
- `TRADING_LAB_CHANGE_BOUNDARY.md`
- `CHANGE_OWNERSHIP_MAP.json`
- `CHANGE_STATUS_LEDGER.json`

High-value extract:

- Every change request names user goal, change type, owner/agent, allowed files, blocked files, DRY_RUN requirement, APPLY approval, validation, commit package, rollback note, and safety boundary.
- Keep one focused package per change.
- Stop and ask for DRY_RUN clarification if scope is unclear.
- `git add .` is blocked.
- Push requires separate approval.
- API/connector work is planning-only unless separately approved; real credentials, tokens, network calls, background sync, broker/OANDA activation, and secret storage are blocked.
- Dashboard planning lives in docs; dashboard code lives in `apps/dashboard/`; exact dashboard paths are required for dashboard edits.
- UI changes must not mix with Trading Lab logic, connector activation, API activation, or product docs unless explicitly approved.
- Trading Lab is paper-only; live trading, broker routing, OANDA execution, API keys, real webhooks, real orders, account login, automatic trade placement, background trading, and scheduled trading are blocked.

### What NOT To Copy

- Do not copy `docs/AI_OS/...` planning paths as V2 canonical destinations.
- Do not copy JSON maps as active hidden authority.
- Do not copy dashboard-specific private media paths unless confirmed current.
- Do not copy owner-agent labels as active staffing unless V2 keeps those agent roles.
- Do not copy examples that imply Trading Lab code paths are under `docs/AI_OS/trading_laboratory/`.

### Unsafe/Stale Wording

- `CHANGE_OWNERSHIP_MAP.json` contains CLEAN-era allowed planning paths under `docs/AI_OS`.
- `CHANGE_STATUS_LEDGER.json` is a ledger-like structured file inside docs; if active, it should move to schemas/state governance later, not remain hidden authority.
- UI/dashboard examples are specific and may not represent all current dashboard paths.

### Later Promotion Shape

Create a new canonical workflow file later:

`docs/workflows/CHANGE_CONTROL.md`

Recommended sections:

- `## Purpose`
- `## Change Request Fields`
- `## Scope Rules`
- `## Boundary Rules`
- `## Safe APPLY Checklist`
- `## Commit Package Rules`
- `## Blocked By Default`

Promote only the markdown doctrine. Treat JSON files as source material for a later schema/registry decision.

## Source 6: problem_resolution/

| Field | Detail |
|---|---|
| Exact source path | `docs/AI_OS/problem_resolution/` |
| Proposed canonical target | proposed new `docs/workflows/SAFE_REPAIR_WORKFLOW.md`; `docs/workflows/CHANGE_CONTROL.md`; `docs/security/approval-model.md` |
| Exact section to create/update later | New `docs/workflows/SAFE_REPAIR_WORKFLOW.md` with `## Problem Classification`, `## Repair Scope`, `## Collision Handling`, `## Validator Routing`, `## Rollback Rules`, `## Verification Checklist` |
| Risk level | medium |
| Recommendation | promote later |

### Useful Content Found

Files inspected:

- `README.md`
- `PROBLEM_CLASSIFICATION_RULES.md`
- `CHANGE_COLLISION_RULES.md`
- `SAFE_REPAIR_FLOW.md`
- `SAFE_ROLLBACK_GUIDE.md`
- `REPAIR_SCOPE_TEMPLATE.md`
- `VALIDATOR_ROUTING_RULES.md`
- `FIX_VERIFICATION_CHECKLIST.md`
- `UI_PROBLEM_PATTERNS.md`
- `PROBLEM_TO_OWNER_MAP.json`

High-value extract:

- Problem classification before repair.
- Categories: UI-only, logic-only, mock-data-only, Trading-Lab-only, connector/API-only, validator gap, mixed scope.
- If category is unclear, mark `UNKNOWN` and do not repair.
- Collision result: stop, mark mixed scope, split into smaller repair requests, route each through change control.
- Safe repair flow: issue, category, owner, affected files, blocked files, repair type, change-control check, validators, rollback note, scoped APPLY prompt, wait for approval.
- Rollback is scoped and approved; broad `git reset --hard`, `git clean`, deleting, moving, renaming, broad checkout, and `.codex_backups/` access are blocked by default.
- Validator routes should inspect and report before a change is trusted.
- Validators may recommend repair work but must not repair automatically unless separately APPLY-approved.
- Fix verification checklist: category, owner, allowed/blocked files, isolated repair type, validators passed, no secrets/API/broker/OANDA/live trading/real webhook/real order path, rollback note, focused commit package, no `git add .`.

### What NOT To Copy

- Do not copy dock-player examples as general canonical doctrine except as optional examples.
- Do not copy owner-agent labels as active V2 staffing.
- Do not copy `docs/AI_OS/change_control/` as a canonical link target.
- Do not copy JSON problem-to-owner map as hidden authority without schema/registry decision.
- Do not copy dashboard file examples unless validated as current.

### Unsafe/Stale Wording

- Several examples are dock-player-specific and may overfit the canonical workflow.
- `PROBLEM_TO_OWNER_MAP.json` uses CLEAN-era paths and role names.
- Problem resolution feeds `docs/AI_OS/change_control/`, which should become a V2 canonical path if promoted.

### Later Promotion Shape

Create a new canonical workflow file later:

`docs/workflows/SAFE_REPAIR_WORKFLOW.md`

Promote only generic repair doctrine:

- classify before repair
- identify owner and affected files
- list blocked files
- decide one isolated repair type
- route through change control
- run validators
- require rollback note
- wait for APPLY approval
- verify before commit

## Proposed Canonical Targets

| Proposed target | Source content to promote | Notes |
|---|---|---|
| `docs/workflows/CHANGE_CONTROL.md` | Change request fields, scope rules, boundary rules, safe APPLY checklist, commit package rules | New canonical workflow recommended. |
| `docs/workflows/SAFE_REPAIR_WORKFLOW.md` | Problem classification, collision handling, safe repair flow, rollback guide, validator routing, fix checklist | New canonical workflow recommended. |
| `docs/workflows/PARALLEL_CODEX_WORKFLOW.md` | Instruction-window fallback principle, no hardcoded local Codex path, extra report fields, explicit push approval | Update existing canonical workflow later. |
| `docs/security/approval-model.md` | APPLY approval checklist and safety-affecting unknowns block | Update existing canonical security doc later. |
| `docs/governance/operational-doctrine.md` | UNKNOWN/INVALID DATA handling, exact paths, bounded/auditable actions, verify outputs before proceeding | Update existing canonical governance doc later. |
| `AGENTS.md` | Possibly no edit needed now; most extracted rules are already present or better suited to workflow docs | Protected root file; avoid unless a later approved root-governance edit is needed. |

## User Decisions Needed

1. Should Phase 5G create new canonical files `docs/workflows/CHANGE_CONTROL.md` and `docs/workflows/SAFE_REPAIR_WORKFLOW.md`, or fold the material into existing workflow docs?
2. Should `CHANGE_OWNERSHIP_MAP.json`, `CHANGE_STATUS_LEDGER.json`, and `PROBLEM_TO_OWNER_MAP.json` be treated as historical source, future schemas, or future registries?
3. Should `AGENTS.md` remain untouched because existing rules already cover the extracted doctrine, or should a later protected-root edit add validation-type language?
4. Should dashboard/dock-player examples be excluded entirely from canonical workflow docs, or kept as examples in a short appendix?
5. Should old worker/launcher command references from the parallel Codex source be validated before any canonical update?

## Next Safe Edit Batch Recommendation

For Phase 5G, make a planning-approved canonical docs edit only:

1. Create `docs/workflows/CHANGE_CONTROL.md`.
2. Create `docs/workflows/SAFE_REPAIR_WORKFLOW.md`.
3. Update `docs/security/approval-model.md` with a compact `## APPLY Approval Checklist`.
4. Do not edit `AGENTS.md` yet.
5. Do not edit `docs/AI_OS/`.
6. Do not copy CLEAN-era paths as canonical paths.
7. Run `git diff --check`.
8. Run `git status --short --branch`.

## Explicit Non-Actions

- No source docs were edited.
- No canonical docs were edited by this extraction plan.
- No files were moved, deleted, renamed, archived, staged, committed, or pushed.
- Runtime, orchestration, dashboard, Trading Lab, telemetry, launchers, archive, secrets, credentials, broker paths, and protected operational paths were not touched.
