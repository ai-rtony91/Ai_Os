from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation
from typing import Any


PACKET_ID = "AIOS-FOREX-FUNDING-READINESS-TRANSFER-GATE-V1"
GATE_VERSION = "v1"

FUNDING_REVIEW_READY = "FUNDING_REVIEW_READY"
FUNDING_REVIEW_BLOCKED_NO_OWNER_INTENT = (
    "FUNDING_REVIEW_BLOCKED_NO_OWNER_INTENT"
)
FUNDING_REVIEW_BLOCKED_OWNER_APPROVAL_MISSING = (
    "FUNDING_REVIEW_BLOCKED_OWNER_APPROVAL_MISSING"
)
FUNDING_REVIEW_BLOCKED_OPEN_EXPOSURE = (
    "FUNDING_REVIEW_BLOCKED_OPEN_EXPOSURE"
)
FUNDING_REVIEW_BLOCKED_BUCKET_NOT_READY = (
    "FUNDING_REVIEW_BLOCKED_BUCKET_NOT_READY"
)
FUNDING_REVIEW_BLOCKED_NEXT_TRADE_NOT_READY = (
    "FUNDING_REVIEW_BLOCKED_NEXT_TRADE_NOT_READY"
)
FUNDING_REVIEW_BLOCKED_RISK_LIMIT = (
    "FUNDING_REVIEW_BLOCKED_RISK_LIMIT"
)
FUNDING_REVIEW_BLOCKED_INVALID_AMOUNT = (
    "FUNDING_REVIEW_BLOCKED_INVALID_AMOUNT"
)
FUNDING_REVIEW_BLOCKED_UNSAFE_INPUT = (
    "FUNDING_REVIEW_BLOCKED_UNSAFE_INPUT"
)

READY_BUCKET_STATUSES = {
    "BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT",
    "BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS",
    "BUCKET_UPDATE_ELIGIBLE_BREAKEVEN",
    "BUCKET_GATE_ELIGIBLE_REALIZED_PROFIT",
    "BUCKET_GATE_ELIGIBLE_REALIZED_LOSS",
    "BUCKET_GATE_ELIGIBLE_BREAKEVEN",
    "RESULT_BUCKET_READY",
    "AIOS_BUCKET_READY",
    "BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_READY",
}
BLOCKED_STATUS_TERMS = ("BLOCKED", "REJECTED", "UNSAFE", "INVALID")

NEXT_TRADE_READY_STATUSES = {
    "NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW",
    "NEXT_TRADE_REVIEW_READY",
    "NEXT_TRADE_READY_FOR_OWNER_REVIEW",
}
NEXT_TRADE_OPEN_EXPOSURE_STATUSES = {
    "NEXT_TRADE_BLOCKED_OPEN_EXPOSURE",
    "FUNDING_REVIEW_BLOCKED_OPEN_EXPOSURE",
}

RISK_LIMIT_BOOLEAN_KEYS = {
    "risk_limit_breached",
    "max_loss_limit_breached",
    "max_loss_exceeded",
    "daily_stop_triggered",
    "daily_loss_limit_breached",
    "kill_switch_active",
    "trading_halt_active",
    "cooldown_active",
    "max_drawdown_exceeded",
    "funding_limit_breached",
    "funding_cap_exceeded",
    "withdrawal_limit_breached",
    "deposit_limit_breached",
}
RISK_BLOCKED_STATUSES = {
    "RISK_LIMIT_BLOCKED",
    "BLOCKED_BY_RISK_LIMIT",
    "RISK_REVIEW_BLOCKED",
    "RISK_BLOCKED",
    "BLOCKED",
    "REJECTED",
}

EXECUTION_AUTHORITY_FIELDS = (
    "funding_transfer_authorized",
    "money_transfer_authorized",
    "deposit_authorized",
    "withdrawal_authorized",
    "bank_call_authorized",
    "broker_call_authorized",
    "oanda_call_authorized",
    "order_placement_authorized",
    "order_execution_authorized",
    "live_trading_authorized",
    "runtime_mutation_authorized",
    "credential_read_authorized",
    "network_call_authorized",
    "scheduler_authorized",
    "daemon_authorized",
    "webhook_authorized",
)

SAFETY_PROOF_FIELDS = (
    "funding_transfer_performed",
    "money_transfer_performed",
    "deposit_performed",
    "withdrawal_performed",
    "bank_call_performed",
    "broker_call_performed",
    "oanda_call_performed",
    "order_placement_performed",
    "order_execution_performed",
    "live_trading_performed",
    "runtime_mutation_performed",
    "credential_read_performed",
    "network_call_performed",
    "scheduler_started",
    "daemon_started",
    "webhook_called",
)

UNSAFE_TRUE_FIELDS = EXECUTION_AUTHORITY_FIELDS + SAFETY_PROOF_FIELDS + (
    "broker_call_allowed",
    "oanda_call_allowed",
    "network_allowed",
    "network_call_allowed",
    "credential_access_allowed",
    "credential_read_allowed",
    "account_id_read_allowed",
    "vault_read_allowed",
    "windows_vault_read_allowed",
    "dotenv_read_allowed",
    "env_read_allowed",
    "order_placement_allowed",
    "order_close_allowed",
    "order_mutation_allowed",
    "trade_mutation_allowed",
    "position_mutation_allowed",
    "live_endpoint_allowed",
    "live_order_allowed",
    "live_funding_allowed",
    "funding_transfer_allowed",
    "deposit_allowed",
    "withdrawal_allowed",
    "bank_call_allowed",
    "bucket_mutation_allowed",
    "runtime_mutation_allowed",
)

SAFE_TRUE_KEYS = {
    "owner_approved_funding_review",
    "review_only",
    "risk_review_only",
    "funding_review_authorized",
    "funding_review_ready",
    "bucket_update_authorized",
    "bucket_gate_ready",
    "aios_bucket_ready",
    "next_trade_review_authorized",
    "next_trade_review_ready",
    "next_trade_eligible_for_owner_review",
    "within_limits",
    "funding_review_within_limits",
}
SENSITIVE_KEY_TERMS = (
    "token",
    "authorization",
    "account_id",
    "accountid",
    "runtime_account_id",
    "credential",
    "secret",
    "password",
    "api_key",
    "apikey",
    "private_key",
    "client_secret",
    "access_key",
)
RAW_PAYLOAD_KEY_TERMS = (
    "raw_payload",
    "rawpayload",
    "raw_broker_payload",
    "broker_payload",
    "broker_response",
    "oanda_response",
)
REQUEST_HEADER_KEY_TERMS = ("headers", "request_headers", "requestheaders")
ENDPOINT_URL_KEY_TERMS = ("url", "endpoint_url", "endpointurl", "endpoint")
ACTION_KEY_TERMS = (
    "network",
    "broker",
    "oanda",
    "credential",
    "vault",
    "dotenv",
    "env",
    "order",
    "trade",
    "position",
    "live",
    "execution",
    "write",
    "mutat",
    "scheduler",
    "daemon",
    "webhook",
    "funding_transfer",
    "money_transfer",
    "deposit",
    "withdraw",
    "withdrawal",
    "bank_call",
)
ACTION_STATE_TERMS = (
    "allowed",
    "performed",
    "started",
    "called",
    "authorized",
    "enabled",
    "used",
    "read",
    "mutated",
    "placed",
    "closed",
    "executed",
    "accessed",
    "connected",
    "sent",
    "posted",
)


def evaluate_funding_readiness_transfer_gate_v1(
    funding_intent: dict | None = None,
    account_separation: dict | None = None,
    bucket_gate_decision: dict | None = None,
    next_trade_eligibility: dict | None = None,
    risk_state: dict | None = None,
    owner_approval: dict | None = None,
) -> dict[str, Any]:
    intent = _mapping(funding_intent)
    separation = _mapping(account_separation)
    bucket = _mapping(bucket_gate_decision)
    next_trade = _mapping(next_trade_eligibility)
    risk = _mapping(risk_state)
    approval = _mapping(owner_approval)

    blockers: list[str] = []
    warnings: list[str] = []
    unsafe_blockers: list[str] = []

    for label, original, payload in (
        ("funding_intent", funding_intent, intent),
        ("account_separation", account_separation, separation),
        ("bucket_gate_decision", bucket_gate_decision, bucket),
        ("next_trade_eligibility", next_trade_eligibility, next_trade),
        ("risk_state", risk_state, risk),
        ("owner_approval", owner_approval, approval),
    ):
        if original is not None and not isinstance(original, Mapping):
            unsafe_blockers.append(f"{label}_must_be_mapping_when_provided")
        if payload:
            unsafe_blockers.extend(_unsafe_input_blockers(payload, label))

    amount = _funding_amount(intent)
    currency = _funding_currency(intent)
    funding_mode = _funding_mode(intent)
    exposure_counts, exposure_blockers = _exposure_counts(separation, next_trade)
    account_status = _status_text(separation)
    bucket_status = _status_text(bucket)
    next_trade_status = _status_text(next_trade)

    if unsafe_blockers:
        return _result(
            gate_status=FUNDING_REVIEW_BLOCKED_UNSAFE_INPUT,
            blockers=unsafe_blockers,
            warnings=warnings,
            amount=amount,
            currency=currency,
            funding_mode=funding_mode,
            account_status=account_status,
            bucket_status=bucket_status,
            next_trade_status=next_trade_status,
            exposure_counts=exposure_counts,
        )

    if not intent:
        return _result(
            gate_status=FUNDING_REVIEW_BLOCKED_NO_OWNER_INTENT,
            blockers=["explicit_funding_intent_required"],
            warnings=warnings,
            amount=amount,
            currency=currency,
            funding_mode=funding_mode,
            account_status=account_status,
            bucket_status=bucket_status,
            next_trade_status=next_trade_status,
            exposure_counts=exposure_counts,
        )

    intent_blockers = _funding_intent_blockers(intent, amount, currency, funding_mode)
    if intent_blockers:
        return _result(
            gate_status=(
                FUNDING_REVIEW_BLOCKED_UNSAFE_INPUT
                if "funding_mode_must_be_review_only" in intent_blockers
                else FUNDING_REVIEW_BLOCKED_INVALID_AMOUNT
            ),
            blockers=intent_blockers,
            warnings=warnings,
            amount=amount,
            currency=currency,
            funding_mode=funding_mode,
            account_status=account_status,
            bucket_status=bucket_status,
            next_trade_status=next_trade_status,
            exposure_counts=exposure_counts,
        )

    if not _owner_approved_funding_review(intent, approval):
        return _result(
            gate_status=FUNDING_REVIEW_BLOCKED_OWNER_APPROVAL_MISSING,
            blockers=["owner_approved_funding_review_true_required"],
            warnings=warnings,
            amount=amount,
            currency=currency,
            funding_mode=funding_mode,
            account_status=account_status,
            bucket_status=bucket_status,
            next_trade_status=next_trade_status,
            exposure_counts=exposure_counts,
        )

    account_blockers = _account_separation_blockers(separation, account_status)
    bucket_blockers = _bucket_gate_blockers(bucket, bucket_status)
    if account_blockers or bucket_blockers:
        return _result(
            gate_status=FUNDING_REVIEW_BLOCKED_BUCKET_NOT_READY,
            blockers=account_blockers + bucket_blockers,
            warnings=warnings,
            amount=amount,
            currency=currency,
            funding_mode=funding_mode,
            account_status=account_status,
            bucket_status=bucket_status,
            next_trade_status=next_trade_status,
            exposure_counts=exposure_counts,
        )

    if exposure_blockers:
        return _result(
            gate_status=FUNDING_REVIEW_BLOCKED_UNSAFE_INPUT,
            blockers=exposure_blockers,
            warnings=warnings,
            amount=amount,
            currency=currency,
            funding_mode=funding_mode,
            account_status=account_status,
            bucket_status=bucket_status,
            next_trade_status=next_trade_status,
            exposure_counts=exposure_counts,
        )

    open_exposure_blockers = _open_exposure_blockers(exposure_counts)
    if (
        next_trade_status in NEXT_TRADE_OPEN_EXPOSURE_STATUSES
        and not open_exposure_blockers
    ):
        open_exposure_blockers.append(
            "next_trade_eligibility_reports_open_exposure"
        )
    if open_exposure_blockers:
        return _result(
            gate_status=FUNDING_REVIEW_BLOCKED_OPEN_EXPOSURE,
            blockers=open_exposure_blockers,
            warnings=warnings,
            amount=amount,
            currency=currency,
            funding_mode=funding_mode,
            account_status=account_status,
            bucket_status=bucket_status,
            next_trade_status=next_trade_status,
            exposure_counts=exposure_counts,
        )

    next_trade_blockers = _next_trade_blockers(next_trade, next_trade_status)
    if next_trade_blockers:
        return _result(
            gate_status=FUNDING_REVIEW_BLOCKED_NEXT_TRADE_NOT_READY,
            blockers=next_trade_blockers,
            warnings=warnings,
            amount=amount,
            currency=currency,
            funding_mode=funding_mode,
            account_status=account_status,
            bucket_status=bucket_status,
            next_trade_status=next_trade_status,
            exposure_counts=exposure_counts,
        )

    risk_blockers = _risk_blockers(risk)
    if risk_blockers:
        return _result(
            gate_status=FUNDING_REVIEW_BLOCKED_RISK_LIMIT,
            blockers=risk_blockers,
            warnings=warnings,
            amount=amount,
            currency=currency,
            funding_mode=funding_mode,
            account_status=account_status,
            bucket_status=bucket_status,
            next_trade_status=next_trade_status,
            exposure_counts=exposure_counts,
        )

    return _result(
        gate_status=FUNDING_REVIEW_READY,
        blockers=blockers,
        warnings=warnings,
        amount=amount,
        currency=currency,
        funding_mode=funding_mode,
        account_status=account_status,
        bucket_status=bucket_status,
        next_trade_status=next_trade_status,
        exposure_counts=exposure_counts,
    )


def funding_readiness_transfer_gate_template_v1() -> dict[str, Any]:
    return {
        "funding_intent": _ready_funding_intent(),
        "account_separation": _ready_account_separation(),
        "bucket_gate_decision": _ready_bucket_gate_decision(),
        "next_trade_eligibility": _ready_next_trade_eligibility(),
        "risk_state": _ready_risk_state(),
        "owner_approval": {"owner_approved_funding_review": True},
        "runtime_input_rule": {
            "sanitized_inputs_only": True,
            "funding_mode_required": "review_only",
            "owner_review_only": True,
            "money_transfer_supported": False,
            "deposit_supported": False,
            "withdrawal_supported": False,
            "broker_or_oanda_call_supported": False,
            "order_placement_supported": False,
            "runtime_mutation_supported": False,
            "live_trading_supported": False,
        },
    }


def funding_readiness_transfer_gate_samples_v1() -> dict[str, dict[str, Any]]:
    ready = funding_readiness_transfer_gate_template_v1()
    return {
        "ready": ready,
        "no-intent": {
            **ready,
            "funding_intent": None,
        },
        "approval-missing": {
            **ready,
            "owner_approval": {"owner_approved_funding_review": False},
        },
        "open-exposure": {
            **ready,
            "next_trade_eligibility": {
                **_ready_next_trade_eligibility(),
                "gate_status": "NEXT_TRADE_BLOCKED_OPEN_EXPOSURE",
                "open_trade_count": 1,
            },
        },
        "invalid-amount": {
            **ready,
            "funding_intent": {
                **_ready_funding_intent(),
                "proposed_amount": "0",
            },
        },
        "unsafe": {
            **ready,
            "funding_intent": {
                **_ready_funding_intent(),
                "api_key": "sk-sample-unsafe-not-a-real-key",
            },
        },
    }


def _result(
    *,
    gate_status: str,
    blockers: Sequence[str],
    warnings: Sequence[str],
    amount: Decimal | None,
    currency: str,
    funding_mode: str,
    account_status: str,
    bucket_status: str,
    next_trade_status: str,
    exposure_counts: Mapping[str, int],
) -> dict[str, Any]:
    review_authorized = gate_status == FUNDING_REVIEW_READY
    safety = _safety_proof()
    execution_authority = _execution_authority()
    result: dict[str, Any] = {
        "packet_id": PACKET_ID,
        "gate_version": GATE_VERSION,
        "gate_status": gate_status,
        "blockers": _unique(blockers),
        "warnings": _unique(_warnings(gate_status) + list(warnings)),
        "funding_review_authorized": review_authorized,
        "funding_transfer_authorized": False,
        "deposit_authorized": False,
        "withdrawal_authorized": False,
        "broker_call_authorized": False,
        "oanda_call_authorized": False,
        "order_placement_authorized": False,
        "live_trading_authorized": False,
        "runtime_mutation_authorized": False,
        "proposed_amount": _decimal_text_or_none(amount),
        "proposed_currency": currency or None,
        "funding_mode": funding_mode or None,
        "account_separation_status": account_status or "UNKNOWN",
        "bucket_gate_status": bucket_status or "UNKNOWN",
        "next_trade_status": next_trade_status or "UNKNOWN",
        "open_trade_count": exposure_counts.get("open_trade_count", 0),
        "open_position_count": exposure_counts.get("open_position_count", 0),
        "pending_order_count": exposure_counts.get("pending_order_count", 0),
        "readiness_checks": _readiness_checks(
            gate_status=gate_status,
            amount=amount,
            currency=currency,
            funding_mode=funding_mode,
            account_status=account_status,
            bucket_status=bucket_status,
            next_trade_status=next_trade_status,
            exposure_counts=exposure_counts,
        ),
        "safety_proof": safety,
        "execution_authority": execution_authority,
        "next_safe_action": _next_safe_action(gate_status),
    }
    result.update(safety)
    result.update(execution_authority)
    return result


def _ready_funding_intent() -> dict[str, Any]:
    return {
        "funding_intent_present": True,
        "funding_mode": "review_only",
        "proposed_amount": "100.00",
        "proposed_currency": "USD",
        "source_bucket": "RESERVE_ACCOUNT",
        "target_bucket": "TRADING_FLOAT",
        "owner_approved_funding_review": True,
    }


def _ready_account_separation() -> dict[str, Any]:
    return {
        "status": "BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_READY",
        "open_trade_count": 0,
        "open_position_count": 0,
        "pending_order_count": 0,
        "withdraw_allowed": False,
        "compound_allowed": False,
        "live_allocation_allowed": False,
        "execution_authority": _execution_authority(),
        "safety_proof": _safety_proof(),
    }


def _ready_bucket_gate_decision() -> dict[str, Any]:
    return {
        "gate_status": "BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT",
        "bucket_update_authorized": True,
        "bucket_update_performed": False,
        "bucket_mutation_performed": False,
        "funding_transfer_authorized": False,
        "live_funding_authorized": False,
    }


def _ready_next_trade_eligibility() -> dict[str, Any]:
    return {
        "gate_status": "NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW",
        "next_trade_review_authorized": True,
        "next_trade_authorized": False,
        "open_trade_count": 0,
        "open_position_count": 0,
        "pending_order_count": 0,
        "order_placement_authorized": False,
        "broker_call_authorized": False,
        "live_funding_authorized": False,
    }


def _ready_risk_state(**overrides: Any) -> dict[str, Any]:
    state: dict[str, Any] = {
        "review_only": True,
        "risk_review_only": True,
        "within_limits": True,
        "funding_review_within_limits": True,
        "risk_limit_breached": False,
        "max_loss_limit_breached": False,
        "daily_stop_triggered": False,
        "kill_switch_active": False,
        "trading_halt_active": False,
        "live_trading_allowed": False,
    }
    state.update(overrides)
    return state


def _funding_intent_blockers(
    intent: Mapping[str, Any],
    amount: Decimal | None,
    currency: str,
    funding_mode: str,
) -> list[str]:
    blockers: list[str] = []
    if amount is None or amount <= 0:
        blockers.append("proposed_amount_must_be_positive")
    if not currency:
        blockers.append("proposed_currency_required")
    if funding_mode != "review_only":
        blockers.append("funding_mode_must_be_review_only")
    if intent.get("funding_intent_present") is False:
        blockers.append("funding_intent_present_must_not_be_false")
    return blockers


def _owner_approved_funding_review(
    intent: Mapping[str, Any],
    approval: Mapping[str, Any],
) -> bool:
    if approval:
        return approval.get("owner_approved_funding_review") is True
    return (
        intent.get("owner_approved_funding_review") is True
    )


def _account_separation_blockers(
    account_separation: Mapping[str, Any],
    status: str,
) -> list[str]:
    if not account_separation:
        return ["account_separation_state_required"]
    if _status_blocked(status):
        return [f"account_separation_status_not_ready_{status}"]
    if status and status not in READY_BUCKET_STATUSES and "READY" not in status:
        return [f"account_separation_status_not_ready_{status}"]
    return []


def _bucket_gate_blockers(
    bucket_gate_decision: Mapping[str, Any],
    status: str,
) -> list[str]:
    if not bucket_gate_decision:
        return ["aios_bucket_or_bucket_gate_state_required"]
    if bucket_gate_decision.get("bucket_gate_ready") is True:
        return []
    if bucket_gate_decision.get("aios_bucket_ready") is True:
        return []
    if bucket_gate_decision.get("bucket_update_authorized") is True:
        return []
    if status in READY_BUCKET_STATUSES:
        return []
    if _status_blocked(status):
        return [f"bucket_gate_status_not_ready_{status}"]
    return [f"bucket_gate_status_not_ready_{status or 'UNKNOWN'}"]


def _next_trade_blockers(
    next_trade_eligibility: Mapping[str, Any],
    status: str,
) -> list[str]:
    if not next_trade_eligibility:
        return ["next_trade_eligibility_state_required"]
    if status in NEXT_TRADE_READY_STATUSES:
        return []
    if next_trade_eligibility.get("next_trade_review_authorized") is True:
        return []
    if next_trade_eligibility.get("next_trade_review_ready") is True:
        return []
    if next_trade_eligibility.get("next_trade_eligible_for_owner_review") is True:
        return []
    return [f"next_trade_status_not_ready_{status or 'UNKNOWN'}"]


def _risk_blockers(risk: Mapping[str, Any]) -> list[str]:
    if not risk:
        return ["risk_state_required_for_funding_review"]

    blockers: list[str] = []
    if risk.get("review_only") is not True and risk.get("risk_review_only") is not True:
        blockers.append("risk_state_must_be_review_only")
    if risk.get("within_limits") is False:
        blockers.append("risk_within_limits_false")
    if risk.get("funding_review_within_limits") is False:
        blockers.append("funding_review_within_limits_false")
    for key in sorted(RISK_LIMIT_BOOLEAN_KEYS):
        if _truthy_unsafe(risk.get(key)):
            blockers.append(f"{key}_true")
    risk_status = _text(risk.get("risk_status") or risk.get("status"))
    if risk_status in RISK_BLOCKED_STATUSES:
        blockers.append(f"risk_status_{risk_status}")
    return _unique(blockers)


def _exposure_counts(
    account_separation: Mapping[str, Any],
    next_trade_eligibility: Mapping[str, Any],
) -> tuple[dict[str, int], list[str]]:
    counts: dict[str, int] = {
        "open_trade_count": 0,
        "open_position_count": 0,
        "pending_order_count": 0,
    }
    blockers: list[str] = []
    for source_name, source in (
        ("account_separation", account_separation),
        ("next_trade_eligibility", next_trade_eligibility),
    ):
        source_counts, source_blockers = _source_exposure_counts(source, source_name)
        for key, value in source_counts.items():
            counts[key] = max(counts[key], value)
        blockers.extend(source_blockers)
    return counts, blockers


def _source_exposure_counts(
    source: Mapping[str, Any],
    source_name: str,
) -> tuple[dict[str, int], list[str]]:
    counts: dict[str, int] = {}
    blockers: list[str] = []
    for output_key, count_keys, collection_keys in (
        (
            "open_trade_count",
            ("open_trade_count", "openTradeCount"),
            ("open_trades", "openTrades", "open_trade_evidence"),
        ),
        (
            "open_position_count",
            ("open_position_count", "openPositionCount"),
            ("open_positions", "openPositions", "open_position_evidence"),
        ),
        (
            "pending_order_count",
            ("pending_order_count", "pendingOrderCount"),
            ("pending_orders", "pendingOrders", "orders_pending"),
        ),
    ):
        value, blocker = _count_value(source, count_keys, collection_keys)
        counts[output_key] = value
        if blocker:
            blockers.append(f"{source_name}_{output_key}_{blocker}")
    return counts, blockers


def _count_value(
    source: Mapping[str, Any],
    count_keys: Sequence[str],
    collection_keys: Sequence[str],
) -> tuple[int, str | None]:
    for key in count_keys:
        if key in source:
            parsed = _count_or_none(source.get(key))
            if parsed is None:
                return 0, "must_be_non_negative_integer"
            return parsed, None
    for key in collection_keys:
        if key in source:
            collection = source.get(key)
            if isinstance(collection, Sequence) and not isinstance(
                collection,
                (str, bytes),
            ):
                return len(collection), None
            return 0, "collection_must_be_sequence"
    return 0, None


def _open_exposure_blockers(counts: Mapping[str, int]) -> list[str]:
    blockers: list[str] = []
    if counts.get("open_trade_count", 0) > 0:
        blockers.append("open_trade_count_must_be_zero")
    if counts.get("open_position_count", 0) > 0:
        blockers.append("open_position_count_must_be_zero")
    if counts.get("pending_order_count", 0) > 0:
        blockers.append("pending_order_count_must_be_zero")
    return blockers


def _funding_amount(intent: Mapping[str, Any]) -> Decimal | None:
    for key in (
        "proposed_amount",
        "amount",
        "funding_amount",
        "proposed_funding_amount",
    ):
        if key in intent:
            return _decimal_or_none(intent.get(key))
    return None


def _funding_currency(intent: Mapping[str, Any]) -> str:
    return _text(
        _first_present(
            intent,
            "proposed_currency",
            "currency",
            "funding_currency",
        )
    ).upper()


def _funding_mode(intent: Mapping[str, Any]) -> str:
    return _normalized_key(_first_present(intent, "funding_mode", "mode"))


def _status_text(payload: Mapping[str, Any]) -> str:
    for path in (
        ("gate_status",),
        ("status",),
        ("decision", "gate_status"),
        ("decision", "status"),
    ):
        value = _text(_nested_value(payload, path))
        if value:
            return value
    return ""


def _status_blocked(status: str) -> bool:
    if not status:
        return False
    return any(term in status for term in BLOCKED_STATUS_TERMS)


def _unsafe_input_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            for raw_key, value in node.items():
                key = _normalized_key(raw_key)
                if key in SAFE_TRUE_KEYS:
                    visit(value)
                    continue
                if key in UNSAFE_TRUE_FIELDS and _truthy_unsafe(value):
                    blockers.append(f"unsafe_{label}_{key}_true")
                if _action_flag_key(key) and _truthy_unsafe(value):
                    blockers.append(f"unsafe_{label}_{key}_true")
                if _sensitive_key(key) and _sensitive_value_present(value):
                    blockers.append(f"unsafe_{label}_{key}_present")
                if _endpoint_url_key(key) and _present(value):
                    blockers.append(f"unsafe_{label}_{key}_present")
                if _request_header_key(key) and _present(value):
                    blockers.append(f"unsafe_{label}_{key}_present")
                if _raw_payload_key(key) and _present(value):
                    blockers.append(f"unsafe_{label}_{key}_present")
                if _unsafe_string_value(value):
                    blockers.append(f"unsafe_{label}_{key}_secret_like_value")
                visit(value)
        elif isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
            for child in node:
                visit(child)

    visit(payload)
    return _unique(blockers)


def _action_flag_key(key: str) -> bool:
    if key in SAFE_TRUE_KEYS:
        return False
    if key.startswith("no_") or "_not_" in key or key.endswith("_not_supported"):
        return False
    return any(term in key for term in ACTION_KEY_TERMS) and any(
        term in key for term in ACTION_STATE_TERMS
    )


def _sensitive_key(key: str) -> bool:
    return any(term in key for term in SENSITIVE_KEY_TERMS)


def _endpoint_url_key(key: str) -> bool:
    return key in ENDPOINT_URL_KEY_TERMS or key.endswith("_url")


def _request_header_key(key: str) -> bool:
    return key in REQUEST_HEADER_KEY_TERMS


def _raw_payload_key(key: str) -> bool:
    return any(term in key for term in RAW_PAYLOAD_KEY_TERMS)


def _unsafe_string_value(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    lowered = text.lower()
    if not text:
        return False
    if "bearer " in lowered:
        return True
    if ".env" in lowered:
        return True
    if "begin private key" in lowered or "begin rsa private key" in lowered:
        return True
    if lowered.startswith("sk-"):
        return True
    if "windows vault" in lowered or "bitwarden" in lowered or "yubikey" in lowered:
        return True
    if "credential" in lowered or "credentials" in lowered:
        return True
    if "api-fxtrade" in lowered or "api-fxpractice" in lowered:
        return True
    if ("http://" in lowered or "https://" in lowered) and (
        "broker" in lowered
        or "oanda" in lowered
        or "orders" in lowered
        or "accounts" in lowered
    ):
        return True
    return False


def _truthy_unsafe(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {
            "true",
            "yes",
            "1",
            "allowed",
            "performed",
            "enabled",
            "started",
            "called",
            "authorized",
            "used",
            "read",
            "mutated",
            "placed",
            "closed",
            "executed",
            "applied",
        }
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value == 1
    return False


def _sensitive_value_present(value: Any) -> bool:
    if value in (None, False):
        return False
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return False
        upper = text.upper()
        return "REDACTED" not in upper and "SANITIZED" not in upper
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return bool(value)
    if isinstance(value, Mapping):
        return bool(value)
    return True


def _present(value: Any) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return bool(value)
    if isinstance(value, Mapping):
        return bool(value)
    return True


def _readiness_checks(
    *,
    gate_status: str,
    amount: Decimal | None,
    currency: str,
    funding_mode: str,
    account_status: str,
    bucket_status: str,
    next_trade_status: str,
    exposure_counts: Mapping[str, int],
) -> dict[str, bool]:
    return {
        "explicit_funding_intent_present": gate_status
        != FUNDING_REVIEW_BLOCKED_NO_OWNER_INTENT,
        "owner_approved_funding_review": gate_status
        not in {
            FUNDING_REVIEW_BLOCKED_NO_OWNER_INTENT,
            FUNDING_REVIEW_BLOCKED_OWNER_APPROVAL_MISSING,
        },
        "proposed_amount_positive": amount is not None and amount > 0,
        "proposed_currency_present": bool(currency),
        "funding_mode_review_only": funding_mode == "review_only",
        "account_separation_state_available": bool(account_status),
        "aios_bucket_or_bucket_gate_state_available": bool(bucket_status),
        "next_trade_eligibility_available": bool(next_trade_status),
        "open_trade_count_zero": exposure_counts.get("open_trade_count", 0) == 0,
        "open_position_count_zero": exposure_counts.get("open_position_count", 0)
        == 0,
        "pending_order_count_zero": exposure_counts.get("pending_order_count", 0)
        == 0,
        "risk_state_review_only_and_within_limits": gate_status
        not in {FUNDING_REVIEW_BLOCKED_RISK_LIMIT},
        "unsafe_input_clear": gate_status
        != FUNDING_REVIEW_BLOCKED_UNSAFE_INPUT,
    }


def _warnings(gate_status: str) -> list[str]:
    warnings = [
        "owner_review_only_not_money_movement",
        "funding_transfer_authorized_false",
        "deposit_authorized_false",
        "withdrawal_authorized_false",
        "broker_call_authorized_false",
        "oanda_call_authorized_false",
        "order_placement_authorized_false",
        "live_trading_authorized_false",
        "runtime_mutation_authorized_false",
        "no_credentials_or_account_ids_read",
        "no_network_or_broker_call_performed",
    ]
    if gate_status == FUNDING_REVIEW_READY:
        warnings.append("ready_for_owner_funding_review_only")
    return warnings


def _next_safe_action(gate_status: str) -> str:
    return {
        FUNDING_REVIEW_READY: "owner_review_funding_decision_only_no_transfer",
        FUNDING_REVIEW_BLOCKED_NO_OWNER_INTENT: "provide_explicit_review_only_funding_intent",
        FUNDING_REVIEW_BLOCKED_OWNER_APPROVAL_MISSING: "obtain_owner_approved_funding_review_true_before_review",
        FUNDING_REVIEW_BLOCKED_OPEN_EXPOSURE: "close_or_clear_open_trades_positions_and_pending_orders_before_review",
        FUNDING_REVIEW_BLOCKED_BUCKET_NOT_READY: "repair_account_separation_or_bucket_gate_before_funding_review",
        FUNDING_REVIEW_BLOCKED_NEXT_TRADE_NOT_READY: "repair_next_trade_eligibility_before_funding_review",
        FUNDING_REVIEW_BLOCKED_RISK_LIMIT: "repair_or_wait_for_risk_state_before_funding_review",
        FUNDING_REVIEW_BLOCKED_INVALID_AMOUNT: "provide_positive_amount_and_currency_before_funding_review",
        FUNDING_REVIEW_BLOCKED_UNSAFE_INPUT: "remove_secret_like_or_execution_fields_before_retry",
    }.get(gate_status, "stop_and_review_funding_gate_inputs")


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _safety_proof() -> dict[str, bool]:
    return {field: False for field in SAFETY_PROOF_FIELDS}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _nested_value(mapping: Mapping[str, Any], path: Sequence[str]) -> Any:
    node: Any = mapping
    for key in path:
        if not isinstance(node, Mapping) or key not in node:
            return None
        node = node[key]
    return node


def _first_present(mapping: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in mapping:
            return mapping.get(key)
    return None


def _decimal_or_none(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None
    if not parsed.is_finite():
        return None
    return parsed


def _count_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    parsed = _decimal_or_none(value)
    if parsed is None or parsed < 0 or parsed != parsed.to_integral_value():
        return None
    return int(parsed)


def _decimal_text_or_none(value: Decimal | None) -> str | None:
    return format(value, "f") if value is not None else None


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return value.strip() if isinstance(value, str) else str(value).strip()


def _normalized_key(value: Any) -> str:
    return str(value).strip().replace("-", "_").replace(" ", "_").lower()


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = _text(value)
        if text and text not in seen:
            seen.add(text)
            output.append(text)
    return output
