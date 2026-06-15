from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from automation.forex_engine import schema_contracts as schemas
from automation.forex_engine.evidence_aggregator import ALLOWED_EVIDENCE_CLASSES


LIVE_TRADE_BLOCKERS = [
    "live readiness requires a separate protected future packet",
    "broker integration is not approved",
    "credentials and secrets are blocked",
    "real orders are blocked",
    "webhooks are blocked",
    "scheduler and daemon activation are blocked",
]


def build_month_end_readiness_review(
    evidence_bundle: dict[str, Any],
    dashboard_state: schemas.DashboardState | dict[str, Any] | None = None,
) -> dict[str, Any]:
    bundle = dict(evidence_bundle)
    dashboard = _payload(dashboard_state) if dashboard_state is not None else {}
    schemas.assert_no_live_permissions([bundle, dashboard])
    classification = str(bundle.get("classification") or "FAIL")
    if classification not in ALLOWED_EVIDENCE_CLASSES:
        classification = "FAIL"
    blockers = _text_list(bundle.get("blockers"))
    paper_forward_ready = classification == "PAPER_FORWARD_READY" and not blockers
    review = {
        "schema": "AIOS_FOREX_BUILDER_MONTH_END_READINESS_REVIEW.v1",
        "classification": classification,
        "complete": _complete_sections(bundle, dashboard),
        "blocked": _unique([*blockers, *LIVE_TRADE_BLOCKERS]),
        "evidence_exists": {
            "backtest": bool(bundle.get("backtest_result")),
            "walk_forward": bool(bundle.get("walk_forward_summary")),
            "cost_model": bool(bundle.get("cost_model")),
            "risk_gate": bool(bundle.get("risk_gate")),
            "paper_forward": bool(bundle.get("paper_forward_summary")),
            "dashboard": bool(dashboard),
        },
        "paper_forward_ready": paper_forward_ready,
        "live_trade_ready": False,
        "live_trade_blockers": list(LIVE_TRADE_BLOCKERS),
        "protected_gate_required": True,
        "next_safe_action": _next_safe_action(paper_forward_ready, blockers),
        "live_ready": False,
    }
    schemas.assert_no_live_permissions(review)
    return review


def _payload(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return dict(value)
    raise TypeError(f"Expected dataclass or dict, got {type(value).__name__}")


def _text_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if value in (None, "", {}, []):
        return []
    return [str(value)]


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique


def _complete_sections(bundle: dict[str, Any], dashboard: dict[str, Any]) -> list[str]:
    complete = []
    for key, label in (
        ("backtest_result", "backtest result"),
        ("walk_forward_summary", "walk-forward summary"),
        ("cost_model", "cost model"),
        ("risk_gate", "risk gate"),
        ("paper_forward_summary", "paper-forward ledger summary"),
    ):
        if bundle.get(key):
            complete.append(label)
    if dashboard:
        complete.append("dashboard state")
    return complete


def _next_safe_action(paper_forward_ready: bool, blockers: list[str]) -> str:
    if paper_forward_ready:
        return "Continue paper-forward evidence expansion; live readiness remains blocked behind protected gates."
    if blockers:
        return "Resolve month-end evidence blockers before paper-forward readiness is claimed."
    return "Collect missing evidence and rerun the local readiness review."
