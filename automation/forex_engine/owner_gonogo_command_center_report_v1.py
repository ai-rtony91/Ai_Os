from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation
from typing import Any


PACKET_ID = "AIOS-FOREX-OWNER-GONOGO-COMMAND-CENTER-REPORT-V1"
COMMAND_VERSION = "v1"

OWNER_GONOGO_READY_FOR_REVIEW = "OWNER_GONOGO_READY_FOR_REVIEW"
OWNER_GONOGO_BLOCKED_TRADE_STILL_OPEN = (
    "OWNER_GONOGO_BLOCKED_TRADE_STILL_OPEN"
)
OWNER_GONOGO_BLOCKED_NO_CLOSED_RESULT = (
    "OWNER_GONOGO_BLOCKED_NO_CLOSED_RESULT"
)
OWNER_GONOGO_BLOCKED_BUCKET_GATE = "OWNER_GONOGO_BLOCKED_BUCKET_GATE"
OWNER_GONOGO_BLOCKED_NEXT_TRADE = "OWNER_GONOGO_BLOCKED_NEXT_TRADE"
OWNER_GONOGO_BLOCKED_FUNDING = "OWNER_GONOGO_BLOCKED_FUNDING"
OWNER_GONOGO_BLOCKED_RISK = "OWNER_GONOGO_BLOCKED_RISK"
OWNER_GONOGO_BLOCKED_UNSAFE_INPUT = "OWNER_GONOGO_BLOCKED_UNSAFE_INPUT"

CLOSED_RESULT_STATUSES = {
    "OWNER_RUN_CLOSED_BY_TAKE_PROFIT",
    "OWNER_RUN_CLOSED_BY_STOP_LOSS",
    "OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER",
    "OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER",
    "OWNER_RUN_CLOSED_BREAKEVEN_OTHER",
    "ADAPTED_CLOSED_BY_TAKE_PROFIT",
    "ADAPTED_CLOSED_BY_STOP_LOSS",
    "ADAPTED_CLOSED_REALIZED_PROFIT_OTHER",
    "ADAPTED_CLOSED_REALIZED_LOSS_OTHER",
    "ADAPTED_CLOSED_BREAKEVEN_OTHER",
    "CLOSED_BY_TAKE_PROFIT",
    "CLOSED_BY_STOP_LOSS",
    "CLOSED_REALIZED_PROFIT_OTHER",
    "CLOSED_REALIZED_LOSS_OTHER",
    "CLOSED_BREAKEVEN_OTHER",
}
STILL_OPEN_STATUSES = {
    "OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT",
    "ADAPTED_STILL_OPEN_NO_REALIZED_RESULT",
    "STILL_OPEN_NO_REALIZED_RESULT",
    "TRADE_STILL_OPEN",
    "OPEN_UNREALIZED_PL_RESULT",
}

BUCKET_READY_STATUSES = {
    "BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT",
    "BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS",
    "BUCKET_UPDATE_ELIGIBLE_BREAKEVEN",
    "BUCKET_GATE_ELIGIBLE_REALIZED_PROFIT",
    "BUCKET_GATE_ELIGIBLE_REALIZED_LOSS",
    "BUCKET_GATE_ELIGIBLE_BREAKEVEN",
    "RESULT_BUCKET_READY",
    "AIOS_BUCKET_READY",
}
BUCKET_ALREADY_APPLIED_STATUSES = {
    "BUCKET_UPDATE_BLOCKED_ALREADY_APPLIED",
    "BUCKET_GATE_ALREADY_APPLIED",
    "RESULT_BUCKET_ALREADY_APPLIED",
}
NEXT_TRADE_READY_STATUSES = {
    "NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW",
    "NEXT_TRADE_REVIEW_READY",
    "NEXT_TRADE_READY_FOR_OWNER_REVIEW",
}
FUNDING_READY_STATUSES = {
    "FUNDING_REVIEW_READY",
    "FUNDING_READY_FOR_OWNER_REVIEW",
    "FUNDING_REVIEW_ELIGIBLE_FOR_OWNER_REVIEW",
}

BLOCKED_STATUS_TERMS = ("BLOCKED", "REJECTED", "UNSAFE", "INVALID")
RISK_BLOCKED_STATUS_TERMS = (
    "BLOCKED",
    "REJECTED",
    "UNSAFE",
    "INVALID",
    "OVER_LIMIT",
    "LIMIT_EXCEEDED",
)

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
    "over_limit",
}

SAFETY_AUTHORITY_FIELDS = (
    "trade_execution_authorized",
    "order_placement_authorized",
    "broker_call_authorized",
    "oanda_call_authorized",
    "funding_transfer_authorized",
    "deposit_authorized",
    "withdrawal_authorized",
    "bucket_mutation_authorized",
    "live_trading_authorized",
    "runtime_mutation_authorized",
    "scheduler_authorized",
    "daemon_authorized",
    "webhook_authorized",
)

EXECUTION_AUTHORITY_FIELDS = SAFETY_AUTHORITY_FIELDS + (
    "execution_allowed",
    "trade_execution_allowed",
    "order_execution_authorized",
    "order_execution_allowed",
    "network_allowed",
    "network_call_allowed",
    "network_call_authorized",
    "broker_call_allowed",
    "broker_network_call_allowed",
    "broker_api_call_allowed",
    "oanda_call_allowed",
    "oanda_api_call_allowed",
    "broker_write_allowed",
    "credential_access_allowed",
    "credential_read_allowed",
    "account_id_read_allowed",
    "vault_read_allowed",
    "windows_vault_read_allowed",
    "dotenv_read_allowed",
    "env_read_allowed",
    "order_close_allowed",
    "order_mutation_allowed",
    "trade_mutation_allowed",
    "position_mutation_allowed",
    "live_endpoint_allowed",
    "live_order_allowed",
    "raw_broker_payload_persistence_allowed",
    "file_persistence_allowed",
    "write_allowed",
    "bucket_update_allowed",
    "bucket_mutation_allowed",
    "result_bucket_update_allowed",
    "result_bucket_mutation_allowed",
    "next_order_authorized",
    "next_trade_authorized",
    "next_trade_execution_allowed",
    "next_allocation_authorized",
    "live_funding_authorized",
    "live_funding_allowed",
    "funding_transfer_allowed",
    "money_transfer_authorized",
    "money_transfer_allowed",
    "deposit_allowed",
    "withdrawal_allowed",
    "bank_call_authorized",
    "bank_call_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
)

SAFETY_PROOF_FIELDS = (
    "network_call_performed",
    "broker_network_call_performed",
    "broker_api_call_performed",
    "broker_call_performed",
    "oanda_call_performed",
    "oanda_api_call_performed",
    "broker_write_performed",
    "credential_read_performed",
    "account_id_read_performed",
    "vault_read_performed",
    "windows_vault_read_performed",
    "dotenv_read",
    "env_read",
    "order_placement_performed",
    "order_execution_performed",
    "order_close_performed",
    "order_mutation_performed",
    "trade_execution_performed",
    "trade_mutation_performed",
    "position_mutation_performed",
    "orders_endpoint_called",
    "live_endpoint_used",
    "raw_broker_payload_persisted",
    "file_persistence_performed",
    "write_performed",
    "bucket_update_performed",
    "bucket_mutation_performed",
    "result_bucket_update_performed",
    "result_bucket_mutation_performed",
    "next_trade_executed",
    "funding_transfer_performed",
    "money_transfer_performed",
    "deposit_performed",
    "withdrawal_performed",
    "bank_call_performed",
    "live_trading_performed",
    "runtime_mutation_performed",
    "scheduler_started",
    "daemon_started",
    "webhook_called",
    "live_funding_performed",
)

UNSAFE_TRUE_FIELDS = EXECUTION_AUTHORITY_FIELDS + SAFETY_PROOF_FIELDS
SAFE_TRUE_KEYS = {
    "aios_bucket_ready",
    "already_applied_safe_idempotent",
    "bucket_gate_ready",
    "bucket_update_authorized",
    "closed_result_available",
    "funding_review_authorized",
    "funding_review_ready",
    "funding_review_within_limits",
    "idempotent_safe",
    "is_closed",
    "next_trade_eligible_for_owner_review",
    "next_trade_review_authorized",
    "next_trade_review_ready",
    "owner_approved_funding_review",
    "owner_approved_next_trade_review",
    "owner_review_only",
    "ready_for_owner_review",
    "review_only",
    "risk_review_only",
    "safe_idempotent_state",
    "sanitized_only",
    "template_only",
    "within_limits",
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
ENDPOINT_URL_KEY_TERMS = (
    "url",
    "endpoint",
    "endpoint_url",
    "endpointurl",
    "broker_endpoint",
    "oanda_endpoint",
)
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
    "bucket",
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


def build_owner_gonogo_command_center_report_v1(
    closed_result: dict[str, Any] | Mapping[str, Any] | None = None,
    bucket_gate_decision: dict[str, Any] | Mapping[str, Any] | None = None,
    next_trade_eligibility: dict[str, Any] | Mapping[str, Any] | None = None,
    funding_readiness: dict[str, Any] | Mapping[str, Any] | None = None,
    account_separation: dict[str, Any] | Mapping[str, Any] | None = None,
    risk_state: dict[str, Any] | Mapping[str, Any] | None = None,
    owner_context: dict[str, Any] | Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    closed = _mapping(closed_result)
    bucket = _mapping(bucket_gate_decision)
    next_trade = _mapping(next_trade_eligibility)
    funding = _mapping(funding_readiness)
    separation = _mapping(account_separation)
    risk = _mapping(risk_state)
    owner = _mapping(owner_context)

    unsafe_blockers: list[str] = []
    type_blockers: list[str] = []
    for label, original, payload in (
        ("closed_result", closed_result, closed),
        ("bucket_gate_decision", bucket_gate_decision, bucket),
        ("next_trade_eligibility", next_trade_eligibility, next_trade),
        ("funding_readiness", funding_readiness, funding),
        ("account_separation", account_separation, separation),
        ("risk_state", risk_state, risk),
        ("owner_context", owner_context, owner),
    ):
        if original is not None and not isinstance(original, Mapping):
            type_blockers.append(f"{label}_must_be_mapping_when_provided")
        if payload:
            unsafe_blockers.extend(_unsafe_input_blockers(payload, label))

    closed_status = _status_text(closed)
    trade_id = _trade_id(closed, bucket, next_trade)
    realized_pl = _text_or_none(_first_path(closed, _REALIZED_PL_PATHS))
    unrealized_pl = _text_or_none(_first_path(closed, _UNREALIZED_PL_PATHS))
    trade_still_open = _trade_still_open(closed, closed_status)
    trade_closed = _trade_closed(closed, closed_status)
    exposure_counts, exposure_blockers = _combined_exposure_counts(
        account_separation=separation,
        next_trade_eligibility=next_trade,
        funding_readiness=funding,
    )

    bucket_ready, bucket_already_applied, bucket_blockers = _bucket_readiness(bucket)
    next_ready, next_not_requested, next_blockers = _next_trade_readiness(next_trade)
    funding_ready, funding_not_requested, funding_blockers = _funding_readiness(
        funding
    )
    risk_ready, risk_blockers = _risk_readiness(risk)
    open_exposure_blockers = _open_exposure_blockers(exposure_counts)

    command_status = OWNER_GONOGO_READY_FOR_REVIEW
    blockers: list[str] = []
    warnings: list[str] = []

    if type_blockers or unsafe_blockers:
        command_status = OWNER_GONOGO_BLOCKED_UNSAFE_INPUT
        blockers.extend(type_blockers + unsafe_blockers)
    elif not closed:
        command_status = OWNER_GONOGO_BLOCKED_NO_CLOSED_RESULT
        blockers.append("closed_result_required")
    elif trade_still_open:
        command_status = OWNER_GONOGO_BLOCKED_TRADE_STILL_OPEN
        blockers.append("closed_result_reports_trade_still_open")
    elif bucket_blockers:
        command_status = OWNER_GONOGO_BLOCKED_BUCKET_GATE
        blockers.extend(bucket_blockers)
    elif next_blockers:
        command_status = OWNER_GONOGO_BLOCKED_NEXT_TRADE
        blockers.extend(next_blockers)
    elif funding_blockers:
        command_status = OWNER_GONOGO_BLOCKED_FUNDING
        blockers.extend(funding_blockers)
    elif risk_blockers:
        command_status = OWNER_GONOGO_BLOCKED_RISK
        blockers.extend(risk_blockers)
    elif exposure_blockers or open_exposure_blockers:
        command_status = OWNER_GONOGO_BLOCKED_NEXT_TRADE
        blockers.extend(exposure_blockers or open_exposure_blockers)
    elif not trade_closed:
        command_status = OWNER_GONOGO_BLOCKED_NO_CLOSED_RESULT
        blockers.append("closed_result_does_not_prove_trade_closed")
    elif not risk_ready:
        command_status = OWNER_GONOGO_BLOCKED_RISK
        blockers.append("risk_state_not_ready")

    if bucket_already_applied:
        warnings.append("bucket_gate_already_applied_accepted_as_safe_idempotent")
    if next_not_requested:
        warnings.append("next_trade_eligibility_deliberately_not_requested")
    if funding_not_requested:
        warnings.append("funding_readiness_deliberately_not_requested")
    warnings.extend(_base_warnings(command_status))

    readiness_matrix = {
        "closed_result_exists": bool(closed),
        "trade_not_still_open": bool(closed and not trade_still_open),
        "trade_closed": trade_closed,
        "unsafe_input_clear": not bool(type_blockers or unsafe_blockers),
        "bucket_gate_ready_or_safe_already_applied": bucket_ready,
        "next_trade_ready_or_not_requested": next_ready or next_not_requested,
        "funding_ready_or_not_requested": funding_ready or funding_not_requested,
        "risk_review_only_within_limits": risk_ready,
        "open_trade_count_zero": exposure_counts["open_trade_count"] == 0,
        "open_position_count_zero": exposure_counts["open_position_count"] == 0,
        "pending_order_count_zero": exposure_counts["pending_order_count"] == 0,
        "safety_authority_false": True,
        "owner_review_only": True,
    }

    result: dict[str, Any] = {
        "packet_id": PACKET_ID,
        "command_version": COMMAND_VERSION,
        "command_status": command_status,
        "owner_summary": _owner_summary(owner),
        "trade_result_summary": {
            "closed_result_present": bool(closed),
            "status": closed_status or "MISSING",
            "trade_id": trade_id,
            "realized_pl": realized_pl,
            "unrealized_pl": unrealized_pl,
            "is_closed": trade_closed,
            "is_still_open": trade_still_open,
            "open_trade_count": exposure_counts["open_trade_count"],
            "open_position_count": exposure_counts["open_position_count"],
            "pending_order_count": exposure_counts["pending_order_count"],
        },
        "bucket_summary": {
            "requested": bool(bucket),
            "status": _status_text(bucket) or "MISSING",
            "ready_for_owner_review": bucket_ready,
            "safely_already_applied": bucket_already_applied,
            "blockers": list(bucket_blockers),
        },
        "next_trade_summary": {
            "requested": bool(next_trade),
            "deliberately_not_requested": next_not_requested,
            "status": _status_text(next_trade) or "NOT_REQUESTED",
            "ready_for_owner_review": next_ready,
            "blockers": list(next_blockers),
            "open_trade_count": _source_exposure_counts(
                next_trade,
                "next_trade_eligibility",
            )[0]["open_trade_count"],
            "open_position_count": _source_exposure_counts(
                next_trade,
                "next_trade_eligibility",
            )[0]["open_position_count"],
            "pending_order_count": _source_exposure_counts(
                next_trade,
                "next_trade_eligibility",
            )[0]["pending_order_count"],
        },
        "funding_summary": {
            "requested": bool(funding),
            "deliberately_not_requested": funding_not_requested,
            "status": _status_text(funding) or "NOT_REQUESTED",
            "ready_for_owner_review": funding_ready,
            "blockers": list(funding_blockers),
            "funding_review_authorized": funding.get("funding_review_authorized")
            is True,
            "funding_transfer_authorized": False,
        },
        "risk_summary": {
            "risk_state_present": bool(risk),
            "status": _status_text(risk) or "MISSING",
            "review_only": risk.get("review_only") is True
            or risk.get("risk_review_only") is True,
            "within_limits": _risk_within_limits(risk),
            "ready_for_owner_review": risk_ready,
            "blockers": list(risk_blockers),
        },
        "blockers": _unique(blockers),
        "warnings": _unique(warnings),
        "readiness_matrix": readiness_matrix,
        "safety_authority": _safety_authority(),
        "next_safe_action": _next_safe_action(command_status),
    }
    result.update(_safety_authority())
    return result


def owner_gonogo_command_center_report_template_v1() -> dict[str, Any]:
    return {
        "closed_result": {
            "exercise_status": "OWNER_RUN_CLOSED_BY_TAKE_PROFIT",
            "trade_anchor": {"trade_id": "328"},
            "realized_pl": "0.0012",
            "unrealized_pl": "0",
            "is_closed": True,
            "is_open": False,
            "execution_authority": _nested_false_authority(),
            "safety_proof": _nested_false_safety(),
        },
        "bucket_gate_decision": {
            "gate_status": "BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT",
            "trade_id": "328",
            "bucket_update_authorized": True,
            "bucket_update_performed": False,
            "bucket_mutation_performed": False,
            "next_trade_authorized": False,
            "live_funding_authorized": False,
        },
        "next_trade_eligibility": {
            "gate_status": "NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW",
            "next_trade_review_authorized": True,
            "next_trade_authorized": False,
            "order_placement_authorized": False,
            "broker_call_authorized": False,
            "open_trade_count": 0,
            "open_position_count": 0,
            "pending_order_count": 0,
        },
        "funding_readiness": {
            "gate_status": "FUNDING_REVIEW_READY",
            "funding_review_authorized": True,
            "funding_transfer_authorized": False,
            "deposit_authorized": False,
            "withdrawal_authorized": False,
            "open_trade_count": 0,
            "open_position_count": 0,
            "pending_order_count": 0,
        },
        "account_separation": {
            "status": "BROKER_BALANCE_BUCKET_EQUITY_SEPARATION_READY",
            "open_trade_count": 0,
            "open_position_count": 0,
            "pending_order_count": 0,
            "withdraw_allowed": False,
            "compound_allowed": False,
            "live_allocation_allowed": False,
        },
        "risk_state": {
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
        },
        "owner_context": {
            "owner_review_only": True,
            "owner_requested_next_trade_review": True,
            "owner_requested_funding_review": True,
        },
        "runtime_input_rule": {
            "sanitized_decisions_only": True,
            "report_only": True,
            "broker_or_oanda_call_supported": False,
            "order_placement_supported": False,
            "funding_transfer_supported": False,
            "bucket_mutation_supported": False,
            "runtime_mutation_supported": False,
            "scheduler_supported": False,
            "daemon_supported": False,
            "webhook_supported": False,
        },
    }


def owner_gonogo_command_center_report_samples_v1() -> dict[str, dict[str, Any]]:
    ready = owner_gonogo_command_center_report_template_v1()
    return {
        "ready": ready,
        "trade-open": {
            **ready,
            "closed_result": {
                **ready["closed_result"],
                "exercise_status": "OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT",
                "realized_pl": None,
                "unrealized_pl": "0.0008",
                "is_closed": False,
                "is_open": True,
            },
        },
        "no-closed-result": {
            **ready,
            "closed_result": None,
        },
        "bucket-blocked": {
            **ready,
            "bucket_gate_decision": {
                "gate_status": "BUCKET_UPDATE_BLOCKED_STILL_OPEN",
                "bucket_update_authorized": False,
                "blockers": ["owner_run_trade_still_open_no_realized_result"],
            },
        },
        "next-trade-blocked": {
            **ready,
            "next_trade_eligibility": {
                **ready["next_trade_eligibility"],
                "gate_status": "NEXT_TRADE_BLOCKED_OPEN_EXPOSURE",
                "next_trade_review_authorized": False,
                "open_trade_count": 1,
            },
        },
        "funding-blocked": {
            **ready,
            "funding_readiness": {
                **ready["funding_readiness"],
                "gate_status": "FUNDING_REVIEW_BLOCKED_OPEN_EXPOSURE",
                "funding_review_authorized": False,
                "open_position_count": 1,
            },
        },
        "risk-blocked": {
            **ready,
            "risk_state": {
                **ready["risk_state"],
                "within_limits": False,
                "max_loss_limit_breached": True,
            },
        },
        "unsafe": {
            **ready,
            "owner_context": {
                "owner_review_only": True,
                "api_key": "sk-sample-unsafe-not-a-real-key",
            },
        },
    }


def _bucket_readiness(bucket: Mapping[str, Any]) -> tuple[bool, bool, list[str]]:
    if not bucket:
        return False, False, ["bucket_gate_decision_required"]
    status = _status_text(bucket)
    blockers = _string_items(bucket.get("blockers"))
    safely_already_applied = _safe_already_applied(bucket, status)
    if safely_already_applied:
        return True, True, []
    if status in BUCKET_READY_STATUSES:
        return True, False, []
    if bucket.get("bucket_gate_ready") is True or bucket.get("aios_bucket_ready") is True:
        return True, False, []
    if bucket.get("bucket_update_authorized") is True and not _status_blocked(status):
        return True, False, []
    if blockers:
        return False, False, blockers
    return False, False, [f"bucket_gate_status_not_ready_{status or 'UNKNOWN'}"]


def _safe_already_applied(bucket: Mapping[str, Any], status: str) -> bool:
    if status not in BUCKET_ALREADY_APPLIED_STATUSES:
        return False
    if (
        bucket.get("safe_idempotent_state") is True
        or bucket.get("already_applied_safe_idempotent") is True
        or bucket.get("idempotent_safe") is True
    ):
        return True
    messages = _string_items(bucket.get("warnings")) + _string_items(
        bucket.get("blockers")
    )
    normalized = {_normalized_key(message) for message in messages}
    return (
        "idempotency_guard_blocked_reapply" in normalized
        or any(message.endswith("_bucket_update_already_applied") for message in normalized)
    )


def _next_trade_readiness(
    next_trade: Mapping[str, Any],
) -> tuple[bool, bool, list[str]]:
    if not next_trade:
        return False, True, []
    status = _status_text(next_trade)
    counts, count_blockers = _source_exposure_counts(
        next_trade,
        "next_trade_eligibility",
    )
    if count_blockers:
        return False, False, count_blockers
    open_blockers = _open_exposure_blockers(counts)
    if open_blockers:
        return False, False, open_blockers
    blockers = _string_items(next_trade.get("blockers"))
    if blockers:
        return False, False, blockers
    if status in NEXT_TRADE_READY_STATUSES:
        return True, False, []
    if (
        next_trade.get("next_trade_review_authorized") is True
        or next_trade.get("next_trade_review_ready") is True
        or next_trade.get("next_trade_eligible_for_owner_review") is True
    ):
        return True, False, []
    return False, False, [f"next_trade_status_not_ready_{status or 'UNKNOWN'}"]


def _funding_readiness(funding: Mapping[str, Any]) -> tuple[bool, bool, list[str]]:
    if not funding:
        return False, True, []
    status = _status_text(funding)
    counts, count_blockers = _source_exposure_counts(
        funding,
        "funding_readiness",
    )
    if count_blockers:
        return False, False, count_blockers
    open_blockers = _open_exposure_blockers(counts)
    if open_blockers:
        return False, False, open_blockers
    blockers = _string_items(funding.get("blockers"))
    if blockers:
        return False, False, blockers
    if status in FUNDING_READY_STATUSES:
        return True, False, []
    if (
        funding.get("funding_review_authorized") is True
        or funding.get("funding_review_ready") is True
    ):
        return True, False, []
    return False, False, [f"funding_status_not_ready_{status or 'UNKNOWN'}"]


def _risk_readiness(risk: Mapping[str, Any]) -> tuple[bool, list[str]]:
    if not risk:
        return False, ["risk_state_required_for_owner_gonogo_review"]
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
    status = _status_text(risk)
    if _risk_status_blocked(status):
        blockers.append(f"risk_status_{status}")
    return not blockers, _unique(blockers)


def _combined_exposure_counts(
    *,
    account_separation: Mapping[str, Any],
    next_trade_eligibility: Mapping[str, Any],
    funding_readiness: Mapping[str, Any],
) -> tuple[dict[str, int], list[str]]:
    counts = {
        "open_trade_count": 0,
        "open_position_count": 0,
        "pending_order_count": 0,
    }
    blockers: list[str] = []
    for label, source in (
        ("account_separation", account_separation),
        ("next_trade_eligibility", next_trade_eligibility),
        ("funding_readiness", funding_readiness),
    ):
        source_counts, source_blockers = _source_exposure_counts(source, label)
        for key, value in source_counts.items():
            counts[key] = max(counts[key], value)
        blockers.extend(source_blockers)
    return counts, blockers


def _source_exposure_counts(
    source: Mapping[str, Any],
    source_name: str,
) -> tuple[dict[str, int], list[str]]:
    counts = {
        "open_trade_count": 0,
        "open_position_count": 0,
        "pending_order_count": 0,
    }
    blockers: list[str] = []
    for output_key, count_keys, collection_keys, present_key in (
        (
            "open_trade_count",
            ("open_trade_count", "openTradeCount"),
            ("open_trades", "openTrades", "open_trade_evidence"),
            "open_exposure_present",
        ),
        (
            "open_position_count",
            ("open_position_count", "openPositionCount"),
            ("open_positions", "openPositions", "open_position_evidence"),
            "open_exposure_present",
        ),
        (
            "pending_order_count",
            ("pending_order_count", "pendingOrderCount"),
            ("pending_orders", "pendingOrders", "orders_pending"),
            "pending_order_present",
        ),
    ):
        value, blocker = _count_value(source, count_keys, collection_keys)
        counts[output_key] = value
        if blocker:
            blockers.append(f"{source_name}_{output_key}_{blocker}")
        if source.get(present_key) is True and counts[output_key] == 0:
            counts[output_key] = 1
    return counts, blockers


def _count_value(
    source: Mapping[str, Any],
    count_keys: Sequence[str],
    collection_keys: Sequence[str],
) -> tuple[int, str | None]:
    if not source:
        return 0, None
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


def _owner_summary(owner_context: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "owner_context_present": bool(owner_context),
        "owner_review_only": True,
        "report_only": True,
        "owner_requested_next_trade_review": owner_context.get(
            "owner_requested_next_trade_review"
        )
        is True,
        "owner_requested_funding_review": owner_context.get(
            "owner_requested_funding_review"
        )
        is True,
        "human_owner_approval_still_required_for_protected_actions": True,
    }


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


def _base_warnings(command_status: str) -> list[str]:
    warnings = [
        "command_center_report_only",
        "no_broker_or_oanda_call_performed",
        "no_order_placement_authorized",
        "no_trade_execution_authorized",
        "no_funding_transfer_authorized",
        "no_deposit_or_withdrawal_authorized",
        "no_bucket_mutation_authorized",
        "no_runtime_mutation_scheduler_daemon_or_webhook_authorized",
        "owner_run_evidence_must_remain_current",
    ]
    if command_status == OWNER_GONOGO_READY_FOR_REVIEW:
        warnings.append("ready_for_owner_review_only_not_execution")
    return warnings


def _next_safe_action(command_status: str) -> str:
    return {
        OWNER_GONOGO_READY_FOR_REVIEW: "owner_review_command_center_report_no_trade_no_transfer",
        OWNER_GONOGO_BLOCKED_TRADE_STILL_OPEN: "continue_read_only_monitoring_until_closed_result_is_current",
        OWNER_GONOGO_BLOCKED_NO_CLOSED_RESULT: "provide_current_sanitized_closed_result_before_owner_gonogo",
        OWNER_GONOGO_BLOCKED_BUCKET_GATE: "repair_or_confirm_bucket_gate_before_owner_gonogo",
        OWNER_GONOGO_BLOCKED_NEXT_TRADE: "repair_next_trade_eligibility_or_open_exposure_before_owner_gonogo",
        OWNER_GONOGO_BLOCKED_FUNDING: "repair_funding_readiness_before_owner_gonogo",
        OWNER_GONOGO_BLOCKED_RISK: "repair_or_wait_for_risk_state_before_owner_gonogo",
        OWNER_GONOGO_BLOCKED_UNSAFE_INPUT: "remove_secret_like_or_execution_authority_fields_before_retry",
    }.get(command_status, "stop_and_review_owner_gonogo_inputs")


def _trade_still_open(closed: Mapping[str, Any], status: str) -> bool:
    if not closed:
        return False
    if status in STILL_OPEN_STATUSES or "STILL_OPEN" in status:
        return True
    if _bool_path(closed, ("is_open",)) is True:
        return True
    if _bool_path(closed, ("classifier_decision", "is_open")) is True:
        return True
    if _bool_path(closed, ("adapter_decision", "classifier_decision", "is_open")) is True:
        return True
    if _bool_path(closed, ("is_closed",)) is False:
        return True
    if _bool_path(closed, ("classifier_decision", "is_closed")) is False:
        return True
    if _collection_present(
        _first_path(
            closed,
            (
                ("pl_evidence", "open_trade_evidence"),
                ("decision", "pl_evidence", "open_trade_evidence"),
            ),
        )
    ):
        return True
    return False


def _trade_closed(closed: Mapping[str, Any], status: str) -> bool:
    if not closed or _trade_still_open(closed, status):
        return False
    if status in CLOSED_RESULT_STATUSES or "CLOSED" in status:
        return True
    if _bool_path(closed, ("is_closed",)) is True:
        return True
    if _bool_path(closed, ("classifier_decision", "is_closed")) is True:
        return True
    if _bool_path(closed, ("adapter_decision", "classifier_decision", "is_closed")) is True:
        return True
    return False


def _risk_within_limits(risk: Mapping[str, Any]) -> bool:
    if not risk:
        return False
    return not _risk_readiness(risk)[1]


def _status_text(payload: Mapping[str, Any]) -> str:
    for path in (
        ("command_status",),
        ("gate_status",),
        ("status",),
        ("exercise_status",),
        ("adapter_status",),
        ("classifier_status",),
        ("risk_status",),
        ("decision", "gate_status"),
        ("decision", "status"),
        ("decision", "exercise_status"),
    ):
        value = _text(_nested_value(payload, path))
        if value:
            return value
    return ""


_REALIZED_PL_PATHS = (
    ("realized_pl",),
    ("realizedPL",),
    ("classifier_decision", "realized_pl"),
    ("classifier_decision", "realizedPL"),
    ("adapter_decision", "realized_pl"),
    ("adapter_decision", "classifier_decision", "realized_pl"),
    ("adapter_decision", "classifier_decision", "realizedPL"),
)
_UNREALIZED_PL_PATHS = (
    ("unrealized_pl",),
    ("unrealizedPL",),
    ("classifier_decision", "unrealized_pl"),
    ("classifier_decision", "unrealizedPL"),
    ("adapter_decision", "unrealized_pl"),
    ("adapter_decision", "classifier_decision", "unrealized_pl"),
    ("adapter_decision", "classifier_decision", "unrealizedPL"),
)
_TRADE_ID_PATHS = (
    ("trade_id",),
    ("tradeID",),
    ("trade_anchor", "trade_id"),
    ("classifier_decision", "trade_id"),
    ("adapter_decision", "trade_id"),
    ("adapter_decision", "classifier_decision", "trade_id"),
    ("proposed_bucket_delta", "trade_id"),
)


def _trade_id(*sources: Mapping[str, Any]) -> str:
    for source in sources:
        value = _first_path(source, _TRADE_ID_PATHS)
        text = _text(value)
        if text:
            return text
    return "UNKNOWN"


def _nested_value(mapping: Mapping[str, Any], path: Sequence[str]) -> Any:
    node: Any = mapping
    for key in path:
        if not isinstance(node, Mapping) or key not in node:
            return None
        node = node[key]
    return node


def _first_path(mapping: Mapping[str, Any], paths: Sequence[Sequence[str]]) -> Any:
    for path in paths:
        value = _nested_value(mapping, path)
        if value is not None:
            return value
    return None


def _bool_path(mapping: Mapping[str, Any], path: Sequence[str]) -> bool | None:
    value = _nested_value(mapping, path)
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    return None


def _count_or_none(value: Any) -> int | None:
    if isinstance(value, bool):
        return None
    try:
        parsed = Decimal(str(value).strip())
    except (InvalidOperation, ValueError):
        return None
    if not parsed.is_finite() or parsed < 0 or parsed != parsed.to_integral_value():
        return None
    return int(parsed)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _safety_authority() -> dict[str, bool]:
    return {field: False for field in SAFETY_AUTHORITY_FIELDS}


def _nested_false_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _nested_false_safety() -> dict[str, bool]:
    return {field: False for field in SAFETY_PROOF_FIELDS}


def _status_blocked(status: str) -> bool:
    return any(term in status for term in BLOCKED_STATUS_TERMS)


def _risk_status_blocked(status: str) -> bool:
    return any(term in status for term in RISK_BLOCKED_STATUS_TERMS)


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
            "connected",
            "sent",
            "posted",
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


def _collection_present(value: Any) -> bool:
    return isinstance(value, Sequence) and not isinstance(value, (str, bytes)) and bool(value)


def _string_items(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [str(item) for item in value]
    return []


def _text_or_none(value: Any) -> str | None:
    text = _text(value)
    return text if text else None


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
