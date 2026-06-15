from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from automation.forex_engine import schema_contracts as schemas


def build_forex_dashboard_state(
    strategy: str | dict[str, Any] = "local_close_momentum_v1",
    fixture: schemas.MarketDataFixture | dict[str, Any] | None = None,
    backtest_result: schemas.BacktestResult | dict[str, Any] | None = None,
    walk_forward_summary: schemas.WalkForwardSummary | dict[str, Any] | None = None,
    risk_gate: schemas.RiskGateResult | dict[str, Any] | None = None,
    paper_forward_summary: dict[str, Any] | None = None,
    blockers: list[str] | None = None,
    sos_required: bool = False,
    next_safe_action: str | None = None,
) -> schemas.DashboardState:
    active_blockers = list(blockers or [])
    active_blockers.extend(_blockers(risk_gate))
    active_blockers.extend(_blockers(walk_forward_summary))
    current_blocker = active_blockers[0] if active_blockers else "none"
    risk_status = _classification(risk_gate, default="not_run")
    paper_state = _paper_state(paper_forward_summary)
    state = schemas.DashboardState(
        current_phase="paper-forward simulation scaffold",
        selected_strategy=_strategy_name(strategy),
        data_fixture_status="ready" if fixture is not None else "missing",
        backtest_status=_backtest_status(backtest_result),
        walk_forward_status=_classification(walk_forward_summary, default="not_run"),
        risk_gate_status=risk_status,
        paper_permission_state=paper_state,
        live_permission_state="blocked",
        current_blocker=current_blocker,
        sos_required=bool(sos_required),
        next_safe_action=next_safe_action
        or _next_safe_action(risk_status, paper_state, current_blocker),
    )
    schemas.validate_dashboard_state_schema(state)
    return state


def format_forex_dashboard_lines(state: schemas.DashboardState | dict[str, Any]) -> list[str]:
    payload = _payload(state)
    schemas.validate_dashboard_state_schema(payload)
    return [
        "FOREX BUILDER STATUS",
        f"Strategy: {payload['selected_strategy']}",
        f"Fixture: {payload['data_fixture_status']}",
        f"Backtest: {payload['backtest_status']} | Walk-forward: {payload['walk_forward_status']}",
        f"Risk gate: {payload['risk_gate_status']}",
        f"Paper-forward: {payload['paper_permission_state']}",
        f"Blocker: {payload['current_blocker']}",
        f"SOS: {'yes' if payload['sos_required'] else 'no'}",
        f"Next: {payload['next_safe_action']}",
        "Safety: no broker/live/secrets/orders/webhooks",
    ]


def dashboard_contract_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_BUILDER_DASHBOARD_CONTRACT.v1",
        "compact_default": True,
        "max_default_lines": 10,
        "reports_written_by_default": False,
        "fields": [
            "strategy",
            "fixture",
            "backtest",
            "walk_forward",
            "risk_gate",
            "paper_forward",
            "blockers",
            "sos",
            "next_safe_action",
        ],
        "live_permission_state": "blocked",
        "safety": "no broker/live/secrets/orders/webhooks",
    }


def _payload(value: Any) -> dict[str, Any]:
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, dict):
        return dict(value)
    raise TypeError(f"Expected dataclass or dict, got {type(value).__name__}")


def _optional_payload(value: Any | None) -> dict[str, Any]:
    if value in (None, "", [], {}):
        return {}
    return _payload(value)


def _strategy_name(strategy: str | dict[str, Any]) -> str:
    if isinstance(strategy, dict):
        return str(strategy.get("strategy_id") or strategy.get("strategy_name") or "unknown_strategy")
    return str(strategy)


def _classification(value: Any | None, default: str) -> str:
    payload = _optional_payload(value)
    return str(payload.get("classification") or payload.get("status") or default)


def _blockers(value: Any | None) -> list[str]:
    payload = _optional_payload(value)
    raw = payload.get("blockers") or []
    return [str(item) for item in raw] if isinstance(raw, list) else [str(raw)]


def _backtest_status(value: Any | None) -> str:
    payload = _optional_payload(value)
    if not payload:
        return "not_run"
    total_trades = int(payload.get("total_trades", 0))
    return "ready" if total_trades > 0 else "no_trades"


def _paper_state(summary: dict[str, Any] | None) -> str:
    payload = summary or {}
    if payload.get("total_entries", 0):
        return "simulated_local_only"
    if payload.get("classification"):
        return str(payload["classification"])
    return "not_started"


def _next_safe_action(risk_status: str, paper_state: str, blocker: str) -> str:
    if blocker != "none":
        return "Resolve blocker before promotion; keep report-only."
    if risk_status == "PAPER_FORWARD_READY" and paper_state == "simulated_local_only":
        return "Expand local paper-forward evidence; live remains blocked."
    if risk_status == "PAPER_FORWARD_READY":
        return "Run local paper-forward simulator; no broker or live path."
    return "Run risk gate and collect stronger local evidence."
