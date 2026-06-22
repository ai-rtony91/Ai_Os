from __future__ import annotations

from typing import Any, Iterable, Mapping

from automation.forex_engine.canonical_demo_review_evidence_bridge import (
    BLOCKED_INCOMPLETE_EVIDENCE,
    DEMO_REVIEW_READY,
    PAPER_CONTINUE,
    REJECTED,
)

REVIEW_CHAIN_BLOCKED = "REVIEW_CHAIN_BLOCKED"
REVIEW_CHAIN_INCOMPLETE = "REVIEW_CHAIN_INCOMPLETE"
REVIEW_CHAIN_REVIEW_READY = "REVIEW_CHAIN_REVIEW_READY"
REVIEW_CHAIN_REJECTED = "REVIEW_CHAIN_REJECTED"

DEMO_CONTRACT_COMPLETE = "DEMO_CONTRACT_COMPLETE"
DEMO_CONTRACT_REJECTED = "DEMO_CONTRACT_REJECTED"
ONE_SHOT_EXCEPTION_REVIEW_READY = "ONE_SHOT_EXCEPTION_REVIEW_READY"
ONE_SHOT_EXCEPTION_REJECTED = "ONE_SHOT_EXCEPTION_REJECTED"
LIVE_REVIEW_CERTIFICATE_REVIEW_READY = "LIVE_REVIEW_CERTIFICATE_REVIEW_READY"
LIVE_REVIEW_CERTIFICATE_REJECTED = "LIVE_REVIEW_CERTIFICATE_REJECTED"


def _read_first(mapping: Mapping[str, Any], aliases: Iterable[str], default: Any = None) -> Any:
    for key in aliases:
        if key in mapping:
            return mapping[key]
    return default


def _read_optional_bool(mapping: Mapping[str, Any], aliases: Iterable[str]) -> tuple[bool | None, bool]:
    for key in aliases:
        if key in mapping:
            return _to_bool(mapping[key], default=False), True
    return None, False


def _to_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on", "pass", "passed", "ok", "active"}:
        return True
    if text in {"0", "false", "no", "off", "inactive", "failed", "fail"}:
        return False
    return bool(value)


def _as_map(value: Any) -> Mapping[str, Any] | None:
    return value if isinstance(value, Mapping) else None


def _append(blockers: list[str], value: str) -> None:
    if value not in blockers:
        blockers.append(value)


def _read_candidate_demo_review_payload(state: Mapping[str, Any]) -> Mapping[str, Any] | None:
    for key in (
        "candidate_demo_review_bridge",
        "candidate_intake_demo_review",
        "demo_review_bundle",
        "canonical_demo_review_bundle",
    ):
        payload = _as_map(state.get(key))
        if payload is not None:
            return payload
    return None


def _normalize_candidate_demo_review_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    nested = _as_map(payload.get("demo_review_bundle")) or _as_map(payload.get("canonical_demo_review_bundle"))
    source = nested if nested is not None else payload
    blockers = _read_first(source, ("blockers",), default=[])
    if not isinstance(blockers, list):
        blockers = list(blockers) if blockers is not None else []

    return {
        "present": True,
        "verdict": str(_read_first(source, ("verdict",), default="")).strip(),
        "blockers": blockers,
        "next_safe_action": str(_read_first(source, ("next_safe_action",), default="")),
        "selected_candidate_id": str(
            _read_first(
                payload,
                (
                    "selected_candidate_id",
                    "candidate_id",
                ),
                default="",
            )
        ),
        "selected_strategy": str(_read_first(payload, ("selected_strategy", "strategy"), default="")),
        "selected_direction": str(_read_first(payload, ("selected_direction", "direction"), default="")),
    }


def _next_action_and_packets(status: str) -> tuple[str, list[str]]:
    if status == REVIEW_CHAIN_REVIEW_READY:
        return (
            "submit_review_chain_for_human",
            ["prepare_final_review_packet", "request_human_review", "close_review_chain"],
        )
    if status == REVIEW_CHAIN_REJECTED:
        return (
            "repair_rejected_inputs",
            ["repair_demo_stage", "repair_one_shot_stage", "repair_certificate_stage"],
        )
    if status == REVIEW_CHAIN_BLOCKED:
        return (
            "resolve_unsafe_runtime_flags",
            ["clear_unsafe_inputs", "revalidate_safety_invariants", "restart_review_chain"],
        )
    return (
        "collect_and_align_chain_stages",
        ["collect_missing_chain_outputs", "repair_stage_consistency", "retest_readiness"],
    )


def orchestrate_forex_review_chain(
    state: Mapping[str, Any] | None = None,
    optional_limits: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    state = state or {}
    _ = optional_limits

    blockers: list[str] = []
    warnings: list[str] = []

    candidate_review_payload = _read_candidate_demo_review_payload(state)
    candidate_review = (
        _normalize_candidate_demo_review_payload(candidate_review_payload)
        if candidate_review_payload is not None
        else None
    )

    demo = _as_map(_read_first(state, ("demo_validation_contract", "demo_contract"), default=None))
    if demo is None:
        demo_status = ""
        demo_completed = False
        demo_candidate_ready = False
        _append(blockers, "missing_demo_validation_contract")
        _append(blockers, "demo_validation_contract_not_complete")
    else:
        demo_status = str(_read_first(demo, ("demo_validation_contract_status", "demo_contract_status"), default=""))
        demo_completed = _to_bool(
            _read_first(demo, ("demo_validation_contract_completed", "demo_contract_completed"), default=False),
            default=False,
        )
        demo_candidate_ready = _to_bool(
            _read_first(demo, ("live_readiness_candidate", "candidate_ready"), default=False),
            default=False,
        )
        if demo_status == DEMO_CONTRACT_REJECTED:
            _append(blockers, "demo_validation_contract_rejected")
        elif demo_status != DEMO_CONTRACT_COMPLETE or not demo_completed:
            _append(blockers, "demo_validation_contract_not_complete")

    one_shot = _as_map(_read_first(state, ("one_shot_exception_package", "exception_package"), default=None))
    if one_shot is None:
        one_shot_status = ""
        one_shot_completed = False
        one_shot_review_ready = False
        _append(blockers, "missing_one_shot_exception_package")
    else:
        one_shot_status = str(_read_first(one_shot, ("exception_package_status", "one_shot_status"), default=""))
        one_shot_completed = _to_bool(
            _read_first(one_shot, ("exception_package_completed", "package_completed"), default=False),
            default=False,
        )
        one_shot_review_ready = _to_bool(
            _read_first(one_shot, ("live_micro_trade_review_ready", "review_ready"), default=False),
            default=False,
        )
        if one_shot_status == ONE_SHOT_EXCEPTION_REJECTED:
            _append(blockers, "one_shot_exception_package_rejected")
        elif one_shot_status != ONE_SHOT_EXCEPTION_REVIEW_READY or not one_shot_completed or not one_shot_review_ready:
            _append(blockers, "one_shot_exception_package_not_review_ready")

    cert = _as_map(_read_first(state, ("live_review_readiness_certificate", "readiness_certificate", "certificate"), default=None))
    if cert is None:
        cert_status = ""
        cert_completed = False
        cert_human_ready = False
        cert_trade_ready = False
        _append(blockers, "missing_live_review_readiness_certificate")
        _append(blockers, "live_review_certificate_not_review_ready")
    else:
        cert_status = str(_read_first(cert, ("certificate_status",), default=""))
        cert_completed = _to_bool(_read_first(cert, ("certificate_completed",), default=False), default=False)
        cert_human_ready = _to_bool(_read_first(cert, ("human_live_review_ready", "human_review_ready"), default=False), default=False)
        cert_trade_ready = _to_bool(_read_first(cert, ("live_micro_trade_review_ready",), default=False), default=False)
        if cert_status == LIVE_REVIEW_CERTIFICATE_REJECTED:
            _append(blockers, "live_review_certificate_rejected")
        elif cert_status != LIVE_REVIEW_CERTIFICATE_REVIEW_READY or not cert_completed or not cert_human_ready or not cert_trade_ready:
            _append(blockers, "live_review_certificate_not_review_ready")

    state_live_readiness_candidate, state_live_readiness_present = _read_optional_bool(
        state,
        ("live_readiness_candidate", "candidate_ready"),
    )
    if candidate_review is not None and candidate_review.get("verdict") == DEMO_REVIEW_READY:
        if state_live_readiness_present and not state_live_readiness_candidate:
            live_readiness_candidate = False
            _append(blockers, "missing_live_readiness_candidate")
        else:
            live_readiness_candidate = True
    else:
        live_readiness_candidate = bool(state_live_readiness_candidate)
        if not live_readiness_candidate:
            _append(blockers, "missing_live_readiness_candidate")

    human_review_ready = _to_bool(_read_first(state, ("human_live_review_ready", "human_review_ready"), default=False), default=False)
    if not human_review_ready:
        _append(blockers, "missing_human_review_ready")

    if human_review_ready and not (demo_status == DEMO_CONTRACT_COMPLETE and demo_completed and demo_candidate_ready):
        _append(blockers, "review_ready_without_demo_completion")
    if human_review_ready and not (
        one_shot_status == ONE_SHOT_EXCEPTION_REVIEW_READY and one_shot_completed and one_shot_review_ready
    ):
        _append(blockers, "review_ready_without_exception_package")
    if human_review_ready and not (
        cert_status == LIVE_REVIEW_CERTIFICATE_REVIEW_READY
        and cert_completed
        and cert_human_ready
        and cert_trade_ready
    ):
        _append(blockers, "review_ready_without_certificate")

    if cert_status == LIVE_REVIEW_CERTIFICATE_REVIEW_READY and demo_status != DEMO_CONTRACT_COMPLETE:
        _append(blockers, "cross_stage_status_conflict")
    if demo_status == DEMO_CONTRACT_COMPLETE and one_shot_status != ONE_SHOT_EXCEPTION_REVIEW_READY:
        _append(blockers, "cross_stage_status_conflict")

    broker_connection = _to_bool(_read_first(state, ("unsafe_broker_connection_detected", "broker_connection_detected", "broker_connection_active"), default=False), default=False)
    network_access = _to_bool(
        _read_first(state, ("unsafe_network_access_detected", "network_access", "network_access_detected"), default=False),
        default=False,
    )
    credential_access = _to_bool(
        _read_first(state, ("unsafe_credential_access_detected", "credential_access_detected", "credentials_accessed"), default=False),
        default=False,
    )
    account_access = _to_bool(
        _read_first(
            state,
            ("unsafe_account_identifier_access_detected", "account_identifier_access_detected", "account_identifiers_accessed"),
            default=False,
        ),
        default=False,
    )
    order_execution = _to_bool(
        _read_first(
            state,
            ("unsafe_order_execution_detected", "order_execution_enabled_detected", "order_execution_enabled"),
            default=False,
        ),
        default=False,
    )
    live_trading_auth = _to_bool(
        _read_first(
            state,
            ("live_trading_authorization_detected", "unsafe_live_trading_detected", "live_trading_authorized", "live_authorized"),
            default=False,
        ),
        default=False,
    )
    exec_authority = _to_bool(
        _read_first(
            state,
            ("execution_authority_detected", "execution_authority", "execution_authority_granted"),
            default=False,
        ),
        default=False,
    )
    capital_allocated = _to_bool(
        _read_first(
            state,
            ("unsafe_capital_allocation_detected", "capital_allocation_detected", "capital_allocation_modified", "capital_allocated"),
            default=False,
        ),
        default=False,
    )

    for flag, blocker in (
        (broker_connection, "broker_connection_active"),
        (network_access, "network_access_detected"),
        (credential_access, "credential_access_detected"),
        (account_access, "account_identifier_access_detected"),
        (order_execution, "order_execution_enabled_detected"),
        (live_trading_auth, "live_trading_authorization_detected"),
        (exec_authority, "execution_authority_detected"),
        (capital_allocated, "capital_allocation_detected"),
    ):
        if flag:
            _append(blockers, blocker)

    candidate_bridge_blocker: str | None = None
    candidate_bridge_incomplete = False
    if candidate_review is not None:
        candidate_verdict = candidate_review.get("verdict", "")
        if candidate_verdict == REJECTED:
            candidate_bridge_blocker = "candidate_demo_review_rejected"
        elif candidate_verdict == PAPER_CONTINUE:
            candidate_bridge_blocker = "candidate_demo_review_continue"
            candidate_bridge_incomplete = True
        elif candidate_verdict == BLOCKED_INCOMPLETE_EVIDENCE:
            candidate_bridge_blocker = "candidate_demo_review_incomplete_evidence"
            candidate_bridge_incomplete = True

    if any(blocker in blockers for blocker in ("demo_validation_contract_rejected", "one_shot_exception_package_rejected", "live_review_certificate_rejected")):
        review_status = REVIEW_CHAIN_REJECTED
    elif any(
        blocker in blockers
        for blocker in (
            "broker_connection_active",
            "network_access_detected",
            "credential_access_detected",
            "account_identifier_access_detected",
            "order_execution_enabled_detected",
            "live_trading_authorization_detected",
            "execution_authority_detected",
            "capital_allocation_detected",
        )
    ):
        review_status = REVIEW_CHAIN_BLOCKED
    elif candidate_bridge_blocker == "candidate_demo_review_rejected":
        review_status = REVIEW_CHAIN_REJECTED
    elif candidate_bridge_blocker in {"candidate_demo_review_continue", "candidate_demo_review_incomplete_evidence"}:
        review_status = REVIEW_CHAIN_INCOMPLETE
    elif any(
        blocker in blockers
        for blocker in (
            "missing_demo_validation_contract",
            "demo_validation_contract_not_complete",
            "missing_one_shot_exception_package",
            "one_shot_exception_package_not_review_ready",
            "missing_live_review_readiness_certificate",
            "live_review_certificate_not_review_ready",
            "missing_live_readiness_candidate",
            "missing_human_review_ready",
            "review_ready_without_demo_completion",
            "review_ready_without_exception_package",
            "review_ready_without_certificate",
            "cross_stage_status_conflict",
        )
    ):
        review_status = REVIEW_CHAIN_INCOMPLETE
    else:
        review_status = REVIEW_CHAIN_REVIEW_READY

    if candidate_bridge_blocker is not None:
        _append(blockers, candidate_bridge_blocker)
        if candidate_bridge_incomplete:
            _append(blockers, "candidate_demo_review_blocked")

    chain_ready = review_status == REVIEW_CHAIN_REVIEW_READY
    next_safe_action, required_next_packets = _next_action_and_packets(review_status)

    one_shot_controls = _as_map(_read_first(state, ("one_shot_controls",), default={})) or {}
    cert_safety = _as_map(_read_first(cert or {}, ("safety",), default={})) or {}

    safety = {
        "broker_connection_active": bool(broker_connection),
        "network_access": bool(network_access),
        "credentials_accessed": bool(credential_access),
        "account_identifiers_accessed": bool(account_access),
        "order_execution_enabled": bool(order_execution),
        "live_trading_authorized": False,
        "execution_authority_granted": False,
        "capital_allocated": bool(capital_allocated),
        "operator_review_required": True,
        "review_chain_only": True,
        "one_shot_only": bool(_to_bool(_read_first(one_shot_controls, ("one_shot_only",), default=True), default=True)),
        "no_retry_loop": bool(_to_bool(_read_first(one_shot_controls, ("no_retry_loop",), default=True), default=True)),
        "no_autonomous_reentry": bool(_to_bool(_read_first(one_shot_controls, ("no_autonomous_reentry",), default=True), default=True)),
        "manual_arming_required": bool(_to_bool(_read_first(one_shot_controls, ("manual_arming_required",), default=True), default=True)),
        "final_disarm_required": bool(_to_bool(_read_first(cert_safety, ("final_disarm_required",), default=True), default=True)),
    }

    return {
        "review_chain_completed": review_status in {REVIEW_CHAIN_REVIEW_READY, REVIEW_CHAIN_REJECTED, REVIEW_CHAIN_BLOCKED},
        "review_chain_status": review_status,
        "human_live_review_ready": bool(chain_ready),
        "live_micro_trade_review_ready": bool(chain_ready),
        "live_trading_authorized": False,
        "blockers": blockers,
        "warnings": warnings,
        "next_safe_action": next_safe_action,
        "required_next_packets": required_next_packets,
        "chain_summary": {
            "demo_status": demo_status,
            "one_shot_status": one_shot_status,
            "certificate_status": cert_status,
            "cross_stage_conflict": bool("cross_stage_status_conflict" in blockers),
            "candidate_demo_review": {
                "present": candidate_review is not None,
                "verdict": candidate_review.get("verdict", "") if candidate_review else "",
                "selected_candidate_id": candidate_review.get("selected_candidate_id", "") if candidate_review else "",
                "selected_strategy": candidate_review.get("selected_strategy", "") if candidate_review else "",
                "selected_direction": candidate_review.get("selected_direction", "") if candidate_review else "",
            },
        },
        "stage_summary": {
            "demo": {"present": demo is not None, "completed": demo_completed, "status": demo_status},
            "one_shot": {"present": one_shot is not None, "completed": one_shot_completed, "status": one_shot_status},
            "certificate": {"present": cert is not None, "completed": cert_completed, "status": cert_status},
            "candidate_demo_review": {
                "present": candidate_review is not None,
                "verdict": candidate_review.get("verdict", "") if candidate_review else "",
                "blockers": list(candidate_review.get("blockers", [])) if candidate_review else [],
            },
        },
        "readiness_summary": {
            "review_ready": chain_ready,
            "demo_ready": demo_status == DEMO_CONTRACT_COMPLETE and demo_completed,
            "one_shot_ready": one_shot_status == ONE_SHOT_EXCEPTION_REVIEW_READY and one_shot_completed and one_shot_review_ready,
            "certificate_ready": cert_status == LIVE_REVIEW_CERTIFICATE_REVIEW_READY and cert_completed and cert_human_ready and cert_trade_ready,
            "live_readiness_candidate": live_readiness_candidate,
            "human_review_ready": human_review_ready,
            "candidate_demo_review_ready": candidate_review is not None and candidate_review.get("verdict") == DEMO_REVIEW_READY,
            "candidate_demo_review_continue": candidate_bridge_incomplete,
            "candidate_demo_review_rejected": candidate_review is not None and candidate_review.get("verdict") == REJECTED,
            "candidate_demo_review_incomplete_evidence": candidate_review is not None
            and candidate_review.get("verdict") == BLOCKED_INCOMPLETE_EVIDENCE,
            "candidate_demo_review_blocker": candidate_bridge_blocker,
            "selected_candidate_id": candidate_review.get("selected_candidate_id", "") if candidate_review else "",
            "selected_strategy": candidate_review.get("selected_strategy", "") if candidate_review else "",
            "selected_direction": candidate_review.get("selected_direction", "") if candidate_review else "",
        },
        "safety": safety,
    }
