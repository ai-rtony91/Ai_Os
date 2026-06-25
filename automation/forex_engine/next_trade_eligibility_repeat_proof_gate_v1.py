from __future__ import annotations

from collections.abc import Mapping, Sequence
from decimal import Decimal, InvalidOperation
from typing import Any


PACKET_ID = "AIOS-FOREX-NEXT-TRADE-ELIGIBILITY-REPEAT-PROOF-GATE-V1"
GATE_VERSION = "v1"
DEFAULT_TRADE_ID = "UNKNOWN"

NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW = (
    "NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW"
)
NEXT_TRADE_BLOCKED_OPEN_EXPOSURE = "NEXT_TRADE_BLOCKED_OPEN_EXPOSURE"
NEXT_TRADE_BLOCKED_PRIOR_TRADE_STILL_OPEN = (
    "NEXT_TRADE_BLOCKED_PRIOR_TRADE_STILL_OPEN"
)
NEXT_TRADE_BLOCKED_BUCKET_GATE_NOT_READY = (
    "NEXT_TRADE_BLOCKED_BUCKET_GATE_NOT_READY"
)
NEXT_TRADE_BLOCKED_ALREADY_APPLIED_OR_REPEAT_RISK = (
    "NEXT_TRADE_BLOCKED_ALREADY_APPLIED_OR_REPEAT_RISK"
)
NEXT_TRADE_BLOCKED_OWNER_APPROVAL_MISSING = (
    "NEXT_TRADE_BLOCKED_OWNER_APPROVAL_MISSING"
)
NEXT_TRADE_BLOCKED_RISK_LIMIT = "NEXT_TRADE_BLOCKED_RISK_LIMIT"
NEXT_TRADE_BLOCKED_UNSAFE_OR_INVALID = "NEXT_TRADE_BLOCKED_UNSAFE_OR_INVALID"

OWNER_RUN_CLOSED_BY_TAKE_PROFIT = "OWNER_RUN_CLOSED_BY_TAKE_PROFIT"
OWNER_RUN_CLOSED_BY_STOP_LOSS = "OWNER_RUN_CLOSED_BY_STOP_LOSS"
OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER = (
    "OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER"
)
OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER = "OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER"
OWNER_RUN_CLOSED_BREAKEVEN_OTHER = "OWNER_RUN_CLOSED_BREAKEVEN_OTHER"
OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT = (
    "OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT"
)
OWNER_RUN_TRADE_NOT_FOUND = "OWNER_RUN_TRADE_NOT_FOUND"
OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID = "OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID"

CLOSED_PROFIT_STATUSES = {
    OWNER_RUN_CLOSED_BY_TAKE_PROFIT,
    OWNER_RUN_CLOSED_REALIZED_PROFIT_OTHER,
}
CLOSED_LOSS_STATUSES = {
    OWNER_RUN_CLOSED_BY_STOP_LOSS,
    OWNER_RUN_CLOSED_REALIZED_LOSS_OTHER,
}
CLOSED_BREAKEVEN_STATUSES = {OWNER_RUN_CLOSED_BREAKEVEN_OTHER}
CLOSED_OWNER_STATUSES = (
    CLOSED_PROFIT_STATUSES | CLOSED_LOSS_STATUSES | CLOSED_BREAKEVEN_STATUSES
)
STILL_OPEN_OWNER_STATUSES = {OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT}

BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT = (
    "BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT"
)
BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS = "BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS"
BUCKET_UPDATE_ELIGIBLE_BREAKEVEN = "BUCKET_UPDATE_ELIGIBLE_BREAKEVEN"
BUCKET_UPDATE_BLOCKED_ALREADY_APPLIED = (
    "BUCKET_UPDATE_BLOCKED_ALREADY_APPLIED"
)

BUCKET_READY_STATUSES = {
    BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT,
    BUCKET_UPDATE_ELIGIBLE_REALIZED_LOSS,
    BUCKET_UPDATE_ELIGIBLE_BREAKEVEN,
    "BUCKET_GATE_ELIGIBLE_REALIZED_PROFIT",
    "BUCKET_GATE_ELIGIBLE_REALIZED_LOSS",
    "BUCKET_GATE_ELIGIBLE_BREAKEVEN",
}
BUCKET_ALREADY_APPLIED_STATUSES = {
    BUCKET_UPDATE_BLOCKED_ALREADY_APPLIED,
    "BUCKET_GATE_ALREADY_APPLIED",
    "RESULT_BUCKET_ALREADY_APPLIED",
}

SAFE_REVIEW_KEYS = {
    "owner_approved_next_trade_review",
    "next_trade_review_allowed",
    "next_trade_review_authorized",
    "review_only",
    "review_only_mode",
    "risk_review_only",
}

EXECUTION_AUTHORITY_FIELDS = (
    "network_allowed",
    "network_call_allowed",
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
    "order_placement_allowed",
    "order_close_allowed",
    "order_mutation_allowed",
    "trade_mutation_allowed",
    "position_mutation_allowed",
    "live_endpoint_allowed",
    "live_trading_allowed",
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
    "order_placement_authorized",
    "next_allocation_authorized",
    "broker_call_authorized",
    "live_funding_authorized",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "live_funding_allowed",
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
    "order_close_performed",
    "order_mutation_performed",
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
    "next_order_authorized",
    "next_trade_authorized",
    "next_trade_executed",
    "order_placement_authorized",
    "scheduler_started",
    "daemon_started",
    "webhook_called",
    "live_funding_performed",
)

UNSAFE_TRUE_FIELDS = EXECUTION_AUTHORITY_FIELDS + SAFETY_PROOF_FIELDS
SENSITIVE_KEY_TERMS = (
    "token",
    "authorization",
    "account_id",
    "runtime_account_id",
    "credential",
    "secret",
    "password",
    "api_key",
    "apikey",
)
RAW_PAYLOAD_KEY_TERMS = ("raw_payload", "rawpayload", "raw_broker_payload")
REQUEST_HEADER_KEY_TERMS = ("headers", "request_headers", "requestheaders")
ENDPOINT_URL_KEY_TERMS = ("url", "endpoint_url", "endpointurl")
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
    "bucket",
    "scheduler",
    "daemon",
    "webhook",
    "funding",
    "next_order",
    "next_trade",
    "next_allocation",
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

REPEAT_RISK_BOOLEAN_KEYS = {
    "repeat_trade_risk",
    "repeat_risk_detected",
    "repeat_trade_blocker",
    "repeat_trade_blocked",
    "next_trade_repeat_risk",
    "prior_trade_already_used_for_next_trade",
    "owner_review_already_consumed",
    "next_trade_review_already_authorized",
    "next_trade_review_already_consumed",
}
USED_PRIOR_TRADE_COLLECTION_KEYS = {
    "used_prior_trade_ids",
    "reviewed_prior_trade_ids",
    "next_trade_review_prior_trade_ids",
    "next_trade_attempt_prior_trade_ids",
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
}
RISK_BLOCKED_STATUSES = {
    "RISK_LIMIT_BLOCKED",
    "BLOCKED_BY_RISK_LIMIT",
    "RISK_REVIEW_BLOCKED",
    "RISK_BLOCKED",
    "BLOCKED",
    "REJECTED",
}


def evaluate_next_trade_eligibility_repeat_proof_gate_v1(
    owner_run_decision: dict,
    bucket_gate_decision: dict,
    exposure_state: dict | None = None,
    owner_approval: dict | None = None,
    risk_state: dict | None = None,
) -> dict[str, Any]:
    owner = _mapping(owner_run_decision)
    bucket = _mapping(bucket_gate_decision)
    exposure = _mapping(exposure_state)
    approval = _mapping(owner_approval)
    risk = _mapping(risk_state)

    blockers: list[str] = []
    warnings: list[str] = []

    if not isinstance(owner_run_decision, Mapping):
        blockers.append("owner_run_decision_must_be_mapping")
    if not isinstance(bucket_gate_decision, Mapping):
        blockers.append("bucket_gate_decision_must_be_mapping")
    if exposure_state is None:
        blockers.append("exposure_state_required_for_zero_exposure_proof")
    elif not isinstance(exposure_state, Mapping):
        blockers.append("exposure_state_must_be_mapping_when_provided")
    if owner_approval is None:
        warnings.append("owner_approval_missing")
    elif not isinstance(owner_approval, Mapping):
        blockers.append("owner_approval_must_be_mapping_when_provided")
    if risk_state is None:
        warnings.append("risk_state_missing")
    elif not isinstance(risk_state, Mapping):
        blockers.append("risk_state_must_be_mapping_when_provided")

    trade_id = _trade_id(owner, bucket)
    prior_trade_result_status = _owner_status(owner)
    bucket_gate_status = _bucket_status(bucket)
    counts, exposure_blockers = _exposure_counts(exposure)

    unsafe_blockers: list[str] = []
    for label, payload in (
        ("owner_run_decision", owner),
        ("bucket_gate_decision", bucket),
        ("exposure_state", exposure),
        ("owner_approval", approval),
        ("risk_state", risk),
    ):
        if payload:
            unsafe_blockers.extend(_unsafe_input_blockers(payload, label))

    if blockers or unsafe_blockers:
        return _result(
            gate_status=NEXT_TRADE_BLOCKED_UNSAFE_OR_INVALID,
            blockers=blockers + unsafe_blockers,
            warnings=warnings,
            trade_id=trade_id,
            prior_trade_result_status=prior_trade_result_status,
            bucket_gate_status=bucket_gate_status,
            counts=counts,
        )

    if _prior_trade_still_open(prior_trade_result_status, owner):
        return _result(
            gate_status=NEXT_TRADE_BLOCKED_PRIOR_TRADE_STILL_OPEN,
            blockers=["prior_trade_still_open_no_closed_result_proof"],
            warnings=warnings,
            trade_id=trade_id,
            prior_trade_result_status=prior_trade_result_status,
            bucket_gate_status=bucket_gate_status,
            counts=counts,
        )

    owner_consistency_blockers = _owner_result_consistency_blockers(
        prior_trade_result_status,
        owner,
    )
    if prior_trade_result_status not in CLOSED_OWNER_STATUSES:
        owner_consistency_blockers.append(
            "prior_owner_run_result_must_be_closed_profit_loss_or_breakeven"
        )
    if owner_consistency_blockers:
        return _result(
            gate_status=NEXT_TRADE_BLOCKED_UNSAFE_OR_INVALID,
            blockers=owner_consistency_blockers,
            warnings=warnings,
            trade_id=trade_id,
            prior_trade_result_status=prior_trade_result_status,
            bucket_gate_status=bucket_gate_status,
            counts=counts,
        )

    repeat_risk_blockers = _repeat_risk_blockers(bucket, trade_id)
    if repeat_risk_blockers:
        return _result(
            gate_status=NEXT_TRADE_BLOCKED_ALREADY_APPLIED_OR_REPEAT_RISK,
            blockers=repeat_risk_blockers,
            warnings=warnings,
            trade_id=trade_id,
            prior_trade_result_status=prior_trade_result_status,
            bucket_gate_status=bucket_gate_status,
            counts=counts,
        )

    bucket_ready, bucket_blockers, bucket_warnings = _bucket_ready(
        bucket,
        bucket_gate_status,
        trade_id,
    )
    warnings.extend(bucket_warnings)
    if not bucket_ready:
        status = (
            NEXT_TRADE_BLOCKED_ALREADY_APPLIED_OR_REPEAT_RISK
            if bucket_gate_status in BUCKET_ALREADY_APPLIED_STATUSES
            else NEXT_TRADE_BLOCKED_BUCKET_GATE_NOT_READY
        )
        return _result(
            gate_status=status,
            blockers=bucket_blockers,
            warnings=warnings,
            trade_id=trade_id,
            prior_trade_result_status=prior_trade_result_status,
            bucket_gate_status=bucket_gate_status,
            counts=counts,
        )

    if exposure_blockers:
        return _result(
            gate_status=NEXT_TRADE_BLOCKED_UNSAFE_OR_INVALID,
            blockers=exposure_blockers,
            warnings=warnings,
            trade_id=trade_id,
            prior_trade_result_status=prior_trade_result_status,
            bucket_gate_status=bucket_gate_status,
            counts=counts,
        )

    open_exposure_blockers = _open_exposure_blockers(counts)
    if open_exposure_blockers:
        return _result(
            gate_status=NEXT_TRADE_BLOCKED_OPEN_EXPOSURE,
            blockers=open_exposure_blockers,
            warnings=warnings,
            trade_id=trade_id,
            prior_trade_result_status=prior_trade_result_status,
            bucket_gate_status=bucket_gate_status,
            counts=counts,
        )

    risk_blockers = _risk_limit_blockers(risk)
    if risk_blockers:
        return _result(
            gate_status=NEXT_TRADE_BLOCKED_RISK_LIMIT,
            blockers=risk_blockers,
            warnings=warnings,
            trade_id=trade_id,
            prior_trade_result_status=prior_trade_result_status,
            bucket_gate_status=bucket_gate_status,
            counts=counts,
        )

    if approval.get("owner_approved_next_trade_review") is not True:
        return _result(
            gate_status=NEXT_TRADE_BLOCKED_OWNER_APPROVAL_MISSING,
            blockers=["owner_approved_next_trade_review_true_required"],
            warnings=warnings,
            trade_id=trade_id,
            prior_trade_result_status=prior_trade_result_status,
            bucket_gate_status=bucket_gate_status,
            counts=counts,
        )

    return _result(
        gate_status=NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW,
        blockers=[],
        warnings=warnings,
        trade_id=trade_id,
        prior_trade_result_status=prior_trade_result_status,
        bucket_gate_status=bucket_gate_status,
        counts=counts,
    )


def next_trade_eligibility_repeat_proof_gate_template_v1() -> dict[str, Any]:
    return {
        "owner_run_decision": _owner_decision(
            OWNER_RUN_CLOSED_BY_TAKE_PROFIT,
            "0.0012",
        ),
        "bucket_gate_decision": _bucket_decision(
            BUCKET_UPDATE_ELIGIBLE_REALIZED_PROFIT,
        ),
        "exposure_state": _flat_exposure_state(),
        "owner_approval": {"owner_approved_next_trade_review": True},
        "risk_state": _risk_state(),
        "runtime_input_rule": {
            "sanitized_decisions_only": True,
            "review_eligibility_only": True,
            "broker_or_oanda_call_supported": False,
            "order_placement_supported": False,
            "bucket_mutation_supported": False,
            "next_trade_execution_supported": False,
            "live_funding_supported": False,
        },
    }


def next_trade_eligibility_repeat_proof_gate_samples_v1() -> (
    dict[str, dict[str, Any]]
):
    eligible = next_trade_eligibility_repeat_proof_gate_template_v1()
    return {
        "eligible": eligible,
        "open-exposure": {
            **eligible,
            "exposure_state": {
                "open_trade_count": 1,
                "open_position_count": 0,
                "pending_order_count": 0,
            },
        },
        "still-open": {
            **eligible,
            "owner_run_decision": _owner_decision(
                OWNER_RUN_STILL_OPEN_NO_REALIZED_RESULT,
                None,
                is_closed=False,
                is_open=True,
            ),
        },
        "bucket-not-ready": {
            **eligible,
            "bucket_gate_decision": _bucket_decision(
                "BUCKET_UPDATE_BLOCKED_STILL_OPEN",
                blockers=["prior_bucket_gate_still_waiting_on_closed_result"],
            ),
        },
        "already-applied": {
            **eligible,
            "bucket_gate_decision": {
                **_bucket_decision(BUCKET_UPDATE_BLOCKED_ALREADY_APPLIED),
                "already_applied": True,
            },
        },
        "owner-missing": {
            **eligible,
            "owner_approval": {"owner_approved_next_trade_review": False},
        },
        "risk-limit": {
            **eligible,
            "risk_state": _risk_state(max_loss_limit_breached=True),
        },
        "unsafe": {
            **eligible,
            "owner_run_decision": {
                **_owner_decision(OWNER_RUN_CLOSED_BY_TAKE_PROFIT, "0.0012"),
                "execution_authority": {
                    **_execution_authority(),
                    "broker_call_allowed": True,
                },
            },
        },
    }


def _result(
    *,
    gate_status: str,
    blockers: Sequence[str],
    warnings: Sequence[str],
    trade_id: str,
    prior_trade_result_status: str,
    bucket_gate_status: str,
    counts: Mapping[str, int],
) -> dict[str, Any]:
    review_authorized = gate_status == NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW
    safety = _safety_proof()
    result: dict[str, Any] = {
        "packet_id": PACKET_ID,
        "gate_version": GATE_VERSION,
        "gate_status": gate_status,
        "blockers": _unique(blockers),
        "warnings": _unique(_warnings(gate_status) + list(warnings)),
        "trade_id": trade_id or DEFAULT_TRADE_ID,
        "prior_trade_result_status": (
            prior_trade_result_status or "UNKNOWN"
        ),
        "bucket_gate_status": bucket_gate_status or "UNKNOWN",
        "open_trade_count": counts.get("open_trade_count", 0),
        "open_position_count": counts.get("open_position_count", 0),
        "pending_order_count": counts.get("pending_order_count", 0),
        "next_trade_review_authorized": review_authorized,
        "next_trade_authorized": False,
        "order_placement_authorized": False,
        "broker_call_authorized": False,
        "live_funding_authorized": False,
        "safety_proof": safety,
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(gate_status, trade_id),
    }
    result.update(safety)
    return result


def _owner_decision(
    status: str,
    realized_pl: str | None,
    *,
    is_closed: bool | None = True,
    is_open: bool | None = False,
) -> dict[str, Any]:
    decision: dict[str, Any] = {
        "packet_id": "AIOS-FOREX-OANDA-OWNER-RUN-CLOSED-RESULT-ADAPTER-EXERCISE-V1",
        "exercise_status": status,
        "trade_anchor": {"trade_id": "328"},
        "realized_pl": realized_pl,
        "execution_authority": _execution_authority(),
        "safety_proof": _safety_proof(),
    }
    if is_closed is not None:
        decision["is_closed"] = is_closed
        decision["classifier_decision"] = {"is_closed": is_closed}
    if is_open is not None:
        decision["is_open"] = is_open
    return decision


def _bucket_decision(
    gate_status: str,
    *,
    blockers: Sequence[str] | None = None,
    warnings: Sequence[str] | None = None,
) -> dict[str, Any]:
    return {
        "packet_id": "AIOS-FOREX-REALIZED-PL-RESULT-BUCKET-UPDATE-GATE-V1",
        "gate_status": gate_status,
        "trade_id": "328",
        "blockers": list(blockers or []),
        "warnings": list(warnings or []),
        "bucket_update_authorized": gate_status in BUCKET_READY_STATUSES,
        "bucket_update_performed": False,
        "next_trade_authorized": False,
        "execution_authority": _execution_authority(),
        "safety_proof": _safety_proof(),
    }


def _flat_exposure_state() -> dict[str, int]:
    return {
        "open_trade_count": 0,
        "open_position_count": 0,
        "pending_order_count": 0,
    }


def _risk_state(**overrides: Any) -> dict[str, Any]:
    state: dict[str, Any] = {
        "review_only": True,
        "risk_review_only": True,
        "execution_allowed": False,
        "next_trade_execution_allowed": False,
        "order_placement_allowed": False,
        "risk_limit_breached": False,
        "max_loss_limit_breached": False,
        "daily_stop_triggered": False,
        "kill_switch_active": False,
        "trading_halt_active": False,
    }
    state.update(overrides)
    return state


def _prior_trade_still_open(
    prior_trade_result_status: str,
    owner: Mapping[str, Any],
) -> bool:
    if prior_trade_result_status in STILL_OPEN_OWNER_STATUSES:
        return True
    if _bool_path(owner, ("is_open",)) is True:
        return True
    if _bool_path(owner, ("classifier_decision", "is_open")) is True:
        return True
    if _bool_path(owner, ("adapter_decision", "classifier_decision", "is_open")) is True:
        return True
    return False


def _owner_result_consistency_blockers(
    prior_trade_result_status: str,
    owner: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if prior_trade_result_status == OWNER_RUN_BLOCKED_UNSAFE_OR_INVALID:
        blockers.append("upstream_owner_run_blocked_unsafe_or_invalid")
    if prior_trade_result_status == OWNER_RUN_TRADE_NOT_FOUND:
        blockers.append("prior_trade_not_found")
    if _bool_path(owner, ("is_closed",)) is False:
        blockers.append("closed_owner_result_conflicts_with_is_closed_false")
    if _bool_path(owner, ("classifier_decision", "is_closed")) is False:
        blockers.append("closed_owner_result_conflicts_with_classifier_is_closed_false")
    realized = _realized_pl(owner)
    if prior_trade_result_status in CLOSED_PROFIT_STATUSES:
        if realized is None or realized <= 0:
            blockers.append("closed_profit_owner_result_requires_positive_realized_pl")
    if prior_trade_result_status in CLOSED_LOSS_STATUSES:
        if realized is None or realized >= 0:
            blockers.append("closed_loss_owner_result_requires_negative_realized_pl")
    if prior_trade_result_status in CLOSED_BREAKEVEN_STATUSES:
        if realized is None or realized != 0:
            blockers.append("closed_breakeven_owner_result_requires_zero_realized_pl")
    return blockers


def _bucket_ready(
    bucket: Mapping[str, Any],
    bucket_gate_status: str,
    trade_id: str,
) -> tuple[bool, list[str], list[str]]:
    if bucket_gate_status in BUCKET_READY_STATUSES:
        return True, [], []
    if bucket_gate_status in BUCKET_ALREADY_APPLIED_STATUSES:
        if _safe_idempotent_state(bucket, trade_id):
            return True, [], ["already_applied_bucket_gate_accepted_as_safe_idempotent"]
        return (
            False,
            ["bucket_gate_already_applied_without_safe_idempotent_state"],
            [],
        )
    return (
        False,
        [f"bucket_gate_status_not_ready_{bucket_gate_status or 'UNKNOWN'}"],
        [],
    )


def _safe_idempotent_state(bucket: Mapping[str, Any], trade_id: str) -> bool:
    if bucket.get("safe_idempotent_state") is True:
        return True
    if bucket.get("already_applied_safe_idempotent") is True:
        return True
    if bucket.get("idempotent_safe") is True:
        return True
    messages = _string_items(bucket.get("warnings")) + _string_items(
        bucket.get("blockers")
    )
    normalized_messages = {_normalized_key(item) for item in messages}
    expected_trade_message = _normalized_key(
        f"trade_{trade_id}_bucket_update_already_applied"
    )
    return (
        "idempotency_guard_blocked_reapply" in normalized_messages
        or expected_trade_message in normalized_messages
    )


def _repeat_risk_blockers(bucket: Mapping[str, Any], trade_id: str) -> list[str]:
    blockers: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            normalized = {_normalized_key(key): value for key, value in node.items()}
            for key in REPEAT_RISK_BOOLEAN_KEYS:
                if _truthy_unsafe(normalized.get(key)):
                    blockers.append(f"{key}_true")
            for key in USED_PRIOR_TRADE_COLLECTION_KEYS:
                if _contains_trade_id(normalized.get(key), trade_id):
                    blockers.append(f"{key}_contains_prior_trade_{trade_id}")
            for child in node.values():
                visit(child)
        elif isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
            for child in node:
                visit(child)

    visit(bucket)
    return _unique(blockers)


def _exposure_counts(
    exposure: Mapping[str, Any],
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
        value, blocker = _count_value(exposure, count_keys, collection_keys)
        counts[output_key] = value
        if blocker:
            blockers.append(f"{output_key}_{blocker}")
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


def _risk_limit_blockers(risk: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if not risk:
        return ["risk_state_required_for_review_only_gate"]
    if risk.get("review_only") is not True and risk.get("risk_review_only") is not True:
        blockers.append("risk_state_must_be_review_only")
    for key in RISK_LIMIT_BOOLEAN_KEYS:
        if _truthy_unsafe(risk.get(key)):
            blockers.append(f"{key}_true")
    risk_status = _text(risk.get("risk_status") or risk.get("status"))
    if risk_status in RISK_BLOCKED_STATUSES:
        blockers.append(f"risk_status_{risk_status}")
    return _unique(blockers)


def _unsafe_input_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            for raw_key, value in node.items():
                key = _normalized_key(raw_key)
                if key in SAFE_REVIEW_KEYS or _safe_bucket_gate_flag(label, key):
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
                visit(value)
        elif isinstance(node, Sequence) and not isinstance(node, (str, bytes)):
            for child in node:
                visit(child)

    visit(payload)
    return _unique(blockers)


def _safe_bucket_gate_flag(label: str, key: str) -> bool:
    return label == "bucket_gate_decision" and key == "bucket_update_authorized"


def _owner_status(owner: Mapping[str, Any]) -> str:
    for path in (
        ("exercise_status",),
        ("owner_run_status",),
        ("status",),
        ("decision", "exercise_status"),
        ("adapter_decision", "exercise_status"),
    ):
        value = _text(_nested_value(owner, path))
        if value:
            return value
    return ""


def _bucket_status(bucket: Mapping[str, Any]) -> str:
    for path in (
        ("gate_status",),
        ("bucket_gate_status",),
        ("status",),
        ("decision", "gate_status"),
    ):
        value = _text(_nested_value(bucket, path))
        if value:
            return value
    return ""


def _trade_id(
    owner: Mapping[str, Any],
    bucket: Mapping[str, Any],
) -> str:
    for source, paths in (
        (
            owner,
            (
                ("trade_id",),
                ("trade_anchor", "trade_id"),
                ("classifier_decision", "trade_id"),
                ("adapter_decision", "trade_id"),
                ("adapter_decision", "classifier_decision", "trade_id"),
            ),
        ),
        (bucket, (("trade_id",), ("proposed_bucket_delta", "trade_id"))),
    ):
        for path in paths:
            value = _text(_nested_value(source, path))
            if value:
                return value
    return DEFAULT_TRADE_ID


def _realized_pl(owner: Mapping[str, Any]) -> Decimal | None:
    for path in (
        ("realized_pl",),
        ("realizedPL",),
        ("classifier_decision", "realized_pl"),
        ("classifier_decision", "realizedPL"),
        ("adapter_decision", "realized_pl"),
        ("adapter_decision", "classifier_decision", "realized_pl"),
        ("adapter_decision", "classifier_decision", "realizedPL"),
    ):
        if _path_exists(owner, path):
            return _decimal_or_none(_nested_value(owner, path))
    return None


def _warnings(gate_status: str) -> list[str]:
    warnings = [
        "review_eligibility_only_not_execution",
        "no_broker_or_oanda_call_performed",
        "no_order_placement_authorized",
        "no_next_trade_execution_authorized",
        "no_bucket_mutation_performed",
        "no_live_funding_authorized",
        "owner_approval_authorizes_review_only",
    ]
    if gate_status == NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW:
        warnings.append("ready_for_owner_review_only")
    return warnings


def _next_safe_action(gate_status: str, trade_id: str) -> str:
    if gate_status == NEXT_TRADE_ELIGIBLE_FOR_OWNER_REVIEW:
        return "owner_review_next_trade_candidate_only_no_execution"
    if gate_status == NEXT_TRADE_BLOCKED_OPEN_EXPOSURE:
        return "clear_open_trades_positions_and_pending_orders_before_review"
    if gate_status == NEXT_TRADE_BLOCKED_PRIOR_TRADE_STILL_OPEN:
        return f"wait_for_prior_trade_{trade_id}_closed_result_proof"
    if gate_status == NEXT_TRADE_BLOCKED_BUCKET_GATE_NOT_READY:
        return "run_or_repair_bucket_gate_before_next_trade_review"
    if gate_status == NEXT_TRADE_BLOCKED_ALREADY_APPLIED_OR_REPEAT_RISK:
        return "stop_repeat_trade_review_until_idempotency_or_repeat_risk_is_resolved"
    if gate_status == NEXT_TRADE_BLOCKED_OWNER_APPROVAL_MISSING:
        return "obtain_owner_approved_next_trade_review_true_before_review"
    if gate_status == NEXT_TRADE_BLOCKED_RISK_LIMIT:
        return "repair_or_wait_for_risk_state_before_next_trade_review"
    return "remove_unsafe_or_invalid_fields_before_retry"


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


def _path_exists(mapping: Mapping[str, Any], path: Sequence[str]) -> bool:
    node: Any = mapping
    for key in path:
        if not isinstance(node, Mapping) or key not in node:
            return False
        node = node[key]
    return True


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


def _contains_trade_id(value: Any, trade_id: str) -> bool:
    if isinstance(value, str):
        return value.strip() == trade_id
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value) == trade_id
    if isinstance(value, Mapping):
        for key in ("trade_id", "tradeID", "id"):
            if _text(value.get(key)) == trade_id:
                return True
        return any(_contains_trade_id(child, trade_id) for child in value.values())
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return any(_contains_trade_id(item, trade_id) for item in value)
    return False


def _string_items(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [str(item) for item in value]
    return []


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return value.strip() if isinstance(value, str) else str(value).strip()


def _normalized_key(value: Any) -> str:
    return str(value).strip().replace("-", "_").replace(" ", "_").lower()


def _action_flag_key(key: str) -> bool:
    if key in SAFE_REVIEW_KEYS:
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
        }
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value == 1
    return False


def _sensitive_value_present(value: Any) -> bool:
    if value in (None, False):
        return False
    if isinstance(value, str):
        return bool(value.strip())
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


def _unique(values: Sequence[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = _text(value)
        if text and text not in seen:
            seen.add(text)
            output.append(text)
    return output
