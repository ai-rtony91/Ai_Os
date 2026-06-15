"""Local-only AIOS SOS notifier planner.

This module converts SOS policy and status evidence into preview-only local
alert instructions. It never sends a notification, starts a process, writes a
file, calls PowerShell, accesses the network, or wakes an external service.
"""

from __future__ import annotations

from typing import Any, Iterable


SCHEMA = "AIOS_SOS_LOCAL_NOTIFIER.v1"

ALERT_LEVELS = {"none": 0, "info": 1, "warning": 2, "critical": 3}

SOS_BOOL_KEYS = {
    "sos_required",
    "sos_wake_required",
    "sos_anthony_required",
}
WAKE_BOOL_KEYS = {
    "wake_anthony",
    "wake_required",
    "anthony_required",
}
PROTECTED_ACTION_KEYS = {
    "protected_action_attempt",
    "protected_action_attempted",
    "protected_action_attempt_detected",
}
BROKER_LIVE_KEYS = {
    "broker_risk",
    "broker_live_trading_risk",
    "broker_or_live_trading",
    "live_trading_risk",
    "broker",
    "live_trading",
    "oanda",
}
CREDENTIAL_KEYS = {
    "credential_risk",
    "credentials_risk",
    "secrets_risk",
    "credential",
    "credentials",
    "secrets",
    "secrets_or_env_access",
}
REAL_ORDER_WEBHOOK_KEYS = {
    "real_order_risk",
    "real_orders_risk",
    "real_webhook_risk",
    "real_webhooks_risk",
    "real_order",
    "real_orders",
    "real_webhook",
    "real_webhooks",
}
DESTRUCTIVE_KEYS = {
    "destructive_action_risk",
    "destructive_action",
    "destructive_action_attempt",
    "forbidden_write_attempt",
}
VALIDATOR_REPAIR_KEYS = {
    "validator_failure_after_repair_budget",
    "validation_failure_after_repair_budget",
    "repair_budget_exhausted",
}
STUCK_LOOP_KEYS = {
    "stuck_loop",
    "no_progress",
    "repeated_failure",
    "repeated_failures",
}

EXTERNAL_CHANNELS = {
    "api",
    "discord",
    "email",
    "http",
    "https",
    "sms",
    "slack",
    "telegram",
    "webhook",
}
REAL_EXECUTION_KEYS = {
    "execute_real_notification",
    "execute_real_notifications",
    "live_delivery",
    "show_notification",
    "show_toast",
    "play_sound",
    "beep",
    "run_powershell",
    "powershell_notification",
    "write_report",
    "write_reports",
    "network_access",
    "send_email",
    "send_sms",
    "send_discord",
    "send_telegram",
    "send_slack",
    "send_webhook",
    "call_api",
    "wake_external_service",
    "wake_external_services",
}


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _safe_str(value: Any) -> str:
    return str(value or "").strip()


def _normalize_key(value: Any) -> str:
    return _safe_str(value).lower().replace("-", "_")


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    text = _safe_str(value).lower()
    if text in {"true", "1", "yes", "y", "on"}:
        return True
    if text in {"false", "0", "no", "n", "off", "none", "null", ""}:
        return False
    return False


def _iter_dicts(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from _iter_dicts(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_dicts(item)


def _iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from _iter_strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_strings(item)


def _truthy_key_any(value: Any, keys: set[str]) -> bool:
    normalized = {_normalize_key(key) for key in keys}
    for item in _iter_dicts(value):
        for key, raw in item.items():
            if _normalize_key(key) in normalized and _bool(raw):
                return True
    return False


def _string_any(value: Any, needles: set[str]) -> bool:
    normalized = {_safe_str(needle).lower() for needle in needles}
    for item in _iter_strings(value):
        text = item.lower()
        if any(needle in text for needle in normalized):
            return True
    return False


def _severity_from_inputs(*values: Any) -> str:
    level = "none"
    severity_keys = {"severity", "alert_level", "status", "escalation_status", "wake_class"}
    critical_terms = {"critical", "sos", "blocked", "sos_hard_stop", "sos_escalation"}
    warning_terms = {"warning", "needs_approval", "review_required", "degraded"}
    info_terms = {"info", "ready", "routine_review"}

    for value in values:
        for item in _iter_dicts(value):
            for key, raw in item.items():
                if _normalize_key(key) not in severity_keys:
                    continue
                text = _safe_str(raw).lower()
                if any(term in text for term in critical_terms):
                    level = _max_level(level, "critical")
                elif any(term in text for term in warning_terms):
                    level = _max_level(level, "warning")
                elif any(term in text for term in info_terms):
                    level = _max_level(level, "info")
    return level


def _max_level(current: str, candidate: str) -> str:
    return candidate if ALERT_LEVELS[candidate] > ALERT_LEVELS[current] else current


def _safe_next_action(*values: Any) -> str:
    for value in values:
        for item in _iter_dicts(value):
            for key in ("next_safe_action", "safe_next_action", "recommended_action"):
                text = _safe_str(item.get(key))
                if text:
                    return text
    return "Review the local SOS preview before any further mutation or protected action."


def _notification_requests(options: dict[str, Any]) -> tuple[bool, bool, list[str]]:
    external_requested = _truthy_key_any(
        options,
        {
            "external_notifications",
            "external_notifications_requested",
            "request_external_notifications",
        },
    ) or _string_any(options.get("channels", []), EXTERNAL_CHANNELS)

    real_execution_requested = _truthy_key_any(options, REAL_EXECUTION_KEYS)
    rejection_reasons: list[str] = []

    if external_requested:
        rejection_reasons.append("external_notifications_blocked_in_v1")
    if real_execution_requested:
        rejection_reasons.append("real_notification_execution_blocked_in_v1")
    if _truthy_key_any(options, {"write_report", "write_reports"}):
        rejection_reasons.append("report_writes_blocked_in_v1")
    if _truthy_key_any(options, {"network_access", "call_api", "send_webhook"}):
        rejection_reasons.append("network_access_blocked_in_v1")
    if _truthy_key_any(options, {"run_powershell", "powershell_notification"}):
        rejection_reasons.append("powershell_notification_blocked_in_v1")

    return external_requested, bool(external_requested or real_execution_requested), rejection_reasons


def _collect_triggers(
    sos_policy: dict[str, Any],
    stop_report: dict[str, Any],
    core_status: dict[str, Any],
) -> tuple[list[dict[str, str]], str, dict[str, bool]]:
    inputs = (sos_policy, stop_report, core_status)
    triggers: list[dict[str, str]] = []
    detected_risks = {
        "protected_action_attempt": False,
        "broker_live_trading": False,
        "credentials": False,
        "real_orders_or_webhooks": False,
        "destructive_action": False,
        "validator_failure_after_repair_budget": False,
        "stuck_loop_or_repeated_failure": False,
    }

    def add(trigger_id: str, reason: str, level: str) -> None:
        if trigger_id not in {item["id"] for item in triggers}:
            triggers.append({"id": trigger_id, "reason": reason, "level": level})

    if _truthy_key_any(sos_policy, SOS_BOOL_KEYS) or _string_any(
        sos_policy.get("escalation_status"), {"sos_escalation"}
    ):
        add("sos_required", "SOS policy requires escalation.", "warning")

    if _truthy_key_any(sos_policy, WAKE_BOOL_KEYS):
        add("wake_anthony", "SOS policy requests Anthony wake/review.", "warning")

    if _string_any(sos_policy.get("matched_sos_categories", []), {"sos", "blocked"}):
        add("matched_sos_category", "SOS policy matched one or more SOS categories.", "warning")

    severity = _severity_from_inputs(*inputs)
    if severity == "critical":
        add("severity_critical", "Critical severity was reported.", "critical")
    elif severity == "warning":
        add("severity_warning", "Warning severity was reported.", "warning")

    if any(_truthy_key_any(value, PROTECTED_ACTION_KEYS) for value in inputs):
        detected_risks["protected_action_attempt"] = True
        add("protected_action_attempt", "Protected action attempt detected.", "warning")

    if any(_truthy_key_any(value, BROKER_LIVE_KEYS) for value in inputs) or _string_any(
        sos_policy.get("matched_sos_categories", []), {"money_trading_broker"}
    ):
        detected_risks["broker_live_trading"] = True
        add("broker_live_trading_risk", "Broker or live-trading risk detected.", "critical")

    if any(_truthy_key_any(value, CREDENTIAL_KEYS) for value in inputs) or _string_any(
        sos_policy.get("matched_sos_categories", []), {"secrets_and_credentials"}
    ):
        detected_risks["credentials"] = True
        add("credentials_risk", "Credential, secret, or API-key risk detected.", "critical")

    if any(_truthy_key_any(value, REAL_ORDER_WEBHOOK_KEYS) for value in inputs):
        detected_risks["real_orders_or_webhooks"] = True
        add("real_orders_or_webhooks_risk", "Real order or real webhook risk detected.", "critical")

    if any(_truthy_key_any(value, DESTRUCTIVE_KEYS) for value in inputs) or _string_any(
        sos_policy.get("matched_sos_categories", []), {"destructive_repo_action"}
    ):
        detected_risks["destructive_action"] = True
        add("destructive_action_risk", "Destructive action risk detected.", "critical")

    if any(_truthy_key_any(value, VALIDATOR_REPAIR_KEYS) for value in inputs) or (
        any(_truthy_key_any(value, {"validator_failed", "validation_failed"}) for value in inputs)
        and any(_truthy_key_any(value, {"repair_budget_exhausted"}) for value in inputs)
    ):
        detected_risks["validator_failure_after_repair_budget"] = True
        add(
            "validator_failure_after_repair_budget",
            "Validator failure remains after repair budget.",
            "warning",
        )

    if any(_truthy_key_any(value, STUCK_LOOP_KEYS) for value in inputs):
        detected_risks["stuck_loop_or_repeated_failure"] = True
        add("stuck_loop_or_repeated_failure", "Stuck loop, no progress, or repeated failure detected.", "warning")

    alert_level = "none"
    for trigger in triggers:
        alert_level = _max_level(alert_level, trigger["level"])
    return triggers, alert_level, detected_risks


def _terminal_banner(alert_level: str, title: str, reason: str, next_safe_action: str) -> list[str]:
    return [
        "========================================",
        "AIOS SOS LOCAL ALERT PREVIEW",
        f"LEVEL: {alert_level.upper()}",
        f"TITLE: {title}",
        f"REASON: {reason}",
        f"NEXT: {next_safe_action}",
        "PREVIEW ONLY: no toast, sound, network, file write, or PowerShell command was executed.",
        "========================================",
    ]


def _beep_plan(alert_level: str, should_alert: bool) -> dict[str, Any]:
    pattern = "none"
    if should_alert and alert_level == "critical":
        pattern = "preview: three short beeps"
    elif should_alert:
        pattern = "preview: one short beep"
    return {
        "enabled": False,
        "would_beep": should_alert,
        "pattern": pattern,
        "execution": "blocked_in_v1_preview_only",
    }


def _safety(external_notifications_requested: bool) -> dict[str, Any]:
    return {
        "mode": "LOCAL_PREVIEW_ONLY",
        "local_only": True,
        "preview_only": True,
        "real_toast_executed": False,
        "sound_played": False,
        "powershell_notification_executed": False,
        "reports_written": False,
        "files_written": False,
        "commands_executed": False,
        "network_access_requested": False,
        "network_access_used": False,
        "external_services_woken": False,
        "external_notifications_blocked": external_notifications_requested,
        "broker": False,
        "credentials": False,
        "live_trading": False,
        "real_orders": False,
        "real_webhooks": False,
        "scheduler_activation": False,
        "daemon_activation": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "destructive_cleanup": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
    }


def build_sos_local_notifier_plan(
    *,
    sos_policy: dict[str, Any] | None = None,
    stop_report: dict[str, Any] | None = None,
    core_status: dict[str, Any] | None = None,
    notifier_options: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a preview-only local alert plan from SOS policy evidence."""

    policy = _as_dict(sos_policy)
    stop = _as_dict(stop_report)
    core = _as_dict(core_status)
    options = _as_dict(notifier_options)

    triggers, alert_level, detected_risks = _collect_triggers(policy, stop, core)
    should_alert = bool(triggers)
    notifier_status = "alert_ready" if should_alert else "no_alert"
    external_requested, blocked_request_present, rejection_reasons = _notification_requests(options)

    if not should_alert:
        alert_level = "none"
        alert_reason = "No SOS policy, wake request, severity, or safety trigger requires a local alert."
        alert_title = "AIOS SOS Local Alert Preview"
        alert_message = "No local SOS alert is needed."
        terminal_banner_preview: list[str] = []
    else:
        alert_reason = "; ".join(trigger["reason"] for trigger in triggers)
        if blocked_request_present:
            alert_reason = f"{alert_reason} External or real notification request was blocked by v1."
        alert_title = f"AIOS SOS Local Alert - {alert_level.upper()}"
        alert_message = f"{alert_reason} Next safe action: {_safe_next_action(policy, stop, core)}"
        terminal_banner_preview = _terminal_banner(
            alert_level,
            alert_title,
            alert_reason,
            _safe_next_action(policy, stop, core),
        )

    repeat_requested = _truthy_key_any(options, {"repeat", "repeat_alert", "repeat_until_acknowledged"})

    return {
        "schema": SCHEMA,
        "notifier_status": notifier_status,
        "alert_level": alert_level,
        "should_alert": should_alert,
        "alert_reason": alert_reason,
        "alert_title": alert_title,
        "alert_message": alert_message,
        "windows_toast_preview": {
            "enabled": False,
            "would_show": should_alert,
            "title": alert_title,
            "message": alert_message,
            "execution": "blocked_in_v1_preview_only",
            "command": None,
        },
        "terminal_banner_preview": terminal_banner_preview,
        "beep_plan_preview": _beep_plan(alert_level, should_alert),
        "repeat_policy": {
            "mode": "preview_only_no_runtime_repeat",
            "repeat_requested": repeat_requested,
            "repeat_allowed": False,
            "repeat_blocked": repeat_requested,
        },
        "external_notifications_requested": external_requested,
        "external_notifications_blocked": external_requested,
        "files_written": [],
        "commands_executed": [],
        "rejection_reasons": rejection_reasons,
        "next_safe_action": (
            _safe_next_action(policy, stop, core)
            if should_alert
            else "Continue governed routine flow; no local SOS alert preview is required."
        ),
        "detected_triggers": triggers,
        "detected_risks": detected_risks,
        "safety": _safety(external_requested),
    }
