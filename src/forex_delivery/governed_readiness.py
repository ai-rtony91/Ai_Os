"""Governed Forex Delivery readiness and fail-closed live arming checks.

This module intentionally stays local and deterministic. It models the repo-side
paper flow needed before a future Single Live Micro-Trade Exception review, but
it never connects to a broker, reads credentials, uses network APIs, or submits
orders.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from automation.forex_engine.broker_specific_paper_demo import (
    build_broker_specific_paper_demo_mapping_set,
    default_broker_specific_paper_demo_config,
)
from automation.forex_engine.oanda_demo_auth_handoff import (
    build_oanda_demo_auth_contract_set,
    evaluate_oanda_demo_auth_handoff_readiness,
)
from automation.forex_engine.oanda_demo_connection_gate import (
    build_oanda_demo_connection_gate_contract_set,
    evaluate_oanda_demo_connection_gate,
)
from automation.forex_engine.oanda_demo_protected_connection_attempt import (
    build_oanda_demo_protected_connection_attempt_contract_set,
    run_oanda_demo_protected_connection_attempt,
)
from automation.forex_engine.oanda_demo_runtime_handoff_intake import (
    build_oanda_demo_runtime_handoff_intake_contract_set,
    evaluate_oanda_demo_runtime_handoff_intake,
)
from automation.forex_engine.oanda_demo_runtime_handoff import (
    AUTH_MATERIAL_LOCATION as OANDA_RUNTIME_AUTH_MATERIAL_LOCATION,
    AUTH_REFERENCE_FORMAT as OANDA_RUNTIME_AUTH_REFERENCE_FORMAT,
    HANDOFF_MODE as OANDA_RUNTIME_HANDOFF_MODE,
    HANDOFF_SCOPE as OANDA_RUNTIME_HANDOFF_SCOPE,
    build_oanda_demo_runtime_handoff_contract_set,
    evaluate_oanda_demo_runtime_handoff,
)
from automation.forex_engine.paper_demo_broker_adapter import (
    PaperDemoBrokerAdapter,
    build_paper_demo_broker_adapter_contract,
)


REQUIRED_EXCEPTION_FIELDS = (
    "broker_path",
    "instrument",
    "side",
    "units_or_notional_limit",
    "maximum_loss",
    "daily_loss_cap",
    "stop_loss",
    "order_type",
    "approval_window",
    "evidence_bundle_path",
    "arming_step",
    "stop_point",
    "human_owner_approval",
    "timestamp",
    "account_mode",
    "paper_live_mode_confirmation",
    "one_order_only",
    "no_retry_loop",
    "no_autonomous_reentry",
    "kill_switch_confirmed",
    "timeout_confirmed",
    "final_disarm_confirmed",
    "rollback_plan_confirmed",
    "post_trade_journal_path",
    "reconciliation_proof",
    "evidence_bundle_complete",
    "demo_or_practice_broker_proof",
    "credential_boundary_confirmed",
    "account_id_boundary_confirmed",
    "live_endpoint_denial_confirmed",
)

LIVE_ARMING_BOOLEAN_GATES = (
    "one_order_only",
    "no_retry_loop",
    "no_autonomous_reentry",
    "kill_switch_confirmed",
    "timeout_confirmed",
    "final_disarm_confirmed",
    "rollback_plan_confirmed",
    "reconciliation_proof",
    "evidence_bundle_complete",
    "demo_or_practice_broker_proof",
    "credential_boundary_confirmed",
    "account_id_boundary_confirmed",
    "live_endpoint_denial_confirmed",
)

LIVE_ARMING_SAFE_TEXT_GATES = (
    "broker_path",
    "instrument",
    "side",
    "units_or_notional_limit",
    "maximum_loss",
    "daily_loss_cap",
    "stop_loss",
    "order_type",
    "approval_window",
    "evidence_bundle_path",
    "arming_step",
    "stop_point",
    "human_owner_approval",
    "timestamp",
    "account_mode",
    "paper_live_mode_confirmation",
    "post_trade_journal_path",
)

DEMO_RUNTIME_REQUIRED_FIELDS = (
    "broker_family_label",
    "practice_demo_mode_confirmed",
    "runtime_auth_reference_label",
    "external_connector_readiness_flag",
    "network_approval_status",
    "account_identifier_status",
    "endpoint_class",
    "no_order_route_approval",
    "no_live_endpoint",
    "no_credential_value",
    "no_account_id_value",
    "timeout_seconds",
    "one_shot_stop_requirement",
    "evidence_bundle_path",
    "human_owner_approval_future_proof",
)

DEMO_RUNTIME_ALLOWED_BROKER_FAMILY_LABELS = (
    "OANDA_PRACTICE",
    "OANDA_PRACTICE_DEMO",
)

DEMO_RUNTIME_ALLOWED_ENDPOINT_CLASSES = (
    "OANDA_PRACTICE",
    "OANDA_PRACTICE_DEMO",
    "PRACTICE_REFERENCE_ONLY",
)

DEMO_RUNTIME_ACCOUNT_IDENTIFIER_STATUSES = (
    "ABSENT",
    "SANITIZED",
)

UNSAFE_REVIEW_MARKERS = (
    "todo",
    "tbd",
    "placeholder",
    "unknown",
    "ambiguous",
    "expired",
    "unsafe",
)

UNSAFE_TRUE_FLAGS = {
    "retry_loop": "retry_loop_must_not_be_enabled",
    "autonomous_reentry": "autonomous_reentry_must_not_be_enabled",
    "scheduler_enabled": "scheduler_must_not_be_enabled",
    "daemon_enabled": "daemon_must_not_be_enabled",
    "order_route_enabled": "order_route_must_not_be_enabled",
    "trade_route_enabled": "trade_route_must_not_be_enabled",
    "live_endpoint_enabled": "live_endpoint_must_not_be_enabled",
}

CHAIN_LINKS = (
    "BROKER CONNECT",
    "AUTHENTICATION",
    "OANDA DEMO AUTH HANDOFF READINESS",
    "OANDA DEMO RUNTIME HANDOFF INTAKE",
    "OANDA DEMO RUNTIME HANDOFF",
    "OANDA DEMO CONNECTION GATE",
    "OANDA PROTECTED DEMO CONNECTION ATTEMPT",
    "MARKET DATA",
    "ACCOUNT STATE",
    "RISK CHECK",
    "ORDER BUILD",
    "PAPER EXECUTION",
    "FILL VERIFY",
    "POSITION MONITOR",
    "POSITION CLOSE",
    "EVIDENCE LOG",
    "LIVE MICRO-TRADE ARMING CHECKLIST",
)

FORBIDDEN_LIVE_FIELDS = {
    "credentials",
    "credential",
    "token",
    "tokens",
    "api_key",
    "apikey",
    "password",
    "secret",
    "account_id",
    "account_identifier",
    "broker_order_identifier",
    "broker_order_id",
    "raw_broker_payload",
    "raw_live_payload",
    "broker_payload",
    "live_payload",
    "private_account_data",
    "endpoint_value",
    "endpoint_url",
    "live_endpoint_value",
    "live_endpoint_url",
}

FORBIDDEN_LIVE_FIELD_MARKERS = (
    "credential",
    "api_key",
    "apikey",
    "token",
    "password",
    "secret",
    "private_key",
    "account_id",
    "account_identifier",
    "broker_order_id",
    "broker_order_identifier",
    "raw_broker_payload",
    "raw_live_payload",
    "broker_payload",
    "live_payload",
    "private_account_data",
)

FORBIDDEN_VALUE_MARKERS = (
    "sk-",
    "bearer ",
    "authorization:",
    "begin private key",
    "api_key=",
    "apikey=",
    "password=",
    "token=",
    "secret=",
)


class LiveExecutionBlocked(RuntimeError):
    """Raised whenever a caller attempts live execution from this package."""


@dataclass(frozen=True)
class ForexDeliveryPolicy:
    allowed_pairs: tuple[str, ...] = ("EUR_USD", "GBP_USD", "USD_JPY")
    max_spread_pips: float = 1.5
    available_margin_usd: float = 1000.0
    margin_per_unit_usd: float = 0.02
    max_units: int = 1
    max_loss_usd: float = 1.0
    require_take_profit: bool = False
    paper_price_by_pair: dict[str, float] = field(
        default_factory=lambda: {
            "EUR_USD": 1.08,
            "GBP_USD": 1.27,
            "USD_JPY": 155.0,
        }
    )


DEFAULT_POLICY = ForexDeliveryPolicy()


def run_governed_paper_flow(
    order_request: dict[str, Any] | None = None,
    auth_handoff: dict[str, Any] | None = None,
    runtime_handoff_intake: dict[str, Any] | None = None,
    runtime_handoff: dict[str, Any] | None = None,
    connection_gate_approval: dict[str, Any] | None = None,
    protected_connection_attempt_request: dict[str, Any] | None = None,
    *,
    policy: ForexDeliveryPolicy = DEFAULT_POLICY,
) -> dict[str, Any]:
    """Run the governed local paper flow and return sanitized evidence."""

    request = _default_order_request()
    if order_request:
        request.update(order_request)

    adapter = PaperDemoBrokerAdapter(
        starting_balance_usd=policy.available_margin_usd,
        available_margin_usd=policy.available_margin_usd,
        max_units=policy.max_units,
    )
    adapter_contract = build_paper_demo_broker_adapter_contract()
    auth_contracts = build_oanda_demo_auth_contract_set()
    runtime_handoff_intake_contracts = build_oanda_demo_runtime_handoff_intake_contract_set()
    runtime_handoff_contracts = build_oanda_demo_runtime_handoff_contract_set()
    connection_gate_contracts = build_oanda_demo_connection_gate_contract_set()
    protected_connection_attempt_contracts = (
        build_oanda_demo_protected_connection_attempt_contract_set()
    )
    broker_connect = adapter.connect()
    authentication = adapter.authenticate()
    auth_readiness = evaluate_oanda_demo_auth_handoff_readiness(auth_handoff)
    runtime_handoff_intake_readiness = evaluate_oanda_demo_runtime_handoff_intake(
        runtime_handoff_intake
    )
    runtime_handoff_readiness = evaluate_oanda_demo_runtime_handoff(runtime_handoff)
    connection_gate = evaluate_oanda_demo_connection_gate(connection_gate_approval)
    protected_connection_attempt = run_oanda_demo_protected_connection_attempt(
        protected_connection_attempt_request
    )
    market_data = adapter.get_market_data(request["instrument"])
    account_state = adapter.get_account_state()

    risk = validate_order_request(request, account_state=account_state, policy=policy)
    payload = build_order_payload(request, risk, policy=policy) if risk["risk_passed"] else None
    execution = adapter.create_order(payload) if payload else _blocked_execution(risk)
    fill = _verify_fill(execution)
    position_state = adapter.get_position_state()
    close = _close_adapter_position(adapter, execution, request, policy=policy)
    adapter_evidence = adapter.build_evidence_bundle()
    broker_specific_mapping = build_broker_specific_paper_demo_mapping_set(
        config=default_broker_specific_paper_demo_config(),
        account_state=account_state,
        market_data=market_data,
        order_state=execution,
        fill_state=dict(execution.get("fill") or {}),
        source_evidence=adapter_evidence,
    )
    evidence = _build_evidence_log(
        broker_connect=broker_connect,
        authentication=authentication,
        auth_readiness=auth_readiness,
        runtime_handoff_intake=runtime_handoff_intake_readiness,
        runtime_handoff=runtime_handoff_readiness,
        connection_gate=connection_gate,
        protected_connection_attempt=protected_connection_attempt,
        market_data=market_data,
        account_state=account_state,
        risk=risk,
        payload=payload,
        execution=execution,
        fill=fill,
        position_state=position_state,
        close=close,
        adapter_evidence=adapter_evidence,
        broker_specific_mapping=broker_specific_mapping,
    )
    final_report = _build_final_trade_report(evidence)
    arming = build_live_arming_checklist({})

    return {
        "schema": "AIOS_FOREX_DELIVERY_GOVERNED_READINESS.v1",
        "mode": "PAPER_ONLY",
        "chain_links": list(CHAIN_LINKS),
        "broker_adapter_contract": adapter_contract,
        "broker_adapter": {
            "adapter_name": adapter_contract["adapter_name"],
            "mode": adapter_contract["mode"],
            "paper_demo_only": True,
            "live_execution_allowed": False,
            "broker_sdk_allowed": False,
            "network_api_allowed": False,
            "credentials_allowed": False,
        },
        "oanda_demo_auth_contracts": auth_contracts,
        "oanda_demo_auth_readiness": auth_readiness,
        "oanda_demo_runtime_handoff_intake_contracts": runtime_handoff_intake_contracts,
        "oanda_demo_runtime_handoff_intake": runtime_handoff_intake_readiness,
        "oanda_demo_runtime_handoff_contracts": runtime_handoff_contracts,
        "oanda_demo_runtime_handoff": runtime_handoff_readiness,
        "oanda_demo_connection_gate_contracts": connection_gate_contracts,
        "oanda_demo_connection_gate": connection_gate,
        "oanda_demo_protected_connection_attempt_contracts": (
            protected_connection_attempt_contracts
        ),
        "oanda_demo_protected_connection_attempt": protected_connection_attempt,
        "broker_specific_integration": broker_specific_mapping,
        "broker_connect": broker_connect,
        "authentication": authentication,
        "market_data": market_data,
        "account_state": account_state,
        "risk_check": risk,
        "order_payload": payload,
        "paper_execution": execution,
        "fill_verify": fill,
        "position_state": position_state,
        "position_close": close,
        "evidence_log": evidence,
        "final_trade_report": final_report,
        "live_micro_trade_arming_checklist": arming,
        "live_order_placed": False,
        "real_credentials_added": False,
        "broker_request_sent": False,
        "network_used": False,
        "stop_point": (
            "Repo-side governed live micro-trade readiness packet complete; "
            "live order remains blocked until Human Owner activates the Single "
            "Live Micro-Trade Exception with all required RISK_POLICY.md fields."
        ),
    }


def validate_order_request(
    order_request: dict[str, Any],
    *,
    account_state: dict[str, Any] | None = None,
    policy: ForexDeliveryPolicy = DEFAULT_POLICY,
) -> dict[str, Any]:
    """Validate local paper order shape and risk controls."""

    request = dict(order_request)
    account = dict(account_state or {"available_margin_usd": policy.available_margin_usd})
    rejection_reasons: list[str] = []

    forbidden = _find_forbidden_fields(request)
    if forbidden:
        rejection_reasons.extend([f"forbidden_field:{field}" for field in forbidden])

    pair = _normalize_pair(request.get("instrument"))
    side = str(request.get("side") or "").upper()
    order_type = str(request.get("order_type") or "").upper()
    units = _int_or_none(request.get("units"))
    spread_pips = _float_or_none(request.get("spread_pips"))
    max_loss_usd = _float_or_none(request.get("max_loss_usd"))
    stop_loss = _float_or_none(request.get("stop_loss"))
    take_profit = _float_or_none(request.get("take_profit"))

    if pair not in policy.allowed_pairs:
        rejection_reasons.append("pair_not_allowlisted")
    if side not in {"BUY", "SELL"}:
        rejection_reasons.append("side_must_be_buy_or_sell")
    if order_type not in {"MARKET", "LIMIT", "STOP"}:
        rejection_reasons.append("order_type_not_supported")
    if units is None or units <= 0:
        rejection_reasons.append("units_must_be_positive")
    elif units > policy.max_units:
        rejection_reasons.append("position_size_exceeds_max_trade_size")
    if spread_pips is None:
        rejection_reasons.append("spread_required")
    elif spread_pips > policy.max_spread_pips:
        rejection_reasons.append("spread_exceeds_limit")
    if stop_loss is None or stop_loss <= 0:
        rejection_reasons.append("stop_loss_required")
    if max_loss_usd is None or max_loss_usd <= 0:
        rejection_reasons.append("max_loss_required")
    elif max_loss_usd > policy.max_loss_usd:
        rejection_reasons.append("max_loss_exceeds_guard")
    if policy.require_take_profit and (take_profit is None or take_profit <= 0):
        rejection_reasons.append("take_profit_required_by_config")
    if units is not None and units > 0:
        required_margin = units * policy.margin_per_unit_usd
        if required_margin > float(account.get("available_margin_usd", 0.0)):
            rejection_reasons.append("margin_check_failed")
    else:
        required_margin = 0.0

    return {
        "schema": "AIOS_FOREX_DELIVERY_RISK_CHECK.v1",
        "risk_passed": not rejection_reasons,
        "rejection_reasons": rejection_reasons,
        "instrument": pair,
        "side": side,
        "order_type": order_type,
        "units": units,
        "spread_pips": spread_pips,
        "required_margin_usd": required_margin,
        "available_margin_usd": account.get("available_margin_usd"),
        "max_loss_usd": max_loss_usd,
        "stop_loss": stop_loss,
        "take_profit": take_profit,
        "execution_allowed": False,
        "paper_only": True,
    }


def build_order_payload(
    order_request: dict[str, Any],
    risk_check: dict[str, Any],
    *,
    policy: ForexDeliveryPolicy = DEFAULT_POLICY,
) -> dict[str, Any]:
    """Build a paper-only order payload after risk validation."""

    if risk_check.get("risk_passed") is not True:
        raise ValueError("risk_check_must_pass_before_payload_build")
    pair = _normalize_pair(order_request.get("instrument"))
    price = policy.paper_price_by_pair[pair]
    return {
        "schema": "AIOS_FOREX_DELIVERY_PAPER_ORDER_PAYLOAD.v1",
        "client_order_id": "AIOS-PAPER-FOREX-DELIVERY-001",
        "instrument": pair,
        "side": str(order_request["side"]).upper(),
        "order_type": str(order_request["order_type"]).upper(),
        "units": int(order_request["units"]),
        "entry_reference_price": price,
        "stop_loss": float(order_request["stop_loss"]),
        "take_profit": _float_or_none(order_request.get("take_profit")),
        "max_loss_usd": float(order_request["max_loss_usd"]),
        "paper_only": True,
        "execution_allowed": False,
        "live_order": False,
        "broker_request_sent": False,
        "network_used": False,
    }


def build_live_arming_checklist(approval_fields: dict[str, Any]) -> dict[str, Any]:
    """Return the fail-closed live arming checklist state."""

    fields = dict(approval_fields or {})
    forbidden = _find_forbidden_fields(fields)
    missing = [
        field_name
        for field_name in REQUIRED_EXCEPTION_FIELDS
        if not _field_present(fields, field_name)
    ]
    blocker_reasons = [f"missing_required_field:{field}" for field in missing]
    blocker_reasons.extend([f"forbidden_field:{field}" for field in forbidden])
    passed_gates: list[str] = []
    failed_gates: list[str] = []

    if missing:
        failed_gates.append("required_exception_fields_present")
    else:
        passed_gates.append("required_exception_fields_present")

    if forbidden:
        failed_gates.append("no_forbidden_live_fields")
    else:
        passed_gates.append("no_forbidden_live_fields")

    if str(fields.get("paper_live_mode_confirmation") or "").upper() != "LIVE":
        blocker_reasons.append("paper_live_mode_confirmation_must_be_live_for_arming_review")
        failed_gates.append("paper_live_mode_confirmation")
    else:
        passed_gates.append("paper_live_mode_confirmation")
    if str(fields.get("account_mode") or "").upper() != "LIVE":
        blocker_reasons.append("account_mode_must_be_live_for_arming_review")
        failed_gates.append("account_mode")
    else:
        passed_gates.append("account_mode")
    if str(fields.get("human_owner_approval") or "") != "Anthony Meza":
        blocker_reasons.append("human_owner_approval_must_name_anthony_meza")
        failed_gates.append("human_owner_approval")
    else:
        passed_gates.append("human_owner_approval")

    for field_name in LIVE_ARMING_BOOLEAN_GATES:
        if _field_present(fields, field_name) and fields[field_name] is True:
            passed_gates.append(field_name)
        else:
            failed_gates.append(field_name)
            blocker_reasons.append(f"{field_name}_must_be_true")

    for field_name in LIVE_ARMING_SAFE_TEXT_GATES:
        if not _field_present(fields, field_name):
            continue
        unsafe_reasons = _unsafe_text_value_reasons(fields[field_name])
        if unsafe_reasons:
            failed_gates.append(field_name)
            blocker_reasons.extend(
                f"unsafe_or_ambiguous_field:{field_name}:{reason}"
                for reason in unsafe_reasons
            )
        elif field_name not in passed_gates:
            passed_gates.append(field_name)

    for field_name, reason in UNSAFE_TRUE_FLAGS.items():
        if fields.get(field_name) is True:
            failed_gates.append(field_name)
            blocker_reasons.append(reason)

    passed_gates = sorted(set(passed_gates))
    failed_gates = sorted(set(failed_gates))

    ready_for_human_review = not blocker_reasons
    next_required_action = (
        "human_owner_review_only_live_execution_remains_blocked"
        if ready_for_human_review
        else "complete_sanitized_live_arming_review_package"
    )
    return {
        "schema": "AIOS_FOREX_DELIVERY_LIVE_ARMING_CHECKLIST.v1",
        "ready_for_human_review": ready_for_human_review,
        "live_execution_allowed": False,
        "order_submit_allowed": False,
        "broker_request_sent": False,
        "network_used": False,
        "credential_material_present": False,
        "required_fields": list(REQUIRED_EXCEPTION_FIELDS),
        "missing_fields": missing,
        "passed_gates": passed_gates,
        "failed_gates": failed_gates,
        "blocker_reasons": sorted(set(blocker_reasons)),
        "next_required_action": next_required_action,
        "stop_point": (
            "Live order remains blocked until Human Owner activates the Single "
            "Live Micro-Trade Exception with all required RISK_POLICY.md fields."
        ),
    }


def build_demo_runtime_readiness_dry_run(readiness_fields: dict[str, Any]) -> dict[str, Any]:
    """Validate value-free demo/runtime readiness metadata without broker access."""

    fields = dict(readiness_fields or {})
    forbidden = _find_forbidden_fields(fields)
    missing = [
        field_name
        for field_name in DEMO_RUNTIME_REQUIRED_FIELDS
        if not _field_present(fields, field_name)
    ]
    blocker_reasons = [f"missing_required_field:{field}" for field in missing]
    blocker_reasons.extend([f"forbidden_field:{field}" for field in forbidden])
    passed_gates: list[str] = []
    failed_gates: list[str] = []

    if missing:
        failed_gates.append("required_demo_runtime_fields_present")
    else:
        passed_gates.append("required_demo_runtime_fields_present")

    if forbidden:
        failed_gates.append("no_forbidden_demo_runtime_fields")
    else:
        passed_gates.append("no_forbidden_demo_runtime_fields")

    broker_family = _normalize_demo_runtime_label(fields.get("broker_family_label"))
    endpoint_class = _normalize_demo_runtime_label(fields.get("endpoint_class"))
    account_identifier_status = _normalize_demo_runtime_label(
        fields.get("account_identifier_status")
    )
    timeout_seconds = _int_or_none(fields.get("timeout_seconds"))

    if broker_family in DEMO_RUNTIME_ALLOWED_BROKER_FAMILY_LABELS:
        passed_gates.append("broker_family_label")
    else:
        failed_gates.append("broker_family_label")
        blocker_reasons.append("broker_family_label_must_be_oanda_practice")

    if fields.get("practice_demo_mode_confirmed") is True:
        passed_gates.append("practice_demo_mode_confirmed")
    else:
        failed_gates.append("practice_demo_mode_confirmed")
        blocker_reasons.append("practice_demo_mode_confirmation_required")

    runtime_label_unsafe = _unsafe_text_value_reasons(
        fields.get("runtime_auth_reference_label")
    )
    if _field_present(fields, "runtime_auth_reference_label") and not runtime_label_unsafe:
        passed_gates.append("runtime_auth_reference_label")
    else:
        failed_gates.append("runtime_auth_reference_label")
        blocker_reasons.append("runtime_auth_reference_label_required")
        blocker_reasons.extend(
            f"unsafe_runtime_auth_reference_label:{reason}"
            for reason in runtime_label_unsafe
        )

    if fields.get("external_connector_readiness_flag") is True:
        passed_gates.append("external_connector_readiness_flag")
    else:
        failed_gates.append("external_connector_readiness_flag")
        blocker_reasons.append("external_connector_readiness_confirmation_required")

    if fields.get("network_approval_status") is False:
        passed_gates.append("network_approval_status")
    else:
        failed_gates.append("network_approval_status")
        blocker_reasons.append("network_approval_status_must_remain_false_for_dry_run")

    if account_identifier_status in DEMO_RUNTIME_ACCOUNT_IDENTIFIER_STATUSES:
        passed_gates.append("account_identifier_status")
    else:
        failed_gates.append("account_identifier_status")
        blocker_reasons.append("account_identifier_status_must_be_absent_or_sanitized")

    if endpoint_class in DEMO_RUNTIME_ALLOWED_ENDPOINT_CLASSES and "LIVE" not in endpoint_class:
        passed_gates.append("endpoint_class")
    else:
        failed_gates.append("endpoint_class")
        blocker_reasons.append("endpoint_class_must_be_demo_or_practice_only")

    for field_name, reason in (
        ("no_order_route_approval", "order_route_approval_must_be_absent"),
        ("no_live_endpoint", "live_endpoint_must_be_absent"),
        ("no_credential_value", "credential_value_must_be_absent"),
        ("no_account_id_value", "account_id_value_must_be_absent"),
        ("one_shot_stop_requirement", "one_shot_stop_requirement_must_be_confirmed"),
    ):
        if fields.get(field_name) is True:
            passed_gates.append(field_name)
        else:
            failed_gates.append(field_name)
            blocker_reasons.append(reason)

    if timeout_seconds is not None and timeout_seconds > 0:
        passed_gates.append("timeout_seconds")
    else:
        failed_gates.append("timeout_seconds")
        blocker_reasons.append("timeout_seconds_required")

    evidence_path_unsafe = _unsafe_text_value_reasons(fields.get("evidence_bundle_path"))
    if _field_present(fields, "evidence_bundle_path") and not evidence_path_unsafe:
        passed_gates.append("evidence_bundle_path")
    else:
        failed_gates.append("evidence_bundle_path")
        blocker_reasons.append("sanitized_evidence_bundle_path_required")
        blocker_reasons.extend(
            f"unsafe_evidence_bundle_path:{reason}" for reason in evidence_path_unsafe
        )

    if str(fields.get("human_owner_approval_future_proof") or "") == "Anthony Meza":
        passed_gates.append("human_owner_approval_future_proof")
    else:
        failed_gates.append("human_owner_approval_future_proof")
        blocker_reasons.append("human_owner_future_proof_approval_must_name_anthony_meza")

    if fields.get("order_route_approval") is True or fields.get("order_route_requested") is True:
        failed_gates.append("order_route_approval")
        blocker_reasons.append("order_route_approval_attempt_blocked")
    if fields.get("live_endpoint_requested") is True or fields.get("live_endpoint_enabled") is True:
        failed_gates.append("live_endpoint")
        blocker_reasons.append("live_endpoint_attempt_blocked")

    endpoint_classification = _demo_runtime_endpoint_classification(endpoint_class)
    runtime_handoff = evaluate_oanda_demo_runtime_handoff(
        {
            "broker_id": "OANDA",
            "account_mode": "PRACTICE_DEMO",
            "environment": endpoint_classification,
            "endpoint_classification": endpoint_classification,
            "handoff_scope": OANDA_RUNTIME_HANDOFF_SCOPE,
            "handoff_mode": OANDA_RUNTIME_HANDOFF_MODE,
            "metadata_intake_authorized": True,
            "runtime_reference_present": _field_present(
                fields, "runtime_auth_reference_label"
            ),
            "runtime_reference_format": OANDA_RUNTIME_AUTH_REFERENCE_FORMAT,
            "auth_material_location": OANDA_RUNTIME_AUTH_MATERIAL_LOCATION,
            "runtime_boundary_confirmed": True,
            "repo_storage_confirmed_absent": True,
            "account_identifier_present": False,
            "credential_value_present": False,
            "no_account_id_storage_confirmed": fields.get("no_account_id_value") is True,
            "no_auth_value_storage_confirmed": fields.get("no_credential_value") is True,
            "audit_logging_acknowledged": True,
        }
    )

    if runtime_handoff.get("runtime_handoff_ready") is True:
        passed_gates.append("runtime_handoff")
    else:
        failed_gates.append("runtime_handoff")
        blocker_reasons.append("runtime_handoff_required")
        blocker_reasons.extend(
            f"runtime_handoff_blocker:{blocker}"
            for blocker in list(runtime_handoff.get("blockers") or [])
        )

    passed_gates = sorted(set(passed_gates))
    failed_gates = sorted(set(failed_gates))
    blocker_reasons = sorted(set(blocker_reasons))
    demo_runtime_ready = not blocker_reasons

    return {
        "schema": "AIOS_FOREX_DELIVERY_DEMO_RUNTIME_READINESS_DRY_RUN.v1",
        "demo_runtime_ready": demo_runtime_ready,
        "future_broker_demo_proof_review_ready": demo_runtime_ready,
        "dry_run_only": True,
        "broker_connection_allowed": False,
        "connection_attempt_allowed": False,
        "connection_attempt_performed": False,
        "broker_request_sent": False,
        "network_allowed": False,
        "network_used": False,
        "network_api_allowed": False,
        "credentials_allowed": False,
        "credentials_used": False,
        "credential_material_present": False,
        "account_access_allowed": False,
        "order_route_allowed": False,
        "order_submit_allowed": False,
        "order_placed": False,
        "live_endpoint_allowed": False,
        "live_execution_allowed": False,
        "required_fields": list(DEMO_RUNTIME_REQUIRED_FIELDS),
        "missing_fields": missing,
        "passed_gates": passed_gates,
        "failed_gates": failed_gates,
        "blocker_reasons": blocker_reasons,
        "runtime_handoff": runtime_handoff,
        "next_required_action": (
            "future_human_owner_demo_connection_proof_packet_review"
            if demo_runtime_ready
            else "complete_sanitized_demo_runtime_readiness_dry_run_fields"
        ),
        "stop_point": (
            "Dry-run readiness validation only; no broker connection, credential access, "
            "network call, market-data fetch, paper order, or live order is authorized."
        ),
    }


def submit_live_order(_: dict[str, Any] | None = None) -> None:
    """Fail closed for any live-order attempt."""

    raise LiveExecutionBlocked(
        "Live order submission is blocked by RISK_POLICY.md and this governed readiness package."
    )


def _paper_execute(payload: dict[str, Any], *, policy: ForexDeliveryPolicy) -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_DELIVERY_PAPER_EXECUTION.v1",
        "status": "FILLED_SIMULATED",
        "fill_price": policy.paper_price_by_pair[payload["instrument"]],
        "filled_units": payload["units"],
        "paper_only": True,
        "live_order": False,
        "broker_request_sent": False,
        "network_used": False,
    }


def _blocked_execution(risk: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_DELIVERY_PAPER_EXECUTION.v1",
        "status": "REJECTED_BY_RISK",
        "rejection_reasons": list(risk.get("rejection_reasons") or []),
        "paper_only": True,
        "live_order": False,
        "broker_request_sent": False,
        "network_used": False,
    }


def _verify_fill(execution: dict[str, Any]) -> dict[str, Any]:
    fill = dict(execution.get("fill") or {})
    return {
        "schema": "AIOS_FOREX_DELIVERY_FILL_VERIFY.v1",
        "fill_verified": (
            execution.get("status") in {"FILLED_SIMULATED", "PAPER_ORDER_ACCEPTED"}
            or fill.get("fill_verified") is True
        ),
        "status": fill.get("status") or execution.get("status"),
        "fill_id": fill.get("fill_id"),
        "paper_order_id": fill.get("paper_order_id") or execution.get("paper_order_id"),
        "evidence_recorded": True,
        "paper_only": True,
        "live_order": False,
    }


def _close_adapter_position(
    adapter: PaperDemoBrokerAdapter,
    execution: dict[str, Any],
    request: dict[str, Any],
    *,
    policy: ForexDeliveryPolicy,
) -> dict[str, Any]:
    position = dict(execution.get("position") or {})
    position_id = str(position.get("position_id") or "")
    if position_id:
        return adapter.close_position(position_id, close_price=position.get("entry_price"))
    fill = _verify_fill(execution)
    pair = _normalize_pair(request.get("instrument"))
    units = _int_or_none(request.get("units")) or 0
    entry = policy.paper_price_by_pair.get(pair, 0.0)
    close = entry
    realized_pl_usd = 0.0 if fill.get("fill_verified") else None
    return {
        "schema": "AIOS_FOREX_DELIVERY_POSITION_CLOSE.v1",
        "position_closed": fill.get("fill_verified") is True,
        "entry_price": entry,
        "close_price": close,
        "units": units,
        "realized_pl_usd": realized_pl_usd,
        "pl_capture_status": "RECORDED" if realized_pl_usd is not None else "NOT_AVAILABLE",
        "paper_only": True,
        "live_order": False,
    }


def _build_evidence_log(**items: dict[str, Any]) -> dict[str, Any]:
    events = []
    for name, payload in items.items():
        events.append(
            {
                "event": name,
                "recorded": True,
                "paper_only": True,
                "sanitized": True,
                "status": payload.get("status") or payload.get("schema"),
            }
        )
    return {
        "schema": "AIOS_FOREX_DELIVERY_EVIDENCE_LOG.v1",
        "archive_status": "LOCAL_REPO_TEMPLATE_ONLY",
        "sanitized": True,
        "contains_private_data": False,
        "contains_real_credentials": False,
        "events": events,
        "adapter_evidence": dict(items.get("adapter_evidence") or {}),
    }


def _build_final_trade_report(evidence: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_DELIVERY_FINAL_TRADE_REPORT.v1",
        "report_status": "PRODUCED",
        "paper_only": True,
        "live_order_placed": False,
        "real_credentials_added": False,
        "evidence_event_count": len(evidence.get("events") or []),
        "next_safe_action": (
            "Human Owner may review the arming checklist fields; live order remains blocked."
        ),
    }


def _default_order_request() -> dict[str, Any]:
    return {
        "instrument": "EUR_USD",
        "side": "BUY",
        "order_type": "MARKET",
        "units": 1,
        "spread_pips": 1.0,
        "stop_loss": 1.075,
        "take_profit": 1.09,
        "max_loss_usd": 1.0,
    }


def _normalize_demo_runtime_label(value: Any) -> str:
    return str(value or "").strip().upper().replace("-", "_").replace(" ", "_")


def _demo_runtime_endpoint_classification(endpoint_class: str) -> str:
    if endpoint_class in {"OANDA_PRACTICE", "OANDA_PRACTICE_DEMO"}:
        return "OANDA_PRACTICE_DEMO"
    return "PRACTICE_REFERENCE_ONLY"


def _normalize_pair(value: Any) -> str:
    return str(value or "").strip().upper().replace("/", "_").replace("-", "_")


def _int_or_none(value: Any) -> int | None:
    try:
        if value in (None, ""):
            return None
        return int(value)
    except (TypeError, ValueError):
        return None


def _float_or_none(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _field_present(fields: dict[str, Any], field_name: str) -> bool:
    return field_name in fields and fields[field_name] not in (None, "", [], {})


def _find_forbidden_fields(value: Any, *, path: str = "") -> list[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, nested in value.items():
            key_text = str(key)
            key_path = f"{path}.{key_text}" if path else key_text
            normalized_key = key_text.lower()
            if _forbidden_key_name(normalized_key):
                found.add(key_path)
            found.update(_find_forbidden_fields(nested, path=key_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            item_path = f"{path}[{index}]" if path else f"[{index}]"
            found.update(_find_forbidden_fields(item, path=item_path))
    elif _looks_like_forbidden_value(value):
        found.add(path or "<value>")
    return sorted(found)


def _forbidden_key_name(key_text: str) -> bool:
    if key_text in REQUIRED_EXCEPTION_FIELDS:
        return False
    if key_text in DEMO_RUNTIME_REQUIRED_FIELDS:
        return False
    if key_text in FORBIDDEN_LIVE_FIELDS:
        return True
    return any(marker in key_text for marker in FORBIDDEN_LIVE_FIELD_MARKERS)


def _looks_like_forbidden_value(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value.strip().lower()
    if any(marker in normalized for marker in FORBIDDEN_VALUE_MARKERS):
        return True
    parts = normalized.split("-")
    return len(parts) >= 3 and all(part.isdigit() for part in parts[:3])


def _unsafe_text_value_reasons(value: Any) -> list[str]:
    if not isinstance(value, str):
        return []
    normalized = value.strip().lower()
    reasons = [marker for marker in UNSAFE_REVIEW_MARKERS if marker in normalized]
    if _looks_like_forbidden_value(value):
        reasons.append("forbidden_value_shape")
    return reasons
