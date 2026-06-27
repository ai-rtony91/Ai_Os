# AIOS Forex Dependency Audit V1 Report

## Packet Identity

- Mission ID: MISSION-AIOS-FOREX
- Mission Name: AIOS Forex Dependency Audit
- Program ID: PRG-FOREX-001
- Program Name: AIOS Forex Supervised Operational Validation
- Epic ID: EPC-FOREX-DEPENDENCY-MAP-V1
- Epic Name: Forex Dependency Mapping
- Bucket ID: BKT-FOREX-DEPENDENCY-GRAPH
- Bucket Name: Dependency Graph
- Packet ID: AIOS-FOREX-DEPENDENCY-AUDIT-V1
- Packet Name: Forex Dependency Audit V1
- Worker Identity: Codex Dependency Auditor
- Worktree: C:\Dev\Ai.Os
- Observed Branch: main
- Mode: LOCAL_APPLY, report only
- Allowed Write Path: Reports/forex_delivery/AIOS_FOREX_DEPENDENCY_AUDIT_V1_REPORT.md

## Authority And State Readback

Read first:

- AGENTS.md
- README.md
- WHITEPAPER.md
- RISK_POLICY.md
- docs/governance/AI_OS_REPO_MEMORY.md
- docs/governance/aios-identity-and-lane-governance.md
- Reports/forex_delivery/AIOS_FOREX_MASTER_CONVERGENCE_LONG_RUN_V2_REPORT.md

The requested master convergence report was not present at repo root. It was resolved from the current worktree as `Reports/forex_delivery/AIOS_FOREX_MASTER_CONVERGENCE_LONG_RUN_V2_REPORT.md`.

Observed repo state before this report:

- Path: C:\Dev\Ai.Os
- Branch: main
- Remote: origin -> https://github.com/ai-rtony91/Ai_Os.git
- Git state: `## main...origin/main [ahead 1]`
- Dirty state: existing same-mission Forex tracked and untracked work is present.
- Dirty state classification: overlapping Forex implementation and report work, not unrelated noise.
- Protected actions performed: none.

## Scope And Method

This audit did not execute Forex business logic, connect to a broker, read credentials, place orders, start schedulers, start daemons, call webhooks, stage files, commit, push, create a PR, merge, stash, reset, clean, or edit code.

Dependency extraction method:

- Python AST parse of `automation/forex_engine/**/*.py`, `scripts/forex_delivery/*.py`, `tests/forex_engine/*.py`, and `tests/forex_delivery/*.py`.
- Internal dependency edges counted only when imports resolve to `automation.forex_engine`.
- Report references counted by explicit module path, dotted module name, script path, or conservative module stem reference in `Reports/forex_delivery`.
- Report-reference edges are evidence links, not runtime imports.
- No Python modules were imported for this audit; files were parsed as text/AST.

## Inventory Summary

| Artifact class | Count |
| --- | ---: |
| Engine Python files, including `run_*.py` and `__init__.py` | 417 |
| Non-run engine modules | 376 |
| Engine-local `run_*.py` demo runners | 40 |
| Delivery runners in `scripts/forex_delivery` | 146 |
| Total runner files audited | 186 |
| Forex tests | 391 |
| Forex reports and JSON evidence files | 561 |

| Edge class | Count |
| --- | ---: |
| Module -> module import edges | 514 |
| Runner -> module import edges | 244 |
| Test -> module import edges | 744 |
| Report -> module reference edges | 1445 |
| Report -> runner reference edges | 381 |

Parser and import integrity:

- Python parse errors: 0.
- Missing internal module imports from modules: 0.
- Missing internal module imports from runners: 0.
- Missing internal module imports from tests: 0.

## Dependency Graph Summary

### Module -> Module Hubs

Top inbound module dependencies from other modules:

| Module | Inbound module imports |
| --- | ---: |
| `automation.forex_engine.schema_contracts` | 36 |
| `automation.forex_engine.models` | 25 |
| `automation.forex_engine.config` | 14 |
| `automation.forex_engine.oanda_owner_run_live_microtrade_result_contract_v1` | 7 |
| `automation.forex_engine.oanda_demo_sanitized_owner_run_read_only_telemetry_adapter_v1` | 7 |
| `automation.forex_engine.oanda_demo_read_only_pl_result_intake_v1` | 7 |
| `automation.forex_engine.market_data` | 7 |
| `automation.forex_engine.oanda_live_runtime_connector_v2` | 6 |
| `automation.forex_engine.paper_forward_runner` | 5 |
| `automation.forex_engine.local_fixture_catalog` | 5 |
| `automation.forex_engine.forex_trust_safety_audit_v1` | 5 |
| `automation.forex_engine.final_live_operator_bridge_v1` | 5 |

Top outbound module dependencies:

| Module | Outbound module imports |
| --- | ---: |
| `automation.forex_engine.paper_forward_evidence_v2` | 15 |
| `automation.forex_engine.final_evidence_bundle_v1` | 12 |
| `automation.forex_engine.backtest` | 11 |
| `automation.forex_engine.long_run_paper_supervisor` | 9 |
| `automation.forex_engine.forex_closure_integration_bridge_v1` | 9 |
| `automation.forex_engine.post_trade_ledger_replay_closeout_v1` | 8 |
| `automation.forex_engine.evidence_bundle_runner` | 8 |
| `automation.forex_engine.demo_trade_readiness_bridge_v1` | 8 |
| `automation.forex_engine.demo_rehearsal_evidence_bundle` | 8 |
| `automation.forex_engine.broker_paper_sandbox_readiness` | 8 |

### Current Closure And Evidence Spine

| Source module | Direct module dependencies |
| --- | --- |
| `automation.forex_engine.forex_closure_integration_bridge_v1` | `broker_health_readonly_v1`, `candidate_scoring_v1`, `dashboard_truth_summary_v1`, `persistent_profitability_evidence_v1`, `profitability_evidence_v1`, `risk_budget_engine_v1`, `stop_pause_resume_engine_v1`, `supervised_compounding_policy_v1`, `supervised_demo_intent_card_v1` |
| `automation.forex_engine.final_evidence_bundle_v1` | `evidence_milestone_selector_v1`, `final_closure_evidence_v1`, `forex_final_readiness_checker_v1`, `forex_owner_decision_brief_v1`, `observation_evidence_intake_v1`, `persistent_profitability_evidence_v1`, `profitability_evidence_intake_v1`, `replay_evidence_intake_v1`, `replay_proof_evidence_v1`, `supervised_observation_22h6d_evidence_v1`, `walk_forward_evidence_intake_v1`, `walk_forward_oos_evidence_v1` |
| `automation.forex_engine.final_closure_evidence_v1` | none |
| `automation.forex_engine.forex_final_readiness_checker_v1` | none |
| `automation.forex_engine.forex_owner_decision_brief_v1` | none |
| `automation.forex_engine.readiness_state_recalculation_v1` | `proof_bundle_to_candidate_bridge`, `review_chain_end_to_end_candidate_journey` |

Interpretation:

- `forex_closure_integration_bridge_v1` is the local closure-chain integration hub.
- `final_evidence_bundle_v1` is the final evidence aggregation hub.
- `forex_final_readiness_checker_v1`, `forex_owner_decision_brief_v1`, and `final_closure_evidence_v1` are intentionally leaf-style evaluators; callers inject inputs instead of those modules importing the chain.
- That input-injection pattern is safe, but it should be documented as the final-readiness contract before cleanup.

### Runner -> Module Graph

Critical delivery runner dependencies:

| Runner | Direct module dependencies |
| --- | --- |
| `scripts/forex_delivery/run_forex_closure_integration_bridge_v1.py` | `automation.forex_engine.forex_closure_integration_bridge_v1` |
| `scripts/forex_delivery/run_forex_final_readiness_checker_v1.py` | `automation.forex_engine.forex_closure_integration_bridge_v1`, `automation.forex_engine.forex_final_readiness_checker_v1` |
| `scripts/forex_delivery/run_forex_owner_decision_brief_v1.py` | `automation.forex_engine.forex_closure_integration_bridge_v1`, `automation.forex_engine.forex_final_readiness_checker_v1`, `automation.forex_engine.forex_owner_decision_brief_v1` |
| `scripts/forex_delivery/run_final_evidence_bundle_v1.py` | `automation.forex_engine.final_evidence_bundle_v1` |
| `scripts/forex_delivery/run_final_closure_evidence_v1.py` | `automation.forex_engine.final_closure_evidence_v1` |
| `scripts/forex_delivery/run_persistent_profitability_evidence_v1.py` | `automation.forex_engine.persistent_profitability_evidence_v1` |
| `scripts/forex_delivery/run_supervised_observation_22h6d_evidence_v1.py` | `automation.forex_engine.supervised_observation_22h6d_evidence_v1` |
| `scripts/forex_delivery/run_walk_forward_evidence_intake_v1.py` | `automation.forex_engine.walk_forward_evidence_intake_v1` |
| `scripts/forex_delivery/run_walk_forward_oos_evidence_v1.py` | `automation.forex_engine.walk_forward_oos_evidence_v1` |

Top runner outbound dependency counts:

| Runner | Outbound module imports |
| --- | ---: |
| `automation/forex_engine/run_paper_operator_demo.py` | 7 |
| `automation/forex_engine/run_paper_demo.py` | 7 |
| `automation/forex_engine/run_parameter_optimization_demo.py` | 6 |
| `automation/forex_engine/run_paper_learning_action_router_demo.py` | 6 |
| `automation/forex_engine/run_strategy_comparison_demo.py` | 5 |
| `automation/forex_engine/run_paper_study_journal_demo.py` | 5 |
| `automation/forex_engine/run_confidence_demo.py` | 5 |
| `scripts/forex_delivery/run_stop_pause_resume_engine_v1.py` | 4 |
| `automation/forex_engine/run_walk_forward_demo.py` | 4 |
| `automation/forex_engine/run_paper_continuity_review_demo.py` | 4 |

### Test -> Module Graph

Critical test dependencies:

| Test | Direct module dependencies |
| --- | --- |
| `tests/forex_engine/test_forex_closure_integration_bridge_v1.py` | `automation.forex_engine.forex_closure_integration_bridge_v1` |
| `tests/forex_engine/test_forex_final_readiness_checker_v1.py` | `automation.forex_engine.forex_closure_integration_bridge_v1`, `automation.forex_engine.forex_final_readiness_checker_v1` |
| `tests/forex_engine/test_forex_owner_decision_brief_v1.py` | `broker_health_readonly_v1`, `demo_owner_approval_phrase_gate_v1`, `demo_trade_readiness_bridge_v1`, `final_closure_evidence_v1`, `final_evidence_bundle_v1`, `forex_closure_integration_bridge_v1`, `forex_final_readiness_checker_v1`, `forex_owner_decision_brief_v1`, `risk_budget_engine_v1`, `stop_pause_resume_engine_v1`, `supervised_demo_intent_card_v1` |
| `tests/forex_engine/test_final_evidence_bundle_v1.py` | `evidence_milestone_selector_v1`, `final_closure_evidence_v1`, `final_evidence_bundle_v1`, `persistent_profitability_evidence_v1`, `replay_proof_evidence_v1`, `supervised_observation_22h6d_evidence_v1`, `walk_forward_oos_evidence_v1` |
| `tests/forex_engine/test_final_closure_evidence_v1.py` | `automation.forex_engine.final_closure_evidence_v1` |
| `tests/forex_engine/test_readiness_state_recalculation_v1.py` | `automation.forex_engine.readiness_state_recalculation_v1` |

Top test inbound module coverage:

| Module | Test import count |
| --- | ---: |
| `automation.forex_engine.models` | 19 |
| `automation.forex_engine.config` | 15 |
| `automation.forex_engine.local_fixture_catalog` | 8 |
| `automation.forex_engine.schema_contracts` | 7 |
| `automation.forex_engine.oanda_owner_run_live_microtrade_result_contract_v1` | 7 |
| `automation.forex_engine.oanda_vacation_profit_readiness_contract_v1` | 6 |
| `automation.forex_engine.oanda_supervised_live_microtrade_final_gate_v1` | 6 |
| `automation.forex_engine.oanda_live_runtime_connector_v2` | 6 |
| `automation.forex_engine.market_data` | 6 |
| `automation.forex_engine.backtest_harness` | 6 |
| `automation.forex_engine.paper_signal_intake` | 5 |
| `automation.forex_engine.paper_forward_evidence_v2` | 5 |
| `automation.forex_engine.forex_closure_integration_bridge_v1` | 5 |

### Report -> Module Graph

Report references are evidence and documentation links, not executable imports.

Top report inbound module references:

| Module | Report reference count |
| --- | ---: |
| `automation.forex_engine.walk_forward` | 36 |
| `automation.forex_engine.paper_long_run_supervisor` | 26 |
| `automation.forex_engine.oanda_demo_protected_connection_attempt` | 23 |
| `automation.forex_engine.profitability_evidence_v1` | 22 |
| `automation.forex_engine.oanda_demo_connection_probe` | 18 |
| `automation.forex_engine.broker_health_readonly_v1` | 18 |
| `automation.forex_engine.supervised_demo_intent_card_v1` | 17 |
| `automation.forex_engine.forex_owner_decision_brief_v1` | 17 |
| `automation.forex_engine.final_evidence_bundle_v1` | 17 |
| `automation.forex_engine.oanda_demo_connection_gate` | 16 |
| `automation.forex_engine.forex_final_readiness_checker_v1` | 16 |
| `automation.forex_engine.demo_validation_contract` | 16 |
| `automation.forex_engine.risk_governor` | 15 |
| `automation.forex_engine.profit_milestone_100_120_tracker_v1` | 15 |
| `automation.forex_engine.forex_closure_integration_bridge_v1` | 15 |

Report traceability findings:

- Reports with module references: 342.
- Reports with no module or runner reference found: 214.
- Report-to-runner reference edges: 381.
- The 214 report artifacts without explicit module or runner references are not automatically bad; many are plans, sanitized evidence records, or governance/status records. They are, however, weak for dependency cleanup because a future worker cannot easily tell which implementation artifact they validate.

Examples of report artifacts without explicit module or runner references:

- `Reports/forex_delivery/AIOS_CANONICAL_TRADING_IDENTITY_DOCTRINE_V1_REPORT.md`
- `Reports/forex_delivery/AIOS_CAPITAL_FLOW_POLICY_SIMULATION_V10.md`
- `Reports/forex_delivery/AIOS_DEMO_CONNECTION_PROOF_SUCCESS_RECORD_V1.md`
- `Reports/forex_delivery/AIOS_FIRST_LIVE_MICRO_TRADE_REMAINING_GAPS_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_100_PERCENT_REPEATABILITY_TARGET_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_BROKER_BRIDGE_COMPLETION_REPORT_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_BROKER_DEMO_CONNECTOR_IMPLEMENTATION_PLAN_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_BROKER_DEMO_INTERFACE_CONTRACT_PLAN_V1.md`
- `Reports/forex_delivery/AIOS_FOREX_BROKER_DEMO_READ_ONLY_PROBE_PLAN_V1.md`

## Orphan Modules

Hard orphan definition: non-run engine module with no inbound module import, no runner import, no test import or conventional test file, and no report reference.

Result:

- Hard orphan modules found: 0.

No-code-inbound definition: non-run engine module with no inbound imports from other modules or runners, but still referenced by tests and/or reports. These are cleanup candidates, not deletion candidates.

No-code-inbound modules found: 66.

Representative examples:

- `automation.forex_engine.broker_demo_account_boundary`
- `automation.forex_engine.broker_demo_connector_approval_workflow`
- `automation.forex_engine.broker_demo_connector_dry_run`
- `automation.forex_engine.broker_demo_credential_boundary`
- `automation.forex_engine.broker_demo_data_adapter_v3`
- `automation.forex_engine.broker_demo_decision_bridge_v4`
- `automation.forex_engine.broker_demo_dry_run_orchestrator`
- `automation.forex_engine.broker_demo_runtime_connector_skeleton`
- `automation.forex_engine.broker_policy_readiness_engine`
- `automation.forex_engine.campaign_evidence_accumulator`
- `automation.forex_engine.capital_allocation_gate`
- `automation.forex_engine.capital_flow_policy_v1`
- `automation.forex_engine.demo_multi_trade_runner`
- `automation.forex_engine.demo_validation_supervisor`
- `automation.forex_engine.evidence_cache_registry_v1`
- `automation.forex_engine.final_demo_readiness_validator_i_v1`
- `automation.forex_engine.live_kill_switch_readiness_engine`
- `automation.forex_engine.live_readiness_review`
- `automation.forex_engine.long_run_paper_supervisor`
- `automation.forex_engine.oanda_demo_runtime_executor_one_order_only_v1`
- `automation.forex_engine.paper_long_run_supervisor`
- `automation.forex_engine.readiness_state_recalculation_v1`
- `automation.forex_engine.self_improvement_review`
- `automation.forex_engine.strategy_campaign_supervisor`

Interpretation:

- The no-code-inbound group is mostly standalone gates, adapters, validators, reports-as-code, demo/live review packets, and candidate evidence processors.
- Do not delete these just because they have no code inbound edge.
- Cleanup should classify each as one of: canonical leaf evaluator, CLI-only command target, report-only historical artifact, superseded duplicate, or archive candidate.

## Duplicate Logic

Exact duplicate module files:

- None found by file hash in non-run engine modules.

Repeated logic families found by shared public function/class names:

| Family | Modules | Shared logic pattern |
| --- | --- | --- |
| Forex review gates | `forex_evidence_depth_quality_gate_v1`, `forex_sos_owner_alert_bridge_v1`, `forex_statistical_profit_proof_gate_v1`, `forex_supervised_compounding_policy_gate_v1`, `forex_vacation_mode_final_readiness_decision_v1`, `forex_vacation_mode_readiness_orchestrator_v1` | `_SchemaState`, `build_sample_ready_input`, `build_sample_partial_input`, `build_sample_schema_invalid_input`, `build_sample_unsafe_input`, `markdown_safety_lines`, `protected_flags_false`, `to_jsonable_dict`, `to_markdown`, `to_operator_text` |
| OANDA vacation profit gates | `oanda_vacation_profit_autonomy_control_gate_v1`, `oanda_vacation_profit_compounding_permission_gate_v1`, `oanda_vacation_profit_live_sample_gate_v1`, `oanda_vacation_profit_readiness_epic_v1`, `oanda_vacation_profit_trial_plan_v1` | repeated readiness samples, unsafe samples, JSON/markdown/operator renderers |
| Live microtrade result chain | `oanda_owner_run_live_microtrade_result_capture_epic_v1`, `oanda_owner_run_live_microtrade_result_classifier_v1`, `oanda_owner_run_live_microtrade_result_intake_v1`, `oanda_owner_run_live_microtrade_result_ledger_bridge_v1`, `oanda_owner_run_live_microtrade_result_quality_gate_v1` | repeated breakeven/loss/profit/missing/unsafe sample builders and renderers |

Interpretation:

- This is not currently broken behavior.
- It is duplication by template drift: many safety-gated modules repeat the same protected-permission, sample-input, serializer, markdown, and operator-text helpers.
- The safest eventual fix is a small shared read-only renderer/schema helper after publication and after targeted tests are locked. Do not centralize broker or execution behavior.

## Unused Or Unreferenced Runners

Definition used: runner files with no test reference and no report reference by exact path or runner stem. This does not prove the runner is unused; it proves the repo currently lacks traceable evidence that another artifact references it.

Unreferenced runner candidates found: 45.

Delivery runner candidates:

- `scripts/forex_delivery/run_auto_exit_live_readiness.py`
- `scripts/forex_delivery/run_live_readiness_consolidated_blocker_burndown.py`
- `scripts/forex_delivery/run_read_only_evidence_approval.py`
- `scripts/forex_delivery/run_read_only_live_data_bridge.py`
- `scripts/forex_delivery/run_trading_history_writeback_verification.py`

Engine-local demo runner candidates:

- `automation/forex_engine/run_backtest_demo.py`
- `automation/forex_engine/run_broker_paper_adapter_plan_approval_gate_demo.py`
- `automation/forex_engine/run_broker_paper_adapter_stub_contract_demo.py`
- `automation/forex_engine/run_broker_paper_dryrun_intent_ledger_demo.py`
- `automation/forex_engine/run_broker_paper_dryrun_replay_evidence_gate_demo.py`
- `automation/forex_engine/run_broker_paper_dryrun_replay_harness_demo.py`
- `automation/forex_engine/run_broker_paper_dryrun_risk_governor_demo.py`
- `automation/forex_engine/run_broker_paper_presecurity_gate_demo.py`
- `automation/forex_engine/run_broker_paper_sandbox_readiness_demo.py`
- `automation/forex_engine/run_broker_sandbox_demo.py`
- `automation/forex_engine/run_confidence_demo.py`
- `automation/forex_engine/run_daily_edge_report.py`
- `automation/forex_engine/run_evidence_bundle_demo.py`
- `automation/forex_engine/run_historical_data_readiness_demo.py`
- `automation/forex_engine/run_low_vol_edge_redesign_demo.py`
- `automation/forex_engine/run_market_data_demo.py`
- `automation/forex_engine/run_month_end_readiness_demo.py`
- `automation/forex_engine/run_oos_expansion_demo.py`
- `automation/forex_engine/run_oos_repair_demo.py`
- `automation/forex_engine/run_paper_continuity_review_demo.py`
- `automation/forex_engine/run_paper_demo.py`
- `automation/forex_engine/run_paper_forward_demo.py`
- `automation/forex_engine/run_paper_forward_evidence_v2_demo.py`
- `automation/forex_engine/run_paper_learning_action_router_demo.py`
- `automation/forex_engine/run_paper_operator_demo.py`
- `automation/forex_engine/run_paper_risk_decision_demo.py`
- `automation/forex_engine/run_paper_signal_intake_demo.py`
- `automation/forex_engine/run_paper_study_journal_demo.py`
- `automation/forex_engine/run_parameter_optimization_demo.py`
- `automation/forex_engine/run_portfolio_optimization_demo.py`
- `automation/forex_engine/run_readiness_demo.py`
- `automation/forex_engine/run_risk_governor_demo.py`
- `automation/forex_engine/run_risk_management_demo.py`
- `automation/forex_engine/run_signal_rules_demo.py`
- `automation/forex_engine/run_strategy_comparison_demo.py`
- `automation/forex_engine/run_stress_and_oos_demo.py`
- `automation/forex_engine/run_stress_repair_demo.py`
- `automation/forex_engine/run_supertrend_edge_demo.py`
- `automation/forex_engine/run_supertrend_walk_forward_demo.py`
- `automation/forex_engine/run_walk_forward_demo.py`

Interpretation:

- Engine-local demo runners are the safest runner cleanup candidates after publication because they are not the current delivery command surface.
- Delivery runners with live/read-only names should not be removed without a safety-specific review because they may be operator-facing protected-action evidence lanes.

## Untested Modules

Definition used: no test imports and no conventional `test_<module>.py` filename.

Untested non-run modules found:

- `automation.forex_engine.demo_validation_scorecard`
- `automation.forex_engine.journal`

Interpretation:

- Test coverage is broad for the current Forex surface.
- These two modules should be handled before any cleanup deletes or consolidates adjacent functionality.

## Circular Dependencies

Detected module cycles:

1. `broker_paper_sandbox_readiness` -> `paper_forward_evidence_v2` -> `broker_paper_sandbox_readiness`
2. `broker_paper_sandbox_readiness` -> `paper_forward_evidence_v2` -> `evidence_bundle_runner` -> `month_end_readiness` -> `broker_paper_sandbox_readiness`
3. `paper_forward_evidence_v2` -> `stress_repair` -> `paper_forward_evidence_v2`
4. `paper_forward_evidence_v2` -> `stress_repair` -> `paper_forward_stress` -> `paper_forward_evidence_v2`
5. `proof_bundle_to_candidate_bridge` -> `replay_reconciliation_proof_bundle` -> `review_chain_end_to_end_candidate_journey` -> `proof_bundle_to_candidate_bridge`

Interpretation:

- The paper-forward cycle group is the most immediate maintainability risk because it ties evidence, stress repair, bundle, readiness, and sandbox readiness together.
- The review-chain cycle group is a final-readiness maintainability risk because candidate bridge, replay reconciliation, and end-to-end journey mutually depend on each other.
- No cleanup should remove modules inside these cycles until a separate APPLY packet breaks the cycles with tests.

## Missing Integration Points

Missing or weak integration points identified:

1. No canonical machine-readable dependency manifest exists for Forex modules, runners, tests, and report references.
2. 66 non-run modules have no code inbound path from modules or runners, so their ownership is not obvious from imports alone.
3. 45 runners lack test/report references, so runner lifecycle status is not clearly recorded.
4. 214 report artifacts do not explicitly reference implementation modules or runners, which weakens future report-to-code traceability.
5. The final readiness and owner decision brief modules intentionally depend on injected inputs rather than importing the closure/evidence chain, but the injection contract is not represented as a dependency manifest.
6. The current same-mission dirty state contains untracked evidence modules, runners, tests, and reports; dependency status is provisional until publication preserves or rejects that work.

No broken internal import integration point was found by AST parse.

## Cleanup Risk Classification

| Cleanup target | Risk | Reason |
| --- | --- | --- |
| Add missing tests for `demo_validation_scorecard` and `journal` | Low to medium | No behavior removal; improves protection before cleanup |
| Add report/module/runner reference metadata to future reports | Low | Documentation-only traceability improvement |
| Classify engine-local demo runners | Low to medium | Mostly local demo entrypoints, but some are still imported by tests |
| Classify delivery runners | Medium to high | Some are operator-facing and safety-sensitive |
| Break paper-forward cycles | Medium | Requires code movement/refactor and regression tests |
| Break review-chain cycles | Medium to high | Touches final-readiness path |
| Deduplicate safety-gate helper templates | Medium | Good cleanup, but must not centralize execution authority or weaken fail-closed behavior |
| Delete or archive Forex modules/reports/runners | High | Requires owner approval, exact file list, validation, and publication state alignment |

## Safest Cleanup Order After Publication

Do not start cleanup until the current dirty Forex work is preserved, rejected, or split through an owner-approved protected-action lane. Cleanup before publication risks deleting or rewriting unpublished evidence.

Recommended order:

1. Publication gate first.
   - Preserve or reject the current dirty Forex modules, runners, tests, and reports.
   - Use exact file lists only.
   - Do not use `git add .`.

2. Coverage guard next.
   - Add or confirm tests for `automation.forex_engine.demo_validation_scorecard`.
   - Add or confirm tests for `automation.forex_engine.journal`.
   - Re-run targeted Forex tests before classifying either module.

3. Create a dependency manifest or index.
   - Capture module, runner, test, and report-reference edges in a generated report or JSON artifact.
   - Keep it evidence-only; do not make it execution authority.

4. Classify no-code-inbound modules.
   - Mark each as canonical leaf evaluator, CLI-only command target, report-only historical artifact, superseded duplicate, or archive candidate.
   - Do not delete during classification.

5. Classify unreferenced runners.
   - Start with engine-local demo runners.
   - Then inspect delivery runners.
   - Treat live, broker, credential, read-only, owner-run, and protected-action runners as safety-sensitive until proven otherwise.

6. Break circular dependencies.
   - First break the `paper_forward_evidence_v2` cycle group.
   - Then break the `proof_bundle_to_candidate_bridge` / `replay_reconciliation_proof_bundle` / `review_chain_end_to_end_candidate_journey` cycle.
   - Use narrow APPLY packets with targeted tests.

7. Deduplicate helper templates.
   - Extract only serialization, protected-permission defaults, sample builders, and markdown/operator rendering where tests prove identical behavior.
   - Do not centralize broker execution, credential handling, live routing, order behavior, approval authority, or risk gates.

8. Report traceability cleanup.
   - Add explicit `Source modules` and `Source runners` sections to future reports.
   - For old reports, prefer an index over mass editing hundreds of files.

9. Removal or archive pass last.
   - Only after tests pass, cycles are broken, runner ownership is classified, and owner approval names exact files.
   - No delete, move, rename, reset, clean, commit, push, PR, or merge without separate approval.

## Recommendation

The Forex implementation is not import-broken and has no hard orphan modules by current graph evidence. The risk is dependency sprawl: many standalone gates, many reports, many runner surfaces, repeated helper templates, and two cycle groups that make cleanup fragile.

The safest cleanup path is publication first, then tests for the two untested modules, then classification, then cycle breaking, then helper deduplication, and only then deletion or archival review.

## Validation Plan

Required packet validators after this report is written:

- `git diff --check -- Reports/forex_delivery/AIOS_FOREX_DEPENDENCY_AUDIT_V1_REPORT.md`
- `Get-Content -LiteralPath Reports/forex_delivery/AIOS_FOREX_DEPENDENCY_AUDIT_V1_REPORT.md -Raw`
- `git status --short --branch`

## Commit And Push Status

- Staged: no.
- Commit: no.
- Push: no.
- PR: no.
- Merge: no.

STATUS: DEPENDENCY AUDIT COMPLETE
