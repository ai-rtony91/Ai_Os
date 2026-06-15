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
        "validators": [VALIDATOR],
        "dependencies": [],
        "conflicts": [],
        "safety_flags": [],
        "forex_builder_alignment": _alignment(),
        "purpose": purpose,
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
                "tests/orchestration/test_aios_forex_builder_data_schemas.py",
            ],
            purpose=(
                "Define local fixture schemas for market data, signals, orders-as-intent, "
                "backtest outputs, and paper ledger records. Must remain non-live and no broker/secrets."
            ),
        ),
        _candidate(
            packet_id="PKT-AIOS-FOREX-BUILDER-BACKTEST-HARNESS",
            title="Create forex builder deterministic backtest harness scaffold",
            lane="forex-builder-backtest",
            priority="medium",
            milestone_value="medium",
            risk_level="low",
            required_files=[
                "docs/trading_lab/AIOS_FOREX_BUILDER_BACKTEST_HARNESS.md",
                "tests/orchestration/test_aios_forex_builder_backtest.py",
            ],
            purpose=(
                "Create deterministic backtest harness scaffold using local fixtures only. "
                "Must remain non-live and no broker/secrets."
            ),
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
                "tests/orchestration/test_aios_forex_builder_risk_contract.py",
            ],
            purpose=(
                "Define risk gate contract before any paper/live execution. "
                "Must remain non-live and no broker/secrets."
            ),
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
                "tests/orchestration/test_aios_forex_builder_dashboard.py",
            ],
            purpose=(
                "Define dashboard fields for strategy status, backtest result, risk gate, "
                "paper state, and SOS blockers. Must remain non-live and no broker/secrets."
            ),
        ),
    ]


def build_forex_builder_roadmap(_evidence: Any | None = None) -> dict[str, Any]:
    candidates = _roadmap_candidates()
    next_candidate = candidates[0]

    return {
        "schema": SCHEMA,
        "roadmap_status": "ready",
        "today_goal_alignment": _alignment(),
        "roadmap_candidates": candidates,
        "candidate_packets": candidates,
        "candidates": candidates,
        "forbidden_lanes": FORBIDDEN_LANES,
        "next_recommended_candidate": next_candidate,
        "commands_executed": [],
        "files_written": [],
        "workers_dispatched": False,
        "queues_mutated": False,
        "approvals_mutated": False,
        "safety": _safety(),
        "next_safe_action": "Promote the canonical forex builder spec candidate as the next unfinished non-live self-build packet.",
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
