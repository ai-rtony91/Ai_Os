"""Short-side readiness verifier for Forex (governed, non-live)."""

from __future__ import annotations

from typing import Any, Iterable, Mapping


FOREX_SHORT_SIDE_READINESS_V1 = "FOREX_SHORT_SIDE_READINESS_V1"
SCHEMA = "AIOS_FOREX_SHORT_SIDE_READINESS_V1"
SUPPORTED_PAIRS = {"EURUSD", "GBPUSD", "USDJPY"}


def evaluate_short_readiness(
    signal: Mapping[str, Any] | None = None,
    *,
    account_snapshot: Mapping[str, Any] | None = None,
    limits: Mapping[str, Any] | None = None,
    broker_proof: Mapping[str, Any] | None = None,
    **safety_flags: Any,
) -> dict[str, Any]:
    signal = signal if isinstance(signal, Mapping) else {}
    account = account_snapshot if isinstance(account_snapshot, Mapping) else {}
    limits = limits if isinstance(limits, Mapping) else {}
    broker_proof = broker_proof if isinstance(broker_proof, Mapping) else {}

    unsafe = _unsafe_reason(safety_flags)
    if unsafe:
        return _blocked(unsafe)

    pair = str(signal.get("pair", "")).upper()
    action = str(signal.get("action", "")).lower()
    if not pair or pair not in SUPPORTED_PAIRS:
        return _blocked("invalid_pair")
    if action not in {"sell", "short"}:
        return _blocked("short_action_required")

    short_permission = bool(
        account.get("short_permission")
        or broker_proof.get("short_permission")
        or broker_proof.get("permissions", {}).get("short", False)
    )
    if not short_permission:
        return _blocked("broker_short_permission_missing")

    entry_price = _safe_float(signal.get("entry_price"), None)
    stop_loss = _safe_float(signal.get("stop_loss"), None)
    take_profit = _safe_float(signal.get("take_profit"), None)
    if entry_price is not None and stop_loss is not None and stop_loss <= entry_price:
        return _blocked("short_stop_loss_not_above_entry")
    if entry_price is not None and take_profit is not None and take_profit >= entry_price:
        return _blocked("short_take_profit_not_below_entry")

    spread_pips = _safe_float(signal.get("spread_pips"), None)
    slippage_pips = _safe_float(signal.get("slippage_pips"), None)
    max_spread = _safe_float(limits.get("max_spread_bps"), _safe_float(limits.get("max_spread_pips"), None))
    max_slippage = _safe_float(
        limits.get("max_slippage_bps"),
        _safe_float(limits.get("max_slippage_pips"), None),
    )
    if spread_pips is not None and max_spread is not None and spread_pips > max_spread:
        return _blocked("short_spread_guard_violated")
    if slippage_pips is not None and max_slippage is not None and slippage_pips > max_slippage:
        return _blocked("short_slippage_guard_violated")

    sizing_model = str(signal.get("sizing_model", "")).lower()
    if "martingale" in sizing_model or "revenge" in sizing_model or "averaging" in sizing_model:
        return _blocked("forbidden_short_sizing_model")
    if _safe_bool(signal.get("is_martingale")) or _safe_bool(signal.get("is_revenge")):
        return _blocked("forbidden_short_sizing_model")

    if not _safe_bool(signal.get("evidence_replay_ok"), False):
        return _blocked("short_evidence_replay_missing")

    if _safe_bool(signal.get("request_short_live_execution"), False) and not _safe_bool(
        signal.get("owner_approved_short_live_execution"),
        False,
    ):
        return _blocked("owner_approval_required_for_short_live_execution")

    position_size_units = _safe_float(signal.get("position_size_units"), 0.0)
    risk_percent = _safe_float(signal.get("risk_percent"), 0.0)
    max_pair_risk = _safe_float(limits.get("max_pair_risk_percent"), _safe_float(limits.get("max_risk_percent"), None))
    if max_pair_risk is not None and risk_percent > max_pair_risk:
        return _blocked("short_risk_percent_above_pair_cap")
    if not _safe_bool(signal.get("paper_only"), True):
        return _blocked("short_live_not_allowed_without_approval")

    readiness = {
        "pair": pair,
        "short_side": True,
        "broker_short_permission": short_permission,
        "risk_ok": True,
        "stop_loss_rule_ok": entry_price is None or stop_loss is None or stop_loss > entry_price,
        "take_profit_rule_ok": entry_price is None or take_profit is None or take_profit < entry_price,
        "evidence_replay_ok": True,
        "spread_slippage_guard_ok": True,
        "paper_readiness": True,
        "live_readiness": False,
    }

    return {
        "schema": SCHEMA,
        "module": FOREX_SHORT_SIDE_READINESS_V1,
        "allowed": True,
        "blocked_reason": None,
        "paper_only": True,
        "short_readiness": readiness,
        "risk_result": {"allowed": True},
        "safety": {
            "paper_only": True,
            "simulation_ready": True,
            "broker_integration": False,
            "live_short_execution": False,
            "scheduler_allowed": False,
            "daemon_allowed": False,
            "webhook_allowed": False,
        },
        "safe_next_action": (
            "Short readiness checks pass in review mode. "
            "Do not execute short orders until a separate owner short-gate packet is issued."
        ),
        "mode": "PAPER_ONLY",
    }


def evaluate_short_batch(
    signal_intents: Iterable[Mapping[str, Any]] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    signals = list(signal_intents or [])
    if not signals:
        return {
            "schema": SCHEMA,
            "module": FOREX_SHORT_SIDE_READINESS_V1,
            "allowed": False,
            "blocked_reason": "no_short_signals",
            "paper_only": True,
            "short_readiness": [],
            "results": [],
            "safety": {
                "paper_only": True,
                "live_short_execution": False,
                "broker_integration": False,
                "scheduler_allowed": False,
                "daemon_allowed": False,
                "webhook_allowed": False,
            },
            "safe_next_action": "Supply short-side signal candidates for review.",
            "mode": "PAPER_ONLY",
        }

    results = [evaluate_short_readiness(signal, **kwargs) for signal in signals]
    blocked = [result for result in results if not result.get("allowed")]
    return {
        "schema": SCHEMA,
        "module": FOREX_SHORT_SIDE_READINESS_V1,
        "allowed": len(blocked) == 0,
        "short_side": True,
        "mode": "PAPER_ONLY",
        "paper_only": True,
        "batch_size": len(results),
        "blocked_count": len(blocked),
        "batch_blocked_reasons": [result.get("blocked_reason") for result in blocked],
        "short_readiness": [result.get("short_readiness", {}) for result in results],
        "results": results,
        "safe_next_action": "Resolve short-side blockers in this same readiness packet before any live short gate.",
        "safety": {
            "paper_only": True,
            "live_short_execution": False,
            "broker_integration": False,
            "scheduler_allowed": False,
            "daemon_allowed": False,
            "webhook_allowed": False,
        },
    }


def _blocked(reason: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "module": FOREX_SHORT_SIDE_READINESS_V1,
        "allowed": False,
        "blocked_reason": reason,
        "paper_only": True,
        "short_readiness": {
            "short_side": True,
            "broker_short_permission": False,
            "paper_readiness": False,
            "live_readiness": False,
        },
        "risk_result": {"allowed": False},
        "safety": {
            "paper_only": True,
            "simulation_ready": False,
            "broker_integration": False,
            "live_short_execution": False,
            "scheduler_allowed": False,
            "daemon_allowed": False,
            "webhook_allowed": False,
        },
        "mode": "PAPER_ONLY",
        "safe_next_action": "Resolve the blocked short-readiness condition before any short-side readiness/activation step.",
    }


def _unsafe_reason(flags: dict[str, Any]) -> str | None:
    blocked_fields = {
        "live_execution": "live_execution_blocked",
        "broker_order": "broker_order_blocked",
        "credentials": "credentials_blocked",
        "api_key": "api_key_blocked",
        "real_order": "real_order_blocked",
        "webhook_url": "real_webhook_blocked",
        "network": "network_blocked",
        "network_access": "network_blocked",
    }
    for field, reason in blocked_fields.items():
        if flags.get(field):
            return reason
    return None


def _safe_float(value: Any, default: float | None = None) -> float | None:
    if value is None or value is True or value is False:
        return default
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _safe_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on"}:
        return True
    if text in {"0", "false", "no", "off"}:
        return False
    return bool(value)
