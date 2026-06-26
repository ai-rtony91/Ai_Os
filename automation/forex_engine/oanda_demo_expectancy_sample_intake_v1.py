from __future__ import annotations

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Any, Mapping, Sequence

from automation.forex_engine.oanda_demo_read_only_pl_result_intake_v1 import (
    EXACT_OWNER_WARNING_TEXT,
    OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_BREAKEVEN,
    OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_LOSS,
    OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_PROFIT,
    PROTECTED_PERMISSION_DEFAULTS,
    RESULT_BUCKET_BREAKEVEN,
    RESULT_BUCKET_LOSS,
    RESULT_BUCKET_PROFIT,
    build_sample_profit_pl_evidence,
    intake_oanda_demo_read_only_pl_result,
    oanda_demo_read_only_pl_result_intake_to_jsonable_dict,
)


VERSION = "oanda_demo_expectancy_sample_intake_v1"
OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_VERSION = VERSION

EXACT_EXPECTANCY_WARNING_TEXT = (
    "Repeated expectancy review only. Codex is not authorized to execute, "
    "call a broker, access credentials, or place orders."
)

OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED = (
    "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED"
)
OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_EMPTY = (
    "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_EMPTY"
)
OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_UNSAFE_RESULT = (
    "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_UNSAFE_RESULT"
)
OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_INCOMPLETE_RESULT = (
    "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_INCOMPLETE_RESULT"
)
OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_MIXED_STRATEGY = (
    "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_MIXED_STRATEGY"
)
OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_MIXED_CANDIDATE = (
    "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_MIXED_CANDIDATE"
)
OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_MIXED_INSTRUMENT = (
    "OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_MIXED_INSTRUMENT"
)

ACCEPTED_INTAKE_CLASSIFICATIONS = {
    OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_PROFIT,
    OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_LOSS,
    OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_BREAKEVEN,
}


@dataclass(frozen=True)
class OandaDemoExpectancySampleIntakeConfig:
    allow_mixed_strategy: bool = False
    allow_mixed_candidate: bool = False
    allow_mixed_instrument: bool = False


@dataclass(frozen=True)
class OandaDemoExpectancySampleInput:
    result_intake_objects: tuple[Mapping[str, Any], ...]


@dataclass(frozen=True)
class OandaDemoExpectancySampleIntakeResult:
    version: str
    classification: str
    sample_review_allowed: bool
    strategy_id: str
    candidate_id: str
    instrument: str
    result_count: int
    accepted_result_buckets: tuple[str, ...]
    sample_items: tuple[Mapping[str, Any], ...]
    blockers: tuple[str, ...]
    owner_warning: str
    expectancy_warning: str
    next_safe_action: str
    permissions: Mapping[str, bool]
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool
    autonomous_execution_allowed: bool
    scheduler_allowed: bool
    daemon_allowed: bool
    webhook_allowed: bool


def build_sample_strong_expectancy_inputs() -> OandaDemoExpectancySampleInput:
    values = (
        Decimal("1.20"),
        Decimal("1.10"),
        Decimal("0.90"),
        Decimal("-0.50"),
        Decimal("1.30"),
        Decimal("0.00"),
        Decimal("1.00"),
        Decimal("-0.40"),
        Decimal("1.40"),
        Decimal("0.80"),
    )
    return OandaDemoExpectancySampleInput(
        result_intake_objects=tuple(
            _build_intake_object(value, index) for index, value in enumerate(values, 1)
        )
    )


def build_sample_weak_mixed_expectancy_inputs() -> OandaDemoExpectancySampleInput:
    values = (
        Decimal("0.40"),
        Decimal("-0.30"),
        Decimal("0.00"),
        Decimal("0.40"),
        Decimal("-0.30"),
    )
    return OandaDemoExpectancySampleInput(
        result_intake_objects=tuple(
            _build_intake_object(value, index) for index, value in enumerate(values, 1)
        )
    )


def build_sample_insufficient_expectancy_inputs() -> OandaDemoExpectancySampleInput:
    values = (Decimal("0.50"), Decimal("-0.20"))
    return OandaDemoExpectancySampleInput(
        result_intake_objects=tuple(
            _build_intake_object(value, index) for index, value in enumerate(values, 1)
        )
    )


def build_sample_losing_expectancy_inputs() -> OandaDemoExpectancySampleInput:
    values = (
        Decimal("0.40"),
        Decimal("-0.60"),
        Decimal("-0.70"),
        Decimal("-0.50"),
        Decimal("-0.60"),
    )
    return OandaDemoExpectancySampleInput(
        result_intake_objects=tuple(
            _build_intake_object(value, index) for index, value in enumerate(values, 1)
        )
    )


def build_sample_unsafe_expectancy_inputs() -> OandaDemoExpectancySampleInput:
    sample = list(build_sample_strong_expectancy_inputs().result_intake_objects)
    unsafe = dict(sample[0])
    unsafe["classification"] = "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_UNSAFE"
    unsafe["safe_to_route"] = False
    sample[0] = unsafe
    return OandaDemoExpectancySampleInput(result_intake_objects=tuple(sample))


def intake_oanda_demo_expectancy_sample(
    sample_input: OandaDemoExpectancySampleInput | Mapping[str, Any] | None = None,
    config: OandaDemoExpectancySampleIntakeConfig | None = None,
) -> OandaDemoExpectancySampleIntakeResult:
    active_input = _coerce_input(sample_input or build_sample_strong_expectancy_inputs())
    active_config = config or OandaDemoExpectancySampleIntakeConfig()
    permissions = dict(PROTECTED_PERMISSION_DEFAULTS)
    raw_items = [dict(item) for item in active_input.result_intake_objects]
    classification, blockers = _classify(raw_items, active_config)
    accepted = classification == OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED
    sample_items = tuple(_sample_item(item) for item in _sorted_items(raw_items)) if accepted else tuple()
    strategy_id = _single_field(sample_items, "strategy_id")
    candidate_id = _single_field(sample_items, "candidate_id")
    instrument = _single_field(sample_items, "instrument")
    return OandaDemoExpectancySampleIntakeResult(
        version=VERSION,
        classification=classification,
        sample_review_allowed=accepted,
        strategy_id=strategy_id,
        candidate_id=candidate_id,
        instrument=instrument,
        result_count=len(sample_items),
        accepted_result_buckets=tuple(str(item.get("result_bucket", "")) for item in sample_items),
        sample_items=sample_items,
        blockers=tuple(blockers),
        owner_warning=EXACT_OWNER_WARNING_TEXT,
        expectancy_warning=EXACT_EXPECTANCY_WARNING_TEXT,
        next_safe_action=_next_safe_action(classification),
        permissions=permissions,
        **permissions,
    )


def oanda_demo_expectancy_sample_intake_to_jsonable_dict(
    result: OandaDemoExpectancySampleIntakeResult,
) -> dict[str, Any]:
    return {
        "version": result.version,
        "classification": result.classification,
        "sample_review_allowed": result.sample_review_allowed,
        "strategy_id": result.strategy_id,
        "candidate_id": result.candidate_id,
        "instrument": result.instrument,
        "result_count": result.result_count,
        "accepted_result_buckets": list(result.accepted_result_buckets),
        "sample_items": _json_value(result.sample_items),
        "blockers": list(result.blockers),
        "owner_warning": result.owner_warning,
        "expectancy_warning": result.expectancy_warning,
        "next_safe_action": result.next_safe_action,
        "permissions": dict(result.permissions),
        **dict(result.permissions),
        "no_trade_placed_by_this_packet": True,
        "no_broker_call_made_by_this_packet": True,
        "mutates_existing_ledger_file": False,
        "preview_only": True,
    }


def oanda_demo_expectancy_sample_intake_to_operator_text(
    result: OandaDemoExpectancySampleIntakeResult,
) -> str:
    return "\n".join(
        (
            f"Repeated expectancy sample intake status: {result.classification}.",
            f"Result count: {result.result_count}.",
            result.expectancy_warning,
            "Repeated expectancy proof is not live execution authority.",
            "No trade placed by this packet.",
            "No broker call made by this packet.",
        )
    )


def oanda_demo_expectancy_sample_intake_to_markdown(
    result: OandaDemoExpectancySampleIntakeResult,
) -> str:
    lines = [
        "# AIOS Forex OANDA Demo Expectancy Sample Intake V1",
        "",
        "## Status",
        f"- Classification: `{result.classification}`",
        f"- Result count: `{result.result_count}`",
        f"- Strategy: `{result.strategy_id}`",
        f"- Candidate: `{result.candidate_id}`",
        f"- Instrument: `{result.instrument}`",
        "",
        "## Safety",
        "- Repeated expectancy proof is not live execution authority.",
        "- No trade placed by this packet.",
        "- No broker call made by this packet.",
        "- All protected permission flags remain false.",
    ]
    return "\n".join(lines) + "\n"


def _build_intake_object(realized_pl: Decimal, index: int) -> dict[str, Any]:
    evidence = replace(
        build_sample_profit_pl_evidence(),
        trade_reference=f"SANITIZED_DEMO_EXPECTANCY_REF_{index:03d}",
        realized_pl=realized_pl,
        result=_result_text(realized_pl),
        close_time=f"2026-06-24T15:{index:02d}:00Z",
        open_time=f"2026-06-24T14:{index:02d}:00Z",
    )
    return oanda_demo_read_only_pl_result_intake_to_jsonable_dict(
        intake_oanda_demo_read_only_pl_result(evidence)
    )


def _result_text(realized_pl: Decimal) -> str:
    if realized_pl > Decimal("0"):
        return "FILLED_PROFIT"
    if realized_pl < Decimal("0"):
        return "FILLED_LOSS"
    return "FILLED_FLAT"


def _coerce_input(
    sample_input: OandaDemoExpectancySampleInput | Mapping[str, Any],
) -> OandaDemoExpectancySampleInput:
    if isinstance(sample_input, OandaDemoExpectancySampleInput):
        return sample_input
    raw = dict(sample_input)
    return OandaDemoExpectancySampleInput(
        result_intake_objects=tuple(raw.get("result_intake_objects", ()))
    )


def _classify(
    raw_items: Sequence[Mapping[str, Any]],
    config: OandaDemoExpectancySampleIntakeConfig,
) -> tuple[str, list[str]]:
    if not raw_items:
        return OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_EMPTY, ["sample_empty"]
    blockers: list[str] = []
    for item in raw_items:
        blockers.extend(_item_blockers(item))
    if any(blocker.startswith("unsafe:") for blocker in blockers):
        return OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_UNSAFE_RESULT, blockers
    if blockers:
        return OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_INCOMPLETE_RESULT, blockers
    sample_items = tuple(_sample_item(item) for item in raw_items)
    if not config.allow_mixed_strategy and len({item["strategy_id"] for item in sample_items}) > 1:
        return OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_MIXED_STRATEGY, ["mixed_strategy_id"]
    if not config.allow_mixed_candidate and len({item["candidate_id"] for item in sample_items}) > 1:
        return OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_MIXED_CANDIDATE, ["mixed_candidate_id"]
    if not config.allow_mixed_instrument and len({item["instrument"] for item in sample_items}) > 1:
        return OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_MIXED_INSTRUMENT, ["mixed_instrument"]
    return OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED, []


def _item_blockers(item: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    classification = str(item.get("classification", ""))
    if classification not in ACCEPTED_INTAKE_CLASSIFICATIONS:
        if "UNSAFE" in classification or "NOT_SANITIZED" in classification:
            blockers.append(f"unsafe:classification:{classification}")
        else:
            blockers.append(f"incomplete:classification:{classification}")
    if item.get("safe_to_route") is not True and classification in ACCEPTED_INTAKE_CLASSIFICATIONS:
        blockers.append("unsafe:safe_to_route_false")
    sanitized = dict(item.get("sanitized_evidence", {}))
    if sanitized.get("sanitized") is not True:
        blockers.append("unsafe:not_sanitized")
    if sanitized.get("broker") != "OANDA_DEMO":
        blockers.append("unsafe:non_demo_broker")
    if sanitized.get("environment") != "DEMO":
        blockers.append("unsafe:non_demo_environment")
    if sanitized.get("broker_reconciled") is not True:
        blockers.append("incomplete:not_reconciled")
    if sanitized.get("read_only_capture") is not True:
        blockers.append("unsafe:not_read_only_capture")
    for key in (
        "raw_payload_included",
        "account_id_included",
        "credential_included",
        "broker_order_id_included",
        "private_account_data_included",
    ):
        if sanitized.get(key) is True:
            blockers.append(f"unsafe:{key}")
    for flag in PROTECTED_PERMISSION_DEFAULTS:
        if item.get(flag) is True:
            blockers.append(f"unsafe:protected_flag_true:{flag}")
    if not sanitized.get("close_time"):
        blockers.append("incomplete:close_time_required")
    if _optional_decimal(item.get("planned_risk")) is None or _optional_decimal(item.get("planned_risk")) <= Decimal("0"):
        blockers.append("incomplete:planned_risk_must_be_positive")
    if _optional_decimal(item.get("realized_pl")) is None:
        blockers.append("incomplete:realized_pl_required")
    if _optional_decimal(item.get("realized_r_multiple")) is None:
        blockers.append("incomplete:realized_r_multiple_required")
    if str(item.get("result_bucket", "")) not in {
        RESULT_BUCKET_PROFIT,
        RESULT_BUCKET_LOSS,
        RESULT_BUCKET_BREAKEVEN,
    }:
        blockers.append("incomplete:unsupported_result_bucket")
    return blockers


def _sorted_items(raw_items: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
    return sorted(raw_items, key=lambda item: str(dict(item.get("sanitized_evidence", {})).get("close_time", "")))


def _sample_item(item: Mapping[str, Any]) -> dict[str, Any]:
    sanitized = dict(item.get("sanitized_evidence", {}))
    return {
        "trade_reference": sanitized.get("trade_reference", ""),
        "strategy_id": sanitized.get("strategy_id", ""),
        "candidate_id": sanitized.get("candidate_id", ""),
        "instrument": sanitized.get("instrument", ""),
        "direction": sanitized.get("direction", ""),
        "close_time": sanitized.get("close_time", ""),
        "result_bucket": item.get("result_bucket", ""),
        "realized_pl": _optional_decimal(item.get("realized_pl")),
        "planned_risk": _optional_decimal(item.get("planned_risk")),
        "realized_r_multiple": _optional_decimal(item.get("realized_r_multiple")),
        "broker": sanitized.get("broker", ""),
        "environment": sanitized.get("environment", ""),
        "broker_reconciled": sanitized.get("broker_reconciled", False),
        "read_only_capture": sanitized.get("read_only_capture", False),
    }


def _single_field(items: Sequence[Mapping[str, Any]], field: str) -> str:
    values = [str(item.get(field, "")) for item in items if item.get(field, "")]
    return values[0] if values else ""


def _next_safe_action(classification: str) -> str:
    if classification == OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_ACCEPTED:
        return "Route the accepted sanitized sample into repeated expectancy accumulation preview."
    if classification == OANDA_DEMO_EXPECTANCY_SAMPLE_INTAKE_BLOCKED_EMPTY:
        return "Add sanitized read-only P/L result-intake objects before expectancy review."
    return "Repair the sample inputs before repeated expectancy accumulation continues."


def _optional_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    return Decimal(str(value))


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): _json_value(child) for key, child in value.items()}
    if isinstance(value, tuple):
        return [_json_value(child) for child in value]
    if isinstance(value, list):
        return [_json_value(child) for child in value]
    return value
