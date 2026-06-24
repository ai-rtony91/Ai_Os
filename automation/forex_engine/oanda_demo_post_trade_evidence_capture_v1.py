from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-POST-TRADE-EVIDENCE-CAPTURE-V1"
EVIDENCE_VERSION = "v1"

EVIDENCE_BLOCKED_MISSING_OWNER_COMMAND = "EVIDENCE_BLOCKED_MISSING_OWNER_COMMAND"
EVIDENCE_BLOCKED_OWNER_COMMAND_NOT_READY = (
    "EVIDENCE_BLOCKED_OWNER_COMMAND_NOT_READY"
)
EVIDENCE_BLOCKED_MISSING_BROKER_CALL_RESULT = (
    "EVIDENCE_BLOCKED_MISSING_BROKER_CALL_RESULT"
)
EVIDENCE_BLOCKED_BROKER_CALL_NOT_ATTEMPTED = (
    "EVIDENCE_BLOCKED_BROKER_CALL_NOT_ATTEMPTED"
)
EVIDENCE_BLOCKED_MISSING_POST_TRADE_EVIDENCE = (
    "EVIDENCE_BLOCKED_MISSING_POST_TRADE_EVIDENCE"
)
EVIDENCE_BLOCKED_OWNER_CONFIRMATION = "EVIDENCE_BLOCKED_OWNER_CONFIRMATION"
EVIDENCE_CAPTURE_READY = "EVIDENCE_CAPTURE_READY"
EVIDENCE_REJECTED = "EVIDENCE_REJECTED"

OWNER_COMMAND_READY_STATUS = "OWNER_COMMAND_READY_FOR_MANUAL_DEMO_ORDER_COMMAND"
BROKER_CALL_ATTEMPTED_STATUS = "BROKER_CALL_ATTEMPTED_DEMO_ORDER_ONCE"
BROKER_CALL_DRY_RUN_STATUS = "BROKER_CALL_DRY_RUN_READY"

POST_TRADE_EVIDENCE_MODES = (
    "DRY_RUN_REHEARSAL",
    "ORDER_REJECTED",
    "ORDER_SUBMITTED",
    "ORDER_FILLED",
    "ORDER_CLOSED",
)

FILLED_OR_REJECTED_VALUES = (
    "FILLED",
    "REJECTED",
    "SUBMITTED",
    "PENDING",
    "CLOSED",
    "DRY_RUN",
)

SENSITIVE_KEY_TERMS = (
    "account_id",
    "token",
    "credential",
    "secret",
    "password",
    "authorization",
)

ALLOWED_SENSITIVE_EVIDENCE_KEYS = {
    "account_id_persistence_detected",
    "credential_persistence_detected",
}

ALLOWED_SENSITIVE_BROKER_KEYS = {
    "account_id_reference",
    "authorization_reference",
}

EXECUTION_AUTHORITY_FIELDS = (
    "execution_allowed",
    "demo_order_allowed",
    "live_order_allowed",
    "broker_write_allowed",
    "autonomous_order_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
)

OWNER_CONFIRMATION_REQUIRED_TRUE_FIELDS = (
    "owner_confirmed_post_trade_evidence_reviewed",
    "owner_confirmed_no_second_order",
    "owner_confirmed_no_credentials_in_evidence",
    "owner_confirmed_no_account_ids_in_evidence",
    "owner_confirmed_stop_loss_checked",
    "owner_confirmed_take_profit_checked",
    "owner_confirmed_pl_recorded",
)


def evaluate_oanda_demo_post_trade_evidence_capture_v1(
    owner_command_result: dict | None = None,
    broker_call_result: dict | None = None,
    post_trade_evidence: dict | None = None,
    owner_evidence_confirmation: dict | None = None,
) -> dict:
    owner_command = _mapping(owner_command_result)
    broker_call = _mapping(broker_call_result)
    evidence = _mapping(post_trade_evidence)
    owner_confirmation = _mapping(owner_evidence_confirmation)

    if not owner_command:
        return _result(
            status=EVIDENCE_BLOCKED_MISSING_OWNER_COMMAND,
            blockers=["missing_owner_command_result"],
            warnings=_warnings(EVIDENCE_BLOCKED_MISSING_OWNER_COMMAND),
            owner_command=owner_command,
            broker_call=broker_call,
            evidence=evidence,
            owner_confirmation=owner_confirmation,
        )

    unsafe_blockers = _unsafe_blockers(owner_command, broker_call, evidence)
    owner_command_blockers = _owner_command_blockers(owner_command)
    broker_missing = not broker_call
    broker_call_blockers = [] if broker_missing else _broker_call_blockers(broker_call)
    evidence_missing = not evidence
    evidence_blockers = [] if evidence_missing else _evidence_blockers(evidence)
    owner_confirmation_blockers = _owner_confirmation_blockers(owner_confirmation)

    blockers = _unique(
        unsafe_blockers
        + owner_command_blockers
        + (["missing_broker_call_result"] if broker_missing else [])
        + broker_call_blockers
        + (["missing_post_trade_evidence"] if evidence_missing else [])
        + evidence_blockers
        + owner_confirmation_blockers
    )
    status = _status(
        unsafe_blockers=unsafe_blockers,
        owner_command_blockers=owner_command_blockers,
        broker_missing=broker_missing,
        broker_call_blockers=broker_call_blockers,
        evidence_missing=evidence_missing,
        evidence_blockers=evidence_blockers,
        owner_confirmation_blockers=owner_confirmation_blockers,
    )

    return _result(
        status=status,
        blockers=blockers,
        warnings=_warnings(status),
        owner_command=owner_command,
        broker_call=broker_call,
        evidence=evidence,
        owner_confirmation=owner_confirmation,
    )


def _status(
    *,
    unsafe_blockers: list[str],
    owner_command_blockers: list[str],
    broker_missing: bool,
    broker_call_blockers: list[str],
    evidence_missing: bool,
    evidence_blockers: list[str],
    owner_confirmation_blockers: list[str],
) -> str:
    if unsafe_blockers:
        return EVIDENCE_REJECTED
    if owner_command_blockers:
        return EVIDENCE_BLOCKED_OWNER_COMMAND_NOT_READY
    if broker_missing:
        return EVIDENCE_BLOCKED_MISSING_BROKER_CALL_RESULT
    if broker_call_blockers:
        return EVIDENCE_BLOCKED_BROKER_CALL_NOT_ATTEMPTED
    if evidence_missing or evidence_blockers:
        return EVIDENCE_BLOCKED_MISSING_POST_TRADE_EVIDENCE
    if owner_confirmation_blockers:
        return EVIDENCE_BLOCKED_OWNER_CONFIRMATION
    return EVIDENCE_CAPTURE_READY


def _owner_command_blockers(owner_command: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if owner_command.get("status") != OWNER_COMMAND_READY_STATUS:
        blockers.append("owner_command_status_not_ready")
    blockers.extend(_authority_blockers(owner_command, "owner_command_result"))
    return blockers


def _broker_call_blockers(broker_call: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    status = broker_call.get("status")
    if status not in {BROKER_CALL_ATTEMPTED_STATUS, BROKER_CALL_DRY_RUN_STATUS}:
        blockers.append("broker_call_result_must_be_attempted_once_or_dry_run")
    if _order_attempt_count(broker_call) > 1:
        blockers.append("broker_call_order_attempt_count_must_not_exceed_one")
    if _bool(broker_call.get("live_order_allowed")):
        blockers.append("broker_call_live_order_allowed_must_not_be_true")
    if _bool(broker_call.get("autonomous_order_allowed")):
        blockers.append("broker_call_autonomous_order_allowed_must_not_be_true")
    blockers.extend(_authority_blockers(broker_call, "broker_call_result"))
    return blockers


def _evidence_blockers(evidence: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    evidence_mode = evidence.get("evidence_mode")
    if evidence_mode not in POST_TRADE_EVIDENCE_MODES:
        blockers.append("post_trade_evidence_mode_invalid")
    if evidence.get("broker") != "OANDA_DEMO":
        blockers.append("post_trade_evidence_broker_must_be_oanda_demo")
    if evidence.get("environment") != "DEMO":
        blockers.append("post_trade_evidence_environment_must_be_demo")
    if not isinstance(evidence.get("order_attempted"), bool):
        blockers.append("post_trade_evidence_order_attempted_must_be_boolean")
    if evidence_mode in {"ORDER_SUBMITTED", "ORDER_FILLED", "ORDER_CLOSED"}:
        if not _text(evidence.get("order_id_or_sanitized_reference")):
            blockers.append("post_trade_evidence_sanitized_order_reference_required")
    if evidence.get("filled_or_rejected") not in FILLED_OR_REJECTED_VALUES:
        blockers.append("post_trade_evidence_filled_or_rejected_invalid")
    if not _present(evidence.get("fill_price_or_rejection_reason")):
        blockers.append("post_trade_evidence_fill_or_rejection_reason_required")
    if not isinstance(evidence.get("stop_loss_attached"), bool):
        blockers.append("post_trade_evidence_stop_loss_attached_must_be_boolean")
    if not isinstance(evidence.get("take_profit_attached"), bool):
        blockers.append("post_trade_evidence_take_profit_attached_must_be_boolean")
    if not _numeric_or_null(evidence.get("realized_pl_when_closed")):
        blockers.append("post_trade_evidence_realized_pl_must_be_numeric_or_null")
    if not _numeric_or_null(evidence.get("unrealized_pl_snapshot")):
        blockers.append("post_trade_evidence_unrealized_pl_must_be_numeric_or_null")
    if evidence_mode == "ORDER_CLOSED" and not _present(evidence.get("close_reason")):
        blockers.append("post_trade_evidence_close_reason_required_when_closed")
    if not _numeric_or_null(evidence.get("post_balance")):
        blockers.append("post_trade_evidence_post_balance_must_be_numeric_or_null")
    if not _numeric_or_null(evidence.get("post_nav")):
        blockers.append("post_trade_evidence_post_nav_must_be_numeric_or_null")
    if not _text(evidence.get("timestamp_utc")):
        blockers.append("post_trade_evidence_timestamp_utc_required")
    if not _bool(evidence.get("one_order_only")):
        blockers.append("post_trade_evidence_one_order_only_required")
    if _number(evidence.get("max_order_attempts"), -1) != 1:
        blockers.append("post_trade_evidence_max_order_attempts_must_be_one")
    if not _bool(evidence.get("no_second_order")):
        blockers.append("post_trade_evidence_no_second_order_required")
    return blockers


def _owner_confirmation_blockers(owner_confirmation: Mapping[str, Any]) -> list[str]:
    if not owner_confirmation:
        return ["missing_owner_evidence_confirmation"]

    blockers: list[str] = []
    for field in OWNER_CONFIRMATION_REQUIRED_TRUE_FIELDS:
        if not _bool(owner_confirmation.get(field)):
            blockers.append(f"{field}_required")
    blockers.extend(_authority_blockers(owner_confirmation, "owner_confirmation"))
    return blockers


def _result(
    *,
    status: str,
    blockers: list[str],
    warnings: list[str],
    owner_command: Mapping[str, Any],
    broker_call: Mapping[str, Any],
    evidence: Mapping[str, Any],
    owner_confirmation: Mapping[str, Any],
) -> dict[str, Any]:
    classification = _classification(evidence) if status == EVIDENCE_CAPTURE_READY else "UNCLASSIFIED"
    overnight_required = _overnight_followup_required(evidence, classification)
    morning_required = overnight_required
    return {
        "packet_id": PACKET_ID,
        "evidence_version": EVIDENCE_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "owner_command_summary": _owner_command_summary(owner_command),
        "broker_call_summary": _broker_call_summary(broker_call),
        "evidence_summary": _evidence_summary(evidence),
        "normalized_evidence_package": _normalized_evidence_package(
            evidence,
            classification,
            overnight_required,
            morning_required,
        )
        if status == EVIDENCE_CAPTURE_READY
        else None,
        "post_trade_classification": classification,
        "overnight_followup_required": overnight_required,
        "morning_proof_required": morning_required,
        "owner_confirmation_summary": _owner_confirmation_summary(owner_confirmation),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status, overnight_required),
    }


def _owner_command_summary(owner_command: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": _text(owner_command.get("status"), "MISSING"),
        "ready": owner_command.get("status") == OWNER_COMMAND_READY_STATUS,
        "execution_authority_false": not _authority_blockers(
            owner_command, "owner_command_result"
        ),
    }


def _broker_call_summary(broker_call: Mapping[str, Any]) -> dict[str, Any]:
    status = _text(broker_call.get("status"), "MISSING")
    return {
        "status": status,
        "actual_attempted_once": status == BROKER_CALL_ATTEMPTED_STATUS,
        "dry_run_rehearsal": status == BROKER_CALL_DRY_RUN_STATUS,
        "order_attempt_count": _order_attempt_count(broker_call),
        "live_order_allowed": _bool(broker_call.get("live_order_allowed")),
        "autonomous_order_allowed": _bool(
            broker_call.get("autonomous_order_allowed")
        ),
        "sensitive_key_terms_detected": _forbidden_key_terms(
            broker_call,
            allowed_keys=ALLOWED_SENSITIVE_BROKER_KEYS,
        ),
        "execution_authority_false": not _authority_blockers(
            broker_call, "broker_call_result"
        ),
    }


def _evidence_summary(evidence: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "evidence_mode": _text(evidence.get("evidence_mode"), "MISSING"),
        "broker": _text(evidence.get("broker"), "MISSING"),
        "environment": _text(evidence.get("environment"), "MISSING"),
        "order_attempted": evidence.get("order_attempted")
        if isinstance(evidence.get("order_attempted"), bool)
        else "MISSING",
        "sanitized_order_reference_present": bool(
            _text(evidence.get("order_id_or_sanitized_reference"))
        ),
        "filled_or_rejected": _text(evidence.get("filled_or_rejected"), "MISSING"),
        "stop_loss_attached": evidence.get("stop_loss_attached")
        if isinstance(evidence.get("stop_loss_attached"), bool)
        else "MISSING",
        "take_profit_attached": evidence.get("take_profit_attached")
        if isinstance(evidence.get("take_profit_attached"), bool)
        else "MISSING",
        "realized_pl_recorded": _numeric_or_null(
            evidence.get("realized_pl_when_closed")
        ),
        "unrealized_pl_recorded": _numeric_or_null(
            evidence.get("unrealized_pl_snapshot")
        ),
        "post_balance_recorded": _numeric_or_null(evidence.get("post_balance")),
        "post_nav_recorded": _numeric_or_null(evidence.get("post_nav")),
        "timestamp_utc_present": bool(_text(evidence.get("timestamp_utc"))),
        "one_order_only": _bool(evidence.get("one_order_only")),
        "max_order_attempts": _number(evidence.get("max_order_attempts"), 0),
        "no_second_order": _bool(evidence.get("no_second_order")),
        "credential_persistence_detected": _bool(
            evidence.get("credential_persistence_detected")
        ),
        "account_identifier_persistence_detected": _bool(
            evidence.get("account_id_persistence_detected")
        ),
        "sensitive_key_terms_detected": _forbidden_key_terms(
            evidence,
            allowed_keys=ALLOWED_SENSITIVE_EVIDENCE_KEYS,
        ),
    }


def _normalized_evidence_package(
    evidence: Mapping[str, Any],
    classification: str,
    overnight_required: bool,
    morning_required: bool,
) -> dict[str, Any]:
    return {
        "ready": True,
        "packet_id": PACKET_ID,
        "evidence_version": EVIDENCE_VERSION,
        "evidence_mode": evidence.get("evidence_mode"),
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "order_attempted": evidence.get("order_attempted"),
        "sanitized_order_reference": _text(
            evidence.get("order_id_or_sanitized_reference"), "DRY_RUN_OR_REJECTED"
        ),
        "filled_or_rejected": evidence.get("filled_or_rejected"),
        "fill_price_or_rejection_reason": evidence.get(
            "fill_price_or_rejection_reason"
        ),
        "stop_loss_attached": evidence.get("stop_loss_attached"),
        "take_profit_attached": evidence.get("take_profit_attached"),
        "realized_pl_when_closed": evidence.get("realized_pl_when_closed"),
        "unrealized_pl_snapshot": evidence.get("unrealized_pl_snapshot"),
        "close_reason": evidence.get("close_reason"),
        "post_balance": evidence.get("post_balance"),
        "post_nav": evidence.get("post_nav"),
        "timestamp_utc": evidence.get("timestamp_utc"),
        "one_order_only": True,
        "max_order_attempts": 1,
        "no_second_order": True,
        "credential_persistence_detected": False,
        "account_reference_persistence_detected": False,
        "post_trade_classification": classification,
        "hold_allowed_overnight": _bool(evidence.get("hold_allowed_overnight")),
        "overnight_followup_required": overnight_required,
        "morning_proof_required": morning_required,
    }


def _owner_confirmation_summary(
    owner_confirmation: Mapping[str, Any],
) -> dict[str, bool]:
    return {
        field: _bool(owner_confirmation.get(field))
        for field in OWNER_CONFIRMATION_REQUIRED_TRUE_FIELDS
    }


def _classification(evidence: Mapping[str, Any]) -> str:
    mode = evidence.get("evidence_mode")
    filled_or_rejected = evidence.get("filled_or_rejected")
    if mode == "DRY_RUN_REHEARSAL":
        return "DRY_RUN_ONLY"
    if mode == "ORDER_REJECTED":
        return "NO_FILL_REJECTED"
    if mode == "ORDER_SUBMITTED" or filled_or_rejected in {"SUBMITTED", "PENDING"}:
        return "OPEN_OR_PENDING"
    if mode == "ORDER_FILLED":
        return "OPEN_POSITION"
    if mode == "ORDER_CLOSED":
        realized = _number(evidence.get("realized_pl_when_closed"), 0)
        if realized > 0:
            return "PROFIT"
        if realized < 0:
            return "LOSS"
        return "BREAKEVEN"
    return "UNCLASSIFIED"


def _overnight_followup_required(
    evidence: Mapping[str, Any],
    classification: str,
) -> bool:
    return classification in {"OPEN_OR_PENDING", "OPEN_POSITION"} and _bool(
        evidence.get("hold_allowed_overnight")
    )


def _unsafe_blockers(
    owner_command: Mapping[str, Any],
    broker_call: Mapping[str, Any],
    evidence: Mapping[str, Any],
) -> list[str]:
    blockers: list[str] = []
    blockers.extend(_authority_blockers(owner_command, "owner_command_result"))
    blockers.extend(_authority_blockers(broker_call, "broker_call_result"))
    blockers.extend(_authority_blockers(evidence, "post_trade_evidence"))
    if _order_attempt_count(broker_call) > 1:
        blockers.append("one_order_cap_violated")
    if _bool(broker_call.get("live_order_allowed")):
        blockers.append("broker_call_live_order_allowed_true")
    if _bool(broker_call.get("autonomous_order_allowed")):
        blockers.append("broker_call_autonomous_order_allowed_true")
    for term in _forbidden_key_terms(
        broker_call,
        allowed_keys=ALLOWED_SENSITIVE_BROKER_KEYS,
    ):
        blockers.append(f"broker_call_forbidden_{term}_field")
    for term in _forbidden_key_terms(
        evidence,
        allowed_keys=ALLOWED_SENSITIVE_EVIDENCE_KEYS,
    ):
        blockers.append(f"post_trade_evidence_forbidden_{term}_field")
    if _bool(evidence.get("credential_persistence_detected")):
        blockers.append("post_trade_evidence_credential_persistence_detected")
    if _bool(evidence.get("account_id_persistence_detected")):
        blockers.append("post_trade_evidence_account_id_persistence_detected")
    return blockers


def _forbidden_key_terms(
    value: Any,
    *,
    allowed_keys: set[str],
) -> list[str]:
    found: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            for key, child in node.items():
                key_text = str(key).lower()
                if key_text in allowed_keys and _allowed_sensitive_value(
                    key_text, child
                ):
                    visit(child)
                    continue
                for term in SENSITIVE_KEY_TERMS:
                    if term in key_text and term not in found:
                        found.append(term)
                visit(child)
        elif isinstance(node, list):
            for child in node:
                visit(child)

    visit(value)
    return found


def _allowed_sensitive_value(key_text: str, value: Any) -> bool:
    if key_text in ALLOWED_SENSITIVE_EVIDENCE_KEYS:
        return value is False
    if key_text == "account_id_reference":
        return value == "RUNTIME_ONLY_ACCOUNT_ID"
    if key_text == "authorization_reference":
        return value == "RUNTIME_ONLY_BEARER_TOKEN"
    return False


def _authority_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []
    authority = _mapping(payload.get("execution_authority"))
    for field in EXECUTION_AUTHORITY_FIELDS:
        if _bool(payload.get(field)) or _bool(authority.get(field)):
            blockers.append(f"unsafe_{label}_{field}_true")
    return blockers


def _order_attempt_count(broker_call: Mapping[str, Any]) -> int:
    execution_attempt = _mapping(broker_call.get("execution_attempt"))
    count = broker_call.get("order_attempt_count")
    if isinstance(count, int) and not isinstance(count, bool):
        return count
    nested_count = execution_attempt.get("order_attempt_count")
    if isinstance(nested_count, int) and not isinstance(nested_count, bool):
        return nested_count
    return 0


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _warnings(status: str) -> list[str]:
    warnings = [
        "post_trade_evidence_capture_only",
        "execution_authority_false",
        "no_oanda_call_performed",
        "no_broker_call_performed",
        "no_credentials_or_account_ids_read_or_persisted",
        "no_order_placement_performed",
    ]
    if status == EVIDENCE_CAPTURE_READY:
        warnings.append("sanitize_evidence_before_storage")
    return warnings


def _next_safe_action(status: str, overnight_required: bool) -> str:
    if status == EVIDENCE_CAPTURE_READY and overnight_required:
        return "capture_morning_proof_for_open_overnight_demo_position"
    return {
        EVIDENCE_BLOCKED_MISSING_OWNER_COMMAND: "provide_owner_command_result",
        EVIDENCE_BLOCKED_OWNER_COMMAND_NOT_READY: (
            "repair_owner_command_readiness_before_evidence_capture"
        ),
        EVIDENCE_BLOCKED_MISSING_BROKER_CALL_RESULT: (
            "provide_broker_call_result_or_dry_run_rehearsal_result"
        ),
        EVIDENCE_BLOCKED_BROKER_CALL_NOT_ATTEMPTED: (
            "provide_attempted_once_or_dry_run_broker_call_result"
        ),
        EVIDENCE_BLOCKED_MISSING_POST_TRADE_EVIDENCE: (
            "provide_complete_sanitized_post_trade_evidence"
        ),
        EVIDENCE_BLOCKED_OWNER_CONFIRMATION: (
            "complete_owner_post_trade_evidence_confirmations"
        ),
        EVIDENCE_CAPTURE_READY: "store_sanitized_evidence_package_and_prepare_result_bucket",
        EVIDENCE_REJECTED: "remove_sensitive_or_unsafe_evidence_before_capture",
    }.get(status, "stop_and_review_post_trade_evidence_state")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _number(value: Any, default: float) -> float:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else default


def _numeric_or_null(value: Any) -> bool:
    return value is None or (
        isinstance(value, (int, float)) and not isinstance(value, bool)
    )


def _present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
