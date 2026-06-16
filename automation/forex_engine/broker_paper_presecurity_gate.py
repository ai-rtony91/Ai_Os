from __future__ import annotations

from typing import Any

from automation.forex_engine import schema_contracts as schemas


PRESECURITY_READY = "PRESECURITY_READY"
PRESECURITY_REPAIR_PACKET = "PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-REPAIR-V1"
ADAPTER_STUB_PACKET = "PKT-AIOS-BROKER-PAPER-SANDBOX-ADAPTER-STUB-CONTRACT"
ALLOWED_PRESECURITY_CLASSIFICATIONS = {"FAIL", "WATCHLIST", PRESECURITY_READY}
FORBIDDEN_PRESECURITY_CLASSIFICATIONS = {"LIVE_READY", "BROKER_READY", "ORDER_READY"}

SECRET_EXCLUSION_PATTERNS = [
    ".env",
    "*.env",
    ".env.*",
    "*.pem",
    "*.key",
    "id_rsa",
    "id_ed25519",
    "*.pfx",
    "*.p12",
    "*secret*",
    "*secrets*",
]

BLOCKED_CAPABILITIES = [
    "broker SDK activation",
    "credential or .env reads",
    "network/API ingestion",
    "webhook registration or execution",
    "scheduler activation",
    "daemon activation",
    "broker-paper order execution",
    "live order execution",
    "real account mutation",
]


def build_presecurity_requirements() -> dict[str, Any]:
    requirements = {
        "schema": "AIOS_BROKER_PAPER_PRESECURITY_REQUIREMENTS.v1",
        "mode": "PAPER_ONLY_CONTRACT",
        "credential_boundary_required": True,
        "env_secret_read_allowed": False,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "manual_approval_required": True,
        "kill_switch_required": True,
        "max_loss_guard_required": True,
        "daily_stop_required": True,
        "audit_log_required": True,
        "rustdesk_operator_hygiene_required": True,
        "secrets_exclusion_patterns": list(SECRET_EXCLUSION_PATTERNS),
        "blocked_capabilities": list(BLOCKED_CAPABILITIES),
        "next_safe_packet_if_ready": ADAPTER_STUB_PACKET,
        "next_safe_packet_if_blocked": PRESECURITY_REPAIR_PACKET,
        "broker_ready": False,
        "broker_paper_ready": False,
        "live_ready": False,
        "protected_gate_required": True,
        "safety": broker_paper_presecurity_boundary_summary(),
    }
    schemas.assert_no_live_permissions(requirements)
    return requirements


def evaluate_broker_paper_presecurity_gate(context: dict[str, Any] | None = None) -> dict[str, Any]:
    requirements = build_presecurity_requirements()
    active = {**requirements, **dict(context or {})}
    active["secrets_exclusion_patterns"] = list(
        active.get("secrets_exclusion_patterns") or SECRET_EXCLUSION_PATTERNS
    )
    active["blocked_capabilities"] = list(active.get("blocked_capabilities") or BLOCKED_CAPABILITIES)
    blockers = _presecurity_blockers(active)
    result = {
        "schema": "AIOS_BROKER_PAPER_PRESECURITY_GATE_RESULT.v1",
        "mode": "PAPER_ONLY_CONTRACT",
        "classification": "WATCHLIST",
        "requirements": requirements,
        "credential_boundary_required": bool(active.get("credential_boundary_required", False)),
        "env_secret_read_allowed": bool(active.get("env_secret_read_allowed", True)),
        "broker_sdk_allowed": bool(active.get("broker_sdk_allowed", True)),
        "network_api_allowed": bool(active.get("network_api_allowed", True)),
        "webhook_allowed": bool(active.get("webhook_allowed", True)),
        "scheduler_allowed": bool(active.get("scheduler_allowed", True)),
        "daemon_allowed": bool(active.get("daemon_allowed", True)),
        "broker_paper_orders_allowed": bool(active.get("broker_paper_orders_allowed", True)),
        "live_orders_allowed": bool(active.get("live_orders_allowed", True)),
        "manual_approval_required": bool(active.get("manual_approval_required", False)),
        "kill_switch_required": bool(active.get("kill_switch_required", False)),
        "max_loss_guard_required": bool(active.get("max_loss_guard_required", False)),
        "daily_stop_required": bool(active.get("daily_stop_required", False)),
        "audit_log_required": bool(active.get("audit_log_required", False)),
        "rustdesk_operator_hygiene_required": bool(active.get("rustdesk_operator_hygiene_required", False)),
        "secrets_exclusion_patterns": list(active["secrets_exclusion_patterns"]),
        "blocked_capabilities": list(active["blocked_capabilities"]),
        "blockers": blockers,
        "broker_ready": False,
        "broker_paper_ready": False,
        "broker_paper_contract_ready": False,
        "broker_paper_orders_ready": False,
        "live_ready": False,
        "live_trade_ready": False,
        "protected_gate_required": True,
        "next_safe_packet": PRESECURITY_REPAIR_PACKET,
        "next_safe_action": _next_safe_action("WATCHLIST", blockers),
        "safety": broker_paper_presecurity_boundary_summary(),
    }
    result["classification"] = classify_presecurity_gate(result)
    result["next_safe_packet"] = ADAPTER_STUB_PACKET if result["classification"] == PRESECURITY_READY else PRESECURITY_REPAIR_PACKET
    result["next_safe_action"] = _next_safe_action(result["classification"], blockers)
    schemas.assert_no_live_permissions(result)
    return result


def summarize_presecurity_gate(result: dict[str, Any]) -> dict[str, Any]:
    payload = dict(result)
    summary = {
        "schema": "AIOS_BROKER_PAPER_PRESECURITY_GATE_SUMMARY.v1",
        "mode": str(payload.get("mode") or "PAPER_ONLY_CONTRACT"),
        "classification": classify_presecurity_gate(payload),
        "presecurity_gate_classification": classify_presecurity_gate(payload),
        "credential_boundary_required": bool(payload.get("credential_boundary_required", True)),
        "env_secret_read_allowed": False,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "manual_approval_required": bool(payload.get("manual_approval_required", True)),
        "kill_switch_required": bool(payload.get("kill_switch_required", True)),
        "max_loss_guard_required": bool(payload.get("max_loss_guard_required", True)),
        "daily_stop_required": bool(payload.get("daily_stop_required", True)),
        "audit_log_required": bool(payload.get("audit_log_required", True)),
        "rustdesk_operator_hygiene_required": bool(payload.get("rustdesk_operator_hygiene_required", True)),
        "secrets_exclusion_patterns": list(payload.get("secrets_exclusion_patterns") or SECRET_EXCLUSION_PATTERNS),
        "blocked_capabilities": list(payload.get("blocked_capabilities") or BLOCKED_CAPABILITIES),
        "blockers": list(payload.get("blockers") or []),
        "broker_paper_contract_ready": False,
        "live_ready": False,
        "protected_gate_required": True,
        "next_safe_packet": str(payload.get("next_safe_packet") or PRESECURITY_REPAIR_PACKET),
        "next_safe_action": str(
            payload.get("next_safe_action")
            or _next_safe_action(classify_presecurity_gate(payload), list(payload.get("blockers") or []))
        ),
    }
    schemas.assert_no_live_permissions(summary)
    return summary


def classify_presecurity_gate(result: dict[str, Any]) -> str:
    payload = dict(result)
    candidate = str(payload.get("classification") or "WATCHLIST")
    if candidate in FORBIDDEN_PRESECURITY_CLASSIFICATIONS or payload.get("live_ready") is True:
        return "FAIL"
    if candidate not in ALLOWED_PRESECURITY_CLASSIFICATIONS:
        return "FAIL"
    forbidden_false_fields = (
        "env_secret_read_allowed",
        "broker_sdk_allowed",
        "network_api_allowed",
        "webhook_allowed",
        "scheduler_allowed",
        "daemon_allowed",
        "broker_paper_orders_allowed",
        "live_orders_allowed",
    )
    if any(payload.get(field) is not False for field in forbidden_false_fields):
        return "FAIL"
    if payload.get("broker_ready") is True or payload.get("broker_paper_ready") is True:
        return "FAIL"
    if payload.get("broker_paper_contract_ready") is True or payload.get("broker_paper_orders_ready") is True:
        return "FAIL"
    if payload.get("protected_gate_required") is not True:
        return "FAIL"
    if _presecurity_blockers(payload):
        return "WATCHLIST"
    return PRESECURITY_READY


def broker_paper_presecurity_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_BROKER_PAPER_PRESECURITY_BOUNDARY.v1",
        "readiness_contract_only": True,
        "local_simulation_only": True,
        "broker_integration_active": False,
        "broker_sdk_allowed": False,
        "broker_paper_orders": False,
        "paper_order_execution": False,
        "broker_paper_orders_allowed": False,
        "real_order_ready": False,
        "network_allowed": False,
        "network_api_allowed": False,
        "api_ingestion": False,
        "webhook_allowed": False,
        "credentials_required_now": False,
        "credentials_allowed": False,
        "secrets_allowed": False,
        "env_reads_allowed": False,
        "env_secret_read_allowed": False,
        "env_writes_allowed": False,
        "live_trading": False,
        "live_orders_allowed": False,
        "live_ready": False,
        "live_trade_ready": False,
        "execution_allowed": False,
        "orders_allowed": False,
        "account_mutation": False,
        "webhooks_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "protected_gate_required": True,
        "reports_written": False,
        "files_written": [],
        "next_safe_packet_if_ready": ADAPTER_STUB_PACKET,
    }


def _presecurity_blockers(payload: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field in (
        "credential_boundary_required",
        "manual_approval_required",
        "kill_switch_required",
        "max_loss_guard_required",
        "daily_stop_required",
        "audit_log_required",
        "rustdesk_operator_hygiene_required",
    ):
        if payload.get(field) is not True:
            blockers.append(f"missing_required_control:{field}")
    for field in (
        "env_secret_read_allowed",
        "broker_sdk_allowed",
        "network_api_allowed",
        "webhook_allowed",
        "scheduler_allowed",
        "daemon_allowed",
        "broker_paper_orders_allowed",
        "live_orders_allowed",
    ):
        if payload.get(field) is not False:
            blockers.append(f"forbidden_capability_enabled:{field}")
    patterns = set(str(item) for item in list(payload.get("secrets_exclusion_patterns") or []))
    for pattern in SECRET_EXCLUSION_PATTERNS:
        if pattern not in patterns:
            blockers.append(f"missing_secret_exclusion:{pattern}")
    return _unique(blockers)


def _next_safe_action(classification: str, blockers: list[str]) -> str:
    if classification == PRESECURITY_READY:
        return (
            "Proceed only to PKT-AIOS-BROKER-PAPER-SANDBOX-ADAPTER-STUB-CONTRACT; "
            "broker SDK, credentials, network, webhooks, paper orders, and live trading remain blocked."
        )
    if any(str(blocker).startswith("forbidden_capability_enabled") for blocker in blockers):
        return "Disable forbidden presecurity capability flags before any broker-paper adapter-stub work."
    return "Repair missing presecurity contract requirements before any broker-paper adapter-stub work."


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
