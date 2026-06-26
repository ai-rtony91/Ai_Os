# AIOS Forex Report Index Classifier V1 Report

Packet ID: AIOS-FOREX-REPORT-INDEX-CLASSIFIER-V1
Mode: APPLY
Zone: Reports Only
Lane: Forex Report Index Classification
Worktree: C:\Dev\Ai.Os
Branch required: feature/forex-epc004-22h6d-augmentation-v1

## Scope

This report is a read-only classification index for files under `Reports/forex_delivery`.

No existing file was moved, deleted, renamed, or modified. Classification is based on filenames only. File contents were not opened, broker code was not run, and secret-adjacent files were not read.

Preflight branch observed:

```text
## feature/forex-epc004-22h6d-augmentation-v1
 M docs/governance/programs/epics/EPC-FOREX-004-PRODUCTION-TRANSITION-V1.md
?? Reports/forex_delivery/AIOS_FOREX_EPC004_22H6D_AUGMENTATION_V1_REPORT.md
?? Reports/forex_delivery/AIOS_FOREX_GOVERNANCE_CONSOLIDATION_V1_REPORT.md
```

The existing dirty files above were treated as out of scope for mutation.

## Method

The directory contains a large flat delivery set, observed through `rg --files Reports/forex_delivery`. The successful enumeration reported 509 paths before this classifier report was created.

Labels are intentionally non-exclusive. A single file may belong to multiple categories, for example `broker/OANDA`, `demo execution`, `profit/P&L`, and `governance`.

## Classification Rules

| Category | Filename signals | Canonical mapping target |
|---|---|---|
| current-state | `STATUS`, `STATE`, `READINESS`, `TRUTH`, `CURRENT`, `JOURNEY`, `COMMAND_CENTER`, `FINAL`, `CLOSEOUT`, `COMPLETION`, `MILESTONE` | Current forex delivery status and owner decision surface |
| evidence-only | `EVIDENCE`, `PROOF`, `RECORD`, `LEDGER`, `CAPTURE`, `RESULT`, `REPLAY`, `SCAN`, `SANITIZED`, `.json` evidence output | Evidence ledger, proof bundle, or readback cache |
| superseded-candidate | older version siblings, `DRAFT`, older packet letters, older `V#` lines, duplicate theme variants | Archive review before canonical replacement |
| archive-candidate | old dry-run plans, obsolete bridge packets, closed sprint artifacts, one-time manual finalization files | Cold archive after canonical linkback |
| broker/OANDA | `BROKER`, `OANDA`, `CONNECTOR`, `ADAPTER`, `RUNTIME`, `TRANSPORT`, `ACCOUNT`, `ORDER`, `VAULT` | Broker integration and OANDA runtime spine |
| profit/P&L | `PROFIT`, `PROFITABILITY`, `PL`, `P_L`, `BALANCE`, `EQUITY`, `CAPITAL`, `FUNDING`, `COMPOUNDING`, `MONEY`, `POSITION`, `TAKE_PROFIT` | Profit proof and P&L result ledger |
| demo execution | `DEMO`, `PAPER`, `REHEARSAL`, `ORDER`, `ONE_ORDER`, `TRADE`, `EXECUTION`, `RUNBOOK`, `OWNER_RUN` | Demo execution and paper-to-demo operational lane |
| live exception | `LIVE`, `MICRO_TRADE`, `MICROTRADE`, `EXCEPTION`, `PROTECTED`, `ONE_SHOT`, `REAL`, `OWNER_APPROVAL` | Protected live micro-trade exception record |
| governance | `GOVERNANCE`, `GOVERNED`, `GATE`, `APPROVAL`, `POLICY`, `RISK`, `CONTRACT`, `SPEC`, `PROCEDURE`, `OWNER`, `PROTECTED`, `VALIDATION` | Governance, approval, and validator chain |
| dashboard truth | `DASHBOARD`, `TRUTH`, `STATUS`, `STATE`, `READ_MODEL`, `VISIBILITY`, `COMMAND_CENTER`, `JOURNEY`, `RECALCULATION` | Dashboard truth/read-model source |

Note: `RECALCULATION` above covers state-recalculation report and JSON naming by meaning, not only exact token spelling.

## Category Index

### current-state

High-priority files in this category include:

- `AIOS_FOREX_EPC004_22H6D_AUGMENTATION_V1_REPORT.md`
- `AIOS_FOREX_GOVERNANCE_CONSOLIDATION_V1_REPORT.md`
- `AIOS_FOREX_DASHBOARD_TRUTH_WIRING_V1_REPORT.md`
- `AIOS_FOREX_OANDA_DEMO_TO_LIVE_PROFIT_READINESS_TRUTH_V1.md`
- `AIOS_FOREX_READINESS_STATE_RECALCULATION_V1_REPORT.md`
- `readiness_state_recalculation_v1_report.json`
- `AIOS_FOREX_JOURNEY_STATUS_CLI_V1_REPORT.md`
- `AIOS_FOREX_END_TO_END_JOURNEY_V1_REPORT.md`
- `AIOS_RUNTIME_VISIBILITY_CACHED_READ_MODEL_V1_REPORT.md`
- `AIOS_FOREX_OWNER_GONOGO_COMMAND_CENTER_REPORT_V1_REPORT.md`
- `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_EXECUTION_AUTHORIZATION_STATUS_V1.md`
- `AIOS_FOREX_LIVE_REVIEW_READINESS_CERTIFICATE_V1_REPORT.md`
- `AIOS_FOREX_LIVE_READINESS_REVIEW_V1_REPORT.md`
- `AIOS_FOREX_FINAL_REMAINING_WORK_CONSOLIDATION_V1.md`
- `AIOS_FOREX_FINAL_COMPLETION_AUDIT_V1.md`
- `AIOS_FOREX_RUNTIME_FOUNDATION_MILESTONE_COMPLETION_CERTIFICATE_V1.md`

Canonical handling: keep these near the front of any future index. They are likely to answer "where are we now?" for Anthony, Codex, Claude, and dashboard consumers.

### evidence-only

High-priority files in this category include:

- `AIOS_FIRST_DEMO_CONNECTION_PROOF_APPLY_V1_SANITIZED_EVIDENCE.md`
- `AIOS_FIRST_DEMO_CONNECTION_PROOF_APPLY_WITH_EXTERNAL_RUNTIME_V1_SANITIZED_EVIDENCE.md`
- `AIOS_FIRST_DEMO_CONNECTION_PROOF_APPLY_WITH_CALLABLE_EXTERNAL_RUNTIME_V1_SANITIZED_EVIDENCE.md`
- `AIOS_FIRST_DEMO_CONNECTION_PROOF_CALLABLE_EXTERNAL_RUNTIME_RERUN_V1_SANITIZED_EVIDENCE.md`
- `AIOS_FIRST_DEMO_CONNECTION_PROOF_CONFIRMED_EXTERNAL_RUNTIME_V1_SANITIZED_EVIDENCE.md`
- `AIOS_FOREX_EVIDENCE_LEDGER_V1_REPORT.md`
- `AIOS_FOREX_EVIDENCE_CACHE_V1_REPORT.md`
- `AIOS_FOREX_EVIDENCE_CACHE_KNOWN_PATH_REGISTRY_V1_REPORT.md`
- `AIOS_FOREX_REPLAY_RECONCILIATION_PROOF_BUNDLE_V1_REPORT.md`
- `AIOS_FOREX_PROOF_BUNDLE_TO_CANDIDATE_BRIDGE_V1_REPORT.md`
- `proof_bundle_to_candidate_bridge_report.json`
- `AIOS_FOREX_NO_SECRET_NO_ACCOUNT_ID_SCAN_EVIDENCE_DRY_RUN_V1.md`
- `LIVE_MICRO_TRADE_EXECUTION_EVIDENCE_V1.md`
- `LIVE_MICRO_TRADE_CLOSE_EVIDENCE_V1.md`
- `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_PROTECTED_EXECUTION_PACKET_V1_SANITIZED_EVIDENCE.md`

Canonical handling: these should remain evidence inputs, not policy authority. Future maps should point to them from canonical records rather than promote them into governance.

### superseded-candidate

High-priority files in this category include:

- `AIOS_CAPITAL_FLOW_TREASURY_CONTROL_PANEL_V10.md`
- `AIOS_CAPITAL_FLOW_POLICY_SIMULATION_V10.md`
- `AIOS_CAPITAL_FLOW_POLICY_SIMULATION_RANGE_V11.md`
- `AIOS_CAPITAL_FLOW_FUTURE_CONNECTOR_CONTRACT_V10.md`
- `AIOS_CAPITAL_FLOW_FUTURE_CONNECTOR_CONTRACT_V11.md`
- `AIOS_BROKER_DEMO_DATA_ADAPTER_V3.md`
- `AIOS_BROKER_DEMO_DECISION_BRIDGE_V4.md`
- `AIOS_BROKER_DEMO_REVIEW_PACKET_V5.md`
- `AIOS_BROKER_DEMO_REHEARSAL_RUNNER_V6.md`
- `AIOS_BROKER_THRESHOLD_SPRINT_V7_V9.md`
- `AIOS_FOREX_DELIVERY_GOVERNED_APPLY_V2_REPORT.md`
- `AIOS_FOREX_FIRST_LIVE_MICRO_TRADE_EXECUTION_PATH_V2.md`
- `AIOS_FOREX_20_PERCENT_MAINTENANCE_WINDOW_PLAN_V2.md`
- `AIOS_FOREX_80_PERCENT_UPTIME_TRANSITION_LADDER_V2.md`
- `AIOS_FOREX_MITIGATION_ROOT_CAUSE_APPLY_V2.md`

Canonical handling: versioned predecessors need explicit successor links before archive. Do not delete based on filename alone.

### archive-candidate

High-priority files in this category include:

- `AIOS_FOREX_BROKER_CONNECTION_TEST_PACKET_DRAFT_DRY_RUN_V1.md`
- `AIOS_FOREX_HUMAN_OWNER_APPROVAL_PACKAGE_DRAFT_DRY_RUN_V1.md`
- `AIOS_FOREX_HUMAN_OWNER_APPROVAL_PACKAGE_REVIEWABLE_DRAFT_DRY_RUN_V1.md`
- `AIOS_FOREX_PROTECTED_ACTION_APPROVAL_RECORD_TEMPLATE_DRY_RUN_V1.md`
- `AIOS_FOREX_PROTECTED_ACTION_APPROVAL_REVIEW_DRY_RUN_V1.md`
- `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_01_REPORT.md`
- `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_02_DEMO_RUNTIME_READINESS_DRY_RUN_REPORT.md`
- `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_03_DEMO_CONNECTION_PROOF_PREFLIGHT_DRY_RUN_REPORT.md`
- `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_04_DEMO_CONNECTION_PROOF_APPROVAL_REVIEW_DRY_RUN_REPORT.md`
- `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_05_DEMO_CONNECTION_PROOF_REQUEST_DRAFT_DRY_RUN_REPORT.md`
- `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_06_DEMO_CONNECTION_PROOF_PROTECTED_ACTION_GATE_DRY_RUN_REPORT.md`
- `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_07_DEMO_CONNECTION_PROOF_EXECUTION_PACKET_DRAFT_DRY_RUN_REPORT.md`
- `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_08_DEMO_CONNECTION_PROOF_PROTECTED_ACTION_APPROVAL_REVIEW_DRY_RUN_REPORT.md`
- `AIOS_LIVE_MICRO_TRADE_EXCEPTION_PACKET_09_DEMO_CONNECTION_PROOF_PROTECTED_ACTION_APPROVAL_RECORD_DRAFT_DRY_RUN_REPORT.md`

Canonical handling: these are likely useful as history but should not be operator-facing unless linked from a final exception package or audit record.

### broker/OANDA

High-priority files in this category include:

- `AIOS_FOREX_BROKER_SPECIFIC_INTEGRATION_BACKLOG_V1.md`
- `AIOS_FOREX_BROKER_SPECIFIC_PAPER_DEMO_INTEGRATION_V1_REPORT.md`
- `AIOS_FOREX_BROKER_READ_ONLY_SNAPSHOT_CONTRACT_V1.md`
- `AIOS_FOREX_BROKER_POLICY_READINESS_ENGINE_V1_REPORT.md`
- `AIOS_FOREX_BROKER_PAPER_ADAPTER_V1_REPORT.md`
- `AIOS_FOREX_BROKER_DEMO_RUNTIME_REVIEW_V1_REPORT.md`
- `AIOS_FOREX_BROKER_DEMO_CONNECTOR_IMPLEMENTATION_PLAN_V1.md`
- `AIOS_FOREX_BROKER_DEMO_CONNECTOR_APPROVAL_WORKFLOW_V1_REPORT.md`
- `AIOS_FOREX_BROKER_DEMO_ACCOUNT_BOUNDARY_V1_REPORT.md`
- `AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_AUDIT_V1.md`
- `AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_EPIC_REPORT_V1.md`
- `AIOS_FOREX_OANDA_DEMO_BROKER_EXECUTION_PACKET_ONE_ORDER_V1.md`
- `AIOS_FOREX_OANDA_DEMO_BROKER_ADAPTER_ONE_ORDER_FINAL_WIRE_V1.md`
- `AIOS_FOREX_OANDA_DEMO_RUNTIME_EXECUTOR_FINAL_GATED_V1.md`
- `AIOS_FOREX_OANDA_DEMO_RUNTIME_HTTP_TRANSPORT_ONE_ORDER_OWNER_RUN_V1.md`
- `AIOS_OANDA_LIVE_RUNTIME_CONNECTOR_V2.md`
- `AIOS_OANDA_LIVE_HTTP_TRANSPORT_V1_REPORT.md`
- `AIOS_OANDA_DEMO_CONNECTION_GATE_SPEC_V1_REPORT.md`

Canonical handling: separate demo broker evidence from live broker exception artifacts. The shared word `OANDA` should not collapse demo and live scopes.

### profit/P&L

High-priority files in this category include:

- `AIOS_FOREX_PROFIT_PROOF_LEDGER_V1_REPORT.md`
- `AIOS_FOREX_PROFIT_PROOF_LEDGER_V1.md`
- `AIOS_FOREX_PROFIT_VALIDATION_LOOP_V1_REPORT.md`
- `AIOS_FOREX_PROFITABILITY_VERDICT_V1.md`
- `AIOS_FOREX_PROFITABILITY_PROOF_PACKET_M_V1_REPORT.md`
- `AIOS_FOREX_PROFITABILITY_PROOF_AND_BEST_CANDIDATE_DISCOVERY_PACKET_M_V1.md`
- `AIOS_FOREX_OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_V1.md`
- `AIOS_FOREX_OANDA_DEMO_PROFIT_PROOF_GAP_BRIDGE_V1.md`
- `AIOS_FOREX_OANDA_DEMO_OPEN_UNREALIZED_PL_RESULT_BUCKET_V1.md`
- `AIOS_FOREX_OANDA_DEMO_PL_RESULT_QUALITY_GATE_V1.md`
- `AIOS_FOREX_OANDA_DEMO_PL_RESULT_BUCKET_REPEAT_PROOF_LANE_V1_REPORT.md`
- `AIOS_FOREX_REALIZED_PL_RESULT_BUCKET_UPDATE_GATE_V1_REPORT.md`
- `AIOS_FOREX_BALANCE_COMPOUNDING_V1_REPORT.md`
- `AIOS_FOREX_CAPITAL_ALLOCATION_GATE_V1_REPORT.md`
- `AIOS_MONEY_COCKPIT_100K_GOAL_LADDER_V11.md`
- `AIOS_MONEY_COCKPIT_CAPITAL_FLOW_SIM_RANGE_V11.md`
- `AIOS_MONEY_RELEVANCE_DASHBOARD_RULE_V11.md`

Canonical handling: map P&L and profit files into one result ledger with separate simulated, demo, and live result scopes.

### demo execution

High-priority files in this category include:

- `AIOS_DEMO_CONNECTION_PROOF_SUCCESS_RECORD_V1.md`
- `AIOS_FIRST_DEMO_CONNECTION_PROOF_APPLY_V1_REPORT.md`
- `AIOS_FIRST_DEMO_CONNECTION_PROOF_CONFIRMED_EXTERNAL_RUNTIME_V1_REPORT.md`
- `AIOS_FOREX_DEMO_VALIDATION_ORCHESTRATOR_V1_REPORT.md`
- `AIOS_FOREX_DEMO_VALIDATION_SUPERVISOR_V1_REPORT.md`
- `AIOS_FOREX_DEMO_REHEARSAL_RUNNER_V1_REPORT.md`
- `AIOS_FOREX_DEMO_REHEARSAL_EVIDENCE_BUNDLE_V1_REPORT.md`
- `AIOS_FOREX_DEMO_ORDER_PLAN_BUILDER_V1.md`
- `AIOS_FOREX_DEMO_ORDER_MAPPING_V1_REPORT.md`
- `AIOS_FOREX_OANDA_DEMO_FIRST_TRADE_RUNBOOK_AND_OWNER_GO_NOGO_V1.md`
- `AIOS_FOREX_OANDA_DEMO_FINAL_OWNER_RUNTIME_RUN_ONE_ORDER_V1.md`
- `AIOS_FOREX_OANDA_DEMO_OWNER_RUN_ACTUAL_ONE_ORDER_COMMAND_V1.md`
- `AIOS_FOREX_OANDA_DEMO_POST_TRADE_EVIDENCE_CAPTURE_OWNER_RUN_V1.md`
- `AIOS_FOREX_PROTECTED_DEMO_MICRO_ORDER_EXECUTION_PACKET_V1.md`
- `AIOS_FOREX_PROTECTED_DEMO_MICRO_ORDER_REVIEW_V1.md`

Canonical handling: keep manual owner-run records separate from reusable demo execution machinery.

### live exception

High-priority files in this category include:

- `AIOS_SINGLE_PROTECTED_LIVE_MICRO_TRADE_EXECUTION_PACKAGE_V1_REPORT.md`
- `AIOS_LIVE_MICRO_TRADE_READINESS_GATE_V1.md`
- `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_APPROVAL_RECORD_V1.md`
- `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_APPROVAL_REVIEW_V1.md`
- `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_EXECUTION_AUTHORIZATION_STATUS_V1.md`
- `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_EXECUTION_PREREQUISITES_V1.md`
- `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_PROTECTED_EXECUTION_PACKET_V1_REPORT.md`
- `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_PROTECTED_EXECUTION_PACKET_V1_SANITIZED_EVIDENCE.md`
- `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_POST_TRADE_RECONCILIATION_V1.md`
- `LIVE_MICRO_TRADE_EXECUTION_EVIDENCE_V1.md`
- `LIVE_MICRO_TRADE_CLOSE_EVIDENCE_V1.md`
- `AIOS_FOREX_FIRST_LIVE_MICRO_TRADE_PROOF_V1_REPORT.md`
- `AIOS_FOREX_FIRST_LIVE_MICRO_TRADE_EXECUTION_PATH_V2.md`
- `AIOS_FOREX_LIVE_CANDIDATE_READINESS_SPINE_V1_REPORT.md`
- `AIOS_FOREX_LIVE_KILL_SWITCH_READINESS_ENGINE_V1_REPORT.md`
- `AIOS_FOREX_LIVE_MULTI_TRADE_EXPANSION_GATE_V1_REPORT.md`

Canonical handling: this is the highest-risk cluster. It should remain approval-gated and should not be merged with demo execution evidence.

### governance

High-priority files in this category include:

- `AIOS_FOREX_GOVERNANCE_CONSOLIDATION_V1_REPORT.md`
- `AIOS_FOREX_GOVERNED_DEMO_ADVANCEMENT_GATE_V1_REPORT.md`
- `AIOS_FOREX_GOVERNED_DEMO_EXECUTION_DECISION_TREE_V1.md`
- `AIOS_FOREX_CAPITAL_ALLOCATION_GATE_V1_REPORT.md`
- `AIOS_FOREX_DEMO_OWNER_APPROVAL_GATE_V1.md`
- `AIOS_FOREX_DEMO_MANUAL_EXECUTION_EXCEPTION_SCOPE_GATE_V1.md`
- `AIOS_FOREX_EXCEPTION_SPECIFIC_PROOF_MATRIX_DRY_RUN_V1.md`
- `AIOS_FOREX_LIVE_MICRO_TRADE_ARMING_GATE_DRY_RUN_V1.md`
- `AIOS_FOREX_RISK_GOVERNOR_V1_REPORT.md`
- `AIOS_FOREX_RISK_BLOCKER_CLOSURE_LIVE_MICRO_GATE_V1.md`
- `AIOS_FOREX_PROTECTED_ACTION_APPROVAL_REVIEW_DRY_RUN_V1.md`
- `AIOS_FOREX_PROTECTED_ACTION_APPROVAL_RECORD_TEMPLATE_DRY_RUN_V1.md`
- `AIOS_FOREX_APPROVAL_RECORD_SPEC_V1.md`
- `AIOS_FOREX_ATTEMPT_RECORD_SPEC_V1.md`
- `AIOS_FOREX_INTENT_RECORD_SPEC_V1.md`
- `AIOS_FOREX_BROKER_READ_ONLY_SNAPSHOT_CONTRACT_V1.md`
- `AIOS_FOREX_OANDA_DEMO_LIVE_EVIDENCE_REQUIREMENT_MATRIX_V1.md`

Canonical handling: separate binding governance from evidence reports. Filename-only classification cannot decide authority; canonical docs must still win.

### dashboard truth

High-priority files in this category include:

- `AIOS_FOREX_DASHBOARD_TRUTH_WIRING_V1_REPORT.md`
- `AIOS_FOREX_OANDA_DEMO_TO_LIVE_PROFIT_READINESS_TRUTH_V1.md`
- `AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_AUDIT_V1.md`
- `AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_EPIC_REPORT_V1.md`
- `AIOS_FOREX_READINESS_STATE_RECALCULATION_V1_REPORT.md`
- `readiness_state_recalculation_v1_report.json`
- `AIOS_RUNTIME_VISIBILITY_CACHED_READ_MODEL_V1_REPORT.md`
- `AIOS_FOREX_JOURNEY_STATUS_CLI_V1_REPORT.md`
- `AIOS_FOREX_OWNER_GONOGO_COMMAND_CENTER_REPORT_V1_REPORT.md`
- `AIOS_MONEY_RELEVANCE_DASHBOARD_RULE_V11.md`

Canonical handling: this category should feed dashboards and operator views, but not become a second governance authority.

## Top 50 Files Needing Canonical Mapping

These files should be mapped first because their names suggest they are current-state, operator-facing, high-risk, duplicated, or cross-category bridge artifacts.

| Rank | File | Labels | Recommended canonical map |
|---:|---|---|---|
| 1 | `AIOS_FOREX_EPC004_22H6D_AUGMENTATION_V1_REPORT.md` | current-state, governance, dashboard truth | EPC004 current augmentation report |
| 2 | `AIOS_FOREX_GOVERNANCE_CONSOLIDATION_V1_REPORT.md` | current-state, governance | Forex governance consolidation index |
| 3 | `AIOS_FOREX_DASHBOARD_TRUTH_WIRING_V1_REPORT.md` | dashboard truth, current-state | Dashboard truth wiring source |
| 4 | `AIOS_FOREX_OANDA_DEMO_TO_LIVE_PROFIT_READINESS_TRUTH_V1.md` | dashboard truth, broker/OANDA, profit/P&L, demo execution, live exception | Demo-to-live readiness truth record |
| 5 | `AIOS_FOREX_READINESS_STATE_RECALCULATION_V1_REPORT.md` | current-state, dashboard truth, evidence-only | Readiness state calculation report |
| 6 | `readiness_state_recalculation_v1_report.json` | dashboard truth, evidence-only | Machine-readable readiness state evidence |
| 7 | `AIOS_RUNTIME_VISIBILITY_CACHED_READ_MODEL_V1_REPORT.md` | dashboard truth, current-state | Runtime visibility cached read model |
| 8 | `AIOS_FOREX_OWNER_GONOGO_COMMAND_CENTER_REPORT_V1_REPORT.md` | current-state, dashboard truth, governance | Owner go/no-go command center |
| 9 | `AIOS_FOREX_JOURNEY_STATUS_CLI_V1_REPORT.md` | current-state, dashboard truth | Journey status CLI source |
| 10 | `AIOS_FOREX_END_TO_END_JOURNEY_V1_REPORT.md` | current-state, governance | End-to-end journey map |
| 11 | `AIOS_FOREX_LIVE_REVIEW_READINESS_CERTIFICATE_V1_REPORT.md` | current-state, live exception, governance | Live readiness certificate |
| 12 | `AIOS_FOREX_LIVE_READINESS_REVIEW_V1_REPORT.md` | current-state, live exception, governance | Live readiness review |
| 13 | `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_EXECUTION_AUTHORIZATION_STATUS_V1.md` | live exception, current-state, governance | One-shot live authorization status |
| 14 | `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_PROTECTED_EXECUTION_PACKET_V1_REPORT.md` | live exception, evidence-only, governance | Protected live execution packet report |
| 15 | `AIOS_LIVE_MICRO_TRADE_ONE_SHOT_PROTECTED_EXECUTION_PACKET_V1_SANITIZED_EVIDENCE.md` | live exception, evidence-only | Sanitized protected execution evidence |
| 16 | `LIVE_MICRO_TRADE_EXECUTION_EVIDENCE_V1.md` | live exception, evidence-only | Live execution evidence |
| 17 | `LIVE_MICRO_TRADE_CLOSE_EVIDENCE_V1.md` | live exception, evidence-only, profit/P&L | Live close evidence |
| 18 | `AIOS_SINGLE_PROTECTED_LIVE_MICRO_TRADE_EXECUTION_PACKAGE_V1_REPORT.md` | live exception, governance | Single protected live micro-trade package |
| 19 | `AIOS_FOREX_FIRST_LIVE_MICRO_TRADE_PROOF_V1_REPORT.md` | live exception, evidence-only | First live micro-trade proof |
| 20 | `AIOS_FOREX_FIRST_LIVE_MICRO_TRADE_EXECUTION_PATH_V2.md` | live exception, superseded-candidate | First live micro-trade execution path |
| 21 | `AIOS_FIRST_LIVE_MICRO_TRADE_REMAINING_GAPS_V1.md` | live exception, current-state | First live micro-trade gap list |
| 22 | `AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CAPTURE_EPIC_REPORT_V1.md` | broker/OANDA, live exception, evidence-only, profit/P&L | OANDA owner-run live result capture |
| 23 | `AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CLASSIFIER_V1.md` | broker/OANDA, live exception, profit/P&L | OANDA live result classifier |
| 24 | `AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_CONTRACT_V1.md` | broker/OANDA, live exception, governance | OANDA live result contract |
| 25 | `AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_INTAKE_V1.md` | broker/OANDA, live exception, evidence-only | OANDA live result intake |
| 26 | `AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_LEDGER_BRIDGE_V1.md` | broker/OANDA, live exception, evidence-only, profit/P&L | OANDA live result ledger bridge |
| 27 | `AIOS_FOREX_OANDA_OWNER_RUN_LIVE_MICROTRADE_RESULT_QUALITY_GATE_V1.md` | broker/OANDA, live exception, governance | OANDA live result quality gate |
| 28 | `AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_FINAL_GATE_V1.md` | broker/OANDA, live exception, governance | Supervised OANDA live final gate |
| 29 | `AIOS_FOREX_OANDA_SUPERVISED_LIVE_MICROTRADE_OWNER_RUNBOOK_V1.md` | broker/OANDA, live exception, governance | Supervised OANDA live owner runbook |
| 30 | `AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_EPIC_REPORT_V1.md` | broker/OANDA, demo execution, dashboard truth | OANDA demo execution truth epic |
| 31 | `AIOS_FOREX_OANDA_DEMO_EXECUTION_TRUTH_AUDIT_V1.md` | broker/OANDA, demo execution, dashboard truth, evidence-only | OANDA demo execution truth audit |
| 32 | `AIOS_FOREX_OANDA_DEMO_TRADE_320_READ_ONLY_PL_REFRESH_V1_REPORT.md` | broker/OANDA, demo execution, profit/P&L, evidence-only | OANDA demo trade 320 P&L refresh |
| 33 | `AIOS_FOREX_OANDA_DEMO_TRADE_320_READ_ONLY_BROKER_TELEMETRY_REPAIR_V1_REPORT.md` | broker/OANDA, demo execution, evidence-only | OANDA demo trade 320 telemetry repair |
| 34 | `AIOS_FOREX_OANDA_DEMO_BROKER_EXECUTION_PACKET_ONE_ORDER_V1.md` | broker/OANDA, demo execution, governance | OANDA demo one-order execution packet |
| 35 | `AIOS_FOREX_OANDA_DEMO_BROKER_ADAPTER_ONE_ORDER_FINAL_WIRE_V1.md` | broker/OANDA, demo execution | OANDA demo one-order adapter wire |
| 36 | `AIOS_FOREX_OANDA_DEMO_RUNTIME_EXECUTOR_FINAL_GATED_V1.md` | broker/OANDA, demo execution, governance | OANDA demo runtime executor gate |
| 37 | `AIOS_FOREX_OANDA_DEMO_RUNTIME_HTTP_TRANSPORT_ONE_ORDER_OWNER_RUN_V1.md` | broker/OANDA, demo execution | OANDA demo HTTP transport owner run |
| 38 | `AIOS_FOREX_OANDA_DEMO_FINAL_OWNER_RUNTIME_RUN_ONE_ORDER_V1.md` | broker/OANDA, demo execution, governance | OANDA demo final owner runtime run |
| 39 | `AIOS_FOREX_OANDA_DEMO_PROFIT_PROOF_LEDGER_BRIDGE_V1.md` | broker/OANDA, demo execution, profit/P&L, evidence-only | OANDA demo profit proof bridge |
| 40 | `AIOS_FOREX_OANDA_DEMO_PL_RESULT_BUCKET_REPEAT_PROOF_LANE_V1_REPORT.md` | broker/OANDA, demo execution, profit/P&L, evidence-only | OANDA demo P&L repeat proof bucket |
| 41 | `AIOS_FOREX_OANDA_DEMO_OPEN_UNREALIZED_PL_RESULT_BUCKET_V1.md` | broker/OANDA, demo execution, profit/P&L | OANDA demo open unrealized P&L bucket |
| 42 | `AIOS_FOREX_REALIZED_PL_RESULT_BUCKET_UPDATE_GATE_V1_REPORT.md` | profit/P&L, governance | Realized P&L bucket update gate |
| 43 | `AIOS_FOREX_PROFIT_PROOF_LEDGER_V1_REPORT.md` | profit/P&L, evidence-only | Profit proof ledger report |
| 44 | `AIOS_FOREX_PROFIT_VALIDATION_LOOP_V1_REPORT.md` | profit/P&L, governance | Profit validation loop |
| 45 | `AIOS_FOREX_PROFITABILITY_VERDICT_V1.md` | profit/P&L, current-state | Profitability verdict |
| 46 | `AIOS_FOREX_TOP_10_PROFIT_CANDIDATES_V1.md` | profit/P&L, current-state | Top profit candidates |
| 47 | `AIOS_FOREX_TOP_CANDIDATE_SCOREBOARD_V1.md` | current-state, profit/P&L | Top candidate scoreboard |
| 48 | `AIOS_FOREX_CANDIDATE_LEADERBOARD_V1.md` | current-state, profit/P&L | Candidate leaderboard |
| 49 | `AIOS_FOREX_CANDIDATE_TO_GATE_BRIDGE_V1_REPORT.md` | governance, current-state | Candidate-to-gate bridge |
| 50 | `AIOS_FOREX_EVIDENCE_LEDGER_V1_REPORT.md` | evidence-only, governance | Evidence ledger |

## Recommended Next Canonical Mapping Pass

1. Create a generated machine index that assigns non-exclusive labels to every file in `Reports/forex_delivery`.
2. Pick one canonical owner-facing current-state report.
3. Pick one canonical live exception package and link all live evidence to it.
4. Pick one canonical OANDA demo execution truth report and link demo broker records to it.
5. Pick one canonical P&L/profit ledger and link simulated, demo, and live result files separately.
6. Mark older version siblings as superseded only after the successor path is confirmed.
7. Archive dry-run packet chains only after their canonical final report is named.

## Stop Condition

This classifier report does not authorize cleanup, archive movement, deletion, renaming, commit, push, PR creation, broker execution, credential handling, or live trading.
