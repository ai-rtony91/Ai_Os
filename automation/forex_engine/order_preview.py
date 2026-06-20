"""Paper-only order preview hardening."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from automation.forex_engine.position_sizing import calculate_position_size
from automation.forex_engine.risk_governor import evaluate_risk_preview

ORDER_PREVIEW_MODE = "PAPER_ONLY"
ORDER_PREVIEW_ALLOWED = "allowed"
ORDER_PREVIEW_BLOCKED = "blocked"

REASON_NONE = "none"
REASON_INVALID_CANDIDATE = "invalid_candidate"
REASON_INVALID_ACCOUNT_STATE = "invalid_account_state"
REASON_NON_PAPER_MODE = "non_paper_mode"
REASON_LIVE_TRADING_BLOCKED = "live_trading_blocked"
REASON_MISSING_PAIR = "missing_pair"
REASON_MISSING_DIRECTION = "missing_direction"
REASON_MISSING_ENTRY_PRICE = "missing_entry_price"
REASON_MISSING_STOP_LOSS = "missing_stop_loss"
REASON_MISSING_TAKE_PROFIT = "missing_take_profit"
REASON_MISSING_ACCOUNT_STATE = "missing_account_state"
REASON_SIZING_BLOCKED = "sizing_blocked"
REASON_RISK_BLOCKED = "risk_blocked"
REASON_MISSING_SIZING_RESULT = "missing_sizing_result"
REASON_MISSING_RISK_RESULT = "missing_risk_result"
REASON_INVALID_PREVIEW = "invalid_preview"
REASON_EVIDENCE_PATH_INVALID = "evidence_path_invalid"

ENTRY_TYPE_DEFAULT = "market"


def _coerce_str(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip()
    return None


def _coerce_lower(value: Any) -> str | None:
    value_str = _coerce_str(value)
    if value_str is None:
        return None
    return value_str.lower()


def _coerce_upper(value: Any) -> str | None:
    value_str = _coerce_str(value)
    if value_str is None:
        return None
    return value_str.upper()


def _coerce_positive_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        value = float(value)
        return value if value > 0 else None
    try:
        value_float = float(str(value))
    except (TypeError, ValueError):
        return None
    return value_float if value_float > 0 else None


def _coerce_non_negative_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        value = float(value)
        return value if value >= 0 else None
    try:
        value_float = float(str(value))
    except (TypeError, ValueError):
        return None
    return value_float if value_float >= 0 else None


def _safe_safety_dict() -> dict[str, bool]:
    return {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def _dedupe(reasons: list[str]) -> list[str]:
    ordered = []
    for reason in reasons:
        if reason not in ordered:
            ordered.append(reason)
    return ordered


def _ordered_reasons(reasons: list[str]) -> list[str]:
    priority = [
        REASON_MISSING_PAIR,
        REASON_NON_PAPER_MODE,
        REASON_LIVE_TRADING_BLOCKED,
        REASON_MISSING_DIRECTION,
        REASON_MISSING_ENTRY_PRICE,
        REASON_MISSING_STOP_LOSS,
        REASON_MISSING_TAKE_PROFIT,
        REASON_INVALID_PREVIEW,
        REASON_INVALID_CANDIDATE,
    ]
    unique = _dedupe(reasons)
    ordered = [reason for reason in priority if reason in unique]
    ordered.extend(reason for reason in unique if reason not in ordered)
    return ordered


def _next_safe_action(first_reason: str | None) -> str:
    if not first_reason or first_reason == REASON_NONE:
        return "proceed_with_paper_preview"
    actions = {
        REASON_NON_PAPER_MODE: "use_paper_mode_inputs",
        REASON_LIVE_TRADING_BLOCKED: "remove_live_inputs",
        REASON_MISSING_PAIR: "provide_pair",
        REASON_MISSING_DIRECTION: "provide_direction",
        REASON_MISSING_ENTRY_PRICE: "provide_entry_price",
        REASON_MISSING_STOP_LOSS: "provide_stop_loss",
        REASON_MISSING_TAKE_PROFIT: "provide_take_profit",
        REASON_INVALID_ACCOUNT_STATE: "fix_account_state_fields",
        REASON_INVALID_PREVIEW: "fix_preview_fields",
        REASON_INVALID_CANDIDATE: "fix_candidate_payload",
        REASON_SIZING_BLOCKED: "address_sizing_block",
        REASON_RISK_BLOCKED: "address_risk_block",
        REASON_MISSING_ACCOUNT_STATE: "add_account_state",
        REASON_MISSING_SIZING_RESULT: "ensure_sizing_inputs",
        REASON_MISSING_RISK_RESULT: "ensure_risk_inputs",
        REASON_EVIDENCE_PATH_INVALID: "use_relative_metadata_path_only",
    }
    return actions.get(first_reason, "review_preview_inputs")


def _safe_is_relative_str(value: Any) -> tuple[bool, str | None]:
    if value is None:
        return True, None
    if not isinstance(value, str):
        return False, None
    s = value.strip()
    if not s:
        return True, s
    if s.startswith("/") or s.startswith("\\"):
        return False, s
    if ":" in s:
        return False, s
    if "\\\\" in s:
        return False, s
    return True, s


def _split_limits(limits: Any) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    sizing_limits: dict[str, Any] = {}
    risk_limits: dict[str, Any] = {}
    pair_config: dict[str, Any] = {}
    if isinstance(limits, Mapping):
        sizing_limits = limits.get("sizing") if isinstance(limits.get("sizing"), Mapping) else dict(limits)
        risk_limits = limits.get("risk") if isinstance(risk_limits := limits.get("risk"), Mapping) else dict(limits)
        pair_config_raw = limits.get("pair_config")
        if isinstance(pair_config_raw, Mapping):
            pair_config = dict(pair_config_raw)
    return sizing_limits, risk_limits, pair_config


def _risk_gate_required(
    risk_limits: Any,
    market_state: Any,
    open_trades: Any,
    closed_trades: Any,
) -> bool:
    explicit_risk_keys = {
        "max_risk_per_trade_pct",
        "max_total_open_risk_pct",
        "max_daily_loss_pct",
        "max_drawdown_pct",
        "max_open_trades",
        "max_pair_exposure",
        "kill_switch_active",
    }
    if isinstance(risk_limits, Mapping) and any(key in risk_limits for key in explicit_risk_keys):
        return True
    if isinstance(market_state, Mapping) and market_state:
        return True
    if open_trades is not None:
        return True
    if closed_trades is not None:
        return True
    return False


@dataclass(frozen=True)
class OrderPreviewLimits:
    require_account_state: bool = True
    default_entry_type: str = ENTRY_TYPE_DEFAULT

    @classmethod
    def from_payload(cls, payload: Any) -> "OrderPreviewLimits":
        if not isinstance(payload, Mapping):
            return cls()

        default_entry_type = _coerce_lower(payload.get("default_entry_type")) or cls.default_entry_type
        require_account_state = payload.get("require_account_state")
        if not isinstance(require_account_state, bool):
            require_account_state = cls.require_account_state
        return cls(
            default_entry_type=default_entry_type,
            require_account_state=require_account_state,
        )


@dataclass(frozen=True)
class OrderPreviewDecision:
    allowed: bool
    decision: str
    preview_id: str
    blocked_reason: str
    blocked_reasons: list[str]
    warnings: list[str]
    paper_only: bool
    mode: str
    pair: str | None
    direction: str | None
    entry_type: str
    entry_price: float | None
    stop_loss: float | None
    take_profit: float | None
    units: float
    raw_units: float
    dollar_risk: float
    percent_risk: float
    reward_estimate: float
    risk_reward: float
    spread: float
    data_freshness: float | None
    sizing_result: dict[str, Any]
    risk_governor_result: dict[str, Any]
    approval_state: str
    evidence_path: str | None
    safety: dict[str, bool]
    next_safe_action: str
    metadata: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _derive_preview_id(candidate: Mapping[str, Any], now_timestamp: Any | None = None) -> str:
    for key in ("preview_id", "id", "trade_id"):
        value = candidate.get(key)
        if isinstance(value, str):
            s = value.strip()
            if s:
                return s
        elif value is not None:
            return str(value)

    pair = _coerce_upper(candidate.get("pair")) or "UNKNOWN"
    direction = _coerce_lower(candidate.get("direction")) or "unknown"
    entry_type = _coerce_lower(candidate.get("entry_type")) or ENTRY_TYPE_DEFAULT
    entry_price = candidate.get("entry_price")
    stop_loss = candidate.get("stop_loss")
    timestamp = _coerce_str(now_timestamp) or "no-ts"
    return f"{pair}:{direction}:{entry_type}:{entry_price}:{stop_loss}:{timestamp}"


def _coerce_str(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip()
    return None


def build_order_preview(
    candidate: Any,
    account_state: Any = None,
    limits: Any = None,
    market_state: Any = None,
    open_trades: Any = None,
    closed_trades: Any = None,
    now_timestamp: Any = None,
    evidence_path: Any = None,
    metadata: Any = None,
) -> dict[str, Any]:
    limits_cfg = OrderPreviewLimits.from_payload(limits)
    blocked_reasons: list[str] = []
    warnings: list[str] = []
    metadata_payload = dict(metadata) if isinstance(metadata, Mapping) else {}

    if not isinstance(candidate, Mapping):
        blocked_reasons.append(REASON_INVALID_CANDIDATE)
        return OrderPreviewDecision(
            allowed=False,
            decision=ORDER_PREVIEW_BLOCKED,
            preview_id="invalid-candidate",
            blocked_reason=REASON_INVALID_CANDIDATE,
            blocked_reasons=_dedupe(blocked_reasons),
            warnings=warnings,
            paper_only=True,
            mode=ORDER_PREVIEW_MODE,
            pair=None,
            direction=None,
            entry_type=ENTRY_TYPE_DEFAULT,
            entry_price=None,
            stop_loss=None,
            take_profit=None,
            units=0.0,
            raw_units=0.0,
            dollar_risk=0.0,
            percent_risk=0.0,
            reward_estimate=0.0,
            risk_reward=0.0,
            spread=0.0,
            data_freshness=None,
            sizing_result={},
            risk_governor_result={},
            approval_state=ORDER_PREVIEW_BLOCKED,
            evidence_path=_coerce_str(evidence_path),
            safety=_safe_safety_dict(),
            next_safe_action=_next_safe_action(REASON_INVALID_CANDIDATE),
            metadata={
                "limits": asdict(limits_cfg),
                "market_state_present": isinstance(market_state, Mapping),
                "account_state_present": isinstance(account_state, Mapping),
                "now_timestamp": now_timestamp,
                "reason": "candidate_not_mapping",
                **metadata_payload,
            },
        ).to_dict()

    candidate_map = dict(candidate)
    preview_id = _derive_preview_id(candidate_map, now_timestamp)

    pair = _coerce_upper(candidate_map.get("pair"))
    direction = _coerce_lower(candidate_map.get("direction"))
    entry_type = _coerce_lower(candidate_map.get("entry_type")) or ENTRY_TYPE_DEFAULT
    entry_price = _coerce_positive_float(candidate_map.get("entry_price"))
    stop_loss = _coerce_positive_float(candidate_map.get("stop_loss"))
    take_profit = _coerce_positive_float(candidate_map.get("take_profit"))
    paper_only = candidate_map.get("paper_only", True)
    mode = _coerce_lower(candidate_map.get("mode"))
    spread = _coerce_non_negative_float(candidate_map.get("spread")) or 0.0
    data_timestamp = candidate_map.get("data_timestamp")
    risk_percent = candidate_map.get("risk_percent")

    valid_preview = True
    if paper_only is False:
        blocked_reasons.append(REASON_NON_PAPER_MODE)
    if mode in {"live", "demo", "broker"}:
        blocked_reasons.append(REASON_LIVE_TRADING_BLOCKED)

    if not pair:
        blocked_reasons.append(REASON_MISSING_PAIR)
        valid_preview = False
    if not direction:
        blocked_reasons.append(REASON_MISSING_DIRECTION)
        valid_preview = False
    elif direction not in {"buy", "sell"}:
        blocked_reasons.append(REASON_INVALID_PREVIEW)
        valid_preview = False
    if entry_price is None:
        blocked_reasons.append(REASON_MISSING_ENTRY_PRICE)
        valid_preview = False
    if stop_loss is None:
        blocked_reasons.append(REASON_MISSING_STOP_LOSS)
        valid_preview = False
    if take_profit is None:
        blocked_reasons.append(REASON_MISSING_TAKE_PROFIT)
        valid_preview = False

    valid_evidence, evidence_value = _safe_is_relative_str(evidence_path)
    if not valid_evidence:
        blocked_reasons.append(REASON_EVIDENCE_PATH_INVALID)

    if limits_cfg.require_account_state and account_state is None:
        blocked_reasons.append(REASON_MISSING_ACCOUNT_STATE)

    if blocked_reasons:
        invalid_candidate = [REASON_NON_PAPER_MODE, REASON_LIVE_TRADING_BLOCKED]
        if (
            REASON_MISSING_PAIR in blocked_reasons
            or REASON_MISSING_DIRECTION in blocked_reasons
            or REASON_MISSING_ENTRY_PRICE in blocked_reasons
            or REASON_MISSING_STOP_LOSS in blocked_reasons
            or REASON_MISSING_TAKE_PROFIT in blocked_reasons
            or REASON_INVALID_PREVIEW in blocked_reasons
            or REASON_INVALID_CANDIDATE in blocked_reasons
        ):
            blocked_reasons.append(REASON_INVALID_CANDIDATE)

    sizing_limits, risk_limits, pair_config = _split_limits(limits)
    sizing_payload = {
        **candidate_map,
        "entry_type": entry_type,
    }
    if risk_percent is not None:
        sizing_payload["risk_percent"] = risk_percent

    if valid_preview:
        if pair is not None:
            sizing_payload["pair"] = pair
        if direction is not None:
            sizing_payload["direction"] = direction
        sizing_payload["paper_only"] = True
        sizing_payload["mode"] = ORDER_PREVIEW_MODE
        sizing_payload["spread"] = spread
        sizing_payload["data_timestamp"] = data_timestamp
        if not isinstance(sizing_limits, Mapping):
            sizing_limits = {}
    else:
        sizing_limits = sizing_limits if isinstance(sizing_limits, Mapping) else {}

    sizing_result = {}
    risk_result = {}

    if valid_preview:
        try:
            sizing_result = calculate_position_size(
                sizing_payload,
                account_state=account_state,
                limits=sizing_limits,
                pair_config=pair_config,
            )
        except Exception:
            blocked_reasons.append(REASON_MISSING_SIZING_RESULT)

    if not sizing_result and not isinstance(sizing_result, dict):
        blocked_reasons.append(REASON_MISSING_SIZING_RESULT)

    if sizing_result:
        if not sizing_result.get("allowed", False):
            blocked_reasons.append(REASON_SIZING_BLOCKED)
            blocked_reasons.extend([f"{REASON_SIZING_BLOCKED}:{r}" for r in sizing_result.get("blocked_reasons", [])])

    risk_payload = {
        **candidate_map,
        "entry_type": entry_type,
        "pair": pair,
        "direction": direction,
        "entry_price": entry_price,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "paper_only": True,
        "mode": ORDER_PREVIEW_MODE,
        "spread": spread,
        "data_timestamp": data_timestamp,
        "risk_percent": candidate_map.get("risk_percent"),
    }
    risk_payload["paper_only"] = True
    risk_payload["mode"] = ORDER_PREVIEW_MODE
    risk_payload["pair"] = pair
    risk_payload["direction"] = direction
    risk_payload["entry_price"] = entry_price
    risk_payload["stop_loss"] = stop_loss
    risk_payload["take_profit"] = take_profit

    if valid_preview and (not sizing_result or sizing_result.get("allowed", False)):
        try:
            if _risk_gate_required(risk_limits, market_state, open_trades, closed_trades):
                risk_result = evaluate_risk_preview(
                    risk_payload,
                    account_state=account_state,
                    open_trades=open_trades,
                    closed_trades=closed_trades,
                    limits=risk_limits if isinstance(risk_limits, Mapping) else {},
                    market_state=market_state,
                    now_timestamp=now_timestamp,
                )
            else:
                risk_result = {
                    "allowed": True,
                    "blocked_reason": "none",
                    "blocked_reasons": [],
                    "paper_only": True,
                    "mode": ORDER_PREVIEW_MODE,
                }
        except Exception:
            blocked_reasons.append(REASON_MISSING_RISK_RESULT)

    if not risk_result and not isinstance(risk_result, dict):
        blocked_reasons.append(REASON_MISSING_RISK_RESULT)

    if risk_result:
        if risk_result.get("blocked_reason") and risk_result.get("blocked_reason") != "none":
            blocked_reasons.append(REASON_RISK_BLOCKED)
            blocked_reasons.extend([f"{REASON_RISK_BLOCKED}:{r}" for r in risk_result.get("blocked_reasons", [])])

    blocked_reasons = _ordered_reasons(blocked_reasons)
    allowed = not blocked_reasons
    blocked_reason = blocked_reasons[0] if blocked_reasons else REASON_NONE

    if not blocked_reasons and not (
        isinstance(sizing_result, Mapping) and isinstance(risk_result, Mapping)
    ):
        allowed = False
        blocked_reason = REASON_INVALID_PREVIEW
        blocked_reasons.append(REASON_INVALID_PREVIEW)

    preview = OrderPreviewDecision(
        allowed=allowed,
        decision=ORDER_PREVIEW_ALLOWED if allowed else ORDER_PREVIEW_BLOCKED,
        preview_id=preview_id,
        blocked_reason=blocked_reason,
        blocked_reasons=blocked_reasons,
        warnings=warnings,
        paper_only=True,
        mode=ORDER_PREVIEW_MODE,
        pair=pair,
        direction=direction,
        entry_type=entry_type,
        entry_price=entry_price,
        stop_loss=stop_loss,
        take_profit=take_profit,
        units=float(sizing_result.get("units", 0.0)) if isinstance(sizing_result, Mapping) else 0.0,
        raw_units=float(sizing_result.get("raw_units", 0.0)) if isinstance(sizing_result, Mapping) else 0.0,
        dollar_risk=float(sizing_result.get("risk_dollars", 0.0)) if isinstance(sizing_result, Mapping) else 0.0,
        percent_risk=float(sizing_result.get("risk_percent", 0.0)) if isinstance(sizing_result, Mapping) else _coerce_non_negative_float(risk_percent) or 0.0,
        reward_estimate=abs((take_profit or 0.0) - (entry_price or 0.0)) * (float(sizing_result.get("units", 0.0)) if isinstance(sizing_result, Mapping) else 0.0),
        risk_reward=0.0,
        spread=spread,
        data_freshness=(risk_result.get("data_age_seconds") if isinstance(risk_result, Mapping) else None),
        sizing_result=sizing_result if isinstance(sizing_result, Mapping) else {},
        risk_governor_result=risk_result if isinstance(risk_result, Mapping) else {},
        approval_state="paper_preview_ready" if allowed else ORDER_PREVIEW_BLOCKED,
        evidence_path=evidence_value,
        safety=_safe_safety_dict(),
        next_safe_action=_next_safe_action(blocked_reason),
        metadata={
            "limits": asdict(limits_cfg),
            "sizing_limits": dict(sizing_limits) if isinstance(sizing_limits, Mapping) else {},
            "risk_limits": dict(risk_limits) if isinstance(risk_limits, Mapping) else {},
            "pair_config": pair_config if isinstance(pair_config, Mapping) else {},
            "mode_input": mode,
            "paper_only_input": paper_only,
            "now_timestamp": now_timestamp,
            "risk_result_present": isinstance(risk_result, Mapping),
            "sizing_result_present": isinstance(sizing_result, Mapping),
            **metadata_payload,
        },
    ).to_dict()

    dollar_risk = preview["dollar_risk"]
    if dollar_risk > 0:
        preview["risk_reward"] = preview["reward_estimate"] / dollar_risk
    return preview
