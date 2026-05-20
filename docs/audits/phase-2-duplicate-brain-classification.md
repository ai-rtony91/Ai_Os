# Phase 2 Duplicate Brain Classification

## Purpose

This table classifies the primary duplicate authority areas targeted by Phase 2 controlled canonicalization.

No source files were moved, deleted, renamed, or rewritten by this classification.

## Canonical V2 brain

| Topic | Canonical active path | Classification | Notes |
|---|---|---|---|
| Human front door | `README.md` | KEEP ACTIVE | Project entry point |
| AI/tool behavior | `AGENTS.md` | KEEP ACTIVE | Single active agent behavior authority |
| Repo governance | `docs/governance/` | KEEP ACTIVE | Ownership, doctrine, placement, source-of-truth maps |
| Operator/developer workflows | `docs/workflows/` | KEEP ACTIVE | Active workflow procedures |
| Security and safety | `docs/security/` | KEEP ACTIVE | Credentials, access, approval, no-live-trading boundaries |
| Architecture | `docs/architecture/` | KEEP ACTIVE | Durable architecture |
| Audit trail | `docs/audits/` | KEEP ACTIVE | Decisions and cleanup evidence |

## Duplicate brain classification

| Current path | Proposed path | Dependency risk | Connected systems | Classification | Why safe/unsafe | Validation required before move |
|---|---|---:|---|---|---|---|
| `docs/AI_OS/system_wizards/00_START_HERE_AI_OS_CONTEXT_PACK.md` | `docs/workflows/` and `AGENTS.md` selected excerpts only | high | Operator startup, agent context | MERGE INTO CANONICAL | Unsafe to archive until durable rules are compared against current `AGENTS.md` | Compare against `AGENTS.md`, `docs/workflows/OPERATOR_WORKFLOW.md`, `docs/workflows/SAFE_SESSION_RESUME.md` |
| `docs/AI_OS/system_wizards/START_HERE_AI_OS_CONTEXT_PACK.md` | Same as above | high | Duplicate start-here context | MERGE INTO CANONICAL | Duplicate-looking but content may differ | Diff against `00_START_HERE_AI_OS_CONTEXT_PACK.md` |
| `docs/AI_OS/system_wizards/01_CURRENT_STATE.md` | `docs/audits/` checkpoint/current-state record | medium | Session context | MERGE INTO CANONICAL | Historical state can mislead if active | Extract durable facts into audit note |
| `docs/AI_OS/system_wizards/02_CHECKPOINT.md` | `docs/audits/` checkpoint record | medium | Session context | MERGE INTO CANONICAL | Checkpoint may be stale but may contain evidence | Compare with active `checkpoints/` and proof files |
| `docs/AI_OS/system_wizards/03_ARCHITECTURE_LOCK.md` | `docs/architecture/` selected excerpts | medium | Architecture context | MERGE INTO CANONICAL | Architecture locks may conflict with current V2 runtime | Compare with `docs/architecture/` |
| `docs/AI_OS/system_wizards/04_AGENT_ROLES.md` | `AGENTS.md` or `docs/governance/agent-roles.md` if created | medium | Agent roles | MERGE INTO CANONICAL | Could duplicate root behavior rules | Compare with `AGENTS.md` |
| `docs/AI_OS/system_wizards/05_RULES_AND_GUARDRAILS.md` | `AGENTS.md`, `docs/security/`, `docs/governance/` | high | Safety rules | MERGE INTO CANONICAL | Safety content must be preserved before retiring source | Compare safety rules against root protected files |
| `docs/AI_OS/system_wizards/06_PROJECT_PATHS.md` | `docs/governance/runtime-ownership-map.md` selected facts only | high | Path authority | MERGE INTO CANONICAL | Path facts can become stale or dangerous | Validate against current filesystem and launchers |
| `docs/AI_OS/system_wizards/07_DAILY_REPORT_PROMPT.md` | `docs/workflows/` selected reporting workflow | low | Reporting workflow | MERGE INTO CANONICAL | Prompt docs should not be active authority alone | Compare with `DAILY_REPORT.md` and reporting rules |
| `docs/AI_OS/context/AIOS_REPO_SOURCE_OF_TRUTH_MAP.md` | `docs/governance/source-of-truth-map.md` | high | Authority map | MERGE INTO CANONICAL | Duplicate authority already exists | Compare sections and preserve active root authority definitions |
| `docs/AI_OS/context/AIOS_OPERATOR_QUICKSTART.md` | `docs/workflows/OPERATOR_WORKFLOW.md` | medium | Operator quickstart | MERGE INTO CANONICAL | May be useful but should not remain separate brain | Compare with active workflow docs |
| `docs/AI_OS/context/AIOS_NEW_CHAT_BOOTSTRAP_SEQUENCE.md` | `docs/workflows/SAFE_SESSION_RESUME.md` | medium | Resume/bootstrap | MERGE INTO CANONICAL | Useful startup context but duplicate | Compare with resume workflow and `automation/session/Resume-AiOsSession.ps1` |
| `docs/AI_OS/context/AIOS_MINIMAL_RECOVERY_CONTEXT_PACKET.md` | `docs/workflows/SAFE_SESSION_RESUME.md` selected excerpts | medium | Recovery context | MERGE INTO CANONICAL | Could help recovery, but not active authority alone | Compare with runtime recovery scripts |
| `docs/AI_OS/context/AIOS_PROJECT_ASSUMPTIONS_AND_DEFAULTS.md` | `docs/governance/operational-doctrine.md` selected excerpts | medium | Assumptions/defaults | MERGE INTO CANONICAL | Assumptions must be labeled if not verified | Verify current state or mark UNKNOWN |
| `docs/AI_OS/context/AIOS_CHATGPT_MEMORY_EXTERNALIZATION.md` | Archive/reference unless still used | low | Assistant memory policy | NEEDS USER DECISION | May be process-specific, not repo authority | User decision |
| `docs/AI_OS/operator/AIOS_OPERATOR_PREFERENCES_AND_WORKFLOW_CANONICAL.md` | `docs/workflows/OPERATOR_WORKFLOW.md` selected excerpts | high | Operator workflow | MERGE INTO CANONICAL | Name says canonical but path is not V2 canonical | Compare with active workflow docs |
| `docs/AI_OS/operator/AIOS_WORKER_BRANCH_AND_LANE_RULES.md` | `docs/workflows/WORKER_BRANCH_AND_LANE_RULES.md` | high | Worker lane rules | MERGE INTO CANONICAL | Duplicate active lane rules | Compare and merge into canonical workflow file |
| `docs/AI_OS/operator/AIOS_PARALLEL_CODEX_WORKFLOW.md` | `docs/workflows/PARALLEL_CODEX_WORKFLOW.md` | high | Parallel worker workflow | MERGE INTO CANONICAL | Duplicate active workflow | Compare and merge selected differences |
| `docs/AI_OS/operator/AIOS_APPLY_APPROVAL_WORKFLOW_DRAFT.md` | `docs/workflows/APPLY_ROUTING_CHAIN.md` selected excerpts | high | Approval/apply flow | MERGE INTO CANONICAL | Approval rules are safety-critical | Compare with approval inbox/gate scripts |
| `docs/AI_OS/operator/AIOS_COMMIT_PUSH_WORKFLOW_DRAFT.md` | `docs/workflows/` selected excerpts | high | Commit/push workflow | MERGE INTO CANONICAL | Commit/push rules are protected by user approval | Compare with `AGENTS.md` rules |
| `docs/AI_OS/operator/AIOS_CLEAN_STOP_WORKFLOW_DRAFT.md` | Archive/reference after review | medium | Clean-stop workflow | ARCHIVE ONLY | CLEAN-era process likely historical | Verify no launcher references |
| `docs/AI_OS/operator_workflows/AIOS_APPLY_ROUTING_CHAIN.md` | `docs/workflows/APPLY_ROUTING_CHAIN.md` | high | Apply routing | MERGE INTO CANONICAL | Duplicate active workflow | Compare content |
| `docs/AI_OS/operator_workflows/AIOS_SAFE_SESSION_RESUME_STANDARD.md` | `docs/workflows/SAFE_SESSION_RESUME.md` | high | Resume workflow | MERGE INTO CANONICAL | Duplicate active workflow | Compare content |
| `docs/AI_OS/operator_workflows/AIOS_MORNING_EXECUTION_PACKET_STANDARD.md` | `docs/workflows/OPERATOR_WORKFLOW.md` selected excerpts | medium | Morning packet workflow | MERGE INTO CANONICAL | May overlap startup flows | Compare with `aios.ps1` daily/morning modes |
| `docs/AI_OS/governance/AIOS_REPO_FOLDER_OWNERSHIP_MAP.md` | `docs/governance/REPO_FOLDER_OWNERSHIP_MAP.md` | high | Folder ownership | MERGE INTO CANONICAL | Duplicate ownership authority | Compare maps before any retirement |
| `docs/AI_OS/governance/AIOS_FILE_PLACEMENT_RULES.md` | `docs/governance/FILE_PLACEMENT_RULES.md` | high | File placement | MERGE INTO CANONICAL | Duplicate placement authority | Compare maps before any retirement |
| `docs/AI_OS/governance/*_DRAFT.md` | Archive/reference or selected canonical excerpts | medium | Governance drafts | ARCHIVE ONLY | Drafts should not act as active authority | Check for unique safety rules before archive proposal |
| `docs/AI_OS/codex/AIOS_CODEX_ORCHESTRATION_PLAYBOOK.md` | `AGENTS.md` selected excerpts | high | Codex behavior | MERGE INTO CANONICAL | Duplicate AI instruction source | Compare with root `AGENTS.md` |
| `docs/AI_OS/codex/PHASE_15_2_CODEX_PERSISTENT_INSTRUCTION_LAYER.md` | Archive/reference after review | medium | Codex instruction layer | ARCHIVE ONLY | Phase-specific historical instruction layer | Verify no current launcher or workflow references |
| `docs/AI_OS/codex/AGENTS_MD_BACKUP_PHASE15_2_20260513.md` | Archive/reference | medium | Backup authority file | ARCHIVE ONLY | Backup must not act as active authority | Confirm root `AGENTS.md` is current |

## Duplicate-brain resolution proposal

1. Keep `AGENTS.md` as the only active AI/tool behavior authority.
2. Keep `docs/governance/` as the only active governance authority.
3. Keep `docs/workflows/` as the only active operator/development workflow authority.
4. Treat `docs/AI_OS/` as CLEAN-era source material until each file is merged or marked archive-only.
5. Do not move `docs/AI_OS/` files until the matching canonical owner has accepted any still-current content.
6. Create merge patches only for approved canonical docs; do not edit source material in place.

## Blockers

- Some CLEAN-era files include safety-critical content and must be compared before archive proposals.
- Some files use names like `CANONICAL` while living outside the proposed V2 canonical path.
- Operator and worker docs overlap with active launch/runtime scripts, so doc cleanup must be validated against `aios.ps1` and `automation/orchestration/`.

## Explicit non-actions

- No duplicate brain files moved.
- No duplicate brain files deleted.
- No source docs rewritten.
- No `docs/AI_OS/` content changed.
