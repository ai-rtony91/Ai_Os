from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


SCHEMA = "AIOS_FOREX_GOAL_DECISION.v1"
SUPPORTED_GOAL = "forex-paper-bot"

FOREX_COMPONENT_PATHS = {
    "forex_paper_bot": Path("apps/trading_lab/trading_lab/forex_paper_bot.py"),
    "forex_backtest": Path("apps/trading_lab/trading_lab/forex_backtest.py"),
    "forex_paper_ledger": Path("apps/trading_lab/trading_lab/forex_paper_ledger.py"),
    "forex_strategy_rules": Path("apps/trading_lab/trading_lab/forex_strategy_rules.py"),
    "forex_data_import": Path("apps/trading_lab/trading_lab/forex_data_import.py"),
    "forex_report": Path("apps/trading_lab/trading_lab/forex_report.py"),
    "forex_decision_policy": Path("apps/trading_lab/trading_lab/forex_decision_policy.py"),
}

NEXT_BUILD_RECOMMENDATIONS = {
    "continue_build": "Continue the next paper-only Forex build step after review.",
    "improve_strategy": "Open a bounded APPLY packet to improve paper strategy rules.",
    "improve_data": "Open a bounded APPLY packet to improve local paper data coverage.",
    "improve_risk_controls": "Open a bounded APPLY packet to improve paper risk controls.",
    "stop_for_human_review": "Stop for Anthony review before continuing the Forex goal.",
}


def safety_flags() -> dict[str, bool]:
    return {
        "file_writes": False,
        "network_access": False,
        "broker": False,
        "credentials": False,
        "live_trading": False,
        "real_orders": False,
        "real_webhooks": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "worker_dispatch": False,
        "runtime_launch": False,
        "scheduler": False,
        "daemon": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
    }


def component_status(repo_root: Path) -> dict[str, bool]:
    return {
        name: (repo_root / relative_path).exists()
        for name, relative_path in FOREX_COMPONENT_PATHS.items()
    }


def deterministic_paper_report_fixture() -> dict[str, Any]:
    return {
        "allowed": True,
        "paper_only": True,
        "report_type": "paper_scorecard",
        "trade_count": 10,
        "win_rate": 60.0,
        "total_pnl": 125.0,
        "risk_flags": [],
    }


def report_summary(report: dict[str, Any]) -> dict[str, Any]:
    return {
        "allowed": report.get("allowed"),
        "paper_only": report.get("paper_only"),
        "report_type": report.get("report_type"),
        "trade_count": report.get("trade_count", 0),
        "win_rate": report.get("win_rate", 0.0),
        "total_pnl": report.get("total_pnl", 0.0),
        "risk_flags": report.get("risk_flags", []),
    }


def _blocked_report(
    goal: str,
    components_present: dict[str, bool],
    reason_code: str,
    summary: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "goal": goal,
        "components_present": components_present,
        "report_summary": summary or {},
        "decision": "stop_for_human_review",
        "reason_code": reason_code,
        "decision_reasons": [reason_code],
        "decision_bridge_passed": False,
        "next_build_recommendation": NEXT_BUILD_RECOMMENDATIONS["stop_for_human_review"],
        "next_safe_action": "Stop and repair the blocked Forex goal decision bridge input.",
        "safety": safety_flags(),
    }


def _load_decision_policy(repo_root: Path):
    policy_path = repo_root / FOREX_COMPONENT_PATHS["forex_decision_policy"]
    spec = importlib.util.spec_from_file_location("forex_decision_policy", policy_path)
    if spec is None or spec.loader is None:
        return None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "decide_next_action"):
        return None
    return module


def build_goal_decision(
    repo_root: Path,
    *,
    goal: str = SUPPORTED_GOAL,
    report: dict[str, Any] | None = None,
    live_execution: bool = False,
    broker_order: bool = False,
    credentials: Any = None,
    api_key: Any = None,
    real_order: bool = False,
    webhook_url: str | None = None,
    network: bool = False,
    network_access: bool = False,
) -> dict[str, Any]:
    components_present = component_status(repo_root)
    if goal != SUPPORTED_GOAL:
        return _blocked_report(goal, components_present, "unsupported_goal")

    if not all(components_present.values()):
        return _blocked_report(goal, components_present, "missing_required_components")

    paper_report = report or deterministic_paper_report_fixture()
    summary = report_summary(paper_report)
    policy = _load_decision_policy(repo_root)
    if policy is None:
        return _blocked_report(goal, components_present, "decision_policy_unavailable", summary)

    decision = policy.decide_next_action(
        paper_report,
        live_execution=live_execution,
        broker_order=broker_order,
        credentials=credentials,
        api_key=api_key,
        real_order=real_order,
        webhook_url=webhook_url,
        network=network,
        network_access=network_access,
    )
    decision_name = decision.get("decision", "stop_for_human_review")
    reason_code = decision.get("reason_code", "unknown_decision_reason")
    next_build_recommendation = NEXT_BUILD_RECOMMENDATIONS.get(
        decision_name,
        NEXT_BUILD_RECOMMENDATIONS["stop_for_human_review"],
    )
    decision_bridge_passed = bool(decision.get("allowed") is True and reason_code != "unknown_decision_reason")

    return {
        "schema": SCHEMA,
        "goal": goal,
        "components_present": components_present,
        "report_summary": summary,
        "decision": decision_name,
        "reason_code": reason_code,
        "decision_reasons": decision.get("decision_reasons", [reason_code]),
        "decision_bridge_passed": decision_bridge_passed,
        "next_build_recommendation": next_build_recommendation,
        "next_safe_action": (
            f"{next_build_recommendation} Commit and push still require Anthony approval."
            if decision_bridge_passed
            else "Stop and repair the blocked Forex goal decision bridge input."
        ),
        "safety": safety_flags(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build one read-only Forex goal decision report.")
    parser.add_argument("--repo-root", default=None, help="Optional repository root.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    repo_root = Path(args.repo_root).resolve() if args.repo_root else Path(__file__).resolve().parents[2]
    decision = build_goal_decision(repo_root)
    print(json.dumps(decision, indent=2, sort_keys=False))
    return 0 if decision.get("decision_bridge_passed") else 1


if __name__ == "__main__":
    raise SystemExit(main())
