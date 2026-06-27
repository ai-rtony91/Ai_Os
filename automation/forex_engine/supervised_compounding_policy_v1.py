"""Supervised compounding policy V1 for AIOS Forex final closure review."""

from __future__ import annotations

from decimal import Decimal, InvalidOperation
import re
from typing import Any, Mapping


SUPERVISED_COMPOUNDING_POLICY_VERSION = "supervised_compounding_policy_v1"

SUPERVISED_COMPOUNDING_POLICY_REVIEW_READY = (
    "SUPERVISED_COMPOUNDING_POLICY_REVIEW_READY"
)
SUPERVISED_COMPOUNDING_POLICY_BLOCKED = "SUPERVISED_COMPOUNDING_POLICY_BLOCKED"
SUPERVISED_COMPOUNDING_POLICY_INCOMPLETE = "SUPERVISED_COMPOUNDING_POLICY_INCOMPLETE"

PERSISTENT_PROFITABILITY_READY_STATUS = "PERSISTENT_PROFITABILITY_READY"

PROTECTED_PERMISSION_FLAGS = {
    "broker_execution_allowed": False,
    "broker_connection_allowed": False,
    "broker_api_call_allowed": False,
    "live_trading_allowed": False,
    "order_submission_allowed": False,
    "credential_access_allowed": False,
    "account_access_allowed": False,
    "money_movement_allowed": False,
    "all_money_control_allowed": False,
    "bank_movement_allowed": False,
    "withdrawal_allowed": False,
    "deposit_allowed": False,
    "compounding_allowed": False,
    "compounding_execution_allowed": False,
    "autonomous_compounding_allowed": False,
    "scheduler_allowed": False,
    "daemon_allowed": False,
    "webhook_allowed": False,
    "dashboard_execution_authority": False,
    "owner_approval_created": False,
}

REQUIRED_POLICY_FIELDS = (
    "compounding_disabled_by_default",
    "owner_review_required",
    "owner_compounding_approval_present",
    "compounding_requested",
    "autonomous_compounding_requested",
    "all_money_control_requested",
    "kill_switch_ready",
    "daily_loss_cap_ready",
    "max_drawdown_cap_ready",
    "risk_per_trade_cap_ready",
    "profit_lock_threshold_ready",
    "drawdown_cooldown_ready",
    "broker_execution_blocked",
    "live_trading_blocked",
    "credential_access_blocked",
    "account_access_blocked",
    "money_movement_blocked",
    "autonomous_compounding_blocked",
    "scheduler_blocked",
    "daemon_blocked",
    "webhook_blocked",
    "sanitized",
)

REQUIRED_TRUE_POLICY_FIELDS = (
    "compounding_disabled_by_default",
    "owner_review_required",
    "kill_switch_ready",
    "daily_loss_cap_ready",
    "max_drawdown_cap_ready",
    "risk_per_trade_cap_ready",
    "profit_lock_threshold_ready",
    "drawdown_cooldown_ready",
    "broker_execution_blocked",
    "live_trading_blocked",
    "credential_access_blocked",
    "account_access_blocked",
    "money_movement_blocked",
    "autonomous_compounding_blocked",
    "scheduler_blocked",
    "daemon_blocked",
    "webhook_blocked",
    "sanitized",
)

UNSAFE_TRUE_FIELDS = (
    "broker_execution_allowed",
    "broker_connection_allowed",
    "broker_api_call_allowed",
    "live_trading_allowed",
    "order_submission_allowed",
    "credential_access_allowed",
    "account_access_allowed",
    "money_movement_allowed",
    "all_money_control_allowed",
    "bank_movement_allowed",
    "withdrawal_allowed",
    "deposit_allowed",
    "compounding_allowed",
    "compounding_execution_allowed",
    "autonomous_compounding_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "dashboard_execution_authority",
    "owner_approval_created",
    "execution_allowed",
    "trade_allowed",
    "broker_access_allowed",
    "real_money_allowed",
)

SECRET_OR_ACCOUNT_FIELD_FRAGMENTS = (
    "api_key",
    "access_token",
    "refresh_token",
    "authorization",
    "bearer",
    "password",
    "secret",
    "credential",
    "account_id",
    "accountid",
    "account_number",
    "account_reference",
    "broker_order_id",
    "raw_order_id",
    "raw_transaction_id",
    "raw_payload",
    "order_payload",
)


def build_sample_compounding_policy_input() -> dict[str, Any]:
    return {
        "compounding_disabled_by_default": True,
        "owner_review_required": True,
        "owner_compounding_approval_present": False,
        "compounding_requested": False,
        "autonomous_compounding_requested": False,
        "all_money_control_requested": False,
        "kill_switch_ready": True,
        "daily_loss_cap_ready": True,
        "max_drawdown_cap_ready": True,
        "risk_per_trade_cap_ready": True,
        "profit_lock_threshold_ready": True,
        "drawdown_cooldown_ready": True,
        "broker_execution_blocked": True,
        "live_trading_blocked": True,
        "credential_access_blocked": True,
        "account_access_blocked": True,
        "money_movement_blocked": True,
        "autonomous_compounding_blocked": True,
        "scheduler_blocked": True,
        "daemon_blocked": True,
        "webhook_blocked": True,
        "sanitized": True,
    }


def evaluate_supervised_compounding_policy(
    persistent_profitability_result: Mapping[str, Any] | None = None,
    policy_controls: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate a local review-only compounding policy gate."""

    if persistent_profitability_result is None or policy_controls is None:
        return _result(
            status=SUPERVISED_COMPOUNDING_POLICY_INCOMPLETE,
            blockers=[
                "persistent profitability result and compounding policy controls are required"
            ],
            missing_fields=list(REQUIRED_POLICY_FIELDS),
            next_safe_action="Provide profitability proof and supervised compounding controls.",
        )
    if not isinstance(persistent_profitability_result, Mapping):
        return _result(
            status=SUPERVISED_COMPOUNDING_POLICY_INCOMPLETE,
            blockers=["persistent profitability result must be a dictionary"],
            missing_fields=[],
            next_safe_action="Provide persistent profitability result as a dictionary.",
        )
    if not isinstance(policy_controls, Mapping):
        return _result(
            status=SUPERVISED_COMPOUNDING_POLICY_INCOMPLETE,
            blockers=["compounding policy controls must be a dictionary"],
            missing_fields=list(REQUIRED_POLICY_FIELDS),
            next_safe_action="Provide compounding policy controls as a dictionary.",
        )

    profitability = dict(persistent_profitability_result)
    controls = dict(policy_controls)
    missing = [name for name in REQUIRED_POLICY_FIELDS if name not in controls]
    blockers: list[str] = []
    blockers.extend(_unsafe_fragments(profitability, "persistent_profitability"))
    blockers.extend(_unsafe_fragments(controls, "compounding_policy"))

    if missing:
        return _result(
            status=SUPERVISED_COMPOUNDING_POLICY_INCOMPLETE,
            blockers=blockers + [f"missing policy field: {name}" for name in missing],
            missing_fields=missing,
            next_safe_action="Provide all supervised compounding policy fields.",
        )

    profitability_status = _status(profitability)
    if profitability_status != PERSISTENT_PROFITABILITY_READY_STATUS:
        blockers.append(
            "persistent profitability is not ready: "
            f"{profitability_status or 'missing'}"
        )
    blockers.extend(f"persistent profitability: {item}" for item in _blockers(profitability))

    for field_name in REQUIRED_TRUE_POLICY_FIELDS:
        if controls.get(field_name) is not True:
            blockers.append(f"{field_name} must be true")

    if _truthy(controls.get("compounding_requested")):
        blockers.append("compounding execution request is outside final closure review")
        if controls.get("owner_compounding_approval_present") is not True:
            blockers.append("compounding requested without owner approval")
    if _truthy(controls.get("autonomous_compounding_requested")):
        blockers.append("autonomous compounding request is blocked")
    if _truthy(controls.get("all_money_control_requested")):
        blockers.append("all-money control request is blocked")

    status = (
        SUPERVISED_COMPOUNDING_POLICY_BLOCKED
        if blockers
        else SUPERVISED_COMPOUNDING_POLICY_REVIEW_READY
    )
    next_safe_action = (
        "Continue to stop/pause/resume review; this policy authorizes no compounding."
        if status == SUPERVISED_COMPOUNDING_POLICY_REVIEW_READY
        else "Resolve supervised compounding blockers before final readiness review."
    )
    return _result(
        status=status,
        blockers=_dedupe(blockers),
        missing_fields=[],
        next_safe_action=next_safe_action,
    )


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return dict(result)


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    status = str(
        result.get(
            "supervised_compounding_policy_status",
            result.get("status", SUPERVISED_COMPOUNDING_POLICY_INCOMPLETE),
        )
    )
    if status == SUPERVISED_COMPOUNDING_POLICY_REVIEW_READY:
        return (
            "Supervised compounding policy is review-ready only. "
            "It creates no compounding, money, broker, or automation authority."
        )
    blockers = result.get("blockers") or ["supervised compounding policy incomplete"]
    return "Supervised compounding policy blocked: " + "; ".join(
        str(item) for item in blockers
    )


def _result(
    *,
    status: str,
    blockers: list[str],
    missing_fields: list[str],
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "engine_version": SUPERVISED_COMPOUNDING_POLICY_VERSION,
        "status": status,
        "supervised_compounding_policy_status": status,
        "review_only": True,
        "owner_review_required": True,
        "owner_approval_created": False,
        "compounding_review_ready": status == SUPERVISED_COMPOUNDING_POLICY_REVIEW_READY,
        "autonomous_compounding_ready": False,
        "compounding_execution_authorized": False,
        "blockers": list(blockers),
        "missing_fields": list(missing_fields),
        "policy_control_count": len(REQUIRED_POLICY_FIELDS),
        "next_safe_action": next_safe_action,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def _status(payload: Mapping[str, Any]) -> str:
    for key in ("status", "persistent_profitability_status"):
        value = payload.get(key)
        if value:
            return str(value)
    return ""


def _blockers(payload: Mapping[str, Any]) -> list[str]:
    raw = payload.get("blockers") or []
    if isinstance(raw, str):
        return [raw] if raw else []
    if isinstance(raw, (list, tuple, set)):
        return [str(item) for item in raw if str(item)]
    return [str(raw)] if raw else []


def _unsafe_fragments(value: Any, prefix: str) -> list[str]:
    fragments: list[str] = []
    _scan_payload(value, prefix, fragments)
    return fragments


def _scan_payload(value: Any, path: str, fragments: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            lowered = key_text.lower()
            if lowered in UNSAFE_TRUE_FIELDS:
                if _truthy(item):
                    fragments.append(f"{path}.{key_text} is unsafe true")
                continue
            if key_text not in REQUIRED_POLICY_FIELDS and any(
                fragment in lowered for fragment in SECRET_OR_ACCOUNT_FIELD_FRAGMENTS
            ):
                fragments.append(
                    f"{path}.{key_text} contains secret-like or account-like data"
                )
            _scan_payload(item, f"{path}.{key_text}", fragments)
    elif isinstance(value, (list, tuple, set)):
        for index, item in enumerate(value):
            _scan_payload(item, f"{path}[{index}]", fragments)
    elif isinstance(value, str):
        if _string_contains_secret_like_data(value):
            fragments.append(f"{path} contains secret-like or account-like text")


def _string_contains_secret_like_data(value: str) -> bool:
    joined = "|".join(re.escape(fragment) for fragment in SECRET_OR_ACCOUNT_FIELD_FRAGMENTS)
    return bool(
        re.search(
            rf"(?i)(?:^|[\s{{\[,'\"])(?:{joined})(?:[\s'\"])*[:=]",
            value,
        )
    )


def _decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError):
        return None


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    number = _decimal(value)
    return number is not None and number != 0


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


__all__ = [
    "SUPERVISED_COMPOUNDING_POLICY_BLOCKED",
    "SUPERVISED_COMPOUNDING_POLICY_INCOMPLETE",
    "SUPERVISED_COMPOUNDING_POLICY_REVIEW_READY",
    "SUPERVISED_COMPOUNDING_POLICY_VERSION",
    "build_sample_compounding_policy_input",
    "evaluate_supervised_compounding_policy",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
