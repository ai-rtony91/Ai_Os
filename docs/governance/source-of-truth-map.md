# AI_OS Source of Truth Map

## Purpose

This document defines the proposed active source-of-truth map for AI_OS.

It is a planning/control document only. It does not move, delete, rename, or promote files by itself.

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
| `apps/dashboard/mock-data/` | Shared / unclear path | Needs classification before APPLY |
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
| `automation/operator/` | Operator launcher/tooling area | NEEDS USER DECISION | Contains active-looking scripts and legacy/imported content |
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
| `apps/dashboard/` | Dashboard/control-plane app | KEEP ACTIVE | UI authority for dashboard implementation |
| `apps/trading_lab/` | Paper-only Trading Lab app | KEEP ACTIVE | Active vertical; no live broker execution |
| `services/` | Backend/runtime services | KEEP ACTIVE | Runtime, dispatcher, policy, telemetry, validation services |
| `automation/` | Orchestration automation | KEEP ACTIVE | System automation and operator orchestration |
| `scripts/` | Developer/operator helper scripts | KEEP ACTIVE | Simple commands and wrappers |
| `schemas/` | Structured contracts | KEEP ACTIVE | JSON/data schemas |
| `tests/` | Validation tests | KEEP ACTIVE | Test authority |
| `aios/modules/trader/` | Possible shared Trading Lab module | NEEDS USER DECISION | Overlaps with `apps/trading_lab/trading_lab/` |
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
| `docs/AI_OS/context/` | Brain/context source | MERGE INTO CANONICAL | Merge selected current facts into root/governance/workflow docs |
| `docs/AI_OS/system_wizards/` | Start-here/checkpoint source | MERGE INTO CANONICAL | Merge selected current rules, then archive |
| `docs/AI_OS/governance/` | Governance source | MERGE INTO CANONICAL | Promote only selected current rules |
| `docs/AI_OS/operator/` | Operator workflow source | MERGE INTO CANONICAL | Promote only selected workflows |
| `docs/AI_OS/codex/` | Codex instruction source | MERGE INTO CANONICAL | Root `AGENTS.md` remains active authority |
| `docs/AI_OS/claude/` | Claude delegation source | NEEDS USER DECISION | Active only if user keeps Claude workflow |
| `docs/AI_OS/security/` | Security source | MERGE INTO CANONICAL | Promote only selected current boundaries |
| `docs/AI_OS/audits/` | CLEAN-era audits | ARCHIVE ONLY | Historical records |
| `docs/AI_OS/**/*_DRAFT.md` | Draft source material | ARCHIVE ONLY | Not active authority unless promoted |

`docs/AI_OS/` rule:

Do not blindly replace CLEAN-era names with current AI_OS authority language. Evaluate each file as source material, then merge, archive, or remove only through approved cleanup batches.

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
| Runtime heartbeat/status/result JSON files | REMOVE/DELETE CANDIDATE AFTER APPROVAL | Generated runtime state unless explicitly designated as ledger/evidence |
| Old reports/checkpoints without current owner | ARCHIVE ONLY | Historical evidence, not instructions |

## Open questions

1. Should `apps/trading_lab/trading_lab/` be the canonical Trading Lab Python package, with `aios/modules/trader/` treated as source material or legacy?
2. Should `agent/` be retained as-is, promoted to `agents/`, or archived after dependency review?
3. Should `automation/orchestration/` be the only active orchestration layer, with `automation/operator/` reduced to launchers or archive-only experiments?
4. Which `docs/AI_OS/` security and trading boundary docs must be promoted before the rest becomes archive-only?
5. Should generated runtime state stay in repo for evidence, move to a runtime/evidence folder, or be deleted after approval?
