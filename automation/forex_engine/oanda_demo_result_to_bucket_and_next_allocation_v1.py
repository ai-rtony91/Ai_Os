from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-RESULT-TO-BUCKET-AND-NEXT-ALLOCATION-V1"
BUCKET_UPDATE_VERSION = "v1"

BUCKET_BLOCKED_MISSING_POST_TRADE_CAPTURE = (
    "BUCKET_BLOCKED_MISSING_POST_TRADE_CAPTURE"
)
BUCKET_BLOCKED_POST_TRADE_NOT_READY = "BUCKET_BLOCKED_POST_TRADE_NOT_READY"
BUCKET_BLOCKED_MISSING_BUCKET_STATE = "BUCKET_BLOCKED_MISSING_BUCKET_STATE"
BUCKET_BLOCKED_ALLOCATION_POLICY = "BUCKET_BLOCKED_ALLOCATION_POLICY"
BUCKET_BLOCKED_OWNER_CONFIRMATION = "BUCKET_BLOCKED_OWNER_CONFIRMATION"
BUCKET_UPDATE_READY = "BUCKET_UPDATE_READY"
BUCKET_REJECTED = "BUCKET_REJECTED"

POST_TRADE_READY_STATUS = "EVIDENCE_CAPTURE_READY"
POST_TRADE_CLASSIFICATIONS = (
    "DRY_RUN_ONLY",
    "NO_FILL_REJECTED",
    "OPEN_OR_PENDING",
    "OPEN_POSITION",
    "PROFIT",
    "LOSS",
    "BREAKEVEN",
)

ALLOCATION_MODES = (
    "PAUSE",
    "CONTINUE_DEMO",
    "REDUCE_RISK",
    "INCREASE_EVIDENCE",
)

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
    "owner_confirmed_result_reviewed",
    "owner_confirmed_bucket_update_demo_only",
    "owner_confirmed_no_live_allocation",
    "owner_confirmed_next_trade_requires_approval",
    "owner_confirmed_no_autonomous_compounding",
)

SENSITIVE_KEY_TERMS = (
    "account_id",
    "token",
    "credential",
    "secret",
    "password",
    "authorization",
)

SAFE_SENSITIVE_STATUS_KEYS = {
    "account_reference_persistence_detected",
    "account_identifier_persistence_detected",
    "account_id_persistence_detected",
    "credential_persistence_detected",
    "owner_confirmed_no_account_ids_in_evidence",
    "owner_confirmed_no_credentials_in_evidence",
    "sensitive_key_terms_detected",
}


def evaluate_oanda_demo_result_to_bucket_and_next_allocation_v1(
    post_trade_capture_result: dict | None = None,
    bucket_state: dict | None = None,
    allocation_policy: dict | None = None,
    owner_bucket_confirmation: dict | None = None,
) -> dict:
    post_trade = _mapping(post_trade_capture_result)
    bucket = _mapping(bucket_state)
    policy = _mapping(allocation_policy)
    owner_confirmation = _mapping(owner_bucket_confirmation)

    if not post_trade:
        return _result(
            status=BUCKET_BLOCKED_MISSING_POST_TRADE_CAPTURE,
            blockers=["missing_post_trade_capture_result"],
            warnings=_warnings(BUCKET_BLOCKED_MISSING_POST_TRADE_CAPTURE),
            post_trade=post_trade,
            bucket=bucket,
            policy=policy,
            owner_confirmation=owner_confirmation,
        )

    unsafe_blockers = _unsafe_blockers(post_trade)
    post_trade_blockers = _post_trade_blockers(post_trade)
    bucket_missing = not bucket
    bucket_blockers = [] if bucket_missing else _bucket_state_blockers(bucket)
    policy_blockers = _allocation_policy_blockers(policy, bucket)
    owner_blockers = _owner_confirmation_blockers(owner_confirmation)

    blockers = _unique(
        unsafe_blockers
        + post_trade_blockers
        + (["missing_bucket_state"] if bucket_missing else [])
        + bucket_blockers
        + policy_blockers
        + owner_blockers
    )
    status = _status(
        unsafe_blockers=unsafe_blockers,
        post_trade_blockers=post_trade_blockers,
        bucket_missing=bucket_missing,
        bucket_blockers=bucket_blockers,
        policy_blockers=policy_blockers,
        owner_blockers=owner_blockers,
    )

    return _result(
        status=status,
        blockers=blockers,
        warnings=_warnings(status),
        post_trade=post_trade,
        bucket=bucket,
        policy=policy,
        owner_confirmation=owner_confirmation,
    )


def _status(
    *,
    unsafe_blockers: list[str],
    post_trade_blockers: list[str],
    bucket_missing: bool,
    bucket_blockers: list[str],
    policy_blockers: list[str],
    owner_blockers: list[str],
) -> str:
    if unsafe_blockers:
        return BUCKET_REJECTED
    if post_trade_blockers:
        return BUCKET_BLOCKED_POST_TRADE_NOT_READY
    if bucket_missing or bucket_blockers:
        return BUCKET_BLOCKED_MISSING_BUCKET_STATE
    if policy_blockers:
        return BUCKET_BLOCKED_ALLOCATION_POLICY
    if owner_blockers:
        return BUCKET_BLOCKED_OWNER_CONFIRMATION
    return BUCKET_UPDATE_READY


def _post_trade_blockers(post_trade: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if post_trade.get("status") != POST_TRADE_READY_STATUS:
        blockers.append("post_trade_capture_status_not_ready")
    if post_trade.get("post_trade_classification") not in POST_TRADE_CLASSIFICATIONS:
        blockers.append("post_trade_classification_not_supported")
    if not _mapping(post_trade.get("normalized_evidence_package")):
        blockers.append("normalized_evidence_package_required")
    blockers.extend(_authority_blockers(post_trade, "post_trade_capture_result"))
    return blockers


def _bucket_state_blockers(bucket: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if bucket.get("bucket_currency") != "USD":
        blockers.append("bucket_state_currency_must_be_usd")
    if not _number_at_least(bucket.get("starting_bucket_balance"), 0):
        blockers.append("bucket_state_starting_balance_must_be_non_negative")
    if not _number_at_least(bucket.get("current_bucket_balance"), 0):
        blockers.append("bucket_state_current_balance_must_be_non_negative")
    if not _is_number(bucket.get("total_realized_pl")):
        blockers.append("bucket_state_total_realized_pl_must_be_numeric")
    if not _number_greater_than(bucket.get("current_cycle_start_balance"), 0):
        blockers.append("bucket_state_cycle_start_balance_must_be_positive")
    if not _is_number(bucket.get("current_cycle_realized_pl")):
        blockers.append("bucket_state_cycle_realized_pl_must_be_numeric")
    if not _number_greater_than(bucket.get("cycle_profit_target_min_pct"), 0):
        blockers.append("bucket_state_cycle_profit_target_min_pct_must_be_positive")
    if not _is_number(bucket.get("cycle_profit_target_max_pct")):
        blockers.append("bucket_state_cycle_profit_target_max_pct_must_be_numeric")
    elif _number(bucket.get("cycle_profit_target_max_pct"), 0) < _number(
        bucket.get("cycle_profit_target_min_pct"), 0
    ):
        blockers.append("bucket_state_cycle_profit_target_max_pct_must_gte_min")
    if not _number_greater_than(bucket.get("max_single_trade_risk_pct"), 0):
        blockers.append("bucket_state_max_single_trade_risk_pct_must_be_positive")
    elif _number(bucket.get("max_single_trade_risk_pct"), 0) > 5:
        blockers.append("bucket_state_max_single_trade_risk_pct_must_be_lte_five")
    if not _bool(bucket.get("one_order_only")):
        blockers.append("bucket_state_one_order_only_required")
    if not _bool(bucket.get("demo_only")):
        blockers.append("bucket_state_demo_only_required")
    if _bool(bucket.get("live_trading")):
        blockers.append("bucket_state_live_trading_must_be_false")
    blockers.extend(_authority_blockers(bucket, "bucket_state"))
    return blockers


def _allocation_policy_blockers(
    policy: Mapping[str, Any], bucket: Mapping[str, Any]
) -> list[str]:
    if not policy:
        return ["missing_allocation_policy"]

    blockers: list[str] = []
    if policy.get("allocation_mode") not in ALLOCATION_MODES:
        blockers.append("allocation_policy_mode_invalid")
    if not isinstance(policy.get("compounding_enabled"), bool):
        blockers.append("allocation_policy_compounding_enabled_must_be_boolean")
    if not isinstance(policy.get("collect_profit_at_target"), bool):
        blockers.append("allocation_policy_collect_profit_at_target_must_be_boolean")
    if not isinstance(policy.get("require_more_evidence_after_loss"), bool):
        blockers.append(
            "allocation_policy_require_more_evidence_after_loss_must_be_boolean"
        )
    if not _bool(policy.get("require_owner_approval_for_next_trade")):
        blockers.append(
            "allocation_policy_require_owner_approval_for_next_trade_required"
        )
    max_next_risk = policy.get("max_next_trade_risk_pct")
    max_bucket_risk = _number(bucket.get("max_single_trade_risk_pct"), 0)
    if not _number_greater_than(max_next_risk, 0):
        blockers.append("allocation_policy_max_next_trade_risk_pct_must_be_positive")
    elif _number(max_next_risk, 0) > max_bucket_risk:
        blockers.append(
            "allocation_policy_max_next_trade_risk_pct_must_not_exceed_bucket_limit"
        )
    if not _bool(policy.get("no_live_allocation")):
        blockers.append("allocation_policy_no_live_allocation_required")
    blockers.extend(_authority_blockers(policy, "allocation_policy"))
    return blockers


def _owner_confirmation_blockers(owner_confirmation: Mapping[str, Any]) -> list[str]:
    if not owner_confirmation:
        return ["missing_owner_bucket_confirmation"]

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
    post_trade: Mapping[str, Any],
    bucket: Mapping[str, Any],
    policy: Mapping[str, Any],
    owner_confirmation: Mapping[str, Any],
) -> dict[str, Any]:
    outcome = _outcome_classification(post_trade)
    update = _bucket_update(status, outcome, post_trade, bucket)
    cycle = _cycle_progress(status, update, bucket)
    decision = _next_allocation_decision(status, outcome, cycle)
    recommendation = _recommendation(status, decision, outcome, policy)
    return {
        "packet_id": PACKET_ID,
        "bucket_update_version": BUCKET_UPDATE_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "post_trade_summary": _post_trade_summary(post_trade),
        "bucket_state_summary": _bucket_state_summary(bucket),
        "allocation_policy_summary": _allocation_policy_summary(policy),
        "owner_confirmation_summary": _owner_confirmation_summary(owner_confirmation),
        "bucket_update": update,
        "cycle_progress": cycle,
        "next_allocation_decision": decision,
        "recommendation": recommendation,
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status, decision),
    }


def _post_trade_summary(post_trade: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "status": _text(post_trade.get("status"), "MISSING"),
        "post_trade_classification": _text(
            post_trade.get("post_trade_classification"), "MISSING"
        ),
        "normalized_evidence_present": bool(
            _mapping(post_trade.get("normalized_evidence_package"))
        ),
        "execution_authority_false": not _authority_blockers(
            post_trade, "post_trade_capture_result"
        ),
        "sensitive_key_terms_detected": _forbidden_key_terms(post_trade),
    }


def _bucket_state_summary(bucket: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "bucket_currency": _text(bucket.get("bucket_currency"), "MISSING"),
        "starting_bucket_balance": _number(bucket.get("starting_bucket_balance"), 0),
        "current_bucket_balance": _number(bucket.get("current_bucket_balance"), 0),
        "total_realized_pl": _number(bucket.get("total_realized_pl"), 0),
        "current_cycle_start_balance": _number(
            bucket.get("current_cycle_start_balance"), 0
        ),
        "current_cycle_realized_pl": _number(
            bucket.get("current_cycle_realized_pl"), 0
        ),
        "cycle_profit_target_min_pct": _number(
            bucket.get("cycle_profit_target_min_pct"), 0
        ),
        "cycle_profit_target_max_pct": _number(
            bucket.get("cycle_profit_target_max_pct"), 0
        ),
        "max_single_trade_risk_pct": _number(
            bucket.get("max_single_trade_risk_pct"), 0
        ),
        "one_order_only": _bool(bucket.get("one_order_only")),
        "demo_only": _bool(bucket.get("demo_only")),
        "live_trading": _bool(bucket.get("live_trading")),
    }


def _allocation_policy_summary(policy: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "allocation_mode": _text(policy.get("allocation_mode"), "MISSING"),
        "compounding_enabled": policy.get("compounding_enabled")
        if isinstance(policy.get("compounding_enabled"), bool)
        else "MISSING",
        "collect_profit_at_target": policy.get("collect_profit_at_target")
        if isinstance(policy.get("collect_profit_at_target"), bool)
        else "MISSING",
        "require_more_evidence_after_loss": policy.get(
            "require_more_evidence_after_loss"
        )
        if isinstance(policy.get("require_more_evidence_after_loss"), bool)
        else "MISSING",
        "require_owner_approval_for_next_trade": _bool(
            policy.get("require_owner_approval_for_next_trade")
        ),
        "max_next_trade_risk_pct": _number(
            policy.get("max_next_trade_risk_pct"), 0
        ),
        "no_live_allocation": _bool(policy.get("no_live_allocation")),
    }


def _owner_confirmation_summary(
    owner_confirmation: Mapping[str, Any],
) -> dict[str, bool]:
    return {
        field: _bool(owner_confirmation.get(field))
        for field in OWNER_CONFIRMATION_REQUIRED_TRUE_FIELDS
    }


def _bucket_update(
    status: str,
    outcome: str,
    post_trade: Mapping[str, Any],
    bucket: Mapping[str, Any],
) -> dict[str, Any]:
    ready = status == BUCKET_UPDATE_READY
    current_balance = _number(bucket.get("current_bucket_balance"), 0)
    total_realized = _number(bucket.get("total_realized_pl"), 0)
    realized_pl = _realized_pl(post_trade) if ready else 0
    applied_pl = _applied_realized_pl(outcome, realized_pl) if ready else 0
    return {
        "ready": ready,
        "outcome_classification": outcome,
        "bucket_currency": _text(bucket.get("bucket_currency"), "USD"),
        "previous_bucket_balance": current_balance,
        "applied_realized_pl": applied_pl,
        "new_bucket_balance": current_balance + applied_pl,
        "previous_total_realized_pl": total_realized,
        "new_total_realized_pl": total_realized + applied_pl,
        "balance_changed": applied_pl != 0,
        "demo_only": True,
        "live_allocation_allowed": False,
    }


def _cycle_progress(
    status: str,
    update: Mapping[str, Any],
    bucket: Mapping[str, Any],
) -> dict[str, Any]:
    ready = status == BUCKET_UPDATE_READY
    cycle_start = _number(bucket.get("current_cycle_start_balance"), 0)
    previous_cycle_pl = _number(bucket.get("current_cycle_realized_pl"), 0)
    applied_pl = _number(update.get("applied_realized_pl"), 0) if ready else 0
    new_cycle_pl = previous_cycle_pl + applied_pl
    cycle_return_pct = (new_cycle_pl / cycle_start * 100) if cycle_start > 0 else 0
    min_target = _number(bucket.get("cycle_profit_target_min_pct"), 0)
    max_target = _number(bucket.get("cycle_profit_target_max_pct"), 0)
    return {
        "ready": ready,
        "current_cycle_start_balance": cycle_start,
        "previous_cycle_realized_pl": previous_cycle_pl,
        "new_cycle_realized_pl": new_cycle_pl,
        "cycle_return_pct": cycle_return_pct,
        "cycle_profit_target_min_pct": min_target,
        "cycle_profit_target_max_pct": max_target,
        "target_band_min_hit": cycle_return_pct >= min_target if ready else False,
        "target_band_max_hit": cycle_return_pct >= max_target if ready else False,
    }


def _next_allocation_decision(
    status: str,
    outcome: str,
    cycle: Mapping[str, Any],
) -> dict[str, Any]:
    if status != BUCKET_UPDATE_READY:
        action = "blocked_until_inputs_are_ready"
    elif outcome == "DRY_RUN":
        action = "continue_demo_rehearsal"
    elif outcome == "REJECTED":
        action = "repair_order_or_context_before_retry"
    elif outcome == "OPEN":
        action = "wait_for_post_trade_close_evidence"
    elif outcome == "PROFIT" and _bool(cycle.get("target_band_min_hit")):
        action = "collect_profit_and_pause_for_owner_review"
    elif outcome == "PROFIT":
        action = "continue_demo_with_same_or_lower_risk"
    elif outcome == "LOSS":
        action = "reduce_risk_and_require_more_evidence"
    elif outcome == "BREAKEVEN":
        action = "continue_demo_with_no_size_increase"
    else:
        action = "stop_and_review_result_bucket_state"
    return {
        "ready": status == BUCKET_UPDATE_READY,
        "action": action,
        "next_trade_requires_owner_approval": True,
        "live_allocation_allowed": False,
        "autonomous_compounding_allowed": False,
    }


def _recommendation(
    status: str,
    decision: Mapping[str, Any],
    outcome: str,
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    action = _text(decision.get("action"), "blocked_until_inputs_are_ready")
    return {
        "ready": status == BUCKET_UPDATE_READY,
        "action": action,
        "rationale": _rationale(action, outcome),
        "next_trade_requires_owner_approval": True,
        "live_allocation_allowed": False,
        "autonomous_compounding_allowed": False,
        "max_next_trade_risk_pct": _number(policy.get("max_next_trade_risk_pct"), 0),
    }


def _outcome_classification(post_trade: Mapping[str, Any]) -> str:
    classification = post_trade.get("post_trade_classification")
    return {
        "DRY_RUN_ONLY": "DRY_RUN",
        "NO_FILL_REJECTED": "REJECTED",
        "OPEN_OR_PENDING": "OPEN",
        "OPEN_POSITION": "OPEN",
        "PROFIT": "PROFIT",
        "LOSS": "LOSS",
        "BREAKEVEN": "BREAKEVEN",
    }.get(classification, "UNKNOWN")


def _realized_pl(post_trade: Mapping[str, Any]) -> float:
    evidence = _mapping(post_trade.get("normalized_evidence_package"))
    return _number(evidence.get("realized_pl_when_closed"), 0)


def _applied_realized_pl(outcome: str, realized_pl: float) -> float:
    if outcome == "PROFIT":
        return realized_pl if realized_pl > 0 else 0
    if outcome == "LOSS":
        return realized_pl if realized_pl < 0 else -abs(realized_pl)
    return 0


def _rationale(action: str, outcome: str) -> str:
    return {
        "continue_demo_rehearsal": "dry_run_result_does_not_change_bucket",
        "repair_order_or_context_before_retry": "order_did_not_fill_or_was_rejected",
        "wait_for_post_trade_close_evidence": "position_or_order_still_open",
        "continue_demo_with_same_or_lower_risk": "profit_recorded_but_cycle_target_not_hit",
        "collect_profit_and_pause_for_owner_review": "cycle_profit_target_hit",
        "reduce_risk_and_require_more_evidence": "loss_recorded",
        "continue_demo_with_no_size_increase": "breakeven_recorded",
    }.get(action, f"outcome_{outcome.lower()}_requires_review")


def _unsafe_blockers(post_trade: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    blockers.extend(_authority_blockers(post_trade, "post_trade_capture_result"))
    for term in _forbidden_key_terms(post_trade):
        blockers.append(f"post_trade_capture_forbidden_{term}_field")
    return blockers


def _forbidden_key_terms(value: Any) -> list[str]:
    found: list[str] = []

    def visit(node: Any) -> None:
        if isinstance(node, Mapping):
            for key, child in node.items():
                key_text = str(key).lower()
                if key_text in SAFE_SENSITIVE_STATUS_KEYS:
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


def _authority_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []
    authority = _mapping(payload.get("execution_authority"))
    for field in EXECUTION_AUTHORITY_FIELDS:
        if _bool(payload.get(field)) or _bool(authority.get(field)):
            blockers.append(f"unsafe_{label}_{field}_true")
    return blockers


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _warnings(status: str) -> list[str]:
    warnings = [
        "result_accounting_only",
        "execution_authority_false",
        "no_oanda_call_performed",
        "no_broker_call_performed",
        "no_order_placement_performed",
        "no_credentials_or_account_ids_read_or_persisted",
        "next_trade_requires_owner_approval",
    ]
    if status == BUCKET_UPDATE_READY:
        warnings.append("demo_bucket_update_ready_for_owner_review")
    return warnings


def _next_safe_action(status: str, decision: Mapping[str, Any]) -> str:
    if status == BUCKET_UPDATE_READY:
        return _text(decision.get("action"), "review_bucket_update")
    return {
        BUCKET_BLOCKED_MISSING_POST_TRADE_CAPTURE: "provide_post_trade_capture_result",
        BUCKET_BLOCKED_POST_TRADE_NOT_READY: (
            "repair_post_trade_capture_before_bucket_update"
        ),
        BUCKET_BLOCKED_MISSING_BUCKET_STATE: "provide_valid_demo_bucket_state",
        BUCKET_BLOCKED_ALLOCATION_POLICY: "provide_valid_allocation_policy",
        BUCKET_BLOCKED_OWNER_CONFIRMATION: (
            "complete_owner_bucket_confirmation_before_update"
        ),
        BUCKET_REJECTED: "remove_sensitive_or_unsafe_bucket_inputs",
    }.get(status, "stop_and_review_result_to_bucket_state")


def _bool(value: Any) -> bool:
    return value is True


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _number(value: Any, default: float) -> float:
    return value if _is_number(value) else default


def _number_at_least(value: Any, floor: float) -> bool:
    return _is_number(value) and value >= floor


def _number_greater_than(value: Any, floor: float) -> bool:
    return _is_number(value) and value > floor


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
