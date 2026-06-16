from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_FOREX_BUILDER_ROADMAP_CANDIDATE_SOURCE.v1"

TODAY_MILESTONE = (
    "AIOS self-building machine -> first proof target: industrial-grade forex trading bot builder "
    "-> specs, schemas, simulation, backtesting, risk policy, and dashboard/reporting scaffolds only"
)

CANONICAL_SPEC_PACKET_ID = "PKT-AIOS-FOREX-BUILDER-CANONICAL-SPEC"
OOS_REPAIR_PACKET_ID = "PKT-AIOS-PAPER-FORWARD-OOS-REPAIR-V1"
LOW_VOL_EDGE_REDESIGN_PACKET_ID = "PKT-AIOS-PAPER-FORWARD-LOW-VOL-EDGE-REDESIGN-V1"
STRESS_REPAIR_V2_PACKET_ID = "PKT-AIOS-PAPER-FORWARD-STRESS-REPAIR-V2"
PRESECURITY_GATE_PACKET_ID = "PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1"

VALIDATOR = "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_forex_builder_roadmap.py -q"

FORBIDDEN_LANES = [
    "broker integration",
    "OANDA/live exchange integration",
    "live orders",
    "paper orders unless separately approved",
    "credentials/secrets/env reads/writes",
    "webhooks",
    "scheduler/daemon execution",
    "real-money trading",
    "account mutation",
    "network market automation",
]


def _alignment() -> dict[str, Any]:
    return {
        "milestone": TODAY_MILESTONE,
        "proof_target": "industrial-grade forex trading bot builder",
        "control_plane_role": "safe forex-builder roadmap candidate source",
        "aligned": True,
        "non_live_only": True,
        "blocked_boundaries": FORBIDDEN_LANES,
        "requires_future_gates_before_execution": True,
        "security_gate_required_before_broker_paper": True,
        "required_security_packet": PRESECURITY_GATE_PACKET_ID,
        "security_gate_reason": "broker-paper requires secrets/network/broker boundaries before adapter work",
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


def _candidate(
    *,
    packet_id: str,
    title: str,
    lane: str,
    priority: str,
    milestone_value: str,
    risk_level: str,
    required_files: list[str],
    purpose: str,
    validators: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "packet_id": packet_id,
        "title": title,
        "lane": lane,
        "priority": priority,
        "milestone_value": milestone_value,
        "risk_level": risk_level,
        "status": "candidate",
        "required_files": required_files,
        "blocked_files": [],
        "required_approvals": [],
        "validators": validators or [VALIDATOR],
        "dependencies": [],
        "conflicts": [],
        "safety_flags": [],
        "non_live_only": True,
        "network_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_allowed": False,
        "live_trading_allowed": False,
        "credentials_allowed": False,
        "orders_allowed": False,
        "webhooks_allowed": False,
    }


def _roadmap_candidates() -> list[dict[str, Any]]:
    return [
        _candidate(
            packet_id=CANONICAL_SPEC_PACKET_ID,
            title="Create canonical forex builder product spec",
            lane="forex-builder-spec",
            priority="high",
            milestone_value="high",
            risk_level="low",
            required_files=[
                "docs/trading_lab/AIOS_FOREX_BUILDER_SPEC.md",
                "tests/orchestration/test_aios_forex_builder_roadmap.py",
            ],
            purpose=(
                "Define industrial-grade forex bot builder requirements, safety boundaries, "
                "non-live phases, and quality gates."
            ),
        ),
        _candidate(
            packet_id="PKT-AIOS-FOREX-BUILDER-DATA-SCHEMAS",
            title="Define forex builder local data schemas",
            lane="forex-builder-data-schemas",
            priority="medium",
            milestone_value="high",
            risk_level="low",
            required_files=[
                "docs/trading_lab/AIOS_FOREX_BUILDER_DATA_SCHEMAS.md",
                "automation/forex_engine/schema_contracts.py",
                "tests/forex_engine/test_schema_contracts.py",
            ],
            purpose=(
                "Define local fixture schemas for market data, signals, orders-as-intent, "
                "backtest outputs, and paper ledger records. Must remain non-live and no broker/secrets."
            ),
        ),
        _candidate(
            packet_id="PKT-AIOS-FOREX-BUILDER-BACKTEST-HARNESS",
            title="Create forex builder deterministic backtest harness contract",
            lane="forex-builder-backtest",
            priority="medium",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "docs/trading_lab/AIOS_FOREX_BUILDER_BACKTEST_HARNESS.md",
                "automation/forex_engine/backtest_harness.py",
                "tests/forex_engine/test_backtest_harness.py",
            ],
            purpose=(
                "Create deterministic backtest harness scaffold using local fixtures only. "
                "Must remain non-live and no broker/secrets."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_backtest_harness.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-FOREX-BUILDER-RISK-CONTRACT",
            title="Define forex builder risk gate contract",
            lane="forex-builder-risk-policy",
            priority="medium",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "docs/trading_lab/AIOS_FOREX_BUILDER_RISK_CONTRACT.md",
                "automation/forex_engine/risk_contract.py",
                "tests/forex_engine/test_risk_contract.py",
            ],
            purpose=(
                "Define risk gate contract before any paper/live execution. "
                "Must remain non-live and no broker/secrets."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_risk_contract.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-FOREX-BUILDER-DASHBOARD-CONTRACT",
            title="Define forex builder dashboard contract",
            lane="forex-builder-dashboard",
            priority="medium",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "docs/trading_lab/AIOS_FOREX_BUILDER_DASHBOARD_CONTRACT.md",
                "automation/forex_engine/forex_dashboard_contract.py",
                "tests/forex_engine/test_forex_dashboard_contract.py",
            ],
            purpose=(
                "Define dashboard fields for strategy status, backtest result, risk gate, "
                "paper state, and SOS blockers. Must remain non-live and no broker/secrets."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_forex_dashboard_contract.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-FOREX-BUILDER-PAPER-FORWARD-SIMULATOR",
            title="Create local paper-forward simulator scaffold",
            lane="forex-builder-paper-forward-simulator",
            priority="medium",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "docs/trading_lab/AIOS_FOREX_BUILDER_PAPER_FORWARD_SIMULATOR.md",
                "automation/forex_engine/paper_forward_simulator.py",
                "tests/forex_engine/test_paper_forward_simulator.py",
            ],
            purpose=(
                "Create local simulated ledger scaffolding from order-intent records. "
                "This is not broker paper trading and must remain local only."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_paper_forward_simulator.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-FOREX-BUILDER-EVIDENCE-AGGREGATOR",
            title="Create forex builder evidence aggregator",
            lane="forex-builder-evidence-aggregator",
            priority="medium",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "docs/trading_lab/AIOS_FOREX_BUILDER_EVIDENCE_AGGREGATOR.md",
                "automation/forex_engine/evidence_aggregator.py",
                "tests/forex_engine/test_evidence_aggregator.py",
            ],
            purpose=(
                "Combine backtest, walk-forward, cost, risk, and local paper-forward evidence "
                "into FAIL/WATCHLIST/PAPER_FORWARD_READY only."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_evidence_aggregator.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-FOREX-BUILDER-MONTH-END-READINESS",
            title="Create forex builder month-end readiness review",
            lane="forex-builder-month-end-readiness",
            priority="medium",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "docs/trading_lab/AIOS_FOREX_BUILDER_MONTH_END_READINESS.md",
                "automation/forex_engine/month_end_readiness.py",
                "tests/forex_engine/test_month_end_readiness.py",
            ],
            purpose=(
                "Summarize complete evidence, blockers, paper-forward readiness, and protected "
                "live-readiness gates without writing reports by default."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_month_end_readiness.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-APPROVED-EXECUTOR-LOOP-LITE",
            title="Document approved executor loop lite",
            lane="approved-executor-loop-lite",
            priority="low",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "docs/orchestration/AIOS_APPROVED_EXECUTOR_LOOP_LITE.md",
                "tests/orchestration/test_aios_operator_checkpoint_dashboard.py",
            ],
            purpose=(
                "Document that AIOS can run only explicitly approved local packets and must stop "
                "before protected actions, dispatch, queues, approvals, schedulers, or daemons."
            ),
        ),
        _candidate(
            packet_id="PKT-AIOS-DAILY-CONTRIBUTION-LOOP-LITE",
            title="Document daily earned contribution loop lite",
            lane="daily-contribution-loop-lite",
            priority="low",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "docs/orchestration/AIOS_DAILY_CONTRIBUTION_LOOP_LITE.md",
                "tests/orchestration/test_aios_operator_checkpoint_dashboard.py",
            ],
            purpose=(
                "Document bored-queue-only daily work when no higher-priority packet exists, "
                "forbidding fake commits and generated noise."
            ),
        ),
        _candidate(
            packet_id="PKT-AIOS-PAPER-FORWARD-EVIDENCE-EXPANSION-V1",
            title="Expand local paper-forward forex evidence",
            lane="paper-forward-evidence-expansion",
            priority="low",
            milestone_value="medium",
            risk_level="low",
            required_files=[
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
            purpose=(
                "Build a usable local evidence layer around deterministic fixtures, simulated "
                "paper-forward ledgers, evidence bundles, compact demos, dashboard state, and "
                "month-end readiness review. No broker, network, secrets, orders, webhooks, scheduler, or daemon."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_local_fixture_catalog.py tests/forex_engine/test_paper_forward_runner.py tests/forex_engine/test_evidence_bundle_runner.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-PAPER-FORWARD-EVIDENCE-EXPANSION-V2",
            title="Expand paper-forward evidence with broader out-of-sample fixtures",
            lane="paper-forward-evidence-expansion-v2",
            priority="medium",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "automation/forex_engine/paper_forward_evidence_v2.py",
                "automation/forex_engine/run_paper_forward_evidence_v2_demo.py",
                "docs/trading_lab/AIOS_FOREX_BUILDER_PAPER_FORWARD_EVIDENCE_V2.md",
                "tests/forex_engine/test_paper_forward_evidence_v2.py",
            ],
            purpose=(
                "Broaden local paper-forward evidence with more out-of-sample fixtures, multi-fixture "
                "paper-forward comparison, regime consistency scoring, and stronger blocker reporting "
                "before any readiness threshold promotion."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_paper_forward_evidence_v2.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-RISK-GOVERNOR-PAPER-FORWARD-THRESHOLDS",
            title="Define paper-forward risk governor thresholds",
            lane="risk-governor-paper-forward-thresholds",
            priority="low",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "automation/forex_engine/risk_governor_thresholds.py",
                "automation/forex_engine/opportunity_capture.py",
                "automation/forex_engine/run_risk_governor_demo.py",
                "docs/trading_lab/AIOS_FOREX_BUILDER_RISK_GOVERNOR_THRESHOLDS.md",
                "docs/trading_lab/AIOS_FOREX_BUILDER_OPPORTUNITY_CAPTURE.md",
                "tests/forex_engine/test_risk_governor_thresholds.py",
                "tests/forex_engine/test_opportunity_capture.py",
            ],
            purpose=(
                "Define stricter paper-forward thresholds, opportunity capture metrics, missed edge "
                "estimates, cost drag, drawdown checks, and stress scenarios for evidence review only. "
                "This must not create live trading approval or broker execution."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_risk_governor_thresholds.py tests/forex_engine/test_opportunity_capture.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-PAPER-FORWARD-STRESS-AND-OUT-OF-SAMPLE-V1",
            title="Expand paper-forward stress and out-of-sample validation",
            lane="paper-forward-stress-and-out-of-sample",
            priority="low",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "automation/forex_engine/paper_forward_stress.py",
                "automation/forex_engine/out_of_sample_validator.py",
                "automation/forex_engine/run_stress_and_oos_demo.py",
                "automation/forex_engine/month_end_readiness.py",
                "automation/forex_engine/forex_dashboard_contract.py",
                "docs/trading_lab/AIOS_FOREX_BUILDER_STRESS_AND_OUT_OF_SAMPLE.md",
                "docs/trading_lab/AIOS_FOREX_BUILDER_BROKER_PAPER_SANDBOX_GATE.md",
                "tests/forex_engine/test_paper_forward_stress.py",
                "tests/forex_engine/test_out_of_sample_validator.py",
            ],
            purpose=(
                "Extend local paper-forward evidence with stronger stress, out-of-sample, and "
                "regime-resilience validation before any broker-paper sandbox readiness contract. "
                "No broker, network, secrets, orders, scheduler, daemon, or live trading path."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_paper_forward_stress.py tests/forex_engine/test_out_of_sample_validator.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-BROKER-PAPER-SANDBOX-READINESS-CONTRACT",
            title="Define broker-paper sandbox readiness contract",
            lane="broker-paper-sandbox-readiness-contract",
            priority="low",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "automation/forex_engine/broker_paper_sandbox_readiness.py",
                "automation/forex_engine/run_broker_paper_sandbox_readiness_demo.py",
                "automation/forex_engine/month_end_readiness.py",
                "automation/forex_engine/forex_dashboard_contract.py",
                "docs/trading_lab/AIOS_FOREX_BUILDER_BROKER_PAPER_SANDBOX_READINESS_CONTRACT.md",
                "tests/forex_engine/test_broker_paper_sandbox_readiness.py",
                "tests/forex_engine/test_month_end_readiness.py",
                "tests/forex_engine/test_forex_dashboard_contract.py",
            ],
            purpose=(
                "Define the protected readiness contract for a future broker-paper sandbox review only. "
                "This packet must not integrate a broker, read credentials, place paper orders, place live "
                "orders, use network/API ingestion, or bypass protected approval."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_broker_paper_sandbox_readiness.py tests/forex_engine/test_month_end_readiness.py tests/forex_engine/test_forex_dashboard_contract.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-PAPER-FORWARD-STRESS-REPAIR-V1",
            title="Repair paper-forward stress WATCHLIST blockers",
            lane="paper-forward-stress-repair",
            priority="low",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "automation/forex_engine/stress_repair.py",
                "automation/forex_engine/run_stress_repair_demo.py",
                "automation/forex_engine/broker_paper_sandbox_readiness.py",
                "automation/forex_engine/month_end_readiness.py",
                "automation/forex_engine/forex_dashboard_contract.py",
                "docs/trading_lab/AIOS_FOREX_BUILDER_STRESS_REPAIR.md",
                "tests/forex_engine/test_stress_repair.py",
                "automation/forex_engine/paper_forward_stress.py",
                "automation/forex_engine/out_of_sample_validator.py",
            ],
            purpose=(
                "Repair deterministic stress/OOS WATCHLIST blockers before any adapter-stub contract. "
                "No broker, network, credentials, orders, scheduler, daemon, or live trading path."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_stress_repair.py tests/forex_engine/test_broker_paper_sandbox_readiness.py tests/forex_engine/test_month_end_readiness.py tests/forex_engine/test_forex_dashboard_contract.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-PAPER-FORWARD-OOS-EXPANSION-V1",
            title="Expand deterministic paper-forward OOS evidence",
            lane="paper-forward-oos-expansion",
            priority="low",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "automation/forex_engine/oos_expansion.py",
                "automation/forex_engine/run_oos_expansion_demo.py",
                "automation/forex_engine/out_of_sample_validator.py",
                "automation/forex_engine/local_fixture_catalog.py",
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
            purpose=(
                "Expand deterministic local heldout and degradation evidence after stress repair remains WATCHLIST. "
                "This is not broker integration, credentials work, paper order execution, or live trading."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_oos_expansion.py tests/forex_engine/test_out_of_sample_validator.py tests/forex_engine/test_broker_paper_sandbox_readiness.py tests/forex_engine/test_month_end_readiness.py tests/forex_engine/test_forex_dashboard_contract.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-PAPER-FORWARD-OOS-REPAIR-V1",
            title="Repair expanded paper-forward OOS WATCHLIST blockers",
            lane="paper-forward-oos-repair",
            priority="low",
            milestone_value="medium",
            risk_level="low",
            required_files=[
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
            purpose=(
                "Repair expanded deterministic OOS WATCHLIST blockers through clearer diagnostics, "
                "more local heldout coverage, and degradation review only. No broker, network, credentials, "
                "orders, scheduler, daemon, or live trading path."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_oos_expansion.py tests/forex_engine/test_out_of_sample_validator.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-PAPER-FORWARD-LOW-VOL-EDGE-REDESIGN-V1",
            title="Redesign low-vol paper-forward edge controls",
            lane="paper-forward-low-vol-edge-redesign",
            priority="low",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "automation/forex_engine/oos_repair.py",
                "automation/forex_engine/oos_expansion.py",
                "docs/trading_lab/AIOS_FOREX_BUILDER_OOS_REPAIR.md",
                "tests/forex_engine/test_oos_repair.py",
                "tests/forex_engine/test_oos_expansion.py",
            ],
            purpose=(
                "Redesign low-volatility edge quality after OOS repair remains WATCHLIST. "
                "This is paper-only local evidence work, not broker integration, credentials, "
                "order execution, scheduler, daemon, or live trading."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_oos_repair.py tests/forex_engine/test_oos_expansion.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-PAPER-FORWARD-STRESS-REPAIR-V2",
            title="Repair remaining stress survival WATCHLIST blockers",
            lane="paper-forward-stress-repair-v2",
            priority="low",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "automation/forex_engine/stress_repair.py",
                "automation/forex_engine/paper_forward_stress.py",
                "automation/forex_engine/oos_expansion.py",
                "docs/trading_lab/AIOS_FOREX_BUILDER_STRESS_REPAIR.md",
                "tests/forex_engine/test_stress_repair.py",
                "tests/forex_engine/test_paper_forward_stress.py",
            ],
            purpose=(
                "Continue protected stress repair if expanded OOS survives but stress repair remains WATCHLIST. "
                "No broker integration, credentials, order execution, scheduler, daemon, or live trading."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_stress_repair.py tests/forex_engine/test_paper_forward_stress.py tests/forex_engine/test_oos_expansion.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1",
            title="Define broker-paper pre-security gate",
            lane="broker-paper-presecurity-gate",
            priority="low",
            milestone_value="medium",
            risk_level="medium",
            required_files=[
                "docs/security/AIOS_BROKER_PAPER_PRESECURITY_GATE.md",
                "tests/forex_engine/test_broker_paper_sandbox_readiness.py",
                "tests/forex_engine/test_month_end_readiness.py",
            ],
            purpose=(
                "Define secrets, network, broker, account, kill-switch, and audit boundaries before "
                "any future broker-paper adapter work. This packet must not implement secrets, broker "
                "connections, network calls, paper orders, live orders, scheduler, daemon, or trading execution."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_broker_paper_sandbox_readiness.py tests/forex_engine/test_month_end_readiness.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-BROKER-PAPER-SANDBOX-ADAPTER-STUB-CONTRACT",
            title="Define sandbox adapter stub contract",
            lane="sandbox-adapter-stub-contract",
            priority="low",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "docs/trading_lab/AIOS_FOREX_BUILDER_SANDBOX_ADAPTER_STUB_CONTRACT.md",
                "tests/forex_engine/test_sandbox_adapter_stub_contract.py",
            ],
            purpose=(
                "Define a protected future adapter-stub contract only. This must not connect to a broker, "
                "read credentials, use network/API ingestion, place paper orders, place live orders, "
                "or bypass protected approval."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/forex_engine/test_sandbox_adapter_stub_contract.py -q",
                VALIDATOR,
            ],
        ),
        _candidate(
            packet_id="PKT-AIOS-APPROVED-EXECUTOR-LOCAL-APPLY-LOOP",
            title="Design approved executor local apply loop",
            lane="approved-executor-local-apply-loop",
            priority="low",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "docs/orchestration/AIOS_APPROVED_EXECUTOR_LOCAL_APPLY_LOOP.md",
                "tests/orchestration/test_aios_approved_executor_local_apply_loop.py",
            ],
            purpose=(
                "Design the next local apply loop after paper-forward evidence exists, with no "
                "worker dispatch, queue mutation, approval mutation, scheduler, daemon, commit, push, or merge."
            ),
            validators=[
                "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_approved_executor_local_apply_loop.py -q",
                VALIDATOR,
            ],
        ),
    ]


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _candidate_by_id(candidates: list[dict[str, Any]], packet_id: str) -> dict[str, Any] | None:
    for candidate in candidates:
        if candidate.get("packet_id") == packet_id:
            return candidate
    return None


def _conditional_repair_routing(evidence: Any | None) -> dict[str, Any]:
    payload = _as_dict(evidence)
    oos_repair = _as_dict(payload.get("oos_repair"))
    stress_repair = _as_dict(payload.get("stress_repair"))
    oos_classification = str(
        payload.get("oos_repair_classification")
        or oos_repair.get("repaired_classification")
        or oos_repair.get("classification")
        or "not_run"
    )
    stress_classification = str(
        payload.get("stress_repair_classification")
        or stress_repair.get("repaired_classification")
        or stress_repair.get("classification")
        or "not_run"
    )
    if oos_classification == "WATCHLIST":
        selected = LOW_VOL_EDGE_REDESIGN_PACKET_ID
        reason = "OOS repair remains WATCHLIST, so low-vol edge quality must be redesigned before broker-paper readiness."
    elif oos_classification == "PAPER_FORWARD_READY" and stress_classification == "WATCHLIST":
        selected = STRESS_REPAIR_V2_PACKET_ID
        reason = "OOS repair passed, but stress repair remains WATCHLIST."
    elif oos_classification == "PAPER_FORWARD_READY" and stress_classification == "PAPER_FORWARD_READY":
        selected = PRESECURITY_GATE_PACKET_ID
        reason = "OOS and stress repair passed, so broker-paper must stop at pre-security gate before adapter work."
    else:
        selected = OOS_REPAIR_PACKET_ID
        reason = "After PR #750, the current selected packet remains OOS repair until repair evidence is supplied."
    return {
        "current_selected_packet_after_pr_750": OOS_REPAIR_PACKET_ID,
        "observed_oos_repair_classification": oos_classification,
        "observed_stress_repair_classification": stress_classification,
        "next_safe_packet": selected,
        "reason": reason,
        "conditional_next_packets": {
            "oos_repair_watchlist": LOW_VOL_EDGE_REDESIGN_PACKET_ID,
            "oos_pass_stress_watchlist": STRESS_REPAIR_V2_PACKET_ID,
            "oos_and_stress_pass": PRESECURITY_GATE_PACKET_ID,
        },
        "forbidden_next_packets": [
            "broker integration",
            "credentials",
            "order execution",
            "live trading",
            "scheduler/daemon trading",
        ],
        "security_gate_required_before_broker_paper": True,
        "required_security_packet": PRESECURITY_GATE_PACKET_ID,
        "security_gate_reason": "broker-paper requires secrets/network/broker boundaries before adapter work",
    }


def build_forex_builder_roadmap(_evidence: Any | None = None) -> dict[str, Any]:
    candidates = _roadmap_candidates()
    next_candidate = candidates[0]
    repair_routing = _conditional_repair_routing(_evidence)

    return {
        "schema": SCHEMA,
        "roadmap_status": "ready",
        "today_goal_alignment": _alignment(),
        "roadmap_candidates": candidates,
        "candidate_packets": candidates,
        "candidates": candidates,
        "forbidden_lanes": FORBIDDEN_LANES,
        "next_recommended_candidate": next_candidate,
        "current_selected_packet": OOS_REPAIR_PACKET_ID,
        "post_oos_repair_routing": repair_routing,
        "post_oos_repair_next_safe_packet": repair_routing["next_safe_packet"],
        "post_oos_repair_next_safe_candidate": _candidate_by_id(candidates, str(repair_routing["next_safe_packet"])),
        "security_gate_required_before_broker_paper": True,
        "required_security_packet": PRESECURITY_GATE_PACKET_ID,
        "security_gate_reason": "broker-paper requires secrets/network/broker boundaries before adapter work",
        "commands_executed": [],
        "files_written": [],
        "workers_dispatched": False,
        "queues_mutated": False,
        "approvals_mutated": False,
        "safety": _safety(),
        "next_safe_action": "Filter roadmap candidates through completed packet memory and promote the first unfinished non-live forex-builder packet.",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Emit safe AIOS forex-builder roadmap candidates.")
    parser.add_argument("--evidence", default="{}", help="Optional JSON evidence reserved for future roadmap filtering.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        evidence = json.loads(args.evidence)
    except json.JSONDecodeError:
        evidence = {}
    result = build_forex_builder_roadmap(evidence)
    print(json.dumps(result, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
