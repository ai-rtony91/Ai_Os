# Phase 83 Dashboard Dispatcher Orchestration Triage

Date: 2026-05-19
Branch: `phase-83-docs-aios-dashboard-dispatcher-triage`
Mode: report-only triage

## Purpose

Triage the largest remaining AI_OS documentation and orchestration clutter after PR #180. This pass did not move, delete, rename, or rewrite source files.

Inspected scope:

- `docs/AI_OS/dashboard`
- `docs/AI_OS/dispatcher`
- `docs/AI_OS/orchestration`
- `automation/orchestration`
- `docs/concepts/aios-dashboard-and-interface-concepts.md`
- `docs/concepts/aios-dispatcher-orchestration-concepts.md`
- `docs/architecture/aios-system-architecture.md`
- `docs/audits/pr-180-repo-consolidation-review-summary.md`

## Current Counts

| Path | Tracked files |
| --- | ---: |
| `docs/AI_OS/dashboard` | 127 |
| `docs/AI_OS/dispatcher` | 57 |
| `docs/AI_OS/orchestration` | 49 |
| `automation/orchestration` | 245 |

Pattern counts:

| Path | Total | Draft/planning/generated pattern count |
| --- | ---: | ---: |
| `docs/AI_OS/dashboard` | 127 | 123 |
| `docs/AI_OS/dispatcher` | 57 | 4 |
| `docs/AI_OS/orchestration` | 49 | 31 |
| `automation/orchestration` | 245 | 42 example/v1 files, 71 JSON files, 135 PS1 files |

## Dashboard Classification

### Keep Active

Keep active for now until canonical product decisions are made:

- `docs/AI_OS/dashboard/README_FOLDER_PURPOSE.txt`
- `docs/AI_OS/dashboard/sidebar/README_FOLDER_PURPOSE.txt`
- Any file that documents safety boundaries, allowed data sources, blocked data sources, no-trading rules, or operator readability.

Examples:

- `AIOS_DASHBOARD_ALLOWED_DATA_SOURCES_DRAFT.md`
- `AIOS_DASHBOARD_BLOCKED_DATA_SOURCES_DRAFT.md`
- `AIOS_DASHBOARD_NO_AUTOMATION_NO_TRADING_VALIDATION_DRAFT.md`
- `AIOS_DASHBOARD_OPERATOR_READABILITY_ACCESSIBILITY_DRAFT.md`
- `AIOS_DASHBOARD_SCREENSHOT_DEMO_SAFETY_RULES_DRAFT.md`

### Extract / Promote

Extract useful ideas into compact active docs before any archive move:

- dashboard data contracts and adapter boundaries,
- operator cockpit / command center layout,
- next action, checkpoint, validator, and safety status cards,
- mobile status behavior,
- fixture/mock data policy,
- static preview boundary,
- dashboard implementation rubric.

Likely destination:

- update `docs/concepts/aios-dashboard-and-interface-concepts.md`, or
- create a future `docs/specs/aios-dashboard-data-contract.md` if MAIN CONTROL wants a spec rather than concept summary.

### Archive Candidate

Most of `docs/AI_OS/dashboard` is archive candidate after extraction because 123 of 127 files match draft/planning/generated naming.

Archive-safe groups later:

- `AIOS_DASHBOARD_*_DRAFT.md`
- `AIOS_*_MOCK_*`
- `AIOS_*_FIXTURE_*`
- phase/stage implementation plans,
- screenshot/demo readiness drafts,
- sidebar duplicate draft timestamp file.

### Delete Candidate Later

Delete only after archive and human review:

- duplicate timestamped sidebar draft,
- obsolete mock fixture drafts after canonical fixtures exist elsewhere,
- repeated card wiring plans if replaced by one data-contract spec.

### Human Review

Needs MAIN CONTROL decision:

- whether dashboard docs become product specs or remain concept archive,
- whether `apps/dashboard` owns dashboard documentation instead,
- whether dashboard should expose orchestration state directly or only summarized safe status,
- how much Trading Lab paper-only status belongs on the dashboard.

## Dispatcher Classification

### Keep Active

Keep active until dispatcher vocabulary is resolved:

- runtime/source-of-truth model docs,
- approval, commit package, packet, lock, validator, and worker schema docs,
- runtime API/status output docs if still used as design reference.

Examples:

- `DISPATCHER_PACKET_SCHEMA.md`
- `DISPATCHER_APPROVAL_SCHEMA.md`
- `DISPATCHER_COMMIT_PACKAGE_SCHEMA.md`
- `DISPATCHER_VALIDATOR_CHAIN.md`
- `runtime/RUNTIME_SOURCE_OF_TRUTH_MAP.md`
- `runtime/RUNTIME_PACKET_AND_LOCK_MODEL.md`
- `runtime/RUNTIME_APPROVAL_AND_COMMIT_MODEL.md`

### Extract / Promote

Extract useful dispatcher ideas into `docs/concepts/aios-dispatcher-orchestration-concepts.md` or a future orchestration source-of-truth spec:

- packet lifecycle,
- approval routing,
- validator chain,
- worker heartbeat,
- lock model,
- dead-letter/recovery model,
- runtime status output.

### Archive Candidate

Archive later if dispatcher is declared legacy vocabulary under orchestration:

- `PHASE_15_3_DISPATCHER_CORE.md`
- phase/runtime architecture drafts that duplicate canonical automation paths,
- validator implementation plans after validator source of truth is hardened,
- worker heartbeat model docs if replaced by canonical worker registry/inbox docs.

### Delete Candidate Later

Delete only after archive and review:

- duplicate dispatcher/runtime model files once one source-of-truth spec exists,
- stale runtime docs that imply live runtime behavior not implemented.

### Human Review

Needs MAIN CONTROL decision:

- whether `dispatcher` remains an active subsystem or becomes historical vocabulary,
- whether dispatcher docs should move under `docs/concepts` or `docs/architecture`,
- whether runtime language overstates implemented automation.

## Docs Orchestration Classification

### Keep Active

Keep active until canonical orchestration doctrine is fully extracted:

- broad operator rulebook/workflow files,
- work packet and worktree lane docs,
- command center / one-command workflow docs,
- GitHub save automation notes,
- guard/safety docs.

Examples:

- `AI_OS_ORCHESTRATION_MODEL.md`
- `AIOS_OPERATOR_RULEBOOK.md`
- `AIOS_WORK_PACKETS.md`
- `AIOS_WORKTREE_LANES.md`
- `AIOS_ONE_COMMAND_WORKFLOW.md`
- `AIOS_GITHUB_SAVE_AUTOMATION.md`
- `AIOS_GUARD.md`

### Extract / Promote

Extract into a compact active orchestration doctrine before archive:

- operator loop,
- work packet lifecycle,
- worker routing,
- approval gate,
- validator chain,
- commit package builder,
- terminal workstation model,
- supervisor boundaries.

Likely destination:

- update `docs/concepts/aios-dispatcher-orchestration-concepts.md`, and
- create a future `docs/workflows/aios-orchestration-operator-loop.md` if needed.

### Archive Candidate

Archive later after extraction:

- `PHASE_16_*` files,
- `PHASE_15_3_*` files,
- `PHASE_111_150_AIOS_OPERATIONS_STACK.md`,
- older framework/session/startup drafts that duplicate canonical docs.

### Delete Candidate Later

Delete only after archive and review:

- superseded phase files after active doctrine exists,
- duplicate old orchestration drafts once canonical workflow docs are accepted.

### Human Review

Needs MAIN CONTROL decision:

- whether docs orchestration should collapse into `docs/workflows` plus `docs/concepts`,
- how much phase history stays in Git,
- whether one-command workflow remains a goal or is deferred.

## Automation Orchestration Classification

### Canonical Runtime / Control Files

These are current canonical or near-canonical active source-of-truth paths and must not move yet:

- `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`
- `automation/orchestration/workers/AIOS_WORKER_PROFILES.json`
- `automation/orchestration/workers/inbox/AIOS_WORKER_INBOX.json`
- `automation/orchestration/work_packets/`
- `automation/orchestration/command_queue/AIOS_COMMAND_QUEUE.json`
- `automation/orchestration/approval_inbox/APPROVAL_INBOX_001.json`
- `automation/orchestration/approval_inbox/APPLY_APPROVAL_GATE_001.json`
- `automation/orchestration/validators/VALIDATOR_CHAIN_CONFIG_001.json`
- `automation/orchestration/validators/VALIDATOR_CHAIN_001.json`
- `automation/orchestration/commit_packages/`
- `automation/orchestration/control/`
- `automation/orchestration/control_summary/`
- `automation/orchestration/health_summary/`
- `automation/orchestration/runtime/`
- `automation/orchestration/supervisor/`

### Display / Status Scripts

Keep for now; these are operator-facing status surfaces:

- `show-orchestration-status.ps1`
- `show-worker-status.ps1`
- `show-dispatcher-queue.ps1`
- `show-approval-inbox.ps1`
- `show-validator-chain.ps1`
- `show-commit-package.ps1`
- other `show-*` scripts pending consolidation.

Risk: many root `show-*` scripts still imply multiple status surfaces. Later hardening should decide one operator status command.

### Validator Files

Keep active for now:

- `automation/orchestration/validators/*.ps1`
- `automation/orchestration/validator_chain_runner/Invoke-AiOsValidatorChain.DRY_RUN.ps1`
- `Test-AiOsReadyForWork.ps1`
- `Test-AiOsOperationalChain.DRY_RUN.ps1`
- `Run-AiOsPreflight.DRY_RUN.ps1`

Risk: validators are spread across root, `validators/`, and `validator_chain_runner/`.

### Generated / Example / State Files

High-risk clutter group:

- 42 example/v1 files,
- 71 JSON files,
- 4 CSV ledger files,
- lock/state/session/snapshot examples,
- task card files under `task_cards/`,
- `reports/*.csv` ledgers.

These may be fixtures, generated examples, or runtime state. Do not move until reference checks prove which role each file has.

### Archive Candidates

Archive candidates after reference hardening:

- remaining root `*.v1.example.json`,
- root supervisor/bootstrap example files,
- duplicate queue/lock/session examples,
- `automation/orchestration/reports/*.csv` if they are generated ledgers,
- `automation/orchestration/task_cards/WORKER-*-TASK.md` if generated runtime task cards,
- old display scripts once a canonical operator status command exists.

### Files That Must Not Move Yet

Do not move:

- canonical paths listed above,
- any script called by `aios.ps1`, root scripts, validators, or dashboard status flows,
- `Run-AiOsOperatorLoop.*` until Phase 82/83 operator-loop direction is resolved,
- `terminal_workstations/Show-AiOsOperatorMenu.ps1`,
- `supervisor/` and `runtime/` until active/runtime boundary is clarified.

## Exact Next Recommended Pass

Recommended Phase 84:

**Phase 84 dashboard summary extraction**

Reason:

- `docs/AI_OS/dashboard` is the largest single active docs clutter area at 127 files.
- 123 of 127 dashboard files match draft/planning/generated patterns.
- A canonical dashboard concept summary already exists, so extraction can be controlled and narrow.
- This pass should extract only the highest-value dashboard doctrine into compact active docs, then prepare a later archive move.

Recommended Phase 84 allowed outputs:

- update `docs/concepts/aios-dashboard-and-interface-concepts.md`, or
- create `docs/specs/aios-dashboard-data-contract.md` if MAIN CONTROL approves a spec path,
- create `docs/audits/phase-84-dashboard-summary-extraction.md`.

Do not archive dashboard files in Phase 84 unless a separate prompt explicitly approves archive moves.

## Risk Controls

- No app source touched.
- No `docs/AI_OS` source files edited.
- No `automation/orchestration` source files edited.
- Preserve ideas before archive.
- No live trading, broker, OANDA, webhook, or order execution activation.
- Avoid breaking references by scanning before any future move.
- Archive-before-delete remains the required policy.

## Validation

Required validation:

```powershell
git status --short
git diff --stat
```

Expected result:

- only `docs/audits/phase-83-dashboard-dispatcher-orchestration-triage.md` changed.
