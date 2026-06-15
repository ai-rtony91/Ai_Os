from __future__ import annotations

import argparse
import json
import re
from typing import Any


SCHEMA = "AIOS_SELF_BUILD_CORE_STATUS_READER.v1"
SANDBOX_1312_MARKER = "createprocessasuserw failed: 1312"

PROTECTED_ACTIONS_BLOCKED = {
    "git_add": True,
    "git_commit": True,
    "git_push": True,
    "merge": True,
    "scheduler_activation": True,
    "daemon_activation": True,
    "worker_dispatch": True,
    "queue_mutation": True,
    "approval_mutation": True,
    "broker_live_trading": True,
    "credentials": True,
    "real_orders": True,
    "real_webhooks": True,
    "destructive_cleanup": True,
}

PROTECTED_ATTEMPT_KEYS = {
    "git_add_attempted": "git_add",
    "git_commit_attempted": "git_commit",
    "git_push_attempted": "git_push",
    "merge_attempted": "merge",
    "scheduler_activation_requested": "scheduler",
    "daemon_activation_requested": "daemon",
    "worker_dispatch_requested": "worker_dispatch",
    "queue_mutation_requested": "queue_mutation",
    "approval_mutation_requested": "approval_mutation",
    "destructive_cleanup_requested": "destructive_action",
}

SAFETY_ALIASES = {
    "broker": "broker",
    "broker_order": "broker",
    "broker_live_trading": "broker",
    "live_trading": "live_trading",
    "live_execution": "live_trading",
    "credentials": "credentials",
    "credential_use": "credentials",
    "real_orders": "real_orders",
    "real_order": "real_orders",
    "real_webhooks": "real_webhooks",
    "webhook_url": "real_webhooks",
    "scheduler": "scheduler",
    "scheduler_activation": "scheduler",
    "daemon": "daemon",
    "daemon_activation": "daemon",
    "worker_dispatch": "worker_dispatch",
    "queue_mutation": "queue_mutation",
    "approval_mutation": "approval_mutation",
    "git_add": "git_add",
    "git_commit": "git_commit",
    "git_push": "git_push",
    "merge": "merge",
    "destructive_action": "destructive_action",
    "destructive_cleanup": "destructive_action",
    "background_runtime": "background_runtime",
    "network": "network_access",
    "network_access": "network_access",
    "codex_launch": "codex_launch",
    "codex_launched": "codex_launch",
    "chatgpt_api_call": "chatgpt_api_call",
    "command_execution": "command_execution",
    "commands_executed": "command_execution",
    "generated_commands_executed": "command_execution",
    "local_apply_executed": "command_execution",
}

UNSAFE_SAFETY_KEYS = {
    "broker",
    "live_trading",
    "credentials",
    "real_orders",
    "real_webhooks",
    "scheduler",
    "daemon",
    "worker_dispatch",
    "queue_mutation",
    "approval_mutation",
    "git_add",
    "git_commit",
    "git_push",
    "merge",
    "destructive_action",
    "background_runtime",
    "network_access",
    "codex_launch",
    "chatgpt_api_call",
    "command_execution",
}


def _base_safety() -> dict[str, bool]:
    return {
        "reader_only": True,
        "files_written": False,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "real_webhooks": False,
        "scheduler": False,
        "daemon": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "git_add": False,
        "git_commit": False,
        "git_push": False,
        "merge": False,
        "destructive_action": False,
        "background_runtime": False,
        "network_access": False,
        "codex_launch": False,
        "chatgpt_api_call": False,
        "command_execution": False,
        "protected_action_attempt": False,
        "sandbox_1312_blocker": False,
    }


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _first_text(*values: Any, default: str = "unknown") -> str:
    for value in values:
        if isinstance(value, str) and value:
            return value
        if value not in (None, "") and not isinstance(value, (dict, list)):
            return str(value)
    return default


def _first_int(*values: Any, default: int = 0) -> int:
    for value in values:
        if isinstance(value, bool):
            continue
        if isinstance(value, int):
            return int(value)
        if isinstance(value, str) and value.strip().isdigit():
            return int(value.strip())
    return default


def _embedded(payload: dict[str, Any], *keys: str) -> dict[str, Any]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, dict):
            return value
    return {}


def _iter_items(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], str, Any]]:
    output: list[tuple[tuple[str, ...], str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            output.append((path, key_text, child))
            output.extend(_iter_items(child, (*path, key_text)))
    elif isinstance(value, list):
        for child in value:
            output.extend(_iter_items(child, path))
    return output


def _payload_text(*payloads: dict[str, Any]) -> str:
    return " ".join(json.dumps(payload, sort_keys=True).lower() for payload in payloads if payload)


def _sandbox_1312_present(*payloads: dict[str, Any]) -> bool:
    return SANDBOX_1312_MARKER in _payload_text(*payloads)


def _validator_pass_count(validators: list[Any]) -> int:
    count = 0
    for validator in validators:
        if not isinstance(validator, dict):
            continue
        stdout = str(validator.get("stdout", ""))
        match = re.search(r"(\d+)\s+passed", stdout)
        if match:
            count += int(match.group(1))
        elif validator.get("passed") is True:
            count += 1
    return count


def _tests_passed_count(
    wake: dict[str, Any],
    readiness: dict[str, Any],
    driver: dict[str, Any],
    stop_report: dict[str, Any],
) -> int:
    validators_summary = _as_dict(stop_report.get("validators_summary"))
    direct_count = _first_int(
        driver.get("tests_passed_count"),
        readiness.get("tests_passed_count"),
        stop_report.get("tests_passed_count"),
        validators_summary.get("tests_passed_count"),
        validators_summary.get("passed_count"),
        default=-1,
    )
    if direct_count >= 0:
        return direct_count
    return _validator_pass_count(_as_list(wake.get("validators_run")))


def _collect_safety(*payloads: dict[str, Any]) -> dict[str, bool]:
    safety = _base_safety()
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        for source_key in ("safety", "safety_summary"):
            source = payload.get(source_key)
            if not isinstance(source, dict):
                continue
            for key, value in source.items():
                alias = SAFETY_ALIASES.get(str(key).lower())
                if alias in safety:
                    safety[alias] = safety[alias] or bool(value)

        for path, raw_key, value in _iter_items(payload):
            path_lower = {part.lower() for part in path}
            if "approval_required" in path_lower or "protected_actions_blocked" in path_lower:
                continue
            if value is not True:
                continue
            key = raw_key.lower()
            if key in PROTECTED_ATTEMPT_KEYS:
                safety[PROTECTED_ATTEMPT_KEYS[key]] = True
                safety["protected_action_attempt"] = True
            alias = SAFETY_ALIASES.get(key)
            if alias in safety and alias != "files_written":
                safety[alias] = True

    if _sandbox_1312_present(*payloads):
        safety["sandbox_1312_blocker"] = True
    return safety


def _protected_flags_required(item: dict[str, Any]) -> bool:
    flags = item.get("protected_action_flags", {})
    if not isinstance(flags, dict):
        return False
    return any(bool(value) for value in flags.values())


def _bounded_dry_run_item(item: dict[str, Any]) -> bool:
    if not isinstance(item, dict) or not item:
        return False
    if str(item.get("status", "ready")) != "ready":
        return False
    mode = str(item.get("queue_item_mode", item.get("execution_mode", "DRY_RUN"))).upper()
    if mode != "DRY_RUN":
        return False
    allowed_paths = item.get("allowed_paths", [])
    if not isinstance(allowed_paths, list) or not allowed_paths:
        return False
    return not _protected_flags_required(item)


def _local_apply_preview_ready(local_apply_preview: dict[str, Any]) -> bool:
    if not isinstance(local_apply_preview, dict) or not local_apply_preview:
        return False
    if local_apply_preview.get("commands_executed") is True:
        return False
    if str(local_apply_preview.get("runner_mode", "DRY_RUN")).upper() != "DRY_RUN":
        return False
    return bool(
        local_apply_preview.get("command_preview")
        or str(local_apply_preview.get("runner_status", "")) == "preview_only"
    )


def _wake_validation_passed(wake: dict[str, Any], driver: dict[str, Any]) -> bool:
    if isinstance(driver.get("wake_validation_passed"), bool):
        return bool(driver["wake_validation_passed"])
    result = str(wake.get("result", "")).upper()
    if result in {"DONE_FOR_CURRENT_GOAL", "REVIEW_REQUIRED", "PASSED", "PREVIEW_ONLY"}:
        validators = _as_list(wake.get("validators_run"))
        return not any(validator.get("passed") is False for validator in validators if isinstance(validator, dict))
    return False


def _selected_queue_item(driver: dict[str, Any], selector: dict[str, Any]) -> dict[str, Any]:
    selected = driver.get("selected_queue_item")
    if isinstance(selected, dict) and selected:
        return selected
    selected = selector.get("selected_queue_item")
    return selected if isinstance(selected, dict) else {}


def _packet_ready(driver: dict[str, Any], packet_preview: dict[str, Any]) -> bool:
    packet = packet_preview if packet_preview else _as_dict(driver.get("codex_packet_preview"))
    return bool(packet.get("packet_ready") is True)


def _unsafe_safety_present(safety: dict[str, bool]) -> bool:
    return any(safety.get(key) is True for key in UNSAFE_SAFETY_KEYS)


def read_self_build_core_status(
    wake_continue: dict[str, Any] | None = None,
    self_build_loop_readiness: dict[str, Any] | None = None,
    self_build_dry_run_driver: dict[str, Any] | None = None,
    queue: dict[str, Any] | None = None,
    selector: dict[str, Any] | None = None,
    codex_packet_preview: dict[str, Any] | None = None,
    local_apply_preview: dict[str, Any] | None = None,
    stop_report: dict[str, Any] | None = None,
    sos: dict[str, Any] | None = None,
) -> dict[str, Any]:
    wake = _as_dict(wake_continue)
    driver = _as_dict(self_build_dry_run_driver)
    if wake.get("schema") == "AIOS_SELF_BUILD_DRY_RUN_DRIVER.v1" and not driver:
        driver = wake
        wake = _embedded(driver, "wake_continue", "wake_report")

    if not driver:
        driver = _embedded(wake, "self_build_dry_run_driver", "dry_run_driver")

    readiness = _as_dict(self_build_loop_readiness) or _embedded(
        driver,
        "self_build_loop_readiness",
        "readiness",
    ) or _embedded(wake, "self_build_loop_readiness")
    queue_payload = _as_dict(queue) or _embedded(driver, "queue", "self_build_work_queue")
    selector_payload = _as_dict(selector) or _embedded(driver, "selector", "next_action_selector")
    packet_preview = _as_dict(codex_packet_preview) or _embedded(
        driver,
        "codex_packet_preview",
        "packet_preview",
    )
    local_preview = _as_dict(local_apply_preview) or _embedded(driver, "local_apply_preview")
    stop_payload = _as_dict(stop_report) or _embedded(driver, "stop_report", "stop_report_resume")
    sos_payload = _as_dict(sos) or _embedded(driver, "sos", "sos_wake_policy") or _embedded(
        wake,
        "sos",
        "sos_escalation",
    )

    item = _selected_queue_item(driver, selector_payload)
    safety = _collect_safety(
        wake,
        readiness,
        driver,
        queue_payload,
        selector_payload,
        packet_preview,
        local_preview,
        stop_payload,
        sos_payload,
        item,
    )
    protected_required = _protected_flags_required(item)
    if protected_required:
        safety["protected_action_attempt"] = True

    sandbox_1312 = bool(safety["sandbox_1312_blocker"])
    unsafe_safety = _unsafe_safety_present(safety) or protected_required
    sos_required = bool(sos_payload.get("sos_required") is True or safety["protected_action_attempt"] or unsafe_safety)
    wake_anthony = bool(sos_payload.get("wake_anthony") is True or safety["protected_action_attempt"] or unsafe_safety)

    readiness_status = _first_text(
        readiness.get("readiness_status"),
        driver.get("readiness_status"),
        default="unknown",
    )
    selected_next_action = _first_text(
        driver.get("selected_next_action"),
        selector_payload.get("selected_next_action"),
        readiness.get("next_allowed_self_build_action"),
        default="none",
    )
    packet_is_ready = _packet_ready(driver, packet_preview)
    local_ready = _local_apply_preview_ready(local_preview)
    bounded_item_selected = _bounded_dry_run_item(item)
    can_continue_preview = bool(
        bounded_item_selected
        and selected_next_action != "none"
        and not sos_required
        and not unsafe_safety
        and (packet_is_ready or local_ready or selector_payload.get("selector_status") == "selected")
    )

    stop_reason = _first_text(
        stop_payload.get("stop_reason"),
        driver.get("stop_reason"),
        selector_payload.get("reason_code"),
        sos_payload.get("reason_code"),
        default="none",
    )
    if sandbox_1312 and not sos_required:
        stop_reason = "sandbox_1312_blocker"
    elif safety["protected_action_attempt"]:
        stop_reason = "protected_action_attempt"
    elif readiness_status == "review_required" and stop_reason == "none":
        stop_reason = "review_required"

    if sos_required:
        next_safe_action = "Stop and wake Anthony before continuing self-build work."
    elif sandbox_1312:
        next_safe_action = "Treat sandbox 1312 as a local runner blocker, not a code failure."
    elif can_continue_preview:
        next_safe_action = "Continue preview only for the selected bounded DRY_RUN queue item."
    elif readiness_status == "review_required":
        next_safe_action = "Stop for Anthony self-build readiness review. This is not a code failure."
    else:
        next_safe_action = _first_text(
            selector_payload.get("next_safe_action"),
            driver.get("next_safe_action"),
            stop_payload.get("next_safe_action"),
            readiness.get("next_safe_action"),
            default="Stop until AIOS self-build status is reviewed.",
        )

    current_goal = _first_text(
        readiness.get("current_goal"),
        driver.get("goal"),
        driver.get("current_goal"),
        wake.get("goal"),
        queue_payload.get("goal"),
        item.get("goal"),
        default="unknown",
    )
    current_mode = _first_text(
        driver.get("current_mode"),
        readiness.get("current_mode"),
        queue_payload.get("mode"),
        item.get("mode"),
        default="unknown",
    )

    return {
        "schema": SCHEMA,
        "current_goal": current_goal,
        "current_mode": current_mode,
        "wake_validation_passed": _wake_validation_passed(wake, driver),
        "tests_passed_count": _tests_passed_count(wake, readiness, driver, stop_payload),
        "readiness_status": readiness_status,
        "selected_next_action": selected_next_action,
        "selected_queue_item": item or None,
        "packet_ready": packet_is_ready,
        "local_apply_preview_ready": local_ready,
        "stop_reason": stop_reason,
        "sos_required": sos_required,
        "wake_anthony": wake_anthony,
        "protected_actions_blocked": PROTECTED_ACTIONS_BLOCKED.copy(),
        "can_continue_preview": can_continue_preview,
        "can_apply_without_human": False,
        "next_safe_action": next_safe_action,
        "safety": safety,
    }


build_self_build_core_status = read_self_build_core_status
summarize_self_build_core_status = read_self_build_core_status


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Summarize AIOS self-build core status from JSON contracts.")
    parser.add_argument("--status", default="{}", help="Aggregate AIOS self-build status JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = json.loads(args.status)
    except json.JSONDecodeError:
        payload = {}
    print(json.dumps(read_self_build_core_status(payload), indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
