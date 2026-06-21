from __future__ import annotations

from typing import Any, Iterable, Mapping

BROKER_DEMO_RUNTIME_REVIEW_BLOCKED = "BROKER_DEMO_RUNTIME_REVIEW_BLOCKED"
BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE = "BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE"
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


def _append(blockers: list[str], value: str) -> None:
    if value not in blockers:
        blockers.append(value)


def _to_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on", "ready", "complete", "pass", "passed", "active"}:
        return True
    if text in {"0", "false", "no", "off", "inactive", "fail", "failed", "blocked", "rejected"}:
        return False
    return bool(value)


def _read_first(mapping: Mapping[str, Any], aliases: Iterable[str], default: Any = None) -> Any:
    for key in aliases:
        if key in mapping:
            return mapping[key]
    return default


def _read_status(mapping: Mapping[str, Any], aliases: Iterable[str], default: str = "") -> str:
    for key in aliases:
        if key in mapping:
            value = mapping[key]
            if isinstance(value, Mapping):
                nested_status = _read_first(value, aliases=("status", "state"), default="")
                if nested_status:
                    return str(nested_status)
            else:
                return str(value)
    return default


def _proof_present(value: Any) -> bool:
    if isinstance(value, Mapping):
        return any(_to_bool(value.get(field, False), default=False) for field in ("present", "verified", "available", "fresh", "active"))
    return _to_bool(value, default=False)


def _required_proof(state: Mapping[str, Any], aliases: Iterable[str]) -> bool:
    return _proof_present(_read_first(state, aliases, default=False))


def _required_next_packets(status: str) -> list[str]:
    if status == BROKER_DEMO_RUNTIME_REVIEW_READY:
        return [
            "AIOS_FOREX_BROKER_DEMO_RUNTIME_CONNECTOR_SKELETON_V1",
            "AIOS_FOREX_LIVE_REVIEW_CONNECTOR_TO_CONTRACT_V1",
            "AIOS_FOREX_BROKER_DEMO_RUNTIME_REVIEW_V1",
        ]
    if status == BROKER_DEMO_RUNTIME_REVIEW_REJECTED:
        return [
            "repair_upstream_rejected_output",
            "recollect_demo_contract_evidence",
            "request_manual_intervention",
        ]
    if status == BROKER_DEMO_RUNTIME_REVIEW_BLOCKED:
        return [
            "clear_unsafe_runtime_flags",
            "restore_review_only_contracts",
            "recheck_blockers",
        ]
    return [
        "collect_missing_upstream_outputs",
        "collect_runtime_readiness_proofs",
        "restore_connector_contract_requirements",
    ]


def _next_safe_action(status: str) -> str:
    if status == BROKER_DEMO_RUNTIME_REVIEW_READY:
        return "prepare_broker_demo_runtime_readiness_review"
    if status == BROKER_DEMO_RUNTIME_REVIEW_REJECTED:
        return "repair_rejected_upstream_stages"
    if status == BROKER_DEMO_RUNTIME_REVIEW_BLOCKED:
        return "resolve_unsafe_runtime_flags_before_demo_review"
    return "collect_missing_demo_runtime_inputs"


def evaluate_broker_demo_runtime_review(
    state: Mapping[str, Any] | None,
    optional_limits: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    state = state or {}
    _ = optional_limits

    blockers: list[str] = []

    runtime_connector = state.get("runtime_connector")
    connector_contract = state.get("connector_contract")
    review_chain = state.get("review_chain")
    certificate = state.get("certificate")
    one_shot_package = state.get("one_shot_package")

    runtime_connector_status = _read_status(
        state,
        ("runtime_connector_status", "broker_demo_runtime_connector_status", "runtime_connector"),
        default="",
    )
    if isinstance(runtime_connector, Mapping) and not runtime_connector_status:
        runtime_connector_status = str(_read_first(runtime_connector, ("runtime_connector_status", "connector_status"), default=""))
    connector_contract_status = _read_status(
        state,
        ("connector_contract_status", "live_review_connector_contract_status", "connector_status", "review_connector_status"),
        default="",
    )
    if isinstance(connector_contract, Mapping) and not connector_contract_status:
        connector_contract_status = str(
            _read_first(connector_contract, ("connector_contract_status", "contract_status", "status"), default="")
        )
    review_chain_status = _read_status(state, ("review_chain_status", "chain_status"), default="")
    if isinstance(review_chain, Mapping) and not review_chain_status:
        review_chain_status = str(_read_first(review_chain, ("review_chain_status", "chain_status"), default=""))
    certificate_status = _read_status(
        state,
        ("certificate_status", "live_review_certificate_status", "readiness_certificate_status", "certificate_state"),
        default="",
    )
    if isinstance(certificate, Mapping) and not certificate_status:
        certificate_status = str(_read_first(certificate, ("certificate_status", "live_readiness_status"), default=""))
    one_shot_status = _read_status(state, ("one_shot_status", "exception_package_status"), default="")
    if isinstance(one_shot_package, Mapping) and not one_shot_status:
        one_shot_status = str(_read_first(one_shot_package, ("exception_package_status", "one_shot_status"), default=""))

    if not runtime_connector:
        _append(blockers, "missing_runtime_connector")
    elif runtime_connector_status == RUNTIME_CONNECTOR_REJECTED:
        _append(blockers, "rejected_runtime_connector")
    elif runtime_connector_status != RUNTIME_CONNECTOR_REVIEW_READY:
        _append(blockers, "runtime_connector_not_ready")

    if not connector_contract:
        _append(blockers, "missing_connector_contract")
    elif connector_contract_status == CONNECTOR_CONTRACT_REJECTED:
        _append(blockers, "rejected_connector_contract")
    elif connector_contract_status != CONNECTOR_CONTRACT_REVIEW_READY:
        _append(blockers, "connector_contract_not_ready")

    if not review_chain:
        _append(blockers, "missing_review_chain")
    elif review_chain_status == REVIEW_CHAIN_REJECTED:
        _append(blockers, "rejected_review_chain")
    elif review_chain_status != REVIEW_CHAIN_REVIEW_READY:
        _append(blockers, "review_chain_not_ready")

    if not certificate:
        _append(blockers, "missing_certificate")
    elif certificate_status == LIVE_REVIEW_CERTIFICATE_REJECTED:
        _append(blockers, "rejected_certificate")
    elif certificate_status != LIVE_REVIEW_CERTIFICATE_REVIEW_READY:
        _append(blockers, "certificate_not_ready")

    if not one_shot_package:
        _append(blockers, "missing_one_shot_package")
    elif one_shot_status == ONE_SHOT_EXCEPTION_REJECTED:
        _append(blockers, "rejected_one_shot_package")
    elif one_shot_status != ONE_SHOT_EXCEPTION_REVIEW_READY:
        _append(blockers, "one_shot_package_not_ready")

    if not _required_proof(state, ("replay_proof", "replayability_proof", "replay")):
        _append(blockers, "missing_replay_proof")
    if not _required_proof(state, ("reconciliation_proof", "reconciliation")):
        _append(blockers, "missing_reconciliation_proof")
    if not _required_proof(state, ("kill_switch_proof", "kill_switch")):
        _append(blockers, "missing_kill_switch_proof")
    if not _required_proof(state, ("rollback_proof", "rollback")):
        _append(blockers, "missing_rollback_proof")
    if not _required_proof(state, ("freshness_proof", "evidence_freshness", "evidence_fresh")):
        _append(blockers, "missing_freshness_proof")
    if not _required_proof(state, ("final_disarm_proof", "final_disarm")):
        _append(blockers, "missing_final_disarm_proof")
    if not bool(_read_first(state, ("post_trade_journal_path", "journal_path"), default="")):
        _append(blockers, "missing_post_trade_journal_path")

    one_shot_controls = _read_first(state, ("one_shot_controls", "controls"), default=None)
    if not isinstance(one_shot_controls, Mapping):
        _append(blockers, "missing_one_shot_controls")
        one_shot_controls = {}
    if not _to_bool(one_shot_controls.get("operator_review_required", False), default=False):
        _append(blockers, "missing_operator_review_requirement")
    if not _to_bool(one_shot_controls.get("manual_arming_required", False), default=False):
        _append(blockers, "missing_manual_arming_requirement")
    if not _to_bool(one_shot_controls.get("no_retry_loop", False), default=False):
        _append(blockers, "retry_loop_detected")
    if not _to_bool(one_shot_controls.get("no_autonomous_reentry", False), default=False):
        _append(blockers, "autonomous_reentry_detected")
    if not _to_bool(one_shot_controls.get("manual_arming_required", False), default=False):
        _append(blockers, "missing_manual_arming_requirement")

    if not _to_bool(_read_first(state, ("operator_review_required",), default=True), default=False):
        _append(blockers, "missing_operator_review_requirement")

    unsafe_flags = {
        "broker_connection_detected": _to_bool(
            _read_first(state, ("unsafe_broker_connection_detected", "broker_connection_active", "broker_connection_detected"), default=False),
            default=False,
        ),
        "network_access_detected": _to_bool(
            _read_first(state, ("unsafe_network_access_detected", "network_access", "network_access_detected"), default=False),
            default=False,
        ),
        "credential_access_detected": _to_bool(
            _read_first(state, ("unsafe_credential_access_detected", "credentials_accessed", "credential_access_detected"), default=False),
            default=False,
        ),
        "account_identifier_access_detected": _to_bool(
            _read_first(
                state,
                ("unsafe_account_identifier_access_detected", "account_identifiers_accessed", "account_identifier_access_detected"),
                default=False,
            ),
            default=False,
        ),
        "order_execution_detected": _to_bool(
            _read_first(state, ("unsafe_order_execution_detected", "order_execution_enabled", "order_execution_detected"), default=False),
            default=False,
        ),
        "live_trading_authorization_detected": _to_bool(
            _read_first(
                state,
                ("unsafe_live_trading_authorization_detected", "live_trading_authorized", "live_trading_authorization_detected"),
                default=False,
            ),
            default=False,
        ),
        "execution_authority_detected": _to_bool(
            _read_first(state, ("unsafe_execution_authority_detected", "execution_authority_granted", "execution_authority_detected"), default=False),
            default=False,
        ),
        "capital_allocation_detected": _to_bool(
            _read_first(state, ("unsafe_capital_allocation_detected", "capital_allocated", "capital_allocation_detected"), default=False),
            default=False,
        ),
    }
    for blocker, active in unsafe_flags.items():
        if active:
            _append(blockers, blocker)

    if any(
        b in blockers
        for b in (
            "rejected_runtime_connector",
            "rejected_connector_contract",
            "rejected_review_chain",
            "rejected_certificate",
            "rejected_one_shot_package",
        )
    ):
        status = BROKER_DEMO_RUNTIME_REVIEW_REJECTED
    elif any(unsafe_flags.values()):
        status = BROKER_DEMO_RUNTIME_REVIEW_BLOCKED
    elif blockers:
        status = BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE
    else:
        status = BROKER_DEMO_RUNTIME_REVIEW_READY

    runtime_connector_review = bool(one_shot_controls if isinstance(one_shot_controls, Mapping) else {})
    broker_demo_runtime_contract = {
        "contract_version": "BROKER_DEMO_RUNTIME_REVIEW_V1",
        "runtime_connector_required": True,
        "connector_contract_required": True,
        "review_chain_required": True,
        "certificate_required": True,
        "one_shot_package_required": True,
        "replay_required": True,
        "reconciliation_required": True,
        "kill_switch_required": True,
        "rollback_required": True,
        "freshness_required": True,
        "final_disarm_required": True,
        "post_trade_journal_required": True,
        "operator_review_required": True,
        "manual_arming_required": True,
        "no_retry_loop_required": True,
        "no_autonomous_reentry_required": True,
        "broker_connection_allowed": False,
        "network_access_allowed": False,
        "credential_access_allowed": False,
        "account_identifier_access_allowed": False,
        "order_execution_allowed": False,
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
        "capital_allocated": False,
        "broker_demo_review_only": True,
        "operator_review_required": True,
        "manual_arming_required": True,
        "no_retry_loop": True,
        "no_autonomous_reentry": True,
        "final_disarm_required": True,
    }

    review_summary = {
        "runtime_connector_ready": runtime_connector_review and runtime_connector_status == RUNTIME_CONNECTOR_REVIEW_READY,
        "connector_contract_ready": connector_contract_status == CONNECTOR_CONTRACT_REVIEW_READY,
        "review_chain_ready": review_chain_status == REVIEW_CHAIN_REVIEW_READY,
        "certificate_ready": certificate_status == LIVE_REVIEW_CERTIFICATE_REVIEW_READY,
        "one_shot_package_ready": one_shot_status == ONE_SHOT_EXCEPTION_REVIEW_READY,
    }

    return {
        "broker_demo_review_completed": status in {
            BROKER_DEMO_RUNTIME_REVIEW_READY,
            BROKER_DEMO_RUNTIME_REVIEW_INCOMPLETE,
            BROKER_DEMO_RUNTIME_REVIEW_BLOCKED,
            BROKER_DEMO_RUNTIME_REVIEW_REJECTED,
        },
        "broker_demo_review_status": status,
        "broker_demo_runtime_review_ready": status == BROKER_DEMO_RUNTIME_REVIEW_READY,
        "broker_demo_runtime_blocked": status == BROKER_DEMO_RUNTIME_REVIEW_BLOCKED,
        "broker_demo_runtime_review_required": status != BROKER_DEMO_RUNTIME_REVIEW_READY,
        "broker_demo_review_summary": review_summary,
        "broker_demo_review_blockers": blockers,
        "broker_demo_review_warnings": [],
        "broker_demo_review_next_safe_action": _next_safe_action(status),
        "broker_demo_review_required_next_packets": _required_next_packets(status),
        "broker_demo_runtime_contract": broker_demo_runtime_contract,
        "safety": safety,
    }
