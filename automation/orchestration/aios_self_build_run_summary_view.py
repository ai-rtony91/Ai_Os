from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_SELF_BUILD_RUN_SUMMARY_VIEW.v1"
SANDBOX_1312_MARKER = "createprocessasuserw failed: 1312"

PROTECTED_ACTIONS = [
    "git_add",
    "git_commit",
    "git_push",
    "merge",
    "scheduler_activation",
    "daemon_activation",
    "worker_dispatch",
    "queue_mutation",
    "approval_mutation",
    "broker_live_trading",
    "credentials",
    "real_orders",
    "real_webhooks",
    "destructive_cleanup",
]

SAFETY_KEYS = {
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


def _base_safety() -> dict[str, bool]:
    return {
        "view_only": True,
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


def _payload_text(payload: dict[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True).lower()


def _collect_safety(*payloads: dict[str, Any]) -> dict[str, bool]:
    safety = _base_safety()
    for payload in payloads:
        if not isinstance(payload, dict):
            continue
        nested_safety = payload.get("safety")
        if isinstance(nested_safety, dict):
            for key, value in nested_safety.items():
                alias = SAFETY_KEYS.get(str(key).lower())
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
            alias = SAFETY_KEYS.get(key)
            if alias in safety:
                safety[alias] = True
        if SANDBOX_1312_MARKER in _payload_text(payload):
            safety["sandbox_1312_blocker"] = True
    return safety


def _core_status(payload: dict[str, Any]) -> dict[str, Any]:
    if payload.get("schema") == "AIOS_SELF_BUILD_CORE_STATUS_READER.v1":
        return payload
    return _as_dict(payload.get("core_status"))


def _protected_actions_summary(core: dict[str, Any], safety: dict[str, bool]) -> dict[str, Any]:
    blocked_source = _as_dict(core.get("protected_actions_blocked"))
    blocked = {
        action: bool(blocked_source.get(action, True))
        for action in PROTECTED_ACTIONS
    }
    return {
        "all_protected_actions_blocked": all(blocked.values()),
        "blocked_actions": [action for action, is_blocked in blocked.items() if is_blocked],
        "unblocked_actions": [action for action, is_blocked in blocked.items() if not is_blocked],
        "protected_action_attempt": bool(safety.get("protected_action_attempt") is True),
    }


def _headline(
    *,
    can_continue_preview: bool,
    readiness_status: str,
    sos_required: bool,
    wake_anthony: bool,
    stop_reason: str,
) -> str:
    if sos_required or wake_anthony:
        return "AIOS self-build stopped: SOS review required"
    if stop_reason == "sandbox_1312_blocker":
        return "AIOS self-build blocked by local runner sandbox"
    if can_continue_preview:
        return "AIOS self-build preview ready"
    if readiness_status == "review_required":
        return "AIOS self-build review required"
    return "AIOS self-build status needs review"


def build_self_build_run_summary_view(status: dict[str, Any] | None) -> dict[str, Any]:
    payload = _as_dict(status)
    core = _core_status(payload)
    source = core or payload
    safety = _collect_safety(payload, core)

    current_goal = _first_text(source.get("current_goal"), payload.get("current_goal"), payload.get("goal"))
    selected_next_action = _first_text(
        source.get("selected_next_action"),
        payload.get("selected_next_action"),
        default="none",
    )
    readiness_status = _first_text(
        source.get("readiness_status"),
        payload.get("readiness_status"),
        default="unknown",
    )
    stop_reason = _first_text(source.get("stop_reason"), payload.get("stop_reason"), default="none")
    if safety["sandbox_1312_blocker"] and stop_reason == "none":
        stop_reason = "sandbox_1312_blocker"

    sos_required = bool(source.get("sos_required") is True or payload.get("sos_required") is True)
    wake_anthony = bool(source.get("wake_anthony") is True or payload.get("wake_anthony") is True)
    if safety["protected_action_attempt"]:
        sos_required = True
        wake_anthony = True

    can_continue_preview = bool(
        source.get("can_continue_preview") is True
        and not sos_required
        and not safety["protected_action_attempt"]
    )
    can_apply_without_human = False
    packet_ready = bool(source.get("packet_ready") is True or payload.get("packet_ready") is True)
    local_apply_preview_ready = bool(
        source.get("local_apply_preview_ready") is True
        or payload.get("local_apply_preview_ready") is True
    )
    next_safe_action = _first_text(
        source.get("next_safe_action"),
        payload.get("next_safe_action"),
        default="Review AIOS self-build DRY_RUN output before continuing.",
    )
    if safety["sandbox_1312_blocker"] and not sos_required:
        next_safe_action = "Treat sandbox 1312 as a local runner blocker, not a code failure."
    elif readiness_status == "review_required" and not sos_required:
        next_safe_action = "Stop for Anthony self-build readiness review. This is not a code failure."

    return {
        "schema": SCHEMA,
        "headline": _headline(
            can_continue_preview=can_continue_preview,
            readiness_status=readiness_status,
            sos_required=sos_required,
            wake_anthony=wake_anthony,
            stop_reason=stop_reason,
        ),
        "current_goal": current_goal,
        "selected_next_action": selected_next_action,
        "readiness_status": readiness_status,
        "tests_passed_count": _first_int(source.get("tests_passed_count"), payload.get("tests_passed_count")),
        "packet_ready": packet_ready,
        "local_apply_preview_ready": local_apply_preview_ready,
        "can_continue_preview": can_continue_preview,
        "can_apply_without_human": can_apply_without_human,
        "sos_required": sos_required,
        "wake_anthony": wake_anthony,
        "stop_reason": stop_reason,
        "next_safe_action": next_safe_action,
        "protected_actions_summary": _protected_actions_summary(core, safety),
        "safety": safety,
    }


summarize_self_build_run = build_self_build_run_summary_view
render_self_build_run_summary_view = build_self_build_run_summary_view


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build a compact AIOS self-build run summary view.")
    parser.add_argument("--status", default="{}", help="Self-build driver or core status JSON.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = json.loads(args.status)
    except json.JSONDecodeError:
        payload = {}
    print(json.dumps(build_self_build_run_summary_view(payload), indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
