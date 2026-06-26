"""Pure-local profitability evidence engine V1 for AIOS Forex.

The engine consumes sanitized closed trade evidence, replay summaries,
walk-forward summaries, and thresholds. Positive evidence supports future
review only; it never approves trading or broker execution.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any, Mapping, Sequence


PROFITABILITY_EVIDENCE_VERSION = "profitability_evidence_v1"

PROFITABILITY_EVIDENCE_REVIEW_READY = "PROFITABILITY_EVIDENCE_REVIEW_READY"
PROFITABILITY_EVIDENCE_BLOCKED = "PROFITABILITY_EVIDENCE_BLOCKED"
PROFITABILITY_EVIDENCE_INCOMPLETE = "PROFITABILITY_EVIDENCE_INCOMPLETE"

PROTECTED_PERMISSION_FLAGS = {
    "broker_execution_allowed": False,
    "live_trading_allowed": False,
    "order_submission_allowed": False,
    "credential_access_allowed": False,
    "account_access_allowed": False,
    "dashboard_execution_authority": False,
    "owner_approval_created": False,
}

SECRET_OR_ACCOUNT_FIELD_FRAGMENTS = (
    "api_key",
    "access_token",
    "refresh_token",
    "authorization",
    "bearer",
    "password",
    "secret",
    "credential",
    "account_id",
    "accountid",
    "account_number",
    "account_reference",
    "broker_order_id",
    "raw_order_id",
    "raw_transaction_id",
    "raw_payload",
)

UNSAFE_TRUE_FIELDS = (
    "broker_execution_allowed",
    "live_trading_allowed",
    "order_submission_allowed",
    "credential_access_allowed",
    "account_access_allowed",
    "dashboard_execution_authority",
    "owner_approval_created",
    "execution_allowed",
    "trade_allowed",
    "broker_access_allowed",
)


def build_sample_closed_trades() -> list[dict[str, Any]]:
    trades: list[dict[str, Any]] = []
    for index in range(1, 37):
        pnl = Decimal("12.50") if index % 4 else Decimal("-4.00")
        regime = "trend" if index % 2 else "range"
        trades.append(
            {
                "trade_id": f"sanitized-closed-trade-{index:03d}",
                "net_pnl": float(pnl),
                "age_days": index % 5,
                "regime": regime,
                "sanitized": True,
            }
        )
    return trades


def build_sample_replay_summaries() -> list[dict[str, Any]]:
    return [
        {
            "replay_id": "replay-proof-sample",
            "status": "PASS",
            "records_replayed": 36,
            "sanitized": True,
        }
    ]


def build_sample_walk_forward_summaries() -> list[dict[str, Any]]:
    return [
        {
            "walk_forward_id": "walk-forward-proof-sample",
            "status": "PASS",
            "windows_passed": 4,
            "windows_total": 4,
            "sanitized": True,
        }
    ]


def build_sample_thresholds() -> dict[str, Any]:
    return {
        "min_closed_trades": 30,
        "min_expectancy": 0.05,
        "min_profit_factor": 1.25,
        "max_drawdown": 100.0,
        "max_evidence_age_days": 7,
        "min_regime_count": 2,
        "require_replay_pass": True,
        "require_walk_forward_pass": True,
    }


def evaluate_profitability_evidence(
    closed_trade_evidence: Sequence[Mapping[str, Any]] | None = None,
    replay_summaries: Sequence[Mapping[str, Any]] | None = None,
    walk_forward_summaries: Sequence[Mapping[str, Any]] | None = None,
    thresholds: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate local profitability proof inputs for review only."""

    if (
        closed_trade_evidence is None
        or replay_summaries is None
        or walk_forward_summaries is None
        or thresholds is None
    ):
        return _result(
            status=PROFITABILITY_EVIDENCE_INCOMPLETE,
            metrics={},
            blockers=["closed trades, replay summaries, walk-forward summaries, and thresholds are required"],
            proof_quality="INCOMPLETE",
            next_safe_action="Provide complete sanitized profitability evidence and rerun locally.",
        )

    trades = [dict(item) for item in closed_trade_evidence if isinstance(item, Mapping)]
    replay = [dict(item) for item in replay_summaries if isinstance(item, Mapping)]
    walk_forward = [dict(item) for item in walk_forward_summaries if isinstance(item, Mapping)]
    active_thresholds = dict(thresholds)

    if not trades or not replay or not walk_forward:
        return _result(
            status=PROFITABILITY_EVIDENCE_INCOMPLETE,
            metrics={},
            blockers=["profitability inputs must include at least one closed trade, replay, and walk-forward summary"],
            proof_quality="INCOMPLETE",
            next_safe_action="Provide non-empty sanitized profitability inputs and rerun locally.",
        )

    safety_blockers = []
    safety_blockers.extend(_unsafe_fragments(trades, "closed_trade_evidence"))
    safety_blockers.extend(_unsafe_fragments(replay, "replay_summaries"))
    safety_blockers.extend(_unsafe_fragments(walk_forward, "walk_forward_summaries"))
    safety_blockers.extend(_unsafe_fragments(active_thresholds, "thresholds"))

    required_thresholds = (
        "min_closed_trades",
        "min_expectancy",
        "min_profit_factor",
        "max_drawdown",
        "max_evidence_age_days",
        "min_regime_count",
    )
    missing_thresholds = [
        name for name in required_thresholds if name not in active_thresholds
    ]
    if missing_thresholds:
        return _result(
            status=PROFITABILITY_EVIDENCE_INCOMPLETE,
            metrics={},
            blockers=[f"missing threshold: {name}" for name in missing_thresholds],
            proof_quality="INCOMPLETE",
            next_safe_action="Provide missing profitability thresholds and rerun locally.",
        )

    numeric_thresholds = {
        name: _decimal(active_thresholds[name]) for name in required_thresholds
    }
    numeric_errors = [
        name for name, value in numeric_thresholds.items() if value is None
    ]
    if numeric_errors:
        return _result(
            status=PROFITABILITY_EVIDENCE_INCOMPLETE,
            metrics={},
            blockers=[f"threshold must be numeric: {name}" for name in numeric_errors],
            proof_quality="INCOMPLETE",
            next_safe_action="Repair numeric profitability thresholds and rerun locally.",
        )

    trade_values: list[Decimal] = []
    trade_ages: list[Decimal] = []
    regimes: set[str] = set()
    trade_errors: list[str] = []
    for index, trade in enumerate(trades):
        if trade.get("sanitized") is not True:
            safety_blockers.append(f"closed_trade_evidence[{index}] is not marked sanitized")
        pnl = _decimal(_first(trade, "net_pnl", "pnl", "r_multiple"))
        age = _decimal(_first(trade, "age_days", "evidence_age_days"))
        if pnl is None:
            trade_errors.append(f"closed_trade_evidence[{index}].net_pnl missing or invalid")
        else:
            trade_values.append(pnl)
        if age is None:
            trade_errors.append(f"closed_trade_evidence[{index}].age_days missing or invalid")
        else:
            trade_ages.append(age)
        regime = _text(trade.get("regime"))
        if regime:
            regimes.add(regime)

    if trade_errors:
        return _result(
            status=PROFITABILITY_EVIDENCE_INCOMPLETE,
            metrics={},
            blockers=trade_errors + safety_blockers,
            proof_quality="INCOMPLETE",
            next_safe_action="Repair closed trade profitability fields and rerun locally.",
        )

    min_trades = numeric_thresholds["min_closed_trades"] or Decimal("0")
    min_expectancy = numeric_thresholds["min_expectancy"] or Decimal("0")
    min_profit_factor = numeric_thresholds["min_profit_factor"] or Decimal("0")
    max_drawdown = numeric_thresholds["max_drawdown"] or Decimal("0")
    max_age = numeric_thresholds["max_evidence_age_days"] or Decimal("0")
    min_regime_count = numeric_thresholds["min_regime_count"] or Decimal("0")

    blockers: list[str] = list(safety_blockers)
    if min_trades <= 0:
        blockers.append("threshold min_closed_trades must be positive")
    if min_profit_factor < Decimal("1"):
        blockers.append("threshold min_profit_factor conflicts with profitability proof")
    if max_drawdown <= 0 or max_age < 0 or min_regime_count <= 0:
        blockers.append("thresholds contain conflicting non-positive limits")

    sample_depth = len(trade_values)
    total = sum(trade_values, Decimal("0"))
    expectancy = total / Decimal(sample_depth)
    gross_profit = sum((value for value in trade_values if value > 0), Decimal("0"))
    gross_loss = abs(sum((value for value in trade_values if value < 0), Decimal("0")))
    profit_factor = Decimal("999") if gross_loss == 0 and gross_profit > 0 else (
        gross_profit / gross_loss if gross_loss else Decimal("0")
    )
    drawdown = _max_drawdown(trade_values)
    max_evidence_age = max(trade_ages) if trade_ages else Decimal("999")
    regime_count = len(regimes)
    replay_passed = all(_status_passed(item) for item in replay)
    walk_forward_passed = all(_status_passed(item) for item in walk_forward)

    if sample_depth < min_trades:
        blockers.append("closed trade sample depth is below threshold")
    if expectancy < min_expectancy:
        blockers.append("expectancy is below threshold")
    if profit_factor < min_profit_factor:
        blockers.append("profit factor is below threshold")
    if drawdown > max_drawdown:
        blockers.append("drawdown exceeds threshold")
    if max_evidence_age > max_age:
        blockers.append("profitability evidence is stale")
    if Decimal(regime_count) < min_regime_count:
        blockers.append("regime coverage is below threshold")
    if active_thresholds.get("require_replay_pass", True) is True and not replay_passed:
        blockers.append("replay proof is missing or failed")
    if active_thresholds.get("require_walk_forward_pass", True) is True and not walk_forward_passed:
        blockers.append("walk-forward proof is missing or failed")

    metrics = {
        "expectancy": _float(expectancy),
        "profit_factor": _float(profit_factor),
        "drawdown": _float(drawdown),
        "sample_depth": sample_depth,
        "freshness": {
            "max_evidence_age_days": _float(max_evidence_age),
            "freshness_threshold_days": _float(max_age),
            "fresh": max_evidence_age <= max_age,
        },
        "regime_coverage": {
            "regime_count": regime_count,
            "required_regime_count": int(min_regime_count),
            "regimes": sorted(regimes),
        },
        "replay_passed": replay_passed,
        "walk_forward_passed": walk_forward_passed,
    }

    status = (
        PROFITABILITY_EVIDENCE_BLOCKED
        if blockers
        else PROFITABILITY_EVIDENCE_REVIEW_READY
    )
    proof_quality = "BLOCKED" if blockers else "REVIEW_READY"
    next_safe_action = (
        "Continue to stop/pause/resume review; profitability evidence authorizes no trading."
        if status == PROFITABILITY_EVIDENCE_REVIEW_READY
        else "Repair profitability proof blockers before any owner review."
    )
    return _result(
        status=status,
        metrics=metrics,
        blockers=blockers,
        proof_quality=proof_quality,
        next_safe_action=next_safe_action,
    )


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return _jsonable(dict(result))


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    status = str(result.get("status", PROFITABILITY_EVIDENCE_INCOMPLETE))
    metrics = result.get("metrics") or {}
    if status == PROFITABILITY_EVIDENCE_REVIEW_READY:
        return (
            "Profitability evidence is review-ready only. "
            f"Expectancy {metrics.get('expectancy')}, profit factor "
            f"{metrics.get('profit_factor')}. No trading approval was created."
        )
    blockers = result.get("blockers") or ["profitability evidence incomplete"]
    return "Profitability evidence blocked: " + "; ".join(str(item) for item in blockers)


def _result(
    *,
    status: str,
    metrics: Mapping[str, Any],
    blockers: list[str],
    proof_quality: str,
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "engine_version": PROFITABILITY_EVIDENCE_VERSION,
        "status": status,
        "metrics": dict(metrics),
        "expectancy": metrics.get("expectancy"),
        "profit_factor": metrics.get("profit_factor"),
        "drawdown": metrics.get("drawdown"),
        "sample_depth": metrics.get("sample_depth"),
        "freshness": metrics.get("freshness", {}),
        "regime_coverage": metrics.get("regime_coverage", {}),
        "blockers": list(blockers),
        "proof_quality": proof_quality,
        "next_safe_action": next_safe_action,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def _max_drawdown(values: Sequence[Decimal]) -> Decimal:
    equity = Decimal("0")
    peak = Decimal("0")
    drawdown = Decimal("0")
    for value in values:
        equity += value
        if equity > peak:
            peak = equity
        current = peak - equity
        if current > drawdown:
            drawdown = current
    return drawdown


def _status_passed(summary: Mapping[str, Any]) -> bool:
    status = _text(_first(summary, "status", "classification")).upper()
    return status in {"PASS", "PASSED", "READY", "REVIEW_READY", "OK"}


def _unsafe_fragments(value: Any, prefix: str) -> list[str]:
    fragments: list[str] = []
    _scan_payload(value, prefix, fragments)
    return fragments


def _scan_payload(value: Any, path: str, fragments: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            lowered = key_text.lower()
            if any(fragment in lowered for fragment in SECRET_OR_ACCOUNT_FIELD_FRAGMENTS):
                fragments.append(f"{path}.{key_text} contains secret-like or account-like data")
            if lowered in UNSAFE_TRUE_FIELDS and _truthy(item):
                fragments.append(f"{path}.{key_text} is unsafe true")
            _scan_payload(item, f"{path}.{key_text}", fragments)
    elif isinstance(value, (list, tuple, set)):
        for index, item in enumerate(value):
            _scan_payload(item, f"{path}[{index}]", fragments)
    elif isinstance(value, str):
        lowered = value.lower()
        if any(fragment in lowered for fragment in SECRET_OR_ACCOUNT_FIELD_FRAGMENTS):
            fragments.append(f"{path} contains secret-like or account-like text")


def _first(source: Mapping[str, Any], *names: str) -> Any:
    for name in names:
        if name in source:
            return source[name]
    return None


def _decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError):
        return None


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return False


def _text(value: Any) -> str:
    if value is None:
        return ""
    return value.strip() if isinstance(value, str) else str(value).strip()


def _float(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.000001")))


def _jsonable(value: Any) -> Any:
    if isinstance(value, Decimal):
        return _float(value)
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, tuple):
        return [_jsonable(item) for item in value]
    if isinstance(value, list):
        return [_jsonable(item) for item in value]
    return value


__all__ = [
    "PROFITABILITY_EVIDENCE_BLOCKED",
    "PROFITABILITY_EVIDENCE_INCOMPLETE",
    "PROFITABILITY_EVIDENCE_REVIEW_READY",
    "PROFITABILITY_EVIDENCE_VERSION",
    "build_sample_closed_trades",
    "build_sample_replay_summaries",
    "build_sample_thresholds",
    "build_sample_walk_forward_summaries",
    "evaluate_profitability_evidence",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
