"""Canonical paper-only forex paper-fill simulator."""
from __future__ import annotations

import hashlib
from dataclasses import asdict, dataclass, is_dataclass
from typing import Any, Mapping

from automation.forex_engine.order_preview import ORDER_PREVIEW_ALLOWED
from automation.forex_engine.paper_trade_lifecycle import (
    build_paper_trade,
    transition_paper_trade,
    paper_trade_to_dict,
)

PAPER_FILL_MODE = "PAPER_ONLY"
PAPER_FILL_ALLOWED = "allowed"
PAPER_FILL_BLOCKED = "blocked"

REASON_NONE = "none"
REASON_INVALID_PREVIEW = "invalid_preview"
REASON_PREVIEW_NOT_APPROVED = "preview_not_approved"
REASON_NON_PAPER_MODE = "non_paper_mode"
REASON_LIVE_TRADING_BLOCKED = "live_trading_blocked"
REASON_MISSING_PAIR = "missing_pair"
REASON_MISSING_DIRECTION = "missing_direction"
REASON_MISSING_UNITS = "missing_units"
REASON_MISSING_ENTRY_PRICE = "missing_entry_price"
REASON_MISSING_MARKET_PRICE = "missing_market_price"
REASON_SPREAD_TOO_HIGH = "spread_too_high"
REASON_SLIPPAGE_TOO_HIGH = "slippage_too_high"
REASON_INVALID_FILL_PRICE = "invalid_fill_price"
REASON_LIFECYCLE_BUILD_FAILED = "lifecycle_build_failed"
REASON_EVIDENCE_PATH_INVALID = "evidence_path_invalid"


def _coerce_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value))
    except (TypeError, ValueError):
        return None


def _coerce_positive_float(value: Any) -> float | None:
    value_float = _coerce_float(value)
    if value_float is None or value_float <= 0:
        return None
    return value_float


def _coerce_non_negative_float(value: Any) -> float | None:
    value_float = _coerce_float(value)
    if value_float is None or value_float < 0:
        return None
    return value_float


def _coerce_upper(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip().upper()
    return None


def _coerce_lower(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip().lower()
    return None


def _safe_safety_dict() -> dict[str, bool]:
    return {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def _safe_relative_path(value: Any) -> tuple[bool, str | None]:
    if value is None:
        return True, None
    if not isinstance(value, str):
        return False, None
    s = value.strip()
    if not s:
        return True, s
    if s.startswith(("/", "\\")) or ":" in s or "\\\\" in s:
        return False, s
    return True, s


def _dedupe(reasons: list[str]) -> list[str]:
    ordered = []
    for reason in reasons:
        if reason not in ordered:
            ordered.append(reason)
    return ordered


def _next_safe_action(first_reason: str | None) -> str:
    if not first_reason or first_reason == REASON_NONE:
        return "prepare_next_paper_fill"
    mapping = {
        REASON_PREVIEW_NOT_APPROVED: "run_order_preview_first",
        REASON_INVALID_PREVIEW: "fix_preview_payload",
        REASON_NON_PAPER_MODE: "set_paper_only_inputs",
        REASON_LIVE_TRADING_BLOCKED: "remove_live_inputs",
        REASON_MISSING_PAIR: "provide_pair",
        REASON_MISSING_DIRECTION: "provide_direction",
        REASON_MISSING_UNITS: "provide_positive_units",
        REASON_MISSING_ENTRY_PRICE: "provide_entry_price",
        REASON_MISSING_MARKET_PRICE: "add_market_price_or_enable_fallback",
        REASON_SPREAD_TOO_HIGH: "reduce_spread_or_adjust_config",
        REASON_SLIPPAGE_TOO_HIGH: "reduce_slippage_or_adjust_config",
        REASON_INVALID_FILL_PRICE: "fix_fill_price",
        REASON_LIFECYCLE_BUILD_FAILED: "retry_fill_after_fixing_lifecycle_inputs",
        REASON_EVIDENCE_PATH_INVALID: "use_relative_metadata_path_only",
    }
    return mapping.get(first_reason, "review_fill_inputs")


def _extract_fill_config(fill_config: Any) -> dict[str, Any]:
    if not isinstance(fill_config, Mapping):
        return {"max_spread": 0.0, "max_slippage": 0.0, "slippage": 0.0}
    max_spread = _coerce_non_negative_float(fill_config.get("max_spread")) or 0.0
    max_slippage = _coerce_non_negative_float(fill_config.get("max_slippage")) or 0.0
    slippage = _coerce_non_negative_float(fill_config.get("slippage")) or 0.0
    return {"max_spread": max_spread, "max_slippage": max_slippage, "slippage": slippage}


def _deterministic_fill_id(payload: dict[str, Any]) -> str:
    fill_key = "|".join(
        str(payload.get(key))
        for key in [
            "preview_id",
            "pair",
            "direction",
            "requested_price",
            "fill_price",
            "filled_units",
            "timestamp",
        ]
    )
    digest = hashlib.sha256(fill_key.encode("utf-8")).hexdigest()
    return f"fill-{digest[:16]}"


def _coerce_mode(value: Any) -> str:
    if value is None:
        return PAPER_FILL_MODE
    return _coerce_lower(value) or PAPER_FILL_MODE


def _build_trade_payload(order_preview: Mapping[str, Any], fill_price: float, opened_timestamp: float, direction: str) -> dict[str, Any]:
    return {
        "trade_id": order_preview.get("preview_id"),
        "pair": order_preview.get("pair"),
        "direction": direction,
        "entry_type": order_preview.get("entry_type") or "market",
        "entry_price": fill_price,
        "stop_loss": order_preview.get("stop_loss"),
        "take_profit": order_preview.get("take_profit"),
        "units": order_preview.get("filled_units", order_preview.get("units", 0.0)),
        "dollar_risk": order_preview.get("dollar_risk", 0.0),
        "percent_risk": order_preview.get("percent_risk", 0.0),
        "status": "candidate",
        "created_timestamp": opened_timestamp,
        "opened_timestamp": opened_timestamp,
        "paper_only": True,
        "safety": _safe_safety_dict(),
        "blocked_reason": "none",
        "lifecycle_history": [],
        "metadata": {
            "source_preview_id": order_preview.get("preview_id"),
            "mode": order_preview.get("mode"),
            "fill_request": order_preview.get("fill_request", {}),
        },
    }


def _safe_apply_transition(trade: Any, status: str, timestamp: float, reason: str) -> Any:
    return transition_paper_trade(trade, status, timestamp=timestamp, reason=reason)


def _safe_build_trade(payload: dict[str, Any]) -> Any:
    allowed_keys = {
        "trade_id",
        "pair",
        "direction",
        "entry_type",
        "entry_price",
        "stop_loss",
        "take_profit",
        "units",
        "dollar_risk",
        "percent_risk",
        "status",
        "created_timestamp",
        "opened_timestamp",
        "closed_timestamp",
        "close_reason",
        "realized_pnl",
        "evidence_path",
        "blocked_reason",
        "lifecycle_history",
        "metadata",
    }
    build_payload = {key: value for key, value in payload.items() if key in allowed_keys}
    try:
        return build_paper_trade(build_payload)
    except TypeError:
        return build_paper_trade(**build_payload)
    except Exception:
        raise


def _safe_trade_to_dict(trade: Any, fallback: Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(trade, Mapping):
        return dict(trade)
    try:
        return paper_trade_to_dict(trade)
    except Exception:
        if is_dataclass(trade):
            try:
                return asdict(trade)
            except Exception:
                return dict(fallback)
        return dict(fallback)


def _trade_status(trade: Any, fallback: str = "candidate") -> str:
    if isinstance(trade, Mapping):
        return str(trade.get("status") or fallback)
    return str(getattr(trade, "status", fallback))


def _trade_history(trade: Any, fallback: list[str]) -> list[Any]:
    if isinstance(trade, Mapping):
        history = trade.get("lifecycle_history")
        return list(history) if isinstance(history, list) else list(fallback)
    history = getattr(trade, "lifecycle_history", None)
    return list(history) if isinstance(history, list) else list(fallback)


def _ordered_blocked_reasons(reasons: list[str]) -> list[str]:
    priority = [
        REASON_PREVIEW_NOT_APPROVED,
        REASON_NON_PAPER_MODE,
        REASON_LIVE_TRADING_BLOCKED,
        REASON_MISSING_PAIR,
        REASON_MISSING_DIRECTION,
        REASON_MISSING_UNITS,
        REASON_MISSING_ENTRY_PRICE,
        REASON_EVIDENCE_PATH_INVALID,
        REASON_SPREAD_TOO_HIGH,
        REASON_SLIPPAGE_TOO_HIGH,
        REASON_INVALID_FILL_PRICE,
        REASON_LIFECYCLE_BUILD_FAILED,
    ]
    unique = _dedupe(reasons)
    ordered = [reason for reason in priority if reason in unique]
    ordered.extend(reason for reason in unique if reason not in ordered)
    return ordered


@dataclass(frozen=True)
class PaperFillDecision:
    allowed: bool
    decision: str
    blocked_reason: str
    blocked_reasons: list[str]
    warnings: list[str]
    paper_only: bool
    mode: str
    fill_id: str
    preview_id: str
    trade_id: str | None
    pair: str | None
    direction: str | None
    entry_type: str | None
    requested_price: float | None
    fill_price: float | None
    filled_units: float
    slippage: float
    spread: float
    opened_timestamp: float | None
    status: str
    trade: dict[str, Any]
    lifecycle_result: dict[str, Any]
    evidence: dict[str, Any]
    evidence_path: str | None
    safety: dict[str, bool]
    next_safe_action: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _normalize_market_price(market_state: Mapping[str, Any] | None) -> tuple[float | None, float | None, float]:
    if not isinstance(market_state, Mapping):
        return None, None, 0.0
    ask = _coerce_positive_float(market_state.get("ask"))
    bid = _coerce_positive_float(market_state.get("bid"))
    spread = _coerce_non_negative_float(market_state.get("spread")) or 0.0
    if spread == 0.0 and ask is not None and bid is not None:
        spread = round(abs(ask - bid), 12)
    return bid, ask, spread


def simulate_paper_fill(
    order_preview: Any,
    market_state: Any = None,
    fill_config: Any = None,
    timestamp: Any = None,
    evidence_path: Any = None,
    metadata: Any = None,
) -> dict[str, Any]:
    blocked_reasons: list[str] = []
    warnings: list[str] = []
    config = _extract_fill_config(fill_config)
    metadata_payload = metadata if isinstance(metadata, Mapping) else {}
    ts_float = _coerce_float(timestamp) or 0.0

    if not isinstance(order_preview, Mapping):
        blocked_reasons.append(REASON_INVALID_PREVIEW)
        return PaperFillDecision(
            allowed=False,
            decision=PAPER_FILL_BLOCKED,
            blocked_reason=REASON_INVALID_PREVIEW,
            blocked_reasons=[REASON_INVALID_PREVIEW],
            warnings=[],
            paper_only=True,
            mode=PAPER_FILL_MODE,
            fill_id="invalid-order-preview",
            preview_id="invalid",
            trade_id=None,
            pair=None,
            direction=None,
            entry_type=None,
            requested_price=None,
            fill_price=None,
            filled_units=0.0,
            slippage=0.0,
            spread=0.0,
            opened_timestamp=None,
            status="candidate",
            trade={},
            lifecycle_result={},
            evidence={},
            evidence_path=None,
            safety=_safe_safety_dict(),
            next_safe_action=_next_safe_action(REASON_INVALID_PREVIEW),
            metadata={
                "reason": "order_preview_not_mapping",
                **dict(metadata_payload),
            },
        ).to_dict()

    preview = dict(order_preview)
    preview_allowed = preview.get("allowed") is True
    approval_state = _coerce_lower(preview.get("approval_state"))
    paper_only = preview.get("paper_only", True)
    mode = _coerce_mode(preview.get("mode"))
    pair = _coerce_upper(preview.get("pair"))
    direction = _coerce_lower(preview.get("direction"))
    entry_type = _coerce_lower(preview.get("entry_type")) or "market"
    requested_price = _coerce_positive_float(preview.get("entry_price"))
    units = _coerce_positive_float(preview.get("units"))
    slippage = config["slippage"]

    valid_evidence, evidence_path_value = _safe_relative_path(evidence_path)
    if not valid_evidence:
        blocked_reasons.append(REASON_EVIDENCE_PATH_INVALID)

    if not preview_allowed or approval_state != "paper_preview_ready":
        blocked_reasons.append(REASON_PREVIEW_NOT_APPROVED)
    if paper_only is False:
        blocked_reasons.append(REASON_PREVIEW_NOT_APPROVED)
        blocked_reasons.append(REASON_NON_PAPER_MODE)
    if mode in {"live", "demo", "broker"}:
        blocked_reasons.append(REASON_LIVE_TRADING_BLOCKED)
    if not pair:
        blocked_reasons.append(REASON_MISSING_PAIR)
    if direction not in {"buy", "sell"}:
        blocked_reasons.append(REASON_MISSING_DIRECTION)
    if requested_price is None:
        blocked_reasons.append(REASON_MISSING_ENTRY_PRICE)

    if units is None:
        blocked_reasons.append(REASON_MISSING_UNITS)

    bid, ask, spread = _normalize_market_price(market_state if isinstance(market_state, Mapping) else None)
    if config["max_spread"] > 0 and spread > config["max_spread"]:
        blocked_reasons.append(REASON_SPREAD_TOO_HIGH)

    if config["max_slippage"] > 0 and slippage > config["max_slippage"]:
        blocked_reasons.append(REASON_SLIPPAGE_TOO_HIGH)

    if direction == "buy":
        if ask is not None:
            fill_price = round(ask + slippage, 12)
        else:
            fill_price = requested_price
    elif direction == "sell":
        if bid is not None:
            fill_price = round(bid - slippage, 12)
        else:
            fill_price = requested_price
    else:
        fill_price = requested_price

    if fill_price is None or fill_price <= 0:
        blocked_reasons.append(REASON_INVALID_FILL_PRICE)

    if not blocked_reasons and not valid_evidence:
        blocked_reasons.append(REASON_EVIDENCE_PATH_INVALID)

    if not preview_allowed and not blocked_reasons:
        blocked_reasons.append(REASON_PREVIEW_NOT_APPROVED)

    if not blocked_reasons:
        fill_payload = _build_trade_payload(
            preview,
            float(fill_price),
            ts_float,
            direction or "buy",
        )
        fill_payload["safety"] = _safe_safety_dict()

        try:
            trade_obj = _safe_build_trade(fill_payload)
        except Exception:
            blocked_reasons.append(REASON_LIFECYCLE_BUILD_FAILED)
            trade_obj = {}

        lifecycle_result = {}
        history: list[str] = []
        trade_status = ""
        if blocked_reasons:
            pass
        elif trade_obj is not None:
            try:
                if isinstance(trade_obj, Mapping) and preview.get("trade_id"):
                    trade_obj["trade_id"] = preview.get("trade_id")
            except Exception:
                pass

            transitions = ["previewed", "queued", "opened", "active"]
            for status in transitions:
                try:
                    trade_obj = _safe_apply_transition(trade_obj, status, ts_float, "paper_fill")
                    history.append(status)
                    trade_status = _trade_status(trade_obj, status)
                except Exception:
                    blocked_reasons.append(REASON_LIFECYCLE_BUILD_FAILED)
                    history.append(f"transition_failed:{status}")
                    break
            if hasattr(trade_obj, "lifecycle_history"):
                lifecycle_result["history"] = list(getattr(trade_obj, "lifecycle_history"))
            else:
                lifecycle_result["history"] = _trade_history(trade_obj, history)
        else:
            history = []
            trade_status = "candidate"

        if blocked_reasons:
            blocked_reasons = _ordered_blocked_reasons(blocked_reasons)
            return PaperFillDecision(
                allowed=False,
                decision=PAPER_FILL_BLOCKED,
                blocked_reason=blocked_reasons[0],
                blocked_reasons=blocked_reasons,
                warnings=warnings,
                paper_only=True,
                mode=PAPER_FILL_MODE,
                fill_id="blocked",
                preview_id=_coerce_lower(preview.get("preview_id")) or str(preview.get("preview_id") or "unknown"),
                trade_id=_coerce_lower(preview.get("trade_id")),
                pair=pair,
                direction=direction,
                entry_type=entry_type,
                requested_price=requested_price,
                fill_price=None,
                filled_units=units or 0.0,
                slippage=slippage,
                spread=spread,
                opened_timestamp=None,
                status="candidate",
                trade={},
                lifecycle_result={},
                evidence={},
                evidence_path=evidence_path_value,
                safety=_safe_safety_dict(),
                next_safe_action=_next_safe_action(blocked_reasons[0]),
                metadata={
                    "config": config,
                    "now_timestamp": ts_float,
                    "reason": "lifecycle_failed",
                    "market_state_present": isinstance(market_state, Mapping),
                    "direction": direction,
                    **dict(metadata_payload),
                },
            ).to_dict()

        if not history:
            history = []
        if not lifecycle_result:
            lifecycle_result = {"status": trade_status, "history": history}

        lifecycle_result.setdefault("status", trade_status)
        lifecycle_result.setdefault("history", history)

        trade_output = _safe_trade_to_dict(trade_obj, fill_payload)
        preview_trade = {
            "trade": dict(trade_output),
            "status": trade_status or _trade_status(trade_obj, "active"),
            "history": history,
            "lifecycle_history": _trade_history(trade_obj, history),
        }

        if not isinstance(trade_output, Mapping):
            trade_output = {}

        preview_id = _coerce_lower(preview.get("preview_id")) or "preview"
        fill_id = _deterministic_fill_id(
            {
                "preview_id": preview_id,
                "pair": pair,
                "direction": direction,
                "requested_price": requested_price,
                "fill_price": fill_price,
                "filled_units": units,
                "timestamp": ts_float,
            }
        )

        evidence = {
            "fill_id": fill_id,
            "preview_id": preview.get("preview_id"),
            "requested_price": requested_price,
            "fill_price": fill_price,
            "slippage": slippage,
            "spread": spread,
            "units": units,
            "mode": PAPER_FILL_MODE,
            "timestamp": ts_float,
            "market_state_present": isinstance(market_state, Mapping),
            "fill_config": dict(config),
        }

        result = PaperFillDecision(
            allowed=True,
            decision=PAPER_FILL_ALLOWED,
            blocked_reason=REASON_NONE,
            blocked_reasons=[],
            warnings=warnings,
            paper_only=True,
            mode=PAPER_FILL_MODE,
            fill_id=fill_id,
            preview_id=_coerce_lower(preview.get("preview_id")) or str(preview.get("preview_id") or preview_id),
            trade_id=_coerce_lower(preview.get("trade_id")) or _coerce_lower(preview.get("preview_id")),
            pair=pair,
            direction=direction,
            entry_type=entry_type,
            requested_price=requested_price,
            fill_price=fill_price,
            filled_units=units,
            slippage=slippage,
            spread=spread,
            opened_timestamp=ts_float,
            status=trade_status or "active",
            trade=dict(trade_output),
            lifecycle_result=dict(preview_trade),
            evidence=evidence,
            evidence_path=evidence_path_value,
            safety=_safe_safety_dict(),
            next_safe_action="paper_fill_complete",
            metadata={
                "trade_payload": fill_payload,
                "config": config,
                "market_state": market_state if isinstance(market_state, Mapping) else {},
                "now_timestamp": ts_float,
                **dict(metadata_payload),
            },
        ).to_dict()
        return result

    blocked_reasons = _ordered_blocked_reasons(blocked_reasons)
    return PaperFillDecision(
        allowed=False,
        decision=PAPER_FILL_BLOCKED,
        blocked_reason=blocked_reasons[0],
        blocked_reasons=blocked_reasons,
        warnings=warnings,
        paper_only=True,
        mode=PAPER_FILL_MODE,
        fill_id="blocked",
        preview_id=_coerce_lower(preview.get("preview_id")) or str(preview.get("preview_id") or "unknown"),
        trade_id=_coerce_lower(preview.get("trade_id")),
        pair=pair,
        direction=direction,
        entry_type=entry_type,
        requested_price=requested_price,
        fill_price=None,
        filled_units=units or 0.0,
        slippage=slippage,
        spread=spread,
        opened_timestamp=None,
        status="candidate",
        trade={},
        lifecycle_result={},
        evidence={},
        evidence_path=evidence_path_value,
        safety=_safe_safety_dict(),
        next_safe_action=_next_safe_action(blocked_reasons[0]),
        metadata={
            "config": config,
            "now_timestamp": ts_float,
            "reason": "validation_failed",
            "market_state_present": isinstance(market_state, Mapping),
            "direction": direction,
            **dict(metadata_payload),
        },
    ).to_dict()
