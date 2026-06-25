from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


POST_TRADE_EVIDENCE_CAPTURE_VERSION = "post_trade_evidence_capture_v1"

POST_TRADE_EVIDENCE_CAPTURED_PROFIT = "POST_TRADE_EVIDENCE_CAPTURED_PROFIT"
POST_TRADE_EVIDENCE_CAPTURED_LOSS = "POST_TRADE_EVIDENCE_CAPTURED_LOSS"
POST_TRADE_EVIDENCE_CAPTURED_BREAKEVEN = "POST_TRADE_EVIDENCE_CAPTURED_BREAKEVEN"
POST_TRADE_EVIDENCE_BLOCKED_MISSING_RESULT = "POST_TRADE_EVIDENCE_BLOCKED_MISSING_RESULT"
POST_TRADE_EVIDENCE_BLOCKED_NOT_RECONCILED = "POST_TRADE_EVIDENCE_BLOCKED_NOT_RECONCILED"
POST_TRADE_EVIDENCE_BLOCKED_UNSANITIZED = "POST_TRADE_EVIDENCE_BLOCKED_UNSANITIZED"


@dataclass(frozen=True)
class PostTradeEvidenceInput:
    trade_id_reference: str
    strategy_id: str
    instrument: str
    direction: str
    planned_entry: Decimal
    actual_entry: Decimal
    planned_stop_loss: Decimal
    actual_stop_loss: Decimal
    planned_take_profit: Decimal
    actual_take_profit: Decimal
    planned_units: int
    actual_units: int
    open_time: str
    close_time: str
    planned_risk: Decimal
    realized_pl: Decimal | None
    result: str
    slippage: Decimal
    spread_at_entry: Decimal
    spread_at_exit: Decimal
    max_adverse_excursion: Decimal
    max_favorable_excursion: Decimal
    broker_reconciled: bool
    sanitized: bool
    notes: str


@dataclass(frozen=True)
class PostTradeEvidenceResult:
    engine_version: str
    classification: str
    evidence_capture_allowed: bool
    planned_vs_actual: dict[str, Any]
    realized_pl: Decimal | None
    result: str
    blockers: tuple[str, ...]
    next_safe_action: str
    evidence: PostTradeEvidenceInput
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool


def build_sample_post_trade_profit_input() -> PostTradeEvidenceInput:
    return PostTradeEvidenceInput(
        trade_id_reference="SANITIZED_DEMO_TRADE_REFERENCE_PRESENT",
        strategy_id="supertrend",
        instrument="EUR_USD",
        direction="LONG",
        planned_entry=Decimal("1.1000"),
        actual_entry=Decimal("1.1001"),
        planned_stop_loss=Decimal("1.0950"),
        actual_stop_loss=Decimal("1.0950"),
        planned_take_profit=Decimal("1.1100"),
        actual_take_profit=Decimal("1.1100"),
        planned_units=20000,
        actual_units=20000,
        open_time="2026-06-25T09:30:00Z",
        close_time="2026-06-25T11:10:00Z",
        planned_risk=Decimal("100.00"),
        realized_pl=Decimal("185.40"),
        result="PROFIT",
        slippage=Decimal("0.1"),
        spread_at_entry=Decimal("0.8"),
        spread_at_exit=Decimal("0.9"),
        max_adverse_excursion=Decimal("28.50"),
        max_favorable_excursion=Decimal("202.20"),
        broker_reconciled=True,
        sanitized=True,
        notes="Sanitized demo evidence sample; no account identifiers are stored.",
    )


def build_sample_post_trade_loss_input() -> PostTradeEvidenceInput:
    sample = build_sample_post_trade_profit_input()
    return _replace_input(sample, realized_pl=Decimal("-75.20"), result="LOSS")


def build_sample_post_trade_missing_input() -> PostTradeEvidenceInput:
    sample = build_sample_post_trade_profit_input()
    return _replace_input(sample, realized_pl=None, result="")


def capture_post_trade_evidence(
    evidence_input: PostTradeEvidenceInput | Mapping[str, Any] | None = None,
) -> PostTradeEvidenceResult:
    active = _coerce_input(evidence_input or build_sample_post_trade_profit_input())
    classification = _classify(active)
    return PostTradeEvidenceResult(
        engine_version=POST_TRADE_EVIDENCE_CAPTURE_VERSION,
        classification=classification,
        evidence_capture_allowed=classification
        in (
            POST_TRADE_EVIDENCE_CAPTURED_PROFIT,
            POST_TRADE_EVIDENCE_CAPTURED_LOSS,
            POST_TRADE_EVIDENCE_CAPTURED_BREAKEVEN,
        ),
        planned_vs_actual=_planned_vs_actual(active),
        realized_pl=active.realized_pl,
        result=active.result,
        blockers=tuple([] if classification.startswith("POST_TRADE_EVIDENCE_CAPTURED") else [classification.lower()]),
        next_safe_action=_next_safe_action(classification),
        evidence=active,
        demo_execution_allowed=False,
        broker_action_allowed=False,
        real_money_allowed=False,
        compounding_allowed=False,
        bank_movement_allowed=False,
    )


def post_trade_evidence_to_jsonable_dict(result: PostTradeEvidenceResult) -> dict[str, Any]:
    return _json_value(result)


def post_trade_evidence_to_operator_text(result: PostTradeEvidenceResult | None = None) -> str:
    active = result or capture_post_trade_evidence()
    return (
        f"Post-trade evidence status: {active.classification}. Realized P/L: {active.realized_pl}. "
        "Evidence is sanitized and local-only when captured."
    )


def post_trade_evidence_to_markdown(result: PostTradeEvidenceResult | None = None) -> str:
    active = result or capture_post_trade_evidence()
    planned_actual = "\n".join(
        f"- {name}: planned {values['planned']} / actual {values['actual']}"
        for name, values in active.planned_vs_actual.items()
    )
    return "\n".join(
        [
            "# Post-Trade Evidence Capture V1",
            "",
            "No trade was placed by this module. Use it only after a supervised demo trade exists.",
            "",
            f"- Status: {active.classification}",
            f"- Realized P/L: {active.realized_pl}",
            f"- Result: {active.result}",
            "",
            "## Planned Vs Actual",
            planned_actual,
        ]
    )


def _classify(value: PostTradeEvidenceInput) -> str:
    if not value.sanitized:
        return POST_TRADE_EVIDENCE_BLOCKED_UNSANITIZED
    if not value.broker_reconciled:
        return POST_TRADE_EVIDENCE_BLOCKED_NOT_RECONCILED
    if not value.result or value.realized_pl is None:
        return POST_TRADE_EVIDENCE_BLOCKED_MISSING_RESULT
    if value.realized_pl > 0:
        return POST_TRADE_EVIDENCE_CAPTURED_PROFIT
    if value.realized_pl < 0:
        return POST_TRADE_EVIDENCE_CAPTURED_LOSS
    return POST_TRADE_EVIDENCE_CAPTURED_BREAKEVEN


def _planned_vs_actual(value: PostTradeEvidenceInput) -> dict[str, Any]:
    return {
        "entry": {"planned": value.planned_entry, "actual": value.actual_entry},
        "stop_loss": {"planned": value.planned_stop_loss, "actual": value.actual_stop_loss},
        "take_profit": {"planned": value.planned_take_profit, "actual": value.actual_take_profit},
        "units": {"planned": value.planned_units, "actual": value.actual_units},
    }


def _next_safe_action(classification: str) -> str:
    if classification.startswith("POST_TRADE_EVIDENCE_CAPTURED"):
        return "Route sanitized post-trade evidence back into proof modules."
    return "Capture missing sanitized reconciliation evidence before routing feedback."


def _replace_input(value: PostTradeEvidenceInput, **updates: Any) -> PostTradeEvidenceInput:
    raw = {field.name: getattr(value, field.name) for field in fields(value)}
    raw.update(updates)
    return PostTradeEvidenceInput(**raw)


def _coerce_input(value: PostTradeEvidenceInput | Mapping[str, Any]) -> PostTradeEvidenceInput:
    if isinstance(value, PostTradeEvidenceInput):
        return value
    raw = dict(value)
    for name in (
        "planned_entry",
        "actual_entry",
        "planned_stop_loss",
        "actual_stop_loss",
        "planned_take_profit",
        "actual_take_profit",
        "planned_risk",
        "slippage",
        "spread_at_entry",
        "spread_at_exit",
        "max_adverse_excursion",
        "max_favorable_excursion",
    ):
        raw[name] = _to_decimal(raw[name])
    if raw.get("realized_pl") is not None:
        raw["realized_pl"] = _to_decimal(raw["realized_pl"])
    return PostTradeEvidenceInput(**raw)


def _to_decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"invalid decimal value: {value!r}") from exc


def _json_value(value: Any) -> Any:
    if isinstance(value, Decimal):
        return format(value, "f")
    if is_dataclass(value):
        return {field.name: _json_value(getattr(value, field.name)) for field in fields(value)}
    if isinstance(value, tuple):
        return [_json_value(item) for item in value]
    if isinstance(value, list):
        return [_json_value(item) for item in value]
    if isinstance(value, dict):
        return {str(key): _json_value(item) for key, item in value.items()}
    return value
