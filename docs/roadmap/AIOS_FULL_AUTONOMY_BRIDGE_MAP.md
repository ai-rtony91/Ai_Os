# AIOS Full Autonomy Bridge Map

## Purpose

This document is the master gap inventory for AIOS achieving full supervised autonomy (the ability to build itself under governed, human-approved constraints). It was produced by a deep six-dimensional scan of all 3,210 tracked files in `ai-rtony91/Ai_Os`.

This is an evidence document. It does not approve APPLY, create workers, bypass governance, or override RISK_POLICY.md, AGENTS.md, or Human Owner authority.

## Scan Dimensions

1. Broken input/output wiring (scripts producing output nothing consumes, or expecting input nothing provides)
2. DRY_RUN to APPLY gaps (every mutation script missing an execution path)
3. Schema to runtime mismatches (contracts vs actual data)
4. Cross-campaign and cross-service dependency graph (wired vs unwired edges)
5. Governance and safety gate enforcement (documented vs enforced in code)
6. Dead, stale, orphan, and duplicate artifacts (things that would mislead autonomous operation)

## Current State Summary

AIOS has built a complete, tested DRY_RUN blueprint and brainstem for building itself. The recursive loop (goal to packet to readiness to validator to approval to commit-package to finish-line) runs end-to-end in sandbox. Zero percent of it has crossed into active mutation. The 61 scripts printing COPY START / COPY END markers are the literal manifestation of the human copy-paste bottleneck.

289 active DRY_RUN scripts exist. Only 2 have matching APPLY files. The entire governance model is honor-system with zero git hooks, no CI validator chain execution, and no pre-write path enforcement.

---

## LAYER 1: Critical Infrastructure Breaks

These are not gaps. These are errors. Things reference them and they do not exist.

### 1.1 Missing telemetry/runtime directory

- **Impact**: Orchestrator API returns ok false for all runtime endpoints
- **References**: `services/orchestrator/runtimeApiService.js` reads `telemetry/runtime/runtime_state.json`, `runtime_heartbeat.json`, `runtime_process.json`
- **Fix**: Create `telemetry/runtime/` with initial empty-state JSON files matching the runtime visibility schema

### 1.2 TypeScript services never compiled

- **Impact**: Runtime loop, dispatcher, supervisor, policy engine, approvals, validation cannot execute
- **References**: `services/package.json` start script points to `dist/runtime/index.js` which does not exist. `node_modules` not installed.
- **Fix**: Run `npm install` and `npm run build` in `services/`, or decide whether TS services are the canonical path vs Python supervisor

### 1.3 Missing relay directory

- **Impact**: `approval_queue.py` reads from `relay/approvals/` which does not exist. Approval queue is always empty.
- **References**: `services/python_supervisor/approval_queue.py:117`
- **Fix**: Create `relay/approvals/` or redirect the approval queue to read from `automation/orchestration/approval_inbox/`

### 1.4 Missing night supervisor output directories

- **Impact**: Night supervisor harness and autonomy bridge have nowhere to write
- **References**: `night_supervisor_harness.py:33` writes to `telemetry/night_supervisor/`, `autonomy_bridge.py:20-22` writes to `telemetry/morning_digest/`
- **Fix**: Create `telemetry/night_supervisor/`, `telemetry/night_supervisor/reports/`, `telemetry/night_supervisor/resume/`, `telemetry/night_supervisor/alerts/`, `telemetry/morning_digest/`

### 1.5 Autonomy bridge glob does not recurse

- **Impact**: Night supervisor writes reports to `telemetry/night_supervisor/reports/` but autonomy bridge glob only matches root-level files
- **References**: `night_supervisor_harness.py:540` writes to `reports/` subdir, `autonomy_bridge.py:157` globs `("telemetry/night_supervisor", "*.json")` without recursion
- **Fix**: Change the glob pattern in `autonomy_bridge.py` to recurse or flatten the output directory

### 1.6 Preflight script broken reference

- **Impact**: Preflight validation chain is broken
- **References**: `Run-AiOsPreflight.DRY_RUN.ps1:11` references `validators/New-CommitPackagePreview.DRY_RUN.ps1` which does not exist. The actual script is `commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1`
- **Fix**: Update the path reference in the preflight script

### 1.7 Active system map references archived file

- **Impact**: Governance map is wrong
- **References**: `docs/audits/active-system-map.md` still references `APPROVAL_INBOX_001.json` which was moved to archive
- **Fix**: Update the active system map

---

## LAYER 2: The Copy-Paste Loop

### 2.1 Scale of the problem

- 289 active DRY_RUN scripts
- 2 have matching APPLY files (both in `automation/trading_lab/`)
- 61 scripts print COPY START / COPY END markers
- Approximately 50 to 60 are mutations that need APPLY counterparts
- Approximately 210 are read-only inspectors that are fine as-is

### 2.2 Mutation scripts needing APPLY paths

#### Worker dispatch (11 scripts)

| Script | What it would do with APPLY |
|---|---|
| `automation/orchestration/workers/inbox/Add-AiOsWorkerInboxItem.DRY_RUN.ps1` | Write inbox JSON |
| `automation/orchestration/workers/inbox/New-AiOsWorkerReadyPacket.DRY_RUN.ps1` | Create ready-packet JSON |
| `automation/orchestration/workers/state/Set-AiOsWorkerTaskState.DRY_RUN.ps1` | Mutate inbox item status |
| `automation/orchestration/workers/completion/Complete-AiOsWorkerInboxItem.DRY_RUN.ps1` | Mark item complete |
| `automation/orchestration/workers/launcher/Open-AiOsWorkerWindow.DRY_RUN.ps1` | Launch terminal window |
| `automation/orchestration/workers/loop/Start-AiOsWorkerLoop.DRY_RUN.ps1` | Start persistent worker loop |
| `automation/orchestration/workers/daemon/Start-AiOsWorkerDaemon.DRY_RUN.ps1` | Start daemon process |
| `automation/orchestration/workers/cycle/Start-AiOsAutonomousWorkerCycle.DRY_RUN.ps1` | Run autonomous cycle |
| `automation/orchestration/workers/execution/Invoke-AiOsWorkerSafeExecute.DRY_RUN.ps1` | Execute task from inbox |
| `automation/orchestration/worker_builder/New-AiOsWorker.DRY_RUN.ps1` | Create new worker profile |
| `automation/orchestration/swarm/Open-AiOsWorkerSwarm.DRY_RUN.ps1` | Launch multi-worker swarm |

#### Lock system (2 scripts)

| Script | What it would do with APPLY |
|---|---|
| `automation/orchestration/locks/Claim-AiOsFileLock.DRY_RUN.ps1` | Persist atomic file lock |
| `automation/orchestration/locks/Release-AiOsFileLock.DRY_RUN.ps1` | Release file lock |

#### Approval and processing (3 scripts)

| Script | What it would do with APPLY |
|---|---|
| `automation/orchestration/approval_inbox/New-AiOsPacketApprovalRequest.DRY_RUN.ps1` | Write approval request |
| `automation/orchestration/approval_processor/Invoke-AiOsApprovalProcessor.DRY_RUN.ps1` | Process approvals |
| `automation/orchestration/approval_runner/Invoke-AiOsApprovalExecutorPreview.DRY_RUN.ps1` | Execute approved actions |

#### Packet lifecycle (5 scripts)

| Script | What it would do with APPLY |
|---|---|
| `automation/orchestration/work_packets/Route-AiOsWorkPacket.DRY_RUN.ps1` | Route packet to worker |
| `automation/orchestration/advancement/Invoke-AiOsPacketAdvancement.DRY_RUN.ps1` | Advance packet state |
| `automation/orchestration/command_queue/Add-AiOsCommandQueueItem.DRY_RUN.ps1` | Add to command queue |
| `automation/orchestration/command_runner/Invoke-AiOsCommandRunner.DRY_RUN.ps1` | Run commands from queue |
| `automation/orchestration/task_generator/New-AiOsTaskFromNextStep.DRY_RUN.ps1` | Generate task from next step |

#### Runtime and daemon (3 scripts)

| Script | What it would do with APPLY |
|---|---|
| `automation/orchestration/daemon/Start-AiOsRuntimeDaemon.DRY_RUN.ps1` | Start persistent daemon |
| `automation/orchestration/runtime/Start-AiOsRuntimeCycle.DRY_RUN.ps1` | Run runtime cycle |
| `automation/orchestration/session/Start-AiOsOperatorSession.DRY_RUN.ps1` | Start operator session |

#### Git and PR (5 scripts)

| Script | What it would do with APPLY |
|---|---|
| `automation/orchestration/pr_gates/Open-AiOsPullRequest.DRY_RUN.ps1` | Create PR |
| `automation/orchestration/pr_gates/Merge-AiOsPullRequest.DRY_RUN.ps1` | Merge PR |
| `automation/git/Complete-AiOsPhasePr.DRY_RUN.ps1` | Complete phase PR |
| `automation/orchestration/commit_packages/New-AiOsCommitPackageRecommendation.DRY_RUN.ps1` | Create commit package |
| `automation/orchestration/commit_packages/Get-AiOsAutoGitDecision.DRY_RUN.ps1` | Decide git actions |

#### Telemetry and evidence (6 scripts)

| Script | What it would do with APPLY |
|---|---|
| `automation/telemetry/Import-AiOsEvidenceIntake.DRY_RUN.ps1` | Import evidence |
| `automation/telemetry/New-AiOsDailyTelemetrySnapshot.DRY_RUN.ps1` | Write daily snapshot |
| `automation/reporting/New-AiOsDailyMetricsRow.DRY_RUN.ps1` | Write metrics row |
| `automation/sessions/New-AiOsSessionEvidenceLog.DRY_RUN.ps1` | Write session log |
| `automation/orchestration/daily_snapshot/New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1` | Write automation snapshot |
| `automation/checkpoints/New-AiOsCheckpointDraft.DRY_RUN.ps1` | Create checkpoint |

#### Other mutation scripts

| Script | What it would do with APPLY |
|---|---|
| `automation/orchestration/memory/Update-AiOsRuntimeMemory.DRY_RUN.ps1` | Write runtime memory |
| `automation/orchestration/self_heal/Invoke-AiOsSelfHeal.DRY_RUN.ps1` | Create missing folders |
| `automation/orchestration/supervisor/Invoke-AiOsSupervisorLoop.DRY_RUN.ps1` | Run supervisor loop |
| `automation/orchestration/supervisor/Resolve-AiOsSupervisorAssignment.DRY_RUN.ps1` | Assign supervisors |
| `automation/orchestration/crew/New-AiOsCrewTask.DRY_RUN.ps1` | Create crew task |
| `automation/orchestration/night_supervisor/Invoke-AiOsNightSupervisor.DRY_RUN.ps1` | Run night supervisor |
| `automation/orchestration/productivity/New-AiOsProductivityTimerEntry.DRY_RUN.ps1` | Write timer entry |
| `automation/intake/Convert-AiOsInputToPacketProposal.DRY_RUN.ps1` | Convert input to packet |
| `automation/orchestration/blockers/Resolve-AiOsRuntimeBlocker.DRY_RUN.ps1` | Resolve runtime blockers |
| `automation/orchestration/queue_runner/Invoke-AiOsOperatorQueueRunner.DRY_RUN.ps1` | Run operator queue |
| `automation/progress/Update-AiOsProgressLedger.DRY_RUN.ps1` | Update progress |
| `automation/orchestration/backups/Start-AiOsPostMainUpdateBackup.DRY_RUN.ps1` | Run backup |

### 2.3 Python modules one parameter flip from execution

These 5 modules have real APPLY code gated behind `apply_enabled=False`:

| Module | What it writes when enabled |
|---|---|
| `services/python_supervisor/telemetry_writer.py` | JSONL events to `telemetry/work_ledger.jsonl` |
| `services/python_supervisor/morning_brief_writer.py` | JSON to `telemetry/supervisor_briefs/` |
| `services/python_supervisor/productivity_ledger.py` | Entries to productivity ledger |
| `services/python_supervisor/autonomy_bridge.py` | JSON to `telemetry/night_supervisor/` and `telemetry/morning_digest/` |
| `services/python_supervisor/approval_queue.py` | Approval queue state JSON |

### 2.4 Scripts with vestigial Apply flag

These scripts accept an `-Apply` switch but still refuse to mutate even when it is passed. The flag is a no-op trap:

- `Add-AiOsWorkerInboxItem.DRY_RUN.ps1`
- `Set-AiOsWorkerTaskState.DRY_RUN.ps1`
- `Complete-AiOsWorkerInboxItem.DRY_RUN.ps1`
- `Update-AiOsRuntimeMemory.DRY_RUN.ps1`
- `Start-AiOsAutonomousWorkerCycle.DRY_RUN.ps1`
- `Invoke-AiOsSelfHeal.DRY_RUN.ps1`

---

## LAYER 3: Disconnected Wiring

### 3.1 Orphan Python modules (built, never imported or called)

| Module | What it does | Call sites |
|---|---|---|
| `services/python_supervisor/supervisor_engine.py` | The brainstem orchestrator (scan, assign, escalate, brief) | 0 external callers |
| `services/python_supervisor/main.py` | Original supervisor skeleton | 0 external callers |
| `services/python_supervisor/contract_normalizer.py` | Normalizes packet contracts | 0 importers |
| `services/python_supervisor/morning_brief_synthesizer.py` | Synthesizes morning brief from evidence | 0 importers |
| `services/python_supervisor/morning_brief_writer.py` | Writes supervisor brief files | 0 importers |
| `services/python_supervisor/evidence_manifest.py` | Manifest of evidence sources | 0 importers |
| `services/python_supervisor/productivity_ledger.py` | Productivity timer entries | 0 importers |

### 3.2 Never-called public functions

| Function | Module | Line |
|---|---|---|
| `build_supervisor_event()` | `telemetry_writer.py` | 37 |
| `append_event()` | `telemetry_writer.py` | 89 |
| `get_enabled_morning_brief_sources()` | `evidence_manifest.py` | 182 |
| `get_sources_by_category()` | `evidence_manifest.py` | 186 |
| `write_brief()` | `morning_brief_writer.py` | 80 |
| `build_entry()` | `productivity_ledger.py` | 69 |
| `append_entry()` | `productivity_ledger.py` | 155 |
| `planned_output_paths()` | `autonomy_bridge.py` | 345 |

### 3.3 Night supervisor outputs written but never consumed

| Output | Path | Consumer |
|---|---|---|
| Resume records | `telemetry/night_supervisor/resume/resume_*.json` | None (comment says morning startup can read this) |
| Night ledger | `telemetry/night_supervisor/night_ledger.jsonl` | None |
| Alerts | `telemetry/night_supervisor/alerts/night_alert_*.json` | None |
| Reports (broken glob) | `telemetry/night_supervisor/reports/night_summary_*.json` | autonomy_bridge.py tries but glob does not recurse |

### 3.4 Unwired cross-system bridges

| From | To | Problem |
|---|---|---|
| TypeScript approval inbox (`services/approvals/`) | PowerShell approval inbox (`automation/orchestration/approval_inbox/`) | Two separate systems, no bridge |
| Python supervisor (`services/python_supervisor/`) | TypeScript services (`services/runtime/`) | Parallel systems reading same files independently |
| Dashboard (`apps/dashboard/`) | Orchestrator API (`services/orchestrator/`) | Mock-data only, requires env var `VITE_AIOS_RUNTIME_VISIBILITY_SOURCE` for live API |
| `services/policy/policyEngine.ts` | Any service | No service imports it |
| `services/validation/cleanStateVerifier.ts` | Any service | No service imports it |

---

## LAYER 4: Schema and Data Integrity

### 4.1 Three incompatible packet schemas

| Schema | Location | ID Field | Status |
|---|---|---|---|
| `work_packets/schema.json` (AIOS_WORK_PACKET.v1) | `work_packets/` | `id` | Runtime packets follow this one |
| `WORK_PACKET_SCHEMA.json` (v0.1.1) | `schemas/aios/orchestration/` | `packet_id` | Not followed by any runtime packet |
| `packet.schema.json` (AIOS_ORCHESTRATION_PACKET.v1) | `schemas/aios/orchestration/` | `packet_id` + `schema` | Not followed by any runtime packet |

### 4.2 Schema index is 41 percent stale

16 of 39 JSON schema files on disk are not referenced in `ORCHESTRATION_SCHEMA_INDEX.json`. Missing from index:

- `packet.schema.json`, `packet-approval.schema.json`, `packet-runtime-state.schema.json`, `packet-lock.schema.json`, `packet-validator.schema.json`, `packet-adapter-report.schema.json`, `packet-read-model.schema.json`
- `aios-strategic-campaign-registry.schema.json`, `overnight_supervisor.schema.json`, `supervisor_queue.schema.json`, `runtime_state_bundle.schema.json`
- `planner_prompt_schema.json`, `validator_confidence.schema.json`, `auto_git_policy.schema.json`, `autonomy_bridge_state.schema.json`, `night_supervisor_approval_queue.schema.json`

### 4.3 Schemas with no runtime counterpart (22 plus)

These schemas define contracts for runtime artifacts that do not yet exist on disk. Full list in the schema audit dimension. Key examples: `AIOS_TELEMETRY_WRITE_RECEIPT`, `AIOS_MORNING_BRIEF_SYNTHESIS`, `AIOS_MORNING_BRIEF_FILE`, `AIOS_BRIEF_WRITE_RECEIPT`, `AIOS_FRESHNESS_SUMMARY`, `AIOS_PACKET_RISK_CLASSIFICATION`, `AIOS_EVIDENCE_MANIFEST`, all 6 `packet-*.schema.json` files.

### 4.4 camelCase vs snake_case telemetry split

TypeScript `services/telemetry/telemetryEvent.ts` uses camelCase fields (`eventId`, `eventType`, `ts`). The canonical telemetry contract and the Python work ledger use snake_case (`event_id`, `event_type`, `timestamp_utc`). The TS implementation is missing 10 plus fields defined in the contract (`actor`, `lane`, `repo_path`, `branch`, `mode`, `authority_token`, `authority_note`, `input_reference`, `output_reference`, `next_safe_action`, `validation_status`).

### 4.5 Scripts defaulting to example.json as real data

| Script | Example File Used As Default |
|---|---|
| `automation/orchestration/bootstrap/Restore-AiOsSession.ps1` | `AIOS_SESSION_STATE.example.json` |
| `automation/orchestration/bootstrap/Save-AiOsSession.ps1` | `AIOS_SESSION_STATE.example.json` |
| `automation/orchestration/bootstrap/Save-AiOsWorkspaceCheckpoint.ps1` | `AIOS_WORKSPACE_CHECKPOINT.example.json` |
| `automation/orchestration/bootstrap/Restore-AiOsWorkspaceCheckpoint.ps1` | `AIOS_WORKSPACE_CHECKPOINT.example.json` |
| `automation/orchestration/locks/Claim-AiOsFileLock.DRY_RUN.ps1` | `FILE_LOCK_REGISTRY.example.json` |
| `automation/orchestration/locks/Release-AiOsFileLock.DRY_RUN.ps1` | `FILE_LOCK_REGISTRY.example.json` |
| `automation/orchestration/locks/Get-AiOsWorkerLockStatus.DRY_RUN.ps1` | `FILE_LOCK_REGISTRY.example.json` |
| `scripts/workers/Test-AiOsWorkerIsolation.ps1` | `FILE_LOCK_REGISTRY.example.json` |
| `automation/work_intelligence/AIOS_WORK_INTELLIGENCE_CONFIG.json` | `MASTER_TODO_LEDGER.example.json` |

### 4.6 Stale data that would mislead autonomous readers

| File | Issue |
|---|---|
| `telemetry/work_ledger.jsonl` | Last entry May 24 shows BLOCKED / FAIL |
| `automation/orchestration/work_packets/active/` | 2 stale packets from May 16, one in awaiting_approval |
| `validation_result.json` (root) | Shows PASS from unknown date |
| `approval.json` (root) | Shows `approved: false, reason: reset` |
| `completion_report.json` (root) | Shows `complete: false` |

### 4.7 Specific schema drift findings

| Schema | Runtime File | Problem |
|---|---|---|
| `WORKER_REGISTRY_SCHEMA.json` | `WORKER_REGISTRY.json` (legacy) | Missing required `registry_id`, `version` |
| `WORKER_REGISTRY_SCHEMA.json` | `AIOS_WORKER_ASSIGNMENT_REGISTRY.example.json` | Missing `registry_id`, `version`, worker `type`, `purpose`. Uses `role` instead |
| `WORK_PACKET_SCHEMA.json` | `work_packets/examples/*.json` (5 files) | All use `id` instead of required `packet_id` |
| `APPROVAL_INBOX_SCHEMA.json` | Both approval inbox examples | Missing required `approval_status`, completely different structure |
| `AIOS_WORK_LEDGER_EVENT.v1.schema.json` | `telemetry/work_ledger.jsonl` | Missing `schema` discriminator and `generated_at`, uses `timestamp_utc` |

---

## LAYER 5: Governance Enforcement

### 5.1 Rules enforced in code

| Rule | Enforcement | Files |
|---|---|---|
| No live trading / broker / OANDA | Runtime safety checks: `TraderConfig.validate_safety()`, `Settings.assert_paper_mode()`, `PaperBroker.submit()`, `aios_paper_validator.py`, `webhook_server.py` hardcodes `execution_allowed=False` | `aios/modules/trader/config.py`, `apps/trading_lab/trading_lab/config.py`, `aios/modules/trader/brokers/paper_broker.py`, `apps/trading_lab/trading_lab/tv_tp_bridge/aios_paper_validator.py`, `apps/trading_lab/trading_lab/ingest/webhook_server.py` |

### 5.2 Rules partially enforced

| Rule | What Exists | What Is Missing |
|---|---|---|
| APPLY requires human approval | `Test-ApplyApprovalGate.DRY_RUN.ps1` checks the gate | Never called automatically. Not in CI. Not in hooks. |
| No secrets committed | `.gitignore` blocks common patterns. CI regex heuristic. | No pre-commit hook. CI excludes `docs/`. No secret scanning workflow. |
| Validation before mutation | CI runs PS1 syntax and Python compile. Orchestration validator chain exists. | CI does not run the chain, does not run `git diff --check`, does not validate JSON. |
| Allowed and blocked paths per worker | `Test-AIOSAllowedPath.ps1` and `Test-AIOSBlockedPath.ps1` exist. Topology guard validates. | Never called automatically before file writes. |
| Worker collision prevention | `Claim-AiOsFileLock.DRY_RUN.ps1` simulates lock claims. | DRY_RUN only. No actual locking mechanism. |
| DRY_RUN scripts must not write files | `Invoke-AiOsExecutionRegistryGuard.ps1` scans for write commands. | Only run manually. Not in CI or hooks. |

### 5.3 Rules documented only (zero enforcement)

- DRY_RUN is the default mode
- No destructive actions without explicit approval
- Emergency stop conditions
- Fail-closed on unknown risk or authority mismatch
- Approval tiers T0, T1, T2
- Protected file edits require approval
- Autonomy levels L1 through L5
- Audit trail enforcement

### 5.4 Not implemented

- Branch protection (listed as Pending in COMPLIANCE_BASELINE.md)
- Test suite execution in CI (tests exist, CI never runs pytest)
- Validator chain in CI
- Git hooks (only .sample files exist)
- CodeQL or GitHub secret scanning workflow

### 5.5 The enforcement gap summary

The repo has thorough governance documentation and a solid collection of validator scripts. The trading module has genuine runtime safety guards. However, the governance-to-code gap is severe. The orchestration validators, approval gates, path validators, file locks, and autonomy levels are all manual-invocation-only. Nothing in CI, git hooks, or runtime integration chains them together automatically. The entire workflow depends on AI agents voluntarily following documented instructions, which is the threat model the governance docs are trying to protect against.

---

## LAYER 6: Duplicates and Dead Weight

### 6.1 Duplicate implementations requiring canonicalization

| What | Count | Locations |
|---|---|---|
| Night Supervisor | 4 | PS1 `automation/orchestration/night_supervisor/Invoke-AiOsNightSupervisor.DRY_RUN.ps1`, Python `automation/orchestration/night_supervisor/night_supervisor_harness.py`, Python `services/python_supervisor/supervisor_engine.py`, TypeScript `services/supervisor/runtimeSupervisor.ts` |
| Approval Inbox | 5+ | `approvals/` (root), `work_packets/approvals/`, `automation/orchestration/approval_inbox/`, `automation/orchestration/approvals/`, `services/approvals/`, `services/python_supervisor/approval_queue.py` |
| Work Packets Directories | 3 | `work_packets/` (root, schemas and examples only), `automation/orchestration/work_packets/` (active lifecycle), `automation/packets/` (empty orphan) |
| Telemetry Writer | 2 | Python `services/python_supervisor/telemetry_writer.py`, TypeScript `services/telemetry/telemetryWriter.ts` |
| Paper Broker | 2 | `aios/modules/trader/brokers/paper_broker.py` (in-memory), `apps/trading_lab/trading_lab/execution/paper_broker.py` (SQLAlchemy) |
| Backtest Engine | 2 | `aios/modules/trader/backtest.py`, `apps/trading_lab/trading_lab/backtest/engine.py` |
| Start-AiOsRuntime | 2 | `scripts/runtime/Start-AiOsRuntime.ps1`, `scripts/control/Start-AiOsRuntime.ps1` |
| Show-Dispatcher-Queue | 2 | `scripts/show-dispatcher-queue.ps1`, `automation/orchestration/show-dispatcher-queue.ps1` |
| Show-Worker-Status | 2 | `scripts/show-worker-status.ps1`, `automation/orchestration/show-worker-status.ps1` |
| Queue Reader | 2 | `services/python_supervisor/queue_reader.py`, `services/python_supervisor/queue_scanner.py` |
| Worker Registry | 2 | `automation/orchestration/workers/AIOS_WORKER_REGISTRY.json`, `automation/window_identity/AIOS_WORKER_REGISTRY.json` |

### 6.2 Dead weight statistics

| Category | Count | Notes |
|---|---|---|
| Archive files | 1,185 | 37 percent of repo. Properly fenced. No active code imports from archive. |
| Legacy docs/AI_OS files | 645 | CLAUDE.md says do not treat as current authority. 230 active script references still point there. |
| Root scaffold md files with no content | 9 | SOURCE_LOG.md, REQUIREMENTS.md, DEPLOYMENT.md, AAR.md, HALLUCINATION_LOG.md, DAILY_REPORT.md, ERROR_LOG.md, ARCHITECTURE.md, CHANGELOG.md. All say PLACEHOLDER. |
| Empty directories with only gitkeep | 10+ | `telemetry/supervisor_briefs/`, `telemetry/runtime_state/`, `telemetry/evidence/`, `telemetry/backup_reports/`, `inputs/pending/`, `inputs/processed/`, `inputs/rejected/`, `automation/packets/` subdirs |
| README_FOLDER_PURPOSE.txt files | 95+ | Governance housekeeping artifacts |
| Automation dirs outside governance maps | 37 dirs, 213 files | Completely ungoverned and unlisted |

### 6.3 Campaign registry status inconsistencies

- `CAMPAIGN-CREW-CORE` is marked READY but its `depends_on` target `CAMPAIGN-AIOS-ORCHESTRATION` is IN_PROGRESS (not COMPLETE). The stage-level dep is met but the campaign-level dep violates the registry's own `dependency_rule`.
- `CAMPAIGN-SUPERVISED-AUTONOMY` is marked NEEDS_REVIEW but depends on CREW-CORE and TELEMETRY-REPORTING, neither COMPLETE.
- `CAMPAIGN-TELEMETRY-REPORTING` depends on GOVERNANCE which is IN_PROGRESS.

---

## Path to Full Autonomy: Sequenced Phases

### Phase 0: Fix what is broken

No new features. Make existing pieces work.

- Create missing directories: `relay/`, `relay/approvals/`, `telemetry/runtime/`, `telemetry/night_supervisor/`, `telemetry/night_supervisor/reports/`, `telemetry/night_supervisor/resume/`, `telemetry/night_supervisor/alerts/`, `telemetry/morning_digest/`
- Create initial empty-state runtime files for `telemetry/runtime/`
- Fix autonomy bridge glob to recurse into reports subdirectory
- Fix preflight script reference to commit package recommendation
- Update active system map to remove archived file reference
- Clear stale telemetry and packet state that would mislead autonomous readers
- Create real initial-state files to replace example.json defaults in lock, session, and checkpoint scripts

### Phase 1: Wire disconnected pieces

- Pick ONE canonical Night Supervisor implementation and retire the other 3
- Connect `supervisor_engine.py` to a PS1 harness or make it the canonical entry point
- Wire the 5 orphan Python modules into the supervisor chain
- Connect night supervisor outputs to morning brief consumption
- Canonicalize ONE packet schema and migrate existing packets to it
- Canonicalize ONE approval inbox location
- Canonicalize ONE worker registry
- Decide TypeScript services vs Python supervisor (build or retire the TS layer)
- Update schema index with all 16 missing schemas

### Phase 2: Close the copy-paste loop

- Build APPLY counterparts for the approximately 50 mutation DRY_RUN scripts
- Priority order: lock claim and release, inbox write, worker dispatch, packet advancement, approval processing
- Flip apply_enabled to True on the 5 Python modules (gated behind the approval gate)
- Replace COPY START / COPY END print blocks with actual execution in the APPLY scripts
- Wire recommendation output to automatic packet creation in `work_packets/proposed/`

### Phase 3: Enforce governance in code

- Install git hooks: pre-commit for secrets, allowed-paths, JSON validation; pre-push for validator chain
- Add validator chain execution to CI
- Add pytest execution to CI
- Build a pre-write gate that enforces allowed_paths per session
- Make autonomy levels L1 through L5 actual code assignments with enforcement
- Build the live session registry and worktree manifest for parallel sessions
- Build atomic persisted lock claim (turn DRY_RUN lock into enforced write with file-locking)

### Phase 4: Activate the self-build loop

- Promote night supervisor from sandbox (telemetry) to active runtime
- Build the Permanent Auditor Registry for continuous self-inspection
- Wire the governed APPLY lane with APPROVE_COMMIT, APPROVE_PUSH, APPROVE_PR_CREATE markers
- Run PKT-AUTONOMY-LEVEL-REVIEW-DRYRUN to advance the autonomy campaign past 25 percent
- Reconcile the telemetry contract (camelCase vs snake_case) for trustworthy self-observation
- Clean up the 37 ungoverned automation directories (add to governance maps or archive)

### The honest ceiling

By the system's own design, AIOS building itself can reach supervised autonomy up to commit-package-prep plus approved APPLY. It can plan, write packets, validate, dispatch workers, prepare exact commits, and execute approved changes overnight. It cannot become unsupervised. Merge, secrets, broker, and governance edits are a permanent human HARD GATE per AI_OS_AUTONOMY_LEVELS.md L5 and RISK_POLICY.md.

---

## Authority

This document is evidence and planning material only. It does not approve APPLY, create workers, bypass governance, or override RISK_POLICY.md, AGENTS.md, or Human Owner authority.

## Generated

- Date: 2026-06-08
- Branch: claude/repo-overview-D1GBF
- Scan scope: all 3,210 tracked files in ai-rtony91/Ai_Os
- Scan method: six parallel deep-scan agents across broken wiring, DRY_RUN gaps, schema mismatches, cross-dependencies, governance enforcement, and dead artifacts
