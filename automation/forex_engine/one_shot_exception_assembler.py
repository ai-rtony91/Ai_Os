from __future__ import annotations

from typing import Any, Iterable, Mapping


ONE_SHOT_EXCEPTION_BLOCKED = "ONE_SHOT_EXCEPTION_BLOCKED"
ONE_SHOT_EXCEPTION_INCOMPLETE = "ONE_SHOT_EXCEPTION_INCOMPLETE"
ONE_SHOT_EXCEPTION_REVIEW_READY = "ONE_SHOT_EXCEPTION_REVIEW_READY"
ONE_SHOT_EXCEPTION_REJECTED = "ONE_SHOT_EXCEPTION_REJECTED"

DEMO_CONTRACT_COMPLETE = "DEMO_CONTRACT_COMPLETE"
DEMO_CONTRACT_REJECTED = "DEMO_CONTRACT_REJECTED"


def _to_bool(value: Any, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"1", "true", "yes", "on", "pass", "passed", "ok", "active"}:
        return True
    if text in {"0", "false", "no", "off", "fail", "failed", "not", "inactive"}:
        return False
    return bool(text)


def _to_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _read_first(mapping: Mapping[str, Any], keys: Iterable[str], default: Any = None) -> Any:
    for key in keys:
        if key in mapping:
            return mapping[key]
    return default


def _read_metric(mapping: Mapping[str, Any], aliases: Iterable[str], default: Any = None) -> Any:
    return _read_first(mapping, aliases, default)


def _to_list(value: Any) -> list[Mapping[str, Any]]:
    if isinstance(value, list):
        return [entry for entry in value if isinstance(entry, Mapping)]
    return []


def _safe_false(value: Any) -> bool:
    return _to_bool(value, default=False)


def _required_blocked(*, blocker: str, target: list[str], blockers: list[str], hard: bool = False) -> None:
    if blocker not in target:
        target.append(blocker)


def _read_domain(state: Mapping[str, Any], aliases: Iterable[str]) -> Mapping[str, Any] | None:
    value = _read_first(state, aliases, default=None)
    if isinstance(value, Mapping):
        return value
    return None


def _read_risk_limit(state: Mapping[str, Any]) -> tuple[dict[str, Any], list[str], bool]:
    blockers: list[str] = []
    completed = True
    block_hard = False

    maximum_loss = _to_float(
        _read_metric(state, ("maximum_loss", "max_loss", "max_drawdown_cap"), default=None),
        default=-1.0,
    )
    daily_loss_cap = _to_float(_read_metric(state, ("daily_loss_cap", "daily_cap", "daily_loss_limit"), default=None), default=-1.0)
    stop_loss = _to_float(_read_metric(state, ("stop_loss", "stop_loss_pct", "stop_loss_limit"), default=None), default=-1.0)
    order_type = _read_metric(state, ("order_type", "order_type_allowed"), default=None)
    units_or_notional_limit = _to_float(
        _read_metric(state, ("units_or_notional_limit", "max_units", "max_notional", "notional_limit"), default=None),
        default=-1.0,
    )

    if maximum_loss < 0:
        blockers.append("missing_maximum_loss")
        completed = False
    if daily_loss_cap < 0:
        blockers.append("missing_daily_loss_cap")
        completed = False
    if stop_loss < 0:
        blockers.append("missing_stop_loss")
        completed = False
    if not any(alias in state for alias in ("order_type", "order_type_allowed")):
        blockers.append("missing_order_type")
        completed = False
    elif not _to_bool(order_type, default=False):
        blockers.append("missing_order_type")
        completed = False
    if units_or_notional_limit < 0:
        blockers.append("missing_units_or_notional_limit")
        completed = False

    return {
        "maximum_loss": maximum_loss,
        "daily_loss_cap": daily_loss_cap,
        "stop_loss": stop_loss,
        "order_type": order_type,
        "units_or_notional_limit": units_or_notional_limit,
    }, blockers, completed


def _read_controls(state: Mapping[str, Any]) -> tuple[list[str], bool]:
    blockers: list[str] = []
    completed = True

    required = {
        "one_order_only": _to_bool(_read_metric(state, ("one_order_only",), default=None), default=None),
        "no_retry_loop": _to_bool(_read_metric(state, ("no_retry_loop",), default=None), default=None),
        "no_autonomous_reentry": _to_bool(_read_metric(state, ("no_autonomous_reentry",), default=None), default=None),
        "manual_arming_required": _to_bool(_read_metric(state, ("manual_arming_required",), default=None), default=None),
        "timeout_required": _to_bool(_read_metric(state, ("timeout_required",), default=None), default=None),
        "final_disarm_required": _to_bool(_read_metric(state, ("final_disarm_required",), default=None), default=None),
        "operator_review_required": _to_bool(
            _read_metric(state, ("operator_review_required",), default=True),
            default=True,
        ),
    }

    missing_flags = [key for key, value in required.items() if not value]
    if missing_flags:
        completed = False
        blockers.append("missing_one_shot_controls")
        for key in missing_flags:
            if key not in ("operator_review_required",):
                blockers.append(f"missing_{key}")

    return blockers, completed


def _read_evidence_freshness(state: Mapping[str, Any], max_age_minutes: float) -> tuple[bool, list[str]]:
    blockers: list[str] = []
    evidence_fresh = _to_bool(_read_metric(state, ("evidence_fresh", "fresh", "is_fresh"), default=None), default=None)
    if evidence_fresh is None:
        age = _to_float(_read_metric(state, ("evidence_age_minutes", "age_minutes"), default=None), default=float("inf"))
        if age <= max_age_minutes:
            evidence_fresh = True
        else:
            evidence_fresh = False
    if not evidence_fresh:
        blockers.append("missing_evidence_freshness")
    return evidence_fresh, blockers


def _safe_status_from_blockers(blockers: list[str], status_map: dict[str, list[str]]) -> str:
    for status, keys in status_map.items():
        if any(key in blockers for key in keys):
            return status
    return ONE_SHOT_EXCEPTION_REVIEW_READY


def assemble_one_shot_exception_package(
    state: Mapping[str, Any],
    optional_limits: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    state = state or {}
    limits = optional_limits or {}
    maximum_evidence_age_minutes = _to_float(
        _read_metric(limits, ("maximum_evidence_age_minutes", "maximum_age_minutes"), default=60),
        default=60,
    )

    blockers: list[str] = []
    warnings: list[str] = []

    unsafe_broker = _to_bool(_read_metric(state, ("unsafe_broker_connection_detected", "broker_connection_detected", "broker_connection_active"), default=False), default=False)
    unsafe_network = _to_bool(_read_metric(state, ("unsafe_network_access_detected", "network_access", "network_access_detected"), default=False), default=False)
    unsafe_credentials = _to_bool(_read_metric(state, ("unsafe_credential_access_detected", "credential_access_detected", "credentials_accessed"), default=False), default=False)
    unsafe_account = _to_bool(_read_metric(state, ("unsafe_account_identifier_access_detected", "account_identifier_detected", "account_identifiers_accessed"), default=False), default=False)
    unsafe_order = _to_bool(_read_metric(state, ("unsafe_order_execution_detected", "order_execution_detected", "order_execution_enabled"), default=False), default=False)
    unsafe_live = _to_bool(_read_metric(state, ("unsafe_live_trading_detected", "live_trading_authorized", "live_trading_detected"), default=False), default=False)
    unsafe_capital_allocation = _to_bool(
        _read_metric(state, ("unsafe_capital_allocation_detected", "capital_allocation_modified", "capital_allocation_active"), default=False),
        default=False,
    )

    retry_detected = _to_bool(_read_metric(state, ("retry_loop_detected", "retry_loop", "one_shot_no_retry"), default=False), default=False)
    autonomous_detected = _to_bool(_read_metric(state, ("autonomous_reentry_detected", "autonomous_reentry", "auto_reentry"), default=False), default=False)

    if unsafe_broker:
        blockers.append("unsafe_broker_connection_detected")
    if unsafe_network:
        blockers.append("unsafe_network_access_detected")
    if unsafe_credentials:
        blockers.append("unsafe_credential_access_detected")
    if unsafe_account:
        blockers.append("unsafe_account_identifier_access_detected")
    if unsafe_order:
        blockers.append("unsafe_order_execution_detected")
    if unsafe_live:
        blockers.append("unsafe_live_trading_detected")
    if unsafe_capital_allocation:
        blockers.append("unsafe_capital_allocation_detected")
    if retry_detected:
        blockers.append("retry_loop_detected")
    if autonomous_detected:
        blockers.append("autonomous_reentry_detected")

    demo_contract = _read_domain(
        state,
        ("demo_validation_contract", "demo_validation_contract_result", "contract"),
    )
    if demo_contract is None:
        blockers.append("missing_demo_validation_contract")
    else:
        contract_status = _read_metric(
            demo_contract,
            ("demo_validation_contract_status", "status", "contract_status"),
            default="",
        )
        if not contract_status:
            blockers.append("demo_contract_not_complete")
        if contract_status != DEMO_CONTRACT_COMPLETE and contract_status != "":
            blockers.append("demo_contract_not_complete")

        contract_metrics = _read_domain(demo_contract, ("metric_summary",)) or {}
        expectancy = _to_float(_read_metric(contract_metrics, ("validation_expectancy", "expectancy"), default=0.0), default=0.0)
        if expectancy < 0:
            blockers.append("negative_expectancy")
        if contract_status == DEMO_CONTRACT_REJECTED:
            blockers.append("demo_validation_rejected")

    live_readiness = _read_domain(
        state,
        ("live_readiness_candidate", "live_readiness", "live_readiness_state"),
    )
    if live_readiness is None:
        blockers.append("missing_live_readiness_candidate")
    elif not _to_bool(_read_metric(live_readiness, ("live_readiness_candidate", "ready", "approved"), default=False), default=False):
        blockers.append("live_readiness_candidate_not_ready")

    approval_trace = _read_domain(state, ("approval_trace", "approval"))
    if approval_trace is None:
        blockers.append("missing_approval_trace")
    else:
        approval_window_active = _to_bool(
            _read_metric(
                approval_trace,
                ("approval_window_active",),
                default=None,
            ),
            default=None,
        )
        approval_window_status = str(
            _read_metric(approval_trace, ("approval_window_status",), default=""),
        ).upper()
        if approval_window_active is None and approval_window_status != "ACTIVE":
            blockers.append("missing_approval_window")
        elif approval_window_status != "ACTIVE" and not _to_bool(approval_window_active, default=False):
            blockers.append("approval_window_expired")

    risk_limits = _read_domain(state, ("risk_limits", "risk_controls", "risk"))
    if risk_limits is None:
        blockers.append("missing_risk_limits")
    else:
        limits_summary, risk_blockers, risk_complete = _read_risk_limit(risk_limits)
        if not risk_complete:
            blockers.extend(risk_blockers)

    proof_domains = [
        ("kill_switch_proof", "missing_kill_switch_proof"),
        ("rollback_proof", "missing_rollback_proof"),
        ("reconciliation_proof", "missing_reconciliation_proof"),
        ("external_runtime_connector_proof", "missing_external_runtime_connector_proof"),
        ("credential_boundary_proof", "missing_credential_boundary_proof"),
        ("account_boundary_proof", "missing_account_boundary_proof"),
        ("replayability_proof", "missing_replayability_proof"),
        ("final_disarm_proof", "missing_final_disarm_proof"),
    ]
    for domain_name, blocker_name in proof_domains:
        proof = _read_domain(state, (domain_name,))
        if proof is None:
            blockers.append(blocker_name)
        elif not _to_bool(_read_metric(proof, ("present", "available", "verified"), default=False), default=False):
            blockers.append(blocker_name)

    controls = _read_domain(state, ("one_shot_controls",))
    if controls is None:
        blockers.append("missing_one_shot_controls")
        control_summary = {}
    else:
        control_blockers, controls_complete = _read_controls(controls)
        blockers.extend(control_blockers)
        control_summary = controls

    evidence_freshness = _read_domain(state, ("evidence_freshness",))
    if evidence_freshness is None:
        blockers.append("missing_evidence_freshness")
        freshness_ok = False
    else:
        freshness_ok, freshness_blockers = _read_evidence_freshness(evidence_freshness, maximum_evidence_age_minutes)
        blockers.extend(freshness_blockers)

    post_trade_journal_path = _read_metric(state, ("post_trade_journal_path", "journal_path", "post_trade_path"), default="")
    if not post_trade_journal_path:
        blockers.append("missing_post_trade_journal_path")

    if not _to_bool(_read_metric(demo_contract or {}, ("live_readiness_candidate", "ready"), default=True), default=True):
        blockers.append("demo_contract_not_complete")

    soft_blockers = {
        "demo_contract_not_complete",
        "missing_risk_limits",
        "missing_maximum_loss",
        "missing_daily_loss_cap",
        "missing_stop_loss",
        "missing_order_type",
        "missing_units_or_notional_limit",
        "missing_approval_window",
        "missing_kill_switch_proof",
        "missing_rollback_proof",
        "missing_reconciliation_proof",
        "missing_external_runtime_connector_proof",
        "missing_credential_boundary_proof",
        "missing_account_boundary_proof",
        "missing_one_shot_controls",
        "missing_evidence_freshness",
        "missing_replayability_proof",
        "missing_final_disarm_proof",
        "missing_post_trade_journal_path",
        "live_readiness_candidate_not_ready",
        "missing_live_readiness_candidate",
    }
    hard_blockers = {
        "unsafe_broker_connection_detected",
        "unsafe_network_access_detected",
        "unsafe_credential_access_detected",
        "unsafe_account_identifier_access_detected",
        "unsafe_order_execution_detected",
        "unsafe_live_trading_detected",
        "unsafe_capital_allocation_detected",
        "retry_loop_detected",
        "autonomous_reentry_detected",
        "approval_window_expired",
        "missing_live_readiness_candidate",
        "missing_demo_validation_contract",
        "missing_approval_trace",
        "demo_validation_rejected",
        "negative_expectancy",
    }

    rejected = bool({"demo_validation_rejected", "negative_expectancy"}.intersection(blockers))
    critical_missing = {
        "missing_demo_validation_contract",
        "missing_live_readiness_candidate",
        "missing_approval_trace",
    }
    blocked = bool({"unsafe_broker_connection_detected", "unsafe_network_access_detected", "unsafe_credential_access_detected", "unsafe_account_identifier_access_detected", "unsafe_order_execution_detected", "unsafe_live_trading_detected", "unsafe_capital_allocation_detected", "retry_loop_detected", "autonomous_reentry_detected", "approval_window_expired"}.intersection(blockers))
    blocked = blocked or bool(critical_missing.intersection(blockers))
    incomplete = not blocked and bool(blockers)

    if rejected:
        status = ONE_SHOT_EXCEPTION_REJECTED
        completed = True
        live_ready = False
    elif blocked:
        status = ONE_SHOT_EXCEPTION_BLOCKED
        completed = True
        live_ready = False
    elif incomplete:
        status = ONE_SHOT_EXCEPTION_INCOMPLETE
        completed = False
        live_ready = False
    else:
        status = ONE_SHOT_EXCEPTION_REVIEW_READY
        completed = True
        live_ready = True

    status_to_next_action = {
        ONE_SHOT_EXCEPTION_INCOMPLETE: "collect_missing_proofs",
        ONE_SHOT_EXCEPTION_BLOCKED: "resolve_blockers_before_review",
        ONE_SHOT_EXCEPTION_REJECTED: "rework_demo_performance_and_risk",
        ONE_SHOT_EXCEPTION_REVIEW_READY: "submit_for_manual_one_shot_review",
    }
    next_safe_action = status_to_next_action[status]

    if status == ONE_SHOT_EXCEPTION_REVIEW_READY:
        required_next_packets = ["prepare_review_package", "request_exception_review", "final_signoff"]
    elif status == ONE_SHOT_EXCEPTION_REJECTED:
        required_next_packets = ["rebuild_demo_validation", "repair_profitability", "restart_one_shot_evidence"]
    elif status == ONE_SHOT_EXCEPTION_BLOCKED:
        required_next_packets = [
            "clear_unsafe_conditions",
            "revalidate_evidence_inputs",
            "restore_authorization_controls",
        ]
    else:
        required_next_packets = [
            "collect_missing_proof_inputs",
            "refresh_evidence_freshness",
            "refresh_risk_and_replay_controls",
        ]

    required_next_packets = list(dict.fromkeys(required_next_packets))

    return {
        "exception_package_completed": completed,
        "exception_package_status": status,
        "live_micro_trade_review_ready": live_ready,
        "blockers": blockers,
        "warnings": warnings,
        "next_safe_action": next_safe_action,
        "required_next_packets": required_next_packets,
        "package_summary": {
            "status": status,
            "maximum_evidence_age_minutes": maximum_evidence_age_minutes,
            "control_summary": control_summary if controls is not None else {},
        },
        "proof_summary": {
            "kill_switch_present": _to_bool(_read_metric(state, ("kill_switch_proof",), default=False), default=False),
            "rollback_present": _to_bool(_read_metric(state, ("rollback_proof",), default=False), default=False),
            "reconciliation_present": _to_bool(_read_metric(state, ("reconciliation_proof",), default=False), default=False),
            "evidence_freshness_ok": freshness_ok,
        },
        "risk_summary": {
            "risk_limits": risk_limits or {},
            "maximum_loss": _to_float(_read_metric(risk_limits or {}, ("maximum_loss", "max_loss"), default=-1.0), default=-1.0),
            "daily_loss_cap": _to_float(_read_metric(risk_limits or {}, ("daily_loss_cap", "daily_cap"), default=-1.0), default=-1.0),
            "stop_loss": _to_float(_read_metric(risk_limits or {}, ("stop_loss", "stop_loss_pct"), default=-1.0), default=-1.0),
            "order_type": _read_metric(risk_limits or {}, ("order_type",), default=""),
            "units_or_notional_limit": _to_float(
                _read_metric(risk_limits or {}, ("units_or_notional_limit", "max_units"), default=-1.0),
                default=-1.0,
            ),
        },
        "safety": {
            "broker_connection_active": unsafe_broker,
            "network_access": unsafe_network,
            "credentials_accessed": unsafe_credentials,
            "account_identifiers_accessed": unsafe_account,
            "order_execution_enabled": False,
            "live_trading_authorized": False,
            "capital_allocated": False,
            "operator_review_required": True,
            "one_shot_only": True,
            "no_retry_loop": False if retry_detected else True,
            "no_autonomous_reentry": False if autonomous_detected else True,
            "manual_arming_required": bool(_to_bool(_read_metric(control_summary, ("manual_arming_required",), default=True), default=True)),
            "final_disarm_required": bool(_to_bool(_read_metric(control_summary, ("final_disarm_required",), default=True), default=True)),
        },
    }
