"""Paper-only forex position sizing helpers."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, Iterable, List, Mapping

POSITION_SIZING_MODE = "PAPER_ONLY"
POSITION_SIZE_ALLOWED = "allowed"
POSITION_SIZE_BLOCKED = "blocked"

REASON_NONE = "none"
REASON_INVALID_ACCOUNT_STATE = "invalid_account_state"
REASON_INVALID_PREVIEW = "invalid_preview"
REASON_NON_PAPER_MODE = "non_paper_mode"
REASON_MISSING_BALANCE = "missing_balance"
REASON_INVALID_BALANCE = "invalid_balance"
REASON_MISSING_ENTRY_PRICE = "missing_entry_price"
REASON_INVALID_ENTRY_PRICE = "invalid_entry_price"
REASON_MISSING_STOP_LOSS = "missing_stop_loss"
REASON_INVALID_STOP_LOSS = "invalid_stop_loss"
REASON_INVALID_STOP_DISTANCE = "invalid_stop_distance"
REASON_INVALID_RISK_PERCENT = "invalid_risk_percent"
REASON_INVALID_RISK_DOLLARS = "invalid_risk_dollars"
REASON_RISK_EXCEEDS_CAP = "risk_exceeds_cap"
REASON_MIN_UNITS_NOT_MET = "min_units_not_met"
REASON_MAX_UNITS_EXCEEDED = "max_units_exceeded"
REASON_INSUFFICIENT_BALANCE = "insufficient_balance"
REASON_UNSUPPORTED_PAIR = "unsupported_pair"
REASON_INVALID_PIP_VALUE = "invalid_pip_value"
REASON_INVALID_ROUNDING = "invalid_rounding"

DEFAULT_SUPPORTED_PAIRS = ("EURUSD", "GBPUSD", "USDJPY")


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
    candidate = _coerce_float(value)
    if candidate is None or candidate <= 0:
        return None
    return candidate


def _coerce_non_negative_float(value: Any) -> float | None:
    candidate = _coerce_float(value)
    if candidate is None or candidate < 0:
        return None
    return candidate


def _coerce_lower(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip().lower()
    return None


def _coerce_upper(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip().upper()
    return None


def _safe_safety_dict() -> Dict[str, Any]:
    return {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def _next_safe_action(first_reason: str | None) -> str:
    if not first_reason or first_reason == REASON_NONE:
        return "proceed_to_risk_governor"
    actions = {
        REASON_NON_PAPER_MODE: "use_paper_only_inputs",
        REASON_INVALID_PREVIEW: "provide_valid_preview",
        REASON_INVALID_ACCOUNT_STATE: "provide_valid_account_state",
        REASON_INVALID_BALANCE: "provide_positive_account_balance",
        REASON_MISSING_BALANCE: "provide_risk_base_or_explicit_risk_dollars",
        REASON_MISSING_ENTRY_PRICE: "add_positive_entry_price",
        REASON_INVALID_ENTRY_PRICE: "fix_entry_price",
        REASON_MISSING_STOP_LOSS: "add_positive_stop_loss",
        REASON_INVALID_STOP_LOSS: "fix_stop_loss",
        REASON_INVALID_STOP_DISTANCE: "increase_stop_distance",
        REASON_INVALID_RISK_PERCENT: "provide_positive_risk_percent",
        REASON_INVALID_RISK_DOLLARS: "use_non_negative_risk_dollars",
        REASON_RISK_EXCEEDS_CAP: "reduce_risk_or_raise_risk_caps",
        REASON_INSUFFICIENT_BALANCE: "reduce_risk",
        REASON_MIN_UNITS_NOT_MET: "reduce_mininimum_unit_limit_or_risk",
        REASON_MAX_UNITS_EXCEEDED: "increase_max_units_or_reduce_risk",
        REASON_UNSUPPORTED_PAIR: "use_supported_pair",
        REASON_INVALID_PIP_VALUE: "fix_pair_pip_value",
        REASON_INVALID_ROUNDING: "fix_rounding_increment",
    }
    return actions.get(first_reason, "review_preview_inputs")


def _dedupe(reasons: List[str]) -> List[str]:
    ordered = []
    for reason in reasons:
        if reason not in ordered:
            ordered.append(reason)
    return ordered


def _get_risk_base(account_state: Any) -> tuple[float | None, bool]:
    if not isinstance(account_state, Mapping):
        return None, False
    keys = ("equity", "current_balance", "cash_balance", "starting_balance")
    values = [account_state.get(key) for key in keys]
    for value in values:
        if not isinstance(value, (int, float)):
            continue
        if value < 0:
            return None, True
    for value in values:
        val = _coerce_positive_float(value)
        if val is not None:
            return val, False
    return None, False


def _get_pair_config(pair: str, pair_config: Any) -> Dict[str, Any]:
    if not isinstance(pair_config, Mapping):
        return {}
    pair_cfg = pair_config.get(pair)
    if isinstance(pair_cfg, Mapping):
        return dict(pair_cfg)
    default_cfg = pair_config.get("default")
    if isinstance(default_cfg, Mapping):
        return dict(default_cfg)
    return {}


def _apply_rounding(units: float, increment: float, allow_fractional: bool) -> float:
    if increment <= 0:
        return units
    factor = units / increment
    if allow_fractional:
        return round(factor) * increment
    return (factor // 1) * increment


@dataclass(frozen=True)
class PositionSizingLimits:
    default_risk_percent: float = 1.0
    max_risk_percent: float = 1.0
    min_units: float = 1.0
    max_units: float = 0.0
    rounding_increment: float = 1.0
    max_risk_dollars: float = 0.0
    allow_fractional_units: bool = False
    supported_pairs: tuple[str, ...] = DEFAULT_SUPPORTED_PAIRS
    max_stop_distance: float | None = None
    max_data_age_seconds: float = 300.0

    @classmethod
    def from_payload(cls, payload: Any) -> "PositionSizingLimits":
        if not isinstance(payload, Mapping):
            return cls()

        default_risk_percent = _coerce_positive_float(payload.get("default_risk_percent")) or cls.default_risk_percent
        max_risk_percent = _coerce_non_negative_float(payload.get("max_risk_percent")) or cls.max_risk_percent
        min_units = _coerce_positive_float(payload.get("min_units")) or cls.min_units
        max_units = _coerce_non_negative_float(payload.get("max_units")) or cls.max_units
        rounding_increment = _coerce_positive_float(payload.get("rounding_increment")) or cls.rounding_increment
        max_risk_dollars = _coerce_non_negative_float(payload.get("max_risk_dollars")) or cls.max_risk_dollars

        allow_fractional_units = payload.get("allow_fractional_units")
        if not isinstance(allow_fractional_units, bool):
            allow_fractional_units = cls.allow_fractional_units

        supported_pairs = cls.supported_pairs
        incoming_pairs = payload.get("supported_pairs")
        if isinstance(incoming_pairs, Iterable) and not isinstance(incoming_pairs, (str, bytes, bytearray)):
            normalized_pairs = []
            for pair in incoming_pairs:
                normalized = _coerce_upper(pair)
                if normalized:
                    normalized_pairs.append(normalized)
            if normalized_pairs:
                seen = []
                for pair in normalized_pairs:
                    if pair not in seen:
                        seen.append(pair)
                supported_pairs = tuple(seen)

        max_stop_distance = _coerce_positive_float(payload.get("max_stop_distance"))
        max_data_age_seconds = _coerce_positive_float(payload.get("max_data_age_seconds")) or cls.max_data_age_seconds

        return cls(
            default_risk_percent=default_risk_percent,
            max_risk_percent=max_risk_percent,
            min_units=min_units,
            max_units=max_units,
            rounding_increment=rounding_increment,
            max_risk_dollars=max_risk_dollars,
            allow_fractional_units=allow_fractional_units,
            supported_pairs=tuple(supported_pairs),
            max_stop_distance=max_stop_distance,
            max_data_age_seconds=max_data_age_seconds,
        )


@dataclass(frozen=True)
class PositionSizingDecision:
    allowed: bool
    decision: str
    blocked_reason: str
    blocked_reasons: List[str]
    warnings: List[str]
    paper_only: bool
    mode: str
    pair: str | None
    direction: str | None
    entry_price: float | None
    stop_loss: float | None
    stop_distance: float | None
    risk_base: float | None
    risk_percent: float | None
    risk_dollars: float
    pip_value: float
    raw_units: float
    units: float
    min_units: float
    max_units: float
    rounding_increment: float
    estimated_loss_at_stop: float
    safety: Dict[str, Any]
    next_safe_action: str
    metadata: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _build_result(
    allowed: bool,
    blocked_reasons: List[str],
    warnings: List[str],
    pair: str | None,
    direction: str | None,
    entry_price: float | None,
    stop_loss: float | None,
    stop_distance: float | None,
    risk_base: float | None,
    risk_percent: float | None,
    risk_dollars: float,
    pip_value: float,
    raw_units: float,
    units: float,
    estimated_loss_at_stop: float,
    limits: PositionSizingLimits,
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    reasons = _dedupe(blocked_reasons)
    blocked_reason = reasons[0] if reasons else REASON_NONE
    return PositionSizingDecision(
        allowed=allowed,
        decision=POSITION_SIZE_ALLOWED if allowed else POSITION_SIZE_BLOCKED,
        blocked_reason=blocked_reason,
        blocked_reasons=reasons,
        warnings=warnings,
        paper_only=True,
        mode=POSITION_SIZING_MODE,
        pair=pair,
        direction=direction,
        entry_price=entry_price,
        stop_loss=stop_loss,
        stop_distance=stop_distance,
        risk_base=risk_base,
        risk_percent=risk_percent,
        risk_dollars=round(risk_dollars, 12),
        pip_value=round(pip_value, 12),
        raw_units=round(raw_units, 12),
        units=round(units, 12),
        min_units=limits.min_units,
        max_units=limits.max_units,
        rounding_increment=limits.rounding_increment,
        estimated_loss_at_stop=round(estimated_loss_at_stop, 12),
        safety=_safe_safety_dict(),
        next_safe_action=_next_safe_action(blocked_reason),
        metadata=metadata,
    ).to_dict()


def calculate_position_size(
    preview: Any,
    account_state: Any = None,
    limits: Any = None,
    pair_config: Any = None,
) -> Dict[str, Any]:
    limits_cfg = PositionSizingLimits.from_payload(limits)
    blocked_reasons: List[str] = []
    warnings: List[str] = []
    metadata: Dict[str, Any] = {}

    if not isinstance(preview, Mapping):
        return _build_result(
            allowed=False,
            blocked_reasons=[REASON_INVALID_PREVIEW],
            warnings=[],
            pair=None,
            direction=None,
            entry_price=None,
            stop_loss=None,
            stop_distance=None,
            risk_base=None,
            risk_percent=None,
            risk_dollars=0.0,
            pip_value=0.0,
            raw_units=0.0,
            units=0.0,
            estimated_loss_at_stop=0.0,
            limits=limits_cfg,
            metadata={"reason": "preview_not_mapping"},
        )

    preview_map = dict(preview)
    preview_pair = _coerce_upper(preview_map.get("pair"))
    preview_direction = _coerce_lower(preview_map.get("direction"))
    paper_only = preview_map.get("paper_only", True)
    mode = _coerce_lower(preview_map.get("mode"))

    # Account checks first to make sure invalid account state can be first in deterministic order.
    risk_base, has_negative_account = _get_risk_base(account_state)
    if has_negative_account:
        blocked_reasons.append(REASON_INVALID_ACCOUNT_STATE)

    # Preview validation
    if paper_only is False:
        blocked_reasons.append(REASON_NON_PAPER_MODE)
    if mode in {"live", "demo", "broker"}:
        blocked_reasons.append(REASON_NON_PAPER_MODE)

    if not preview_pair:
        blocked_reasons.append(REASON_INVALID_PREVIEW)
    elif preview_pair not in limits_cfg.supported_pairs:
        blocked_reasons.append(REASON_UNSUPPORTED_PAIR)

    if preview_direction is not None and preview_direction not in {"buy", "sell"}:
        blocked_reasons.append(REASON_INVALID_PREVIEW)

    entry_price = _coerce_positive_float(preview_map.get("entry_price"))
    if entry_price is None:
        if "entry_price" in preview_map:
            blocked_reasons.append(REASON_INVALID_ENTRY_PRICE)
        else:
            blocked_reasons.append(REASON_MISSING_ENTRY_PRICE)

    stop_loss = _coerce_positive_float(preview_map.get("stop_loss"))
    if stop_loss is None:
        if "stop_loss" in preview_map:
            blocked_reasons.append(REASON_INVALID_STOP_LOSS)
        else:
            blocked_reasons.append(REASON_MISSING_STOP_LOSS)

    stop_distance = None
    if entry_price is not None and stop_loss is not None:
        stop_distance = abs(entry_price - stop_loss)
        if stop_distance <= 0:
            blocked_reasons.append(REASON_INVALID_STOP_DISTANCE)

    risk_percent = _coerce_non_negative_float(preview_map.get("risk_percent"))
    if risk_percent is None:
        risk_percent = limits_cfg.default_risk_percent
    if risk_percent <= 0:
        blocked_reasons.append(REASON_INVALID_RISK_PERCENT)

    risk_dollars_input_present = "risk_dollars" in preview_map
    risk_dollars_input = _coerce_non_negative_float(preview_map.get("risk_dollars")) if risk_dollars_input_present else None
    if risk_dollars_input_present and risk_dollars_input is None:
        blocked_reasons.append(REASON_INVALID_RISK_DOLLARS)

    if (
        not risk_dollars_input_present
        and (risk_base is None or risk_base <= 0)
        and not has_negative_account
    ):
        blocked_reasons.append(REASON_MISSING_BALANCE)

    pair_cfg = _get_pair_config(preview_pair or "", pair_config)
    if pair_cfg:
        pip_value = _coerce_positive_float(pair_cfg.get("pip_value_per_unit"))
        if pip_value is None:
            blocked_reasons.append(REASON_INVALID_PIP_VALUE)
            pip_value = 0.0
    else:
        pip_value = 1.0

    if limits_cfg.rounding_increment <= 0:
        blocked_reasons.append(REASON_INVALID_ROUNDING)

    risk_dollars = (
        risk_dollars_input
        if risk_dollars_input is not None
        else (risk_base or 0.0) * risk_percent / 100.0
    )

    if risk_percent > limits_cfg.max_risk_percent:
        blocked_reasons.append(REASON_RISK_EXCEEDS_CAP)
    if limits_cfg.max_risk_dollars > 0 and risk_dollars > limits_cfg.max_risk_dollars:
        blocked_reasons.append(REASON_RISK_EXCEEDS_CAP)

    if risk_base is not None and risk_dollars > risk_base:
        blocked_reasons.append(REASON_INSUFFICIENT_BALANCE)

    if limits_cfg.max_stop_distance is not None and stop_distance is not None:
        if stop_distance > limits_cfg.max_stop_distance:
            blocked_reasons.append(REASON_INVALID_STOP_DISTANCE)

    raw_units = 0.0
    units = 0.0
    estimated_loss_at_stop = 0.0
    if stop_distance is not None and stop_distance > 0 and pip_value is not None and risk_dollars >= 0:
        if risk_dollars > 0:
            raw_units = risk_dollars / (stop_distance * pip_value)
            units = _apply_rounding(raw_units, limits_cfg.rounding_increment, limits_cfg.allow_fractional_units)
            estimated_loss_at_stop = units * stop_distance * pip_value
            if units < limits_cfg.min_units:
                blocked_reasons.append(REASON_MIN_UNITS_NOT_MET)
            if limits_cfg.max_units > 0 and units > limits_cfg.max_units:
                blocked_reasons.append(REASON_MAX_UNITS_EXCEEDED)

    deterministic_blocked = _dedupe(blocked_reasons)
    allowed = len(deterministic_blocked) == 0

    metadata = {
        "limits": asdict(limits_cfg),
        "pair_config": pair_cfg,
        "paper_only_input": paper_only,
        "mode_input": mode,
    }

    return _build_result(
        allowed=allowed,
        blocked_reasons=deterministic_blocked,
        warnings=warnings,
        pair=preview_pair,
        direction=preview_direction,
        entry_price=entry_price,
        stop_loss=stop_loss,
        stop_distance=stop_distance,
        risk_base=risk_base,
        risk_percent=risk_percent,
        risk_dollars=risk_dollars,
        pip_value=pip_value,
        raw_units=raw_units,
        units=units,
        estimated_loss_at_stop=estimated_loss_at_stop,
        limits=limits_cfg,
        metadata=metadata,
    )
