# AIOS Forex Evidence Index V1 Report

## Packet Identity

- Mission ID: MISSION-AIOS-FOREX
- Mission Name: AIOS Forex Evidence Index
- Program ID: PRG-FOREX-001
- Program Name: AIOS Forex Supervised Operational Validation
- Epic ID: EPC-FOREX-EVIDENCE-INDEX-V1
- Epic Name: Evidence Index
- Bucket ID: BKT-FOREX-EVIDENCE-CATALOG
- Bucket Name: Evidence Catalog
- Packet ID: AIOS-FOREX-EVIDENCE-INDEX-V1
- Packet Name: Forex Evidence Index V1
- Mode: LOCAL_APPLY, report-only
- Worker identity: Codex Evidence Catalog Auditor
- Worktree: C:\Dev\Ai.Os
- Branch instruction: current branch only; no branch switch
- Allowed write path: Reports/forex_delivery/AIOS_FOREX_EVIDENCE_INDEX_V1_REPORT.md

## Authority And Safety Boundary

Authority files read: `AGENTS.md`, `README.md`, `WHITEPAPER.md`, `RISK_POLICY.md`, `docs/governance/AI_OS_REPO_MEMORY.md`, and `docs/governance/aios-identity-and-lane-governance.md`.

This report is evidence only. It does not create governance authority, approve broker/API access, approve credentials, approve trading, approve scheduler/daemon/webhook work, approve production activation, or approve protected Git actions.

No existing report, code file, test file, script, governance file, broker file, credential file, scheduler, daemon, webhook, production surface, branch, stash, reset, clean, stage, commit, push, PR, or merge was modified by this packet.

## Method

- Enumerated `Reports/forex_delivery` after authority preflight.
- Cataloged 570 current artifacts under `Reports/forex_delivery`.
- Read selected existing index, ledger, readiness, closure, and classifier reports for flow and status language.
- Used repository text where explicit status was present.
- Used filename-derived tags where no explicit status was available. Filename-derived tags are index hints, not authority.
- Populated `superseded by` only as `Not stated in inspected text` or as a `Candidate successor by version family` when a direct version-family successor exists. Candidate successor does not mean delete.

## Current Git Evidence

- Branch observed during preflight: `main...origin/main [ahead 1]`.
- Current dirty/active/reference report entries in this folder after this index write: 46.
- This index intentionally treats existing dirty/untracked Forex reports as current evidence artifacts, not as authority and not as approved publication state.

## Canonical Evidence Flow

```text
Evidence Intake -> Validation -> Readiness -> Owner Review -> Publication -> Closure
```

| Flow stage | Purpose | Typical report signals | Feeds into |
|---|---|---|---|
| Evidence Intake | Capture raw, sanitized, replay, proof, ledger, cache, or result evidence. | `EVIDENCE`, `PROOF`, `INTAKE`, `CAPTURE`, `LEDGER`, `RESULT`, `REPLAY`, `SANITIZED`, `.json` | Validation |
| Validation | Check evidence quality, gate status, matrix coverage, audit findings, and regression status. | `VALIDATION`, `VALIDATOR`, `GATE`, `HARNESS`, `MATRIX`, `AUDIT`, `REVIEW` | Readiness |
| Readiness | Convert validated evidence into readiness, state, truth, decision, or certificate outputs. | `READINESS`, `READY`, `STATE`, `STATUS`, `TRUTH`, `CERTIFICATE`, `CERTIFICATION` | Owner Review |
| Owner Review | Package current readiness for Anthony review without creating execution authority. | `OWNER`, `GONOGO`, `APPROVAL`, `MANUAL_FINALIZATION`, owner review packets | Publication or Closure |
| Publication | Prepare preservation, PR, release manifest, branch hygiene, or commit-readiness evidence. | `PUBLICATION`, `PRESERVATION`, `PR`, `BRANCH`, `COMMIT`, `HYGIENE`, `RELEASE` | Closure |
| Closure | Record final audit, closeout, completion, landing, and final-system status. | `CLOSURE`, `CLOSEOUT`, `FINAL`, `COMPLETION`, `LANDING`, `WRAPUP` | Later archive review or next evidence cycle |

## Category Counts

| Purpose family | Count |
|---|---:|
| Audit / review artifact | 17 |
| Broker / OANDA evidence | 170 |
| Capital / compounding evidence | 12 |
| Closure / closeout report | 37 |
| Demo / paper operation evidence | 57 |
| Evidence intake / proof artifact | 44 |
| Governance / contract evidence | 5 |
| Live / protected exception evidence | 111 |
| Other forex delivery artifact | 69 |
| Publication / PR hygiene | 11 |
| Readiness / state report | 13 |
| Validation / gate report | 24 |

| Flow stage | Count |
|---|---:|
| Closure | 50 |
| Evidence Intake | 307 |
| Owner Review | 73 |
| Publication | 11 |
| Readiness | 46 |
| Validation | 83 |

| Status class | Count | Meaning |
|---|---:|---|
| ACTIVE_CURRENT_UNTRACKED | 40 | Current local report artifact not yet tracked. |
| ACTIVE_LOCAL_MODIFIED | 3 | Tracked report artifact with local modification. |
| ACTIVE_REFERENCE_ANCHOR | 3 | Tracked anchor used for current index context. |
| BASELINE_EVIDENCE_OR_HISTORY | 439 | Tracked corpus artifact; evidence/history unless promoted elsewhere. |
| HISTORICAL_OR_DRY_RUN | 78 | Dry-run, draft, preflight, manual-finalization, or packet-chain history. |
| SUPERSEDED_CANDIDATE_VERSION_FAMILY | 7 | Older member of a direct version family; needs explicit successor review before archive. |

## Active Report Artifacts

These files are active because current `git status --porcelain -- Reports/forex_delivery` shows them as modified or untracked. They remain report evidence only and are not publication approval.

| Filename | Purpose | Status | Feeds into |
|---|---|---|---|
| `AIOS_FOREX_22H6D_OBSERVATION_CLOSURE_V2_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Owner Review / later archive review |
| `AIOS_FOREX_BROKER_DEMO_CONNECTOR_APPROVAL_WORKFLOW_V1_REPORT.md` | Broker / OANDA evidence | ACTIVE_LOCAL_MODIFIED | Publication or Closure |
| `AIOS_FOREX_BROKER_DEMO_READINESS_LANE_V1_REPORT.md` | Broker / OANDA evidence | ACTIVE_CURRENT_UNTRACKED | Owner Review |
| `AIOS_FOREX_CANDIDATE_INTAKE_DEMO_REVIEW_BRIDGE_V1_REPORT.md` | Demo / paper operation evidence | ACTIVE_LOCAL_MODIFIED | Readiness |
| `AIOS_FOREX_CANONICAL_COMPLETION_ROADMAP_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Owner Review / later archive review |
| `AIOS_FOREX_CAPITAL_COMPOUNDING_SAFETY_LANE_V1_REPORT.md` | Capital / compounding evidence | ACTIVE_CURRENT_UNTRACKED | Validation |
| `AIOS_FOREX_COLLECT_MISSING_REAL_EVIDENCE_V1_REPORT.md` | Evidence intake / proof artifact | ACTIVE_CURRENT_UNTRACKED | Validation |
| `AIOS_FOREX_CONTINUOUS_CLOSURE_LONG_RUN_V2_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Owner Review / later archive review |
| `AIOS_FOREX_CONTINUOUS_CLOSURE_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Owner Review / later archive review |
| `AIOS_FOREX_CONTINUOUS_EVIDENCE_ADVANCEMENT_V1_REPORT.md` | Evidence intake / proof artifact | ACTIVE_CURRENT_UNTRACKED | Validation |
| `AIOS_FOREX_CONTINUOUS_LONG_RUN_V3_REPORT.md` | Other forex delivery artifact | ACTIVE_CURRENT_UNTRACKED | Validation |
| `AIOS_FOREX_CROSS_REFERENCE_VALIDATION_V1_REPORT.md` | Validation / gate report | ACTIVE_CURRENT_UNTRACKED | Readiness |
| `AIOS_FOREX_DASHBOARD_VALIDATOR_SCOPE_REPAIR_V1_REPORT.md` | Validation / gate report | ACTIVE_CURRENT_UNTRACKED | Readiness |
| `AIOS_FOREX_DEMO_TRADE_DECISION_DRY_RUN_LANE_V1_REPORT.md` | Demo / paper operation evidence | ACTIVE_CURRENT_UNTRACKED | Owner Review |
| `AIOS_FOREX_DEPENDENCY_AUDIT_V1_REPORT.md` | Audit / review artifact | ACTIVE_CURRENT_UNTRACKED | Readiness |
| `AIOS_FOREX_DIRTY_MAIN_PRESERVATION_REVIEW_V1_REPORT.md` | Publication / PR hygiene | ACTIVE_CURRENT_UNTRACKED | Closure |
| `AIOS_FOREX_EVIDENCE_GAP_CLOSURE_LANDING_REVIEW_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Owner Review / later archive review |
| `AIOS_FOREX_EVIDENCE_INDEX_V1_REPORT.md` | Evidence intake / proof artifact | ACTIVE_CURRENT_UNTRACKED | Validation |
| `AIOS_FOREX_EVIDENCE_LANDING_RECONCILE_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Owner Review / later archive review |
| `AIOS_FOREX_EVIDENCE_LEDGER_V1_REPORT.md` | Evidence intake / proof artifact | ACTIVE_REFERENCE_ANCHOR | Validation |
| `AIOS_FOREX_EVIDENCE_MILESTONE_CONTINUATION_V1_REPORT.md` | Evidence intake / proof artifact | ACTIVE_CURRENT_UNTRACKED | Validation |
| `AIOS_FOREX_FINAL_BUNDLE_REPAIR_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Owner Review / later archive review |
| `AIOS_FOREX_FINAL_CLOSURE_AUDIT_LANE_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Owner Review / later archive review |
| `AIOS_FOREX_FINAL_SYSTEM_VALIDATION_CLOSURE_LANE_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Owner Review / later archive review |
| `AIOS_FOREX_LOCAL_COMMIT_10ED5808_CONVERGENCE_VALIDATION_V1_REPORT.md` | Publication / PR hygiene | ACTIVE_CURRENT_UNTRACKED | Closure |
| `AIOS_FOREX_LOCAL_COMMIT_10ED5808_PRESERVATION_VALIDATION_V1_REPORT.md` | Publication / PR hygiene | ACTIVE_CURRENT_UNTRACKED | Closure |
| `AIOS_FOREX_MASTER_CONVERGENCE_LONG_RUN_V2_REPORT.md` | Other forex delivery artifact | ACTIVE_CURRENT_UNTRACKED | Validation |
| `AIOS_FOREX_METADATA_INVENTORY_V1_REPORT.md` | Audit / review artifact | ACTIVE_CURRENT_UNTRACKED | Validation |
| `AIOS_FOREX_OPERATIONAL_READINESS_CERTIFICATION_V1_REPORT.md` | Readiness / state report | ACTIVE_CURRENT_UNTRACKED | Owner Review |
| `AIOS_FOREX_PRESERVATION_PR_HYGIENE_LANE_V1_REPORT.md` | Publication / PR hygiene | ACTIVE_CURRENT_UNTRACKED | Closure |
| `AIOS_FOREX_PUBLICATION_EXECUTION_PLAN_V2_REPORT.md` | Publication / PR hygiene | ACTIVE_CURRENT_UNTRACKED | Closure |
| `AIOS_FOREX_PUBLICATION_PR_LANDING_LANE_V1_REPORT.md` | Publication / PR hygiene | ACTIVE_CURRENT_UNTRACKED | Closure |
| `AIOS_FOREX_READINESS_MATRIX_V1_REPORT.md` | Readiness / state report | ACTIVE_CURRENT_UNTRACKED | Owner Review |
| `AIOS_FOREX_READINESS_STATE_RECALCULATION_V1_REPORT.md` | Readiness / state report | ACTIVE_REFERENCE_ANCHOR | Owner Review |
| `AIOS_FOREX_REAL_EVIDENCE_GAP_CLOSURE_LONG_RUN_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Owner Review / later archive review |
| `AIOS_FOREX_REAL_EVIDENCE_INTAKE_REVALIDATION_V1_REPORT.md` | Validation / gate report | ACTIVE_CURRENT_UNTRACKED | Readiness |
| `AIOS_FOREX_REAL_EVIDENCE_INTAKE_REVALIDATION_V2_REPORT.md` | Validation / gate report | ACTIVE_CURRENT_UNTRACKED | Readiness |
| `AIOS_FOREX_REAL_EVIDENCE_INTAKE_V1_REPORT.md` | Evidence intake / proof artifact | ACTIVE_CURRENT_UNTRACKED | Validation |
| `AIOS_FOREX_REAL_PROFIT_EVIDENCE_CONTINUATION_V1_REPORT.md` | Evidence intake / proof artifact | ACTIVE_CURRENT_UNTRACKED | Validation |
| `AIOS_FOREX_RELEASE_MANIFEST_V1_REPORT.md` | Publication / PR hygiene | ACTIVE_CURRENT_UNTRACKED | Closure |
| `AIOS_FOREX_REPLAY_WALKFORWARD_PROFITABILITY_EVIDENCE_VALIDATION_V1_REPORT.md` | Validation / gate report | ACTIVE_CURRENT_UNTRACKED | Readiness |
| `AIOS_FOREX_REPORT_INDEX_CLASSIFIER_V1_REPORT.md` | Audit / review artifact | ACTIVE_REFERENCE_ANCHOR | Validation |
| `AIOS_FOREX_SHUTDOWN_RECOVERY_LANDING_REVIEW_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Owner Review / later archive review |
| `AIOS_FOREX_TECHNICAL_DEBT_AUDIT_V1_REPORT.md` | Audit / review artifact | ACTIVE_CURRENT_UNTRACKED | Readiness |
| `AIOS_FOREX_WALKFORWARD_OOS_CLOSURE_V2_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Owner Review / later archive review |
| `readiness_state_recalculation_v1_report.json` | Readiness / state report | ACTIVE_LOCAL_MODIFIED | Owner Review |

## Duplicate Or Paired Report Families

Duplicate here means same normalized file family, paired report/source forms, or direct version siblings. It does not mean safe to delete.

| Family | Files | Handling |
|---|---|---|
| `AIOS_CAPITAL_FLOW_FUTURE_CONNECTOR_CONTRACT` | AIOS_CAPITAL_FLOW_FUTURE_CONNECTOR_CONTRACT_V10.md<br>AIOS_CAPITAL_FLOW_FUTURE_CONNECTOR_CONTRACT_V11.md | Duplicate or paired responsibility cluster; keep until successor/consumer links are confirmed. |
| `AIOS_FOREX_IMPLEMENTATION_READINESS_ASSESSMENT` | AIOS_FOREX_IMPLEMENTATION_READINESS_ASSESSMENT_V1_REPORT.md<br>AIOS_FOREX_IMPLEMENTATION_READINESS_ASSESSMENT_V1.md | Duplicate or paired responsibility cluster; keep until successor/consumer links are confirmed. |
| `AIOS_FOREX_OANDA_DEMO_SECURE_CREDENTIAL_PERSISTENCE_WINDOWS_VAULT` | AIOS_FOREX_OANDA_DEMO_SECURE_CREDENTIAL_PERSISTENCE_WINDOWS_VAULT_V1_REPORT.md<br>AIOS_FOREX_OANDA_DEMO_SECURE_CREDENTIAL_PERSISTENCE_WINDOWS_VAULT_V1.md | Duplicate or paired responsibility cluster; keep until successor/consumer links are confirmed. |
| `AIOS_FOREX_PROFIT_AUTONOMY_MASTER_BUCKET_PACK` | AIOS_FOREX_PROFIT_AUTONOMY_MASTER_BUCKET_PACK_V1_REPORT.md<br>AIOS_FOREX_PROFIT_AUTONOMY_MASTER_BUCKET_PACK_V1.md | Duplicate or paired responsibility cluster; keep until successor/consumer links are confirmed. |
| `AIOS_FOREX_PROFIT_PROOF_LEDGER` | AIOS_FOREX_PROFIT_PROOF_LEDGER_V1_REPORT.md<br>AIOS_FOREX_PROFIT_PROOF_LEDGER_V1.md | Duplicate or paired responsibility cluster; keep until successor/consumer links are confirmed. |
| `AIOS_FOREX_REAL_EVIDENCE_INTAKE_REVALIDATION` | AIOS_FOREX_REAL_EVIDENCE_INTAKE_REVALIDATION_V1_REPORT.md<br>AIOS_FOREX_REAL_EVIDENCE_INTAKE_REVALIDATION_V2_REPORT.md | Duplicate or paired responsibility cluster; keep until successor/consumer links are confirmed. |
| `AIOS_FOREX_REVIEW_READY_CANDIDATE_SELECTOR` | AIOS_FOREX_REVIEW_READY_CANDIDATE_SELECTOR_V1_REPORT.md<br>AIOS_FOREX_REVIEW_READY_CANDIDATE_SELECTOR_V1.md | Duplicate or paired responsibility cluster; keep until successor/consumer links are confirmed. |
| `AIOS_FOREX_STRATEGY_PROOF_ENGINE` | AIOS_FOREX_STRATEGY_PROOF_ENGINE_V1_REPORT.md<br>AIOS_FOREX_STRATEGY_PROOF_ENGINE_V1.md | Duplicate or paired responsibility cluster; keep until successor/consumer links are confirmed. |
| `AIOS_FOREX_SUPERVISED_DEMO_TRADE_EPIC` | AIOS_FOREX_SUPERVISED_DEMO_TRADE_EPIC_REPORT_V1.md<br>AIOS_FOREX_SUPERVISED_DEMO_TRADE_EPIC_V1.md | Duplicate or paired responsibility cluster; keep until successor/consumer links are confirmed. |

Additional duplicate-responsibility clusters found in repository text: broker-proof intake versus runtime-only human intake, state summary/readiness recalculation families, and take-profit risk-gate versus take-profit evidence closure. Existing text says these can have distinct roles and should not be removed without consumer mapping.

## Orphan Report Classification

No inspected artifact was proven orphaned. Existing cleanup classification text says report-only status is not enough proof of orphaning because `Reports/forex_delivery` also functions as an evidence archive. The correct classification for weakly connected reports is `ORPHAN_UNPROVEN`, not delete-ready.

## Historical Reports

Historical reports include older dry-run packet chains, draft request packets, preflight reports, manual-finalization reports, branch/PR planning reports, and earlier version siblings. They are useful for audit reconstruction but should not override `AGENTS.md`, `README.md`, `RISK_POLICY.md`, or current owner-approved packets.

## Reports Safe To Archive Later

Safe-to-archive-later means candidate for a future owner-approved archive review only. It does not recommend deleting anything and does not authorize moving files.

- Direct version-family predecessors listed as `SUPERSEDED_CANDIDATE_VERSION_FAMILY`.
- Historical or dry-run packet chains listed as `HISTORICAL_OR_DRY_RUN`.
- Older manual-finalization reports after a current owner-review package is named.
- Draft request packets after their final review or closure report is linked.
- Baseline evidence that is explicitly linked from a current final closure report before archive movement.

## Canonical Active Anchors

Use these as orientation anchors before opening historical packet chains:

- `AIOS_FOREX_REPORT_INDEX_CLASSIFIER_V1_REPORT.md` - prior filename-only report classifier.
- `AIOS_FOREX_EVIDENCE_LEDGER_V1_REPORT.md` - evidence ledger behavior and paper-only safety boundary.
- `AIOS_FOREX_OPERATIONAL_READINESS_CERTIFICATION_V1_REPORT.md` - current operational readiness certification evidence.
- `AIOS_FOREX_FINAL_CLOSURE_AUDIT_LANE_V1_REPORT.md` - final closure audit and remaining blocker evidence.
- `readiness_state_recalculation_v1_report.json` and `AIOS_FOREX_READINESS_STATE_RECALCULATION_V1_REPORT.md` - machine/readable readiness state artifacts.
- `AIOS_FOREX_BROKER_DEMO_READINESS_LANE_V1_REPORT.md` - broker-read-only to demo-readiness owner-review evidence.
- `AIOS_FOREX_PUBLICATION_PR_LANDING_LANE_V1_REPORT.md`, `AIOS_FOREX_PUBLICATION_EXECUTION_PLAN_V2_REPORT.md`, and `AIOS_FOREX_RELEASE_MANIFEST_V1_REPORT.md` - publication planning evidence only.

## Complete File-Level Evidence Catalog

Every file currently under `Reports/forex_delivery` is listed below. Purpose and flow values are compact index classifications. Supersession is only explicit when marked as a candidate successor by direct version family; otherwise it is not stated in inspected text.

| Filename | Purpose | Status | Superseded by | Depends on | Feeds into |
|---|---|---|---|---|---|
| `AIOS_BROKER_DEMO_DATA_ADAPTER_V3.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_BROKER_DEMO_DECISION_BRIDGE_V4.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_BROKER_DEMO_EFFECTIVENESS_V2.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_BROKER_DEMO_REHEARSAL_RUNNER_V6.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_BROKER_DEMO_REVIEW_PACKET_V5.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_BROKER_INTEGRATION_EFFECTIVENESS_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_BROKER_THRESHOLD_SPRINT_V7_V9.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_CANONICAL_TRADING_IDENTITY_DOCTRINE_V1_REPORT.md` | Governance / contract evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_CAPITAL_FLOW_FUTURE_CONNECTOR_CONTRACT_V10.md` | Broker / OANDA evidence | SUPERSEDED_CANDIDATE_VERSION_FAMILY | Candidate successor by version family: AIOS_CAPITAL_FLOW_FUTURE_CONNECTOR_CONTRACT_V11.md | Prior Forex delivery context | Validation |
| `AIOS_CAPITAL_FLOW_FUTURE_CONNECTOR_CONTRACT_V11.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_CAPITAL_FLOW_POLICY_SIMULATION_RANGE_V11.md` | Capital / compounding evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_CAPITAL_FLOW_POLICY_SIMULATION_V10.md` | Capital / compounding evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_CAPITAL_FLOW_TREASURY_CONTROL_PANEL_V10.md` | Capital / compounding evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_DEMO_CONNECTION_PROOF_SUCCESS_RECORD_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_DOC_AUTHORITY_DRIFT_ELIMINATION_V2_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_EXTERNAL_RUNTIME_CONNECTOR_HANDOFF_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FIRST_DEMO_CONNECTION_PROOF_APPLY_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FIRST_DEMO_CONNECTION_PROOF_APPLY_V1_SANITIZED_EVIDENCE.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FIRST_DEMO_CONNECTION_PROOF_APPLY_WITH_CALLABLE_EXTERNAL_RUNTIME_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FIRST_DEMO_CONNECTION_PROOF_APPLY_WITH_CALLABLE_EXTERNAL_RUNTIME_V1_SANITIZED_EVIDENCE.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FIRST_DEMO_CONNECTION_PROOF_APPLY_WITH_EXTERNAL_RUNTIME_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FIRST_DEMO_CONNECTION_PROOF_APPLY_WITH_EXTERNAL_RUNTIME_V1_SANITIZED_EVIDENCE.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FIRST_DEMO_CONNECTION_PROOF_CALLABLE_EXTERNAL_RUNTIME_RERUN_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FIRST_DEMO_CONNECTION_PROOF_CALLABLE_EXTERNAL_RUNTIME_RERUN_V1_SANITIZED_EVIDENCE.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FIRST_DEMO_CONNECTION_PROOF_CONFIRMED_EXTERNAL_RUNTIME_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FIRST_DEMO_CONNECTION_PROOF_CONFIRMED_EXTERNAL_RUNTIME_V1_SANITIZED_EVIDENCE.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FIRST_DEMO_CONNECTION_PROOF_PATH_ASSESSMENT_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FIRST_DEMO_CONNECTION_PROOF_RUNNER_INJECTION_PREFLIGHT_V1_REPORT.md` | Demo / paper operation evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FIRST_LIVE_MICRO_TRADE_REMAINING_GAPS_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_100_120_PROFIT_MILESTONE_FIRST_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_100_PERCENT_REPEATABILITY_TARGET_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_120_PERCENT_PROFITABILITY_CAMPAIGN_ANCHOR_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_20_PERCENT_MAINTENANCE_WINDOW_PLAN_V2.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_22H6D_OBSERVATION_CLOSURE_V2_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_50_PERCENT_CAMPAIGN_TARGET_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_80_PERCENT_UPTIME_TRANSITION_LADDER_V2.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_APPROVAL_RECORD_SPEC_V1.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_ATTEMPT_RECORD_SPEC_V1.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_AUTO_EXIT_LIVE_READINESS_DRY_RUN_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_AUTO_EXIT_READONLY_RECONCILIATION_CLOSURE_V1.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_BALANCE_COMPOUNDING_V1_REPORT.md` | Capital / compounding evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BEFORE_AFTER_WALK_FORWARD_COMPARISON_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BEST_PROFIT_CANDIDATE_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BRANCH_PRESERVATION_MERGE_PREP_V1_REPORT.md` | Publication / PR hygiene | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Owner Review and clean git state | Closure |
| `AIOS_FOREX_BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_BRIDGE_ACCELERATION_PACKET_A_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_BRIDGE_ACCELERATION_PACKET_B_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_BRIDGE_ACCELERATION_PACKET_C_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_BRIDGE_COMPLETION_REPORT_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_BROKER_BRIDGE_KILL_SWITCH_HALT_PROPAGATION_PLAN_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_CONNECTION_PROOF_PATH_DRY_RUN_V1.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_BROKER_CONNECTION_TEST_PACKET_DRAFT_DRY_RUN_V1.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_BROKER_DEMO_ACCOUNT_BOUNDARY_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_DEMO_CONNECTOR_APPROVAL_WORKFLOW_V1_REPORT.md` | Broker / OANDA evidence | ACTIVE_LOCAL_MODIFIED | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_BROKER_DEMO_CONNECTOR_DRY_RUN_V1_REPORT.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_DEMO_CONNECTOR_IMPLEMENTATION_PLAN_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_DEMO_CREDENTIAL_BOUNDARY_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_DEMO_CREDENTIAL_HANDLING_PROCEDURE_DRY_RUN_V1_REPORT.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_DEMO_DRY_RUN_ORCHESTRATOR_V1_REPORT.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_DEMO_ENDPOINT_MODE_PROOF_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_BROKER_DEMO_INTERFACE_CONTRACT_PLAN_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_DEMO_NO_ORDER_CONNECTOR_IMPLEMENTATION_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_DEMO_ORDER_INTENT_DRY_RUN_V1.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_DEMO_READ_ONLY_PROBE_PLAN_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_DEMO_READINESS_LANE_V1_REPORT.md` | Broker / OANDA evidence | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_BROKER_DEMO_RUNTIME_CONNECTOR_SKELETON_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_DEMO_RUNTIME_REVIEW_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_BROKER_GATE_LIVE_EXCEPTION_BUNDLE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_BROKER_INTEGRATION_READINESS_FINAL_REVIEW_PACKET_J_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_BROKER_PAPER_ADAPTER_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_POLICY_READINESS_ENGINE_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_BROKER_PROOF_INTAKE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_BROKER_PROOF_RUNTIME_ONLY_HUMAN_INTAKE_TEMPLATE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_BROKER_PROOF_RUNTIME_ONLY_HUMAN_INTAKE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_BROKER_READ_ONLY_SNAPSHOT_CONTRACT_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_SPECIFIC_INTEGRATION_BACKLOG_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_SPECIFIC_INTEGRATION_PLANNING_PACKET_K_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_BROKER_SPECIFIC_PAPER_DEMO_INTEGRATION_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_C1_EUR_BUY_EVIDENCE_DEPTH_SCOREBOARD_V1.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_C1_EUR_BUY_FAILURE_REGIME_SCOREBOARD_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_C1_EUR_BUY_OPTIMIZATION_SCOREBOARD_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_C1_EUR_BUY_WALK_FORWARD_STABILITY_SCOREBOARD_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_CAMPAIGN_EVIDENCE_ACCUMULATOR_V1_REPORT.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_CANDIDATE_EVIDENCE_INTAKE_V1_REPORT.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_CANDIDATE_INTAKE_DEMO_REVIEW_BRIDGE_V1_REPORT.md` | Demo / paper operation evidence | ACTIVE_LOCAL_MODIFIED | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_CANDIDATE_LEADERBOARD_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_CANDIDATE_REPLACEMENT_ANALYSIS_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_CANDIDATE_TO_GATE_BRIDGE_V1_REPORT.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_CANONICAL_COMPLETION_ROADMAP_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_CANONICAL_DEMO_REVIEW_EVIDENCE_BRIDGE_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_CAPITAL_ALLOCATION_GATE_V1_REPORT.md` | Capital / compounding evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_CAPITAL_COMPOUNDING_SAFETY_LANE_V1_REPORT.md` | Capital / compounding evidence | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_CLEANUP_CLASSIFICATION_DRYRUN_V2.md` | Audit / review artifact | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_CLOUDFLARE_PORTAL_OPERATOR_ACCESS_CONTEXT_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_COLLECT_MISSING_REAL_EVIDENCE_V1_REPORT.md` | Evidence intake / proof artifact | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_COMPLETION_CLEANUP_VALIDATION_UNBLOCK_V2_REPORT.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_COMPLETION_FULL_RERUN_VALIDATION_V1_REPORT.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_COMPLETION_REPAIR_PROMPT_V1_REPORT.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_COMPOUNDING_CAPITAL_BUCKET_SUPERVISOR_V1.md` | Capital / compounding evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_CONNECTOR_AND_READONLY_EVIDENCE_FINAL_CONSOLIDATION_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_CONNECTOR_RUNTIME_HANDOFF_ORCHESTRATION_DESIGN_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_CONSOLIDATED_READINESS_BLOCKER_CLOSURE_V1_REPORT.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_CONTINUOUS_CLOSURE_LONG_RUN_V2_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_CONTINUOUS_CLOSURE_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_CONTINUOUS_EVIDENCE_ADVANCEMENT_V1_REPORT.md` | Evidence intake / proof artifact | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_CONTINUOUS_LONG_RUN_V3_REPORT.md` | Other forex delivery artifact | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_CREDENTIAL_VAULT_READINESS_ENGINE_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_CROSS_REFERENCE_VALIDATION_V1_REPORT.md` | Validation / gate report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_CURRENT_BRANCH_ARCHITECTURE_NOTE_V1_REPORT.md` | Publication / PR hygiene | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Owner Review and clean git state | Closure |
| `AIOS_FOREX_CURRENT_BRANCH_PRESERVATION_PROTECTED_ACTION_GATE_V1_DRY_RUN_REPORT.md` | Publication / PR hygiene | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Owner Review and clean git state | Closure |
| `AIOS_FOREX_DASHBOARD_TRUTH_WIRING_V1_REPORT.md` | Audit / review artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_DASHBOARD_VALIDATOR_SCOPE_REPAIR_V1_REPORT.md` | Validation / gate report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_DELIVERY_GOVERNED_APPLY_V2_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_DEMO_BROKER_CONNECTIVITY_AUTHORIZATION_GATE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_DEMO_BROKER_SNAPSHOT_REVIEW_PACKET_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_DEMO_CANDIDATE_LIFECYCLE_MANAGER_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_DEMO_CONNECTOR_READONLY_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_DEMO_LOSS_REVIEW_METRICS_GATE_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_GATE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_DEMO_MULTI_TRADE_RUNNER_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_DEMO_ORDER_MAPPING_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_DEMO_ORDER_PLAN_BUILDER_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_DEMO_OWNER_APPROVAL_GATE_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_DEMO_PHASE_EVIDENCE_TRACKER_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_DEMO_PHASE_OPERATOR_REVIEW_PACKET_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_DEMO_PHASE_PERFORMANCE_MONITOR_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_DEMO_PHASE_RISK_ESCALATION_ENGINE_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_DEMO_READINESS_PROFIT_TRUST_SPINE_CLOSEOUT_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_DEMO_READINESS_PROFIT_TRUST_SPINE_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_DEMO_READINESS_SPINE_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_DEMO_RECONCILIATION_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_DEMO_REHEARSAL_EVIDENCE_BUNDLE_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_DEMO_REHEARSAL_RUNNER_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_DEMO_REVIEW_ENGINE_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_DEMO_REVIEW_EPIC_REPORT_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_DEMO_REVIEW_READINESS_ENGINE_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_DEMO_REVIEW_VERDICT_CONSUMER_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_DEMO_TRADE_DECISION_DRY_RUN_LANE_V1_REPORT.md` | Demo / paper operation evidence | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_DEMO_TRADE_READINESS_BRIDGE_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_DEMO_VALIDATION_CONTRACT_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_DEMO_VALIDATION_ORCHESTRATOR_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_DEMO_VALIDATION_RESULT_AGGREGATOR_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_DEMO_VALIDATION_SUPERVISOR_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_DEPENDENCY_AUDIT_V1_REPORT.md` | Audit / review artifact | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_DIRECTIONAL_EDGE_ANALYSIS_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_DIRTY_MAIN_PRESERVATION_REVIEW_V1_REPORT.md` | Publication / PR hygiene | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Owner Review and clean git state | Closure |
| `AIOS_FOREX_EDGE_DISCOVERY_SCOREBOARD_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_END_TO_END_JOURNEY_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_EOM_LIVE_TRADE_REMAINING_15_PERCENT_CLOSURE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_EPC004_22H6D_AUGMENTATION_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_EPIC_BUCKET_PACKET_CONSOLIDATION_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_EVIDENCE_CACHE_KNOWN_PATH_REGISTRY_V1_REPORT.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_EVIDENCE_CACHE_V1_REPORT.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_EVIDENCE_DEPTH_EXPANSION_PACKET_Q_V1_REPORT.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_EVIDENCE_DEPTH_QUALITY_GATE_MANUAL_FINALIZATION_V1.md` | Closure / closeout report | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_EVIDENCE_DEPTH_QUALITY_GATE_V1.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_EVIDENCE_GAP_CLOSURE_LANDING_REVIEW_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_EVIDENCE_INDEX_V1_REPORT.md` | Evidence intake / proof artifact | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_EVIDENCE_LANDING_RECONCILE_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_EVIDENCE_LEDGER_V1_REPORT.md` | Evidence intake / proof artifact | ACTIVE_REFERENCE_ANCHOR | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_EVIDENCE_MILESTONE_CONTINUATION_V1_REPORT.md` | Evidence intake / proof artifact | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_EVIDENCE_SCHEMA_CONTRACTS_IMPLEMENTATION_PACKET_F_V1_REPORT.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_EVIDENCE_SCHEMA_IMPLEMENTATION_PREPARATION_PACKET_E_V1_REPORT.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_EVIDENCE_SCHEMA_INVENTORY_V1.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_EVIDENCE_SCHEMA_TEST_MATRIX_V1.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_EXCEPTION_SPECIFIC_PROOF_MATRIX_DRY_RUN_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_EXPANDED_CANDIDATE_SCOREBOARD_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_EXPECTANCY_STRENGTH_ROUTER_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_EXPECTANCY_TICKET_GATE_CLOSURE_V1.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_EXTERNAL_PROOF_REQUIREMENTS_CHECKLIST_DRY_RUN_V1.md` | Evidence intake / proof artifact | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_FAILURE_REGIME_ANALYSIS_PACKET_S_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_FINAL_ARMING_PACKET_CHECKLIST_DRY_RUN_V1.md` | Closure / closeout report | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_FINAL_BUNDLE_REPAIR_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_FINAL_CLOSURE_AUDIT_LANE_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_FINAL_COMPLETION_AUDIT_V1.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_FINAL_GAP_ANALYSIS_V1_REPORT.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_FINAL_LIVE_OPERATOR_BRIDGE_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_FINAL_REMAINING_WORK_CONSOLIDATION_V1.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_FINAL_SYSTEM_VALIDATION_CLOSURE_LANE_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_FIRST_BLOCKER_COLLAPSE_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_FIRST_DAY_TRADING_STRATEGY_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_FIRST_LIVE_MICRO_TRADE_EXECUTION_PATH_V2.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_FIRST_LIVE_MICRO_TRADE_PROOF_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_FIRST_REAL_BLOCKER_VALIDATION_DRYRUN_V1.md` | Validation / gate report | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_FUNDING_READINESS_TRANSFER_GATE_V1_REPORT.md` | Capital / compounding evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_GIG_CLOSEOUT_V1.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_GOVERNANCE_CONSOLIDATION_V1_REPORT.md` | Governance / contract evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_GOVERNED_DEMO_ADVANCEMENT_GATE_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_GOVERNED_DEMO_EXECUTION_DECISION_TREE_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_HUMAN_OWNER_APPROVAL_PACKAGE_DRAFT_DRY_RUN_V1.md` | Other forex delivery artifact | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_HUMAN_OWNER_APPROVAL_PACKAGE_REVIEWABLE_DRAFT_DRY_RUN_V1.md` | Audit / review artifact | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_IMPLEMENTATION_BACKLOG_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_IMPLEMENTATION_PHASE_ACCELERATION_PACKET_D_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_IMPLEMENTATION_PHASE_TICKET_SEQUENCE_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_IMPLEMENTATION_READINESS_ASSESSMENT_V1_REPORT.md` | Readiness / state report | SUPERSEDED_CANDIDATE_VERSION_FAMILY | Candidate successor by version family: AIOS_FOREX_IMPLEMENTATION_READINESS_ASSESSMENT_V1.md | Validation | Owner Review |
| `AIOS_FOREX_IMPLEMENTATION_READINESS_ASSESSMENT_V1.md` | Readiness / state report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_INCIDENT_STOP_PROCEDURE_V1.md` | Governance / contract evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_INSUFFICIENT_SAMPLE_COLLAPSE_APPLY_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_INTENT_RECORD_SPEC_V1.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_INTENT_TO_ATTEMPT_EVIDENCE_SCHEMA_PLAN_V1.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_JOURNEY_STATUS_CLI_V1_REPORT.md` | Readiness / state report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_KILL_SWITCH_ROLLBACK_PROOF_DRY_RUN_V1.md` | Evidence intake / proof artifact | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_LIVE_ARMING_EVIDENCE_BUNDLE_COMPLETENESS_DRY_RUN_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_LIVE_ARMING_EVIDENCE_GAP_DRY_RUN_V1_REPORT.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_LIVE_CANDIDATE_READINESS_SPINE_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_LIVE_EXECUTION_TO_80_UPTIME_MASTER_V2.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_LIVE_KILL_SWITCH_READINESS_ENGINE_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_LIVE_MICRO_TRADE_ARMING_GATE_DRY_RUN_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_LIVE_MULTI_TRADE_EXPANSION_GATE_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_LIVE_READINESS_CONSOLIDATED_BLOCKER_BURNDOWN_DRY_RUN_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_LIVE_READINESS_REVIEW_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_LIVE_REVIEW_CONNECTOR_TO_CONTRACT_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_LIVE_REVIEW_READINESS_CERTIFICATE_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_LOCAL_COMMIT_10ED5808_CONVERGENCE_VALIDATION_V1_REPORT.md` | Publication / PR hygiene | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Owner Review and clean git state | Closure |
| `AIOS_FOREX_LOCAL_COMMIT_10ED5808_PRESERVATION_VALIDATION_V1_REPORT.md` | Publication / PR hygiene | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Owner Review and clean git state | Closure |
| `AIOS_FOREX_LONG_ONLY_AUTONOMOUS_SUPERVISOR_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_LONG_RUN_PAPER_SUPERVISOR_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_LONG_SHORT_EVIDENCE_DEPTH_MATRIX_V1.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_LOSS_TO_NEXT_PROFIT_CANDIDATE_GATE_V1_REPORT.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_MARKET_DATA_NORMALIZER_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_MARKET_REGIME_EVALUATION_HARNESS_V1_REPORT.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_MASTER_CLOSURE_LONG_RUN_V1_REPORT.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_MASTER_COMPLETION_LONG_RUN_APPLY_V1_REPORT.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_MASTER_CONVERGENCE_LONG_RUN_V2_REPORT.md` | Other forex delivery artifact | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_METADATA_INVENTORY_V1_REPORT.md` | Audit / review artifact | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_MEAN_REVERSION_STRATEGY_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_MICRO_BATCH_CAMPAIGN_LADDER_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_MINIMUM_VIABLE_DEMO_INTEGRATION_PATH_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_MITIGATION_OPTIMIZATION_PACKET_T_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_MITIGATION_ROOT_CAUSE_APPLY_V2.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_MONTH_END_BLOCKER_BURNDOWN_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_MULTI_TRADE_QUEUE_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_NEXT_ACTION_ENGINE_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_NEXT_ARMING_CLASSIFICATION_V1.md` | Audit / review artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_NEXT_CANDIDATE_DISCOVERY_PACKET_U_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_NEXT_HUMAN_ARMING_CANDIDATE_GATE_V1.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_NEXT_PROFIT_ACTION_RECOMMENDATION_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_NEXT_TRADE_ELIGIBILITY_REPEAT_PROOF_GATE_V1_REPORT.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_NO_ORDER_CONNECTOR_CONTRACTS_IMPLEMENTATION_PACKET_G_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_NO_ORDER_CONNECTOR_TEST_STRATEGY_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_NO_SECRET_NO_ACCOUNT_ID_SCAN_EVIDENCE_DRY_RUN_V1.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_CLOSED_TRADE_TPSL_RESULT_CAPTURE_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_BID_ASK_CORRECTED_RUNTIME_PACKET_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_BID_ASK_SLTP_VALIDATION_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_OANDA_DEMO_BIDASK_CORRECTED_POST_TRADE_EVIDENCE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_BROKER_ADAPTER_ONE_ORDER_FINAL_WIRE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_OANDA_DEMO_BROKER_CALL_IMPLEMENTATION_ONE_ORDER_MANUAL_RUN_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_BROKER_EXECUTION_PACKET_ONE_ORDER_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_CORRECTED_FUTURE_POST_TRADE_EVIDENCE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_CORRECTED_FUTURE_RUNTIME_PACKET_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_CORRECTED_ORDER_COMMAND_PACKAGE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_CREDENTIAL_ACCOUNT_PERMISSION_PREFLIGHT_NO_ORDER_V1.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_AUDIT_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_EPIC_REPORT_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_MANUAL_FINALIZATION_V1.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_EXPECTANCY_SUFFICIENCY_GATE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_OANDA_DEMO_EXPECTANCY_TO_LIVE_EVIDENCE_BUNDLE_EPIC_REPORT_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_EXPECTANCY_TO_LIVE_EVIDENCE_BUNDLE_MANUAL_FINALIZATION_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_EXPECTANCY_TO_LIVE_GAP_MAPPER_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_FILLED_TRADE_RESULT_BUCKET_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_FINAL_OWNER_CLICK_ORDER_BRIDGE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_FINAL_OWNER_ORDER_COMMAND_REVIEW_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_FINAL_OWNER_RUNTIME_RUN_ONE_ORDER_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_FIRST_ORDER_ATTEMPT_403_EVIDENCE_CAPTURE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_FIRST_TRADE_ACTUAL_OWNER_COMMAND_RUN.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_FIRST_TRADE_OWNER_MANUAL_EXECUTION_WINDOW_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_FIRST_TRADE_RUNBOOK_AND_OWNER_GO_NOGO_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_FUTURE_ORDER_APPROVAL_GATE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_INTEGRATION_BOUNDARY_PLAN_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_LIVE_EVIDENCE_BUNDLE_GAP_GATE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_OANDA_DEMO_LIVE_EVIDENCE_REQUIREMENT_MATRIX_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_OANDA_DEMO_LIVE_QUOTE_DERIVED_POST_TRADE_EVIDENCE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_LIVE_QUOTE_DERIVED_SLTP_RUNTIME_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_MICRO_TRADE_OWNER_APPROVAL_EVIDENCE_CAPTURE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_MICRO_TRADE_PROFITABILITY_BRIDGE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_ONE_TRADE_READINESS_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_OANDA_DEMO_OPEN_TRADE_MONITOR_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_OPEN_UNREALIZED_PL_RESULT_BUCKET_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_OWNER_ONE_TRADE_COMMAND_PACKAGE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_OWNER_RUN_ACTUAL_ONE_ORDER_COMMAND_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_GENERATOR_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_ATTEMPT_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_OWNER_VAULT_SAVE_HELPER_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_PACKET12E_SANITIZED_EVIDENCE_CHAIN_READINESS_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_OANDA_DEMO_PACKET12F_OWNER_READ_HELPER_REQUIRED_FIELDS_COMPLETION_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_PL_RESULT_BUCKET_REPEAT_PROOF_LANE_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_PL_RESULT_QUALITY_GATE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_OANDA_DEMO_POST_TRADE_EVIDENCE_CAPTURE_OWNER_RUN_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_POST_TRADE_EVIDENCE_CAPTURE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_PROFIT_PROOF_GAP_BRIDGE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_READ_ONLY_FILLED_TRADE_PL_CAPTURE_IDRANGE_REPAIR_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_READ_ONLY_FILLED_TRADE_PL_CAPTURE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_EPIC_REPORT_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_READ_ONLY_PL_PROFIT_PROOF_MANUAL_FINALIZATION_V1.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_READ_ONLY_PL_RESULT_INTAKE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_READ_ONLY_PREFLIGHT_FROM_VAULT_V1.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_READ_ONLY_PREFLIGHT_RESULT_CAPTURE_V1.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_ACCUMULATOR_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_EPIC_REPORT_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_REPEATED_EXPECTANCY_SAMPLE_MANUAL_FINALIZATION_V1.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_RESULT_BUCKET_AND_NEXT_ALLOCATION_AFTER_CANCEL_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_RESULT_TO_BUCKET_AND_NEXT_ALLOCATION_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_RUNTIME_AUTH_BOUNDARY_READ_ONLY_HELPER_REPAIR_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_RUNTIME_EXECUTOR_DRYRUN_V1.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_RUNTIME_EXECUTOR_FINAL_GATED_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_OANDA_DEMO_RUNTIME_EXECUTOR_ONE_ORDER_ONLY_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_RUNTIME_HTTP_TRANSPORT_ONE_ORDER_OWNER_RUN_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_RUNTIME_ONE_ORDER_EXECUTION_EXCEPTION_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_RUNTIME_ONLY_ORDER_TICKET_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_RUN_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_SANITIZED_OWNER_RUN_READ_ONLY_TELEMETRY_ADAPTER_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_SANITIZED_PACKET09_JSON_EXPORT_LOCATOR_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_SANITIZED_TELEMETRY_SHAPE_NORMALIZER_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_DEMO_SECURE_CREDENTIAL_PERSISTENCE_WINDOWS_VAULT_V1_REPORT.md` | Broker / OANDA evidence | SUPERSEDED_CANDIDATE_VERSION_FAMILY | Candidate successor by version family: AIOS_FOREX_OANDA_DEMO_SECURE_CREDENTIAL_PERSISTENCE_WINDOWS_VAULT_V1.md | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_SECURE_CREDENTIAL_PERSISTENCE_WINDOWS_VAULT_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_SLTP_VALIDATION_CORRECTION_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_OANDA_DEMO_TO_LIVE_PROFIT_READINESS_TRUTH_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_OANDA_DEMO_TRADE_320_OWNER_RUN_READ_ONLY_REFRESH_GATE_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_DEMO_TRADE_320_READ_ONLY_BROKER_TELEMETRY_REPAIR_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_TRADE_320_READ_ONLY_PL_REFRESH_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_VAULT_BACKED_ONE_ORDER_TRANSPORT_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_VAULT_MISSING_CREDENTIAL_RECOVERY_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_DEMO_VAULT_PREFLIGHT_TRUTH_RUNBOOK_V1.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_OANDA_DEMO_VAULT_READONLY_PREFLIGHT_NEXT_STEP_V1.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_LEFTOVER_PROOF_CHAIN_INTAKE_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_MANUAL_FINALIZATION_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_LIVE_MICROTRADE_PROFIT_PROOF_CANDIDATE_REVIEW_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_MANUAL_FINALIZATION_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_MANUAL_FINALIZATION_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_PLAN_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_MANUAL_FINALIZATION_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_LIVE_MICROTRADE_RESULT_TO_NEXT_PROOF_ROUTER_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_GATE_MANUAL_FINALIZATION_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_LIVE_MICROTRADE_ROUTED_PROOF_OWNER_DECISION_GATE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_MANUAL_FINALIZATION_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_LIVE_MICROTRADE_SELECTED_PROOF_PACKET_PREVIEW_CATALOG_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_OANDA_LONG_ONLY_BROKER_PROOF_INTAKE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_OWNER_RUN_CLOSED_RESULT_ADAPTER_EXERCISE_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RECONCILIATION_GATE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_EPIC_REPORT_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_MANUAL_FINALIZATION_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CLASSIFIER_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_GATE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_READONLY_ACCOUNT_SNAPSHOT_BALANCE_SEPARATION_ADAPTER_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_READONLY_CLOSED_RESULT_TPSL_CLASSIFIER_ADAPTER_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_DISARM_RECOVERY_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_EPIC_REPORT_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_OWNER_RUN_MANUAL_FINALIZATION_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_POST_TRADE_CAPTURE_PLAN_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_TICKET_PREVIEW_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_OANDA_VACATION_PROFIT_AUTONOMY_CONTROL_GATE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_OANDA_VACATION_PROFIT_COMPOUNDING_PERMISSION_GATE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_OANDA_VACATION_PROFIT_LIVE_SAMPLE_GATE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_OANDA_VACATION_PROFIT_READINESS_CONTRACT_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_OANDA_VACATION_PROFIT_READINESS_EPIC_REPORT_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_OANDA_VACATION_PROFIT_READINESS_MANUAL_FINALIZATION_V1.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_OANDA_VACATION_PROFIT_TRIAL_PLAN_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_ONE_SHOT_EXCEPTION_ASSEMBLER_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_ONE_SHOT_LIVE_MICRO_TRADE_ARMING_REVIEW_DRY_RUN_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_ONE_SHOT_LIVE_MICRO_TRADE_EXECUTION_REVIEW_DRY_RUN_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_OPERATIONAL_READINESS_CERTIFICATION_V1_REPORT.md` | Readiness / state report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_OPERATOR_NEXT_TRADE_REVIEW_COMPOSER_V1_REPORT.md` | Audit / review artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_OPERATOR_NEXT_TRADE_REVIEW_RUNNER_V1_REPORT.md` | Audit / review artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_ORDER_PREVIEW_HARDENING_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_OVERNIGHT_PROFIT_EXECUTION_READINESS_V1.md` | Readiness / state report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_OWNER_GONOGO_COMMAND_CENTER_REPORT_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_PAPER_ENGINE_SPINE_V2_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PAPER_EVIDENCE_PROMOTION_GATE_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_PAPER_FILL_SIMULATOR_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PAPER_PROFITABILITY_EVALUATOR_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PAPER_SESSION_SAMPLE_GENERATOR_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PAPER_SESSION_SUPERVISOR_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PAPER_SIGNAL_EXECUTION_LOOP_DRY_RUN_V1.md` | Demo / paper operation evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PAPER_TO_DEMO_PROMOTION_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PAPER_TO_DEMO_PROMOTION_WORKFLOW_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PAPER_TRADE_MODEL_V1_REPORT.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PARALLEL_WORKER_SYNTHESIS_INTAKE_V1_REPORT.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_PERSISTENT_BROKER_EXECUTION_HANDOFF_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PHASE1_LAND_AND_GATE_V2_REPORT.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_PLUMBING_DIAGNOSTIC_CAMPAIGN_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PORTFOLIO_EVIDENCE_ACCUMULATION_RUNNER_V1_REPORT.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_PORTFOLIO_PROMOTION_DECISION_ENGINE_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_POSITION_SIZING_V1_REPORT.md` | Capital / compounding evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_POST_TRADE_EVIDENCE_CAPTURE_PLAN_V2.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_POST_TRADE_EVIDENCE_CAPTURE_V1.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_PR_1040_SECRET_SCAN_FIX_V1.md` | Publication / PR hygiene | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Owner Review and clean git state | Closure |
| `AIOS_FOREX_PRESERVATION_PR_HYGIENE_LANE_V1_REPORT.md` | Publication / PR hygiene | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Owner Review and clean git state | Closure |
| `AIOS_FOREX_PROFIT_AUTONOMY_MASTER_BUCKET_PACK_V1_REPORT.md` | Other forex delivery artifact | SUPERSEDED_CANDIDATE_VERSION_FAMILY | Candidate successor by version family: AIOS_FOREX_PROFIT_AUTONOMY_MASTER_BUCKET_PACK_V1.md | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PROFIT_AUTONOMY_MASTER_BUCKET_PACK_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PROFIT_CAMPAIGN_GO_LIVE_WRAPUP_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_PROFIT_GATE_FAILURE_ANALYSIS_V1.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_PROFIT_OBJECTIVE_ACCELERATION_PACKET_L_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PROFIT_PROOF_LEDGER_V1_REPORT.md` | Evidence intake / proof artifact | SUPERSEDED_CANDIDATE_VERSION_FAMILY | Candidate successor by version family: AIOS_FOREX_PROFIT_PROOF_LEDGER_V1.md | Source evidence and prior report context | Validation |
| `AIOS_FOREX_PROFIT_PROOF_LEDGER_V1.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_PROFIT_VALIDATION_LOOP_V1_REPORT.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_PROFITABILITY_PROOF_AND_BEST_CANDIDATE_DISCOVERY_PACKET_M_V1.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_PROFITABILITY_PROOF_PACKET_M_V1_REPORT.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_PROFITABILITY_VERDICT_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PROFITABLE_LIVE_BOT_FINAL_EXECUTION_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_PROOF_BUNDLE_TO_CANDIDATE_BRIDGE_V1_REPORT.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_PROOF_GAP_CLOSURE_PLAN_V1_REPORT.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_PROTECTED_ACTION_APPROVAL_RECORD_TEMPLATE_DRY_RUN_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_PROTECTED_ACTION_APPROVAL_REVIEW_DRY_RUN_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_PROTECTED_BROKER_CONNECTION_TEST_APPLY_PACKET_DRAFT_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_PROTECTED_BROKER_CONNECTION_TEST_APPLY_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_PROTECTED_BROKER_DEMO_CONNECTOR_GATE_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_PROTECTED_BROKER_DEMO_RUNTIME_PLAN_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PROTECTED_CONNECTOR_PREFLIGHT_DRY_RUN_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PROTECTED_DEMO_MICRO_ORDER_EXECUTION_PACKET_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_PROTECTED_DEMO_MICRO_ORDER_REVIEW_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_PUBLICATION_EXECUTION_PLAN_V2_REPORT.md` | Publication / PR hygiene | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Owner Review and clean git state | Closure |
| `AIOS_FOREX_PUBLICATION_PR_LANDING_LANE_V1_REPORT.md` | Publication / PR hygiene | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Owner Review and clean git state | Closure |
| `AIOS_FOREX_READ_ONLY_EVIDENCE_APPROVAL_AND_RECONCILIATION_DRY_RUN_V1.md` | Evidence intake / proof artifact | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_READ_ONLY_EVIDENCE_BLOCKER_BURNDOWN_DRY_RUN_V1.md` | Evidence intake / proof artifact | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_READ_ONLY_LIVE_DATA_BRIDGE_DRY_RUN_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_READ_ONLY_RECONCILIATION_PROPAGATION_DRY_RUN_V1.md` | Other forex delivery artifact | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_READINESS_MATRIX_V1_REPORT.md` | Readiness / state report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_READINESS_STATE_RECALCULATION_V1_REPORT.md` | Readiness / state report | ACTIVE_REFERENCE_ANCHOR | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_READONLY_BROKER_SANITIZED_EVIDENCE_CLOSURE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_REAL_CANDIDATE_EVIDENCE_EXPANSION_PACKET_P_V1.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_REAL_EVIDENCE_DEPTH_ENGINE_V1.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_REAL_EVIDENCE_DEPTH_EPIC_REPORT_V1.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_REAL_EVIDENCE_GAP_CLOSURE_LONG_RUN_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_REAL_EVIDENCE_INTAKE_REVALIDATION_V1_REPORT.md` | Validation / gate report | ACTIVE_CURRENT_UNTRACKED | Candidate successor by version family: AIOS_FOREX_REAL_EVIDENCE_INTAKE_REVALIDATION_V2_REPORT.md | Evidence Intake | Readiness |
| `AIOS_FOREX_REAL_EVIDENCE_INTAKE_REVALIDATION_V2_REPORT.md` | Validation / gate report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_REAL_EVIDENCE_INTAKE_V1_REPORT.md` | Evidence intake / proof artifact | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_REAL_PROFIT_EVIDENCE_CONTINUATION_V1_REPORT.md` | Evidence intake / proof artifact | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_REALIZED_PL_RESULT_BUCKET_UPDATE_GATE_V1_REPORT.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_RELEASE_MANIFEST_V1_REPORT.md` | Publication / PR hygiene | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Owner Review and clean git state | Closure |
| `AIOS_FOREX_REMAINING_WORK_INVENTORY_V1_REPORT.md` | Audit / review artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_REPLAY_RECONCILIATION_PROOF_BUNDLE_V1_REPORT.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_REPLAY_WALKFORWARD_PROFITABILITY_EVIDENCE_VALIDATION_V1_REPORT.md` | Validation / gate report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_REPORT_INDEX_CLASSIFIER_V1_REPORT.md` | Audit / review artifact | ACTIVE_REFERENCE_ANCHOR | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_REVIEW_CHAIN_END_TO_END_CANDIDATE_JOURNEY_V1_REPORT.md` | Audit / review artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_REVIEW_CHAIN_ORCHESTRATOR_V1_REPORT.md` | Audit / review artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_REVIEW_READY_CANDIDATE_SELECTOR_V1_REPORT.md` | Readiness / state report | SUPERSEDED_CANDIDATE_VERSION_FAMILY | Candidate successor by version family: AIOS_FOREX_REVIEW_READY_CANDIDATE_SELECTOR_V1.md | Validation | Owner Review |
| `AIOS_FOREX_REVIEW_READY_CANDIDATE_SELECTOR_V1.md` | Readiness / state report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_REVIEW_READY_STAGE_CHAIN_CONTINUITY_V1_REPORT.md` | Readiness / state report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_RISK_BLOCKER_CLOSURE_LIVE_MICRO_GATE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_RISK_GOVERNOR_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_RUNTIME_COMPLETION_PACKET_I_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_RUNTIME_EXECUTED_EDGE_EVIDENCE_PACKET_O_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_RUNTIME_EXECUTED_EDGE_EVIDENCE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_RUNTIME_EXECUTED_PROFITABILITY_VERDICT_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_RUNTIME_EXECUTED_TOP_CANDIDATE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_RUNTIME_FOUNDATION_COMPLETION_PACKET_H_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_RUNTIME_FOUNDATION_MILESTONE_COMPLETION_CERTIFICATE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_SANITIZED_BROKER_SNAPSHOT_INTAKE_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_SANITIZED_TERMINAL_PROOF_INTAKE_PREFLIGHT_V1.md` | Evidence intake / proof artifact | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_SCHEMA_IMPLEMENTATION_ROADMAP_V1.md` | Audit / review artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_SELF_IMPROVEMENT_REVIEW_V1_REPORT.md` | Audit / review artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_SESSION_REPLAY_TEST_REGRESSION_FIX_V1_REPORT.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_SESSION_REPLAY_V1_REPORT.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_SHUTDOWN_RECOVERY_LANDING_REVIEW_V1_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_SIX_BULLET_EXECUTION_TRACKER_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_SOS_OWNER_ALERT_BRIDGE_MANUAL_FINALIZATION_V1.md` | Closure / closeout report | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_SOS_OWNER_ALERT_BRIDGE_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_SOURCE_CHAIN_CLOSEOUT_V1_REPORT.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_SPRINT2B_BROKER_HEALTH_SPEC_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_SPRINT2B_CURRENT_MAIN_IMPLEMENTATION_QUEUE_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_SPRINT2B_DASHBOARD_TRUTH_SPEC_V1_REPORT.md` | Audit / review artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_SPRINT2B_PROFITABILITY_EVIDENCE_SPEC_V1_REPORT.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_SPRINT2B_RISK_BUDGET_SPEC_V1_REPORT.md` | Governance / contract evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_STATISTICAL_PROFIT_PROOF_GATE_MANUAL_FINALIZATION_V1.md` | Closure / closeout report | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_STATISTICAL_PROFIT_PROOF_GATE_V1.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_STRATEGY_CAMPAIGN_SUPERVISOR_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_STRATEGY_CANDIDATES_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_STRATEGY_EVALUATION_HARNESS_V1_REPORT.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_STRATEGY_PORTFOLIO_COMPETITION_RUNNER_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_STRATEGY_PORTFOLIO_RANKING_ENGINE_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_STRATEGY_PROMOTION_ROUTER_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_STRATEGY_PROOF_ENGINE_V1_REPORT.md` | Evidence intake / proof artifact | SUPERSEDED_CANDIDATE_VERSION_FAMILY | Candidate successor by version family: AIOS_FOREX_STRATEGY_PROOF_ENGINE_V1.md | Source evidence and prior report context | Validation |
| `AIOS_FOREX_STRATEGY_PROOF_ENGINE_V1.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_SUPERVISED_COMPOUNDING_POLICY_GATE_MANUAL_FINALIZATION_V1.md` | Demo / paper operation evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_SUPERVISED_COMPOUNDING_POLICY_GATE_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_EPIC_REPORT_V1.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_SUPERVISED_DEMO_BROKER_SNAPSHOT_INTAKE_MANUAL_FINALIZATION_V1.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_EPIC_REPORT_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_MANUAL_FINALIZATION_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_SUPERVISED_DEMO_MANUAL_EXECUTION_EXCEPTION_PACKET_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_SUPERVISED_DEMO_OPERATIONAL_VALIDATION_RUNNER_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_SUPERVISED_DEMO_OWNER_APPROVAL_EPIC_REPORT_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_SUPERVISED_DEMO_OWNER_APPROVAL_MANUAL_FINALIZATION_V1.md` | Demo / paper operation evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_SUPERVISED_DEMO_OWNER_APPROVAL_PACKET_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_SUPERVISED_DEMO_TRADE_EPIC_REPORT_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_SUPERVISED_DEMO_TRADE_EPIC_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_SUPERVISED_DEMO_TRADE_MANUAL_FINALIZATION_V1.md` | Demo / paper operation evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_SUPERVISED_DEMO_TRADE_READINESS_EPIC_REPORT_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_SUPERVISED_DEMO_TRADE_READINESS_MANUAL_FINALIZATION_V1.md` | Demo / paper operation evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_SUPERVISED_DEMO_TRADE_REVIEW_BUNDLE_V1.md` | Demo / paper operation evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_TAKE_PROFIT_EVIDENCE_CLOSURE_V1.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_TAKE_PROFIT_RISK_GATE_CLOSURE_V1.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_TECHNICAL_DEBT_AUDIT_V1_REPORT.md` | Audit / review artifact | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_TERMINAL_EVIDENCE_BUNDLE_REVIEW_V1.md` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_TONIGHT_LIVE_TRADE_COMPLETION_ROADMAP_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_TOP_10_PROFIT_CANDIDATES_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_TOP_CANDIDATE_SCOREBOARD_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_TRADE_LATENCY_BASELINE_REPORTER_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_TRADE_LIFECYCLE_MANAGER_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_TRADE_TICKET_CLOSURE_V1.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_TRADING_HISTORY_WRITEBACK_VERIFICATION_DRY_RUN_V1.md` | Other forex delivery artifact | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_TRUSTED_PROFIT_22_6_EPIC_REPORT_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_TRUSTED_PROFIT_22_6_READINESS_V1.md` | Readiness / state report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_UPTIME_RANGE_PLANNER_80_22_5_22_6_V1.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_VACATION_MODE_FINAL_READINESS_DECISION_MANUAL_FINALIZATION_V1.md` | Closure / closeout report | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_VACATION_MODE_FINAL_READINESS_DECISION_V1.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_VACATION_MODE_READINESS_ORCHESTRATOR_MANUAL_FINALIZATION_V1.md` | Closure / closeout report | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_FOREX_VACATION_MODE_READINESS_ORCHESTRATOR_V1.md` | Readiness / state report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_FOREX_VALUE_FREE_BROKER_PROOF_INTAKE_DRY_RUN_V1.md` | Broker / OANDA evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_FOREX_WALK_FORWARD_DEPTH_PACKET_R_V1_REPORT.md` | Other forex delivery artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_WALK_FORWARD_FAILURE_ROOT_CAUSE_MATRIX_V1.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_WALK_FORWARD_WINDOW_MATRIX_V1.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_FOREX_WALKFORWARD_OOS_CLOSURE_V2_REPORT.md` | Closure / closeout report | ACTIVE_CURRENT_UNTRACKED | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_FOREX_WALKFORWARD_ROOT_CAUSE_DRYRUN_V2.md` | Other forex delivery artifact | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_FOREX_WALKFORWARD_VALIDATION_HARNESS_V1_REPORT.md` | Validation / gate report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_LIVE_EXECUTION_MILESTONE_SPRINT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_01_REPORT.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_02_DEMO_RUNTIME_READINESS_DRY_RUN_REPORT.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Validation | Owner Review |
| `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_03_DEMO_CONNECTION_PROOF_PREFLIGHT_DRY_RUN_REPORT.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_04_DEMO_CONNECTION_PROOF_APPROVAL_REVIEW_DRY_RUN_REPORT.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_05_DEMO_CONNECTION_PROOF_REQUEST_DRAFT_DRY_RUN_REPORT.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_06_DEMO_CONNECTION_PROOF_PROTECTED_ACTION_GATE_DRY_RUN_REPORT.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_07_DEMO_CONNECTION_PROOF_EXECUTION_PACKET_DRAFT_DRY_RUN_REPORT.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_08_DEMO_CONNECTION_PROOF_PROTECTED_ACTION_APPROVAL_REVIEW_DRY_RUN_REPORT.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_09_DEMO_CONNECTION_PROOF_PROTECTED_ACTION_APPROVAL_RECORD_DRAFT_DRY_RUN_REPORT.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_APPROVAL_RECORD_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_APPROVAL_REVIEW_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_EXECUTION_AUTHORIZATION_STATUS_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_EXECUTION_PREREQUISITES_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_FILLED_APPROVAL_RECORD_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Readiness | Publication or Closure |
| `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_FINAL_BLOCKERS_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_POST_TRADE_RECONCILIATION_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_PROTECTED_EXECUTION_PACKET_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_PROTECTED_EXECUTION_PACKET_V1_SANITIZED_EVIDENCE.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_PROTECTED_EXECUTION_PREFLIGHT_V1.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_LIVE_MICRO_TRADE_READINESS_GATE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_LIVE_PREFLIGHT_EVIDENCE_BUNDLE_V1_REPORT.md` | Live / protected exception evidence | HISTORICAL_OR_DRY_RUN | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_LIVE_RUNTIME_EXECUTOR_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_MONEY_COCKPIT_100K_GOAL_LADDER_V11.md` | Capital / compounding evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_MONEY_COCKPIT_CAPITAL_FLOW_SIM_RANGE_V11.md` | Capital / compounding evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_MONEY_RELEVANCE_DASHBOARD_RULE_V11.md` | Capital / compounding evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_OANDA_DEMO_AUTH_HANDOFF_READINESS_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation | Owner Review |
| `AIOS_OANDA_DEMO_CONNECTION_FIRST_PROBE_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_OANDA_DEMO_CONNECTION_GATE_SPEC_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |
| `AIOS_OANDA_DEMO_PROBE_RUNTIME_HANDOFF_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_OANDA_DEMO_PROTECTED_CONNECTION_ATTEMPT_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_OANDA_DEMO_RUNTIME_HANDOFF_INTAKE_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_OANDA_LIVE_HTTP_TRANSPORT_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_OANDA_LIVE_RUNTIME_CONNECTOR_V2.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_PARALLEL_EXECUTION_DOCTRINE_V1_REPORT.md` | Governance / contract evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_POST_TRADE_LEDGER_REPLAY_CLOSEOUT_V1_REPORT.md` | Closure / closeout report | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Validation, Readiness, and Publication as applicable | Owner Review / later archive review |
| `AIOS_PROTECTED_LIVE_EXECUTION_COMMAND_PACKAGE_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_PROTECTED_RUNTIME_CREDENTIAL_INJECTION_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `AIOS_RUNTIME_VISIBILITY_CACHED_READ_MODEL_V1_REPORT.md` | Broker / OANDA evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `AIOS_SINGLE_PROTECTED_LIVE_MICRO_TRADE_EXECUTION_PACKAGE_V1_REPORT.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Prior Forex delivery context | Validation |
| `LIVE_MICRO_TRADE_CLOSE_EVIDENCE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `LIVE_MICRO_TRADE_EXECUTION_EVIDENCE_V1.md` | Live / protected exception evidence | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `proof_bundle_to_candidate_bridge_report.json` | Evidence intake / proof artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Source evidence and prior report context | Validation |
| `readiness_state_recalculation_v1_report.json` | Readiness / state report | ACTIVE_LOCAL_MODIFIED | Not stated in inspected text | Validation | Owner Review |
| `review_chain_end_to_end_candidate_journey.json` | Audit / review artifact | BASELINE_EVIDENCE_OR_HISTORY | Not stated in inspected text | Evidence Intake | Readiness |

## Stop Point

Stopped after writing this single report. No stage, commit, push, PR, merge, broker/API call, credential read, trade action, scheduler, daemon, webhook, production action, implementation edit, or existing report edit is approved or performed by this packet.

## Required Validators

- `git diff --check -- Reports/forex_delivery/AIOS_FOREX_EVIDENCE_INDEX_V1_REPORT.md`
- `Get-Content -LiteralPath Reports/forex_delivery/AIOS_FOREX_EVIDENCE_INDEX_V1_REPORT.md -Raw`
- `git status --short --branch`
