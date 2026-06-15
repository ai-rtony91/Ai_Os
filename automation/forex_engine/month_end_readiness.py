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


def build_month_end_readiness_v2_review(evidence_bundle: dict[str, Any]) -> dict[str, Any]:
    bundle = dict(evidence_bundle)
    schemas.assert_no_live_permissions(bundle)
    classification = str(bundle.get("classification") or "FAIL")
    if classification not in ALLOWED_EVIDENCE_CLASSES:
        classification = "FAIL"
    blockers = _text_list(bundle.get("blockers"))
    multi_summary = dict(bundle.get("multi_fixture_paper_forward_summary") or {})
    regime = dict(bundle.get("regime_consistency") or {})
    catalog = dict(bundle.get("fixture_catalog_summary") or {})
    paper_forward_ready = classification == "PAPER_FORWARD_READY" and not blockers
    review = {
        "schema": "AIOS_FOREX_BUILDER_MONTH_END_READINESS_REVIEW_V2.v1",
        "classification": classification,
        "paper_forward_ready": paper_forward_ready,
        "v2_evidence_ready": paper_forward_ready,
        "live_trade_ready": False,
        "protected_gate_required": True,
        "evidence_summary": {
            "fixture_count": int(multi_summary.get("fixture_count", 0)),
            "regime_count": int(regime.get("total_regimes", 0)),
            "total_intents": int(multi_summary.get("total_intents", 0)),
            "simulated_ledger_entries": int(multi_summary.get("total_ledger_entries", 0)),
            "aggregate_paper_pnl": float(multi_summary.get("aggregate_pnl", 0.0)),
            "consistency_pct": float(multi_summary.get("consistency_pct", 0.0)),
            "regime_consistency_pct": float(regime.get("consistent_regimes_pct", 0.0)),
            "symbols": list(catalog.get("symbols") or []),
            "timeframes": list(catalog.get("timeframes") or []),
        },
        "blockers": _unique(blockers),
        "blocked": _unique([*blockers, *LIVE_TRADE_BLOCKERS]),
        "live_trade_blockers": list(LIVE_TRADE_BLOCKERS),
        "next_safe_action": _next_safe_action_v2(paper_forward_ready, blockers),
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


def _next_safe_action_v2(paper_forward_ready: bool, blockers: list[str]) -> str:
    if paper_forward_ready:
        return "Continue protected paper-forward evidence expansion and risk review; live readiness requires separate future approval."
    if blockers:
        return "Resolve V2 local evidence blockers before claiming paper-forward readiness."
    return "Collect stronger multi-regime local evidence and rerun V2 readiness review."
