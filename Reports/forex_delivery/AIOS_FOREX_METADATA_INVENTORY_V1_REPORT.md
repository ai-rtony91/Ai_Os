# AIOS Forex Metadata Inventory V1

| Field | Value |
|---|---:|
| Packet ID | AIOS-FOREX-METADATA-INVENTORY-V1 |
| Mode | LOCAL_APPLY report only |
| Branch | main |
| Worktree | C:\Dev\Ai.Os |
| Remote baseline | origin/main 6fa19b73 |
| Remote baseline subject | docs: eliminate AIOS trading authority drift (#1146) |
| Local baseline | HEAD 10ed5808 |
| Local baseline subject | feat: add forex completion review engines |
| Git tags found | 0 |
| Snapshot basis | Point-in-time filesystem and git metadata before this report was created |
| Snapshot stability | Dirty Forex report count changed during inspection; target report did not exist before write |
| Generated cache exclusions | __pycache__ and .pyc |

| Measurement | Definition |
|---|---|
| Forex engine modules | Python files under automation/forex_engine |
| Forex runner scripts | run_*.py files under scripts/forex_delivery |
| Forex runner/support scripts | Python files under scripts/forex_delivery |
| Forex test suites | test_*.py files under tests/forex_engine, tests/forex_delivery, or Forex-named test paths |
| Forex reports | Files under Reports/forex_delivery |
| Largest files | Sorted by bytes, with line counts from local file reads |
| File growth | Current snapshot compared with origin/main and HEAD tree metadata |

| Category | origin/main | HEAD | Snapshot Before This Report | After This Report | Growth vs origin/main Before Report | Growth vs HEAD Before Report |
|---|---:|---:|---:|---:|---:|---:|
| Forex engine modules | 396 | 405 | 417 | 417 | 21 | 12 |
| Forex runner scripts | 125 | 134 | 145 | 145 | 20 | 11 |
| Forex runner/support scripts | 126 | 135 | 146 | 146 | 20 | 11 |
| Forex test suites | 389 | 398 | 410 | 410 | 21 | 12 |
| Forex reports | 526 | 530 | 569 | 570 | 43 | 39 |

| Git Dirty State | Before This Report | After This Report |
|---|---:|---:|
| Modified tracked files | 15 | 15 |
| Untracked files | 74 | 75 |
| Total dirty entries | 89 | 90 |

| Forex Report Extension | Before This Report | After This Report |
|---|---:|---:|
| .json | 3 | 3 |
| .md | 566 | 567 |
| Total | 569 | 570 |

| Rank | Largest Report File | Bytes | Lines |
|---:|---|---:|---:|
| 1 | Reports/forex_delivery/AIOS_FOREX_MASTER_CLOSURE_LONG_RUN_V1_REPORT.md | 76791 | 1299 |
| 2 | Reports/forex_delivery/AIOS_FOREX_PUBLICATION_PR_LANDING_LANE_V1_REPORT.md | 38971 | 682 |
| 3 | Reports/forex_delivery/AIOS_FOREX_REAL_EVIDENCE_INTAKE_V1_REPORT.md | 37103 | 252 |
| 4 | Reports/forex_delivery/AIOS_FOREX_REMAINING_WORK_INVENTORY_V1_REPORT.md | 37067 | 689 |
| 5 | Reports/forex_delivery/AIOS_FOREX_FINAL_CLOSURE_AUDIT_LANE_V1_REPORT.md | 32523 | 393 |
| 6 | Reports/forex_delivery/AIOS_FOREX_DEMO_READINESS_SPINE_V1_REPORT.md | 31384 | 395 |
| 7 | Reports/forex_delivery/AIOS_FOREX_SPRINT2B_CURRENT_MAIN_IMPLEMENTATION_QUEUE_V1_REPORT.md | 30902 | 843 |
| 8 | Reports/forex_delivery/AIOS_FOREX_TECHNICAL_DEBT_AUDIT_V1_REPORT.md | 28445 | 520 |
| 9 | Reports/forex_delivery/AIOS_FOREX_PRESERVATION_PR_HYGIENE_LANE_V1_REPORT.md | 28322 | 447 |
| 10 | Reports/forex_delivery/AIOS_FOREX_SPRINT2B_DASHBOARD_TRUTH_SPEC_V1_REPORT.md | 28074 | 755 |

| Rank | Largest Engine Module | Bytes | Lines |
|---:|---|---:|---:|
| 1 | automation/forex_engine/broker_paper_sandbox_readiness.py | 71672 | 1570 |
| 2 | automation/forex_engine/post_trade_ledger_replay_closeout_v1.py | 70530 | 1358 |
| 3 | automation/forex_engine/oanda_demo_protected_connection_attempt.py | 60790 | 1411 |
| 4 | automation/forex_engine/profit_proof_ledger_v1.py | 60661 | 1510 |
| 5 | automation/forex_engine/consolidated_readiness_blocker_closure_v1.py | 54089 | 1157 |
| 6 | automation/forex_engine/expectancy_ticket_gate_closure_v1.py | 52822 | 1240 |
| 7 | automation/forex_engine/profit_autonomy_master_bucket_pack_v1.py | 52531 | 1148 |
| 8 | automation/forex_engine/forex_vacation_mode_final_readiness_decision_v1.py | 52307 | 1293 |
| 9 | automation/forex_engine/oanda_demo_owner_run_sanitized_broker_read_output_generator_v1.py | 51907 | 1393 |
| 10 | automation/forex_engine/month_end_readiness.py | 47622 | 981 |

| Rank | Largest Test Suite | Bytes | Lines |
|---:|---|---:|---:|
| 1 | tests/forex_delivery/test_governed_readiness.py | 91703 | 2069 |
| 2 | tests/orchestration/test_aios_forex_builder_roadmap.py | 43282 | 750 |
| 3 | tests/forex_engine/test_broker_paper_sandbox_readiness.py | 34613 | 772 |
| 4 | tests/forex_engine/test_consolidated_readiness_blocker_closure_v1.py | 30260 | 731 |
| 5 | tests/forex_engine/test_protected_broker_demo_runtime_plan.py | 27990 | 712 |
| 6 | tests/forex_engine/test_oanda_demo_owner_run_sanitized_broker_read_output_generator_v1.py | 27648 | 764 |
| 7 | tests/forex_engine/test_oanda_live_microtrade_selected_proof_packet_preview_catalog_v1.py | 26999 | 783 |
| 8 | tests/forex_engine/test_oanda_live_microtrade_profit_proof_evidence_depth_plan_v1.py | 25569 | 760 |
| 9 | tests/forex_engine/test_oanda_live_microtrade_profit_proof_candidate_review_v1.py | 24773 | 730 |
| 10 | tests/forex_engine/test_oanda_live_microtrade_profit_proof_evidence_depth_collection_v1.py | 24669 | 723 |

| Rank | Forex-Associated Directory | Files Before This Report | Files After This Report |
|---:|---|---:|---:|
| 1 | Reports/forex_delivery | 569 | 570 |
| 2 | automation/forex_engine | 415 | 415 |
| 3 | tests/forex_engine | 382 | 382 |
| 4 | scripts/forex_delivery | 146 | 146 |
| 5 | apps/trading_lab/trading_lab | 12 | 12 |
| 6 | tests/trading_lab | 12 | 12 |
| 7 | services/orchestrator | 10 | 10 |
| 8 | tests/forex_delivery | 9 | 9 |
| 9 | tests/orchestration | 7 | 7 |
| 10 | automation/forex_engine/fixtures | 6 | 6 |
| 11 | automation/orchestration/night_supervisor | 4 | 4 |
| 12 | automation/orchestration | 3 | 3 |
| 13 | automation/forex_engine/strategies | 2 | 2 |
| 14 | automation/orchestration/self_development | 2 | 2 |
| 15 | automation/forex_engine/runtime | 1 | 1 |

| Rank | Dirty Directory | Dirty Files Before This Report | Dirty Files After This Report |
|---:|---|---:|---:|
| 1 | Reports/forex_delivery | 42 | 43 |
| 2 | tests/forex_engine | 17 | 17 |
| 3 | automation/forex_engine | 15 | 15 |
| 4 | scripts/forex_delivery | 11 | 11 |
| 5 | tests/forex_delivery | 4 | 4 |
