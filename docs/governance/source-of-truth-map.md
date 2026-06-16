# AI_OS Source of Truth Map

## Purpose

This document defines the approved planning source-of-truth map for AI_OS.

It is a planning/control document only. It does not move, delete, rename, or promote files by itself.

## Approved canonical ownership defaults

These ownership decisions are approved for planning and future cleanup packets. They do not approve cleanup, archive moves, deletes, renames, runtime mutation, Trading Lab consolidation, dashboard API migration, commit, or push.

| Domain | Approved canonical owner | Safe default |
|---|---|---|
| Root identity | `README.md`, `AGENTS.md`, and protected root docs | Root authority wins over drafts, archives, generated reports, and CLEAN-era source material |
| Governance/docs authority | `docs/governance/`, `docs/workflows/`, `docs/security/`, `docs/architecture/`, `docs/audits/` | Update existing canonical docs before creating new authority |
| Orchestration | `automation/orchestration/` and `automation/orchestration/README.md` with named canonical subfolders | Keep old/example/reference files until references are checked |
| Campaign registry | `automation/orchestration/campaign_registry/AIOS_STRATEGIC_CAMPAIGN_REGISTRY.json` and `automation/orchestration/campaign_registry/Get-AiOsCampaignNextTask.DRY_RUN.ps1` | Campaign selection is read-only routing evidence unless a separate APPLY packet changes registry state |
| Worker registry | `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json` | Treat other registries as presentation, legacy, or REVIEW_REQUIRED until validated |
| Worker inbox | `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json` | Protect active inbox state from cleanup |
| Work packets | `automation/orchestration/work_packets/` | Active packet lifecycle authority; protect active, blocked, and complete packet state |
| Approval authority | `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json` and `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json` | `automation/orchestration/approval_inbox/` is the single active approval authority; Human Owner remains final approval authority; validator output, Relay, Operation Glue, telemetry, Night Supervisor, Autonomy Bridge, and dashboard outputs are evidence/projection only |
| Validator chain | `automation/orchestration/validators/` | Validator PASS does not approve protected actions |
| Commit package flow | `automation/orchestration/commit_packages/` | Commit/push remains blocked without explicit approval and gate review |
| Orchestration runtime bundle | `automation/orchestration/runtime/Get-AiOsRuntimeStateBundle.DRY_RUN.ps1` | Runtime bundle is a read-only orchestration view over canonical packet, approval, validator, and recommendation evidence |
| Runtime recommendation | `automation/runtime/recommendation/Get-AiOsNextCommand.ps1` and `automation/orchestration/recommendations/` | Runtime recommendation output is guidance only; it does not stage, commit, push, merge, move packets, or approve protected actions |
| Runtime state readers/control | `automation/runtime/state/AIOS_RUNTIME_STATE.json`, `automation/orchestration/runtime/`, `scripts/control/`, `services/runtime/`, `services/orchestrator/`, `telemetry/runtime/` | Runtime/generated state is protected evidence until retention policy exists; runtime proof-trail readers must label ledger evidence as current, stale, historical, or reference |
| Trading Lab package ownership | `apps/trading_lab/trading_lab/` likely long-term; `aios/modules/trader/` remains active | REVIEW_REQUIRED; keep both active and do not consolidate yet |
| Operator layer | `aios.ps1` root launcher plus canonical `automation/orchestration/` | Keep `automation/operator/` active launcher/legacy-mixed until dependency review |
| Dashboard/frontend state source | Current fixture-driven `apps/dashboard/`; future read-only API owner `services/orchestrator/`; frontend display contract in `schemas/aios/orchestration/STATE_PROJECTION_RULES.md` and `RUNTIME_VISIBILITY_SCHEMA.json` | Frontends may display read-only projections only; do not wire API mutation, remove fixtures, expose execution controls, or treat display state as authority until approved |
| CLEAN-era source | `docs/AI_OS/**` | Reference/source material only until file-by-file classification |

Dashboard State Contract V1 pointer: `schemas/aios/orchestration/AIOS_DASHBOARD_STATE_CONTRACT.v1.schema.json`.

## Frontend and Immersive UI State Boundary

Future dashboard, GUI, UE5, VR, AR, or other visual command-center surfaces must use display-only state projections. A visual layer may read and render canonical evidence, but it does not gain authority to approve work, mutate approvals, move packets, claim locks, launch workers, run APPLY paths, stage files, commit, push, merge, schedule tasks, start daemons, touch broker/live trading paths, or read secrets.

Safe frontend projections must preserve:

- `display_state`
- `authority_state`
- `source_path`
- `source_type`
- `freshness`
- `blocked_actions`
- `next_safe_action`
- `approval_required`
- `execution_allowed=false`
- `mutation_allowed=false`
- `stale_or_legacy`
- `safe_for_frontend_display`

If a source lacks those fields, future frontends should render it as `NEEDS_REVIEW` or hide it behind an evidence drilldown instead of presenting it as live command authority.

## Root authority files

| Path | Role | Classification | Notes |
|---|---|---|---|
| `README.md` | Human front door | KEEP ACTIVE | Project identity, current mission, repo orientation, first commands |
| `AGENTS.md` | AI/tool behavior authority | KEEP ACTIVE | Required behavior for Codex and AI coding agents |
| `SECURITY.md` | Root security entry | KEEP ACTIVE | Public-facing security posture and reporting entry |
| `CHANGELOG.md` | Change history | KEEP ACTIVE | Human-readable change history |
| `LICENSE` | License authority | KEEP ACTIVE | Legal license terms |
| `RISK_POLICY.md` | Safety and risk policy source | KEEP ACTIVE | Protected root governance; keep until merged or explicitly retained |
| `ARCHITECTURE.md` | Root architecture summary | KEEP ACTIVE | Protected root summary; detailed architecture belongs in `docs/architecture/` |
| `SOURCE_LOG.md` | Source traceability | KEEP ACTIVE | Protected root evidence log |
| `ERROR_LOG.md` | Error and mismatch log | KEEP ACTIVE | Protected root error log |
| `HALLUCINATION_LOG.md` | Suspected false-claim log | KEEP ACTIVE | Protected root hallucination/mismatch log |
| `AAR.md` | After-action review log | KEEP ACTIVE | Protected root lessons log |
| `DAILY_REPORT.md` | Daily report pointer/log | KEEP ACTIVE | Protected root reporting file |
| `WHITEPAPER.md` | High-level concept/vision | KEEP ACTIVE | Protected root vision file |

Root authority rule:

When a root authority file conflicts with a draft, generated report, or CLEAN-era source document, the root authority file wins unless the user explicitly approves a promotion or replacement.

## Active docs authority

| Path | Role | Classification | Notes |
|---|---|---|---|
| `docs/governance/` | Repo rules, ownership, doctrine | KEEP ACTIVE | Canonical policy and ownership home |
| `docs/governance/aios-identity-and-lane-governance.md` | Identity and lane governance | KEEP ACTIVE | Canonical identity spine for Human Owner, Business GPT, Claude Chat, Codex East, Claude Code West, temporary workers, validators, locks, packets, and stop points |
| `docs/workflows/` | Operator and development workflows | KEEP ACTIVE | Canonical workflow home |
| `docs/security/` | Access and safety boundaries | KEEP ACTIVE | Canonical security documentation home |
| `docs/architecture/` | System architecture | KEEP ACTIVE | Canonical architecture home |
| `docs/audits/` | Audit trail and cleanup decisions | KEEP ACTIVE | Decision history, not day-to-day operating authority |
| `docs/specs/` | Product/API/data specifications | KEEP ACTIVE | Active specs when referenced by code or workflow |
| `docs/roadmap/` | Product/build roadmap | KEEP ACTIVE | Planning direction, not safety authority |
| `docs/concepts/` | Conceptual design material | MERGE INTO CANONICAL | Keep as source material unless promoted to architecture/specs |
| `docs/infrastructure/` | Infrastructure maps | MERGE INTO CANONICAL | Useful source for architecture/runtime docs |

## West Territory Classification

Claude Code West territory remains proposed until approved by Human Owner packet authority. The canonical doctrine lives in `docs/governance/aios-identity-and-lane-governance.md`; workflow details belong in `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md`.

| Path | Proposed classification | Notes |
|---|---|---|
| `docs/concepts/` | Proposed West-owned path | Conceptual refinement only; promotion still requires canonical review |
| `docs/architecture/` | Proposed West-owned path | Architecture refinement only |
| `docs/roadmap/` | Proposed West-owned path | Planning direction only, not safety authority |
| `docs/specs/` | Proposed West-owned path | Specification refinement only |
| `docs/standards/` | Proposed West-owned path after classification | Must be classified before APPLY |
| `apps/dashboard/` | Proposed West UI path only | UI layer only; no runtime, telemetry persistence, broker, or trading execution authority |
| `docs/governance/` | Shared / approval-required path | Canonical governance authority |
| `docs/workflows/` | Shared / approval-required path | Canonical workflow authority |
| `docs/security/` | Shared / approval-required path | Security and approval boundary authority |
| `schemas/aios/orchestration/` | Shared / approval-required path | Packet, validator, lock, and approval contracts |
| `apps/dashboard/mock-data/` | Shared fixture path | Fixture-only frontend evidence; not runtime truth, not command authority |
| `automation/orchestration/` | Forbidden West path | East/runtime orchestration machinery |
| `automation/operator/` | Forbidden West path | Operator tooling and unresolved legacy risk |
| `services/` | Forbidden West path | Backend/runtime services |
| `telemetry/` | Forbidden West path | Evidence layer, not West authority |
| `scripts/` | Forbidden West path | Developer/operator helper scripts |
| `aios/modules/trader/` | Forbidden until Human Owner decision | Trading Lab overlap remains unresolved |
| `approvals/` | Unclear path needing classification | Root approval area outside active approval inbox |
| `work_packets/` | Unclear path needing classification | Root packet area outside active orchestration packet state |
| `checkpoints/` | Unclear path needing classification | Authority role unresolved |
| `.local_hold/` | Unclear local state | Local workstation state, not authority |
| `internal/` | Unclear / archive-source candidate | Source-artifact role requires classification |
| `docs/AI_OS/` | Source material, not active authority | CLEAN-era source pending merge/archive classification |

## Workflow authority

| Path | Role | Classification | Notes |
|---|---|---|---|
| `docs/workflows/OPERATOR_WORKFLOW.md` | Human operator workflow | KEEP ACTIVE | Canonical operator workflow candidate |
| `docs/workflows/SAFE_SESSION_RESUME.md` | Resume/checkpoint workflow | KEEP ACTIVE | Canonical safe resume candidate |
| `docs/workflows/APPLY_ROUTING_CHAIN.md` | DRY_RUN/APPLY routing | KEEP ACTIVE | Canonical apply-routing candidate |
| `docs/workflows/PARALLEL_CODEX_WORKFLOW.md` | Parallel Codex workflow | KEEP ACTIVE | Canonical multi-agent workflow candidate |
| `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` | Worker branch/lane rules | KEEP ACTIVE | Canonical branch/lane candidate |
| `docs/workflows/WORKER_TASK_LIFECYCLE_STANDARD.md` | Worker task lifecycle | KEEP ACTIVE | Canonical lifecycle, approval-status, handoff, and stop-condition standard |
| `docs/workflows/VALIDATOR_EXECUTION_STANDARD.md` | Validator execution | KEEP ACTIVE | Canonical validator behavior, evidence, severity, and stop-condition standard |
| `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` | West branch/worktree/lock doctrine | KEEP ACTIVE | Canonical workflow location for West PR-lane branch naming, proposed worktree naming, lock naming, and lane metadata |
| `docs/AI_OS/operator/` | CLEAN-era operator workflow source | MERGE INTO CANONICAL | Not active authority by default |
| `docs/AI_OS/operator_workflows/` | CLEAN-era workflow source | MERGE INTO CANONICAL | Not active authority by default |
| `automation/operator/` | Operator launcher/tooling area | KEEP ACTIVE / REVIEW_REQUIRED | Active launcher and legacy-mixed area; keep untouched until dependency review against `aios.ps1` and `automation/orchestration/` |
| `automation/orchestration/` | Orchestration automation layer | KEEP ACTIVE | Active tooling, but individual generated files need classification |

Workflow rule:

There should be one active workflow document per job. Duplicates from `docs/AI_OS/` should be merged into `docs/workflows/` or marked archive-only.

## Security authority

| Path | Role | Classification | Notes |
|---|---|---|---|
| `SECURITY.md` | Root security entry | KEEP ACTIVE | Root security front door |
| `docs/security/secret-prevention.md` | Secret prevention | KEEP ACTIVE | Canonical no-secrets guidance candidate |
| `docs/security/approval-model.md` | Approval model | KEEP ACTIVE | Canonical approval/safety model candidate |
| `docs/security/ACCESS_MODEL_OVERVIEW.md` | Access model | KEEP ACTIVE | Canonical access model candidate |
| `docs/security/PRIVACY_CREDENTIAL_EXCLUSION_CHECKLIST.md` | Credential/privacy exclusion | KEEP ACTIVE | Canonical credential exclusion candidate |
| `docs/AI_OS/security/` | CLEAN-era security source | MERGE INTO CANONICAL | Promote selected current security docs only |
| `docs/AI_OS/brokers/` | Broker boundary source | MERGE INTO CANONICAL | Preserve no-live-trading boundaries; do not create live execution path |
| `docs/AI_OS/execution/` | Execution boundary source | MERGE INTO CANONICAL | Preserve execution safety rules |
| `docs/AI_OS/trading/` | Trading boundary source | MERGE INTO CANONICAL | Preserve paper-only and no-live-order rules |

Security rule:

No file in `docs/AI_OS/`, `apps/`, `services/`, `automation/`, or `scripts/` may override root safety rules or the no-live-trading boundary without explicit user approval.

## Runtime/code authority

| Path | Role | Classification | Notes |
|---|---|---|---|
| `apps/` | User-facing applications | KEEP ACTIVE | Dashboard and Trading Lab app home |
| `apps/dashboard/` | Dashboard/control-plane app | KEEP ACTIVE | Current dashboard remains fixture-driven until API migration is separately approved |
| `apps/trading_lab/` | Paper-only Trading Lab app | KEEP ACTIVE | Active vertical; likely long-term Trading Lab package owner; no live broker execution |
| `services/` | Backend/runtime services | KEEP ACTIVE | Runtime, dispatcher, policy, telemetry, validation services; `services/orchestrator/` is future read-only dashboard API owner |
| `automation/` | Orchestration automation | KEEP ACTIVE | System automation and operator orchestration |
| `scripts/` | Developer/operator helper scripts | KEEP ACTIVE | Simple commands and wrappers; `scripts/control/` owns runtime reader/control scripts |
| `schemas/` | Structured contracts | KEEP ACTIVE | JSON/data schemas |
| `tests/` | Validation tests | KEEP ACTIVE | Test authority |
| `aios/modules/trader/` | Active paper trader module | REVIEW_REQUIRED | Keep active because tests import it; overlaps with likely long-term owner `apps/trading_lab/trading_lab/` |
| `agent/` | Possible agent runtime folder | NEEDS USER DECISION | Target structure prefers `agents/`, but do not rename without dependency review |
| `packages/` | Shared libraries | NEEDS USER DECISION | Target folder does not currently exist |
| `tools/` | Repo tooling | NEEDS USER DECISION | Target folder does not currently exist |

Runtime/code rule:

AI_OS should keep one canonical code path per job. Current overlap between `aios/modules/trader/` and `apps/trading_lab/trading_lab/` needs a user decision before any cleanup.

## Archive/reference-only areas

| Path | Role | Classification | Notes |
|---|---|---|---|
| `archive/` | Historical/reference only | ARCHIVE ONLY | Not active authority |
| `internal/source-artifacts/` | Imported source material | ARCHIVE ONLY | Candidate to archive after approval |
| `inputs/` | Imported source inputs | ARCHIVE ONLY | Candidate to archive after approval |
| `docs/audits/phase-*.md` | Historical audit record | ARCHIVE ONLY | Keep as audit trail unless consolidated |
| `automation/operator/legacy_imports/` | Legacy script source | ARCHIVE ONLY | Explicit legacy content |

Archive rule:

Archive files are reference-only. They should not be used as active operating instructions unless explicitly promoted.

## What `docs/AI_OS` means now

`docs/AI_OS/` is CLEAN-era source material pending merge/archive classification.

Default classification:

| Path | Role | Classification | Notes |
|---|---|---|---|
| `docs/AI_OS/context/AIOS_REPO_SOURCE_OF_TRUTH_MAP.md` | Header-hardened legacy brain/context source | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Not active authority. Do not follow as live instructions. Physical archive/delete requires a separate dependency-confirmation APPLY packet. |
| `docs/AI_OS/system_wizards/00_START_HERE_AI_OS_CONTEXT_PACK.md` | Header-hardened legacy start-here brain | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Not active authority. Do not follow as live instructions. Physical archive/delete requires a separate dependency-confirmation APPLY packet. |
| `docs/AI_OS/system_wizards/START_HERE_AI_OS_CONTEXT_PACK.md` | Header-hardened duplicate start-here brain | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Not active authority. Do not follow as live instructions. Physical archive/delete requires a separate dependency-confirmation APPLY packet. |
| `docs/AI_OS/system_wizards/01_CURRENT_STATE.md` | Header-hardened legacy current-state brain | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Not active authority. Do not follow as live instructions. Physical archive/delete requires a separate dependency-confirmation APPLY packet. |
| `docs/AI_OS/system_wizards/02_CHECKPOINT.md` | Header-hardened legacy checkpoint brain | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Not active authority. Do not follow as live instructions. Physical archive/delete requires a separate dependency-confirmation APPLY packet. |
| `docs/AI_OS/governance/` | Header-hardened legacy governance source | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Not active authority. Promote only a specific durable rule that is not already represented in active authority; otherwise archive only after dependency confirmation. |
| `docs/AI_OS/operator/` | Header-hardened legacy operator workflow source | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Not active authority. Promote only a specific durable rule that is not already represented in active authority; otherwise archive only after dependency confirmation. |
| `docs/AI_OS/operator_workflows/` | Header-hardened legacy operator workflow source | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Not active authority. Promote only a specific durable rule that is not already represented in active authority; otherwise archive only after dependency confirmation. |
| `docs/AI_OS/codex/` | Header-hardened legacy Codex instruction source | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Root `AGENTS.md` remains active authority. Do not follow these files as live Codex instructions. |
| `docs/AI_OS/claude/` | Header-hardened Claude delegation source | MARK_REFERENCE_ONLY_COMPLETE / NEEDS_HUMAN_DECISION | Not active authority unless Human Owner explicitly retains Claude workflow. Human decision required before archive, retirement, or promotion. |
| `docs/AI_OS/index/` | Header-hardened legacy index/source-map source | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Not active authority. Do not follow as live ownership/source-map instructions. Physical archive/delete requires a separate dependency-confirmation APPLY packet. |
| `docs/AI_OS/security/` | Security source | MERGE INTO CANONICAL | Promote only selected current boundaries |
| `docs/AI_OS/audits/` | CLEAN-era audits | ARCHIVE ONLY | Historical records |
| `docs/AI_OS/**/*_DRAFT.md` | Draft source material | ARCHIVE ONLY | Not active authority unless promoted |

`docs/AI_OS/` rule:

The 11 known duplicate-brain zones above have been header-hardened as historical/reference-only. They are not active authority, must not be followed as live instructions, and are not approved for physical delete in this packet. Physical archive/delete requires a separate dependency-confirmation APPLY packet.

## Duplicate-brain reference markings

These markings reflect the current duplicate-brain validator state after active dependency cleanup. They do not approve deletion, archive moves, JSON mutation, or runtime cleanup.

| Path or pattern | Current marking | Rule |
|---|---|---|
| `docs/AI_OS/context/AIOS_REPO_SOURCE_OF_TRUTH_MAP.md` | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Header-hardened historical/reference-only source map. Not active authority; do not follow as live instructions. No physical archive/delete without separate dependency-confirmation APPLY. |
| `docs/AI_OS/system_wizards/00_START_HERE_AI_OS_CONTEXT_PACK.md` | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Header-hardened historical/reference-only start-here brain. Not active authority; do not follow as live instructions. No physical archive/delete without separate dependency-confirmation APPLY. |
| `docs/AI_OS/system_wizards/START_HERE_AI_OS_CONTEXT_PACK.md` | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Header-hardened historical/reference-only duplicate start-here brain. Not active authority; do not follow as live instructions. No physical archive/delete without separate dependency-confirmation APPLY. |
| `docs/AI_OS/system_wizards/01_CURRENT_STATE.md` | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Header-hardened historical/reference-only current-state brain. Not active authority; do not follow as live instructions. No physical archive/delete without separate dependency-confirmation APPLY. |
| `docs/AI_OS/system_wizards/02_CHECKPOINT.md` | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Header-hardened historical/reference-only checkpoint brain. Not active authority; do not follow as live instructions. No physical archive/delete without separate dependency-confirmation APPLY. |
| `docs/AI_OS/operator/` | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Header-hardened legacy operator workflow source. Archive after dependency confirmation unless a specific durable rule is not already represented in active authority. |
| `docs/AI_OS/operator_workflows/` | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Header-hardened legacy operator workflow source. Archive after dependency confirmation unless a specific durable rule is not already represented in active authority. |
| `docs/AI_OS/codex/` | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Header-hardened legacy Codex instruction source. Root `AGENTS.md` remains active authority; do not follow as live instructions. |
| `docs/AI_OS/claude/` | MARK_REFERENCE_ONLY_COMPLETE / NEEDS_HUMAN_DECISION | Header-hardened Claude delegation source. Human Owner decision required before retain, retire, promote, or archive. |
| `docs/AI_OS/governance/` | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Header-hardened legacy governance source. Archive after dependency confirmation unless a specific durable rule is not already represented in active authority. |
| `docs/AI_OS/index/` | MARK_REFERENCE_ONLY_COMPLETE / ARCHIVE_CANDIDATE_AFTER_DEPENDENCY_CONFIRMATION | Header-hardened legacy index/source-map source. Not active authority; do not follow as live ownership/source-map instructions. |
| `work_packets/**` | KEEP_PROTECTED_EVIDENCE / NEEDS_HUMAN_DECISION | Root work packets are not active queue authority. They require a retention or migration decision before archive. |
| `approvals/**` | KEEP_PROTECTED_EVIDENCE / NEEDS_HUMAN_DECISION | Root approvals are not active approval authority. They require a retention or migration decision before archive. |
| `relay/approvals/**` | KEEP_PROTECTED_EVIDENCE / PROJECTION_INPUT | Relay approvals may feed review and projection views, but they are not active approval authority unless promoted by Human Owner in a separate packet. |
| `control/operation_glue/APPROVAL_INBOX.json` | LOCAL_RUNTIME_EVIDENCE / PROJECTION_INPUT | Operation Glue approval inbox state is local evidence and must not override `automation/orchestration/approval_inbox/`. |
| `telemetry/approvals/**` | GENERATED_PROJECTION / EVIDENCE_ONLY | Unified approval projections are dashboard/validator evidence only; they do not approve, reject, migrate, or mutate source approval records. |
| `telemetry/work_ledger.jsonl` | KEEP_PROTECTED_EVIDENCE / GENERAL_WORK_TELEMETRY | Historical/general work telemetry ledger. It can look canonical, but it must be treated as stale unless recent writes prove it has been revived. Staleness here does not prove that Night Supervisor activity did not occur. |
| `telemetry/night_supervisor/night_ledger.jsonl` | KEEP_PROTECTED_EVIDENCE / ACTIVE_NIGHT_RUNTIME_LEDGER | Current Night Supervisor and Night Cycle runtime ledger. It proves runtime-cycle evidence only; it does not prove productive autonomy unless paired with a real GREEN task output, truthful marker evidence, validation, and report. |
| `automation/operator/AIOS_PARALLEL_WORKER_REGISTRY.json` | KEEP_PROTECTED_EVIDENCE / FUTURE_ARCHIVE_CANDIDATE | Compatibility evidence only until adapter-first registry use is fully proven and retirement is approved. |
| `automation/orchestration/*.example.json` | FUTURE_ARCHIVE_CANDIDATE | Example files require fixture ownership review before archive. |
| `automation/orchestration/work_packets/proposed/**` | NON_LIVE_PACKET_EVIDENCE | Proposed packet material only; future interfaces must not render these as active executable work. |
| `automation/orchestration/work_packets/deferred/**` | NON_LIVE_PACKET_EVIDENCE | Deferred packet material only; future interfaces must not render these as active executable work. |
| `automation/orchestration/work_packets/rejected/**` | NON_LIVE_PACKET_EVIDENCE | Rejected packet material only; future interfaces must not render these as active executable work. |
| `automation/orchestration/work_packets/templates/**` | TEMPLATE_ONLY | Packet templates are not work. |
| `automation/orchestration/work_packets/examples/**` | EXAMPLE_ONLY | Packet examples are not active work. |

Current delete readiness:

- `ACTIVE_DEPENDENCY` count is 0.
- Safe delete candidate count is 0.
- No old-brain path is approved for deletion by this map.

Runtime proof-trail ledger rule:

- `telemetry/work_ledger.jsonl` is the general work telemetry ledger and may be historical/stale unless current writes prove otherwise.
- `telemetry/night_supervisor/night_ledger.jsonl` is the active Night Supervisor/Night Cycle runtime ledger today.
- Dashboards, morning reports, runtime exporters, and visibility adapters must label ledger evidence as current, stale, historical, or reference instead of treating every ledger path as the same authority.
- AI_OS must not treat stale `telemetry/work_ledger.jsonl` as proof that no night runtime activity occurred.
- AI_OS must not claim productive autonomy from `telemetry/night_supervisor/night_ledger.jsonl` unless a real GREEN task produced a safe work product and the matching marker, validator, ledger, and report evidence exists.
- Future productive proof must write to the chosen canonical runtime proof trail or an explicit ledger pointer/index approved by Human Owner packet authority.

Runtime proof-trail marker rule:

- `control/cycle/last_marker.json` is protected runtime evidence and must distinguish requested apply intent from effective apply authority.
- Cycle markers must preserve `requested_apply`, `effective_apply`, `mode`, `observe_only`, `completed_phases`, `skipped_phases`, and per-phase result evidence when available.
- Skipped observer-mode phases must not be counted or displayed as completed productive work.
- Dashboard, morning report, and runtime visibility readers that consume cycle markers must label skipped, completed, failed, and not-run phases separately.

## What files should not be treated as active authority

| Path pattern | Classification | Reason |
|---|---|---|
| `archive/**` | ARCHIVE ONLY | Historical/reference only |
| `.codex_worktrees/**` | ARCHIVE ONLY | Worktree material, ignored for active authority |
| `**/__pycache__/**` | REMOVE/DELETE CANDIDATE AFTER APPROVAL | Generated Python cache |
| `**/node_modules/**` | REMOVE/DELETE CANDIDATE AFTER APPROVAL | Installed dependencies |
| `.pytest_cache/**` | REMOVE/DELETE CANDIDATE AFTER APPROVAL | Test cache |
| `*_DRAFT.md` under `docs/AI_OS/` | ARCHIVE ONLY | Draft status means not canonical |
| `*BACKUP*` under `docs/AI_OS/` | ARCHIVE ONLY | Backup copies are not authority |
| Runtime heartbeat/status/result JSON files | PROTECTED EVIDENCE / REVIEW_REQUIRED | Runtime/generated state must not move or delete until retention policy exists |
| Old reports/checkpoints without current owner | ARCHIVE ONLY | Historical evidence, not instructions |

## Open questions

1. When should `apps/trading_lab/trading_lab/` become the sole canonical Trading Lab Python package, with `aios/modules/trader/` migrated or retired after tests/imports are moved?
2. Should `agent/` be retained as-is, promoted to `agents/`, or archived after dependency review?
3. Which `automation/operator/` scripts remain active launchers, and which become archive candidates after dependency review?
4. Which `docs/AI_OS/` security and trading boundary docs must be promoted before the rest becomes archive-only?
5. Should generated runtime state stay in repo for evidence, move to a runtime/evidence folder, or be deleted after a retention policy and reference checks are approved?
