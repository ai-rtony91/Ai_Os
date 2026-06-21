from __future__ import annotations

from typing import Any, Iterable, Mapping

PROTECTED_CONNECTOR_GATE_BLOCKED = "PROTECTED_CONNECTOR_GATE_BLOCKED"
PROTECTED_CONNECTOR_GATE_INCOMPLETE = "PROTECTED_CONNECTOR_GATE_INCOMPLETE"
PROTECTED_CONNECTOR_GATE_REVIEW_READY = "PROTECTED_CONNECTOR_GATE_REVIEW_READY"
PROTECTED_CONNECTOR_GATE_REJECTED = "PROTECTED_CONNECTOR_GATE_REJECTED"
PROTECTED_CONNECTOR_GATE_REVOKED = "PROTECTED_CONNECTOR_GATE_REVOKED"
PROTECTED_CONNECTOR_GATE_EXPIRED = "PROTECTED_CONNECTOR_GATE_EXPIRED"

BROKER_DEMO_RUNTIME_REVIEW_READY = "BROKER_DEMO_RUNTIME_REVIEW_READY"
BROKER_DEMO_RUNTIME_REVIEW_REJECTED = "BROKER_DEMO_RUNTIME_REVIEW_REJECTED"

RUNTIME_CONNECTOR_REVIEW_READY = "RUNTIME_CONNECTOR_REVIEW_READY"
RUNTIME_CONNECTOR_REJECTED = "RUNTIME_CONNECTOR_REJECTED"

CONNECTOR_CONTRACT_REVIEW_READY = "CONNECTOR_CONTRACT_REVIEW_READY"
CONNECTOR_CONTRACT_REJECTED = "CONNECTOR_CONTRACT_REJECTED"

REVIEW_CHAIN_REVIEW_READY = "REVIEW_CHAIN_REVIEW_READY"
REVIEW_CHAIN_REJECTED = "REVIEW_CHAIN_REJECTED"

LIVE_REVIEW_CERTIFICATE_REVIEW_READY = "LIVE_REVIEW_CERTIFICATE_REVIEW_READY"
LIVE_REVIEW_CERTIFICATE_REJECTED = "LIVE_REVIEW_CERTIFICATE_REJECTED"

ONE_SHOT_EXCEPTION_REVIEW_READY = "ONE_SHOT_EXCEPTION_REVIEW_READY"
ONE_SHOT_EXCEPTION_REJECTED = "ONE_SHOT_EXCEPTION_REJECTED"


def _to_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on", "ready", "complete", "pass", "passed", "active", "required"}:
        return True
    if text in {"0", "false", "no", "off", "inactive", "fail", "failed", "blocked", "rejected", "not ready"}:
        return False
    return bool(value)


def _read_first(mapping: Mapping[str, Any], aliases: Iterable[str], default: Any = None) -> Any:
    for key in aliases:
        if key in mapping:
            return mapping[key]
    return default


def _read_status(state: Mapping[str, Any], aliases: Iterable[str], nested_aliases: Iterable[str] = ("status", "state"), default: str = "") -> tuple[str, bool]:
    for key in aliases:
        if key not in state:
            continue
        value = state[key]
        if value is None:
            continue
        if isinstance(value, Mapping):
            nested_status = _read_first(value, aliases, default=None)
            if nested_status is not None:
                nested_text = str(nested_status).strip()
                if nested_text:
                    return nested_text, True
                continue
            for nested_key in nested_aliases:
                if nested_key in value and value[nested_key] is not None:
                    nested_text = str(value[nested_key]).strip()
                    if nested_text:
                        return nested_text, True
            continue
        text = str(value).strip()
        if text:
            return text, True
    return default, False


def _append(blockers: list[str], value: str) -> None:
    if value not in blockers:
        blockers.append(value)


def _proof_present(value: Any) -> bool:
    if isinstance(value, Mapping):
        return _to_bool(
            _read_first(
                value,
                ("present", "verified", "available", "fresh", "active", "enabled", "ok"),
                default=False,
            ),
            default=False,
        )
    return _to_bool(value, default=False)


def _required_next_packets(status: str) -> list[str]:
    if status == PROTECTED_CONNECTOR_GATE_REVIEW_READY:
        return [
            "AIOS_FOREX_PROTECTED_BROKER_DEMO_CONNECTOR_GATE_V1_APPROVAL_READY",
            "AIOS_FOREX_PROTECTED_BROKER_DEMO_CONNECTOR_INTEGRATION_QUEUE",
        ]
    if status == PROTECTED_CONNECTOR_GATE_REJECTED:
        return [
            "repair_rejected_upstream_connector_gate_inputs",
            "request_connector_review_recovery_packet",
            "reopen_human_approval_cycle",
        ]
    if status == PROTECTED_CONNECTOR_GATE_BLOCKED:
        return [
            "clear_unsafe_connector_flags",
            "restore_no_connection_invariants",
            "recheck_connector_controls",
        ]
    if status in {PROTECTED_CONNECTOR_GATE_REVOKED, PROTECTED_CONNECTOR_GATE_EXPIRED}:
        return [
            "restore_gate_authority",
            "refresh_safety_contracts",
            "renew_connector_window",
        ]
    return [
        "collect_missing_protected_connector_gate_inputs",
        "collect_missing_connector_gate_proofs",
        "resolve_connector_scope_requirements",
    ]


def _next_safe_action(status: str) -> str:
    if status == PROTECTED_CONNECTOR_GATE_REVIEW_READY:
        return "collect_connector_integration_handshake_packet"
    if status == PROTECTED_CONNECTOR_GATE_REJECTED:
        return "repair_rejected_upstream_protected_connector_stages"
    if status == PROTECTED_CONNECTOR_GATE_BLOCKED:
        return "resolve_unsafe_protected_connector_runtime_flags"
    if status in {PROTECTED_CONNECTOR_GATE_REVOKED, PROTECTED_CONNECTOR_GATE_EXPIRED}:
        return "renew_protected_connector_authorization"
    return "collect_missing_connector_gate_blockers"


def evaluate_protected_broker_demo_connector_gate(
    state: Mapping[str, Any] | None,
    optional_limits: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    _ = optional_limits
    state = state or {}

    blockers: list[str] = []

    broker_demo_runtime_review_status, br_review_present = _read_status(
        state,
        ("broker_demo_runtime_review_status", "broker_demo_review_status", "broker_demo_runtime_review"),
    )
    runtime_connector_status, runtime_connector_present = _read_status(
        state,
        ("runtime_connector_status", "broker_demo_runtime_connector_status", "runtime_connector"),
    )
    connector_contract_status, connector_contract_present = _read_status(
        state,
        ("connector_contract_status", "live_review_connector_contract_status", "connector_contract"),
    )
    review_chain_status, review_chain_present = _read_status(
        state,
        ("review_chain_status", "chain_status"),
    )
    certificate_status, certificate_present = _read_status(
        state,
        ("certificate_status", "live_review_certificate_status"),
    )
    one_shot_status, one_shot_present = _read_status(
        state,
        ("one_shot_status", "exception_package_status"),
    )

    if not br_review_present:
        _append(blockers, "missing_broker_demo_runtime_review")
    elif broker_demo_runtime_review_status == BROKER_DEMO_RUNTIME_REVIEW_REJECTED:
        _append(blockers, "rejected_broker_demo_runtime_review")
    elif broker_demo_runtime_review_status != BROKER_DEMO_RUNTIME_REVIEW_READY:
        _append(blockers, "broker_demo_runtime_review_not_ready")

    if not runtime_connector_present:
        _append(blockers, "missing_runtime_connector")
    elif runtime_connector_status == RUNTIME_CONNECTOR_REJECTED:
        _append(blockers, "rejected_runtime_connector")
    elif runtime_connector_status != RUNTIME_CONNECTOR_REVIEW_READY:
        _append(blockers, "runtime_connector_not_ready")

    if not connector_contract_present:
        _append(blockers, "missing_connector_contract")
    elif connector_contract_status == CONNECTOR_CONTRACT_REJECTED:
        _append(blockers, "rejected_connector_contract")
    elif connector_contract_status != CONNECTOR_CONTRACT_REVIEW_READY:
        _append(blockers, "connector_contract_not_ready")

    if not review_chain_present:
        _append(blockers, "missing_review_chain")
    elif review_chain_status == REVIEW_CHAIN_REJECTED:
        _append(blockers, "rejected_review_chain")
    elif review_chain_status != REVIEW_CHAIN_REVIEW_READY:
        _append(blockers, "review_chain_not_ready")

    if not certificate_present:
        _append(blockers, "missing_certificate")
    elif certificate_status == LIVE_REVIEW_CERTIFICATE_REJECTED:
        _append(blockers, "rejected_certificate")
    elif certificate_status != LIVE_REVIEW_CERTIFICATE_REVIEW_READY:
        _append(blockers, "certificate_not_ready")

    if not one_shot_present:
        _append(blockers, "missing_one_shot_package")
    elif one_shot_status == ONE_SHOT_EXCEPTION_REJECTED:
        _append(blockers, "rejected_one_shot_package")
    elif one_shot_status != ONE_SHOT_EXCEPTION_REVIEW_READY:
        _append(blockers, "one_shot_package_not_ready")

    protected_connector_approval = _read_first(
        state,
        ("protected_connector_approval", "connector_approval"),
        default=False,
    )
    if not _to_bool(protected_connector_approval, default=False):
        _append(blockers, "missing_protected_connector_approval")

    approval_window_active = _read_first(
        state,
        ("approval_window_active", "approval_active"),
        default=False,
    )
    approval_window_present = "approval_window_active" in state or "approval_active" in state
    if approval_window_present and not _to_bool(approval_window_active, default=False):
        _append(blockers, "approval_window_inactive")

    approval_trace = _read_first(state, ("approval_trace", "approval"), default=None)
    if not _proof_present(approval_trace):
        _append(blockers, "missing_approval_trace")

    replay_proof = _read_first(
        state,
        ("replay_proof", "replayability_proof", "replay"),
        default=False,
    )
    if not _proof_present(replay_proof):
        _append(blockers, "missing_replay_proof")

    reconciliation_proof = _read_first(
        state,
        ("reconciliation_proof", "reconciliation"),
        default=False,
    )
    if not _proof_present(reconciliation_proof):
        _append(blockers, "missing_reconciliation_proof")

    kill_switch_proof = _read_first(
        state,
        ("kill_switch_proof", "kill_switch"),
        default=False,
    )
    if not _proof_present(kill_switch_proof):
        _append(blockers, "missing_kill_switch_proof")

    rollback_proof = _read_first(
        state,
        ("rollback_proof", "rollback"),
        default=False,
    )
    if not _proof_present(rollback_proof):
        _append(blockers, "missing_rollback_proof")

    freshness_proof = _read_first(
        state,
        ("freshness_proof", "evidence_freshness", "evidence_fresh"),
        default=False,
    )
    if not _proof_present(freshness_proof):
        _append(blockers, "missing_freshness_proof")

    final_disarm_proof = _read_first(
        state,
        ("final_disarm_proof", "final_disarm"),
        default=False,
    )
    if not _proof_present(final_disarm_proof):
        _append(blockers, "missing_final_disarm_proof")

    one_shot_controls = _read_first(state, ("one_shot_controls", "controls"), default=None)
    if not isinstance(one_shot_controls, Mapping):
        _append(blockers, "missing_one_shot_controls")
        one_shot_controls = {}

    if not _to_bool(_read_first(one_shot_controls, ("operator_review_required",), default=True), default=True):
        _append(blockers, "missing_operator_review_requirement")
    if not _to_bool(_read_first(one_shot_controls, ("manual_arming_required",), default=True), default=True):
        _append(blockers, "missing_manual_arming_requirement")
    if not _to_bool(_read_first(one_shot_controls, ("no_retry_loop",), default=True), default=True):
        _append(blockers, "retry_loop_detected")
    if not _to_bool(_read_first(one_shot_controls, ("no_autonomous_reentry",), default=True), default=True):
        _append(blockers, "autonomous_reentry_detected")

    timeout_required = _read_first(state, ("timeout_required",), default=False)
    if not _to_bool(timeout_required, default=False):
        _append(blockers, "missing_timeout_requirement")

    revocation_path = _read_first(state, ("revocation_path", "revoke_path"), default="")
    if not _proof_present(revocation_path):
        _append(blockers, "missing_revocation_path")

    replay_prevention = _read_first(state, ("replay_prevention", "anti_replay"), default=False)
    if not _proof_present(replay_prevention):
        _append(blockers, "missing_replay_prevention")

    rollback_path = _read_first(state, ("rollback_path", "rollback_route"), default="")
    if not _proof_present(rollback_path):
        _append(blockers, "missing_rollback_path")

    post_trade_journal_path = _read_first(state, ("post_trade_journal_path", "journal_path"), default="")
    if not _proof_present(post_trade_journal_path):
        _append(blockers, "missing_post_trade_journal_path")

    connector_scope = _read_first(state, ("connector_scope", "scope"), default="")
    if not _proof_present(connector_scope):
        _append(blockers, "missing_connector_scope")

    if not _proof_present(_read_first(state, ("post_trade_journal_path", "journal_path"), default="")):
        _append(blockers, "missing_post_trade_journal_path")

    if not _to_bool(_read_first(state, ("operator_review_required",), default=True), default=True):
        _append(blockers, "missing_operator_review_requirement")
    if not _to_bool(_read_first(state, ("manual_arming_required",), default=True), default=True):
        _append(blockers, "missing_manual_arming_requirement")

    unsafe_blockers = {
        "broker_connection_detected": _to_bool(
            _read_first(
                state,
                ("broker_connection_detected", "broker_connection_active", "unsafe_broker_connection_detected"),
                default=False,
            ),
            default=False,
        ),
        "network_access_detected": _to_bool(
            _read_first(
                state,
                ("network_access_detected", "network_access", "unsafe_network_access_detected"),
                default=False,
            ),
            default=False,
        ),
        "credential_access_detected": _to_bool(
            _read_first(
                state,
                ("credential_access_detected", "credential_access", "credentials_accessed", "unsafe_credential_access_detected"),
                default=False,
            ),
            default=False,
        ),
        "account_identifier_access_detected": _to_bool(
            _read_first(
                state,
                (
                    "account_identifier_access_detected",
                    "account_identifier_access",
                    "account_identifiers_accessed",
                    "unsafe_account_identifier_access_detected",
                ),
                default=False,
            ),
            default=False,
        ),
        "order_execution_detected": _to_bool(
            _read_first(
                state,
                ("order_execution_detected", "order_execution_enabled", "unsafe_order_execution_detected"),
                default=False,
            ),
            default=False,
        ),
        "live_trading_authorization_detected": _to_bool(
            _read_first(
                state,
                ("live_trading_authorization_detected", "live_trading_authorized", "unsafe_live_trading_detected"),
                default=False,
            ),
            default=False,
        ),
        "execution_authority_detected": _to_bool(
            _read_first(
                state,
                ("execution_authority_detected", "execution_authority_granted", "unsafe_execution_authority_detected"),
                default=False,
            ),
            default=False,
        ),
        "capital_allocation_detected": _to_bool(
            _read_first(
                state,
                (
                    "capital_allocation_detected",
                    "capital_allocated",
                    "capital_allocation_modified",
                    "unsafe_capital_allocation_detected",
                ),
                default=False,
            ),
            default=False,
        ),
        "retry_loop_detected": not _to_bool(
            _read_first(one_shot_controls, ("no_retry_loop",), default=True), default=True
        ),
        "autonomous_reentry_detected": not _to_bool(
            _read_first(one_shot_controls, ("no_autonomous_reentry",), default=True), default=True
        ),
    }
    for blocker, active in unsafe_blockers.items():
        if active:
            _append(blockers, blocker)

    revoked = bool(_read_first(state, ("protected_connector_revoked",), default=False))
    if revoked:
        _append(blockers, "protected_connector_revoked")

    expired = bool(_read_first(state, ("protected_connector_expired",), default=False))
    if not _to_bool(approval_window_active, default=False):
        _append(blockers, "approval_window_inactive")
    if expired:
        _append(blockers, "protected_connector_expired")

    if revoked:
        status = PROTECTED_CONNECTOR_GATE_REVOKED
    elif expired or (approval_window_present and not _to_bool(approval_window_active, default=False)):
        status = PROTECTED_CONNECTOR_GATE_EXPIRED
    elif "rejected_broker_demo_runtime_review" in blockers:
        status = PROTECTED_CONNECTOR_GATE_REJECTED
    elif "rejected_runtime_connector" in blockers:
        status = PROTECTED_CONNECTOR_GATE_REJECTED
    elif "rejected_connector_contract" in blockers:
        status = PROTECTED_CONNECTOR_GATE_REJECTED
    elif "rejected_review_chain" in blockers:
        status = PROTECTED_CONNECTOR_GATE_REJECTED
    elif "rejected_certificate" in blockers:
        status = PROTECTED_CONNECTOR_GATE_REJECTED
    elif "rejected_one_shot_package" in blockers:
        status = PROTECTED_CONNECTOR_GATE_REJECTED
    elif any(
        flag in blockers
        for flag in (
            "broker_connection_detected",
            "network_access_detected",
            "credential_access_detected",
            "account_identifier_access_detected",
            "order_execution_detected",
            "live_trading_authorization_detected",
            "execution_authority_detected",
            "capital_allocation_detected",
            "retry_loop_detected",
            "autonomous_reentry_detected",
        )
    ):
        status = PROTECTED_CONNECTOR_GATE_BLOCKED
    elif blockers:
        status = PROTECTED_CONNECTOR_GATE_INCOMPLETE
    else:
        status = PROTECTED_CONNECTOR_GATE_REVIEW_READY

    if not blockers:
        warnings: list[str] = []
    else:
        warnings = []

    summary = {
        "broker_demo_runtime_review_status": broker_demo_runtime_review_status or "",
        "runtime_connector_status": runtime_connector_status or "",
        "connector_contract_status": connector_contract_status or "",
        "review_chain_status": review_chain_status or "",
        "certificate_status": certificate_status or "",
        "one_shot_status": one_shot_status or "",
        "approval_window_active": _to_bool(approval_window_active, default=False),
        "approval_controls_present": bool(_proof_present(approval_trace)),
        "blocking_count": len(blockers),
    }

    safety = {
        "broker_connection_active": False,
        "network_access": False,
        "credentials_accessed": False,
        "account_identifiers_accessed": False,
        "order_execution_enabled": False,
        "live_trading_authorized": False,
        "execution_authority_granted": False,
        "capital_allocated": False,
        "protected_connector_gate_only": True,
        "broker_demo_connector_not_active": True,
        "operator_review_required": True,
        "manual_arming_required": True,
        "no_retry_loop": True,
        "no_autonomous_reentry": True,
        "final_disarm_required": True,
        "timeout_required": True,
        "revocation_path_required": True,
        "replay_prevention_required": True,
    }

    contract = {
        "contract_version": "PROTECTED_BROKER_DEMO_CONNECTOR_GATE_V1",
        "broker_demo_runtime_review_required": True,
        "runtime_connector_required": True,
        "connector_contract_required": True,
        "review_chain_required": True,
        "certificate_required": True,
        "one_shot_package_required": True,
        "protected_connector_approval_required": True,
        "approval_window_required": True,
        "approval_trace_required": True,
        "replay_required": True,
        "reconciliation_required": True,
        "kill_switch_required": True,
        "rollback_required": True,
        "freshness_required": True,
        "final_disarm_required": True,
        "one_shot_controls_required": True,
        "post_trade_journal_required": True,
        "operator_review_required": True,
        "manual_arming_required": True,
        "timeout_required": True,
        "revocation_path_required": True,
        "replay_prevention_required": True,
        "rollback_path_required": True,
        "connector_scope_required": True,
        "broker_connection_allowed": False,
        "network_access_allowed": False,
        "credential_access_allowed": False,
        "account_identifier_access_allowed": False,
        "order_execution_allowed": False,
        "live_trading_authorized": False,
        "execution_authority_granted": False,
    }

    return {
        "protected_connector_gate_completed": status in {
            PROTECTED_CONNECTOR_GATE_REVIEW_READY,
            PROTECTED_CONNECTOR_GATE_INCOMPLETE,
            PROTECTED_CONNECTOR_GATE_BLOCKED,
            PROTECTED_CONNECTOR_GATE_REJECTED,
            PROTECTED_CONNECTOR_GATE_REVOKED,
            PROTECTED_CONNECTOR_GATE_EXPIRED,
        },
        "protected_connector_gate_status": status,
        "protected_connector_gate_review_ready": status == PROTECTED_CONNECTOR_GATE_REVIEW_READY,
        "protected_connector_gate_blocked": status == PROTECTED_CONNECTOR_GATE_BLOCKED,
        "protected_connector_gate_review_required": status != PROTECTED_CONNECTOR_GATE_REVIEW_READY,
        "protected_connector_gate_summary": summary,
        "protected_connector_gate_blockers": blockers,
        "protected_connector_gate_warnings": warnings,
        "protected_connector_gate_next_safe_action": _next_safe_action(status),
        "protected_connector_gate_required_next_packets": _required_next_packets(status),
        "protected_connector_gate_contract": contract,
        "safety": safety,
    }
