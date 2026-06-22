from __future__ import annotations

from automation.forex_engine.live_execution_milestone_sprint import (
    LIVE_BROKER_PREFLIGHT_BLOCKED,
    LIVE_BROKER_PREFLIGHT_INVALID,
    LIVE_BROKER_PREFLIGHT_READY,
    LIVE_BROKER_PREFLIGHT_REVIEW_REQUIRED,
    LIVE_MICRO_TRADE_ARMED,
    LIVE_MICRO_TRADE_BLOCKED,
    LIVE_MICRO_TRADE_INVALID,
    LIVE_MICRO_TRADE_REVIEW_REQUIRED,
    LIVE_ORDER_COMMAND_BLOCKED,
    LIVE_ORDER_COMMAND_INVALID,
    LIVE_ORDER_COMMAND_READY,
    LIVE_ORDER_COMMAND_REVIEW_REQUIRED,
    LIVE_READINESS_BLOCKED,
    LIVE_READINESS_INVALID,
    LIVE_READINESS_READY,
    LIVE_READINESS_REVIEW_REQUIRED,
    LIVE_MICRO_UNITS_MAX,
    OPERATOR_LOGIN_PORTAL_BLOCKED,
    OPERATOR_LOGIN_PORTAL_READY,
    OPERATOR_LOGIN_PORTAL_REVIEW_REQUIRED,
    PROTECTED_LIVE_ACTION_AUTH_BLOCKED,
    PROTECTED_LIVE_ACTION_AUTH_READY,
    PROTECTED_LIVE_ACTION_AUTH_REVIEW_REQUIRED,
    SUPPORTED_LOGIN_PROVIDERS,
    build_live_broker_connection_preflight,
    build_live_micro_trade_arming_packet,
    build_live_order_execution_command_contract,
    build_operator_login_portal_contract,
    build_protected_live_action_auth_gate,
    evaluate_live_readiness_evidence,
)


def _demo_state(ready=True):
    return {
        "demo_validated": ready,
        "demo_trade_count": 20,
        "demo_positive_expectancy": True,
        "demo_profit_factor_clear": True,
        "demo_drawdown_clear": True,
        "demo_execution_quality_clear": True,
        "demo_result_ledger_present": True,
    }


def _strategy_state():
    return {
        "expected_value_positive": True,
        "win_rate_present": True,
        "average_win_present": True,
        "average_loss_present": True,
        "max_drawdown_present": True,
        "risk_of_ruin_present": True,
        "repeatability_present": True,
    }


def _risk_state():
    return {
        "kill_switch_enabled": False,
        "max_loss_gate_clear": True,
        "daily_stop_clear": True,
        "position_size_micro_only": True,
        "portfolio_exposure_clear": True,
        "stop_loss_required": True,
        "take_profit_required": True,
    }


def _operator_state():
    return {
        "authenticated_operator": True,
        "protected_action_authorized": True,
        "live_exception_requested": True,
        "understands_live_risk_ack": True,
    }


def _preflight_request():
    return {
        "operator_approved": True,
        "live_exception_mode": True,
        "read_only_first": True,
        "credentials_runtime_only": True,
        "credentials_persisted": False,
        "account_id_persisted": False,
        "endpoint_classification": "LIVE_EXCEPTION_APPROVED",
        "order_execution_requested": False,
        "network_requested": False,
        "single_micro_trade_scope": True,
    }


def _trade_candidate():
    return {
        "instrument": "EUR_USD",
        "side": "BUY",
        "units": 100,
        "risk_cap": 50,
        "stop_loss": 1.0800,
        "take_profit": 1.0900,
        "max_loss_gate_clear": True,
        "daily_stop_clear": True,
        "kill_switch_enabled": False,
        "live_exception_only": True,
        "single_trade_only": True,
        "micro_size_only": True,
    }


def _trade_approval():
    return {
        "human_approved_live_micro_trade": True,
        "authenticated_operator": True,
        "protected_action_auth_passed": True,
        "understands_loss_risk_ack": True,
        "single_trade_ack": True,
        "no_revenge_trade_ack": True,
        "stop_after_execution_ack": True,
    }


def _operator_command():
    return {
        "final_execute_live_order_command": True,
        "confirmed_one_trade_only": True,
        "confirmed_micro_size": True,
        "confirmed_stop_loss": True,
        "confirmed_take_profit": True,
        "confirmed_risk_cap": True,
        "confirmed_no_default_network": True,
        "confirmed_manual_operator_presence": True,
    }


def _ready_login_request():
    return {
        "provider": "github",
        "operator_authenticated": True,
        "cloudflare_human_challenge_passed": True,
        "bot_detection_passed": True,
        "protected_action": "live_readiness_review",
        "reauth_completed": True,
        "operator_approval_recorded": True,
    }


def test_live_readiness_ready_path():
    readiness = evaluate_live_readiness_evidence(
        _demo_state(),
        _strategy_state(),
        _risk_state(),
        _operator_state(),
    )

    assert readiness["readiness_status"] == LIVE_READINESS_READY
    assert readiness["ready"] is True
    assert readiness["next_safe_action"] == "prepare_live_broker_connection_preflight"


def test_live_readiness_blocked_when_demo_validation_missing():
    state = _demo_state()
    state["demo_validated"] = False

    readiness = evaluate_live_readiness_evidence(state, _strategy_state(), _risk_state(), _operator_state())

    assert readiness["readiness_status"] == LIVE_READINESS_BLOCKED
    assert "demo_validation_incomplete" in readiness["blockers"]


def test_live_readiness_blocked_when_expected_value_not_positive():
    strategy = _strategy_state()
    strategy["expected_value_positive"] = False

    readiness = evaluate_live_readiness_evidence(_demo_state(), strategy, _risk_state(), _operator_state())

    assert readiness["readiness_status"] == LIVE_READINESS_BLOCKED
    assert "expected_value_not_positive" in readiness["blockers"]


def test_live_readiness_blocked_when_kill_switch_enabled():
    risk = _risk_state()
    risk["kill_switch_enabled"] = True

    readiness = evaluate_live_readiness_evidence(_demo_state(), _strategy_state(), risk, _operator_state())

    assert readiness["readiness_status"] == LIVE_READINESS_BLOCKED
    assert "kill_switch_enabled" in readiness["blockers"]


def test_live_readiness_review_required_when_operator_auth_missing():
    operator = _operator_state()
    operator["authenticated_operator"] = False

    readiness = evaluate_live_readiness_evidence(_demo_state(), _strategy_state(), _risk_state(), operator)

    assert readiness["readiness_status"] == LIVE_READINESS_REVIEW_REQUIRED
    assert readiness["next_safe_action"] == "complete_live_readiness_operator_acknowledgment"


def test_live_preflight_ready_path():
    readiness = evaluate_live_readiness_evidence(_demo_state(), _strategy_state(), _risk_state(), _operator_state())
    preflight = build_live_broker_connection_preflight(readiness, _preflight_request())

    assert preflight["preflight_status"] == LIVE_BROKER_PREFLIGHT_READY
    assert preflight["ready"] is True


def test_live_preflight_missing_readiness_invalid():
    preflight = build_live_broker_connection_preflight(None, _preflight_request())

    assert preflight["preflight_status"] == LIVE_BROKER_PREFLIGHT_INVALID
    assert preflight["ready"] is False


def test_live_preflight_review_required_when_request_missing():
    readiness = evaluate_live_readiness_evidence(_demo_state(), _strategy_state(), _risk_state(), _operator_state())
    preflight = build_live_broker_connection_preflight(readiness)

    assert preflight["preflight_status"] == LIVE_BROKER_PREFLIGHT_REVIEW_REQUIRED
    assert "request_missing" in preflight["blockers"]


def test_live_preflight_persisted_credentials_blocked():
    readiness = evaluate_live_readiness_evidence(_demo_state(), _strategy_state(), _risk_state(), _operator_state())
    request = _preflight_request()
    request["credentials_persisted"] = True

    preflight = build_live_broker_connection_preflight(readiness, request)

    assert preflight["preflight_status"] == LIVE_BROKER_PREFLIGHT_BLOCKED
    assert "credentials_persisted_blocked" in preflight["blockers"]


def test_live_preflight_order_execution_request_blocked():
    readiness = evaluate_live_readiness_evidence(_demo_state(), _strategy_state(), _risk_state(), _operator_state())
    request = _preflight_request()
    request["order_execution_requested"] = True

    preflight = build_live_broker_connection_preflight(readiness, request)

    assert preflight["preflight_status"] == LIVE_BROKER_PREFLIGHT_BLOCKED
    assert "order_execution_request_blocked" in preflight["blockers"]


def test_live_arming_ready_path():
    readiness = evaluate_live_readiness_evidence(_demo_state(), _strategy_state(), _risk_state(), _operator_state())
    preflight = build_live_broker_connection_preflight(readiness, _preflight_request())
    arming = build_live_micro_trade_arming_packet(preflight, _trade_candidate(), _trade_approval())

    assert arming["arming_status"] == LIVE_MICRO_TRADE_ARMED
    assert arming["ready"] is True
    assert arming["next_safe_action"] == "route_to_final_live_order_command_contract"


def test_live_arming_review_required_when_approval_missing():
    readiness = evaluate_live_readiness_evidence(_demo_state(), _strategy_state(), _risk_state(), _operator_state())
    preflight = build_live_broker_connection_preflight(readiness, _preflight_request())
    arming = build_live_micro_trade_arming_packet(preflight, _trade_candidate())

    assert arming["arming_status"] == LIVE_MICRO_TRADE_REVIEW_REQUIRED
    assert arming["next_safe_action"] == "obtain_live_micro_trade_human_approval"


def test_live_arming_kill_switch_blocks():
    readiness = evaluate_live_readiness_evidence(_demo_state(), _strategy_state(), _risk_state(), _operator_state())
    preflight = build_live_broker_connection_preflight(readiness, _preflight_request())
    trade = _trade_candidate()
    trade["kill_switch_enabled"] = True

    arming = build_live_micro_trade_arming_packet(preflight, trade, _trade_approval())

    assert arming["arming_status"] == LIVE_MICRO_TRADE_BLOCKED
    assert "kill_switch_enabled" in arming["blockers"]


def test_live_arming_blocks_units_above_micro_policy():
    readiness = evaluate_live_readiness_evidence(_demo_state(), _strategy_state(), _risk_state(), _operator_state())
    preflight = build_live_broker_connection_preflight(readiness, _preflight_request())
    trade = _trade_candidate()
    trade["units"] = LIVE_MICRO_UNITS_MAX + 1

    arming = build_live_micro_trade_arming_packet(preflight, trade, _trade_approval())

    assert arming["arming_status"] == LIVE_MICRO_TRADE_BLOCKED
    assert "units_above_micro_policy" in arming["blockers"]


def test_live_order_command_ready_path():
    readiness = evaluate_live_readiness_evidence(_demo_state(), _strategy_state(), _risk_state(), _operator_state())
    preflight = build_live_broker_connection_preflight(readiness, _preflight_request())
    arming = build_live_micro_trade_arming_packet(preflight, _trade_candidate(), _trade_approval())
    command = build_live_order_execution_command_contract(arming, _operator_command())

    assert command["command_status"] == LIVE_ORDER_COMMAND_READY
    assert command["ready"] is True
    assert command["next_safe_action"] == "await_separate_explicit_runtime_order_executor_packet"


def test_live_order_command_review_required():
    readiness = evaluate_live_readiness_evidence(_demo_state(), _strategy_state(), _risk_state(), _operator_state())
    preflight = build_live_broker_connection_preflight(readiness, _preflight_request())
    arming = build_live_micro_trade_arming_packet(preflight, _trade_candidate(), _trade_approval())
    command = build_live_order_execution_command_contract(arming)

    assert command["command_status"] == LIVE_ORDER_COMMAND_REVIEW_REQUIRED
    assert "final_operator_command_missing" in command["blockers"]


def test_live_order_command_never_executes_order():
    readiness = evaluate_live_readiness_evidence(_demo_state(), _strategy_state(), _risk_state(), _operator_state())
    preflight = build_live_broker_connection_preflight(readiness, _preflight_request())
    arming = build_live_micro_trade_arming_packet(preflight, _trade_candidate(), _trade_approval())
    command = build_live_order_execution_command_contract(arming, _operator_command())

    assert command["safety_summary"]["order_executed"] is False
    assert command["safety_summary"]["broker_call_performed"] is False


def test_operator_login_portal_ready():
    portal = build_operator_login_portal_contract()

    assert portal["portal_status"] == OPERATOR_LOGIN_PORTAL_READY
    assert portal["ready"] is True
    assert portal["sanitized_summary"]["cloudflare_gate"]["cloudflare_turnstile_required"] is True
    assert len(portal["sanitized_summary"]["providers"]) == 3
    assert portal["sanitized_summary"]["providers"][0]["provider_name"] in ("GitHub", "Google", "Microsoft")


def test_operator_login_portal_blocks_secret_persistence():
    portal = build_operator_login_portal_contract(
        {
            "providers": {
                "github": {"client_secret_persisted": True},
            }
        }
    )

    assert portal["portal_status"] == OPERATOR_LOGIN_PORTAL_BLOCKED
    assert "github_secret_persistence_not_allowed" in portal["blockers"]


def test_protected_action_auth_ready_with_verified_operator_and_challenge():
    portal = build_operator_login_portal_contract()
    gate = build_protected_live_action_auth_gate(portal, _ready_login_request())

    assert gate["auth_gate_status"] == PROTECTED_LIVE_ACTION_AUTH_READY
    assert gate["ready"] is True
    assert gate["next_safe_action"] == "proceed_live_governance_lane"


def test_protected_action_auth_blocked_on_unsupported_provider():
    portal = build_operator_login_portal_contract()
    request = _ready_login_request()
    request["provider"] = "unknown"

    gate = build_protected_live_action_auth_gate(portal, request)

    assert gate["auth_gate_status"] == PROTECTED_LIVE_ACTION_AUTH_BLOCKED
    assert "unsupported_provider" in gate["blockers"]


def test_protected_action_auth_blocks_human_challenge_failure():
    portal = build_operator_login_portal_contract()
    request = _ready_login_request()
    request["cloudflare_human_challenge_passed"] = False

    gate = build_protected_live_action_auth_gate(portal, request)

    assert gate["auth_gate_status"] == PROTECTED_LIVE_ACTION_AUTH_BLOCKED
    assert "human_challenge_not_passed" in gate["blockers"]


def test_protected_action_auth_review_required_when_request_missing():
    portal = build_operator_login_portal_contract()
    gate = build_protected_live_action_auth_gate(portal)

    assert gate["auth_gate_status"] == PROTECTED_LIVE_ACTION_AUTH_REVIEW_REQUIRED
    assert gate["next_safe_action"] == "collect_live_action_auth_request"


def test_chain_live_readiness_to_command_no_execution_occurs():
    portal = build_operator_login_portal_contract()
    login_providers = tuple(SUPPORTED_LOGIN_PROVIDERS)
    assert "github" in login_providers

    auth_request = _ready_login_request()
    auth_request["protected_action"] = "live_order_command_contract"
    auth = build_protected_live_action_auth_gate(portal, auth_request)
    assert auth["ready"] is True

    readiness = evaluate_live_readiness_evidence(_demo_state(), _strategy_state(), _risk_state(), _operator_state())
    preflight = build_live_broker_connection_preflight(readiness, _preflight_request())
    trade_candidate = _trade_candidate()
    approval = _trade_approval()
    approval["protected_action_auth_passed"] = auth["ready"]
    arming = build_live_micro_trade_arming_packet(preflight, trade_candidate, approval)
    command = build_live_order_execution_command_contract(arming, _operator_command())

    assert readiness["readiness_status"] == LIVE_READINESS_READY
    assert preflight["preflight_status"] == LIVE_BROKER_PREFLIGHT_READY
    assert arming["arming_status"] == LIVE_MICRO_TRADE_ARMED
    assert command["command_status"] == LIVE_ORDER_COMMAND_READY
    assert command["safety_summary"]["order_executed"] is False
    assert command["safety_summary"]["broker_call_performed"] is False
    assert readiness["safety_summary"]["broker_call_performed"] is False
    assert readiness["safety_summary"]["order_executed"] is False


def test_latency_budgets_exclude_network():
    readiness = evaluate_live_readiness_evidence(_demo_state(), _strategy_state(), _risk_state(), _operator_state())
    preflight = build_live_broker_connection_preflight(readiness, _preflight_request())
    arming = build_live_micro_trade_arming_packet(preflight, _trade_candidate(), _trade_approval())
    command = build_live_order_execution_command_contract(arming, _operator_command())

    assert readiness["latency_budget"]["network_latency_ms"] == "excluded_offline_default"
    assert preflight["latency_budget"]["network_latency_ms"] == "excluded_offline_default"
    assert arming["latency_budget"]["network_latency_ms"] == "excluded_offline_default"
    assert command["latency_budget"]["network_latency_ms"] == "excluded_offline_default"


def test_invalid_missing_inputs():
    assert evaluate_live_readiness_evidence().get("readiness_status") == LIVE_READINESS_INVALID
    assert (
        build_live_broker_connection_preflight(
            {"ready": True, "readiness_status": LIVE_READINESS_READY},
            None,
        )["preflight_status"]
        == LIVE_BROKER_PREFLIGHT_REVIEW_REQUIRED
    )
    assert (
        build_live_micro_trade_arming_packet(None, _trade_candidate(), _trade_approval())["arming_status"]
        == LIVE_MICRO_TRADE_INVALID
    )
    assert (
        build_live_order_execution_command_contract(None, _operator_command())["command_status"]
        == LIVE_ORDER_COMMAND_INVALID
    )
