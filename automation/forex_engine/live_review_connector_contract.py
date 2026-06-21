from __future__ import annotations

from typing import Any, Iterable, Mapping

CONNECTOR_CONTRACT_BLOCKED = "CONNECTOR_CONTRACT_BLOCKED"
CONNECTOR_CONTRACT_INCOMPLETE = "CONNECTOR_CONTRACT_INCOMPLETE"
CONNECTOR_CONTRACT_REVIEW_READY = "CONNECTOR_CONTRACT_REVIEW_READY"
CONNECTOR_CONTRACT_REJECTED = "CONNECTOR_CONTRACT_REJECTED"

REVIEW_CHAIN_REVIEW_READY = "REVIEW_CHAIN_REVIEW_READY"
REVIEW_CHAIN_REJECTED = "REVIEW_CHAIN_REJECTED"
LIVE_REVIEW_CERTIFICATE_REVIEW_READY = "LIVE_REVIEW_CERTIFICATE_REVIEW_READY"
LIVE_REVIEW_CERTIFICATE_REJECTED = "LIVE_REVIEW_CERTIFICATE_REJECTED"
ONE_SHOT_EXCEPTION_REVIEW_READY = "ONE_SHOT_EXCEPTION_REVIEW_READY"
ONE_SHOT_EXCEPTION_REJECTED = "ONE_SHOT_EXCEPTION_REJECTED"


def _read_first(mapping: Mapping[str, Any], aliases: Iterable[str], default: Any = None) -> Any:
    for key in aliases:
        if key in mapping:
            return mapping[key]
    return default


def _as_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on", "pass", "passed", "ok", "active"}:
        return True
    if text in {"0", "false", "no", "off", "inactive", "fail", "failed"}:
        return False
    return bool(value)


def _as_map(value: Any) -> Mapping[str, Any] | None:
    return value if isinstance(value, Mapping) else None


def _append(blockers: list[str], value: str) -> None:
    if value not in blockers:
        blockers.append(value)


def _proof_present(value: Any) -> bool:
    if isinstance(value, Mapping):
        return _as_bool(_read_first(value, ("present", "verified", "available"), default=False), default=False)
    return _as_bool(value, default=False)


def _safe_true_map(state: Mapping[str, Any], aliases: Iterable[str], default: bool = False) -> bool:
    return _as_bool(_read_first(state, aliases, default=default), default=default)


def _derive_next_action_and_packets(status: str) -> tuple[str, list[str]]:
    if status == CONNECTOR_CONTRACT_REVIEW_READY:
        return "submit_review_chain_for_human_approval", [
            "prepare_final_connector_signoff_packet",
            "request_human_review",
            "close_connector_contract_review",
        ]
    if status == CONNECTOR_CONTRACT_REJECTED:
        return "repair_rejected_runtime_inputs", [
            "repair_review_chain_stage",
            "repair_live_readiness_certificate_stage",
            "repair_one_shot_exception_stage",
        ]
    if status == CONNECTOR_CONTRACT_BLOCKED:
        return "resolve_unsafe_runtime_and_clear_blocks", [
            "clear_broker_flags",
            "clear_network_flags",
            "repair_control_invariants",
        ]
    return "collect_missing_connector_contract_inputs", [
        "complete_review_chain_output",
        "collect_missing_connector_readiness_proofs",
        "repair_one_shot_controls",
    ]


def _read_upstream_output(state: Mapping[str, Any], aliases: Iterable[str]) -> Mapping[str, Any] | None:
    for alias in aliases:
        value = state.get(alias)
        if isinstance(value, Mapping):
            return value
    return None


def _read_status(output: Mapping[str, Any] | None, aliases: Iterable[str], default: str = "") -> str:
    if output is None:
        return default
    return str(_read_first(output, aliases, default=default) or default)


def _read_controls(state: Mapping[str, Any], one_shot_output: Mapping[str, Any] | None) -> Mapping[str, Any]:
    controls = _as_map(_read_first(state, ("one_shot_controls", "controls"), default=None))
    if controls is not None:
        return controls
    if one_shot_output is None:
        return {}
    package_controls = _as_map(_read_first(one_shot_output, ("one_shot_controls", "controls", "control_summary"), default=None))
    if package_controls is not None:
        return package_controls
    return {}


def evaluate_live_review_connector_contract(
    state: Mapping[str, Any] | None = None,
    optional_limits: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    state = state or {}
    _ = optional_limits

    review_chain = _read_upstream_output(
        state,
        ("review_chain_orchestrator", "review_chain", "chain"),
    )
    certificate = _read_upstream_output(
        state,
        ("live_review_readiness_certificate", "readiness_certificate", "certificate"),
    )
    one_shot = _read_upstream_output(
        state,
        ("one_shot_exception_package", "exception_package", "one_shot_package"),
    )

    blockers: list[str] = []
    warnings: list[str] = []

    review_chain_status = _read_status(review_chain, ("review_chain_status", "chain_status"), default="")
    certificate_status = _read_status(
        certificate,
        ("certificate_status", "live_review_certificate_status"),
        default="",
    )
    one_shot_status = _read_status(
        one_shot,
        ("exception_package_status", "one_shot_status"),
        default="",
    )

    review_chain_orchestrator_output_present = review_chain is not None
    certificate_output_present = certificate is not None
    one_shot_output_present = one_shot is not None

    if not review_chain_orchestrator_output_present:
        _append(blockers, "missing_review_chain_orchestrator")
    if review_chain_status != REVIEW_CHAIN_REVIEW_READY:
        if review_chain_status == REVIEW_CHAIN_REJECTED:
            _append(blockers, "rejected_review_chain")
        elif review_chain_status:
            _append(blockers, "review_chain_not_review_ready")
        elif review_chain_orchestrator_output_present:
            _append(blockers, "review_chain_not_review_ready")
        else:
            _append(blockers, "review_chain_not_review_ready")

    if not certificate_output_present:
        _append(blockers, "missing_live_review_certificate")
    if certificate_status != LIVE_REVIEW_CERTIFICATE_REVIEW_READY:
        if certificate_status == LIVE_REVIEW_CERTIFICATE_REJECTED:
            _append(blockers, "certificate_rejected")
        elif certificate_status:
            _append(blockers, "certificate_not_review_ready")
        else:
            _append(blockers, "certificate_not_review_ready")

    if not one_shot_output_present:
        _append(blockers, "missing_one_shot_exception_package")
    if one_shot_status != ONE_SHOT_EXCEPTION_REVIEW_READY:
        if one_shot_status == ONE_SHOT_EXCEPTION_REJECTED:
            _append(blockers, "one_shot_package_rejected")
        elif one_shot_status:
            _append(blockers, "one_shot_package_not_review_ready")
        else:
            _append(blockers, "one_shot_package_not_review_ready")

    replay_proof = _as_bool(_proof_present(_read_first(state, ("replay_proof", "replayability_proof", "replay"))), default=False)
    reconciliation_proof = _as_bool(
        _proof_present(_read_first(state, ("reconciliation_proof", "reconciliation"))), default=False
    )
    kill_switch_proof = _as_bool(_proof_present(_read_first(state, ("kill_switch_proof", "kill_switch"))), default=False)
    rollback_proof = _as_bool(_proof_present(_read_first(state, ("rollback_proof", "rollback"))), default=False)
    freshness_proof = _as_bool(
        _proof_present(_read_first(state, ("freshness_proof", "evidence_freshness", "evidence_fresh"))),
        default=False,
    )
    final_disarm_proof = _as_bool(
        _proof_present(_read_first(state, ("final_disarm_proof", "final_disarm"))),
        default=False,
    )
    post_trade_journal_path = _read_first(state, ("post_trade_journal_path", "journal_path"), default="")
    one_shot_controls = _read_controls(state, one_shot)

    if not replay_proof:
        _append(blockers, "missing_replay_proof")
    if not reconciliation_proof:
        _append(blockers, "missing_reconciliation_proof")
    if not kill_switch_proof:
        _append(blockers, "missing_kill_switch_proof")
    if not rollback_proof:
        _append(blockers, "missing_rollback_proof")
    if not freshness_proof:
        _append(blockers, "missing_freshness_proof")
    if not final_disarm_proof:
        _append(blockers, "missing_final_disarm_proof")
    if not post_trade_journal_path:
        _append(blockers, "missing_post_trade_journal_path")

    operator_review_required = _as_bool(_read_first(state, ("operator_review_required",), default=True), default=False)
    if not operator_review_required:
        _append(blockers, "missing_operator_review_requirement")

    manual_arming_required = _as_bool(
        _read_first(one_shot_controls, ("manual_arming_required",), default=True),
        default=False,
    )
    if not manual_arming_required:
        _append(blockers, "missing_manual_arming_requirement")

    no_retry_loop = _as_bool(_read_first(one_shot_controls, ("no_retry_loop",), default=True), default=False)
    if not no_retry_loop:
        _append(blockers, "retry_loop_detected")

    no_autonomous_reentry = _as_bool(
        _read_first(one_shot_controls, ("no_autonomous_reentry",), default=True),
        default=False,
    )
    if not no_autonomous_reentry:
        _append(blockers, "autonomous_reentry_detected")

    if not one_shot_controls:
        _append(blockers, "missing_one_shot_controls")

    broker_connection_detected = _safe_true_map(
        state,
        ("broker_connection_detected", "broker_connection_active", "unsafe_broker_connection_detected"),
        default=False,
    )
    network_access_detected = _safe_true_map(
        state,
        ("network_access", "network_access_detected", "unsafe_network_access_detected"),
        default=False,
    )
    credential_access_detected = _safe_true_map(
        state,
        ("credential_access_detected", "credentials_accessed", "unsafe_credential_access_detected"),
        default=False,
    )
    account_identifier_access_detected = _safe_true_map(
        state,
        ("account_identifier_access_detected", "account_identifiers_accessed", "unsafe_account_identifier_access_detected"),
        default=False,
    )
    order_execution_detected = _safe_true_map(
        state,
        ("order_execution_enabled", "order_execution_enabled_detected", "unsafe_order_execution_detected"),
        default=False,
    )
    live_trading_authorization_detected = _safe_true_map(
        state,
        ("live_trading_authorized", "live_trading_authorization_detected", "unsafe_live_trading_detected"),
        default=False,
    )
    execution_authority_detected = _safe_true_map(
        state,
        ("execution_authority_granted", "execution_authority_detected", "unsafe_execution_authority_detected"),
        default=False,
    )
    capital_allocation_detected = _safe_true_map(
        state,
        ("capital_allocated", "capital_allocation_modified", "capital_allocation_detected", "unsafe_capital_allocation_detected"),
        default=False,
    )
    retry_loop_detected = _safe_true_map(
        state,
        ("retry_loop_detected", "retry_loop", "unsafe_retry_loop_detected"),
        default=False,
    )
    autonomous_reentry_detected = _safe_true_map(
        state,
        ("autonomous_reentry_detected", "autonomous_reentry", "unsafe_autonomous_reentry_detected"),
        default=False,
    )

    if broker_connection_detected:
        _append(blockers, "broker_connection_detected")
    if network_access_detected:
        _append(blockers, "network_access_detected")
    if credential_access_detected:
        _append(blockers, "credential_access_detected")
    if account_identifier_access_detected:
        _append(blockers, "account_identifier_access_detected")
    if order_execution_detected:
        _append(blockers, "order_execution_detected")
    if live_trading_authorization_detected:
        _append(blockers, "live_trading_authorization_detected")
    if execution_authority_detected:
        _append(blockers, "execution_authority_detected")
    if capital_allocation_detected:
        _append(blockers, "capital_allocation_detected")

    if retry_loop_detected and "retry_loop_detected" not in blockers:
        _append(blockers, "retry_loop_detected")
    if autonomous_reentry_detected and "autonomous_reentry_detected" not in blockers:
        _append(blockers, "autonomous_reentry_detected")

    connector_blocked = False
    rejected = (
        "rejected_review_chain" in blockers
        or "certificate_rejected" in blockers
        or "one_shot_package_rejected" in blockers
    )
    missing_upstream = {
        "missing_review_chain_orchestrator",
        "missing_live_review_certificate",
        "missing_one_shot_exception_package",
    }
    unsafe_blockers = {
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
    }

    if any(flag in blockers for flag in unsafe_blockers) or any(flag in blockers for flag in missing_upstream):
        connector_blocked = True
        connector_status = CONNECTOR_CONTRACT_BLOCKED
    elif rejected:
        connector_status = CONNECTOR_CONTRACT_REJECTED
    elif blockers:
        connector_status = CONNECTOR_CONTRACT_INCOMPLETE
    else:
        connector_status = CONNECTOR_CONTRACT_REVIEW_READY

    next_safe_action, required_next_packets = _derive_next_action_and_packets(connector_status)
    required_next_packets = list(dict.fromkeys(required_next_packets))

    connector_runtime_contract = {
        "contract_version": "LIVE_REVIEW_CONNECTOR_CONTRACT_V1",
        "review_chain_required": True,
        "certificate_required": True,
        "one_shot_package_required": True,
        "replay_proof_required": True,
        "reconciliation_proof_required": True,
        "kill_switch_required": True,
        "rollback_required": True,
        "freshness_required": True,
        "manual_arming_required": True,
        "one_order_only_required": True,
        "no_retry_loop_required": True,
        "no_autonomous_reentry_required": True,
        "final_disarm_required": True,
        "post_trade_journal_required": True,
        "broker_connection_allowed": False,
        "credential_access_allowed": False,
        "account_identifier_access_allowed": False,
        "network_access_allowed": False,
        "order_execution_allowed": False,
        "live_trading_authorized": False,
        "execution_authority_granted": False,
        "operator_review_required": True,
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
        "operator_review_required": True,
        "connector_contract_only": True,
        "broker_connection_allowed": False,
        "credential_access_allowed": False,
        "account_identifier_access_allowed": False,
        "network_access_allowed": False,
        "order_execution_allowed": False,
        "one_shot_only": True,
        "manual_arming_required": True,
        "no_retry_loop": True,
        "no_autonomous_reentry": True,
        "final_disarm_required": True,
    }

    review_chain_summary = {
        "review_chain_status": review_chain_status,
        "review_chain_present": review_chain_orchestrator_output_present,
        "review_chain_ready": review_chain_status == REVIEW_CHAIN_REVIEW_READY,
    }
    proof_summary = {
        "replay_proof": replay_proof,
        "reconciliation_proof": reconciliation_proof,
        "kill_switch_proof": kill_switch_proof,
        "rollback_proof": rollback_proof,
        "freshness_proof": freshness_proof,
        "final_disarm_proof": final_disarm_proof,
        "post_trade_journal_path": bool(post_trade_journal_path),
        "one_shot_controls": bool(one_shot_controls),
    }
    runtime_contract_summary = dict(connector_runtime_contract)

    return {
        "connector_contract_completed": connector_status in {
            CONNECTOR_CONTRACT_REVIEW_READY,
            CONNECTOR_CONTRACT_REJECTED,
            CONNECTOR_CONTRACT_BLOCKED,
        },
        "connector_contract_status": connector_status,
        "connector_ready": connector_status == CONNECTOR_CONTRACT_REVIEW_READY,
        "connector_blocked": connector_blocked,
        "connector_review_required": True,
        "connector_runtime_contract": connector_runtime_contract,
        "connector_blockers": blockers,
        "connector_warnings": warnings,
        "connector_next_safe_action": next_safe_action,
        "connector_required_next_packets": required_next_packets,
        "review_chain_summary": review_chain_summary,
        "proof_summary": proof_summary,
        "runtime_contract_summary": runtime_contract_summary,
        "safety": safety,
    }
