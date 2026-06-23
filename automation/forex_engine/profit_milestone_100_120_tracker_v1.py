"""Read-only 100% to 120% profit milestone tracker."""

from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-100-120-PROFIT-MILESTONE-FIRST-V1"

TARGET_NOT_PROVEN = "TARGET_NOT_PROVEN"
TARGET_BLOCKED_BY_EVIDENCE = "TARGET_BLOCKED_BY_EVIDENCE"
TARGET_BLOCKED_BY_BROKER = "TARGET_BLOCKED_BY_BROKER"
TARGET_BLOCKED_BY_RISK = "TARGET_BLOCKED_BY_RISK"
TARGET_READY_FOR_OWNER_REVIEW = "TARGET_READY_FOR_OWNER_REVIEW"

DEFAULT_TARGET_MIN = 100.0
DEFAULT_TARGET_MAX = 120.0


SENSITIVE_MARKERS = (
    "api_key",
    "token",
    "secret",
    "password",
    "credential",
    "authorization",
    "bearer",
    "account_id",
    "accountid",
    "account-number",
    "account_number",
    "accountnumber",
    "sk-",
)


def _to_float(value: Any) -> float | None:
    try:
        if value is None:
            return None
        value_float = float(value)
    except (TypeError, ValueError):
        return None
    if value_float != value_float or value_float in (float("inf"), float("-inf")):
        return None
    return value_float


def _to_int(value: Any) -> int | None:
    try:
        if value is None:
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _safe_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip().lower() in {"true", "1", "yes", "on", "y"}
    return bool(value)


def _string(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _contains_sensitive(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, Mapping):
        return any(_contains_sensitive(item) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return any(_contains_sensitive(item) for item in value)
    lowered = str(value).lower()
    return any(marker in lowered for marker in SENSITIVE_MARKERS)


def _compute_return_percent(starting_balance: float | None, current_balance: float | None) -> float | None:
    if starting_balance is None or current_balance is None:
        return None
    if starting_balance <= 0:
        return None
    return round((current_balance - starting_balance) / starting_balance * 100.0, 6)


def _build_status(
    status: str,
    *,
    blockers: list[str],
    current_return_percent: float | None,
    candidate: Mapping[str, Any] | None,
) -> dict[str, Any]:
    candidate = candidate or {}
    sample_size = _to_int(candidate.get("sample_size"))
    open_trades = _to_int(candidate.get("open_trades"))
    closed_trades = _to_int(candidate.get("closed_trades"))
    current_return_source = _string(candidate.get("current_return_source"), "MISSING")
    broker_readiness_status = _string(candidate.get("broker_readiness_status"), "MISSING")
    risk_gate_status = _string(candidate.get("risk_gate_status"), "MISSING")

    if status == TARGET_READY_FOR_OWNER_REVIEW:
        next_safe_action = (
            "Evidence is within target band and required gates pass. "
            "Execution remains blocked until explicit owner arming command."
        )
    elif status == TARGET_BLOCKED_BY_BROKER:
        next_safe_action = "Provide sanitized read-only broker money proof and reconciled broker readiness."
    elif status == TARGET_BLOCKED_BY_RISK:
        next_safe_action = "Resolve risk gate blockers before milestone review."
    elif blockers:
        next_safe_action = "Collect additional evidence to close milestone blockers."
    else:
        next_safe_action = "Collect evidence before attempting 100%-120% target review."

    return {
        "packet_id": PACKET_ID,
        "target_return_min_percent": DEFAULT_TARGET_MIN,
        "target_return_max_percent": DEFAULT_TARGET_MAX,
        "target_status": status,
        "current_return_percent": current_return_percent,
        "current_return_source": current_return_source,
        "starting_balance": _to_float(candidate.get("starting_balance")),
        "current_balance": _to_float(candidate.get("current_balance")),
        "realized_pl": _to_float(candidate.get("realized_pl")),
        "unrealized_pl": _to_float(candidate.get("unrealized_pl")),
        "open_trades": open_trades,
        "closed_trades": closed_trades,
        "sample_size": sample_size,
        "expectancy": _to_float(candidate.get("expectancy")),
        "profit_factor": _to_float(candidate.get("profit_factor")),
        "max_drawdown": _to_float(candidate.get("max_drawdown")),
        "walk_forward_status": _string(candidate.get("walk_forward_status"), "NOT_PROVEN"),
        "consistency_status": _string(candidate.get("consistency_status"), "NOT_PROVEN"),
        "persistence_status": _string(candidate.get("persistence_status"), "NOT_PROVEN"),
        "broker_readiness_status": broker_readiness_status,
        "risk_gate_status": risk_gate_status,
        "candidate_id": _string(candidate.get("candidate_id"), "UNSPECIFIED"),
        "strategy_id": _string(candidate.get("strategy_id"), "UNSPECIFIED"),
        "instrument": _string(candidate.get("instrument"), "UNSPECIFIED"),
        "execution_allowed": False,
        "demo_order_allowed": False,
        "live_order_allowed": False,
        "blockers": blockers,
        "next_safe_action": next_safe_action,
    }


def evaluate_profit_milestone_100_120_tracker_v1(*, candidate_evidence: Mapping[str, Any] | None = None) -> dict[str, Any]:
    if not isinstance(candidate_evidence, Mapping):
        return _build_status(
            TARGET_NOT_PROVEN,
            blockers=["candidate_evidence_not_provided_or_invalid"],
            current_return_percent=None,
            candidate={},
        )

    if _contains_sensitive(candidate_evidence):
        return _build_status(
            TARGET_BLOCKED_BY_EVIDENCE,
            blockers=["sensitive_payload_present"],
            current_return_percent=None,
            candidate={"current_return_source": "BLOCKED"},
        )

    direction = _string(candidate_evidence.get("direction")).strip().upper()
    if direction and direction != "LONG":
        return _build_status(
            TARGET_BLOCKED_BY_EVIDENCE,
            blockers=["non_long_direction"],
            current_return_percent=None,
            candidate=candidate_evidence,
        )

    if not _safe_bool(candidate_evidence.get("long_only"), default=False):
        return _build_status(
            TARGET_BLOCKED_BY_EVIDENCE,
            blockers=["long_only_required"],
            current_return_percent=None,
            candidate=candidate_evidence,
        )
    if not _safe_bool(candidate_evidence.get("short_side_disabled"), default=True):
        return _build_status(
            TARGET_BLOCKED_BY_EVIDENCE,
            blockers=["short_side_enabled"],
            current_return_percent=None,
            candidate=candidate_evidence,
        )

    sample_size = _to_int(candidate_evidence.get("sample_size"))
    closed_trades = _to_int(candidate_evidence.get("closed_trades"))
    expectancy = _to_float(candidate_evidence.get("expectancy"))
    profit_factor = _to_float(candidate_evidence.get("profit_factor"))
    max_drawdown = _to_float(candidate_evidence.get("max_drawdown"))
    out_of_sample_folds = _to_int(candidate_evidence.get("out_of_sample_folds"))
    walk_forward_folds = _to_int(candidate_evidence.get("walk_forward_folds"))
    starting_balance = _to_float(candidate_evidence.get("starting_balance"))
    current_balance = _to_float(candidate_evidence.get("current_balance"))
    current_return_percent = _compute_return_percent(starting_balance, current_balance)

    min_required_trades = _to_int(candidate_evidence.get("min_required_trades", 30))
    min_required_walk_forward_folds = _to_int(candidate_evidence.get("min_required_walk_forward_folds", 3))
    min_required_out_of_sample_folds = _to_int(candidate_evidence.get("min_required_out_of_sample_folds", 3))
    min_expectancy = _to_float(candidate_evidence.get("min_expectancy", 0.0))
    min_profit_factor = _to_float(candidate_evidence.get("min_profit_factor", 1.2))
    max_drawdown_allowed = _to_float(candidate_evidence.get("max_drawdown_allowed", 30.0))
    target_min = _to_float(candidate_evidence.get("target_return_min_percent", DEFAULT_TARGET_MIN))
    target_max = _to_float(candidate_evidence.get("target_return_max_percent", DEFAULT_TARGET_MAX))
    if min_required_trades is None:
        min_required_trades = 30
    if min_required_walk_forward_folds is None:
        min_required_walk_forward_folds = 3
    if min_required_out_of_sample_folds is None:
        min_required_out_of_sample_folds = 3
    if min_expectancy is None:
        min_expectancy = 0.0
    if min_profit_factor is None:
        min_profit_factor = 1.2
    if max_drawdown_allowed is None:
        max_drawdown_allowed = 30.0
    if target_min is None:
        target_min = DEFAULT_TARGET_MIN
    if target_max is None:
        target_max = DEFAULT_TARGET_MAX

    blockers: list[str] = []

    required_ids = [
        _string(candidate_evidence.get("candidate_id"), "").strip(),
        _string(candidate_evidence.get("strategy_id"), "").strip(),
        _string(candidate_evidence.get("instrument"), "").strip(),
    ]
    if any(not value for value in required_ids):
        blockers.append("missing_candidate_metadata")

    if sample_size is None or sample_size < min_required_trades:
        blockers.append("insufficient_sample")
    if closed_trades is None or closed_trades < min_required_trades:
        blockers.append("insufficient_closed_trades")
    if expectancy is None or expectancy <= min_expectancy:
        blockers.append("weak_expectancy")
    if profit_factor is None or profit_factor < min_profit_factor:
        blockers.append("weak_profit_factor")
    if max_drawdown is None or max_drawdown > max_drawdown_allowed:
        blockers.append("weak_drawdown_gate")
    if walk_forward_folds is None or walk_forward_folds < min_required_walk_forward_folds:
        blockers.append("insufficient_walk_forward_folds")
    if out_of_sample_folds is None or out_of_sample_folds < min_required_out_of_sample_folds:
        blockers.append("insufficient_oos_folds")

    broker_ready = _safe_bool(candidate_evidence.get("broker_readiness_passed"), default=False) or _safe_bool(
        candidate_evidence.get("broker_readiness_status"),
        default=False,
    )
    risk_ready = _safe_bool(candidate_evidence.get("risk_gate_passed"), default=False) or _safe_bool(
        candidate_evidence.get("risk_gate_status"),
        default=False,
    )
    if not broker_ready:
        blockers.append("broker_readiness_not_proven")
    if not risk_ready:
        blockers.append("risk_gate_not_proven")

    if current_return_percent is None:
        blockers.append("return_unavailable")
    elif current_return_percent < target_min:
        blockers.append("target_not_reached")
    elif current_return_percent > target_max:
        blockers.append("target_exceeds_ceiling")

    if blockers:
        if "broker_readiness_not_proven" in blockers:
            status = TARGET_BLOCKED_BY_BROKER
        elif "risk_gate_not_proven" in blockers:
            status = TARGET_BLOCKED_BY_RISK
        else:
            status = TARGET_BLOCKED_BY_EVIDENCE
    else:
        status = TARGET_READY_FOR_OWNER_REVIEW

    return _build_status(
        status,
        blockers=blockers,
        current_return_percent=current_return_percent,
        candidate=candidate_evidence,
    )
