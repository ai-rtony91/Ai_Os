# Phase 196 Active Authority Canonicalization

Branch: `phase-189-high-risk-doctrine-review`
Date: 2026-05-19

## Starting Point

Phase 195 proved there is no safe bulk archive path for the remaining `docs/AI_OS` tree. The remaining material is tangled active authority: validators, dashboard fixtures, governance maps, runtime fixtures, and workflow docs still point into `docs/AI_OS`.

This phase converts high-value authority into canonical docs outside `docs/AI_OS`. It does not delete files, does not bulk archive, and does not repoint active runtime/model fixtures.

## Files Inspected

- `docs/audits/phase-195-final-reaper-unblock-archive-plan.md`
- `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md`
- `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md`
- `docs/governance/operational-doctrine.md`
- `docs/governance/aios-governance-model.md`
- `docs/AI_OS/operator`
- `docs/AI_OS/operator_workflows`
- `docs/workflows/aios-operator-workflows.md`
- `docs/AI_OS/telemetry`
- `automation/status/Test-AiOsLifetimeDevelopmentTelemetry.DRY_RUN.ps1`
- `automation/status/Test-AiOsTelemetryReportingPersistenceReadiness.DRY_RUN.ps1`
- `docs/AI_OS/agent_runtime`
- `automation/agent_runtime`
- `apps/dashboard/mock-data/aios-orchestration-control-room.example.json`
- `docs/AI_OS/security`
- `docs/security/secret-prevention.md`
- `docs/security/approval-model.md`

## Canonical Docs Created Or Updated

### `docs/governance/FILE_PLACEMENT_RULES.md`

- Source docs used: `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md`.
- Authority preserved: placement rules, planning-vs-implementation split, report rules, telemetry boundaries, broker/OANDA blocks, legal/compliance/monetization boundaries, fail-closed rules, blocked-action matrix.
- Replaces conceptually: the active placement doctrine in `docs/AI_OS/governance`.
- Old docs archive-ready now: NO. Active validators and governance references still point at `docs/AI_OS/governance`.

### `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md`

- Source docs used: `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md`.
- Authority preserved: owner categories, allowed contents, blocked contents, high-risk folder boundaries, protected root boundary, archive-before-delete rule.
- Replaces conceptually: the active folder ownership map in `docs/AI_OS/governance`.
- Old docs archive-ready now: NO. This pass created a canonical map but did not retire validator references.

### `docs/workflows/OPERATOR_WORKFLOW.md`

- Source docs used: `docs/AI_OS/operator`, `docs/AI_OS/operator_workflows`, `docs/workflows/aios-operator-workflows.md`.
- Authority preserved: inspect-plan-approve-apply-validate-report loop, human approval gates, clean stop conditions, final report contract.
- Replaces conceptually: general operator workflow drafts.
- Old docs archive-ready now: NO. Dashboard mock data, router validators, and status validators still point at `docs/AI_OS/operator` and `docs/AI_OS/operator_workflows`.

### `docs/workflows/PARALLEL_CODEX_WORKFLOW.md`

- Source docs used: `docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md`.
- Authority preserved: parallel DRY_RUN lanes, serial APPLY lane, worker reports, validation, no commit/push from workers.
- Replaces conceptually: parallel Codex crew workflow doctrine.
- Old docs archive-ready now: NO.

### `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md`

- Source docs used: `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md`.
- Authority preserved: branch naming, lane metadata, path ownership, collision handling.
- Replaces conceptually: worker branch and lane rules.
- Old docs archive-ready now: NO.

### `docs/workflows/SAFE_SESSION_RESUME.md`

- Source docs used: `docs/AI_OS/operator_workflows/AIOS_SAFE_SESSION_RESUME_STANDARD.md`.
- Authority preserved: resume evidence, restore rules, stale/invalid state handling, no automatic execution resume.
- Replaces conceptually: safe session resume standard.
- Old docs archive-ready now: NO.

### `docs/workflows/APPLY_ROUTING_CHAIN.md`

- Source docs used: `docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md`.
- Authority preserved: DRY_RUN to APPLY candidate chain, required evidence, blocked conditions, non-automation statement.
- Replaces conceptually: APPLY routing chain doctrine.
- Old docs archive-ready now: NO.

### `docs/concepts/aios-telemetry-data-model-concepts.md`

- Source docs used: `docs/AI_OS/telemetry`.
- Authority preserved: evidence-backed telemetry, `UNKNOWN`/`PARTIAL` handling, blocked data classes, no-real-collector boundary, storage boundary, user/app/business telemetry split, privacy and retention boundaries, mismatch reporting.
- Replaces conceptually: telemetry data model doctrine.
- Old docs archive-ready now: NO. Telemetry validators still read exact legacy contracts.

### `docs/architecture/AGENT_RUNTIME_ARCHITECTURE.md`

- Source docs used: `docs/AI_OS/agent_runtime`.
- Authority preserved: local file-based runtime model, task flow, task state boundary, active fixture list, worker boundary, approval and validation requirements.
- Replaces conceptually: architectural summary only.
- Old docs archive-ready now: NO. Runtime JSON fixtures remain active and must stay in place.

### `docs/security/SECURE_ACCESS_DOCS_CANONICAL_LINEAGE.md`

- Source docs used: `docs/AI_OS/security/secure_access`, `docs/AI_OS/security/phase_15_secure_access`.
- Authority preserved: lineage decision, secure access boundary, archive-candidate caution for phase-specific lineage.
- Replaces conceptually: lineage ambiguity between `secure_access` and `phase_15_secure_access`.
- Old docs archive-ready now: NO. Security validators/references need a separate review.

### `docs/security/ACCESS_MODEL_OVERVIEW.md`

- Source docs used: `docs/AI_OS/security/secure_access/AIOS_ACCESS_MODEL_OVERVIEW.md`.
- Authority preserved: Cloudflare Access, Microsoft Entra, YubiKey/passkey, GitHub identity separation, trading safety boundary.
- Replaces conceptually: access model overview.
- Old docs archive-ready now: NO.

### `docs/security/PRIVACY_CREDENTIAL_EXCLUSION_CHECKLIST.md`

- Source docs used: `docs/AI_OS/security/AIOS_PRIVACY_CREDENTIAL_EXCLUSION_CHECKLIST_DRAFT.md`.
- Authority preserved: blocked credential/private/broker/live market data classes, fail-closed rule, mismatch rule.
- Replaces conceptually: privacy and credential exclusion checklist.
- Old docs archive-ready now: NO.

## Live Wires Repointed

None.

No live wires were repointed in this phase because the highest-risk references are active validators, dashboard mock-data source references, or exact runtime fixture checks. The canonical docs now exist, but blocker retirement should happen in dedicated subsystem packets.

## Live Wires Not Repointed

- `automation/agent_runtime/*`
  - Old path: `docs/AI_OS/agent_runtime`
  - Reason not safe yet: active runtime JSON fixtures and snapshot readers still use exact paths.
  - Required next action: create an agent runtime blocker-retirement packet only after a new active fixture destination is designed or the existing folder is explicitly retained.
- `apps/dashboard/mock-data/aios-orchestration-control-room.example.json`
  - Old path: `docs/AI_OS/agent_runtime/...`
  - Reason not safe yet: source references are dashboard fixture/model inputs.
  - Required next action: leave until fixture migration is approved and validated.
- `automation/status/Test-AiOsLifetimeDevelopmentTelemetry.DRY_RUN.ps1`
  - Old path: `docs\AI_OS\telemetry\AIOS_LIFETIME_DEVELOPMENT_TELEMETRY_*`
  - Reason not safe yet: validator checks exact evidence/storage contracts and fixture safety.
  - Required next action: telemetry validator retirement packet can repoint to `docs/concepts/aios-telemetry-data-model-concepts.md` only after equivalent phrase checks are designed.
- `automation/status/Test-AiOsTelemetryReportingPersistenceReadiness.DRY_RUN.ps1`
  - Old path: multiple `docs/AI_OS/telemetry` boundary docs.
  - Reason not safe yet: validates exact persistence-readiness boundary files.
  - Required next action: telemetry persistence validator repoint packet.
- `apps/dashboard/mock-data/aios-apply-routing-v1.example.json`
  - Old path: `docs/AI_OS/operator_workflows/...`
  - Reason not safe yet: dashboard fixture source references need semantic review before repoint.
  - Required next action: operator workflow fixture repoint packet using `docs/workflows/APPLY_ROUTING_CHAIN.md`, `SAFE_SESSION_RESUME.md`, and related docs.
- `apps/dashboard/mock-data/aios-session-resume-state-v1.example.json`
  - Old path: `docs/AI_OS/operator_workflows/...`
  - Reason not safe yet: fixture currently models exact source path lineage.
  - Required next action: dashboard mock-data source-reference review.
- `automation/router/Test-AiOsRouterCommandMap.DRY_RUN.ps1`
  - Old path: `docs/AI_OS/router`, `docs/AI_OS/operator`.
  - Reason not safe yet: router docs were not canonicalized in this phase.
  - Required next action: router/operator canonicalization packet.
- `automation/status/Test-AiOsDocumentationConsolidation.DRY_RUN.ps1`
  - Old path: `docs/AI_OS/governance`, `docs/AI_OS/index`, `docs/AI_OS/operator`, `docs/AI_OS/runbooks`, `docs/AI_OS/validators`.
  - Reason not safe yet: validator checks legacy consolidation coverage, not only canonical governance.
  - Required next action: documentation consolidation validator modernization packet.
- `automation/execution_safety/*`
  - Old path: `docs/AI_OS/execution`, `docs/AI_OS/brokers`, `docs/AI_OS/risk_controls`.
  - Reason not safe yet: trading/live execution safety boundary; do not repoint in this pass.
  - Required next action: separate execution safety review.

## Folder Status Table

| Folder | Status | Canonical Destination | Safe To Archive Now | Reason |
| --- | --- | --- | --- | --- |
| `agent_runtime` | Active runtime fixture/model | `docs/architecture/AGENT_RUNTIME_ARCHITECTURE.md` plus active fixtures in place | NO | JSON fixtures and validators still active |
| `telemetry` | Active planning/source docs | `docs/concepts/aios-telemetry-data-model-concepts.md` | NO | validators still read exact contracts |
| `operator` | Active workflow source | `docs/workflows/OPERATOR_WORKFLOW.md`, `PARALLEL_CODEX_WORKFLOW.md`, `WORKER_BRANCH_AND_LANE_RULES.md` | NO | dashboard, router, status refs remain |
| `operator_workflows` | Active workflow source | `docs/workflows/APPLY_ROUTING_CHAIN.md`, `SAFE_SESSION_RESUME.md` | NO | dashboard mock-data refs remain |
| `governance` | Active authority | `docs/governance/FILE_PLACEMENT_RULES.md`, `REPO_FOLDER_OWNERSHIP_MAP.md` | NO | consolidation/governance refs remain |
| `security` | Active security authority | `docs/security/SECURE_ACCESS_DOCS_CANONICAL_LINEAGE.md`, `ACCESS_MODEL_OVERVIEW.md`, `PRIVACY_CREDENTIAL_EXCLUSION_CHECKLIST.md` | NO | security lineage needs separate validator review |
| `analytics` | Active validator source | Future `docs/specs` | NO | analytics validators still point at legacy docs |
| `reporting` | Active validator source | Future reporting spec/concept | NO | reporting validators still point at legacy docs |
| `multi_agent` | Active validator/dashboard source | Future agent/multi-agent concept | NO | validators and fixtures still point at legacy docs |
| `backtesting` | Active validator source | Future backtesting spec | NO | backtesting validators still point at legacy docs |
| `strategy_registry` | Active validator source | Future strategy registry spec | NO | backtesting validator uses strategy registry draft |
| `router` | Active validator source | Future workflow/router doc | NO | router validators still point at legacy docs |
| `validators` | Active validator/dashboard source | Future validator workflow/spec | NO | status/dashboard refs remain |
| `execution` | Active safety boundary | Future execution safety spec after separate review | NO | live execution safety boundary |
| `risk_controls` | Active safety boundary | Future risk-control spec after separate review | NO | trading safety boundary |
| `azure` | Active deployment boundary | Future infrastructure/security doc | NO | Azure validator still points at legacy docs |
| `observability` | Active validator source | Future observability spec | NO | production validator still points at legacy docs |

## Archive Candidates After Canonicalization

Potential future candidates after additional file-level review and scans:

- `docs/AI_OS/governance` after validators are modernized.
- `docs/AI_OS/operator` after dashboard/router/status refs are repointed.
- `docs/AI_OS/operator_workflows` after dashboard fixtures are repointed.
- `docs/AI_OS/telemetry` after telemetry validators are redesigned around canonical concepts/specs.
- `docs/AI_OS/security/phase_15_secure_access` after security validator/reference review confirms `secure_access` or canonical `docs/security` docs preserve the useful content.

## Delete Candidates Later

No deletion was performed.

Delete-candidate list remains the Phase 195 list of root-level stale drafts and generated archive lineage. Every delete candidate requires:

- exact active-area scan.
- proof useful content is preserved.
- human review.
- separate deletion approval.

## Actions Performed

Created:

- `docs/governance/FILE_PLACEMENT_RULES.md`
- `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md`
- `docs/workflows/OPERATOR_WORKFLOW.md`
- `docs/workflows/PARALLEL_CODEX_WORKFLOW.md`
- `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md`
- `docs/workflows/SAFE_SESSION_RESUME.md`
- `docs/workflows/APPLY_ROUTING_CHAIN.md`
- `docs/concepts/aios-telemetry-data-model-concepts.md`
- `docs/architecture/AGENT_RUNTIME_ARCHITECTURE.md`
- `docs/security/SECURE_ACCESS_DOCS_CANONICAL_LINEAGE.md`
- `docs/security/ACCESS_MODEL_OVERVIEW.md`
- `docs/security/PRIVACY_CREDENTIAL_EXCLUSION_CHECKLIST.md`
- `docs/audits/phase-196-active-authority-canonicalization.md`

No files moved. No files deleted. No APPLY scripts run. No app, service, schema, test, or `.github` files edited.

## Validation

- `git status --short -uall`: shows new canonical docs, Phase 196 audit, and pre-existing Phase 195 audit as untracked files.
- `git diff --stat`: no tracked-file diff output because all current changes are new untracked docs.
- `git diff --name-status`: no tracked-file diff output because all current changes are new untracked docs.
- `git diff --check`: PASS.
- Changed PowerShell parser checks: not required; no changed `.ps1` files.
- Changed JSON parse checks: not required; no changed `.json` files.
- Delete-only check: PASS, no delete-only entries.
- Unauthorized change check: PASS, only expected audit/canonical docs are present.
- Final `docs/AI_OS` count: 443 tracked files.
- Final `archive/docs_aios_legacy` count: 327 tracked files.

## Recommended Next Execution Packet

`AI_OS PHASE 197 - GOVERNANCE AND OPERATOR LIVE WIRE RETIREMENT`

Objective: repoint safe governance/operator validators and dashboard source references to the new canonical governance and workflow docs where equivalence is clear; leave runtime fixtures, telemetry contracts, security docs, and trading safety boundaries active until their dedicated packets.

## Recommended Commit Message

`docs: canonicalize active AI_OS authority`
