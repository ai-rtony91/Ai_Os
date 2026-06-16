from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_COMPLETED_PACKET_MEMORY_SUPPRESSION.v1"

FOREX_MILESTONE = (
    "AIOS is the factory -> forex is the first proof product -> daily earned repo work "
    "-> gated trade readiness, with no broker/live/secrets until protected gates prove safety"
)

DEFAULT_COMPLETED_PACKETS = [
    {
        "packet_id": "PKT-AIOS-SELFROUTE-CANDIDATE-EVIDENCE-INTEGRATION",
        "title": "Connect candidate packet evidence adapter into self-route",
        "lane": "connect-candidate-evidence-to-selfroute",
        "required_files": [
            "automation/orchestration/runtime/Invoke-AiOsRuntimeSelfRoute.ps1",
            "tests/orchestration/test_aios_persistent_runtime_supervisor.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-PACKET-QUEUE-PLANNER",
        "title": "AIOS packet queue planner",
        "lane": "add-aios-packet-queue-planner",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-RUNTIME-SELFROUTE-PACKET-QUEUE-CONNECTOR",
        "title": "Connect runtime self-route to packet queue planner",
        "lane": "connect-runtime-selfroute-to-packet-queue-planner",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-CYCLE-LEDGER-DASHBOARD-SOS",
        "title": "AIOS cycle ledger dashboard SOS contract",
        "lane": "build-aios-cycle-ledger-dashboard-sos-contract",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-RUNTIME-SELFROUTE-CYCLE-LEDGER-CONNECTOR",
        "title": "Connect runtime self-route to cycle ledger",
        "lane": "connect-runtime-selfroute-to-cycle-ledger",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-CANDIDATE-PACKET-EVIDENCE-ADAPTER",
        "title": "AIOS candidate packet evidence adapter",
        "lane": "build-candidate-packet-evidence-adapter",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-RUNTIME-SELFROUTE-CANDIDATE-EVIDENCE-CONNECTOR",
        "title": "Connect runtime self-route to candidate evidence adapter",
        "lane": "connect-runtime-selfroute-to-candidate-evidence-adapter",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-FIX-CANDIDATE-TO-PLANNER-HANDOFF",
        "title": "Fix candidate planner JSON handoff",
        "lane": "fix-selfroute-candidate-to-planner-handoff",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-APPROVED-PACKET-EXECUTOR-CONTRACT",
        "title": "AIOS approved packet executor contract",
        "lane": "build-approved-packet-executor-contract",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-RUNTIME-SELFROUTE-APPROVED-EXECUTOR-CONNECTOR",
        "title": "Connect runtime self-route to approved executor contract",
        "lane": "connect-runtime-selfroute-to-approved-executor-contract",
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC",
        "title": "feat(trading-lab): add canonical forex builder spec",
        "lane": "forex-builder-spec",
        "landed_pr": "#737",
        "commit": "cd012419",
        "completion_reason": "canonical forex builder spec landed on main",
        "completed_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_SPEC.md",
            "tests/orchestration/test_aios_forex_builder_roadmap.py",
        ],
        "required_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_SPEC.md",
            "tests/orchestration/test_aios_forex_builder_roadmap.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-FOREX-BUILDER-DATA-SCHEMAS",
        "title": "Add local forex builder data schema contracts",
        "lane": "forex-builder-data-schemas",
        "landed_pr": "#742",
        "completion_reason": "local forex builder data schema contracts landed on main",
        "completed_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_DATA_SCHEMAS.md",
            "automation/forex_engine/schema_contracts.py",
            "tests/forex_engine/test_schema_contracts.py",
        ],
        "required_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_DATA_SCHEMAS.md",
            "automation/forex_engine/schema_contracts.py",
            "tests/forex_engine/test_schema_contracts.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-FOREX-BUILDER-BACKTEST-HARNESS",
        "title": "Create forex builder deterministic backtest harness scaffold",
        "lane": "forex-builder-backtest",
        "landed_pr": "#743",
        "completion_reason": "monthly forex factory scaffold landed with local deterministic backtest harness contract, docs, and tests",
        "completed_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_BACKTEST_HARNESS.md",
            "automation/forex_engine/backtest_harness.py",
            "tests/forex_engine/test_backtest_harness.py",
        ],
        "required_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_BACKTEST_HARNESS.md",
            "automation/forex_engine/backtest_harness.py",
            "tests/forex_engine/test_backtest_harness.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-FOREX-BUILDER-RISK-CONTRACT",
        "title": "Define forex builder risk gate contract",
        "lane": "forex-builder-risk-policy",
        "landed_pr": "#743",
        "completion_reason": "monthly forex factory scaffold landed with local forex risk contract, docs, and tests",
        "completed_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_RISK_CONTRACT.md",
            "automation/forex_engine/risk_contract.py",
            "tests/forex_engine/test_risk_contract.py",
        ],
        "required_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_RISK_CONTRACT.md",
            "automation/forex_engine/risk_contract.py",
            "tests/forex_engine/test_risk_contract.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-FOREX-BUILDER-DASHBOARD-CONTRACT",
        "title": "Define forex builder dashboard contract",
        "lane": "forex-builder-dashboard",
        "landed_pr": "#743",
        "completion_reason": "monthly forex factory scaffold landed with compact forex dashboard/report contract, docs, and tests",
        "completed_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_DASHBOARD_CONTRACT.md",
            "automation/forex_engine/forex_dashboard_contract.py",
            "tests/forex_engine/test_forex_dashboard_contract.py",
        ],
        "required_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_DASHBOARD_CONTRACT.md",
            "automation/forex_engine/forex_dashboard_contract.py",
            "tests/forex_engine/test_forex_dashboard_contract.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-FOREX-BUILDER-PAPER-FORWARD-SIMULATOR",
        "title": "Create local paper-forward simulator scaffold",
        "lane": "forex-builder-paper-forward-simulator",
        "landed_pr": "#743",
        "completion_reason": "paper-forward simulator scaffold landed and V1 local runner validates simulated ledger evidence",
        "completed_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_PAPER_FORWARD_SIMULATOR.md",
            "automation/forex_engine/paper_forward_simulator.py",
            "automation/forex_engine/paper_forward_runner.py",
            "automation/forex_engine/run_paper_forward_demo.py",
            "tests/forex_engine/test_paper_forward_simulator.py",
            "tests/forex_engine/test_paper_forward_runner.py",
        ],
        "required_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_PAPER_FORWARD_SIMULATOR.md",
            "automation/forex_engine/paper_forward_simulator.py",
            "automation/forex_engine/paper_forward_runner.py",
            "automation/forex_engine/run_paper_forward_demo.py",
            "tests/forex_engine/test_paper_forward_simulator.py",
            "tests/forex_engine/test_paper_forward_runner.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-FOREX-BUILDER-EVIDENCE-AGGREGATOR",
        "title": "Create forex builder evidence aggregator",
        "lane": "forex-builder-evidence-aggregator",
        "landed_pr": "#743",
        "completion_reason": "evidence aggregator scaffold landed and V1 local evidence bundle runner validates aggregator output",
        "completed_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_EVIDENCE_AGGREGATOR.md",
            "automation/forex_engine/evidence_aggregator.py",
            "automation/forex_engine/evidence_bundle_runner.py",
            "automation/forex_engine/run_evidence_bundle_demo.py",
            "tests/forex_engine/test_evidence_aggregator.py",
            "tests/forex_engine/test_evidence_bundle_runner.py",
        ],
        "required_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_EVIDENCE_AGGREGATOR.md",
            "automation/forex_engine/evidence_aggregator.py",
            "automation/forex_engine/evidence_bundle_runner.py",
            "automation/forex_engine/run_evidence_bundle_demo.py",
            "tests/forex_engine/test_evidence_aggregator.py",
            "tests/forex_engine/test_evidence_bundle_runner.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-FOREX-BUILDER-MONTH-END-READINESS",
        "title": "Create forex builder month-end readiness review",
        "lane": "forex-builder-month-end-readiness",
        "landed_pr": "#743",
        "completion_reason": "month-end readiness scaffold landed and V1 local readiness demo validates summary output",
        "completed_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_MONTH_END_READINESS.md",
            "automation/forex_engine/month_end_readiness.py",
            "automation/forex_engine/run_month_end_readiness_demo.py",
            "tests/forex_engine/test_month_end_readiness.py",
        ],
        "required_files": [
            "docs/trading_lab/AIOS_FOREX_BUILDER_MONTH_END_READINESS.md",
            "automation/forex_engine/month_end_readiness.py",
            "automation/forex_engine/run_month_end_readiness_demo.py",
            "tests/forex_engine/test_month_end_readiness.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-APPROVED-EXECUTOR-LOOP-LITE",
        "title": "Document approved executor loop lite",
        "lane": "approved-executor-loop-lite",
        "landed_pr": "#743",
        "completion_reason": "approved executor loop-lite doc landed with monthly forex factory scaffolds",
        "completed_files": [
            "docs/orchestration/AIOS_APPROVED_EXECUTOR_LOOP_LITE.md",
            "tests/orchestration/test_aios_operator_checkpoint_dashboard.py",
        ],
        "required_files": [
            "docs/orchestration/AIOS_APPROVED_EXECUTOR_LOOP_LITE.md",
            "tests/orchestration/test_aios_operator_checkpoint_dashboard.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-DAILY-CONTRIBUTION-LOOP-LITE",
        "title": "Document daily earned contribution loop lite",
        "lane": "daily-contribution-loop-lite",
        "landed_pr": "#743",
        "completion_reason": "daily contribution loop-lite doc landed with monthly forex factory scaffolds",
        "completed_files": [
            "docs/orchestration/AIOS_DAILY_CONTRIBUTION_LOOP_LITE.md",
            "tests/orchestration/test_aios_operator_checkpoint_dashboard.py",
        ],
        "required_files": [
            "docs/orchestration/AIOS_DAILY_CONTRIBUTION_LOOP_LITE.md",
            "tests/orchestration/test_aios_operator_checkpoint_dashboard.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-PAPER-FORWARD-EVIDENCE-EXPANSION-V1",
        "title": "Add paper-forward evidence expansion",
        "lane": "paper-forward-evidence-expansion",
        "landed_pr": "#744",
        "completion_reason": "local fixture catalog, paper-forward runner, evidence bundle runner, readiness demos, and V1 evidence routing landed on main",
        "completed_files": [
            "automation/forex_engine/local_fixture_catalog.py",
            "automation/forex_engine/paper_forward_runner.py",
            "automation/forex_engine/evidence_bundle_runner.py",
            "automation/forex_engine/run_paper_forward_demo.py",
            "automation/forex_engine/run_evidence_bundle_demo.py",
            "automation/forex_engine/run_month_end_readiness_demo.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_PAPER_FORWARD_EVIDENCE.md",
            "docs/trading_lab/AIOS_FOREX_BUILDER_LOCAL_FIXTURE_CATALOG.md",
            "docs/trading_lab/AIOS_FOREX_BUILDER_READINESS_DEMO_COMMANDS.md",
            "tests/forex_engine/test_local_fixture_catalog.py",
            "tests/forex_engine/test_paper_forward_runner.py",
            "tests/forex_engine/test_evidence_bundle_runner.py",
        ],
        "required_files": [
            "automation/forex_engine/local_fixture_catalog.py",
            "automation/forex_engine/paper_forward_runner.py",
            "automation/forex_engine/evidence_bundle_runner.py",
            "automation/forex_engine/run_paper_forward_demo.py",
            "automation/forex_engine/run_evidence_bundle_demo.py",
            "automation/forex_engine/run_month_end_readiness_demo.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_PAPER_FORWARD_EVIDENCE.md",
            "docs/trading_lab/AIOS_FOREX_BUILDER_LOCAL_FIXTURE_CATALOG.md",
            "docs/trading_lab/AIOS_FOREX_BUILDER_READINESS_DEMO_COMMANDS.md",
            "tests/forex_engine/test_local_fixture_catalog.py",
            "tests/forex_engine/test_paper_forward_runner.py",
            "tests/forex_engine/test_evidence_bundle_runner.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-PAPER-FORWARD-EVIDENCE-EXPANSION-V2",
        "title": "Add paper-forward evidence V2",
        "lane": "paper-forward-evidence-expansion-v2",
        "landed_pr": "#745",
        "completion_reason": "paper-forward evidence V2 landed with multi-fixture evidence, regime consistency, V2 demo, readiness/dashboard integration, and safe next selector",
        "completed_files": [
            "automation/forex_engine/local_fixture_catalog.py",
            "automation/forex_engine/paper_forward_runner.py",
            "automation/forex_engine/paper_forward_evidence_v2.py",
            "automation/forex_engine/run_paper_forward_evidence_v2_demo.py",
            "automation/forex_engine/month_end_readiness.py",
            "automation/forex_engine/forex_dashboard_contract.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_PAPER_FORWARD_EVIDENCE_V2.md",
            "docs/trading_lab/AIOS_FOREX_BUILDER_READINESS_DEMO_COMMANDS.md",
            "tests/forex_engine/test_paper_forward_evidence_v2.py",
            "tests/forex_engine/test_local_fixture_catalog.py",
            "tests/forex_engine/test_paper_forward_runner.py",
            "tests/forex_engine/test_month_end_readiness.py",
            "tests/forex_engine/test_forex_dashboard_contract.py",
        ],
        "required_files": [
            "automation/forex_engine/local_fixture_catalog.py",
            "automation/forex_engine/paper_forward_runner.py",
            "automation/forex_engine/paper_forward_evidence_v2.py",
            "automation/forex_engine/run_paper_forward_evidence_v2_demo.py",
            "automation/forex_engine/month_end_readiness.py",
            "automation/forex_engine/forex_dashboard_contract.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_PAPER_FORWARD_EVIDENCE_V2.md",
            "docs/trading_lab/AIOS_FOREX_BUILDER_READINESS_DEMO_COMMANDS.md",
            "tests/forex_engine/test_paper_forward_evidence_v2.py",
            "tests/forex_engine/test_local_fixture_catalog.py",
            "tests/forex_engine/test_paper_forward_runner.py",
            "tests/forex_engine/test_month_end_readiness.py",
            "tests/forex_engine/test_forex_dashboard_contract.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-RISK-GOVERNOR-PAPER-FORWARD-THRESHOLDS",
        "title": "Add paper-forward risk governor thresholds",
        "lane": "risk-governor-paper-forward-thresholds",
        "landed_pr": "#746",
        "completion_reason": "risk-to-reward, expectancy, opportunity capture, cost/slippage stress, and threshold governor landed on main",
        "completed_files": [
            "automation/forex_engine/opportunity_capture.py",
            "automation/forex_engine/risk_governor_thresholds.py",
            "automation/forex_engine/run_risk_governor_demo.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_OPPORTUNITY_CAPTURE.md",
            "docs/trading_lab/AIOS_FOREX_BUILDER_RISK_GOVERNOR_THRESHOLDS.md",
            "tests/forex_engine/test_opportunity_capture.py",
            "tests/forex_engine/test_risk_governor_thresholds.py",
        ],
        "required_files": [
            "automation/forex_engine/opportunity_capture.py",
            "automation/forex_engine/risk_governor_thresholds.py",
            "automation/forex_engine/run_risk_governor_demo.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_OPPORTUNITY_CAPTURE.md",
            "docs/trading_lab/AIOS_FOREX_BUILDER_RISK_GOVERNOR_THRESHOLDS.md",
            "tests/forex_engine/test_opportunity_capture.py",
            "tests/forex_engine/test_risk_governor_thresholds.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-PAPER-FORWARD-STRESS-AND-OUT-OF-SAMPLE-V1",
        "title": "Add paper-forward stress and out-of-sample validation",
        "lane": "paper-forward-stress-and-out-of-sample",
        "landed_pr": "#747",
        "completion_reason": "stress scenarios, OOS validation, heldout fixtures, leave-one-regime/symbol/timeframe checks, combined stress/OOS gate, readiness/dashboard propagation, docs, and tests landed on main",
        "completed_files": [
            "automation/forex_engine/paper_forward_stress.py",
            "automation/forex_engine/out_of_sample_validator.py",
            "automation/forex_engine/run_stress_and_oos_demo.py",
            "automation/forex_engine/month_end_readiness.py",
            "automation/forex_engine/forex_dashboard_contract.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_STRESS_AND_OUT_OF_SAMPLE.md",
            "docs/trading_lab/AIOS_FOREX_BUILDER_BROKER_PAPER_SANDBOX_GATE.md",
            "tests/forex_engine/test_paper_forward_stress.py",
            "tests/forex_engine/test_out_of_sample_validator.py",
            "tests/forex_engine/test_month_end_readiness.py",
            "tests/forex_engine/test_forex_dashboard_contract.py",
        ],
        "required_files": [
            "automation/forex_engine/paper_forward_stress.py",
            "automation/forex_engine/out_of_sample_validator.py",
            "automation/forex_engine/run_stress_and_oos_demo.py",
            "automation/forex_engine/month_end_readiness.py",
            "automation/forex_engine/forex_dashboard_contract.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_STRESS_AND_OUT_OF_SAMPLE.md",
            "docs/trading_lab/AIOS_FOREX_BUILDER_BROKER_PAPER_SANDBOX_GATE.md",
            "tests/forex_engine/test_paper_forward_stress.py",
            "tests/forex_engine/test_out_of_sample_validator.py",
            "tests/forex_engine/test_month_end_readiness.py",
            "tests/forex_engine/test_forex_dashboard_contract.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-BROKER-PAPER-SANDBOX-READINESS-CONTRACT",
        "title": "Add broker-paper sandbox readiness contract",
        "lane": "broker-paper-sandbox-readiness-contract",
        "landed_pr": "#748",
        "completion_reason": "broker-paper sandbox readiness contract landed, kept broker-paper blocked as WATCHLIST, and advanced to stress repair",
        "completed_files": [
            "automation/forex_engine/broker_paper_sandbox_readiness.py",
            "automation/forex_engine/run_broker_paper_sandbox_readiness_demo.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_BROKER_PAPER_SANDBOX_READINESS_CONTRACT.md",
            "tests/forex_engine/test_broker_paper_sandbox_readiness.py",
        ],
        "required_files": [
            "automation/forex_engine/broker_paper_sandbox_readiness.py",
            "automation/forex_engine/run_broker_paper_sandbox_readiness_demo.py",
            "automation/forex_engine/month_end_readiness.py",
            "automation/forex_engine/forex_dashboard_contract.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_BROKER_PAPER_SANDBOX_READINESS_CONTRACT.md",
            "tests/forex_engine/test_broker_paper_sandbox_readiness.py",
            "tests/forex_engine/test_month_end_readiness.py",
            "tests/forex_engine/test_forex_dashboard_contract.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-PAPER-FORWARD-STRESS-REPAIR-V1",
        "title": "Add paper-forward stress repair",
        "lane": "paper-forward-stress-repair",
        "landed_pr": "#749",
        "completion_reason": "stress repair diagnostics and conservative filtering/sizing policy landed, improving worst stress PnL while preserving WATCHLIST blockers honestly",
        "completed_files": [
            "automation/forex_engine/stress_repair.py",
            "automation/forex_engine/run_stress_repair_demo.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_STRESS_REPAIR.md",
            "tests/forex_engine/test_stress_repair.py",
        ],
        "required_files": [
            "automation/forex_engine/stress_repair.py",
            "automation/forex_engine/run_stress_repair_demo.py",
            "automation/forex_engine/broker_paper_sandbox_readiness.py",
            "automation/forex_engine/month_end_readiness.py",
            "automation/forex_engine/forex_dashboard_contract.py",
            "automation/forex_engine/paper_forward_stress.py",
            "automation/forex_engine/out_of_sample_validator.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_STRESS_REPAIR.md",
            "tests/forex_engine/test_stress_repair.py",
            "tests/forex_engine/test_month_end_readiness.py",
            "tests/forex_engine/test_forex_dashboard_contract.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-PAPER-FORWARD-OOS-EXPANSION-V1",
        "title": "Add expanded OOS validation",
        "lane": "paper-forward-oos-expansion",
        "completion_reason": "expanded deterministic OOS validation landed with broader fixtures, regime/symbol/timeframe holdouts, degradation scoring, readiness/dashboard propagation, docs, and tests",
        "completed_files": [
            "automation/forex_engine/oos_expansion.py",
            "automation/forex_engine/run_oos_expansion_demo.py",
            "automation/forex_engine/out_of_sample_validator.py",
            "automation/forex_engine/local_fixture_catalog.py",
            "automation/forex_engine/paper_forward_evidence_v2.py",
            "automation/forex_engine/broker_paper_sandbox_readiness.py",
            "automation/forex_engine/month_end_readiness.py",
            "automation/forex_engine/forex_dashboard_contract.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_OOS_EXPANSION.md",
            "tests/forex_engine/test_oos_expansion.py",
            "tests/forex_engine/test_out_of_sample_validator.py",
            "tests/forex_engine/test_broker_paper_sandbox_readiness.py",
            "tests/forex_engine/test_month_end_readiness.py",
            "tests/forex_engine/test_forex_dashboard_contract.py",
        ],
        "required_files": [
            "automation/forex_engine/oos_expansion.py",
            "automation/forex_engine/run_oos_expansion_demo.py",
            "automation/forex_engine/out_of_sample_validator.py",
            "automation/forex_engine/local_fixture_catalog.py",
            "automation/forex_engine/paper_forward_evidence_v2.py",
            "automation/forex_engine/broker_paper_sandbox_readiness.py",
            "automation/forex_engine/month_end_readiness.py",
            "automation/forex_engine/forex_dashboard_contract.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_OOS_EXPANSION.md",
            "tests/forex_engine/test_oos_expansion.py",
            "tests/forex_engine/test_out_of_sample_validator.py",
            "tests/forex_engine/test_broker_paper_sandbox_readiness.py",
            "tests/forex_engine/test_month_end_readiness.py",
            "tests/forex_engine/test_forex_dashboard_contract.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-PAPER-FORWARD-OOS-REPAIR-V1",
        "title": "Add OOS repair gate",
        "lane": "paper-forward-oos-repair",
        "landed_pr": "#751",
        "completion_reason": (
            "OOS repair gate landed with low-vol filters, reduced sizing, degradation improvement, "
            "WATCHLIST preservation, and broker-paper kept blocked"
        ),
        "completed_files": [
            "automation/forex_engine/oos_repair.py",
            "automation/forex_engine/run_oos_repair_demo.py",
            "automation/forex_engine/oos_expansion.py",
            "automation/forex_engine/broker_paper_sandbox_readiness.py",
            "automation/forex_engine/month_end_readiness.py",
            "automation/forex_engine/forex_dashboard_contract.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_OOS_REPAIR.md",
            "tests/forex_engine/test_oos_repair.py",
        ],
        "required_files": [
            "automation/forex_engine/oos_repair.py",
            "automation/forex_engine/run_oos_repair_demo.py",
            "automation/forex_engine/oos_expansion.py",
            "automation/forex_engine/out_of_sample_validator.py",
            "automation/forex_engine/local_fixture_catalog.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_OOS_REPAIR.md",
            "docs/trading_lab/AIOS_FOREX_BUILDER_OOS_EXPANSION.md",
            "tests/forex_engine/test_oos_repair.py",
            "tests/forex_engine/test_oos_expansion.py",
            "tests/forex_engine/test_out_of_sample_validator.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-T9-BACKUP-DAILY-WORK-METRICS-SOS-V1",
        "title": "Add T9 backup daily work metrics and courtesy SOS",
        "lane": "backup-reporting-hardening",
        "landed_pr": "#752",
        "completion_reason": (
            "backup reports now separate copied snapshot metrics from dev-work delta, daily work metrics, "
            "timeslot work metrics, and report-only courtesy SOS"
        ),
        "completed_files": [
            "automation/orchestration/backups/Get-AiOsBackupWorkDelta.ps1",
            "automation/orchestration/backups/New-AiOsBackupCourtesySos.ps1",
            "automation/orchestration/backups/Start-AiOsPostMainUpdateBackup.DRY_RUN.ps1",
            "automation/orchestration/daily_snapshot/New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1",
            "scripts/backup/Start-AiOsT9SnapshotBackup.ps1",
            "docs/AI_OS/operations/T9_BACKUP_DAILY_WORK_METRICS_POLICY.md",
        ],
        "required_files": [
            "automation/orchestration/backups/Get-AiOsBackupWorkDelta.ps1",
            "automation/orchestration/backups/New-AiOsBackupCourtesySos.ps1",
            "automation/orchestration/backups/Start-AiOsPostMainUpdateBackup.DRY_RUN.ps1",
            "automation/orchestration/daily_snapshot/New-AiOsDailyAutomationSnapshot.DRY_RUN.ps1",
            "scripts/backup/Start-AiOsT9SnapshotBackup.ps1",
            "docs/AI_OS/operations/T9_BACKUP_DAILY_WORK_METRICS_POLICY.md",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-PAPER-FORWARD-LOW-VOL-EDGE-REDESIGN-V1",
        "title": "Add low-vol edge redesign",
        "lane": "forex-low-vol-edge-redesign",
        "landed_pr": "#753",
        "completion_reason": (
            "low-vol edge redesign landed with paper-only low-vol no-trade/reduced-size policy, "
            "audit fields, and broker/live blocked"
        ),
        "completed_files": [
            "automation/forex_engine/low_vol_edge_redesign.py",
            "automation/forex_engine/run_low_vol_edge_redesign_demo.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_LOW_VOL_EDGE_REDESIGN.md",
            "tests/forex_engine/test_low_vol_edge_redesign.py",
        ],
        "required_files": [
            "automation/forex_engine/low_vol_edge_redesign.py",
            "automation/forex_engine/run_low_vol_edge_redesign_demo.py",
            "automation/forex_engine/oos_repair.py",
            "automation/forex_engine/oos_expansion.py",
            "automation/forex_engine/broker_paper_sandbox_readiness.py",
            "automation/forex_engine/month_end_readiness.py",
            "automation/forex_engine/forex_dashboard_contract.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_LOW_VOL_EDGE_REDESIGN.md",
            "tests/forex_engine/test_low_vol_edge_redesign.py",
            "tests/forex_engine/test_oos_repair.py",
            "tests/forex_engine/test_oos_expansion.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1",
        "title": "Add broker-paper presecurity gate",
        "lane": "broker-paper-presecurity-gate",
        "landed_pr": "#754",
        "completion_reason": (
            "presecurity contract blocks credentials, env reads, broker SDKs, network/API, webhooks, "
            "schedulers, daemons, broker-paper orders, and live orders before adapter work"
        ),
        "completed_files": [
            "automation/forex_engine/broker_paper_presecurity_gate.py",
            "automation/forex_engine/run_broker_paper_presecurity_gate_demo.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_BROKER_PAPER_PRESECURITY_GATE.md",
            "tests/forex_engine/test_broker_paper_presecurity_gate.py",
        ],
        "required_files": [
            "automation/forex_engine/broker_paper_presecurity_gate.py",
            "automation/forex_engine/run_broker_paper_presecurity_gate_demo.py",
            "automation/forex_engine/broker_paper_sandbox_readiness.py",
            "automation/forex_engine/month_end_readiness.py",
            "automation/forex_engine/forex_dashboard_contract.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_BROKER_PAPER_PRESECURITY_GATE.md",
            "tests/forex_engine/test_broker_paper_presecurity_gate.py",
            "tests/forex_engine/test_broker_paper_sandbox_readiness.py",
            "tests/forex_engine/test_month_end_readiness.py",
            "tests/forex_engine/test_forex_dashboard_contract.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "PKT-AIOS-BROKER-PAPER-SANDBOX-ADAPTER-STUB-CONTRACT",
        "title": "Add broker-paper adapter stub contract",
        "lane": "broker-paper-adapter-stub-contract",
        "landed_pr": "#755",
        "completion_reason": (
            "local-only broker-paper adapter stub validates fake dry-run intents and produces simulated/rejected "
            "audit records while keeping broker SDK, credentials, network/API, broker-paper orders, and live trading blocked"
        ),
        "completed_files": [
            "automation/forex_engine/broker_paper_adapter_stub_contract.py",
            "automation/forex_engine/run_broker_paper_adapter_stub_contract_demo.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_BROKER_PAPER_ADAPTER_STUB_CONTRACT.md",
            "tests/forex_engine/test_broker_paper_adapter_stub_contract.py",
        ],
        "required_files": [
            "automation/forex_engine/broker_paper_adapter_stub_contract.py",
            "automation/forex_engine/run_broker_paper_adapter_stub_contract_demo.py",
            "automation/forex_engine/broker_paper_sandbox_readiness.py",
            "automation/forex_engine/month_end_readiness.py",
            "automation/forex_engine/forex_dashboard_contract.py",
            "docs/trading_lab/AIOS_FOREX_BUILDER_BROKER_PAPER_ADAPTER_STUB_CONTRACT.md",
            "tests/forex_engine/test_broker_paper_adapter_stub_contract.py",
            "tests/forex_engine/test_broker_paper_sandbox_readiness.py",
            "tests/forex_engine/test_month_end_readiness.py",
            "tests/forex_engine/test_forex_dashboard_contract.py",
        ],
        "source": "default_completed_memory",
    },
    {
        "packet_id": "AIOS-EDGE-PROOF-BUILDER-MASTER-V1",
        "alternate_packet_ids": [
            "PKT-AIOS-FOREX-EDGE-PROOF-SUPERTREND-V1",
            "PKT-AIOS-PAPER-ONLY-SUPERTREND-EDGE-PROOF",
        ],
        "title": "Add paper-only Supertrend edge proof builder",
        "lane": "paper-only-supertrend-edge-proof-builder",
        "landed_pr": "#740",
        "completion_reason": "paper-only Supertrend edge proof builder landed on main",
        "completed_files": [
            "automation/forex_engine/indicators.py",
            "automation/forex_engine/strategies.py",
            "automation/forex_engine/costs.py",
            "automation/forex_engine/metrics.py",
            "automation/forex_engine/edge_gate_policy.py",
            "automation/forex_engine/daily_edge_report.py",
            "automation/forex_engine/run_supertrend_edge_demo.py",
            "automation/forex_engine/run_supertrend_walk_forward_demo.py",
            "automation/forex_engine/run_daily_edge_report.py",
            "docs/AI_OS/trading/AIOS_TRADING_EDGE_PROOF_GATE.md",
            "docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_SUPERTREND_EDGE_PROOF.md",
            "tests/forex_engine/test_indicators.py",
            "tests/forex_engine/test_strategies.py",
            "tests/forex_engine/test_costs.py",
            "tests/forex_engine/test_metrics.py",
            "tests/forex_engine/test_edge_gate_policy.py",
            "tests/forex_engine/test_daily_edge_report.py",
        ],
        "required_files": [
            "automation/forex_engine/indicators.py",
            "automation/forex_engine/strategies.py",
            "automation/forex_engine/costs.py",
            "automation/forex_engine/metrics.py",
            "automation/forex_engine/edge_gate_policy.py",
            "automation/forex_engine/daily_edge_report.py",
            "automation/forex_engine/run_supertrend_edge_demo.py",
            "automation/forex_engine/run_supertrend_walk_forward_demo.py",
            "automation/forex_engine/run_daily_edge_report.py",
            "docs/AI_OS/trading/AIOS_TRADING_EDGE_PROOF_GATE.md",
            "docs/AI_OS/trading/FOREX_ENGINE_V1_SPRINT_4_SUPERTREND_EDGE_PROOF.md",
            "tests/forex_engine/test_indicators.py",
            "tests/forex_engine/test_strategies.py",
            "tests/forex_engine/test_costs.py",
            "tests/forex_engine/test_metrics.py",
            "tests/forex_engine/test_edge_gate_policy.py",
            "tests/forex_engine/test_daily_edge_report.py",
        ],
        "source": "default_completed_memory",
    },
]

COMPLETE_STATUSES = {
    "complete",
    "completed",
    "done",
    "closed",
    "merged",
    "landed",
    "passed",
    "success",
}

REOPENED_STATUSES = {"reopened", "reopen", "open_again"}
REPAIR_STATUSES = {"validation_failed", "failed", "repair", "needs_repair"}
SUPPRESSIBLE_FOREX_SCAFFOLD_PACKET_IDS = {
    "PKT-AIOS-FOREX-BUILDER-PAPER-FORWARD-SIMULATOR",
}


def _safety() -> dict[str, bool]:
    return {
        "preview_only": True,
        "evidence_only": True,
        "command_execution": False,
        "filesystem_writes": False,
        "reports_written": False,
        "network_access": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "scheduler_activation": False,
        "daemon_activation": False,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "real_webhooks": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "git_merge": False,
    }


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_items(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, str):
        return [part.strip() for part in value.replace("\r", "\n").replace(",", "\n").splitlines() if part.strip()]
    if value in (None, "", {}, []):
        return []
    return [value]


def _as_text_list(value: Any) -> list[str]:
    return [str(item).strip() for item in _as_items(value) if str(item).strip()]


def _text(value: Any, default: str = "") -> str:
    text = str(value or "").strip()
    return text if text else default


def _normalized(value: Any) -> str:
    return _text(value).lower().replace("-", "_").replace(" ", "_")


def _normalized_path(value: Any) -> str:
    normalized = _text(value).replace("\\", "/").strip().lower()
    while normalized.startswith("./"):
        normalized = normalized[2:]
    return normalized.rstrip("/")


def _candidate_list(evidence: Any) -> list[dict[str, Any]]:
    if isinstance(evidence, list):
        return [item for item in evidence if isinstance(item, dict)]
    if isinstance(evidence, dict):
        for key in ("candidate_packets", "candidates", "packets"):
            value = evidence.get(key)
            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]
        if evidence.get("packet_id"):
            return [evidence]
    return []


def _packet_id(record: dict[str, Any]) -> str:
    return _text(record.get("packet_id") or record.get("id"))


def _packet_ids(record: dict[str, Any]) -> list[str]:
    ids: list[str] = []
    for value in [_packet_id(record), *_as_text_list(record.get("alternate_packet_ids"))]:
        if value and value not in ids:
            ids.append(value)
    return ids


def _record_title(record: dict[str, Any]) -> str:
    return _text(record.get("title") or record.get("name") or record.get("pr_title"))


def _record_lane(record: dict[str, Any]) -> str:
    return _text(record.get("lane") or record.get("work_lane") or record.get("branch"))


def _required_files(record: dict[str, Any]) -> list[str]:
    return _as_text_list(
        record.get("required_files")
        or record.get("completed_files")
        or record.get("write_scope")
        or record.get("files")
        or record.get("changed_files")
    )


def _record_from_value(value: Any, source: str) -> dict[str, Any]:
    if isinstance(value, dict):
        record = dict(value)
        record.setdefault("source", source)
        return record
    return {
        "packet_id": _text(value),
        "source": source,
    }


def _normalize_completed_packet_record(record: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(record)
    if _packet_id(normalized) == "PKT-AIOS-PAPER-FORWARD-OOS-EXPANSION-V1":
        normalized.update(
            {
                "landed_pr": "#750",
                "title": "Add expanded OOS validation",
                "completion_reason": (
                    "expanded deterministic OOS validation landed with 14 fixtures, 29 splits, "
                    "low-vol degradation blocker exposed, and broker-paper kept blocked"
                ),
                "completed_files": [
                    "automation/forex_engine/oos_expansion.py",
                    "automation/forex_engine/run_oos_expansion_demo.py",
                    "docs/trading_lab/AIOS_FOREX_BUILDER_OOS_EXPANSION.md",
                    "tests/forex_engine/test_oos_expansion.py",
                ],
            }
        )
    if _packet_id(normalized) == "PKT-AIOS-PAPER-FORWARD-OOS-REPAIR-V1":
        normalized.update(
            {
                "landed_pr": "#751",
                "title": "Add OOS repair gate",
                "completion_reason": (
                    "OOS repair gate landed with low-vol filters, reduced sizing, degradation improvement, "
                    "WATCHLIST preservation, and broker-paper kept blocked"
                ),
            }
        )
    if _packet_id(normalized) == "PKT-AIOS-T9-BACKUP-DAILY-WORK-METRICS-SOS-V1":
        normalized.update(
            {
                "landed_pr": "#752",
                "title": "Add T9 backup daily work metrics and courtesy SOS",
                "completion_reason": (
                    "backup reports now separate copied snapshot metrics from dev-work delta, daily work metrics, "
                    "timeslot work metrics, and report-only courtesy SOS"
                ),
            }
        )
    if _packet_id(normalized) == "PKT-AIOS-PAPER-FORWARD-LOW-VOL-EDGE-REDESIGN-V1":
        normalized.update(
            {
                "landed_pr": "#753",
                "title": "Add low-vol edge redesign",
                "completion_reason": (
                    "low-vol edge redesign landed with paper-only low-vol no-trade/reduced-size policy, "
                    "audit fields, and broker/live blocked"
                ),
            }
        )
    if _packet_id(normalized) == "PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1":
        normalized.update(
            {
                "landed_pr": "#754",
                "title": "Add broker-paper presecurity gate",
                "completion_reason": (
                    "presecurity contract blocks credentials, env reads, broker SDKs, network/API, webhooks, "
                    "schedulers, daemons, broker-paper orders, and live orders before adapter work"
                ),
            }
        )
    if _packet_id(normalized) == "PKT-AIOS-BROKER-PAPER-SANDBOX-ADAPTER-STUB-CONTRACT":
        normalized.update(
            {
                "landed_pr": "#755",
                "title": "Add broker-paper adapter stub contract",
                "completion_reason": (
                    "local-only broker-paper adapter stub validates fake dry-run intents and produces simulated/rejected "
                    "audit records while keeping broker SDK, credentials, network/API, broker-paper orders, and live trading blocked"
                ),
            }
        )
    return normalized


def _completed_memory_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records = [dict(record) for record in DEFAULT_COMPLETED_PACKETS]
    for item in _as_items(payload.get("completed_packet_ids")):
        records.append(_record_from_value(item, "completed_packet_ids"))
    for item in _as_items(payload.get("completed_packets")):
        records.append(_record_from_value(item, "completed_packets"))
    for item in _as_items(payload.get("landed_prs")):
        records.append(_record_from_value(item, "landed_prs"))
    for item in _as_items(payload.get("commit_history_summary")):
        records.append(_record_from_value(item, "commit_history_summary"))
    return [_normalize_completed_packet_record(record) for record in records]


def _cycle_ledger_records(payload: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in _as_items(payload.get("cycle_ledger_history")):
        if not isinstance(item, dict):
            continue
        selected = item.get("selected_packet")
        record: dict[str, Any]
        if isinstance(selected, dict):
            record = dict(selected)
        else:
            record = {}
        record.setdefault("packet_id", item.get("packet_id") or item.get("current_packet") or selected)
        record.setdefault("title", item.get("title"))
        record.setdefault("lane", item.get("lane"))
        record.setdefault("status", item.get("status") or item.get("validation_status") or item.get("packet_status"))
        record["source"] = "cycle_ledger_history"
        records.append(record)
    return records


def _manual_rules(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rules: list[dict[str, Any]] = []
    for item in _as_items(payload.get("manual_suppression_rules")):
        if isinstance(item, dict):
            rules.append(item)
        else:
            rules.append({"packet_id": str(item)})
    return rules


def _completed_packet_ids(records: list[dict[str, Any]], cycle_records: list[dict[str, Any]]) -> list[str]:
    ids: list[str] = []
    for record in [*records, *cycle_records]:
        for packet_id in _packet_ids(record):
            if packet_id not in ids:
                ids.append(packet_id)
    return ids


def _files_are_new(candidate: dict[str, Any], memory_record: dict[str, Any]) -> bool:
    candidate_files = {_normalized_path(path) for path in _required_files(candidate)}
    memory_files = {_normalized_path(path) for path in _required_files(memory_record)}
    if not candidate_files or not memory_files:
        return False
    return not candidate_files.issubset(memory_files)


def _title_or_lane_matches(candidate: dict[str, Any], memory_record: dict[str, Any]) -> bool:
    candidate_title = _normalized(_record_title(candidate))
    candidate_lane = _normalized(_record_lane(candidate))
    memory_title = _normalized(_record_title(memory_record))
    memory_lane = _normalized(_record_lane(memory_record))
    return bool(
        (candidate_title and candidate_title == memory_title)
        or (candidate_lane and candidate_lane == memory_lane)
    )


def _write_scope_matches(candidate: dict[str, Any], memory_record: dict[str, Any]) -> bool:
    candidate_files = {_normalized_path(path) for path in _required_files(candidate)}
    memory_files = {_normalized_path(path) for path in _required_files(memory_record)}
    if not candidate_files or not memory_files:
        return False
    return candidate_files.issubset(memory_files)


def _is_reopened(candidate: dict[str, Any]) -> bool:
    status = _normalized(candidate.get("status"))
    return (
        candidate.get("reopened") is True
        or candidate.get("explicitly_reopened") is True
        or status in REOPENED_STATUSES
    )


def _is_validation_repair(candidate: dict[str, Any]) -> bool:
    status = _normalized(candidate.get("status"))
    validation_status = _normalized(candidate.get("validation_status"))
    return (
        candidate.get("validation_failed") is True
        or status in REPAIR_STATUSES
        or validation_status in {"failed", "fail", "validation_failed"}
    )


def _is_forex_scaffold(candidate: dict[str, Any]) -> bool:
    if _packet_id(candidate) in SUPPRESSIBLE_FOREX_SCAFFOLD_PACKET_IDS:
        return False
    text = " ".join(
        [
            _packet_id(candidate),
            _record_title(candidate),
            _record_lane(candidate),
            " ".join(_as_text_list(candidate.get("tags"))),
        ]
    ).lower()
    return "forex" in text and "scaffold" in text


def _cycle_record_is_complete(record: dict[str, Any]) -> bool:
    status_values = [
        record.get("status"),
        record.get("validation_status"),
        record.get("packet_status"),
        record.get("pr_status"),
        record.get("checks_status"),
    ]
    return any(_normalized(value) in COMPLETE_STATUSES for value in status_values)


def _manual_rule_matches(candidate: dict[str, Any], rule: dict[str, Any]) -> bool:
    candidate_id = _packet_id(candidate)
    candidate_lane = _normalized(_record_lane(candidate))
    rule_id = _text(rule.get("packet_id") or rule.get("id"))
    rule_lane = _normalized(rule.get("lane"))
    return bool(
        (rule_id and rule_id == candidate_id)
        or (rule_lane and rule_lane == candidate_lane)
    )


def _suppression_reasons(
    candidate: dict[str, Any],
    memory_records: list[dict[str, Any]],
    cycle_records: list[dict[str, Any]],
    manual_rules: list[dict[str, Any]],
) -> list[str]:
    if _is_reopened(candidate) or _is_validation_repair(candidate) or _is_forex_scaffold(candidate):
        return []

    reasons: list[str] = []
    candidate_id = _packet_id(candidate)
    for record in memory_records:
        if _files_are_new(candidate, record):
            continue
        record_ids = _packet_ids(record)
        source = _text(record.get("source"), "memory")
        if candidate_id and candidate_id in record_ids:
            reasons.append(f"completed_packet_id:{candidate_id}")
        if source == "landed_prs" and _title_or_lane_matches(candidate, record):
            reasons.append(f"landed_pr_match:{_record_title(record) or _record_lane(record)}")
        if _write_scope_matches(candidate, record) and (_record_lane(candidate) == _record_lane(record) or record_ids):
            reasons.append(f"completed_write_scope_match:{source}")
        if source == "commit_history_summary" and _title_or_lane_matches(candidate, record):
            reasons.append(f"commit_history_match:{_record_title(record) or _record_lane(record)}")

    for rule in manual_rules:
        if _manual_rule_matches(candidate, rule):
            reasons.append(f"manual_suppression_rule:{_text(rule.get('reason'), 'matched')}")

    for record in cycle_records:
        if not _cycle_record_is_complete(record):
            continue
        if candidate_id and _packet_id(record) == candidate_id:
            reasons.append(f"cycle_ledger_complete:{candidate_id}")
        elif _title_or_lane_matches(candidate, record):
            reasons.append(f"cycle_ledger_complete:{_record_title(record) or _record_lane(record)}")

    unique: list[str] = []
    for reason in reasons:
        if reason and reason not in unique:
            unique.append(reason)
    return unique


def _alignment() -> dict[str, Any]:
    return {
        "milestone": FOREX_MILESTONE,
        "monthly_goal": "Legitimate daily repo progress while building forex toward gated trade readiness.",
        "factory_status": "AIOS is the factory.",
        "proof_target": "industrial-grade forex bot builder",
        "proof_product": "forex is the first proof product",
        "daily_contribution_policy": "Daily GitHub work must be legitimate validated repo work.",
        "future_gate_warning": "Live trade readiness is a protected downstream gate, not an automatic background action.",
        "control_plane_role": "completed packet memory and candidate suppression",
        "aligned": True,
        "blocked_boundaries": [],
        "requires_future_gates_before_execution": True,
    }


def _next_safe_action(status: str, next_available: bool) -> str:
    if status == "empty":
        return "Add candidate packet evidence before applying completed packet memory."
    if next_available:
        return "Feed active candidates to the packet queue planner; do not mutate queues from memory suppression."
    return "All provided candidates are suppressed; provide the next unfinished self-build or forex-builder candidate."


def build_completed_packet_memory(raw_evidence: Any | None = None) -> dict[str, Any]:
    payload = _as_dict(raw_evidence)
    candidates = _candidate_list(raw_evidence)
    memory_records = _completed_memory_records(payload)
    cycle_records = _cycle_ledger_records(payload)
    manual_rules = _manual_rules(payload)
    completed_ids = _completed_packet_ids(memory_records, cycle_records)

    active_candidates: list[dict[str, Any]] = []
    suppressed_candidates: list[dict[str, Any]] = []
    suppression_reasons: dict[str, list[str]] = {}

    for candidate in candidates:
        packet_id = _packet_id(candidate) or _record_title(candidate) or "unknown_candidate"
        reasons = _suppression_reasons(candidate, memory_records, cycle_records, manual_rules)
        if reasons:
            suppressed_candidates.append(
                {
                    "candidate": candidate,
                    "packet_id": packet_id,
                    "suppression_reasons": reasons,
                }
            )
            suppression_reasons[packet_id] = reasons
        else:
            active_candidates.append(candidate)

    status = "empty" if not candidates else "ready"
    next_candidate = active_candidates[0] if active_candidates else None

    return {
        "schema": SCHEMA,
        "suppression_status": status,
        "active_candidates": active_candidates,
        "suppressed_candidates": suppressed_candidates,
        "completed_packet_ids": completed_ids,
        "suppression_reasons": suppression_reasons,
        "next_candidate_available": next_candidate is not None,
        "next_candidate": next_candidate,
        "memory_source": {
            "default_completed_memory_count": len(DEFAULT_COMPLETED_PACKETS),
            "completed_packet_ids_count": len(_as_items(payload.get("completed_packet_ids"))),
            "landed_prs_count": len(_as_items(payload.get("landed_prs"))),
            "commit_history_summary_count": len(_as_items(payload.get("commit_history_summary"))),
            "cycle_ledger_history_count": len(_as_items(payload.get("cycle_ledger_history"))),
            "manual_suppression_rules_count": len(manual_rules),
        },
        "forex_builder_alignment": _alignment(),
        "commands_executed": [],
        "files_written": [],
        "workers_dispatched": False,
        "queues_mutated": False,
        "approvals_mutated": False,
        "safety": _safety(),
        "next_safe_action": _next_safe_action(status, next_candidate is not None),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Suppress completed AIOS candidate packets.")
    parser.add_argument("--evidence", default="{}", help="JSON candidate and completed packet evidence.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        evidence = json.loads(args.evidence)
    except json.JSONDecodeError:
        evidence = {}
    result = build_completed_packet_memory(evidence)
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
