from __future__ import annotations

import argparse
import json
from typing import Any


SCHEMA = "AIOS_SOS_WAKE_POLICY.v1"

CRITICAL_KEYS = {
    "broker",
    "broker_order",
    "live_trading",
    "live_execution",
    "credentials",
    "credential_use",
    "real_orders",
    "real_order",
    "real_webhooks",
    "webhook_url",
}

PROTECTED_ATTEMPT_KEYS = {
    "git_add_attempted",
    "git_commit_attempted",
    "git_push_attempted",
    "merge_attempted",
    "scheduler_activation_requested",
    "daemon_activation_requested",
    "worker_dispatch_requested",
    "queue_mutation_requested",
    "approval_mutation_requested",
    "destructive_cleanup_requested",
}


def _items(value: Any, path: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], str, Any]]:
    output: list[tuple[tuple[str, ...], str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            key_text = str(key)
            output.append((path, key_text, child))
            output.extend(_items(child, (*path, key_text)))
    elif isinstance(value, list):
        for child in value:
            output.extend(_items(child, path))
    return output


def _trigger_flags(status: dict[str, Any]) -> list[str]:
    triggers: set[str] = set()
    for path, raw_key, value in _items(status):
        key = raw_key.lower()
        path_lower = {part.lower() for part in path}
        if "approval_required" in path_lower or "protected_actions_blocked" in path_lower:
            continue
        if value is not True:
            continue
        if key in CRITICAL_KEYS:
            triggers.add("broker_live_credential_or_real_order_trigger")
        if key in PROTECTED_ATTEMPT_KEYS:
            triggers.add("protected_action_attempt")
    return sorted(triggers)


def evaluate_sos_wake_policy(status: dict[str, Any] | None) -> dict[str, Any]:
    payload = status if isinstance(status, dict) else {}
    text = json.dumps(payload, sort_keys=True).lower()
    triggers = set(_trigger_flags(payload))

    if "createprocessasuserw failed: 1312" in text:
        triggers.add("sandbox_1312_blocker")
    repeated_failures = int(payload.get("validator_failures", payload.get("repeated_validator_failures", 0)) or 0)
    if repeated_failures >= 2:
        triggers.add("repeated_validator_failures")
    if str(payload.get("result", "")).upper() == "REVIEW_REQUIRED" and triggers == set():
        triggers = set()

    critical_triggers = {
        "broker_live_credential_or_real_order_trigger",
        "protected_action_attempt",
        "repeated_validator_failures",
    }
    sos_required = bool(triggers.intersection(critical_triggers))
    wake_anthony = sos_required
    severity = "critical" if sos_required else "medium" if "sandbox_1312_blocker" in triggers else "none"
    return {
        "schema": SCHEMA,
        "sos_required": sos_required,
        "wake_anthony": wake_anthony,
        "severity": severity,
        "triggers": sorted(triggers),
        "reason_code": "sos_required" if sos_required else "sandbox_blocker" if triggers else "no_sos",
        "next_safe_action": (
            "Wake Anthony and stop AIOS self-build work."
            if sos_required
            else "Treat sandbox 1312 as a runner blocker, not a code failure."
            if "sandbox_1312_blocker" in triggers
            else "Continue normal bounded review."
        ),
        "safety": {
            "broker": "broker_live_credential_or_real_order_trigger" in triggers,
            "live_trading": "broker_live_credential_or_real_order_trigger" in triggers,
            "credentials": "broker_live_credential_or_real_order_trigger" in triggers,
            "real_orders": "broker_live_credential_or_real_order_trigger" in triggers,
            "real_webhooks": "broker_live_credential_or_real_order_trigger" in triggers,
            "protected_action_attempt": "protected_action_attempt" in triggers,
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Preview AIOS SOS wake policy.")
    parser.add_argument("--status", default="{}")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    status = json.loads(args.status)
    print(json.dumps(evaluate_sos_wake_policy(status), indent=2, sort_keys=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
