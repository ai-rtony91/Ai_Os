"""Consolidated readiness blocker closure contract for Forex review progression."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from .proof_bundle_to_candidate_bridge import run_proof_bundle_to_candidate_bridge

PACKET_ID = "AIOS_FOREX_CONSOLIDATED_READINESS_BLOCKER_CLOSURE_V1"
REPORT_PATH = Path("Reports/forex_delivery/AIOS_FOREX_CONSOLIDATED_READINESS_BLOCKER_CLOSURE_V1_REPORT.md")

CANONICAL_BLOCKERS: list[str] = [
    "walk_forward_failed",
    "paper_evidence_not_ready",
    "mitigation_worsened",
    "missing_validation_results",
    "candidate_not_approved_for_demo_validation",
    "demo_contract_not_complete",
    "missing_live_readiness_candidate",
    "missing_approval_trace",
    "missing_risk_limits",
    "missing_kill_switch_proof",
    "missing_rollback_proof",
    "missing_reconciliation_proof",
    "missing_evidence_freshness",
    "missing_replayability_proof",
    "missing_final_disarm_proof",
    "missing_post_trade_journal_path",
    "demo_validation_contract_not_complete",
    "one_shot_exception_package_not_review_ready",
    "live_review_certificate_not_review_ready",
    "missing_human_review_ready",
]

DEFAULT_MIN_SAMPLE_SIZE = 10
DEFAULT_MAX_EXPECTANCY = 0.0
DEFAULT_MIN_PROFIT_FACTOR = 1.0
DEFAULT_MAX_FRESHNESS_HOURS = 24

PROFITABLE_LIVE_BOT_READY = "PROFITABLE_LIVE_BOT_READY"
REQUIRE_MORE_EVIDENCE = "REQUIRE_MORE_EVIDENCE"
BLOCKED_BY_RISK = "BLOCKED_BY_RISK"
BLOCKED_BY_BROKER_GATE = "BLOCKED_BY_BROKER_GATE"
BLOCKED_BY_POLICY = "BLOCKED_BY_POLICY"
BLOCKED_BY_SANDBOX_1312 = "BLOCKED_BY_SANDBOX_1312"

FINAL_MIN_CLOSED_TRADES = 30
FINAL_MIN_WALK_FORWARD_WINDOWS = 3
FINAL_MIN_PROFIT_FACTOR = 1.20
FINAL_DEFAULT_MAX_DRAWDOWN = 0.10
FINAL_DEFAULT_MAX_EFFECTIVE_LEVERAGE = 2.0
FINAL_DEFAULT_MAX_LIVE_MICRO_UNITS = 1000
FINAL_DEFAULT_LIVE_MICRO_UNITS = 1

ACCOUNT_PERMISSION_GATE = "ACCOUNT_PERMISSION_GATE"
ACCOUNT_PERMISSION_GATE_CLEARED = "ACCOUNT_PERMISSION_GATE_CLEARED"
ACCOUNT_PERMISSION_REQUIRED_FIELDS = (
    "broker_name",
    "broker_environment",
    "asset_class",
    "account_type",
    "account_currency",
    "margin_available_confirmed",
    "effective_leverage_limit",
    "long_permission",
    "short_permission",
    "fifo_required",
    "hedging_available",
    "instrument_tradable",
    "max_units",
    "stop_loss_supported",
    "take_profit_supported",
    "order_type_supported",
    "one_order_only_supported",
    "demo_sandbox_order_preview_supported",
    "broker_house_restrictions",
    "proof_timestamp",
    "proof_source",
    "sanitized_evidence_only",
)
ACCOUNT_PERMISSION_FIELD_ALIASES: dict[str, tuple[str, ...]] = {
    "margin_available_confirmed": ("margin_available",),
    "hedging_available": ("hedging_allowed",),
    "demo_sandbox_order_preview_supported": ("broker_demo_or_sandbox_proof", "broker_sandbox_or_demo_proof"),
}
BROKER_DEMO_SANDBOX_ENVIRONMENTS = {"demo", "sandbox", "practice", "paper_demo", "paper-sandbox"}

LIVE_EXCEPTION_RISK_CONFIRMATIONS = (
    "kill_switch_confirmed",
    "max_loss_confirmed",
    "daily_stop_confirmed",
    "stop_loss_confirmed",
    "take_profit_confirmed",
    "one_order_only_confirmed",
    "micro_size_confirmed",
    "low_effective_leverage_confirmed",
)
LIVE_EXCEPTION_NO_ACTION_PROOFS = (
    "no_credential_read",
    "no_credential_write",
    "no_env_read",
    "no_env_write",
    "no_account_id_read",
    "no_account_id_write",
    "no_network_call",
    "no_broker_mutation",
    "no_live_order_execution",
)


def _to_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if not text:
        return default
    return text in {"1", "true", "yes", "ok", "passed", "pass", "complete"}


def _to_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, tuple):
        return [str(item) for item in value]
    return [str(value)]


def _safe_float(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if number != number:
        return 0.0
    return number


def _safe_int(value: Any) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def _read_time(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        try:
            dt = datetime.fromisoformat(str(value))
        except Exception:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _parse_evidence_timestamp(state: dict[str, Any], now: datetime) -> bool:
    raw = state.get("evidence_timestamp", state.get("updated_at", state.get("created_at")))
    ts = _read_time(raw)
    if ts is None:
        return False
    age_hours = (now - ts).total_seconds() / 3600.0
    return age_hours <= DEFAULT_MAX_FRESHNESS_HOURS


def _proof_true(value: Any) -> bool:
    if isinstance(value, dict):
        if "status" in value:
            return str(value.get("status")).lower() in {"pass", "passed", "complete", "ready", "true", "1"}
        if "passed" in value:
            return _to_bool(value.get("passed"), default=False)
        if "value" in value:
            return bool(value.get("value"))
    if isinstance(value, str):
        return str(value).strip().lower() not in {"", "none", "false", "0", "missing"}
    return bool(value)


def _final_proof_true(value: Any) -> bool:
    if isinstance(value, dict):
        for key in ("status", "passed", "value", "present", "available", "verified", "active", "ready"):
            if key in value:
                return _to_bool(value.get(key), default=False)
        return bool(value)
    return _proof_true(value)


def _positive_number(value: Any) -> bool:
    try:
        return float(value) > 0
    except (TypeError, ValueError):
        return False


def _first_value(mapping: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in mapping and mapping.get(key) not in (None, ""):
            return mapping.get(key)
    return default


def _unknown_value(value: Any) -> bool:
    if value is None:
        return True
    if isinstance(value, str):
        text = value.strip().lower()
        return text in {"", "unknown", "missing", "none", "null", "n/a", "na", "tbd", "todo", "pending"}
    return False


def _gate_value(gate: Mapping[str, Any], field: str, default: Any = None) -> Any:
    if field in gate:
        return gate.get(field)
    for alias in ACCOUNT_PERMISSION_FIELD_ALIASES.get(field, ()):
        if alias in gate:
            return gate.get(alias)
    return default


def _supported_order_type(value: Any, expected: str = "market") -> bool:
    expected_lower = expected.lower()
    if isinstance(value, (list, tuple, set)):
        return expected_lower in {str(item).strip().lower() for item in value}
    if isinstance(value, str):
        text = value.strip().lower()
        if text in {"true", "yes", "passed", "pass", "complete"}:
            return True
        return expected_lower in {item.strip() for item in text.replace(";", ",").split(",")}
    return _to_bool(value, default=False)


def _default_final_readiness_payload() -> dict[str, Any]:
    from automation.forex_engine import candidate_intake_demo_review_bridge
    from automation.forex_engine import mitigation_optimization_t_v1

    intake = candidate_intake_demo_review_bridge.run_candidate_intake_demo_review_bridge(write_reports=False)
    mitigation = mitigation_optimization_t_v1.run_mitigation_optimization(write_reports=False)
    candidate = dict(intake.get("normalized_candidate") or {})
    optimized = dict(mitigation.get("optimized_results") or {})
    optimized_windows = [
        row for row in optimized.get("window_results", []) if isinstance(row, dict)
    ]
    passing_windows = sum(1 for row in optimized_windows if not row.get("blocker_reasons"))
    sample_size = int(candidate.get("sample_size", 0) or 0)
    return {
        "candidate": candidate,
        "paper_metrics": {
            "total_trades": sample_size,
            "closed_trades": sample_size,
            "sample_size": sample_size,
            "expectancy": candidate.get("expectancy", 0.0),
            "profit_factor": candidate.get("profit_factor", 0.0),
            "max_drawdown": candidate.get("max_drawdown", 0.0),
            "win_rate": candidate.get("win_rate", 0.0),
        },
        "walk_forward_result": {
            "windows_evaluated": len(optimized_windows),
            "passing_windows": passing_windows,
            "walk_forward_gate_cleared": bool(optimized.get("walk_forward_gate_cleared")),
        },
        "validation_results": [{"status": "PASS", "source": "candidate_intake_demo_review_bridge"}],
        "kill_switch_proof": candidate.get("kill_switch_proof"),
        "replayability_proof": candidate.get("replay_proof"),
        "broker_gate": {},
        "account_permission_gate": {},
        "risk_limits": {
            "maximum_loss": 1.0,
            "daily_loss_cap": 2.0,
            "stop_loss": 1.0,
            "take_profit": 2.0,
            "max_drawdown_limit": FINAL_DEFAULT_MAX_DRAWDOWN,
            "effective_leverage": 0.5,
            "max_effective_leverage": FINAL_DEFAULT_MAX_EFFECTIVE_LEVERAGE,
            "requested_units": FINAL_DEFAULT_LIVE_MICRO_UNITS,
            "max_live_micro_units": FINAL_DEFAULT_MAX_LIVE_MICRO_UNITS,
        },
        "one_shot_controls": {
            "one_order_only": True,
            "micro_size_only": True,
            "retry_allowed": False,
            "autonomous_reentry_allowed": False,
            "scheduler_enabled": False,
            "daemon_enabled": False,
            "webhook_enabled": False,
            "background_execution": False,
        },
        "live_exception_contracts": {},
    }


def _final_metrics(raw: Mapping[str, Any]) -> dict[str, Any]:
    candidate = _ensure_demo_candidate(dict(raw), str(raw.get("candidate_id", "c1-eur-buy")))
    paper_metrics = raw.get("paper_metrics") if isinstance(raw.get("paper_metrics"), dict) else {}
    walk_forward = raw.get("walk_forward_result")
    if not isinstance(walk_forward, dict):
        walk_forward = raw.get("walk_forward") if isinstance(raw.get("walk_forward"), dict) else {}
    sample_size = _safe_int(
        _first_value(
            paper_metrics,
            "sample_size",
            "closed_trades",
            "total_trades",
            default=_first_value(candidate, "sample_size", "closed_trade_count", default=0),
        )
    )
    return {
        "candidate_id": str(candidate.get("candidate_id", raw.get("candidate_id", "c1-eur-buy"))),
        "closed_trades": sample_size,
        "expectancy": _safe_float(_first_value(paper_metrics, "expectancy", default=candidate.get("expectancy", 0.0))),
        "profit_factor": _safe_float(_first_value(paper_metrics, "profit_factor", default=candidate.get("profit_factor", 0.0))),
        "max_drawdown": _safe_float(_first_value(paper_metrics, "max_drawdown", default=candidate.get("max_drawdown", 0.0))),
        "win_rate": _safe_float(_first_value(paper_metrics, "win_rate", default=candidate.get("win_rate", 0.0))),
        "walk_forward_status": str(
            raw.get(
                "walk_forward_status",
                candidate.get("walk_forward_status", ""),
            )
        ).strip().lower(),
        "walk_forward_windows": _safe_int(
            _first_value(walk_forward, "windows_evaluated", "total_windows", default=raw.get("walk_forward_windows", 0))
        ),
        "passing_walk_forward_windows": _safe_int(
            _first_value(walk_forward, "passing_windows", default=raw.get("passing_walk_forward_windows", 0))
        ),
        "walk_forward_gate_cleared": bool(
            walk_forward.get("walk_forward_gate_cleared", raw.get("walk_forward_gate_cleared", False))
        ),
    }


def evaluate_account_permission_gate(
    gate_payload: Mapping[str, Any] | None,
    *,
    activation_side: Any = "buy",
) -> dict[str, Any]:
    gate = gate_payload if isinstance(gate_payload, Mapping) else {}
    blockers: list[str] = []
    missing = [
        field
        for field in ACCOUNT_PERMISSION_REQUIRED_FIELDS
        if _unknown_value(_gate_value(gate, field))
    ]
    blockers.extend([f"unknown_account_permission:{field}" for field in missing])

    side_text = str(_first_value(gate, "activation_side", "side", default=activation_side)).strip().lower()
    if side_text in {"sell", "short"}:
        normalized_side = "SHORT"
    elif side_text in {"buy", "long"}:
        normalized_side = "LONG"
    else:
        normalized_side = "UNKNOWN"
        blockers.append("unknown_account_permission:activation_side")

    if not missing:
        broker_environment = str(_gate_value(gate, "broker_environment", "")).strip().lower()
        if broker_environment not in BROKER_DEMO_SANDBOX_ENVIRONMENTS:
            blockers.append("broker_environment_not_demo_or_sandbox_for_proof")
        asset_class = str(_gate_value(gate, "asset_class", "")).strip().lower()
        if asset_class not in {"forex", "fx"}:
            blockers.append("asset_class_not_forex")
        if not _to_bool(_gate_value(gate, "margin_available_confirmed"), default=False):
            blockers.append("margin_unavailable")
        if not _positive_number(_gate_value(gate, "effective_leverage_limit")):
            blockers.append("invalid_effective_leverage_limit")
        if normalized_side == "LONG" and not _to_bool(_gate_value(gate, "long_permission"), default=False):
            blockers.append("long_permission_not_granted")
        if not _to_bool(_gate_value(gate, "instrument_tradable"), default=False):
            blockers.append("instrument_not_tradable")
        if not _positive_number(_gate_value(gate, "max_units")):
            blockers.append("invalid_account_max_units")
        if not _to_bool(_gate_value(gate, "stop_loss_supported"), default=False):
            blockers.append("stop_loss_not_supported")
        if not _to_bool(_gate_value(gate, "take_profit_supported"), default=False):
            blockers.append("take_profit_not_supported")
        if not _supported_order_type(_gate_value(gate, "order_type_supported")):
            blockers.append("order_type_not_supported")
        if not _to_bool(_gate_value(gate, "one_order_only_supported"), default=False):
            blockers.append("one_order_only_not_supported")
        if not _to_bool(_gate_value(gate, "demo_sandbox_order_preview_supported"), default=False):
            blockers.append("missing_broker_demo_or_sandbox_proof")
        if not _to_bool(_gate_value(gate, "sanitized_evidence_only"), default=False):
            blockers.append("broker_permission_evidence_not_sanitized")
        if _read_time(_gate_value(gate, "proof_timestamp")) is None:
            blockers.append("invalid_broker_permission_proof_timestamp")
        restrictions = {item.strip().lower() for item in _to_list(_gate_value(gate, "broker_house_restrictions"))}
        blocking_restrictions = {
            "trading_blocked",
            "orders_blocked",
            "forex_blocked",
            "instrument_blocked",
            "no_forex",
            "no_live_trading",
        }
        if restrictions.intersection(blocking_restrictions):
            blockers.append("broker_house_restriction_blocks_trade")
        if normalized_side == "SHORT" and not _to_bool(_gate_value(gate, "short_permission"), default=False):
            blockers.append("short_permission_not_granted")

    blockers = list(dict.fromkeys(blockers))
    short_allowed = _to_bool(_gate_value(gate, "short_permission"), default=False) and not blockers
    long_allowed = normalized_side == "LONG" and not blockers
    permission_summary = {
        field: _gate_value(gate, field)
        for field in ACCOUNT_PERMISSION_REQUIRED_FIELDS
        if not _unknown_value(_gate_value(gate, field))
    }
    return {
        "gate": ACCOUNT_PERMISSION_GATE,
        "status": ACCOUNT_PERMISSION_GATE_CLEARED if not blockers else BLOCKED_BY_BROKER_GATE,
        "cleared": not blockers,
        "blockers": blockers,
        "activation_side": normalized_side,
        "long_only_status": "LONG_ONLY_ALLOWED" if long_allowed else BLOCKED_BY_BROKER_GATE,
        "short_side_status": "SHORT_SIDE_ALLOWED" if short_allowed else BLOCKED_BY_BROKER_GATE,
        "permission_summary": permission_summary,
    }


def evaluate_live_exception_evidence_bundle(contracts: Mapping[str, Any] | None) -> dict[str, Any]:
    contracts = contracts if isinstance(contracts, Mapping) else {}
    bundle = contracts.get("evidence_bundle") if isinstance(contracts.get("evidence_bundle"), Mapping) else {}
    arming_state = contracts.get("arming_state") if isinstance(contracts.get("arming_state"), Mapping) else {}
    approval = contracts.get("approval") if isinstance(contracts.get("approval"), Mapping) else {}
    request = contracts.get("request") if isinstance(contracts.get("request"), Mapping) else {}

    risk_blockers: list[str] = []
    broker_blockers: list[str] = []
    policy_blockers: list[str] = []

    if not bundle:
        broker_blockers.append("missing_live_exception_evidence_bundle_contract")
    if not request:
        policy_blockers.append("missing_owner_live_exception_request")
    if not approval:
        policy_blockers.append("missing_owner_approval")
    if not arming_state:
        policy_blockers.append("missing_live_exception_arming_state_contract")

    if bundle:
        if not _to_bool(bundle.get("owner_live_exception_request"), default=False):
            policy_blockers.append("missing_owner_live_exception_request")
        if not _to_bool(bundle.get("owner_approval_required"), default=False):
            policy_blockers.append("missing_owner_approval_required")
        if not _to_bool(bundle.get("owner_approval_present"), default=False):
            policy_blockers.append("missing_owner_approval")
        if _read_time(bundle.get("arming_timestamp")) is None:
            policy_blockers.append("missing_arming_timestamp")
        for field in LIVE_EXCEPTION_RISK_CONFIRMATIONS:
            if not _to_bool(bundle.get(field), default=False):
                risk_blockers.append(f"missing_live_exception_{field}")
        if not _to_bool(bundle.get("sanitized_evidence_only"), default=False):
            broker_blockers.append("live_exception_bundle_not_sanitized")
        for field in LIVE_EXCEPTION_NO_ACTION_PROOFS:
            if not _to_bool(bundle.get(field), default=False):
                broker_blockers.append(f"missing_live_exception_{field}_proof")
        for field in ("scheduler_enabled", "daemon_enabled", "webhook_enabled", "background_execution"):
            if _to_bool(bundle.get(field), default=False):
                policy_blockers.append(f"live_exception_{field}_not_allowed")
        for field in (
            "credential_read",
            "credential_write",
            "env_read",
            "env_write",
            "account_id_read",
            "account_id_write",
            "network_call",
            "broker_mutation",
            "live_order_execution",
        ):
            if _to_bool(bundle.get(field), default=False):
                broker_blockers.append(f"live_exception_{field}_detected")

    return {
        "cleared": not risk_blockers and not broker_blockers and not policy_blockers,
        "risk_blockers": list(dict.fromkeys(risk_blockers)),
        "broker_blockers": list(dict.fromkeys(broker_blockers)),
        "policy_blockers": list(dict.fromkeys(policy_blockers)),
        "summary": {
            "owner_live_exception_request": _to_bool(bundle.get("owner_live_exception_request"), default=False),
            "owner_approval_required": _to_bool(bundle.get("owner_approval_required"), default=False),
            "owner_approval_present": _to_bool(bundle.get("owner_approval_present"), default=False),
            "arming_timestamp_present": _read_time(bundle.get("arming_timestamp")) is not None,
            "risk_confirmations": {
                field: _to_bool(bundle.get(field), default=False) for field in LIVE_EXCEPTION_RISK_CONFIRMATIONS
            },
            "no_action_proofs": {
                field: _to_bool(bundle.get(field), default=False) for field in LIVE_EXCEPTION_NO_ACTION_PROOFS
            },
        },
    }


def _validate_live_exception_contracts(contracts: Mapping[str, Any]) -> dict[str, list[str]]:
    if not isinstance(contracts, Mapping):
        contracts = {}
    from automation.forex_engine import live_micro_trade_contract

    broker_blockers: list[str] = []
    policy_blockers: list[str] = []
    risk_blockers: list[str] = []
    validators = (
        ("request", live_micro_trade_contract.validate_micro_trade_request, policy_blockers),
        ("approval", live_micro_trade_contract.validate_micro_trade_approval, policy_blockers),
        ("evidence_bundle", live_micro_trade_contract.validate_evidence_bundle, broker_blockers),
        ("arming_state", live_micro_trade_contract.validate_arming_state, policy_blockers),
    )
    for key, validator, blockers in validators:
        if key not in contracts:
            blockers.append(f"missing_live_exception_{key}_contract")
            continue
        try:
            validator(contracts.get(key))
        except live_micro_trade_contract.ContractValidationError as exc:
            blockers.append(f"invalid_live_exception_{key}:{exc.code}")
        if key in {"request", "approval"}:
            contract = contracts.get(key) if isinstance(contracts.get(key), Mapping) else {}
            if not _positive_number(contract.get("take_profit")):
                risk_blockers.append(f"missing_live_exception_{key}_take_profit")
    return {
        "broker_blockers": broker_blockers,
        "policy_blockers": policy_blockers,
        "risk_blockers": risk_blockers,
    }


def build_profitable_live_bot_final_status(
    *,
    evidence_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    raw: dict[str, Any] = dict(evidence_payload or _default_final_readiness_payload())
    metrics = _final_metrics(raw)
    risk_limits = raw.get("risk_limits") if isinstance(raw.get("risk_limits"), dict) else {}
    broker_gate = raw.get("broker_gate") if isinstance(raw.get("broker_gate"), dict) else {}
    controls = raw.get("micro_trade_constraints")
    if not isinstance(controls, dict):
        controls = raw.get("one_shot_controls") if isinstance(raw.get("one_shot_controls"), dict) else {}
    candidate = raw.get("candidate") if isinstance(raw.get("candidate"), dict) else {}
    account_permission_gate = evaluate_account_permission_gate(
        raw.get("account_permission_gate") if isinstance(raw.get("account_permission_gate"), Mapping) else {},
        activation_side=_first_value(candidate, "direction", "side", default=raw.get("side", "buy")),
    )

    evidence_blockers: list[str] = []
    risk_blockers: list[str] = []
    broker_blockers: list[str] = []
    policy_blockers: list[str] = []

    if metrics["closed_trades"] < FINAL_MIN_CLOSED_TRADES:
        evidence_blockers.append("insufficient_sample")
    if metrics["walk_forward_windows"] < FINAL_MIN_WALK_FORWARD_WINDOWS:
        evidence_blockers.append("insufficient_walk_forward_windows")
    if metrics["passing_walk_forward_windows"] < FINAL_MIN_WALK_FORWARD_WINDOWS:
        evidence_blockers.append("insufficient_passing_walk_forward_windows")
    if (
        metrics["walk_forward_status"] not in {"pass", "passed", "ready", "complete"}
        or not metrics["walk_forward_gate_cleared"]
    ):
        evidence_blockers.append("walk_forward_not_cleared")

    max_drawdown_limit = _safe_float(
        _first_value(risk_limits, "max_drawdown_limit", "max_drawdown", default=FINAL_DEFAULT_MAX_DRAWDOWN)
    )
    if metrics["expectancy"] <= 0:
        risk_blockers.append("non_positive_expectancy")
    if metrics["profit_factor"] <= FINAL_MIN_PROFIT_FACTOR:
        risk_blockers.append("profit_factor_not_above_1_20")
    if metrics["max_drawdown"] > max_drawdown_limit:
        risk_blockers.append("drawdown_exceeds_risk_cap")

    if not _positive_number(_first_value(risk_limits, "maximum_loss", "max_loss")):
        risk_blockers.append("missing_max_loss_cap")
    if not _positive_number(_first_value(risk_limits, "daily_stop", "daily_stop_cap", "daily_loss_cap")):
        risk_blockers.append("missing_daily_stop_cap")
    if not _positive_number(_first_value(risk_limits, "stop_loss", "stop_loss_price", "stop_loss_limit")):
        risk_blockers.append("missing_stop_loss")
    if not _positive_number(_first_value(risk_limits, "take_profit", "take_profit_price", "take_profit_limit")):
        risk_blockers.append("missing_take_profit")
    effective_leverage = _safe_float(_first_value(risk_limits, "effective_leverage", default=None))
    max_effective_leverage = _safe_float(
        _first_value(risk_limits, "max_effective_leverage", default=FINAL_DEFAULT_MAX_EFFECTIVE_LEVERAGE)
    )
    if not _positive_number(effective_leverage) or not _positive_number(max_effective_leverage):
        risk_blockers.append("missing_low_effective_leverage_guard")
    elif effective_leverage > max_effective_leverage:
        risk_blockers.append("effective_leverage_above_low_guard")
    requested_units = _safe_int(_first_value(risk_limits, "requested_units", "units", default=0))
    max_live_micro_units = _safe_int(
        _first_value(risk_limits, "max_live_micro_units", "max_units", default=FINAL_DEFAULT_MAX_LIVE_MICRO_UNITS)
    )
    if requested_units <= 0 or max_live_micro_units <= 0 or requested_units > max_live_micro_units:
        risk_blockers.append("micro_size_units_not_within_guard")
    if not _final_proof_true(raw.get("kill_switch_proof")):
        risk_blockers.append("missing_kill_switch")
    if not _to_bool(_first_value(controls, "one_order_only", "single_order_only"), default=False):
        risk_blockers.append("missing_one_order_only_constraint")
    if not _to_bool(_first_value(controls, "micro_size_only", default=True), default=True):
        risk_blockers.append("missing_micro_size_only_constraint")
    if _to_bool(_first_value(controls, "retry_allowed", "retry_loop_detected"), default=False):
        risk_blockers.append("retry_loop_not_allowed")
    if _to_bool(_first_value(controls, "autonomous_reentry_allowed", "autonomous_reentry_detected"), default=False):
        risk_blockers.append("autonomous_reentry_not_allowed")
    for field in ("scheduler_enabled", "daemon_enabled", "webhook_enabled", "background_execution"):
        if _to_bool(_first_value(controls, field), default=False):
            policy_blockers.append(f"{field}_not_allowed")

    broker_demo_proof = _first_value(
        broker_gate,
        "broker_sandbox_or_demo_proof",
        "broker_demo_or_sandbox_proof",
        default=account_permission_gate["permission_summary"].get("demo_sandbox_order_preview_supported"),
    )
    if not _final_proof_true(broker_demo_proof):
        broker_blockers.append("missing_broker_demo_or_sandbox_proof")
    if _to_bool(_first_value(broker_gate, "broker_mutation", "broker_call_performed"), default=False):
        broker_blockers.append("broker_mutation_detected")
    if _to_bool(_first_value(broker_gate, "credentials_persisted"), default=False):
        broker_blockers.append("credentials_persisted")
    if _to_bool(_first_value(broker_gate, "account_id_persisted"), default=False):
        broker_blockers.append("account_id_persisted")
    broker_blockers.extend(account_permission_gate["blockers"])

    contract_result = _validate_live_exception_contracts(raw.get("live_exception_contracts", {}))
    evidence_bundle_result = evaluate_live_exception_evidence_bundle(raw.get("live_exception_contracts", {}))
    risk_blockers.extend(contract_result["risk_blockers"])
    risk_blockers.extend(evidence_bundle_result["risk_blockers"])
    broker_blockers.extend(contract_result["broker_blockers"])
    broker_blockers.extend(evidence_bundle_result["broker_blockers"])
    policy_blockers.extend(contract_result["policy_blockers"])
    policy_blockers.extend(evidence_bundle_result["policy_blockers"])

    evidence_blockers = list(dict.fromkeys(evidence_blockers))
    risk_blockers = list(dict.fromkeys(risk_blockers))
    broker_blockers = list(dict.fromkeys(broker_blockers))
    policy_blockers = list(dict.fromkeys(policy_blockers))

    if evidence_blockers:
        status = REQUIRE_MORE_EVIDENCE
    elif risk_blockers:
        status = BLOCKED_BY_RISK
    elif broker_blockers:
        status = BLOCKED_BY_BROKER_GATE
    elif policy_blockers:
        status = BLOCKED_BY_POLICY
    else:
        status = PROFITABLE_LIVE_BOT_READY

    return {
        "status": status,
        "candidate_id": metrics["candidate_id"],
        "metrics": metrics,
        "thresholds": {
            "min_closed_trades": FINAL_MIN_CLOSED_TRADES,
            "min_walk_forward_windows": FINAL_MIN_WALK_FORWARD_WINDOWS,
            "min_profit_factor_exclusive": FINAL_MIN_PROFIT_FACTOR,
            "max_drawdown": max_drawdown_limit,
            "max_effective_leverage": max_effective_leverage,
            "max_live_micro_units": max_live_micro_units,
        },
        "evidence_gate_cleared": not evidence_blockers,
        "risk_gate_cleared": not risk_blockers,
        "broker_gate_cleared": not broker_blockers,
        "policy_gate_cleared": not policy_blockers,
        "live_for_keeps_ready": status == PROFITABLE_LIVE_BOT_READY,
        "risk_contract_summary": {
            "maximum_loss": _safe_float(_first_value(risk_limits, "maximum_loss", "max_loss", default=0.0)),
            "daily_loss_cap": _safe_float(_first_value(risk_limits, "daily_stop", "daily_stop_cap", "daily_loss_cap", default=0.0)),
            "stop_loss": _safe_float(_first_value(risk_limits, "stop_loss", "stop_loss_price", "stop_loss_limit", default=0.0)),
            "take_profit": _safe_float(_first_value(risk_limits, "take_profit", "take_profit_price", "take_profit_limit", default=0.0)),
            "effective_leverage": effective_leverage,
            "max_effective_leverage": max_effective_leverage,
            "low_effective_leverage_guard": bool(
                _positive_number(effective_leverage)
                and _positive_number(max_effective_leverage)
                and effective_leverage <= max_effective_leverage
            ),
            "requested_units": requested_units,
            "max_live_micro_units": max_live_micro_units,
            "one_order_only": _to_bool(_first_value(controls, "one_order_only", "single_order_only"), default=False),
            "micro_size_only": _to_bool(_first_value(controls, "micro_size_only", default=True), default=True),
            "no_scheduler_daemon_webhook_background": not any(
                _to_bool(_first_value(controls, field), default=False)
                for field in ("scheduler_enabled", "daemon_enabled", "webhook_enabled", "background_execution")
            ),
        },
        "account_permission_gate": account_permission_gate,
        "long_only_status": account_permission_gate["long_only_status"],
        "short_side_status": account_permission_gate["short_side_status"],
        "broker_gate_summary": {
            "broker_demo_or_sandbox_proof": _final_proof_true(broker_demo_proof),
            "broker_mutation": _to_bool(_first_value(broker_gate, "broker_mutation", "broker_call_performed"), default=False),
            "credentials_persisted": _to_bool(_first_value(broker_gate, "credentials_persisted"), default=False),
            "account_id_persisted": _to_bool(_first_value(broker_gate, "account_id_persisted"), default=False),
            "account_permission_gate": account_permission_gate["status"],
            "broker_environment": account_permission_gate["permission_summary"].get("broker_environment", "UNKNOWN"),
            "account_currency": account_permission_gate["permission_summary"].get("account_currency", "UNKNOWN"),
            "margin_available_confirmed": account_permission_gate["permission_summary"].get("margin_available_confirmed", "UNKNOWN"),
            "effective_leverage_limit": account_permission_gate["permission_summary"].get("effective_leverage_limit", "UNKNOWN"),
        },
        "live_exception_status": {
            "contracts_present": sorted(raw.get("live_exception_contracts", {}).keys())
            if isinstance(raw.get("live_exception_contracts"), Mapping)
            else [],
            "request_contract_present": isinstance(raw.get("live_exception_contracts"), Mapping)
            and "request" in raw.get("live_exception_contracts", {}),
            "approval_contract_present": isinstance(raw.get("live_exception_contracts"), Mapping)
            and "approval" in raw.get("live_exception_contracts", {}),
            "arming_contract_present": isinstance(raw.get("live_exception_contracts"), Mapping)
            and "arming_state" in raw.get("live_exception_contracts", {}),
            "evidence_bundle_contract_present": isinstance(raw.get("live_exception_contracts"), Mapping)
            and "evidence_bundle" in raw.get("live_exception_contracts", {}),
            "evidence_bundle_cleared": evidence_bundle_result["cleared"],
            "evidence_bundle_summary": evidence_bundle_result["summary"],
        },
        "blockers": {
            "evidence": evidence_blockers,
            "risk": risk_blockers,
            "broker": broker_blockers,
            "policy": policy_blockers,
        },
        "next_safe_action": (
            "stop_before_live_execution_and_request_owner_review"
            if status == PROFITABLE_LIVE_BOT_READY
            else "resolve_" + status.lower()
        ),
        "safety": _safety_defaults(),
        "mode": "PROFITABLE_LIVE_FOREX_BOT_FINAL_STATUS_V1",
    }


def _approval_ready(approval_trace: dict[str, Any] | None) -> bool:
    if not isinstance(approval_trace, dict) or not approval_trace:
        return False
    return (
        _to_bool(approval_trace.get("signed"), default=False)
        or _to_bool(approval_trace.get("approved"), default=False)
        or _to_bool(approval_trace.get("human_review_ready"), default=False)
        or "reviewed_by" in approval_trace
    )


def _ensure_demo_candidate(state: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    candidate = state.get("candidate")
    if not isinstance(candidate, dict):
        candidate = {}
    if not candidate and state.get("normalized_candidate"):
        candidate = state.get("normalized_candidate") or {}
    if not isinstance(candidate, dict):
        candidate = {}
    if not candidate.get("candidate_id"):
        candidate["candidate_id"] = candidate_id
    return candidate


def _safety_defaults() -> dict[str, bool]:
    return {
        "paper_only": True,
        "broker_connected": False,
        "credentials_used": False,
        "account_id_present": False,
        "network_used": False,
        "order_execution": False,
        "broker_mutation": False,
        "credential_read": False,
        "credential_write": False,
        "env_read": False,
        "account_id_read": False,
        "account_id_write": False,
        "demo_trading": False,
        "live_trading": False,
        "live_trading_authorized": False,
        "scheduler": False,
        "daemon": False,
        "webhook": False,
        "background_execution": False,
    }


@dataclass
class _EvidenceContract:
    candidate_id: str
    strategy_name: str
    symbol: str
    direction: str
    walk_forward_status: str
    mitigation_status: str
    candidate_approved_for_demo_validation: bool
    validation_results: list[dict[str, Any]]
    paper_metrics: dict[str, Any]
    demo_validation_contract: dict[str, Any]
    live_readiness_candidate: dict[str, Any]
    approval_trace: dict[str, Any]
    risk_limits: dict[str, Any]
    kill_switch_proof: Any
    rollback_proof: Any
    reconciliation_proof: Any
    evidence_timestamp: Any
    replayability_proof: Any
    final_disarm_proof: Any
    post_trade_journal_path: str | None
    one_shot_exception_package: dict[str, Any]
    live_review_certificate: dict[str, Any]
    human_review_ready: bool


def _normalise(raw: dict[str, Any], candidate_id: str) -> _EvidenceContract:
    candidate = _ensure_demo_candidate(raw, candidate_id)
    paper_metrics = raw.get("paper_metrics", {})
    if not isinstance(paper_metrics, dict):
        paper_metrics = {}
    return _EvidenceContract(
        candidate_id=str(candidate.get("candidate_id", candidate_id)),
        strategy_name=str(candidate.get("strategy", candidate.get("strategy_name", ""))),
        symbol=str(candidate.get("pair", candidate.get("symbol", ""))),
        direction=str(candidate.get("direction", "")),
        walk_forward_status=str(candidate.get("walk_forward_status", raw.get("walk_forward_status", ""))),
        mitigation_status=str(candidate.get("mitigation_status", candidate.get("mitigation", ""))).strip().lower(),
        candidate_approved_for_demo_validation=_to_bool(
            raw.get(
                "approved_for_demo_validation",
                raw.get("candidate_approved", raw.get("candidate_approved_for_demo_validation")),
            ),
            default=False,
        ) or _to_bool(candidate.get("approved_for_demo_validation"), default=False),
        validation_results=_to_list(raw.get("validation_results")),
        paper_metrics=paper_metrics,
        demo_validation_contract=raw.get("demo_validation_contract", {}) if isinstance(raw.get("demo_validation_contract", {}), dict) else {},
        live_readiness_candidate=raw.get("live_readiness_candidate", {}) if isinstance(raw.get("live_readiness_candidate", {}), dict) else {},
        approval_trace=raw.get("approval_trace", {}) if isinstance(raw.get("approval_trace", {}), dict) else {},
        risk_limits=raw.get("risk_limits", {}) if isinstance(raw.get("risk_limits", {}), dict) else {},
        kill_switch_proof=raw.get("kill_switch_proof"),
        rollback_proof=raw.get("rollback_proof"),
        reconciliation_proof=raw.get("reconciliation_proof"),
        evidence_timestamp=raw.get("evidence_timestamp"),
        replayability_proof=raw.get("replayability_proof"),
        final_disarm_proof=raw.get("final_disarm_proof"),
        post_trade_journal_path=raw.get("post_trade_journal_path"),
        one_shot_exception_package=raw.get("one_shot_exception_package", {}) if isinstance(raw.get("one_shot_exception_package", {}), dict) else {},
        live_review_certificate=raw.get("live_review_certificate", {}) if isinstance(raw.get("live_review_certificate", {}), dict) else {},
        human_review_ready=_to_bool(raw.get("human_review_ready"), default=False),
    )


def _collect_blocker_details(
    candidate: _EvidenceContract,
    evidence_fresh: bool,
    now: datetime,
) -> dict[str, list[str]]:
    details: dict[str, list[str]] = {}
    if candidate.walk_forward_status.strip().lower() in {"failed", "fail", "failed_walk_forward"}:
        details["walk_forward_failed"] = ["Walk-forward status indicates failed."]
    paper_metrics = candidate.paper_metrics
    total_trades = paper_metrics.get("total_trades")
    closed_trades = paper_metrics.get("closed_trades")
    expectancy = paper_metrics.get("expectancy")
    profit_factor = paper_metrics.get("profit_factor")
    max_drawdown = paper_metrics.get("max_drawdown")
    sample_size = paper_metrics.get("sample_size", paper_metrics.get("closed_trades"))
    if (
        total_trades in (None, "")
        or closed_trades in (None, "")
        or expectancy in (None, "")
        or profit_factor in (None, "")
        or max_drawdown in (None, "")
        or sample_size in (None, "")
        or not candidate.validation_results
    ):
        details.setdefault("paper_evidence_not_ready", []).append("Missing required paper metrics.")
    else:
        try:
            total_trades_i = int(total_trades)
            sample_size_i = int(sample_size)
            expectancy_f = float(expectancy)
            pf = float(profit_factor)
            drawdown_f = float(max_drawdown)
        except (TypeError, ValueError):
            details.setdefault("paper_evidence_not_ready", []).append(
                "Paper metrics cannot be converted to required numeric ranges."
            )
        else:
            if total_trades_i <= 0:
                details.setdefault("paper_evidence_not_ready", []).append("Closed trades must be positive.")
            if expectancy_f <= DEFAULT_MAX_EXPECTANCY:
                details.setdefault("paper_evidence_not_ready", []).append("Expectancy must be positive.")
            if pf <= DEFAULT_MIN_PROFIT_FACTOR:
                details.setdefault("paper_evidence_not_ready", []).append("Profit factor must exceed 1.")
            if sample_size_i < DEFAULT_MIN_SAMPLE_SIZE:
                details.setdefault("paper_evidence_not_ready", []).append("Sample size below minimum threshold.")

    if candidate.human_review_ready is False:
        details["missing_human_review_ready"] = ["human_review_ready flag not true."]

    if candidate.replayability_proof is None or not _proof_true(candidate.replayability_proof):
        details["missing_replayability_proof"] = ["Replayability proof not present or stale."]

    if not evidence_fresh:
        details["missing_evidence_freshness"] = ["Freshness proof cannot be established."]

    if not candidate.validation_results:
        details["missing_validation_results"] = ["No validation results payload available."]

    if not _approval_ready(candidate.approval_trace):
        details["missing_approval_trace"] = ["Approval trace missing."]

    risk_limits = candidate.risk_limits
    if not isinstance(risk_limits, dict) or not risk_limits:
        details["missing_risk_limits"] = ["Risk limits record missing."]
    else:
        max_drawdown_limit = risk_limits.get("max_drawdown_limit", risk_limits.get("max_drawdown"))
        if max_drawdown_limit not in (None, ""):
            try:
                drawdown_limit = float(max_drawdown_limit)
            except (TypeError, ValueError):
                drawdown_limit = None
            else:
                try:
                    drawdown_f = float(candidate.paper_metrics.get("max_drawdown", 0.0))
                except (TypeError, ValueError):
                    drawdown_f = None
                if drawdown_f is not None and drawdown_f > drawdown_limit:
                    details["paper_evidence_not_ready"] = details.get("paper_evidence_not_ready", [])
                    details["paper_evidence_not_ready"].append("Drawdown exceeds configured risk limits.")

        else:
            details.setdefault("missing_risk_limits", []).append("Risk limit fields incomplete.")

    if candidate.mitigation_status == "worsened":
        details.setdefault("mitigation_worsened", []).append("Mitigation has worsened metrics.")

    if not candidate.live_readiness_candidate:
        details["missing_live_readiness_candidate"] = ["No live readiness candidate artifact."]
    elif not _to_bool(
        candidate.live_readiness_candidate.get("live_readiness_candidate", candidate.live_readiness_candidate.get("live_ready")),
        default=False,
    ):
        details["missing_live_readiness_candidate"] = ["No explicit live readiness candidate record."]

    contract = candidate.demo_validation_contract
    contract_complete = _proof_true(contract.get("demo_validation_contract_completed")) if isinstance(contract, dict) else False
    contract_status = str(contract.get("status", "")).lower() if isinstance(contract, dict) else ""
    if not contract or not contract_complete and contract_status not in {"complete", "approved", "ready", "passed"}:
        details["demo_contract_not_complete"] = ["Demo validation contract incomplete."]
        details["demo_validation_contract_not_complete"] = ["Demo validation contract incomplete."]

    if not candidate.candidate_approved_for_demo_validation:
        details["candidate_not_approved_for_demo_validation"] = [
            "Candidate approval marker not present."
        ]

    if not _proof_true(candidate.kill_switch_proof):
        details["missing_kill_switch_proof"] = ["Kill switch proof missing."]
    if not _proof_true(candidate.rollback_proof):
        details["missing_rollback_proof"] = ["Rollback proof missing."]
    if not _proof_true(candidate.reconciliation_proof):
        details["missing_reconciliation_proof"] = ["Reconciliation proof missing."]

    if not candidate.post_trade_journal_path:
        details["missing_post_trade_journal_path"] = ["post_trade_journal_path missing."]

    if not candidate.final_disarm_proof:
        details["missing_final_disarm_proof"] = ["Final disarm proof missing."]

    if not _to_bool(candidate.one_shot_exception_package.get("exception_package_completed"), default=False):
        details["one_shot_exception_package_not_review_ready"] = [
            "One-shot package not review ready."
        ]

    if not _to_bool(candidate.live_review_certificate.get("certificate_completed"), default=False):
        details["live_review_certificate_not_review_ready"] = [
            "Live review certificate not review ready."
        ]

    if not details:
        details = {}
    return details


def run_consolidated_readiness_blocker_closure_v1(
    candidate_id: str = "c1-eur-buy",
    *,
    evidence_payload: dict[str, Any] | None = None,
    proof_bundle_payload: dict[str, Any] | None = None,
    evidence_path: str | None = None,
    write_reports: bool = True,
) -> dict[str, Any]:
    if evidence_path:
        raw: dict[str, Any] = {}
        try:
            raw = json.loads(Path(evidence_path).read_text(encoding="utf-8"))
        except Exception:
            raw = {}
    else:
        raw = evidence_payload or {}

    if not raw:
        if proof_bundle_payload is not None:
            raw = proof_bundle_payload
        else:
            raw = run_proof_bundle_to_candidate_bridge(write_reports=False)

    evidence = _normalise(raw or {}, candidate_id)

    now = datetime.now(timezone.utc)
    evidence_fresh = _parse_evidence_timestamp(raw or {}, now)

    blocker_details = _collect_blocker_details(evidence, evidence_fresh, now)
    unresolved = [name for name in CANONICAL_BLOCKERS if blocker_details.get(name)]
    # remove duplicate literal entry
    unresolved = list(dict.fromkeys([b for b in unresolved if b]))

    resolved = [b for b in CANONICAL_BLOCKERS if b not in unresolved]

    ready_for_demo_validation = (
        "walk_forward_failed" not in unresolved
        and "paper_evidence_not_ready" not in unresolved
        and "missing_validation_results" not in unresolved
        and "candidate_not_approved_for_demo_validation" not in unresolved
        and "demo_contract_not_complete" not in unresolved
        and "demo_validation_contract_not_complete" not in unresolved
    )

    live_readiness_requirements = {
        "missing_live_readiness_candidate",
        "missing_approval_trace",
        "missing_risk_limits",
        "missing_kill_switch_proof",
        "missing_rollback_proof",
        "missing_reconciliation_proof",
        "missing_replayability_proof",
        "missing_final_disarm_proof",
        "missing_post_trade_journal_path",
        "one_shot_exception_package_not_review_ready",
        "live_review_certificate_not_review_ready",
        "missing_human_review_ready",
    }
    ready_for_live_review = ready_for_demo_validation and not (
        any(item in unresolved for item in live_readiness_requirements)
    )

    safety = _safety_defaults()
    safety.update(
        {
            "paper_only": True,
            "broker_connected": False,
            "credentials_used": False,
            "account_id_present": False,
            "network_used": False,
            "order_execution": False,
            "demo_trading": False,
            "live_trading": False,
            "live_trading_authorized": False,
        }
    )

    status = "READY" if not unresolved else "BLOCKED"
    decision = "advance" if status == "READY" else "blocked"
    next_safe_action = unresolved[0] if unresolved else "candidate_promo_recommended"

    result: dict[str, Any] = {
        "status": status,
        "decision": decision,
        "ready_for_demo_validation": bool(ready_for_demo_validation),
        "ready_for_live_review": bool(ready_for_live_review),
        "blockers": resolved + unresolved,
        "resolved_blockers": resolved,
        "unresolved_blockers": unresolved,
        "blocker_details": blocker_details,
        "required_evidence": {name: _required_fields_for_blocker(name) for name in unresolved},
        "approval_trace": evidence.approval_trace,
        "risk_limits": evidence.risk_limits,
        "kill_switch_proof": evidence.kill_switch_proof,
        "rollback_proof": evidence.rollback_proof,
        "reconciliation_proof": evidence.reconciliation_proof,
        "evidence_freshness": {"fresh": evidence_fresh},
        "replayability_proof": evidence.replayability_proof,
        "final_disarm_proof": evidence.final_disarm_proof,
        "post_trade_journal_path": evidence.post_trade_journal_path,
        "human_review_ready": bool(evidence.human_review_ready),
        "next_safe_action": str(next_safe_action),
        "packet_id": PACKET_ID,
        "mode": "LOCAL_APPLY",
        "safety": safety,
        "candidate_id": evidence.candidate_id,
        "strategy_name": evidence.strategy_name,
        "symbol": evidence.symbol,
        "direction": evidence.direction,
        "walk_forward_status": evidence.walk_forward_status,
        "validation_results": evidence.validation_results,
    }

    if write_reports:
        result["report_path"] = _write_report(result)
    return result


def _required_fields_for_blocker(blocker: str) -> list[str]:
    mapping = {
        "walk_forward_failed": ["walk_forward_status"],
        "paper_evidence_not_ready": ["paper_metrics.total_trades", "paper_metrics.expectancy", "paper_metrics.profit_factor", "paper_metrics.max_drawdown"],
        "mitigation_worsened": ["mitigation_status"],
        "missing_validation_results": ["validation_results"],
        "candidate_not_approved_for_demo_validation": ["candidate_approved", "approved_for_demo_validation"],
        "demo_contract_not_complete": ["demo_validation_contract"],
        "missing_live_readiness_candidate": ["live_readiness_candidate"],
        "missing_approval_trace": ["approval_trace.signed", "approval_trace.reviewed_by"],
        "missing_risk_limits": ["risk_limits"],
        "missing_kill_switch_proof": ["kill_switch_proof"],
        "missing_rollback_proof": ["rollback_proof"],
        "missing_reconciliation_proof": ["reconciliation_proof"],
        "missing_evidence_freshness": ["evidence_timestamp"],
        "missing_replayability_proof": ["replayability_proof"],
        "missing_final_disarm_proof": ["final_disarm_proof"],
        "missing_post_trade_journal_path": ["post_trade_journal_path"],
        "demo_validation_contract_not_complete": ["demo_validation_contract"],
        "one_shot_exception_package_not_review_ready": ["one_shot_exception_package.exception_package_completed"],
        "live_review_certificate_not_review_ready": ["live_review_certificate.certificate_completed"],
        "missing_human_review_ready": ["human_review_ready"],
    }
    return mapping.get(blocker, ["evidence_field"])


def _write_report(payload: dict[str, Any]) -> str:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = [
        "# AIOS FOREX Consolidated Readiness Blocker Closure V1",
        "",
        f"- candidate_id: {payload.get('candidate_id')}",
        f"- status: {payload.get('status')}",
        f"- ready_for_demo_validation: {payload.get('ready_for_demo_validation')}",
        f"- ready_for_live_review: {payload.get('ready_for_live_review')}",
        "",
        "## Resolved blockers",
        "- " + ", ".join(payload.get("resolved_blockers", [])),
        "",
        "## Unresolved blockers",
        "- " + ", ".join(payload.get("unresolved_blockers", [])),
    ]
    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")
    return str(REPORT_PATH)


def main() -> dict[str, Any]:  # pragma: no cover
    return run_consolidated_readiness_blocker_closure_v1(write_reports=True)


if __name__ == "__main__":  # pragma: no cover
    print(main())
