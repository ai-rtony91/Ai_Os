"""Read-only OANDA demo broker adapter runtime binding with injected transport only."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

SCHEMA = "AIOS_FOREX_OANDA_DEMO_BROKER_ADAPTER_RUNTIME_BINDING_V1"
MODE = "INJECTED_TRANSPORT_OANDA_DEMO_BROKER_ADAPTER_BINDING"

OANDA_DEMO_BINDING_READY_FOR_OWNER_RUNTIME_TRANSPORT = (
    "OANDA_DEMO_BINDING_READY_FOR_OWNER_RUNTIME_TRANSPORT"
)
OANDA_DEMO_BINDING_READY_WITH_INJECTED_FAKE_TRANSPORT = (
    "OANDA_DEMO_BINDING_READY_WITH_INJECTED_FAKE_TRANSPORT"
)
OANDA_DEMO_FAKE_TRANSPORT_ACCEPTED = "OANDA_DEMO_FAKE_TRANSPORT_ACCEPTED"
BLOCKED_BY_MISSING_TRANSPORT = "BLOCKED_BY_MISSING_TRANSPORT"
BLOCKED_BY_TRANSPORT_CONTRACT = "BLOCKED_BY_TRANSPORT_CONTRACT"
BLOCKED_BY_RUNTIME_CONTEXT = "BLOCKED_BY_RUNTIME_CONTEXT"
BLOCKED_BY_OWNER_APPROVAL = "BLOCKED_BY_OWNER_APPROVAL"
BLOCKED_BY_DEMO_BOUNDARY = "BLOCKED_BY_DEMO_BOUNDARY"
BLOCKED_BY_ORDER_REQUEST = "BLOCKED_BY_ORDER_REQUEST"
BLOCKED_BY_RISK_ENVELOPE = "BLOCKED_BY_RISK_ENVELOPE"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY = "BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

OWNER_ACTION_IDS = (
    "REVIEW_RUNTIME_CONTEXT",
    "REVIEW_OWNER_APPROVAL",
    "REVIEW_DEMO_BOUNDARY",
    "REVIEW_ORDER_REQUEST",
    "REVIEW_RISK_ENVELOPE",
    "REVIEW_TRANSPORT_CONTRACT",
    "REVIEW_SANITIZED_ORDER_ENVELOPE",
    "REVIEW_TRANSPORT_RESULT",
    "REVIEW_NEXT_PACKET",
)

ALLOWED_BROKER_MODES = frozenset({"DEMO", "PRACTICE", "OANDA_DEMO"})
ALLOWED_ACCOUNT_ENVIRONMENTS = frozenset({"PRACTICE", "DEMO", "OANDA_DEMO"})
ALLOWED_SIDES = frozenset({"BUY", "SELL", "LONG", "SHORT"})
ALLOWED_ORDER_TYPES = frozenset({"MARKET", "LIMIT", "PREP_ONLY"})
SENSITIVE_KEY_PARTS = (
    "routing_number",
    "account_number",
    "account_id",
    "oanda_account_id",
    "debit_card_number",
    "card_number",
    "cvv",
    "password",
    "api_key",
    "token_value",
    "secret",
    "broker_token",
    "access_token",
    "bearer",
)

SAFE_METADATA_KEYS = frozenset(
    {
        "demo_account_reference_present",
        "account_identifier_values_provided",
        "account_identifier_storage_allowed",
        "credential_storage_allowed",
        "credential_read_allowed",
        "broker_api_allowed",
        "direct_broker_api_allowed",
        "network_call_allowed",
        "live_trading_allowed",
        "money_movement_allowed",
        "bank_access_allowed",
        "approval_token_required",
        "approval_token_metadata_present",
        "live_execution_allowed",
        "live_account_allowed",
        "approval_token_evidence",
        "approval_token_required",
    }
)


class OandaDemoBrokerAdapterRuntimeBindingV1:
    """Read-only wrapper for injecting a fake broker transport."""

    schema = SCHEMA
    mode = MODE

    def __init__(self, payload: Mapping[str, Any] | None = None, transport: Any | None = None) -> None:
        self.payload = dict(payload or {})
        self.transport = transport
        self.transport_call_count = 0
        self.transport_last_request: dict[str, Any] | None = None
        self._last_transport_result: dict[str, Any] | None = None

    def submit_demo_order(self, order_request: Mapping[str, Any] | None = None) -> dict[str, Any]:
        """Send one sanitized request to the injected transport."""
        transport_method = _transport_method(self.transport)
        if transport_method is None:
            return {
                "status": BLOCKED_BY_TRANSPORT_CONTRACT,
                "blockers": ["adapter_submit_method_missing"],
            }
        request = _copy_mapping(order_request)
        self.transport_call_count += 1
        self.transport_last_request = request
        result = _sanitize_mapping(_safe_call(transport_method, request))
        self._last_transport_result = result
        return result

    def bind(self) -> dict[str, Any]:
        """Build the adapter binding decision and optionally call transport once."""
        return _build_binding_result(self)


def bind_oanda_demo_broker_adapter_runtime_v1(
    payload: Mapping[str, Any] | None = None,
    transport: Any | None = None,
) -> dict[str, Any]:
    """Evaluate and return the runtime-binding decision."""
    return build_oanda_demo_broker_adapter_runtime_binding_v1(payload=payload, transport=transport).bind()


def build_oanda_demo_broker_adapter_runtime_binding_v1(
    payload: Mapping[str, Any] | None = None,
    transport: Any | None = None,
) -> OandaDemoBrokerAdapterRuntimeBindingV1:
    """Construct the adapter object."""
    return OandaDemoBrokerAdapterRuntimeBindingV1(payload=payload, transport=transport)


def _build_binding_result(adapter: OandaDemoBrokerAdapterRuntimeBindingV1) -> dict[str, Any]:
    source = adapter.payload

    transport_supplied = adapter.transport is not None
    transport_contract = _transport_contract_summary(adapter.transport)
    transport_contract_ready = transport_contract["ready"]
    transport_call_count = adapter.transport_call_count
    transport_call_attempted = False

    runtime_context_summary = _runtime_context_summary(source.get("runtime_context"), transport_supplied)
    owner_approval_summary = _owner_approval_summary(
        source.get("owner_approval"),
        source.get("approval_token_evidence"),
        source.get("owner_name"),
    )
    demo_boundary_summary = _demo_boundary_summary(source.get("demo_boundary"))
    order_request_summary = _order_request_summary(source.get("order_request"))
    risk_envelope_summary = _risk_envelope_summary(source.get("risk_envelope"))
    telemetry_summary = _telemetry_summary(source.get("telemetry"))

    sanitized_order_envelope = _build_sanitized_order_envelope(
        runtime_context_summary=runtime_context_summary,
        demo_boundary_summary=demo_boundary_summary,
        order_request_summary=order_request_summary,
        risk_envelope_summary=risk_envelope_summary,
    )

    missing_input_fields = _missing_inputs(source)
    live_or_money_blockers = _live_or_money_authority_blockers(
        runtime_context_summary=runtime_context_summary,
        demo_boundary_summary=demo_boundary_summary,
        order_request_summary=order_request_summary,
    )
    sensitive_data_present = _contains_sensitive_data(source)
    sensitive_data_blockers = ["sensitive_data_provided"] if sensitive_data_present else []

    if missing_input_fields:
        binding_status = INCOMPLETE_INPUTS
        binding_blockers = missing_input_fields
    elif sensitive_data_present:
        binding_status = BLOCKED_BY_SENSITIVE_DATA
        binding_blockers = sensitive_data_blockers
    elif live_or_money_blockers:
        binding_status = BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY
        binding_blockers = live_or_money_blockers
    elif not runtime_context_summary["ready"]:
        binding_status = BLOCKED_BY_RUNTIME_CONTEXT
        binding_blockers = list(runtime_context_summary["blockers"])
    elif not owner_approval_summary["ready"]:
        binding_status = BLOCKED_BY_OWNER_APPROVAL
        binding_blockers = list(owner_approval_summary["blockers"])
    elif not demo_boundary_summary["ready"]:
        binding_status = BLOCKED_BY_DEMO_BOUNDARY
        binding_blockers = list(demo_boundary_summary["blockers"])
    elif not order_request_summary["ready"]:
        binding_status = BLOCKED_BY_ORDER_REQUEST
        binding_blockers = list(order_request_summary["blockers"])
    elif not risk_envelope_summary["ready"]:
        binding_status = BLOCKED_BY_RISK_ENVELOPE
        binding_blockers = list(risk_envelope_summary["blockers"])
    elif not transport_supplied:
        binding_status = OANDA_DEMO_BINDING_READY_FOR_OWNER_RUNTIME_TRANSPORT
        binding_blockers = []
    elif not transport_contract_ready:
        binding_status = BLOCKED_BY_TRANSPORT_CONTRACT
        binding_blockers = list(transport_contract["blockers"])
    else:
        # Transport is supplied and contract is valid, execute once.
        transport_call_attempted = True
        transport_call_result = adapter.submit_demo_order(sanitized_order_envelope)
        transport_call_count = adapter.transport_call_count
        sanitized_transport_result = transport_call_result
        binding_status = OANDA_DEMO_FAKE_TRANSPORT_ACCEPTED
        binding_blockers = []

    if binding_status != OANDA_DEMO_FAKE_TRANSPORT_ACCEPTED:
        sanitized_transport_result = {}

    next_best_packet = _next_best_packet(binding_status)

    binding_result = {
        "schema": SCHEMA,
        "mode": MODE,
        "read_only_binding": True,
        "direct_broker_api_allowed": False,
        "broker_api_import_allowed": False,
        "network_call_allowed": False,
        "live_trading_allowed": False,
        "real_money_allowed": False,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "credential_storage_allowed": False,
        "credential_read_allowed": False,
        "account_identifier_storage_allowed": False,
        "scheduler_created": False,
        "daemon_created": False,
        "webhook_created": False,
        "dashboard_runtime_created": False,
        "owner_decision_required": True,
        "binding_status": binding_status,
        "adapter_available": transport_supplied and transport_contract_ready,
        "transport_supplied": transport_supplied,
        "transport_contract_ready": transport_contract_ready,
        "transport_call_attempted": transport_call_attempted,
        "transport_call_count": transport_call_count,
        "sanitized_order_envelope": sanitized_order_envelope if sanitized_order_envelope else None,
        "sanitized_transport_result": sanitized_transport_result,
        "runtime_context_summary": runtime_context_summary,
        "owner_approval_summary": owner_approval_summary,
        "demo_boundary_summary": demo_boundary_summary,
        "order_request_summary": order_request_summary,
        "risk_envelope_summary": risk_envelope_summary,
        "telemetry_summary": telemetry_summary,
        "binding_blockers": list(binding_blockers),
        "owner_action_queue": _owner_action_queue(
            next_best_packet=next_best_packet,
            binding_status=binding_status,
            blocking_items= list(binding_blockers),
        ),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(binding_status),
        "audit_record": _audit_record(
            source=source,
            binding_status=binding_status,
            transport_supplied=transport_supplied,
            transport_contract_ready=transport_contract_ready,
            transport_call_attempted=transport_call_attempted,
            transport_call_count=transport_call_count,
            sensitive_data_present=sensitive_data_present,
        ),
        "safety": _safety_summary(),
    }
    return binding_result


def _runtime_context_summary(runtime_context: Mapping[str, Any] | None, transport_supplied: bool) -> dict[str, Any]:
    context = _mapping(runtime_context)
    broker_name = _text(context.get("broker_name"), "OANDA")
    broker_mode = _text(context.get("broker_mode"))
    account_environment = _text(context.get("account_environment"))
    live_account_allowed = _bool(context.get("live_account_allowed"))
    real_money_allowed = _bool(context.get("real_money_allowed"))
    live_execution_allowed = _bool(context.get("live_execution_allowed"))
    money_movement_allowed = _bool(context.get("money_movement_allowed"))
    bank_access_allowed = _bool(context.get("bank_access_allowed"))
    demo_account_reference_present = _bool(context.get("demo_account_reference_present"))
    account_identifier_values_provided = _bool(context.get("account_identifier_values_provided"))
    credential_values_provided = _bool(context.get("credential_values_provided"))
    runtime_credentials_managed_by_owner = _bool(context.get("runtime_credentials_managed_by_owner"))
    direct_broker_api_allowed = _bool(context.get("direct_broker_api_allowed"))
    broker_api_allowed = _bool(context.get("broker_api_allowed"))
    network_call_allowed = _bool(context.get("network_call_allowed"))

    blockers: list[str] = []
    if not broker_name:
        blockers.append("broker_name_missing")
    elif broker_name.upper() != "OANDA":
        blockers.append("broker_name_not_oanda")
    if not broker_mode:
        blockers.append("broker_mode_missing")
    elif broker_mode.upper() not in ALLOWED_BROKER_MODES:
        blockers.append("broker_mode_not_demo")
    if not account_environment:
        blockers.append("account_environment_missing")
    elif account_environment.upper() not in ALLOWED_ACCOUNT_ENVIRONMENTS:
        blockers.append("account_environment_not_demo")

    boolean_expectations = (
        ("live_account_allowed", live_account_allowed, False),
        ("real_money_allowed", real_money_allowed, False),
        ("live_execution_allowed", live_execution_allowed, False),
        ("money_movement_allowed", money_movement_allowed, False),
        ("bank_access_allowed", bank_access_allowed, False),
        ("demo_account_reference_present", demo_account_reference_present, True),
        ("account_identifier_values_provided", account_identifier_values_provided, False),
        ("credential_values_provided", credential_values_provided, False),
        ("runtime_credentials_managed_by_owner", runtime_credentials_managed_by_owner, True),
        ("direct_broker_api_allowed", direct_broker_api_allowed, False),
        ("broker_api_allowed", broker_api_allowed, False),
        ("network_call_allowed", network_call_allowed, False),
    )
    for key, actual, expected in boolean_expectations:
        if actual is None:
            blockers.append(f"{key}_missing")
        elif actual is not expected:
            blockers.append(f"{key}_{str(actual).lower()}")

    return {
        "ready": not blockers,
        "broker_name": broker_name,
        "broker_mode": broker_mode,
        "account_environment": account_environment,
        "transport_injected": transport_supplied,
        "demo_account_reference_present": demo_account_reference_present,
        "account_identifier_values_provided": account_identifier_values_provided,
        "credential_values_provided": credential_values_provided,
        "runtime_credentials_managed_by_owner": runtime_credentials_managed_by_owner,
        "live_account_allowed": live_account_allowed,
        "real_money_allowed": real_money_allowed,
        "live_execution_allowed": live_execution_allowed,
        "money_movement_allowed": money_movement_allowed,
        "bank_access_allowed": bank_access_allowed,
        "direct_broker_api_allowed": direct_broker_api_allowed,
        "broker_api_allowed": broker_api_allowed,
        "network_call_allowed": network_call_allowed,
        "blockers": _unique(blockers),
    }


def _owner_approval_summary(
    owner_approval: Mapping[str, Any] | None,
    approval_token_evidence: Mapping[str, Any] | None,
    owner_name: str | None,
) -> dict[str, Any]:
    owner = _mapping(owner_approval)
    token = _mapping(approval_token_evidence)
    resolved_owner_name = _text(owner.get("owner_name"), _text(owner_name, "Anthony"))

    expected_true = {
        "owner_approval_required": _bool(owner.get("owner_approval_required")),
        "owner_accepts_demo_only_boundary": _bool(owner.get("owner_accepts_demo_only_boundary")),
        "owner_accepts_injected_transport_only": _bool(owner.get("owner_accepts_injected_transport_only")),
        "owner_accepts_no_credentials_in_repo": _bool(owner.get("owner_accepts_no_credentials_in_repo")),
        "owner_accepts_no_real_money": _bool(owner.get("owner_accepts_no_real_money")),
        "owner_can_cancel": _bool(owner.get("owner_can_cancel")),
        "approval_token_metadata_present": _bool(token.get("approval_token_metadata_present")),
        "approval_phrase_matches": _bool(owner.get("approval_phrase_matches")),
        "approval_action_matches": _bool(owner.get("approval_action_matches")),
        "approval_mode_matches": _bool(owner.get("approval_mode_matches")),
        "approval_token_unexpired": _bool(token.get("approval_token_unexpired")),
        "approval_token_unused": _bool(token.get("approval_token_unused")),
    }
    owner_cancel_phrase_detected = _bool(owner.get("owner_cancel_phrase_detected"), default=False)

    blockers: list[str] = []
    for key, value in expected_true.items():
        if value is None:
            blockers.append(f"{key}_missing")
        elif value is not True:
            blockers.append(f"{key}_false")
    if owner_cancel_phrase_detected is None:
        blockers.append("owner_cancel_phrase_detected_missing")
    elif owner_cancel_phrase_detected is True:
        blockers.append("owner_cancel_phrase_detected_true")
    if owner.get("owner_name") and owner.get("owner_name") != "Anthony":
        blockers.append("owner_name_not_anthony")

    return {
        "ready": not blockers,
        "owner_name": resolved_owner_name,
        "owner_approval_required": expected_true["owner_approval_required"],
        "owner_accepts_demo_only_boundary": expected_true["owner_accepts_demo_only_boundary"],
        "owner_accepts_injected_transport_only": expected_true["owner_accepts_injected_transport_only"],
        "owner_accepts_no_credentials_in_repo": expected_true["owner_accepts_no_credentials_in_repo"],
        "owner_accepts_no_real_money": expected_true["owner_accepts_no_real_money"],
        "owner_can_cancel": expected_true["owner_can_cancel"],
        "approval_token_metadata_present": expected_true["approval_token_metadata_present"],
        "approval_phrase_matches": expected_true["approval_phrase_matches"],
        "approval_action_matches": expected_true["approval_action_matches"],
        "approval_mode_matches": expected_true["approval_mode_matches"],
        "approval_token_unexpired": expected_true["approval_token_unexpired"],
        "approval_token_unused": expected_true["approval_token_unused"],
        "owner_cancel_phrase_detected": owner_cancel_phrase_detected,
        "blockers": _unique(blockers),
    }


def _demo_boundary_summary(demo_boundary: Mapping[str, Any] | None) -> dict[str, Any]:
    boundary = _mapping(demo_boundary)
    demo_only = _bool(boundary.get("demo_only"))
    broker_name = _text(boundary.get("broker_name"), "OANDA")
    broker_mode = _text(boundary.get("broker_mode"))
    account_environment = _text(boundary.get("account_environment"))
    live_account_allowed = _bool(boundary.get("live_account_allowed"))
    real_money_allowed = _bool(boundary.get("real_money_allowed"))
    live_execution_allowed = _bool(boundary.get("live_execution_allowed"))
    money_movement_allowed = _bool(boundary.get("money_movement_allowed"))
    bank_access_allowed = _bool(boundary.get("bank_access_allowed"))

    blockers: list[str] = []
    if demo_only is None:
        blockers.append("demo_only_missing")
    elif demo_only is not True:
        blockers.append("demo_only_false")
    if not broker_name:
        blockers.append("broker_name_missing")
    elif broker_name.upper() != "OANDA":
        blockers.append("broker_name_not_oanda")
    if not broker_mode:
        blockers.append("broker_mode_missing")
    elif broker_mode.upper() not in ALLOWED_BROKER_MODES:
        blockers.append("broker_mode_not_demo")
    if not account_environment:
        blockers.append("account_environment_missing")
    elif account_environment.upper() not in ALLOWED_ACCOUNT_ENVIRONMENTS:
        blockers.append("account_environment_not_demo")
    for key, actual, expected in (
        ("live_account_allowed", live_account_allowed, False),
        ("real_money_allowed", real_money_allowed, False),
        ("live_execution_allowed", live_execution_allowed, False),
        ("money_movement_allowed", money_movement_allowed, False),
        ("bank_access_allowed", bank_access_allowed, False),
    ):
        if actual is None:
            blockers.append(f"{key}_missing")
        elif actual is not expected:
            blockers.append(f"{key}_{str(actual).lower()}")

    return {
        "ready": not blockers,
        "demo_only": demo_only,
        "broker_name": broker_name,
        "broker_mode": broker_mode,
        "account_environment": account_environment,
        "live_account_allowed": live_account_allowed,
        "real_money_allowed": real_money_allowed,
        "live_execution_allowed": live_execution_allowed,
        "money_movement_allowed": money_movement_allowed,
        "bank_access_allowed": bank_access_allowed,
        "blockers": _unique(blockers),
    }


def _order_request_summary(order_request: Mapping[str, Any] | None) -> dict[str, Any]:
    request = _mapping(order_request)
    schema = _text(request.get("schema"))
    mode = _text(request.get("mode"))
    broker_name = _text(request.get("broker_name"), "OANDA")
    broker_mode = _text(request.get("broker_mode"))
    account_environment = _text(request.get("account_environment"))
    strategy_id = _text(request.get("strategy_id"))
    candidate_id = _text(request.get("candidate_id"))
    instrument = _text(request.get("instrument"))
    side = _text(request.get("side"))
    order_type = _text(request.get("order_type"))
    units = _number(request.get("units"))
    stop_loss_present = _bool(request.get("stop_loss_present"))
    take_profit_present = _bool(request.get("take_profit_present"))
    max_spread_pips = _number(request.get("max_spread_pips"))
    max_slippage_pips = _number(request.get("max_slippage_pips"))
    demo_only = _bool(request.get("demo_only"))
    live_execution_allowed = _bool(request.get("live_execution_allowed"))
    credentials_included = _bool(request.get("credentials_included"))

    blockers: list[str] = []
    if schema is None:
        blockers.append("schema_missing")
    if mode is None:
        blockers.append("mode_missing")
    if not strategy_id:
        blockers.append("strategy_id_missing")
    if not candidate_id:
        blockers.append("candidate_id_missing")
    if not instrument:
        blockers.append("instrument_missing")
    if not side:
        blockers.append("side_missing")
    elif side.upper() not in ALLOWED_SIDES:
        blockers.append("side_not_allowed")
    if not order_type:
        blockers.append("order_type_missing")
    elif order_type.upper() not in ALLOWED_ORDER_TYPES:
        blockers.append("order_type_not_allowed")
    if units is None:
        blockers.append("units_missing")
    elif units <= 0:
        blockers.append("units_not_positive")
    if stop_loss_present is None:
        blockers.append("stop_loss_present_missing")
    elif stop_loss_present is not True:
        blockers.append("stop_loss_present_false")
    if take_profit_present is None:
        blockers.append("take_profit_present_missing")
    elif take_profit_present is not True:
        blockers.append("take_profit_present_false")
    if max_spread_pips is None:
        blockers.append("max_spread_pips_missing")
    if max_slippage_pips is None:
        blockers.append("max_slippage_pips_missing")
    if demo_only is None:
        blockers.append("demo_only_missing")
    elif demo_only is not True:
        blockers.append("demo_only_false")
    if live_execution_allowed is None:
        blockers.append("live_execution_allowed_missing")
    elif live_execution_allowed is not False:
        blockers.append("live_execution_allowed_true")
    if credentials_included is None:
        blockers.append("credentials_included_missing")
    elif credentials_included is not False:
        blockers.append("credentials_included_true")
    if broker_name.upper() not in ("OANDA", ""):
        blockers.append("broker_name_not_oanda")
    if not broker_mode:
        blockers.append("broker_mode_missing")
    elif broker_mode.upper() not in ALLOWED_BROKER_MODES:
        blockers.append("broker_mode_not_demo")
    if not account_environment:
        blockers.append("account_environment_missing")
    elif account_environment.upper() not in ALLOWED_ACCOUNT_ENVIRONMENTS:
        blockers.append("account_environment_not_demo")

    return {
        "ready": not blockers,
        "schema": schema,
        "mode": mode,
        "broker_name": broker_name,
        "broker_mode": broker_mode,
        "account_environment": account_environment,
        "strategy_id": strategy_id,
        "candidate_id": candidate_id,
        "instrument": instrument,
        "side": side,
        "order_type": order_type,
        "units": units,
        "stop_loss_present": stop_loss_present,
        "take_profit_present": take_profit_present,
        "max_spread_pips": max_spread_pips,
        "max_slippage_pips": max_slippage_pips,
        "demo_only": demo_only,
        "live_execution_allowed": live_execution_allowed,
        "credentials_included": credentials_included,
        "blockers": _unique(blockers),
    }


def _risk_envelope_summary(risk_envelope: Mapping[str, Any] | None) -> dict[str, Any]:
    envelope = _mapping(risk_envelope)
    max_risk_per_trade_pct = _number(envelope.get("max_risk_per_trade_pct"))
    max_daily_loss_pct = _number(envelope.get("max_daily_loss_pct"))
    one_order_only = _bool(envelope.get("one_order_only"))
    kill_switch_active = _bool(envelope.get("kill_switch_active"))
    daily_loss_stop_active = _bool(envelope.get("daily_loss_stop_active"))
    duplicate_order_detected = _bool(envelope.get("duplicate_order_detected"))

    blockers: list[str] = []
    if max_risk_per_trade_pct is None:
        blockers.append("max_risk_per_trade_pct_missing")
    elif max_risk_per_trade_pct > 0.01:
        blockers.append("max_risk_per_trade_pct_above_limit")
    if max_daily_loss_pct is None:
        blockers.append("max_daily_loss_pct_missing")
    elif max_daily_loss_pct > 0.03:
        blockers.append("max_daily_loss_pct_above_limit")
    if one_order_only is None:
        blockers.append("one_order_only_missing")
    elif one_order_only is not True:
        blockers.append("one_order_only_false")
    if kill_switch_active is None:
        blockers.append("kill_switch_active_missing")
    elif kill_switch_active is not False:
        blockers.append("kill_switch_active_true")
    if daily_loss_stop_active is None:
        blockers.append("daily_loss_stop_active_missing")
    elif daily_loss_stop_active is not False:
        blockers.append("daily_loss_stop_active_true")
    if duplicate_order_detected is None:
        blockers.append("duplicate_order_detected_missing")
    elif duplicate_order_detected is not False:
        blockers.append("duplicate_order_detected_true")

    return {
        "ready": not blockers,
        "max_risk_per_trade_pct": max_risk_per_trade_pct,
        "max_daily_loss_pct": max_daily_loss_pct,
        "one_order_only": one_order_only,
        "kill_switch_active": kill_switch_active,
        "daily_loss_stop_active": daily_loss_stop_active,
        "duplicate_order_detected": duplicate_order_detected,
        "blockers": _unique(blockers),
    }


def _telemetry_summary(telemetry: Mapping[str, Any] | None) -> dict[str, Any]:
    raw = _mapping(telemetry)
    telemetry_fields_seen = [str(key) for key in raw.keys() if isinstance(key, str)]
    return {
        "ready": bool(telemetry),
        "telemetry_fields_seen": telemetry_fields_seen,
    }

def _build_sanitized_order_envelope(
    runtime_context_summary: Mapping[str, Any],
    demo_boundary_summary: Mapping[str, Any],
    order_request_summary: Mapping[str, Any],
    risk_envelope_summary: Mapping[str, Any],
) -> dict[str, Any]:
    if not order_request_summary.get("ready"):
        return {}
    return {
        "schema": SCHEMA,
        "mode": order_request_summary.get("mode"),
        "broker_name": order_request_summary.get("broker_name"),
        "broker_mode": (
            order_request_summary.get("broker_mode")
            or runtime_context_summary.get("broker_mode")
            or demo_boundary_summary.get("broker_mode")
        ),
        "account_environment": (
            order_request_summary.get("account_environment")
            or runtime_context_summary.get("account_environment")
            or demo_boundary_summary.get("account_environment")
        ),
        "instrument": order_request_summary.get("instrument"),
        "side": order_request_summary.get("side"),
        "order_type": order_request_summary.get("order_type"),
        "units": order_request_summary.get("units"),
        "stop_loss_present": order_request_summary.get("stop_loss_present"),
        "take_profit_present": order_request_summary.get("take_profit_present"),
        "max_spread_pips": order_request_summary.get("max_spread_pips"),
        "max_slippage_pips": order_request_summary.get("max_slippage_pips"),
        "risk_limits": {
            "max_risk_per_trade_pct": risk_envelope_summary.get("max_risk_per_trade_pct"),
            "max_daily_loss_pct": risk_envelope_summary.get("max_daily_loss_pct"),
            "kill_switch_active": risk_envelope_summary.get("kill_switch_active"),
            "daily_loss_stop_active": risk_envelope_summary.get("daily_loss_stop_active"),
            "one_order_only": risk_envelope_summary.get("one_order_only"),
        },
        "strategy_id": order_request_summary.get("strategy_id"),
        "candidate_id": order_request_summary.get("candidate_id"),
        "demo_only": order_request_summary.get("demo_only"),
        "live_execution_allowed": False,
        "credentials_included": False,
        "account_identifiers_included": False,
        "transport_injected": bool(runtime_context_summary.get("transport_injected")),
    }


def _missing_inputs(source: Mapping[str, Any]) -> list[str]:
    required = (
        "runtime_context",
        "owner_approval",
        "demo_boundary",
        "order_request",
        "risk_envelope",
        "telemetry",
    )
    missing = []
    for key in required:
        value = source.get(key)
        if not isinstance(value, Mapping):
            missing.append(f"missing_{key}")
    return missing


def _live_or_money_authority_blockers(
    runtime_context_summary: Mapping[str, Any],
    demo_boundary_summary: Mapping[str, Any],
    order_request_summary: Mapping[str, Any],
) -> list[str]:
    checks = {
        "live_account_allowed": (
            _bool(runtime_context_summary.get("live_account_allowed"))
            or _bool(demo_boundary_summary.get("live_account_allowed"))
        ),
        "real_money_allowed": (
            _bool(runtime_context_summary.get("real_money_allowed"))
            or _bool(demo_boundary_summary.get("real_money_allowed"))
        ),
        "money_movement_allowed": (
            _bool(runtime_context_summary.get("money_movement_allowed"))
            or _bool(demo_boundary_summary.get("money_movement_allowed"))
        ),
        "bank_access_allowed": (
            _bool(runtime_context_summary.get("bank_access_allowed"))
            or _bool(demo_boundary_summary.get("bank_access_allowed"))
        ),
        "live_execution_allowed": _bool(order_request_summary.get("live_execution_allowed")),
    }
    return [name for name, value in checks.items() if value is True]


def _owner_action_queue(
    *,
    next_best_packet: str,
    binding_status: str,
    blocking_items: list[str],
) -> list[dict[str, Any]]:
    action_safe_action = {
        "REVIEW_RUNTIME_CONTEXT": "Validate broker/runtime context fields and required false-authority flags.",
        "REVIEW_OWNER_APPROVAL": "Validate owner approval payload and signature/token metadata.",
        "REVIEW_DEMO_BOUNDARY": "Validate demo boundary limits and broker demo mode.",
        "REVIEW_ORDER_REQUEST": "Validate sanitized OANDA demo order request fields.",
        "REVIEW_RISK_ENVELOPE": "Validate risk caps and live risk protections.",
        "REVIEW_TRANSPORT_CONTRACT": "Verify injected transport exposes submit_oanda_demo_order or submit_demo_order.",
        "REVIEW_SANITIZED_ORDER_ENVELOPE": "Inspect sanitized envelope before transport call.",
        "REVIEW_TRANSPORT_RESULT": "Inspect sanitized transport result and ensure no secrets were returned.",
        "REVIEW_NEXT_PACKET": "Advance to the next packet in the bounded path.",
    }
    return [
        {
            "action_id": action_id,
            "owner_decision_required": True,
            "live_execution_allowed": False,
            "safe_action": action_safe_action[action_id],
            "blocked_by": list(blocking_items),
            "next_best_packet": next_best_packet if action_id == "REVIEW_NEXT_PACKET" else None,
        }
        for action_id in OWNER_ACTION_IDS
    ]


def _next_best_packet(binding_status: str) -> str:
    if binding_status == OANDA_DEMO_BINDING_READY_FOR_OWNER_RUNTIME_TRANSPORT:
        return "AIOS_FOREX_OANDA_DEMO_OWNER_RUNTIME_TRANSPORT_PACKET_V1"
    if binding_status == OANDA_DEMO_FAKE_TRANSPORT_ACCEPTED:
        return "AIOS_FOREX_OANDA_DEMO_POST_EXECUTION_REVIEW_V1"
    return "AIOS_FOREX_OANDA_DEMO_BROKER_ADAPTER_RUNTIME_BINDING_V1"


def _safe_manual_next_action(binding_status: str) -> str:
    return {
        OANDA_DEMO_FAKE_TRANSPORT_ACCEPTED: "Sanitized transport output is ready; route to post-execution review.",
        OANDA_DEMO_BINDING_READY_FOR_OWNER_RUNTIME_TRANSPORT: "Inject a verified fake transport and rerun binding.",
        INCOMPLETE_INPUTS: "Supply all required packet sections: runtime_context, owner_approval, demo_boundary, order_request, risk_envelope, telemetry.",
        BLOCKED_BY_SENSITIVE_DATA: "Remove forbidden credential/account fields and rerun.",
        BLOCKED_BY_RUNTIME_CONTEXT: "Repair runtime context and required demo sandbox flags.",
        BLOCKED_BY_OWNER_APPROVAL: "Repair owner approval and token evidence fields.",
        BLOCKED_BY_DEMO_BOUNDARY: "Repair demo boundary constraints.",
        BLOCKED_BY_ORDER_REQUEST: "Repair OANDA demo order request fields.",
        BLOCKED_BY_RISK_ENVELOPE: "Repair risk envelope constraints and rerun.",
        BLOCKED_BY_TRANSPORT_CONTRACT: "Supply transport exposing submit_oanda_demo_order or submit_demo_order.",
        BLOCKED_BY_LIVE_OR_MONEY_AUTHORITY: "Set all live/money authority booleans to false and rerun.",
    }.get(binding_status, "Resolve blockers and rerun binding.")


def _audit_record(
    *,
    source: Mapping[str, Any],
    binding_status: str,
    transport_supplied: bool,
    transport_contract_ready: bool,
    transport_call_attempted: bool,
    transport_call_count: int,
    sensitive_data_present: bool,
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "as_of_date": _text(source.get("as_of_date"), _now_utc_iso()),
        "owner_name": _text(source.get("owner_name"), "Anthony"),
        "input_fields_seen": sorted(str(key) for key in source.keys()),
        "binding_status": binding_status,
        "transport_supplied": transport_supplied,
        "transport_contract_ready": transport_contract_ready,
        "transport_call_attempted": transport_call_attempted,
        "transport_call_count": transport_call_count,
        "sensitive_data_present": sensitive_data_present,
    }


def _safety_summary() -> dict[str, Any]:
    return {
        "read_only_binding": True,
        "injected_transport_only": True,
        "direct_broker_api_allowed": False,
        "broker_api_import_allowed": False,
        "network_call_allowed": False,
        "live_trading_allowed": False,
        "real_money_allowed": False,
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "credential_storage_allowed": False,
        "credential_read_allowed": False,
        "account_identifier_storage_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
        "dashboard_runtime_allowed": False,
        "owner_gate_required": True,
        "demo_only": True,
        "fixed_return_target_promised": False,
        "profit_claim_authorized": False,
    }


def _transport_contract_summary(transport: Any) -> dict[str, Any]:
    method = _transport_method(transport)
    blockers: list[str] = []
    if transport is None:
        blockers.append("transport_missing")
    if method is None and transport is not None:
        blockers.append("submit_method_missing")
    return {
        "ready": method is not None,
        "method_name": getattr(method, "__name__", None),
        "blockers": _unique(blockers),
    }


def _contains_sensitive_data(source: Mapping[str, Any]) -> bool:
    return _contains_sensitive_key(source)


def _contains_sensitive_key(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key).lower()
            if key_text in SAFE_METADATA_KEYS:
                continue
            if any(sensitive in key_text for sensitive in SENSITIVE_KEY_PARTS):
                return True
            if _contains_sensitive_key(child):
                return True
        return False
    if isinstance(value, (list, tuple)):
        return any(_contains_sensitive_key(child) for child in value)
    return False


def _transport_method(transport: Any) -> Any | None:
    if transport is None:
        return None
    submit_oanda_demo_order = getattr(transport, "submit_oanda_demo_order", None)
    if callable(submit_oanda_demo_order):
        return submit_oanda_demo_order
    submit_demo_order = getattr(transport, "submit_demo_order", None)
    if callable(submit_demo_order):
        return submit_demo_order
    return None


def _safe_call(method: Any, envelope: Mapping[str, Any]) -> Any:
    result = method(_copy_mapping(envelope))
    return result if result is not None else {}


def _sanitize_mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        return {"transport_payload_type": type(value).__name__}
    sanitized: dict[str, Any] = {}
    for key, child in value.items():
        key_text = str(key).lower()
        if any(sensitive in key_text for sensitive in SENSITIVE_KEY_PARTS):
            continue
        if isinstance(child, Mapping):
            sanitized[str(key)] = _sanitize_mapping(child)
        elif isinstance(child, (list, tuple)):
            sanitized[str(key)] = [
                _sanitize_mapping(item) if isinstance(item, Mapping) else item for item in child
            ]
        else:
            sanitized[str(key)] = child
    return sanitized


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _copy_mapping(value: Mapping[str, Any] | None) -> dict[str, Any]:
    return dict(value or {})


def _unique(values: Sequence[Any]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value)
        if text not in seen:
            seen.add(text)
            output.append(text)
    return output


def _text(value: Any, default: str | None = None) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return default


def _bool(value: Any, default: bool | None = None) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes"}:
            return True
        if lowered in {"false", "0", "no"}:
            return False
    return default


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int | float):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None


def _now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
