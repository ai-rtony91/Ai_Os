# PERMANENT AUDITOR FRAMEWORK — DRY_RUN ARCHITECTURE REPORT

- **Packet:** `AIOS-PERMANENT-AUDITOR-SYSTEM-DRYRUN-001`
- **Mode:** DRY_RUN (investigation + proposal only)
- **Constraints honored:** no files modified, no commit, no push. This report is a *new* analysis file; nothing existing was changed.
- **Authority:** subordinate to `AGENTS.md`, `RISK_POLICY.md`, `README.md`, and `docs/context/AI_OS_CURRENT_STATE_FOR_CLAUDE.md`. This proposal does not grant APPLY, auto-approval, runtime mutation, trading, or secret-handling authority. The stricter rule always wins.
- **Repo evidence:** `ai-rtony91/Ai_Os`, branch `main` (work staged on `claude/aios-nightly-supervision-5PxU9`). Findings below were gathered by read-only inspection; no V2/stale assumptions.

---

## 0. Target Architecture — the loop (operator-specified spine)

```
            ┌─────────────────────────────────────────────────────────┐
            │                    AUDITOR REGISTRY                       │
            │  automation/orchestration/night_supervisor/               │
            │  AUDITOR_REGISTRY.json  (proposed, DRY_RUN)               │
            └───────────────┬─────────────────────────────────────────┘
                            │ (1) reads registry
                            ▼
            ┌─────────────────────────────────────────────────────────┐
            │              NIGHT SUPERVISOR  (already built)            │
            │  night_supervisor_harness.py  →  new "auditor" phase      │
            │  (2) runs each enabled auditor in DRY_RUN, fail-closed    │
            └───────────────┬─────────────────────────────────────────┘
                            │ (3) writes telemetry reports
                            ▼
            ┌─────────────────────────────────────────────────────────┐
            │   TELEMETRY  (sandbox, allowed write path)                │
            │   telemetry/night_supervisor/<date>/auditors/*.json       │
            │   + append-only night_ledger.jsonl                        │
            └───────────────┬─────────────────────────────────────────┘
                            │ (4) OCC reads the consolidated report fixture
                            ▼
            ┌─────────────────────────────────────────────────────────┐
            │   OCC / DASHBOARD  (apps/dashboard, static JSON ingest)   │
            │   new "Auditors" panel group                              │
            └───────────────┬─────────────────────────────────────────┘
                            │ (5) human reviews + approves next action
                            ▼
                   ┌──────────────────────┐
                   │  HUMAN (Anthony)     │ ── approves next-action focus ──┐
                   └──────────────────────┘                                 │
                            ▲                                                │
                            └──────────────── loop ──────────────────────────┘
```

**Why this fits cleanly:** the Night Supervisor engine (`automation/orchestration/night_supervisor/night_supervisor_harness.py`) *already* runs a fail-closed, sandbox-bounded phase chain (bootstrap → checkpoint → validator → … → report → safety) writing only into `telemetry/night_supervisor/`. The framework adds **one registry-driven phase** ("run registered auditors") between validator and report. No new execution authority is introduced — every auditor is DRY_RUN, read-only outside the sandbox, and human approval remains the only path to action.

---

## 1. INVESTIGATION FINDINGS (what already exists)

### 1.1 Existing auditors / validators / compliance (REUSE-HEAVY)
A **data-driven 12-step validator chain** already exists and is the backbone to reuse:

`VALIDATOR_CHAIN_CONFIG_001.json` order: `execution_registry_guard → git_clean_state → allowed_paths → blocked_paths → json_integrity → powershell_syntax → markdown_exists → no_secrets → no_live_trading_enablement → approval_gate → commit_package_review → final_git_status`.

| Existing system | Path | Reusable for |
|---|---|---|
| Validator chain runner | `automation/orchestration/validator_chain_runner/Invoke-AiOsValidatorChain.DRY_RUN.ps1` | core auditor execution |
| Config-driven chain | `automation/orchestration/validators/Invoke-OrchestrationValidatorChain.DRY_RUN.ps1` | registry-driven pattern precedent |
| Confidence scorer | `automation/orchestration/validators/Get-AiOsValidatorConfidence.DRY_RUN.ps1` (`validator_confidence.schema.json`) | auditor confidence/roll-up |
| Approval-inbox integrity | `…/validators/Test-ApprovalInboxIntegrity.DRY_RUN.ps1` | Approval Inbox Auditor |
| Lock-registry integrity | `…/validators/Test-LockRegistryIntegrity.DRY_RUN.ps1` | Lock Registry Auditor |
| Worker-claim collision | `…/validators/Test-WorkerClaimCollision.DRY_RUN.ps1` | Worker Activity Auditor |
| Identity-spine check | `…/validators/Test-AiOsIdentitySpine.DRY_RUN.ps1` | Agent/README/Whitepaper/Source-of-Truth Auditors |
| Schema-contract check | `…/validators/Test-AiOsOrchestrationSchemaContracts.DRY_RUN.ps1` | structural auditors |
| Runtime health | `…/health/Test-AiOsRuntimeHealth.DRY_RUN.ps1` | Runtime State Auditor |
| Orchestration health (dashboard-visible) | `…/health_summary/Get-AiOsOrchestrationHealth.DRY_RUN.ps1` | Dashboard Metrics Auditor |
| Agent compliance | `…/compliance/Test-AiOsAgentCompliance.DRY_RUN.ps1` | Agent File Auditor |
| Source-of-truth resolver | `…/recommendations/Resolve-AiOsSourceOfTruth.ps1` | Source-of-Truth Auditor |

Audit/evidence schemas already defined: `schemas/aios/orchestration/command_audit_ledger.schema.json`, `…/validator_confidence.schema.json`, `…/packet-validator.schema.json`. Doctrine: `docs/security/audit-logging.md`, `COMPLIANCE_BASELINE.md`.

### 1.2 Existing telemetry collectors & the canonical event contract
- **Canonical ledger:** `telemetry/work_ledger.jsonl`, written by `scripts/telemetry/Write-AIOSTelemetryEvent.ps1`, validated by `scripts/telemetry/Test-AIOSTelemetryLedger.ps1`, governed by `docs/governance/telemetry-contract.md`.
- **Canonical event fields (snake_case):** `event_id, timestamp_utc, event_type, source, actor, lane, repo_path, branch, mode, authority_token, authority_note, input_reference, output_reference, result, risk_level, next_safe_action, validation_status`.
- **Known gap (documented):** legacy camelCase fields (`eventId`, `eventType`, `ts`, `risk`, …) are not yet reconciled to the canonical schema, and **dashboard live-wiring is explicitly blocked pending that reconciliation**.
- Other collectors: `Reports/telemetry/TELEMETRY_REGISTRY.example.json`, `Reports/telemetry/daily_snapshots/…`, `Reports/work_intelligence/…`.

### 1.3 Existing ledgers
- JSONL: `telemetry/work_ledger.jsonl`, `telemetry/night_supervisor/night_ledger.jsonl`, `telemetry/productivity/PRODUCTIVITY_TIMER_LEDGER.example.jsonl`.
- CSV (append-only): `automation/orchestration/reports/{WORKER_ACTIVITY,APPROVAL_ACTIVITY,COMMIT_PACKAGE_ACTIVITY,VALIDATOR_CHAIN_ACTIVITY}_LEDGER_001.csv`.
- JSON ledgers/state: `packet_queue_ledger.v1`, `orchestration_gap_ledger`, `Reports/work_intelligence/MASTER_TODO_LEDGER`.

### 1.4 Existing runtime-state & memory/continuity systems
- Active runtime state: `automation/runtime/state/AIOS_RUNTIME_STATE.json`; path registry `automation/runtime/path_registry/AIOS_PATH_REGISTRY.json`.
- Durable memory: `automation/orchestration/memory/AIOS_RUNTIME_MEMORY.json` (proposals only via `Update-AiOsRuntimeMemory.DRY_RUN.ps1`).
- 18+ control/continuity state templates: `orchestration_control_state.v1`, `queue_health_supervisor.v1`, `session_continuity.v1`, `recovery_bootstrap*`, `startup_orchestration.v1`, `assignment_lock_controller.v1`, `launch_supervisor.v1`.
- Night Supervisor memory: `telemetry/night_supervisor/<date>/runtime_snapshot.json`, `checkpoint.json`, `resume/resume_<date>.json`, `runtime_state_proposal.json`.

### 1.5 Existing Night Supervisor capabilities
- **New engine (this branch):** `automation/orchestration/night_supervisor/night_supervisor_harness.py` (+ `.ps1` preview, config, safety policy, report schema, tests). 10-phase fail-closed DRY_RUN chain, hard sandbox write boundary (`SandboxWriter._assert_sandbox`), secret fail-closed scan, non-zero exit on BLOCKED.
- **Prior supervisor (interactive, read-only):** `automation/orchestration/supervisor/` (`Show-AiOsSupervisorDashboard.ps1`, `Show-AiOsSupervisorStatus.ps1`, `Get-AiOsOvernightSupervisorPlan.DRY_RUN.ps1`, `aios_supervisor_state.example.json`).
- **Python brainstem:** `services/python_supervisor/` (`supervisor_engine.py`, `escalation_engine.py`, `queue_scanner.py`, `packet_risk_classifier.py`, `worker_assignment.py`, `runtime_state.py`) — risk classification (8 classes) and ranked escalations (BLOCKED=3/WARNING=2/REVIEW=1).

### 1.6 Existing validator chains
Two runners over the same 12-step config (§1.1); confidence scoring + recommendation layered on top. **This is the engine the Auditor Registry should drive, not replace.**

### 1.7 Existing approval systems
- Tier policy: `automation/orchestration/policy/AIOS_APPROVAL_TIER_POLICY.json` — **TIER_0_AUTO** (read-only), **TIER_1_LOW_RISK** (scoped, single approval per packet), **TIER_2_HUMAN_REQUIRED** (hard stop). Seven non-overridable scope guards force TIER_2: credential/trading/root-authority/validator-integrity/live-runtime/broad-staging/out-of-repo.
- Inbox + processing: `approval_inbox/`, `approval_processor/`, `approval_runner/`, `approval_detection/`; ledger `APPROVAL_ACTIVITY_LEDGER_001.csv`.

### 1.8 OCC / dashboard ingestion (display surface for the loop)
- `apps/dashboard/` is a **static** site reading **JSON fixtures** from `apps/dashboard/mock-data/` via `apps/dashboard/src/runtimeVisibilityAdapter.js`. Sources registered in `dashboard-data-sources.example.json`; panels in `dashboard-panel-groups.example.json` (already has `validators` and `safety` groups). **No backend API.** Adding an "Auditors" panel = one fixture + one panel-group entry.

---

## 2. AUDITOR REGISTRY (proposed)

**Location (allowed write path):** `automation/orchestration/night_supervisor/AUDITOR_REGISTRY.json`
**Registry entry shape (proposed):**
```json
{
  "auditor_id": "lock_registry_auditor",
  "enabled": true,
  "frequency": "nightly",
  "mode": "DRY_RUN",
  "reuses": "automation/orchestration/validators/Test-LockRegistryIntegrity.DRY_RUN.ps1",
  "inputs": ["automation/orchestration/locks/FILE_LOCK_REGISTRY_001.json"],
  "output_path": "telemetry/night_supervisor/{date}/auditors/lock_registry_auditor.json",
  "dashboard_panel": "auditors",
  "risk_tier": "TIER_0",
  "complexity": "LOW"
}
```
The Night Supervisor's new auditor phase iterates `enabled` entries, runs each in DRY_RUN, captures the result under the sandbox, appends a `night_ledger.jsonl` event per auditor, and rolls findings into the nightly summary + an `auditors` OCC fixture. Any auditor failure routes through the existing fail-closed alert path (CRITICAL → `alerts/`, non-zero exit).

### 2.1 The 18 proposed auditors

> Frequency legend: **N**=nightly (default), session=per operator session. **All are DRY_RUN.** Telemetry root = `telemetry/night_supervisor/<date>/auditors/<id>.json` + `night_ledger.jsonl`; OCC = new `auditors` panel unless noted. "Reuse" cites the existing system to wrap rather than rebuild.

| # | Auditor | Purpose | Freq | Inputs | Outputs | Dashboard | Complexity | Reuse |
|---|---|---|---|---|---|---|---|---|
| 1 | **Agent File Auditor** | Verify `AGENTS.md` present, protected, unmodified vs HEAD; authority order intact | N | `AGENTS.md`, git diff | integrity report | auditors panel | **LOW** | `Test-AiOsIdentitySpine`, `Test-AiOsAgentCompliance`, `no_secrets`, git diff |
| 2 | **README Auditor** | Verify `README.md` front-door + source-of-truth pointers resolve | N | `README.md`, `docs/governance/source-of-truth-map.md` | integrity report | auditors | **LOW** | `Test-AiOsIdentitySpine`, `markdown_exists` |
| 3 | **Whitepaper Auditor** | Confirm `WHITEPAPER.md` pointer + canonical candidate `docs/architecture/AI_OS_WHITEPAPER.md` exist & unmodified | N | `WHITEPAPER.md`, candidate path | integrity report | auditors | **LOW** | `Test-AiOsIdentitySpine`, `markdown_exists` |
| 4 | **Source-of-Truth Auditor** | Detect duplicate/conflicting authority; verify map ↔ active-system-map consistency | N | `docs/governance/source-of-truth-map.md`, `docs/audits/active-system-map.md` | drift report | auditors | **MEDIUM** | `Resolve-AiOsSourceOfTruth.ps1`, `Test-AiOsSourceOfTruthResolution.ps1` |
| 5 | **Runtime State Auditor** | Validate `AIOS_RUNTIME_STATE.json` + control state freshness/parse/health | N | `automation/runtime/state/…`, `orchestration_control_state.v1` | health report | auditors | **LOW–MED** | `Test-AiOsRuntimeHealth`, NS checkpoint phase |
| 6 | **Memory Continuity Auditor** | Confirm `AIOS_RUNTIME_MEMORY.json` continuity + snapshot→checkpoint→resume chain intact | N | memory file, NS snapshot/resume | continuity report | auditors | **MEDIUM** | NS bootstrap/resume phases, `Update-AiOsRuntimeMemory` |
| 7 | **Worker Activity Auditor** | Stale/orphaned workers, claim collisions, ledger sanity | N | `WORKER_ACTIVITY_LEDGER_001.csv`, `worker_registry.v1`, `persistent_worker_supervisor.v1` | activity report | auditors | **MEDIUM** | `Test-WorkerClaimCollision`, `Get-AiOsWorkerLockStatus`, `queue_scanner.py` |
| 8 | **Approval Inbox Auditor** | Inbox integrity, tier classification, expired/pending items | N | `approval_inbox/`, `AIOS_APPROVAL_TIER_POLICY.json` | inbox report | auditors + reuse `safety` panel | **LOW** | `Test-ApprovalInboxIntegrity`, `Get-AiOsApprovalInboxSummary` |
| 9 | **Lock Registry Auditor** | Malformed/duplicate locks, orphaned/expired locks, path conflicts | N | `FILE_LOCK_REGISTRY_001.json` | lock report (release **plan only**) | auditors | **LOW** | `Test-LockRegistryIntegrity`, `Get-AiOsWorkerLockStatus` (≈ NS lock phase) |
| 10 | **Telemetry Auditor** | Ledger append-only integrity + canonical schema compliance | N | `telemetry/work_ledger.jsonl`, `telemetry-contract.md` | schema/integrity report | validators/auditors | **MEDIUM** (blocked by schema reconciliation gap) | `Test-AIOSTelemetryLedger` |
| 11 | **Dashboard Metrics Auditor** | OCC fixture freshness + data-source mapping + panel coverage | N | `dashboard-data-sources.example.json`, `mock-data/`, orchestration health | coverage report | auditors | **MEDIUM** | `Get-AiOsOrchestrationHealth`, `runtimeVisibilityAdapter.js` |
| 12 | **Question Counter Auditor** | Count operator questions per session | session | *operator-input transcript (does not exist)* | count metric | productivity panel | **HIGH** ⚠ no data source | extend `PRODUCTIVITY_TIMER_LEDGER` |
| 13 | **Character Counter Auditor** | Count characters in operator/session text | session | *transcript (does not exist)* | count metric | productivity | **HIGH** ⚠ no data source | extend timer ledger |
| 14 | **Word Counter Auditor** | Count words in operator/session text | session | *transcript (does not exist)* | count metric | productivity | **HIGH** ⚠ no data source | extend timer ledger |
| 15 | **Aha-Moment Auditor** | Flag breakthrough markers | session | *transcript + sentiment (does not exist)* | event markers | productivity | **HIGH** ⚠ greenfield + NLP | none |
| 16 | **Frustration Marker Auditor** | Flag friction/frustration markers | session | *transcript + sentiment (does not exist)* | event markers | productivity | **HIGH** ⚠ greenfield + NLP + privacy | none |
| 17 | **Night Supervisor Auditor** | Meta-audit NS runs: fail-closed counts, `forbidden_write_attempts==0`, alert review | N | `night_ledger.jsonl`, `reports/night_summary_*.json` | meta report | auditors | **LOW–MED** | NS harness outputs, report schema |
| 18 | **Fun Facts Generator** | Derive light "fun facts" (busiest lane, longest validator chain, streaks) | N | all ledgers/snapshots | facts JSON | command_center panel | **LOW** (not an auditor — see §4) | read-only over existing ledgers |

---

## 3. GAPS

1. **No Auditor Registry / auditor phase exists yet** — greenfield, but small given the NS phase pattern and config-driven validator precedent.
2. **No data source for human-interaction metrics (#12–#16).** Question/Character/Word/Aha/Frustration auditors need an *operator-input/session transcript* capture that **does not exist** anywhere in the repo. Building one is the largest effort and raises a **RISK_POLICY privacy concern** (capturing operator text risks private data/secrets; must fail-closed and exclude sensitive content). These cannot be implemented from current data.
3. **Telemetry schema reconciliation unresolved** (camelCase ↔ snake_case). Telemetry Auditor (#10) and dashboard live-wiring are **blocked** until `telemetry-contract.md` reconciliation lands a validator.
4. **OCC has no live data path** — static fixtures only. Auditor output reaches the OCC only via a generated fixture + new panel-group entry.
5. **Resume promotion path** is outside allowed write paths (sandboxed in `telemetry/night_supervisor/`), so morning-startup continuity from auditor state needs a separate approved packet.
6. **PowerShell parse deferred** in the Linux build env — auditors wrapping `.ps1` validators are parse-verified only on the Windows worktree.
7. **Command audit ledger schema exists but is unpopulated** — no active per-command audit stream yet.

---

## 4. DUPLICATE FUNCTIONALITY (avoid rebuilding)

- **#8 / #9 / #10 / #5 substantially duplicate existing validators** (`Test-ApprovalInboxIntegrity`, `Test-LockRegistryIntegrity`, `Test-AIOSTelemetryLedger`, `Test-AiOsRuntimeHealth`). They must be **thin registry adapters that invoke the existing checks**, not new logic.
- **#9 Lock Registry Auditor overlaps the Night Supervisor's existing lock phase** (`phase_locks`) — consolidate; the auditor should *call* that logic, not re-scan.
- **#1–#4 overlap `Test-AiOsIdentitySpine`** (which already checks governance docs exist) — split only by *target file*, sharing one underlying check.
- **#17 overlaps the NS safety-confirmation block** already emitted in `night_summary_*.json` — make it a reader/asserter over that block.
- **#18 "Fun Facts Generator" is not an auditor** — it is a presentation/derivation over existing ledgers. Recommend reclassifying it out of the auditor registry (or marking `category: derivation`) so it never gates anything.
- The proposed `auditors` OCC panel overlaps the existing `validators` and `safety` panel groups — reuse those where the data is the same to avoid panel sprawl.

---

## 5. WHERE EXISTING SYSTEMS CAN BE REUSED (recommended build order)

1. **Drive, don't duplicate:** model the Auditor Registry on `VALIDATOR_CHAIN_CONFIG_001.json` (data-driven), and have the NS auditor phase reuse `Invoke-AiOsValidatorChain` + `Get-AiOsValidatorConfidence` for execution and roll-up scoring.
2. **Emit on the canonical contract:** every auditor writes a `telemetry/work_ledger.jsonl`-shaped event (snake_case fields) and a sandbox JSON — reuse `Write-AIOSTelemetryEvent.ps1` semantics; do **not** invent a new event schema.
3. **Host in the NS engine:** add `phase_auditors()` to `night_supervisor_harness.py` between validator and report; inherit the sandbox boundary, fail-closed alerting, and non-zero-exit-on-BLOCKED for free.
4. **Reuse the approval tier model:** auditors are TIER_0 (read-only); any *action* they recommend routes through `AIOS_APPROVAL_TIER_POLICY.json` unchanged — MEDIUM/HIGH stays human-gated.
5. **OCC bridge:** generate one `auditors` fixture into `apps/dashboard/mock-data/` and register it in `dashboard-data-sources.example.json` + `dashboard-panel-groups.example.json` — reuse `runtimeVisibilityAdapter.js`.

**Suggested phasing:** Phase A (LOW, pure reuse): #1, #2, #3, #5, #8, #9, #17, #18. Phase B (MEDIUM): #4, #6, #7, #10*, #11 (*#10 gated on schema reconciliation). Phase C (HIGH, blocked on a new + privacy-reviewed data source): #12–#16.

---

## 6. NEXT SAFE ACTION / HUMAN DECISION NEEDED

Nothing was modified, committed, or pushed. Anthony's decisions to proceed:
1. **Approve the Auditor Registry shape + NS auditor phase** as the loop's mechanism (Phase A reuse-only auditors first), **or** adjust scope.
2. **Rule on the human-interaction auditors (#12–#16):** they require a *new operator-transcript data source* that does not exist and carries a privacy/secret-exposure risk under `RISK_POLICY.md`. Decide whether to (a) defer, (b) commission a privacy-reviewed capture spec, or (c) drop them.
3. **Decide #18 reclassification** (derivation, not auditor).
4. **Sequence the telemetry schema reconciliation** before enabling the Telemetry Auditor + OCC live data.

**Recommended next packet:** `AIOS-AUDITOR-REGISTRY-PHASEA-DRYRUN-002` — implement the registry + NS auditor phase + the 8 LOW-complexity reuse auditors, DRY_RUN, into the existing allowed write paths only.

---
*DRY_RUN report. No execution authority created. Human approval remains the sole path to any action.*
