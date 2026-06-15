from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_SOS_ESCALATION_POLICY.v1"

SAFETY_KEY_TRIGGERS = {
    "credentials": "secret_or_credential_flag",
    "credential": "secret_or_credential_flag",
    "broker": "broker_live_real_order_or_webhook_flag",
    "live_trading": "broker_live_real_order_or_webhook_flag",
    "real_orders": "broker_live_real_order_or_webhook_flag",
    "real_order": "broker_live_real_order_or_webhook_flag",
    "real_webhooks": "broker_live_real_order_or_webhook_flag",
    "real_webhook": "broker_live_real_order_or_webhook_flag",
    "scheduler": "scheduler_daemon_or_worker_dispatch_requested",
    "daemon": "scheduler_daemon_or_worker_dispatch_requested",
    "worker_dispatch": "scheduler_daemon_or_worker_dispatch_requested",
    "queue_mutation": "queue_or_approval_mutation_requested",
    "approval_mutation": "queue_or_approval_mutation_requested",
    "destructive_action": "destructive_action_requested",
    "delete_reset": "destructive_action_requested",
}


def base_safety() -> dict[str, bool]:
    return {
        "sos_required": False,
        "broker": False,
        "live_trading": False,
        "real_orders": False,
        "real_webhooks": False,
        "credentials": False,
        "scheduler": False,
        "daemon": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "destructive_action": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
    }


def _iter_items(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], str, Any]]:
    items: list[tuple[tuple[str, ...], str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            child_path = (*path, key_text)
            items.append((path, key_text, child))
            items.extend(_iter_items(child, child_path))
    elif isinstance(value, list):
        for child in value:
            items.extend(_iter_items(child, path))
    return items


def _status_text(status: dict[str, Any]) -> str:
    try:
        return json.dumps(status, sort_keys=True).lower()
    except TypeError:
        return str(status).lower()


def _sandbox_1312_with_passing_pytest(status: dict[str, Any], text: str) -> bool:
    if "createprocessasuserw failed: 1312" not in text and status.get("sandbox_blocked") is not True:
        return False
    passed = int(status.get("tests_passed_count", 0) or 0)
    failed = int(status.get("tests_failed_count", 0) or 0)
    return passed > 0 and failed == 0


def _is_normal_non_sos(status: dict[str, Any], text: str) -> bool:
    if _sandbox_1312_with_passing_pytest(status, text):
        return True
    if status.get("result") == "REVIEW_REQUIRED" or status.get("status") == "REVIEW_REQUIRED":
        return True
    if status.get("merge_block_reason") == "no_checks_reported":
        return True
    if "waiting for human pr merge approval" in text:
        return True
    return False


def _flag_triggers(status: dict[str, Any]) -> set[str]:
    triggers: set[str] = set()
    for path, raw_key, value in _iter_items(status):
        key = raw_key.lower()
        path_lower = {part.lower() for part in path}
        if "approval_required" in path_lower or value is not True:
            continue
        for trigger_key, trigger in SAFETY_KEY_TRIGGERS.items():
            if key == trigger_key or key.endswith(f"_{trigger_key}") or key.startswith(f"{trigger_key}_"):
                triggers.add(trigger)
    return triggers


def build_sos_escalation(status: dict[str, Any] | None) -> dict[str, Any]:
    payload = status if isinstance(status, dict) else {}
    text = _status_text(payload)
    triggers = _flag_triggers(payload)

    repair_attempts = int(payload.get("repair_attempts", 0) or 0)
    tests_failed = int(payload.get("tests_failed_count", 0) or 0)
    if (payload.get("result") in {"failed", "FAILED"} or tests_failed > 0) and repair_attempts > 0:
        triggers.add("tests_failed_after_repair")
    if "unknown_action" in text or "unsupported_action" in text:
        triggers.add("unknown_action")
    if "unsupported_mode" in text or "mode_not_enabled" in text:
        triggers.add("unsupported_mode")
    if "unbounded_path" in text or "outside_allowed" in text:
        triggers.add("unbounded_path")
    if "merge conflict" in text:
        triggers.add("git_merge_conflict")
    if "required check failed" in text or "validate fail" in text:
        triggers.add("github_required_check_failed")
    if "repeated ci failure" in text:
        triggers.add("repeated_ci_failure")
    if payload.get("command_execution_requested") is True and payload.get("command_execution_approved") is not True:
        triggers.add("command_execution_requested_without_approval")
    if payload.get("runtime_launch_requested") is True and payload.get("runtime_launch_approved") is not True:
        triggers.add("runtime_launch_requested_without_approval")

    if _is_normal_non_sos(payload, text):
        triggers.difference_update({"tests_failed_after_repair"})
        if not any(
            trigger
            for trigger in triggers
            if trigger
            not in {
                "github_required_check_failed",
                "repeated_ci_failure",
            }
        ):
            triggers = set()

    triggers_list = sorted(triggers)
    sos_required = bool(triggers_list)
    safety = base_safety()
    safety["sos_required"] = sos_required
    for key, trigger in SAFETY_KEY_TRIGGERS.items():
        if trigger in triggers_list and key in safety:
            safety[key] = True

    severity = "none"
    if sos_required:
        severity = "critical" if any("broker" in trigger or "credential" in trigger for trigger in triggers_list) else "high"

    return {
        "schema": SCHEMA,
        "sos_required": sos_required,
        "severity": severity,
        "triggers": triggers_list,
        "wake_anthony": sos_required,
        "stop_reason": ", ".join(triggers_list) if triggers_list else "none",
        "next_safe_action": (
            "Stop AIOS continuation and escalate to Anthony before any further build action."
            if sos_required
            else "Continue under the bounded control-plane path."
        ),
        "safety": safety,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview the AIOS SOS escalation policy.")
    parser.add_argument("--status", default="{}", help="JSON status object.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        status = json.loads(args.status)
    except json.JSONDecodeError:
        status = {"status_text": args.status}
    escalation = build_sos_escalation(status)
    print(json.dumps(escalation, indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
