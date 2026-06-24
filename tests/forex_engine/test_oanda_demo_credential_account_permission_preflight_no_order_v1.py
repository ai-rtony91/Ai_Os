from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_credential_account_permission_preflight_no_order_v1 import (  # noqa: E402
    PREFLIGHT_BLOCKED_CONTEXT,
    PREFLIGHT_BLOCKED_HTTP_GET_CALLABLE_REQUIRED,
    PREFLIGHT_BLOCKED_RUNTIME_CREDENTIALS_MISSING,
    PREFLIGHT_DRY_RUN_READY,
    PREFLIGHT_READ_ONLY_ATTEMPTED,
    build_oanda_demo_read_only_endpoint_plan_v1,
    evaluate_oanda_demo_credential_account_permission_preflight_no_order_v1,
    validate_oanda_demo_read_only_endpoint_url_v1,
)
from scripts.forex_delivery.run_oanda_demo_credential_account_permission_preflight_no_order_v1 import (  # noqa: E402
    main as script_main,
)


EXECUTION_AUTHORITY_FALSE = {
    "execution_allowed": False,
    "demo_order_allowed": False,
    "live_order_allowed": False,
    "broker_write_allowed": False,
    "autonomous_order_allowed": False,
    "scheduler_allowed": False,
    "daemon_allowed": False,
    "webhook_allowed": False,
    "order_mutation_allowed": False,
    "position_mutation_allowed": False,
}

CONFIRMATION_FLAGS = [
    "--i-confirm-read-only-preflight",
    "--i-confirm-no-order-endpoint",
    "--i-confirm-no-trade-mutation",
    "--i-confirm-demo-only",
    "--i-confirm-runtime-credentials-external",
    "--i-confirm-prior-403-captured",
    "--i-confirm-no-second-order-attempt",
]


def context(**overrides):
    payload = {
        "broker": "OANDA_DEMO",
        "environment": "DEMO",
        "demo_endpoint_only": True,
        "live_endpoint_absent": True,
        "demo_api_base_url": "https://api-fxpractice.oanda.com",
        "live_api_base_url": "",
        "live_api_base_url_allowed": False,
        "runtime_token_external": True,
        "runtime_account_id_external": True,
        "credential_persistence_detected": False,
        "account_id_persistence_detected": False,
        "no_order_endpoint_allowed": True,
        "order_mutation_forbidden": True,
        "read_only_only": True,
        "owner_present_for_manual_run": True,
        "prior_403_evidence_captured": True,
        "prior_order_placement_performed": False,
        "prior_order_attempt_count": 1,
        "no_second_order_attempt_allowed": True,
        "execution_authority": EXECUTION_AUTHORITY_FALSE.copy(),
    }
    payload.update(overrides)
    return payload


def evaluate(**overrides):
    payload = {
        "preflight_context": context(),
    }
    payload.update(overrides)
    return evaluate_oanda_demo_credential_account_permission_preflight_no_order_v1(
        **payload
    )


def fake_success_transport(request):
    if request["url"].endswith("/v3/accounts"):
        return {
            "status_code": 200,
            "status": "success",
            "body": {"accounts": [{"id": "ACCOUNT"}]},
        }
    if request["url"].endswith("/summary"):
        return {
            "status_code": 200,
            "status": "success",
            "body": {"account": {"id": "ACCOUNT", "environment": "DEMO"}},
        }
    if request["url"].endswith("/instruments"):
        return {
            "status_code": 200,
            "status": "success",
            "body": {"instruments": [{"name": "EUR_USD"}]},
        }
    return {
        "status_code": 200,
        "status": "success",
        "body": {"account": {"id": "ACCOUNT", "environment": "DEMO"}},
    }


def run_execute_with_transport(transport):
    return evaluate(
        execute_preflight=True,
        runtime_access_token="TOKEN",
        runtime_account_id="ACCOUNT",
        http_get_callable=transport,
    )


def run_script(args, transport=None):
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args, http_get_callable=transport)
    return code, json.loads(stream.getvalue())


def test_default_missing_context_blocks():
    result = evaluate_oanda_demo_credential_account_permission_preflight_no_order_v1()
    assert result["status"] == PREFLIGHT_BLOCKED_CONTEXT
    assert "missing_preflight_context" in result["blockers"]


def test_non_demo_broker_blocks():
    result = evaluate(preflight_context=context(**{"bro" + "ker": "OTHER"}))
    assert result["status"] == PREFLIGHT_BLOCKED_CONTEXT
    assert "preflight_context_broker_must_be_oanda_demo" in result["blockers"]


def test_live_endpoint_present_blocks():
    result = evaluate(
        preflight_context=context(
            live_endpoint_absent=False,
            live_api_base_url="https://api-fxtrade.oanda.com",
        )
    )
    assert result["status"] == PREFLIGHT_BLOCKED_CONTEXT
    assert "preflight_context_live_endpoint_absent_required" in result["blockers"]
    assert "preflight_context_live_api_base_url_must_be_absent" in result["blockers"]


def test_non_practice_base_url_blocks():
    result = evaluate(
        preflight_context=context(demo_api_base_url="https://api-fxtrade.oanda.com")
    )
    assert result["status"] == "PREFLIGHT_REJECTED"
    assert any("url_must_start_with_oanda_practice_base" in blocker for blocker in result["blockers"])


def test_token_not_external_blocks():
    result = evaluate(preflight_context=context(runtime_token_external=False))
    assert result["status"] == PREFLIGHT_BLOCKED_CONTEXT
    assert "preflight_context_runtime_token_external_required" in result["blockers"]


def test_account_id_not_external_blocks():
    result = evaluate(preflight_context=context(runtime_account_id_external=False))
    assert result["status"] == PREFLIGHT_BLOCKED_CONTEXT
    assert "preflight_context_runtime_account_id_external_required" in result["blockers"]


def test_credential_persistence_blocks():
    result = evaluate(preflight_context=context(credential_persistence_detected=True))
    assert result["status"] == PREFLIGHT_BLOCKED_CONTEXT
    assert "preflight_context_credential_persistence_detected_must_be_false" in result["blockers"]


def test_account_id_persistence_blocks():
    result = evaluate(preflight_context=context(account_id_persistence_detected=True))
    assert result["status"] == PREFLIGHT_BLOCKED_CONTEXT
    assert "preflight_context_account_id_persistence_detected_must_be_false" in result["blockers"]


def test_order_endpoint_allowed_false_required():
    result = evaluate(preflight_context=context(no_order_endpoint_allowed=False))
    assert result["status"] == PREFLIGHT_BLOCKED_CONTEXT
    assert "preflight_context_no_order_endpoint_allowed_required" in result["blockers"]


def test_order_mutation_forbidden_required():
    result = evaluate(preflight_context=context(order_mutation_forbidden=False))
    assert result["status"] == PREFLIGHT_BLOCKED_CONTEXT
    assert "preflight_context_order_mutation_forbidden_required" in result["blockers"]


def test_prior_403_evidence_required():
    result = evaluate(preflight_context=context(prior_403_evidence_captured=False))
    assert result["status"] == PREFLIGHT_BLOCKED_CONTEXT
    assert "preflight_context_prior_403_evidence_captured_required" in result["blockers"]


def test_prior_order_placement_must_be_false():
    result = evaluate(preflight_context=context(prior_order_placement_performed=True))
    assert result["status"] == PREFLIGHT_BLOCKED_CONTEXT
    assert "preflight_context_prior_order_placement_performed_must_be_false" in result["blockers"]


def test_prior_order_attempt_count_must_equal_one():
    result = evaluate(preflight_context=context(prior_order_attempt_count=2))
    assert result["status"] == PREFLIGHT_BLOCKED_CONTEXT
    assert "preflight_context_prior_order_attempt_count_must_equal_one" in result["blockers"]


def test_dry_run_ready_performs_no_network():
    result = evaluate()
    assert result["status"] == PREFLIGHT_DRY_RUN_READY
    assert result["preflight_attempt"]["network_call_performed"] is False
    assert result["preflight_attempt"]["order_placement_performed"] is False


def test_execute_missing_credentials_blocks():
    result = evaluate(execute_preflight=True, http_get_callable=lambda _request: {})
    assert result["status"] == PREFLIGHT_BLOCKED_RUNTIME_CREDENTIALS_MISSING
    assert result["preflight_attempt"]["network_call_performed"] is False


def test_execute_missing_http_get_callable_blocks():
    result = evaluate(
        execute_preflight=True,
        runtime_access_token="TOKEN",
        runtime_account_id="ACCOUNT",
    )
    assert result["status"] == PREFLIGHT_BLOCKED_HTTP_GET_CALLABLE_REQUIRED
    assert result["preflight_attempt"]["network_call_performed"] is False


def test_fake_callable_gets_only_get_requests():
    calls = []

    def fake(request):
        calls.append(request)
        return {"status_code": 200, "status": "success", "body": {}}

    result = run_execute_with_transport(fake)
    assert result["status"] == PREFLIGHT_READ_ONLY_ATTEMPTED
    assert calls
    assert all(call["method"] == "GET" for call in calls)


def test_fake_callable_never_receives_orders_url():
    calls = []

    def fake(request):
        calls.append(request)
        return {"status_code": 200, "status": "success", "body": {}}

    run_execute_with_transport(fake)
    assert all("/orders" not in call["url"] for call in calls)


def test_fake_callable_never_receives_live_url():
    calls = []

    def fake(request):
        calls.append(request)
        return {"status_code": 200, "status": "success", "body": {}}

    run_execute_with_transport(fake)
    assert all("api-fxtrade.oanda.com" not in call["url"] for call in calls)


def test_successful_accounts_list_marks_token_valid_true():
    result = run_execute_with_transport(fake_success_transport)
    assert result["root_cause_summary"]["token_valid"] is True


def test_account_list_without_target_marks_account_visible_false():
    def fake(request):
        if request["url"].endswith("/v3/accounts"):
            return {"status_code": 200, "status": "success", "body": {"accounts": [{"id": "OTHER"}]}}
        return {"status_code": 200, "status": "success", "body": {}}

    result = run_execute_with_transport(fake)
    assert result["root_cause_summary"]["account_visible_to_token"] is False


def test_account_details_403_marks_account_details_accessible_false():
    def fake(request):
        if request["url"].endswith("/v3/accounts"):
            return {"status_code": 200, "status": "success", "body": {"accounts": [{"id": "ACCOUNT"}]}}
        if request["url"].endswith("/summary") or request["url"].endswith("/instruments"):
            return {"status_code": 200, "status": "success", "body": {}}
        return {"status_code": 403, "status": "http_error", "body": {"errorMessage": "forbidden"}}

    result = run_execute_with_transport(fake)
    assert result["root_cause_summary"]["account_details_accessible"] is False


def test_summary_success_marks_summary_accessible_true():
    result = run_execute_with_transport(fake_success_transport)
    assert result["root_cause_summary"]["account_summary_accessible"] is True


def test_instruments_success_with_eur_usd_marks_available_true():
    result = run_execute_with_transport(fake_success_transport)
    assert result["root_cause_summary"]["eur_usd_available"] is True


def test_instruments_without_eur_usd_marks_available_false():
    def fake(request):
        if request["url"].endswith("/v3/accounts"):
            return {"status_code": 200, "status": "success", "body": {"accounts": [{"id": "ACCOUNT"}]}}
        if request["url"].endswith("/instruments"):
            return {"status_code": 200, "status": "success", "body": {"instruments": [{"name": "USD_JPY"}]}}
        return {"status_code": 200, "status": "success", "body": {"account": {"id": "ACCOUNT"}}}

    result = run_execute_with_transport(fake)
    assert result["root_cause_summary"]["eur_usd_available"] is False


def test_sanitized_output_redacts_token_account_authorization():
    def fake(request):
        return {
            "status_code": 200,
            "status": "success",
            "body": {
                "accountID": "RAW_ACCOUNT_123",
                "authorization": "Bearer RAW_TOKEN_456",
                "message": "RAW_TOKEN_456 RAW_ACCOUNT_123",
            },
        }

    result = evaluate(
        execute_preflight=True,
        runtime_access_token="RAW_TOKEN_456",
        runtime_account_id="RAW_ACCOUNT_123",
        http_get_callable=fake,
    )
    evidence = json.dumps(result, sort_keys=True)
    assert "RAW_TOKEN_456" not in evidence
    assert "RAW_ACCOUNT_123" not in evidence
    assert "REDACTED_RUNTIME" in evidence


def test_all_execution_authority_fields_remain_false():
    assert evaluate()["execution_authority"] == EXECUTION_AUTHORITY_FALSE


def test_output_is_json_serializable():
    json.dumps(evaluate(), sort_keys=True)


def test_script_print_template_emits_sanitized_template():
    code, payload = run_script(["--print-template"])
    assert code == 0
    assert payload["script_status"] == "READ_ONLY_PREFLIGHT_TEMPLATE_ONLY"
    assert "REDACTED_RUNTIME_ACCOUNT_ID" in json.dumps(payload, sort_keys=True)
    assert payload["order_placement_performed"] is False


def test_script_dry_run_performs_no_broker_call():
    code, payload = run_script([])
    assert code == 0
    assert payload["script_status"] == "READ_ONLY_PREFLIGHT_DRY_RUN_PREVIEW"
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False


def test_script_execute_without_confirmations_blocks():
    code, payload = run_script(["--execute-read-only-preflight"])
    assert code == 1
    assert payload["script_status"] == "BLOCKED_MISSING_REQUIRED_CONFIRMATIONS"
    assert "--i-confirm-read-only-preflight" in payload["missing_confirmations"]


def test_script_execute_with_confirmations_but_missing_env_blocks(monkeypatch):
    monkeypatch.delenv("OANDA_DEMO_ACCESS_TOKEN", raising=False)
    monkeypatch.delenv("OANDA_DEMO_ACCOUNT_ID", raising=False)
    code, payload = run_script(["--execute-read-only-preflight", *CONFIRMATION_FLAGS])
    assert code == 1
    assert payload["script_status"] == PREFLIGHT_BLOCKED_RUNTIME_CREDENTIALS_MISSING
    assert payload["broker_network_call_performed"] is False


def test_script_uses_injectable_transport_in_tests_without_network(monkeypatch):
    monkeypatch.setenv("OANDA_DEMO_ACCESS_TOKEN", "TOKEN")
    monkeypatch.setenv("OANDA_DEMO_ACCOUNT_ID", "ACCOUNT")
    calls = []

    def fake(request):
        calls.append(request)
        return {"status_code": 200, "status": "success", "body": {}}

    code, payload = run_script(["--execute-read-only-preflight", *CONFIRMATION_FLAGS], transport=fake)
    assert code == 0
    assert calls
    assert payload["script_status"] == PREFLIGHT_READ_ONLY_ATTEMPTED


def test_recursive_sanitizer_redacts_sensitive_keys():
    def fake(_request):
        return {
            "status_code": 200,
            "status": "success",
            "body": {
                "credential": "RAW_TOKEN_456",
                "nested": {"api_key": "RAW_TOKEN_456", "id": "RAW_ACCOUNT_123"},
            },
        }

    result = evaluate(
        execute_preflight=True,
        runtime_access_token="RAW_TOKEN_456",
        runtime_account_id="RAW_ACCOUNT_123",
        http_get_callable=fake,
    )
    evidence = json.dumps(result, sort_keys=True)
    assert "RAW_TOKEN_456" not in evidence
    assert "RAW_ACCOUNT_123" not in evidence


def test_endpoint_planner_rejects_any_mutation_endpoint():
    blockers = validate_oanda_demo_read_only_endpoint_url_v1(
        "https://api-fxpractice.oanda.com/v3/accounts/ACCOUNT/orders"
    )
    assert blockers
    assert any("orders" in blocker for blocker in blockers)


def test_endpoint_planner_rejects_live_url():
    blockers = validate_oanda_demo_read_only_endpoint_url_v1(
        "https://api-fxtrade.oanda.com/v3/accounts"
    )
    assert blockers
    assert any("practice" in blocker or "api-fxtrade" in blocker for blocker in blockers)


def test_endpoint_plan_contains_only_allowed_read_only_urls():
    plan = build_oanda_demo_read_only_endpoint_plan_v1(
        "https://api-fxpractice.oanda.com",
        runtime_account_id="ACCOUNT",
    )
    urls = [endpoint["url"] for endpoint in plan["endpoints"]]
    assert urls == [
        "https://api-fxpractice.oanda.com/v3/accounts",
        "https://api-fxpractice.oanda.com/v3/accounts/ACCOUNT",
        "https://api-fxpractice.oanda.com/v3/accounts/ACCOUNT/summary",
        "https://api-fxpractice.oanda.com/v3/accounts/ACCOUNT/instruments",
    ]
