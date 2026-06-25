from __future__ import annotations

from dataclasses import dataclass, fields, is_dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Mapping


BROKER_READ_ONLY_SNAPSHOT_CONTRACT_VERSION = "broker_read_only_snapshot_contract_v1"
PLACEHOLDER_ACCOUNT_REFERENCE = "DEMO_ACCOUNT_REFERENCE_PRESENT"

BROKER_SNAPSHOT_VALID = "BROKER_SNAPSHOT_VALID"
BROKER_SNAPSHOT_BLOCKED_MISSING_ACCOUNT = "BROKER_SNAPSHOT_BLOCKED_MISSING_ACCOUNT"
BROKER_SNAPSHOT_BLOCKED_MISSING_BALANCE = "BROKER_SNAPSHOT_BLOCKED_MISSING_BALANCE"
BROKER_SNAPSHOT_BLOCKED_MISSING_MARGIN = "BROKER_SNAPSHOT_BLOCKED_MISSING_MARGIN"
BROKER_SNAPSHOT_BLOCKED_UNKNOWN_EXPOSURE = "BROKER_SNAPSHOT_BLOCKED_UNKNOWN_EXPOSURE"
BROKER_SNAPSHOT_BLOCKED_MARKET_CLOSED = "BROKER_SNAPSHOT_BLOCKED_MARKET_CLOSED"
BROKER_SNAPSHOT_BLOCKED_INSTRUMENT_NOT_TRADEABLE = "BROKER_SNAPSHOT_BLOCKED_INSTRUMENT_NOT_TRADEABLE"
BROKER_SNAPSHOT_BLOCKED_SPREAD_MISSING = "BROKER_SNAPSHOT_BLOCKED_SPREAD_MISSING"
BROKER_SNAPSHOT_BLOCKED_STALE_OR_UNRECONCILED = "BROKER_SNAPSHOT_BLOCKED_STALE_OR_UNRECONCILED"
BROKER_SNAPSHOT_BLOCKED_UNSANITIZED = "BROKER_SNAPSHOT_BLOCKED_UNSANITIZED"


@dataclass(frozen=True)
class BrokerReadOnlySnapshot:
    account_present: bool
    account_reference: str
    balance_present: bool
    balance: Decimal
    margin_available_present: bool
    margin_available: Decimal
    open_trades_present: bool
    open_trades: int
    open_positions_present: bool
    open_positions: int
    pending_orders_present: bool
    pending_orders: int
    last_transaction_id_present: bool
    last_transaction_id: str
    market_hours_open: bool
    instrument_tradeable: bool
    spread_present: bool
    spread: Decimal
    timestamp_present: bool
    read_only_reconciled: bool
    no_unknown_open_exposure: bool
    source: str
    sanitized: bool


@dataclass(frozen=True)
class BrokerSnapshotValidationConfig:
    placeholder_account_reference: str = PLACEHOLDER_ACCOUNT_REFERENCE
    require_market_open: bool = True
    require_instrument_tradeable: bool = True
    require_sanitized: bool = True


@dataclass(frozen=True)
class BrokerSnapshotValidationResult:
    engine_version: str
    classification: str
    valid_for_review: bool
    account_reference_allowed: bool
    blockers: tuple[str, ...]
    next_safe_action: str
    snapshot: BrokerReadOnlySnapshot
    demo_execution_allowed: bool
    broker_action_allowed: bool
    real_money_allowed: bool
    compounding_allowed: bool
    bank_movement_allowed: bool
    live_trading_allowed: bool
    credential_access_allowed: bool
    account_id_persistence_allowed: bool


def build_sample_valid_broker_snapshot() -> BrokerReadOnlySnapshot:
    return BrokerReadOnlySnapshot(
        account_present=True,
        account_reference=PLACEHOLDER_ACCOUNT_REFERENCE,
        balance_present=True,
        balance=Decimal("10000.00"),
        margin_available_present=True,
        margin_available=Decimal("9500.00"),
        open_trades_present=True,
        open_trades=0,
        open_positions_present=True,
        open_positions=0,
        pending_orders_present=True,
        pending_orders=0,
        last_transaction_id_present=True,
        last_transaction_id="SANITIZED_TRANSACTION_REFERENCE_PRESENT",
        market_hours_open=True,
        instrument_tradeable=True,
        spread_present=True,
        spread=Decimal("0.8"),
        timestamp_present=True,
        read_only_reconciled=True,
        no_unknown_open_exposure=True,
        source="sanitized_manual_broker_review_snapshot",
        sanitized=True,
    )


def build_sample_missing_account_snapshot() -> BrokerReadOnlySnapshot:
    snapshot = build_sample_valid_broker_snapshot()
    return _replace_snapshot(snapshot, account_present=False, account_reference="")


def build_sample_unknown_exposure_snapshot() -> BrokerReadOnlySnapshot:
    snapshot = build_sample_valid_broker_snapshot()
    return _replace_snapshot(
        snapshot,
        open_trades_present=False,
        open_positions_present=False,
        no_unknown_open_exposure=False,
    )


def build_sample_market_closed_snapshot() -> BrokerReadOnlySnapshot:
    return _replace_snapshot(build_sample_valid_broker_snapshot(), market_hours_open=False)


def validate_broker_read_only_snapshot(
    snapshot: BrokerReadOnlySnapshot | Mapping[str, Any] | None = None,
    config: BrokerSnapshotValidationConfig | Mapping[str, Any] | None = None,
) -> BrokerSnapshotValidationResult:
    active_snapshot = _coerce_snapshot(snapshot or build_sample_valid_broker_snapshot())
    active_config = _coerce_config(config)
    classification = BROKER_SNAPSHOT_VALID
    blockers: list[str] = []

    if active_config.require_sanitized and not active_snapshot.sanitized:
        classification = BROKER_SNAPSHOT_BLOCKED_UNSANITIZED
        blockers.append("broker snapshot is not sanitized")
    elif not active_snapshot.account_present or not _account_reference_allowed(active_snapshot, active_config):
        classification = BROKER_SNAPSHOT_BLOCKED_MISSING_ACCOUNT
        blockers.append("sanitized demo account placeholder is missing")
    elif not active_snapshot.balance_present:
        classification = BROKER_SNAPSHOT_BLOCKED_MISSING_BALANCE
        blockers.append("balance is missing from the read-only snapshot")
    elif not active_snapshot.margin_available_present:
        classification = BROKER_SNAPSHOT_BLOCKED_MISSING_MARGIN
        blockers.append("available margin is missing from the read-only snapshot")
    elif (
        not active_snapshot.open_trades_present
        or not active_snapshot.open_positions_present
        or not active_snapshot.pending_orders_present
        or not active_snapshot.last_transaction_id_present
        or not active_snapshot.no_unknown_open_exposure
    ):
        classification = BROKER_SNAPSHOT_BLOCKED_UNKNOWN_EXPOSURE
        blockers.append("open exposure cannot be reconciled safely")
    elif active_config.require_market_open and not active_snapshot.market_hours_open:
        classification = BROKER_SNAPSHOT_BLOCKED_MARKET_CLOSED
        blockers.append("market hours are closed")
    elif active_config.require_instrument_tradeable and not active_snapshot.instrument_tradeable:
        classification = BROKER_SNAPSHOT_BLOCKED_INSTRUMENT_NOT_TRADEABLE
        blockers.append("instrument is not tradeable")
    elif not active_snapshot.spread_present:
        classification = BROKER_SNAPSHOT_BLOCKED_SPREAD_MISSING
        blockers.append("spread is missing")
    elif not active_snapshot.timestamp_present or not active_snapshot.read_only_reconciled:
        classification = BROKER_SNAPSHOT_BLOCKED_STALE_OR_UNRECONCILED
        blockers.append("snapshot is stale or not reconciled")

    valid = classification == BROKER_SNAPSHOT_VALID
    return BrokerSnapshotValidationResult(
        engine_version=BROKER_READ_ONLY_SNAPSHOT_CONTRACT_VERSION,
        classification=classification,
        valid_for_review=valid,
        account_reference_allowed=_account_reference_allowed(active_snapshot, active_config),
        blockers=tuple(blockers),
        next_safe_action=_next_safe_action(classification),
        snapshot=active_snapshot,
        **_permission_defaults(),
    )


def broker_snapshot_to_jsonable_dict(snapshot: BrokerReadOnlySnapshot | Mapping[str, Any]) -> dict[str, Any]:
    return _json_value(_coerce_snapshot(snapshot))


def broker_snapshot_result_to_operator_text(result: BrokerSnapshotValidationResult | None = None) -> str:
    active = result or validate_broker_read_only_snapshot()
    if active.valid_for_review:
        return (
            "Broker snapshot is review-ready. It is sanitized, read-only, reconciled, "
            "and uses only the demo account placeholder. No trade was placed."
        )
    blockers = "; ".join(active.blockers) if active.blockers else "snapshot did not pass review"
    return f"Broker snapshot is blocked: {blockers}. No trade was placed."


def _replace_snapshot(snapshot: BrokerReadOnlySnapshot, **updates: Any) -> BrokerReadOnlySnapshot:
    values = {field.name: getattr(snapshot, field.name) for field in fields(snapshot)}
    values.update(updates)
    return BrokerReadOnlySnapshot(**values)


def _coerce_snapshot(snapshot: BrokerReadOnlySnapshot | Mapping[str, Any]) -> BrokerReadOnlySnapshot:
    if isinstance(snapshot, BrokerReadOnlySnapshot):
        return snapshot
    values = dict(snapshot)
    for name in ("balance", "margin_available", "spread"):
        values[name] = _to_decimal(values.get(name, "0"))
    return BrokerReadOnlySnapshot(**values)


def _coerce_config(
    config: BrokerSnapshotValidationConfig | Mapping[str, Any] | None,
) -> BrokerSnapshotValidationConfig:
    if config is None:
        return BrokerSnapshotValidationConfig()
    if isinstance(config, BrokerSnapshotValidationConfig):
        return config
    return BrokerSnapshotValidationConfig(**dict(config))


def _account_reference_allowed(
    snapshot: BrokerReadOnlySnapshot, config: BrokerSnapshotValidationConfig
) -> bool:
    return snapshot.account_reference == config.placeholder_account_reference


def _next_safe_action(classification: str) -> str:
    if classification == BROKER_SNAPSHOT_VALID:
        return "Continue to account readiness review; keep broker action locked."
    return "Collect a sanitized read-only demo snapshot; do not request or store account IDs."


def _permission_defaults() -> dict[str, bool]:
    return {
        "demo_execution_allowed": False,
        "broker_action_allowed": False,
        "real_money_allowed": False,
        "compounding_allowed": False,
        "bank_movement_allowed": False,
        "live_trading_allowed": False,
        "credential_access_allowed": False,
        "account_id_persistence_allowed": False,
    }


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
