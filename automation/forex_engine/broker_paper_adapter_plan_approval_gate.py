from __future__ import annotations

from typing import Any

from automation.forex_engine import broker_paper_dryrun_replay_evidence_gate
from automation.forex_engine import schema_contracts as schemas


ADAPTER_PLAN_APPROVAL_READY = "ADAPTER_PLAN_APPROVAL_READY"
PACKET_ID = "PKT-AIOS-BROKER-PAPER-ADAPTER-PLAN-APPROVAL-GATE-V1"
ALLOWED_ADAPTER_PLAN_CLASSIFICATIONS = {"FAIL", "WATCHLIST", ADAPTER_PLAN_APPROVAL_READY}
FORBIDDEN_ADAPTER_PLAN_CLASSIFICATIONS = {
    "LIVE_READY",
    "BROKER_READY",
    "ORDER_READY",
    "AUTO_TRADE_READY",
}
APPROVAL_SCOPE = "broker_paper_adapter_plan_only"
PLAN_MODE = "PLAN_ONLY"
APPROVED_HUMAN_OWNERS = {"Anthony Meza", "Human Owner Anthony Meza"}
REQUIRED_APPROVAL_FIELDS = (
    "broker_selection_approval",
    "external_auth_boundary_approval",
    "paper_account_boundary_approval",
    "network_api_plan_approval",
    "order_intent_translation_approval",
    "kill_switch_approval",
    "audit_log_approval",
    "max_loss_daily_stop_approval",
    "human_owner_confirmation",
)
REQUIRED_EXACT_APPROVAL_FIELDS = {
    "approval_scope": APPROVAL_SCOPE,
    "plan_mode": PLAN_MODE,
}
FORBIDDEN_APPROVAL_FIELD_NAMES = {
    "api_key",
    "apikey",
    "access_token",
    "refresh_token",
    "token",
    "password",
    "secret",
    "private_key",
    "credential",
    "credentials",
    "broker_credentials",
    "account_id",
    "account_number",
    "live_account_id",
}


def build_broker_paper_adapter_plan_approval_gate_contract() -> dict[str, Any]:
    contract = {
        "schema": "AIOS_BROKER_PAPER_ADAPTER_PLAN_APPROVAL_GATE_CONTRACT.v1",
        "packet_id": PACKET_ID,
        "mode": "PAPER_ONLY_ADAPTER_PLAN_APPROVAL_GATE",
        "approval_scope_required": APPROVAL_SCOPE,
        "plan_mode_required": PLAN_MODE,
        "source_evidence_required": broker_paper_dryrun_replay_evidence_gate.DRYRUN_REPLAY_EVIDENCE_READY,
        "required_approval_fields": list(REQUIRED_APPROVAL_FIELDS),
        "required_exact_approval_fields": dict(REQUIRED_EXACT_APPROVAL_FIELDS),
        "approved_human_owners": sorted(APPROVED_HUMAN_OWNERS),
        "approval_artifact_forbidden_fields": sorted(FORBIDDEN_APPROVAL_FIELD_NAMES),
        "paper_demo_adapter_planning_allowed": False,
        "adapter_implementation_allowed": False,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "live_trade_ready": False,
        "real_order_ready": False,
        "approval_mutation": False,
        "next_safe_action_if_ready": (
            "Stop for a separate Human Owner-approved broker-paper adapter implementation packet; "
            "broker SDKs, credentials, network/API, broker-paper orders, and live trading remain blocked."
        ),
        "next_safe_action_if_blocked": (
            "Complete the broker-paper adapter plan approval fields without broker credentials, "
            "tokens, account IDs, network calls, order routing, or live execution."
        ),
    }
    schemas.assert_no_live_permissions(contract)
    return contract


def required_broker_paper_adapter_plan_approval_fields() -> list[str]:
    return [
        *REQUIRED_APPROVAL_FIELDS,
        "approved_by_human_owner",
        *REQUIRED_EXACT_APPROVAL_FIELDS.keys(),
    ]


def build_example_plan_only_approval() -> dict[str, Any]:
    return {
        "approval_scope": APPROVAL_SCOPE,
        "plan_mode": PLAN_MODE,
        "broker_selection_approval": True,
        "external_auth_boundary_approval": True,
        "paper_account_boundary_approval": True,
        "network_api_plan_approval": True,
        "order_intent_translation_approval": True,
        "kill_switch_approval": True,
        "audit_log_approval": True,
        "max_loss_daily_stop_approval": True,
        "human_owner_confirmation": True,
        "approved_by_human_owner": "Anthony Meza",
    }


def evaluate_broker_paper_adapter_plan_approval_gate(
    replay_evidence: dict[str, Any] | None = None,
    approval: dict[str, Any] | None = None,
    contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_contract = dict(contract or build_broker_paper_adapter_plan_approval_gate_contract())
    active_replay_evidence = dict(
        replay_evidence
        or broker_paper_dryrun_replay_evidence_gate.build_default_replay_evidence_gate_result()
    )
    replay_summary = broker_paper_dryrun_replay_evidence_gate.summarize_replay_evidence_gate(
        active_replay_evidence
    )
    active_approval = dict(approval or {})
    source_evidence_ready = _source_evidence_ready(active_replay_evidence, replay_summary)
    approval_blockers = _approval_blockers(active_approval)
    source_blockers = _source_evidence_blockers(source_evidence_ready)
    unsafe_blockers = _unsafe_blockers(replay_summary, active_approval)
    forbidden_approval_fields = _forbidden_approval_field_paths(active_approval)
    unsafe_approval_detected = _has_unsafe_approval_flag(active_approval)
    result = {
        "schema": "AIOS_BROKER_PAPER_ADAPTER_PLAN_APPROVAL_GATE_RESULT.v1",
        "packet_id": PACKET_ID,
        "mode": active_contract["mode"],
        "approval_scope_required": APPROVAL_SCOPE,
        "plan_mode_required": PLAN_MODE,
        "source_evidence_classification": str(
            active_replay_evidence.get("classification")
            or replay_summary.get("classification")
            or "WATCHLIST"
        ),
        "source_evidence_ready": source_evidence_ready,
        "approval_complete": not approval_blockers and not unsafe_approval_detected,
        "unsafe_approval_detected": unsafe_approval_detected,
        "forbidden_approval_fields": forbidden_approval_fields,
        "approval_fields_present": sorted(str(key) for key in active_approval.keys()),
        "paper_demo_adapter_planning_allowed": False,
        "adapter_implementation_allowed": False,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "live_trade_ready": False,
        "real_order_ready": False,
        "approval_mutation": False,
        "source_evidence_summary": replay_summary,
        "required_approval_fields": required_broker_paper_adapter_plan_approval_fields(),
        "blockers": _unique([*source_blockers, *approval_blockers, *unsafe_blockers]),
        "contract": active_contract,
    }
    result["classification"] = classify_broker_paper_adapter_plan_approval_gate(result)
    result["broker_paper_adapter_plan_approval_gate_classification"] = result["classification"]
    result["broker_paper_adapter_plan_approval_gate_ready"] = (
        result["classification"] == ADAPTER_PLAN_APPROVAL_READY
    )
    result["paper_demo_adapter_planning_allowed"] = result[
        "broker_paper_adapter_plan_approval_gate_ready"
    ]
    result["next_safe_action"] = _next_safe_action(result["classification"])
    assert_no_broker_paper_adapter_plan_side_effects(result)
    return result


def build_default_broker_paper_adapter_plan_approval_gate_result() -> dict[str, Any]:
    return evaluate_broker_paper_adapter_plan_approval_gate()


def summarize_broker_paper_adapter_plan_approval_gate(
    result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(result or build_default_broker_paper_adapter_plan_approval_gate_result())
    summary = {
        "schema": "AIOS_BROKER_PAPER_ADAPTER_PLAN_APPROVAL_GATE_SUMMARY.v1",
        "packet_id": PACKET_ID,
        "mode": str(payload.get("mode") or "PAPER_ONLY_ADAPTER_PLAN_APPROVAL_GATE"),
        "classification": str(payload.get("classification") or "WATCHLIST"),
        "broker_paper_adapter_plan_approval_gate_classification": str(
            payload.get("broker_paper_adapter_plan_approval_gate_classification")
            or payload.get("classification")
            or "WATCHLIST"
        ),
        "broker_paper_adapter_plan_approval_gate_ready": bool(
            payload.get("broker_paper_adapter_plan_approval_gate_ready", False)
        ),
        "source_evidence_classification": str(
            payload.get("source_evidence_classification") or "WATCHLIST"
        ),
        "source_evidence_ready": payload.get("source_evidence_ready") is True,
        "approval_complete": payload.get("approval_complete") is True,
        "unsafe_approval_detected": payload.get("unsafe_approval_detected") is True,
        "forbidden_approval_fields": list(payload.get("forbidden_approval_fields") or []),
        "paper_demo_adapter_planning_allowed": payload.get("paper_demo_adapter_planning_allowed") is True,
        "adapter_implementation_allowed": False,
        "broker_sdk_allowed": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "live_orders_allowed": False,
        "file_writes_allowed": False,
        "reports_writes_allowed": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credentials_used": False,
        "live_ready": False,
        "live_trade_ready": False,
        "real_order_ready": False,
        "approval_mutation": False,
        "required_approval_fields": list(
            payload.get("required_approval_fields")
            or required_broker_paper_adapter_plan_approval_fields()
        ),
        "blockers": list(payload.get("blockers") or []),
        "next_safe_action": str(payload.get("next_safe_action") or _next_safe_action("WATCHLIST")),
    }
    summary["classification"] = classify_broker_paper_adapter_plan_approval_gate(summary)
    summary["broker_paper_adapter_plan_approval_gate_classification"] = summary["classification"]
    summary["broker_paper_adapter_plan_approval_gate_ready"] = (
        summary["classification"] == ADAPTER_PLAN_APPROVAL_READY
    )
    summary["paper_demo_adapter_planning_allowed"] = summary[
        "broker_paper_adapter_plan_approval_gate_ready"
    ]
    summary["next_safe_action"] = _next_safe_action(summary["classification"])
    assert_no_broker_paper_adapter_plan_side_effects(summary)
    return summary


def classify_broker_paper_adapter_plan_approval_gate(result: dict[str, Any] | None = None) -> str:
    if result is None:
        return classify_broker_paper_adapter_plan_approval_gate(
            summarize_broker_paper_adapter_plan_approval_gate()
        )
    payload = dict(result)
    candidate = str(
        payload.get("classification")
        or payload.get("broker_paper_adapter_plan_approval_gate_classification")
        or "WATCHLIST"
    )
    if candidate in FORBIDDEN_ADAPTER_PLAN_CLASSIFICATIONS:
        return "FAIL"
    if candidate not in ALLOWED_ADAPTER_PLAN_CLASSIFICATIONS:
        return "FAIL"
    if (
        _has_forbidden_effect(payload)
        or payload.get("forbidden_approval_fields")
        or payload.get("unsafe_approval_detected") is True
        or "approval_artifact_attempts_execution_or_live_permission" in list(payload.get("blockers") or [])
    ):
        return "FAIL"
    if list(payload.get("blockers") or []):
        return "WATCHLIST"
    if payload.get("source_evidence_ready") is True and payload.get("approval_complete") is True:
        return ADAPTER_PLAN_APPROVAL_READY
    return "WATCHLIST"


def broker_paper_adapter_plan_approval_gate_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_BROKER_PAPER_ADAPTER_PLAN_APPROVAL_GATE_BOUNDARY.v1",
        "mode": "PAPER_ONLY_ADAPTER_PLAN_APPROVAL_GATE",
        "approval_gate_only": True,
        "adapter_plan_only": True,
        "paper_demo_adapter_planning_allowed_if_approved": True,
        "adapter_implementation_allowed": False,
        "broker_integration_active": False,
        "broker_sdk_allowed": False,
        "network_allowed": False,
        "network_api_allowed": False,
        "api_ingestion": False,
        "credentials_allowed": False,
        "credentials_used": False,
        "credentials_required_now": False,
        "secrets_allowed": False,
        "env_reads_allowed": False,
        "env_secret_read_allowed": False,
        "webhook_allowed": False,
        "webhooks_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "broker_paper_orders_allowed": False,
        "paper_order_execution": False,
        "live_orders_allowed": False,
        "live_ready": False,
        "live_trade_ready": False,
        "real_order_ready": False,
        "execution_allowed": False,
        "orders_allowed": False,
        "would_place_order": False,
        "order_placed": False,
        "broker_request_sent": False,
        "network_used": False,
        "account_mutation": False,
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "reports_written": False,
        "files_written": [],
        "source_evidence_required": broker_paper_dryrun_replay_evidence_gate.DRYRUN_REPLAY_EVIDENCE_READY,
        "approval_scope_required": APPROVAL_SCOPE,
        "plan_mode_required": PLAN_MODE,
    }


def assert_no_broker_paper_adapter_plan_side_effects(payload: dict[str, Any]) -> bool:
    if _has_forbidden_effect(payload):
        raise ValueError("broker-paper adapter approval gate must not enable execution side effects")
    schemas.assert_no_live_permissions(payload)
    return True


def _blocked_capability_fields() -> tuple[str, ...]:
    return (
        "adapter_implementation_allowed",
        "file_writes_allowed",
        "reports_writes_allowed",
        "broker_sdk_allowed",
        "network_api_allowed",
        "credentials_allowed",
        "env_secret_read_allowed",
        "webhook_allowed",
        "scheduler_allowed",
        "daemon_allowed",
        "broker_paper_orders_allowed",
        "live_orders_allowed",
        "would_place_order",
        "order_placed",
        "broker_request_sent",
        "network_used",
        "credentials_used",
        "live_ready",
        "live_trade_ready",
        "real_order_ready",
        "broker_integration_active",
        "credentials_required_now",
        "approval_mutation",
    )


def _has_forbidden_effect(payload: dict[str, Any]) -> bool:
    if any(payload.get(field) is True for field in _blocked_capability_fields()):
        return True
    for nested_name in ("source_evidence_summary", "contract", "safety", "safety_flags"):
        nested = payload.get(nested_name)
        if isinstance(nested, dict) and any(
            nested.get(field) is True for field in _blocked_capability_fields()
        ):
            return True
    return False


def _source_evidence_ready(
    replay_evidence: dict[str, Any],
    replay_summary: dict[str, Any],
) -> bool:
    replay_classification = str(
        replay_evidence.get("classification")
        or replay_evidence.get("broker_paper_dryrun_replay_evidence_gate_classification")
        or ""
    )
    summary_classification = str(replay_summary.get("classification") or "")
    return (
        replay_classification == broker_paper_dryrun_replay_evidence_gate.DRYRUN_REPLAY_EVIDENCE_READY
        and summary_classification == broker_paper_dryrun_replay_evidence_gate.DRYRUN_REPLAY_EVIDENCE_READY
        and replay_evidence.get("evidence_ready") is True
        and replay_summary.get("evidence_ready") is True
    )


def _source_evidence_blockers(source_evidence_ready: bool) -> list[str]:
    if source_evidence_ready:
        return []
    return ["source_replay_evidence_gate_must_be_ready"]


def _approval_blockers(approval: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    for field in REQUIRED_APPROVAL_FIELDS:
        if field not in approval:
            blockers.append(f"missing_approval:{field}")
        elif approval.get(field) is not True:
            blockers.append(f"approval_not_granted:{field}")
    for field, expected in REQUIRED_EXACT_APPROVAL_FIELDS.items():
        if approval.get(field) != expected:
            blockers.append(f"approval_field_must_equal:{field}:{expected}")
    if str(approval.get("approved_by_human_owner") or "") not in APPROVED_HUMAN_OWNERS:
        blockers.append("approved_by_human_owner_must_be_Anthony_Meza")
    for field_path in _forbidden_approval_field_paths(approval):
        blockers.append(f"forbidden_approval_field:{field_path}")
    return _unique(blockers)


def _unsafe_blockers(replay_summary: dict[str, Any], approval: dict[str, Any]) -> list[str]:
    blockers: list[str] = []
    if _has_forbidden_effect(replay_summary):
        blockers.append("source_replay_evidence_has_unsafe_flag")
    if _has_unsafe_approval_flag(approval):
        blockers.append("approval_artifact_attempts_execution_or_live_permission")
    return blockers


def _has_unsafe_approval_flag(value: Any) -> bool:
    if isinstance(value, dict):
        for key, nested in value.items():
            normalized_key = _normalize_key(str(key))
            if normalized_key in _blocked_capability_fields() and nested is True:
                return True
            if normalized_key in {"live_approved", "live_execution_approved"} and nested is True:
                return True
            if _has_unsafe_approval_flag(nested):
                return True
    elif isinstance(value, list):
        return any(_has_unsafe_approval_flag(item) for item in value)
    return False


def _forbidden_approval_field_paths(approval: dict[str, Any]) -> list[str]:
    return _unique(_collect_forbidden_approval_field_paths(approval))


def _collect_forbidden_approval_field_paths(value: Any, prefix: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            if _is_forbidden_approval_field_name(key_text):
                paths.append(path)
            paths.extend(_collect_forbidden_approval_field_paths(nested, path))
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            paths.extend(_collect_forbidden_approval_field_paths(nested, f"{prefix}[{index}]"))
    return paths


def _is_forbidden_approval_field_name(key: str) -> bool:
    normalized = _normalize_key(key)
    if normalized in FORBIDDEN_APPROVAL_FIELD_NAMES:
        return True
    return any(
        marker in normalized
        for marker in (
            "api_key",
            "access_token",
            "refresh_token",
            "private_key",
            "password",
            "secret",
            "credential",
            "credentials",
            "account_id",
            "account_number",
            "live_account_id",
        )
    )


def _normalize_key(key: str) -> str:
    return key.strip().lower().replace("-", "_").replace(" ", "_")


def _next_safe_action(classification: str) -> str:
    if classification == ADAPTER_PLAN_APPROVAL_READY:
        return (
            "Stop for a separate Human Owner-approved broker-paper adapter implementation packet; "
            "broker SDKs, credentials, network/API, broker-paper orders, and live trading remain blocked."
        )
    if classification == "FAIL":
        return (
            "Repair the approval artifact by removing execution permissions and forbidden fields before "
            "any broker-paper adapter planning can continue."
        )
    return (
        "Complete the broker-paper adapter plan approval fields without broker credentials, tokens, "
        "account IDs, network calls, order routing, or live execution."
    )


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
