from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from automation.forex_engine import schema_contracts as schemas


ALLOWED_EVIDENCE_CLASSES = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}


def aggregate_forex_evidence(
    backtest_result: schemas.BacktestResult | dict[str, Any],
    walk_forward_summary: schemas.WalkForwardSummary | dict[str, Any] | None,
    risk_gate: schemas.RiskGateResult | dict[str, Any],
    paper_summary: dict[str, Any] | None = None,
    cost_model: dict[str, Any] | None = None,
) -> dict[str, Any]:
    backtest_payload = _payload(backtest_result)
    risk_payload = _payload(risk_gate)
    walk_payload = _payload(walk_forward_summary) if walk_forward_summary is not None else {}
    paper_payload = dict(paper_summary or {})
    cost_payload = cost_model or {
        "status": "LOCAL_FIXED_COST_MODEL",
        "used": True,
        "network_allowed": False,
    }
    schemas.validate_backtest_result_schema(backtest_payload)
    schemas.validate_risk_gate_schema(risk_payload)
    schemas.assert_no_live_permissions([backtest_payload, walk_payload, risk_payload, paper_payload, cost_payload])

    blockers = []
    blockers.extend(_text_list(risk_payload.get("blockers")))
    blockers.extend(_text_list(walk_payload.get("blockers")))
    blockers.extend(_text_list(paper_payload.get("blockers")))
    if int(backtest_payload.get("total_trades", 0)) <= 0:
        blockers.append("backtest_has_no_trades")
    if not walk_payload:
        blockers.append("walk_forward_summary_missing")
    if not paper_payload:
        blockers.append("paper_forward_summary_missing")
    if cost_payload.get("used") is not True:
        blockers.append("cost_model_required")
    if _classification(risk_payload) == "FAIL":
        blockers.append("risk_gate_failed")

    bundle = {
        "schema": "AIOS_FOREX_BUILDER_EVIDENCE_BUNDLE.v1",
        "backtest_result": backtest_payload,
        "walk_forward_summary": walk_payload,
        "cost_model": cost_payload,
        "risk_gate": risk_payload,
        "paper_forward_summary": paper_payload,
        "blockers": _unique(blockers),
        "live_ready": False,
        "allowed_classifications": sorted(ALLOWED_EVIDENCE_CLASSES),
    }
    bundle["classification"] = classify_evidence_bundle(bundle)
    bundle["next_safe_action"] = _next_safe_action(bundle["classification"], bundle["blockers"])
    schemas.assert_no_live_permissions(bundle)
    return bundle


def classify_evidence_bundle(bundle: dict[str, Any]) -> str:
    payload = dict(bundle)
    if payload.get("live_ready") is True or payload.get("classification") == "LIVE_READY":
        return "FAIL"
    risk_gate = payload.get("risk_gate") or {}
    backtest = payload.get("backtest_result") or {}
    walk_forward = payload.get("walk_forward_summary") or {}
    paper = payload.get("paper_forward_summary") or {}
    blockers = _text_list(payload.get("blockers"))
    if _classification(risk_gate) == "FAIL" or int(backtest.get("total_trades", 0)) <= 0:
        return "FAIL"
    if blockers:
        return "WATCHLIST"
    if (
        _classification(risk_gate) == "PAPER_FORWARD_READY"
        and _classification(walk_forward) == "PAPER_FORWARD_READY"
        and int(paper.get("total_entries", 0)) > 0
    ):
        return "PAPER_FORWARD_READY"
    return "WATCHLIST"


def _payload(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return dict(value)
    raise TypeError(f"Expected dataclass or dict, got {type(value).__name__}")


def _classification(payload: dict[str, Any]) -> str:
    return str(payload.get("classification") or payload.get("status") or "WATCHLIST")


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


def _next_safe_action(classification: str, blockers: list[str]) -> str:
    if classification == "PAPER_FORWARD_READY":
        return "Expand local paper-forward evidence; live readiness remains blocked."
    if blockers:
        return "Resolve evidence blockers before any promotion discussion."
    return "Continue collecting local backtest, walk-forward, cost, and paper-forward evidence."
