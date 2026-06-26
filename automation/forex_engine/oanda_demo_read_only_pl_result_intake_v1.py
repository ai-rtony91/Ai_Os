from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping

VERSION = "oanda_demo_read_only_pl_result_intake_v1"
OANDA_DEMO_READ_ONLY_PL_RESULT_INTAKE_VERSION = VERSION

OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_PROFIT = (
    "OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_PROFIT"
)
OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_LOSS = (
    "OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_LOSS"
)
OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_BREAKEVEN = (
    "OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_BREAKEVEN"
)
OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_INCOMPLETE = (
    "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_INCOMPLETE"
)
OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_UNSAFE = (
    "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_UNSAFE"
)
OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_NOT_SANITIZED = (
    "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_NOT_SANITIZED"
)
OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_MISSING_RECONCILIATION = (
    "OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_MISSING_RECONCILIATION"
)

RESULT_BUCKET_PROFIT = "PROFIT"
RESULT_BUCKET_LOSS = "LOSS"
RESULT_BUCKET_BREAKEVEN = "BREAKEVEN"
RESULT_BUCKET_INCOMPLETE = "INCOMPLETE"

EXACT_OWNER_WARNING_TEXT = "Do not execute unless Anthony explicitly approves."
EXACT_READ_ONLY_WARNING_TEXT = (
    "Read-only P/L evidence intake only. Codex is not authorized to execute, "
    "call a broker, access credentials, or place orders."
)

PROTECTED_PERMISSION_DEFAULTS = {
    "demo_execution_allowed": False,
    "broker_action_allowed": False,
    "real_money_allowed": False,
    "compounding_allowed": False,
    "bank_movement_allowed": False,
    "live_trading_allowed": False,
    "credential_access_allowed": False,
    "account_id_persistence_allowed": False,
    "autonomous_execution_allowed": False,
    "scheduler_allowed": False,
    "daemon_allowed": False,
    "webhook_allowed": False,
}


@dataclass(frozen=True)
class OandaDemoReadOnlyPlResultIntakeConfig:
    expected_broker: str = "OANDA_DEMO"
    expected_environment: str = "DEMO"


@dataclass(frozen=True)
class OandaDemoReadOnlyPlEvidence:
    sanitized: bool
    broker: str
    environment: str
    trade_reference: str
    strategy_id: str
    candidate_id: str
    instrument: str
    direction: str
    planned_units: int
    actual_units: int
    planned_entry: Decimal
    actual_entry: Decimal
    planned_stop_loss: Decimal
    actual_stop_loss: Decimal
    planned_take_profit: Decimal
    actual_take_profit: Decimal
    planned_risk: Decimal
    realized_pl: Decimal | None
    result: str
    open_time: str
    close_time: str
    broker_reconciled: bool
    read_only_capture: bool
    raw_payload_included: bool
    account_id_included: bool
    credential_included: bool
    broker_order_id_included: bool
    private_account_data_included: bool
    notes: str


@dataclass(frozen=True)
class OandaDemoReadOnlyPlResultIntakeResult:
    version: str
    classification: str
    result_bucket: str
    sanitized_evidence: Mapping[str, Any]
    realized_pl: Decimal | None
    planned_risk: Decimal
    realized_r_multiple: Decimal | None
    planned_vs_actual: Mapping[str, Any]
    safe_to_route: bool
    blockers: tuple[str, ...]
    owner_warning: str
    read_only_warning: str
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


def build_sample_profit_pl_evidence() -> OandaDemoReadOnlyPlEvidence:
    return _base_evidence(realized_pl=Decimal("1.20"), result="FILLED_PROFIT")


def build_sample_loss_pl_evidence() -> OandaDemoReadOnlyPlEvidence:
    return _base_evidence(realized_pl=Decimal("-0.80"), result="FILLED_LOSS")


def build_sample_breakeven_pl_evidence() -> OandaDemoReadOnlyPlEvidence:
    return _base_evidence(realized_pl=Decimal("0.00"), result="FILLED_FLAT")


def build_sample_incomplete_pl_evidence() -> OandaDemoReadOnlyPlEvidence:
    return _base_evidence(
        realized_pl=None,
        result="",
        close_time="",
    )


def build_sample_unsafe_pl_evidence() -> OandaDemoReadOnlyPlEvidence:
    return _base_evidence(
        realized_pl=Decimal("1.20"),
        result="FILLED_PROFIT",
        raw_payload_included=True,
        account_id_included=True,
        credential_included=True,
        broker_order_id_included=True,
        private_account_data_included=True,
    )


def intake_oanda_demo_read_only_pl_result(
    evidence: OandaDemoReadOnlyPlEvidence | Mapping[str, Any] | None = None,
    config: OandaDemoReadOnlyPlResultIntakeConfig | None = None,
) -> OandaDemoReadOnlyPlResultIntakeResult:
    active_config = config or OandaDemoReadOnlyPlResultIntakeConfig()
    active_evidence = _coerce_evidence(evidence or build_sample_profit_pl_evidence())
    blockers = _blockers(active_evidence, active_config)
    result_bucket = _result_bucket(active_evidence.realized_pl)
    classification = _classification(active_evidence, blockers, result_bucket)
    safe_to_route = classification in {
        OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_PROFIT,
        OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_LOSS,
        OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_BREAKEVEN,
    }
    permissions = dict(PROTECTED_PERMISSION_DEFAULTS)
    return OandaDemoReadOnlyPlResultIntakeResult(
        version=VERSION,
        classification=classification,
        result_bucket=result_bucket,
        sanitized_evidence=_sanitized_evidence(active_evidence),
        realized_pl=active_evidence.realized_pl,
        planned_risk=active_evidence.planned_risk,
        realized_r_multiple=_realized_r_multiple(
            active_evidence.realized_pl, active_evidence.planned_risk
        ),
        planned_vs_actual=_planned_vs_actual(active_evidence),
        safe_to_route=safe_to_route,
        blockers=tuple(blockers),
        owner_warning=EXACT_OWNER_WARNING_TEXT,
        read_only_warning=EXACT_READ_ONLY_WARNING_TEXT,
        next_safe_action=_next_safe_action(classification),
        permissions=permissions,
        **permissions,
    )


def oanda_demo_read_only_pl_result_intake_to_jsonable_dict(
    result: OandaDemoReadOnlyPlResultIntakeResult,
) -> dict[str, Any]:
    return {
        "version": result.version,
        "classification": result.classification,
        "result_bucket": result.result_bucket,
        "sanitized_evidence": _json_value(result.sanitized_evidence),
        "realized_pl": _json_value(result.realized_pl),
        "planned_risk": _json_value(result.planned_risk),
        "realized_r_multiple": _json_value(result.realized_r_multiple),
        "planned_vs_actual": _json_value(result.planned_vs_actual),
        "safe_to_route": result.safe_to_route,
        "blockers": list(result.blockers),
        "owner_warning": result.owner_warning,
        "read_only_warning": result.read_only_warning,
        "next_safe_action": result.next_safe_action,
        "permissions": dict(result.permissions),
        **dict(result.permissions),
        "no_trade_placed_by_this_packet": True,
        "no_broker_call_made_by_this_packet": True,
    }


def oanda_demo_read_only_pl_result_intake_to_operator_text(
    result: OandaDemoReadOnlyPlResultIntakeResult,
) -> str:
    return "\n".join(
        (
            f"Read-only P/L intake status: {result.classification}.",
            f"Result bucket: {result.result_bucket}.",
            f"Realized R multiple: {_json_value(result.realized_r_multiple)}.",
            result.read_only_warning,
            "No trade placed by this packet.",
            "No broker call made by this packet.",
        )
    )


def oanda_demo_read_only_pl_result_intake_to_markdown(
    result: OandaDemoReadOnlyPlResultIntakeResult,
) -> str:
    lines = [
        "# AIOS Forex OANDA Demo Read Only P/L Result Intake V1",
        "",
        "## Status",
        f"- Classification: `{result.classification}`",
        f"- Result bucket: `{result.result_bucket}`",
        f"- Safe to route: `{result.safe_to_route}`",
        "",
        "## Warnings",
        f"- {result.owner_warning}",
        f"- {result.read_only_warning}",
        "",
        "## Planned Versus Actual",
    ]
    lines.extend(f"- {key}: `{_json_value(value)}`" for key, value in result.planned_vs_actual.items())
    lines.extend(
        [
            "",
            "## Safety",
            "- No trade placed by this packet.",
            "- No broker call made by this packet.",
            "- All protected permission flags remain false.",
        ]
    )
    return "\n".join(lines) + "\n"


def _base_evidence(
    *,
    realized_pl: Decimal | None,
    result: str,
    sanitized: bool = True,
    broker: str = "OANDA_DEMO",
    environment: str = "DEMO",
    read_only_capture: bool = True,
    broker_reconciled: bool = True,
    raw_payload_included: bool = False,
    account_id_included: bool = False,
    credential_included: bool = False,
    broker_order_id_included: bool = False,
    private_account_data_included: bool = False,
    close_time: str = "2026-06-24T14:42:00Z",
) -> OandaDemoReadOnlyPlEvidence:
    return OandaDemoReadOnlyPlEvidence(
        sanitized=sanitized,
        broker=broker,
        environment=environment,
        trade_reference="SANITIZED_DEMO_TRADE_REF_001",
        strategy_id="strategy_supertrend_review_ready_v1",
        candidate_id="candidate_oanda_demo_pl_001",
        instrument="EUR_USD",
        direction="BUY",
        planned_units=100,
        actual_units=100,
        planned_entry=Decimal("1.08000"),
        actual_entry=Decimal("1.08010"),
        planned_stop_loss=Decimal("1.07800"),
        actual_stop_loss=Decimal("1.07800"),
        planned_take_profit=Decimal("1.08400"),
        actual_take_profit=Decimal("1.08400"),
        planned_risk=Decimal("2.00"),
        realized_pl=realized_pl,
        result=result,
        open_time="2026-06-24T14:30:00Z",
        close_time=close_time,
        broker_reconciled=broker_reconciled,
        read_only_capture=read_only_capture,
        raw_payload_included=raw_payload_included,
        account_id_included=account_id_included,
        credential_included=credential_included,
        broker_order_id_included=broker_order_id_included,
        private_account_data_included=private_account_data_included,
        notes="sanitized read-only P/L evidence sample",
    )


def _coerce_evidence(
    evidence: OandaDemoReadOnlyPlEvidence | Mapping[str, Any],
) -> OandaDemoReadOnlyPlEvidence:
    if isinstance(evidence, OandaDemoReadOnlyPlEvidence):
        return evidence
    raw = dict(evidence)
    return OandaDemoReadOnlyPlEvidence(
        sanitized=bool(raw.get("sanitized")),
        broker=str(raw.get("broker", "")),
        environment=str(raw.get("environment", "")),
        trade_reference=str(raw.get("trade_reference", "")),
        strategy_id=str(raw.get("strategy_id", "")),
        candidate_id=str(raw.get("candidate_id", "")),
        instrument=str(raw.get("instrument", "")),
        direction=str(raw.get("direction", "")),
        planned_units=int(raw.get("planned_units", 0)),
        actual_units=int(raw.get("actual_units", 0)),
        planned_entry=_decimal(raw.get("planned_entry")),
        actual_entry=_decimal(raw.get("actual_entry")),
        planned_stop_loss=_decimal(raw.get("planned_stop_loss")),
        actual_stop_loss=_decimal(raw.get("actual_stop_loss")),
        planned_take_profit=_decimal(raw.get("planned_take_profit")),
        actual_take_profit=_decimal(raw.get("actual_take_profit")),
        planned_risk=_decimal(raw.get("planned_risk")),
        realized_pl=_optional_decimal(raw.get("realized_pl")),
        result=str(raw.get("result", "")),
        open_time=str(raw.get("open_time", "")),
        close_time=str(raw.get("close_time", "")),
        broker_reconciled=bool(raw.get("broker_reconciled")),
        read_only_capture=bool(raw.get("read_only_capture")),
        raw_payload_included=bool(raw.get("raw_payload_included")),
        account_id_included=bool(raw.get("account_id_included")),
        credential_included=bool(raw.get("credential_included")),
        broker_order_id_included=bool(raw.get("broker_order_id_included")),
        private_account_data_included=bool(raw.get("private_account_data_included")),
        notes=str(raw.get("notes", "")),
    )


def _blockers(
    evidence: OandaDemoReadOnlyPlEvidence,
    config: OandaDemoReadOnlyPlResultIntakeConfig,
) -> list[str]:
    blockers: list[str] = []
    if evidence.raw_payload_included:
        blockers.append("raw_payload_included")
    if evidence.account_id_included:
        blockers.append("account_id_included")
    if evidence.credential_included:
        blockers.append("credential_included")
    if evidence.broker_order_id_included:
        blockers.append("broker_order_id_included")
    if evidence.private_account_data_included:
        blockers.append("private_account_data_included")
    if evidence.broker != config.expected_broker:
        blockers.append("broker_must_be_oanda_demo")
    if evidence.environment != config.expected_environment:
        blockers.append("environment_must_be_demo")
    if not evidence.read_only_capture:
        blockers.append("read_only_capture_required")
    if not evidence.sanitized:
        blockers.append("evidence_not_sanitized")
    if not evidence.broker_reconciled:
        blockers.append("broker_reconciliation_missing")
    if evidence.realized_pl is None:
        blockers.append("realized_pl_required")
    if not evidence.result.strip():
        blockers.append("result_required")
    if not evidence.instrument.strip():
        blockers.append("instrument_required")
    if not evidence.direction.strip():
        blockers.append("direction_required")
    if evidence.planned_risk <= Decimal("0"):
        blockers.append("planned_risk_must_be_positive")
    if evidence.actual_units <= 0:
        blockers.append("actual_units_must_be_positive")
    if not evidence.open_time.strip() or not evidence.close_time.strip():
        blockers.append("timestamps_required")
    return blockers


def _classification(
    evidence: OandaDemoReadOnlyPlEvidence,
    blockers: list[str],
    result_bucket: str,
) -> str:
    unsafe = {
        "raw_payload_included",
        "account_id_included",
        "credential_included",
        "broker_order_id_included",
        "private_account_data_included",
        "broker_must_be_oanda_demo",
        "environment_must_be_demo",
        "read_only_capture_required",
    }
    if any(blocker in unsafe for blocker in blockers):
        return OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_UNSAFE
    if "evidence_not_sanitized" in blockers:
        return OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_NOT_SANITIZED
    if "broker_reconciliation_missing" in blockers:
        return OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_MISSING_RECONCILIATION
    incomplete = set(blockers)
    if incomplete:
        return OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_INCOMPLETE
    if result_bucket == RESULT_BUCKET_PROFIT:
        return OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_PROFIT
    if result_bucket == RESULT_BUCKET_LOSS:
        return OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_LOSS
    if result_bucket == RESULT_BUCKET_BREAKEVEN:
        return OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_BREAKEVEN
    return OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_INCOMPLETE


def _result_bucket(realized_pl: Decimal | None) -> str:
    if realized_pl is None:
        return RESULT_BUCKET_INCOMPLETE
    if realized_pl > Decimal("0"):
        return RESULT_BUCKET_PROFIT
    if realized_pl < Decimal("0"):
        return RESULT_BUCKET_LOSS
    return RESULT_BUCKET_BREAKEVEN


def _realized_r_multiple(
    realized_pl: Decimal | None, planned_risk: Decimal
) -> Decimal | None:
    if realized_pl is None or planned_risk <= Decimal("0"):
        return None
    return (realized_pl / planned_risk).quantize(Decimal("0.0001"))


def _planned_vs_actual(evidence: OandaDemoReadOnlyPlEvidence) -> dict[str, Any]:
    return {
        "units_match": evidence.planned_units == evidence.actual_units,
        "stop_loss_match": evidence.planned_stop_loss == evidence.actual_stop_loss,
        "take_profit_match": evidence.planned_take_profit == evidence.actual_take_profit,
        "entry_slippage": evidence.actual_entry - evidence.planned_entry,
        "risk_present": evidence.planned_risk > Decimal("0"),
        "p_l_present": evidence.realized_pl is not None,
    }


def _sanitized_evidence(evidence: OandaDemoReadOnlyPlEvidence) -> dict[str, Any]:
    return {
        "sanitized": evidence.sanitized,
        "broker": evidence.broker,
        "environment": evidence.environment,
        "trade_reference": evidence.trade_reference,
        "strategy_id": evidence.strategy_id,
        "candidate_id": evidence.candidate_id,
        "instrument": evidence.instrument,
        "direction": evidence.direction,
        "planned_units": evidence.planned_units,
        "actual_units": evidence.actual_units,
        "planned_entry": evidence.planned_entry,
        "actual_entry": evidence.actual_entry,
        "planned_stop_loss": evidence.planned_stop_loss,
        "actual_stop_loss": evidence.actual_stop_loss,
        "planned_take_profit": evidence.planned_take_profit,
        "actual_take_profit": evidence.actual_take_profit,
        "planned_risk": evidence.planned_risk,
        "realized_pl": evidence.realized_pl,
        "result": evidence.result,
        "open_time": evidence.open_time,
        "close_time": evidence.close_time,
        "broker_reconciled": evidence.broker_reconciled,
        "read_only_capture": evidence.read_only_capture,
        "raw_payload_included": evidence.raw_payload_included,
        "account_id_included": evidence.account_id_included,
        "credential_included": evidence.credential_included,
        "broker_order_id_included": evidence.broker_order_id_included,
        "private_account_data_included": evidence.private_account_data_included,
        "notes": evidence.notes,
    }


def _next_safe_action(classification: str) -> str:
    if classification in {
        OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_PROFIT,
        OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_LOSS,
        OANDA_DEMO_PL_RESULT_INTAKE_ACCEPTED_BREAKEVEN,
    }:
        return "Review sanitized P/L result and route preview into the local proof ledger bridge."
    if classification == OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_NOT_SANITIZED:
        return "Provide sanitized read-only P/L evidence before result intake."
    if classification == OANDA_DEMO_PL_RESULT_INTAKE_BLOCKED_MISSING_RECONCILIATION:
        return "Provide broker-reconciled sanitized P/L evidence before routing."
    return "Repair missing or unsafe P/L evidence before any proof routing review."


def _decimal(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError):
        return Decimal("0")


def _optional_decimal(value: Any) -> Decimal | None:
    if value is None:
        return None
    return _decimal(value)


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
