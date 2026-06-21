from __future__ import annotations

from typing import Any, Dict, Iterable, Mapping


RUNTIME_CONNECTOR_BLOCKED = "RUNTIME_CONNECTOR_BLOCKED"
RUNTIME_CONNECTOR_INCOMPLETE = "RUNTIME_CONNECTOR_INCOMPLETE"
RUNTIME_CONNECTOR_REVIEW_READY = "RUNTIME_CONNECTOR_REVIEW_READY"
RUNTIME_CONNECTOR_REJECTED = "RUNTIME_CONNECTOR_REJECTED"


def _read_first(mapping: Mapping[str, Any], *keys: str, default: Any = None) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def _read_first_nested(mapping: Mapping[str, Any], aliases: Iterable[str], default: Any = None) -> Any:
    for key in aliases:
        if key in mapping:
            return mapping[key]
    return default


def _append(items: list[str], value: str) -> None:
    if value not in items:
        items.append(value)


def _to_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on", "pass", "passed", "ready", "complete", "active"}:
        return True
    if text in {"0", "false", "no", "off", "inactive", "fail", "failed", "blocked", "rejected"}:
        return False
    return bool(value)


def _is_presentproof(value: Any) -> bool:
    if isinstance(value, Mapping):
        if not value:
            return False
        return any(_to_bool(value.get(key, False), default=False) for key in ("present", "verified", "available", "enabled"))
    return _to_bool(value, default=False)


def _status_is_ready(value: Any, expected: str) -> bool:
    return str(value or "").strip() == expected


def _required_next_packets(status: str) -> list[str]:
    if status == RUNTIME_CONNECTOR_REVIEW_READY:
        return [
            "AIOS_FOREX_BROKER_DEMO_RUNTIME_REVIEW_V1",
            "AIOS_FOREX_REPLAYABILITY_GUARD_V1",
            "AIOS_FOREX_RECONCILIATION_MANDATE_V1",
        ]
    if status == RUNTIME_CONNECTOR_BLOCKED:
        return ["remove_unsafe_runtime_controls", "restore_connector_invariants"]
    return [
        "collect_missing_connector_inputs",
        "provide_required_proofs",
        "verify_one_shot_controls",
    ]


def _next_action(status: str) -> str:
    if status == RUNTIME_CONNECTOR_REVIEW_READY:
        return "prepare_broker_demo_runtime_review"
    if status == RUNTIME_CONNECTOR_BLOCKED:
        return "resolve_runtime_connector_unsafe_flags"
    return "resolve_runtime_connector_blockers"


def evaluate_broker_demo_runtime_connector(
    state: Mapping[str, Any] | None,
    optional_limits: Mapping[str, Any] | None = None,
) -> Dict[str, Any]:
    state = state or {}
    _ = optional_limits or {}

    blockers: list[str] = []

    connector_contract_status = _read_first(
        state,
        "connector_contract_status",
        "connector_status",
        "connector_state",
        default="",
    )
    review_chain_status = _read_first(state, "review_chain_status", "chain_status", "review_chain_state", default="")
    review_chain_completed = _to_bool(_read_first(state, "review_chain_completed", "review_chain_complete", default=False), default=False)
    certificate_status = _read_first(
        state,
        "certificate_status",
        "live_review_certificate_status",
        "certificate_state",
        default="",
    )
    certificate_completed = _to_bool(_read_first(state, "certificate_completed", "certificate_complete", default=False), default=False)
    one_shot_status = _read_first(
        state,
        "one_shot_status",
        "exception_package_status",
        "one_shot_package_status",
        default="",
    )
    one_shot_review_ready = _to_bool(
        _read_first(
            state,
            "live_micro_trade_review_ready",
            "one_shot_ready",
            "review_ready",
            default=False,
        ),
        default=False,
    )

    if not connector_contract_status:
        _append(blockers, "missing_connector_contract")
    elif not _status_is_ready(connector_contract_status, "CONNECTOR_CONTRACT_REVIEW_READY"):
        _append(blockers, "connector_contract_not_ready")

    if not review_chain_status:
        _append(blockers, "missing_review_chain")
    elif not _status_is_ready(review_chain_status, "REVIEW_CHAIN_REVIEW_READY"):
        _append(blockers, "review_chain_not_ready")
    elif not review_chain_completed:
        _append(blockers, "review_chain_not_ready")

    if not certificate_status:
        _append(blockers, "missing_certificate")
    elif not _status_is_ready(certificate_status, "LIVE_REVIEW_CERTIFICATE_REVIEW_READY"):
        _append(blockers, "certificate_not_ready")
    elif not certificate_completed:
        _append(blockers, "certificate_not_ready")

    if not one_shot_status:
        _append(blockers, "missing_one_shot_controls")
    elif not _status_is_ready(one_shot_status, "ONE_SHOT_EXCEPTION_REVIEW_READY"):
        _append(blockers, "missing_one_shot_controls")
    if not one_shot_review_ready:
        _append(blockers, "missing_one_shot_controls")

    proof_aliases = {
        "replay_proof": ("replay_proof", "replayability_proof", "replay"),
        "reconciliation_proof": ("reconciliation_proof", "reconciliation"),
        "kill_switch_proof": ("kill_switch_proof", "kill_switch"),
        "rollback_proof": ("rollback_proof", "rollback"),
        "freshness_proof": ("freshness_proof", "evidence_freshness", "evidence_fresh"),
        "final_disarm_proof": ("final_disarm_proof", "final_disarm"),
    }

    for blocker_key, aliases in proof_aliases.items():
        if not _is_presentproof(_read_first_nested(state, aliases, default=False)):
            _append(blockers, f"missing_{blocker_key}")

    one_shot_controls = _read_first_nested(state, ("one_shot_controls", "controls"), default=None)
    if not isinstance(one_shot_controls, Mapping):
        _append(blockers, "missing_one_shot_controls")
    else:
        if not _to_bool(one_shot_controls.get("one_order_only", False), default=False):
            _append(blockers, "missing_one_shot_controls")
        if not _to_bool(one_shot_controls.get("manual_arming_required", False), default=False):
            _append(blockers, "missing_one_shot_controls")
        if not _to_bool(one_shot_controls.get("no_retry_loop", False), default=False):
            _append(blockers, "missing_one_shot_controls")
        if not _to_bool(one_shot_controls.get("no_autonomous_reentry", False), default=False):
            _append(blockers, "missing_one_shot_controls")

    unsafe_map = {
        "broker_connection_detected": _to_bool(
            _read_first_nested(
                state,
                ("unsafe_broker_connection_detected", "broker_connection_active", "broker_connection_detected"),
                default=False,
            ),
            default=False,
        ),
        "network_access_detected": _to_bool(
            _read_first_nested(
                state,
                ("unsafe_network_access_detected", "network_access", "network_access_detected"),
                default=False,
            ),
            default=False,
        ),
        "credential_access_detected": _to_bool(
            _read_first_nested(
                state,
                ("unsafe_credential_access_detected", "credentials_accessed", "credential_access_detected"),
                default=False,
            ),
            default=False,
        ),
        "account_identifier_access_detected": _to_bool(
            _read_first_nested(
                state,
                ("unsafe_account_identifier_access_detected", "account_identifiers_accessed", "account_identifier_access_detected"),
                default=False,
            ),
            default=False,
        ),
        "order_execution_detected": _to_bool(
            _read_first_nested(
                state,
                ("unsafe_order_execution_detected", "order_execution_enabled", "order_execution_detected"),
                default=False,
            ),
            default=False,
        ),
        "live_trading_authorization_detected": _to_bool(
            _read_first_nested(
                state,
                ("unsafe_live_trading_authorization_detected", "live_trading_authorized", "live_trading_authorization_detected"),
                default=False,
            ),
            default=False,
        ),
        "execution_authority_detected": _to_bool(
            _read_first_nested(
                state,
                ("unsafe_execution_authority_detected", "execution_authority_granted", "execution_authority_detected"),
                default=False,
            ),
            default=False,
        ),
    }
    for blocker, active in unsafe_map.items():
        if active:
            _append(blockers, blocker)

    if all(v in blockers for v in ("missing_connector_contract", "missing_review_chain", "missing_certificate")):
        status = RUNTIME_CONNECTOR_BLOCKED
    elif any(unsafe_map.values()):
        status = RUNTIME_CONNECTOR_BLOCKED
    elif blockers:
        status = RUNTIME_CONNECTOR_INCOMPLETE
    else:
        status = RUNTIME_CONNECTOR_REVIEW_READY

    runtime_connector_completed = status in {
        RUNTIME_CONNECTOR_REVIEW_READY,
        RUNTIME_CONNECTOR_INCOMPLETE,
        RUNTIME_CONNECTOR_BLOCKED,
    }

    runtime_contract = {
        "contract_version": "BROKER_DEMO_RUNTIME_CONNECTOR_SKELETON_V1",
        "review_chain_required": True,
        "connector_contract_required": True,
        "certificate_required": True,
        "replay_required": True,
        "reconciliation_required": True,
        "kill_switch_required": True,
        "rollback_required": True,
        "freshness_required": True,
        "final_disarm_required": True,
        "one_shot_controls_required": True,
        "broker_connection_active": False,
        "network_access": False,
        "credentials_accessed": False,
        "account_identifiers_accessed": False,
        "order_execution_enabled": False,
        "live_trading_authorized": False,
        "execution_authority_granted": False,
    }

    safety = {
        "broker_connection_active": False,
        "network_access": False,
        "credentials_accessed": False,
        "account_identifiers_accessed": False,
        "order_execution_enabled": False,
        "live_trading_authorized": False,
        "execution_authority_granted": False,
    }

    return {
        "runtime_connector_completed": runtime_connector_completed,
        "runtime_connector_status": status,
        "runtime_connector_ready": status == RUNTIME_CONNECTOR_REVIEW_READY,
        "runtime_connector_review_required": status != RUNTIME_CONNECTOR_REVIEW_READY,
        "runtime_connector_blocked": status == RUNTIME_CONNECTOR_BLOCKED,
        "runtime_connector_summary": {
            "connector_contract_status": connector_contract_status,
            "review_chain_status": review_chain_status,
            "certificate_status": certificate_status,
            "one_shot_status": one_shot_status,
        },
        "runtime_connector_blockers": blockers,
        "runtime_connector_warnings": [],
        "runtime_connector_next_safe_action": _next_action(status),
        "runtime_connector_required_next_packets": _required_next_packets(status),
        "runtime_contract": runtime_contract,
        "safety": safety,
    }
