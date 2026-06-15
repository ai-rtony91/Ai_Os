from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from automation.forex_engine import schema_contracts as schemas
from automation.forex_engine.edge_gate_policy import (
    DEFAULT_POLICY as EDGE_GATE_POLICY,
    FAIL,
    PAPER_FORWARD_READY,
    WATCHLIST,
    classify_edge_gate,
)


ALLOWED_RISK_CLASSES = {FAIL, WATCHLIST, PAPER_FORWARD_READY}

FORBIDDEN_BOUNDARY_KEYS = {
    "live_ready",
    "broker_allowed",
    "broker_permission",
    "real_orders_allowed",
    "orders_allowed",
    "network_allowed",
    "network_market_automation_allowed",
    "credentials_allowed",
    "secrets_allowed",
    "env_reads_allowed",
    "env_writes_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhooks_allowed",
    "execution_allowed",
    "live_order",
}


def classify_risk_gate(
    backtest_result: schemas.BacktestResult | dict[str, Any],
    walk_forward_summary: schemas.WalkForwardSummary | dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
) -> schemas.RiskGateResult:
    boundary_blockers = _boundary_blockers(backtest_result, walk_forward_summary, policy or {})
    if boundary_blockers:
        gate = schemas.RiskGateResult(
            gate_id="risk-gate-live-boundary-block",
            classification=FAIL,
            blockers=boundary_blockers,
            next_safe_action="Remove live, broker, credential, network, scheduler, daemon, webhook, or order permissions.",
        )
        assert_risk_contract_blocks_live(gate)
        return gate

    metrics = _metrics(backtest_result)
    walk_forward_payload = _walk_forward_payload(walk_forward_summary)
    active_policy = dict(EDGE_GATE_POLICY)
    active_policy.update({key: value for key, value in (policy or {}).items() if key in EDGE_GATE_POLICY})
    edge_gate = classify_edge_gate(metrics, walk_forward_payload, active_policy, cost_model_used=True)

    classification = str(edge_gate["classification"])
    if classification not in ALLOWED_RISK_CLASSES:
        classification = FAIL
    gate = schemas.RiskGateResult(
        gate_id=f"risk-gate-{_text(_field(backtest_result, 'result_id'), 'local-backtest')}",
        classification=classification,
        blockers=list(edge_gate.get("blockers", [])),
        next_safe_action=str(edge_gate.get("next_safe_action") or _next_safe_action(classification)),
    )
    schemas.validate_risk_gate_schema(gate)
    assert_risk_contract_blocks_live(gate)
    return gate


def risk_policy_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_BUILDER_RISK_CONTRACT.v1",
        "allowed_classifications": sorted(ALLOWED_RISK_CLASSES),
        "automatic_live_ready": False,
        "live_ready_output_allowed": False,
        "edge_gate_policy_module": "automation/forex_engine/edge_gate_policy.py",
        "edge_gate_policy": dict(EDGE_GATE_POLICY),
        "blocked_boundaries": sorted(FORBIDDEN_BOUNDARY_KEYS),
        "next_safe_action": "Classify only FAIL, WATCHLIST, or PAPER_FORWARD_READY; live readiness remains protected downstream.",
    }


def assert_risk_contract_blocks_live(result: schemas.RiskGateResult | dict[str, Any]) -> bool:
    payload = _payload(result)
    if payload.get("classification") == "LIVE_READY":
        raise ValueError("Risk contract must never emit LIVE_READY")
    if payload.get("classification") not in ALLOWED_RISK_CLASSES:
        raise ValueError("Risk contract classification must be FAIL, WATCHLIST, or PAPER_FORWARD_READY")
    if payload.get("live_ready") is not False:
        raise ValueError("Risk contract live_ready must always be false")
    schemas.assert_no_live_permissions(payload)
    return True


def _payload(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return dict(value)
    raise TypeError(f"Expected dataclass or dict, got {type(value).__name__}")


def _field(value: Any, key: str, default: Any = None) -> Any:
    return _payload(value).get(key, default)


def _text(value: Any, default: str = "") -> str:
    text = str(value or "").strip()
    return text if text else default


def _metrics(backtest_result: schemas.BacktestResult | dict[str, Any]) -> dict[str, Any]:
    payload = _payload(backtest_result)
    if "metrics" in payload and isinstance(payload["metrics"], dict):
        return dict(payload["metrics"])
    schemas.validate_backtest_result_schema(payload)
    losing_streak = 0
    current_losing_streak = 0
    for trade in payload.get("trades", []):
        trade_payload = _payload(trade)
        if float(trade_payload.get("pnl_usd", 0.0)) < 0:
            current_losing_streak += 1
            losing_streak = max(losing_streak, current_losing_streak)
        else:
            current_losing_streak = 0
    return {
        "total_trades": int(payload["total_trades"]),
        "expectancy_r": float(payload["expectancy_r"]),
        "profit_factor": float(payload["profit_factor"] or 0.0),
        "max_drawdown_pct": float(payload["max_drawdown_pct"]),
        "longest_losing_streak": losing_streak,
    }


def _walk_forward_payload(summary: schemas.WalkForwardSummary | dict[str, Any] | None) -> dict[str, Any] | None:
    if summary is None:
        return None
    payload = _payload(summary)
    if "windows" in payload:
        schemas.validate_walk_forward_summary_schema(payload)
    return payload


def _boundary_blockers(*values: Any) -> list[str]:
    blockers: list[str] = []
    for value in values:
        _collect_boundary_blockers(_payload(value), blockers)
    return blockers


def _collect_boundary_blockers(value: Any, blockers: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in FORBIDDEN_BOUNDARY_KEYS and item is True:
                blocker = f"forbidden_boundary:{key}"
                if blocker not in blockers:
                    blockers.append(blocker)
            if key == "broker_order_id" and item not in (None, ""):
                blocker = "forbidden_boundary:broker_order_id"
                if blocker not in blockers:
                    blockers.append(blocker)
            _collect_boundary_blockers(item, blockers)
    elif isinstance(value, list):
        for item in value:
            _collect_boundary_blockers(item, blockers)


def _next_safe_action(classification: str) -> str:
    if classification == PAPER_FORWARD_READY:
        return "Continue local paper-forward simulation only; live trading remains blocked."
    if classification == WATCHLIST:
        return "Collect stronger backtest, walk-forward, cost, and paper-forward evidence."
    return "Reject or repair the strategy candidate before paper-forward simulation."
