from __future__ import annotations

import json
from pathlib import Path

from automation.forex_engine.oanda_demo_secure_credential_persistence_windows_vault_v1 import (
    ACCOUNT_ID_CREDENTIAL_NAME,
    ACCESS_TOKEN_CREDENTIAL_NAME,
    MISMATCHED_DEMO_ACCOUNT_REFERENCE,
    TOKEN_VISIBLE_DEMO_ACCOUNT_REFERENCE,
    VAULT_BLOCKED_ACCOUNT_MISMATCH,
    VAULT_BLOCKED_CALLABLE_REQUIRED,
    VAULT_BLOCKED_CONTEXT,
    VAULT_BLOCKED_DEMO_ONLY_REQUIRED,
    VAULT_BLOCKED_SECRET_MISSING,
    VAULT_DELETED,
    VAULT_DRY_RUN_READY,
    VAULT_LOADED_REDACTED,
    VAULT_SAVED,
    VAULT_STATUS_REDACTED,
    default_oanda_demo_secure_credential_persistence_context_v1,
    evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1,
    sanitize_oanda_demo_vault_value_v1,
)
from scripts.forex_delivery.run_oanda_demo_secure_credential_persistence_windows_vault_v1 import (
    main as script_main,
)


TOKEN = "raw_demo_token_value"
VALID_ACCOUNT = "101-001-00000000-001"


def ready_context(**overrides: object) -> dict:
    context = default_oanda_demo_secure_credential_persistence_context_v1()
    context.update(overrides)
    return context


def fake_save_recorder(calls: list[dict]):
    def save(payload: dict) -> dict:
        calls.append(payload)
        return {
            "status": "saved",
            "credential_name": payload["credential_name"],
            "secret_value": payload["secret_value"],
        }

    return save


def fake_load_recorder(calls: list[dict]):
    def load(payload: dict) -> dict:
        calls.append(payload)
        if payload["credential_name"] == ACCESS_TOKEN_CREDENTIAL_NAME:
            return {"credential_name": payload["credential_name"], "secret": TOKEN}
        return {
            "credential_name": payload["credential_name"],
            "account_id": VALID_ACCOUNT,
        }

    return load


def fake_status_recorder(calls: list[dict]):
    def status(payload: dict) -> dict:
        calls.append(payload)
        return {"credential_name": payload["credential_name"], "exists": True}

    return status


def fake_delete_recorder(calls: list[dict]):
    def delete(payload: dict) -> dict:
        calls.append(payload)
        return {"credential_name": payload["credential_name"], "deleted": True}

    return delete


def decision_text(decision: dict) -> str:
    return json.dumps(decision, sort_keys=True)


def test_default_dry_run_ready_with_valid_default_context() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1()

    assert decision["status"] == VAULT_DRY_RUN_READY
    assert decision["vault_attempt"]["broker_call_performed"] is False


def test_non_demo_broker_blocks() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        persistence_context=ready_context(**{"broker": "OANDA_LIVE"})
    )

    assert decision["status"] == VAULT_BLOCKED_DEMO_ONLY_REQUIRED


def test_live_credentials_allowed_true_blocks() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        persistence_context=ready_context(live_credentials_allowed=True)
    )

    assert decision["status"] == VAULT_BLOCKED_DEMO_ONLY_REQUIRED


def test_plaintext_persistence_allowed_true_blocks() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        persistence_context=ready_context(plaintext_persistence_allowed=True)
    )

    assert decision["status"] == VAULT_BLOCKED_CONTEXT


def test_env_file_persistence_allowed_true_blocks() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        persistence_context=ready_context(env_file_persistence_allowed=True)
    )

    assert decision["status"] == VAULT_BLOCKED_CONTEXT


def test_repo_persistence_allowed_true_blocks() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        persistence_context=ready_context(repo_persistence_allowed=True)
    )

    assert decision["status"] == VAULT_BLOCKED_CONTEXT


def test_credential_printing_allowed_true_blocks() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        persistence_context=ready_context(credential_printing_allowed=True)
    )

    assert decision["status"] == VAULT_BLOCKED_CONTEXT


def test_account_id_printing_allowed_true_blocks() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        persistence_context=ready_context(account_id_printing_allowed=True)
    )

    assert decision["status"] == VAULT_BLOCKED_CONTEXT


def test_order_execution_allowed_true_blocks() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        persistence_context=ready_context(order_execution_allowed=True)
    )

    assert decision["status"] == VAULT_BLOCKED_CONTEXT


def test_broker_call_allowed_true_blocks() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        persistence_context=ready_context(broker_call_allowed=True)
    )

    assert decision["status"] == VAULT_BLOCKED_CONTEXT


def test_orders_endpoint_allowed_true_blocks() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        persistence_context=ready_context(orders_endpoint_allowed=True)
    )

    assert decision["status"] == VAULT_BLOCKED_CONTEXT


def test_save_missing_token_blocks() -> None:
    calls: list[dict] = []
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="save",
        runtime_demo_account_id=VALID_ACCOUNT,
        vault_save_callable=fake_save_recorder(calls),
    )

    assert decision["status"] == VAULT_BLOCKED_SECRET_MISSING
    assert calls == []


def test_save_wrong_account_id_blocks() -> None:
    calls: list[dict] = []
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="save",
        runtime_demo_access_token=TOKEN,
        runtime_demo_account_id="WRONG_ACCOUNT",
        vault_save_callable=fake_save_recorder(calls),
    )

    assert decision["status"] == VAULT_BLOCKED_ACCOUNT_MISMATCH
    assert calls == []


def test_save_rejected_mismatched_account_blocks() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="save",
        runtime_demo_access_token=TOKEN,
        runtime_demo_account_id=MISMATCHED_DEMO_ACCOUNT_REFERENCE,
        vault_save_callable=fake_save_recorder([]),
    )

    assert decision["status"] == VAULT_BLOCKED_ACCOUNT_MISMATCH
    assert (
        decision["credential_policy"]["runtime_account_classification"]
        == "prior_mismatched_account_rejected"
    )


def test_save_accepted_token_visible_account_proceeds_with_fake_callable() -> None:
    calls: list[dict] = []
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="save",
        runtime_demo_access_token=TOKEN,
        runtime_demo_account_id=VALID_ACCOUNT,
        vault_save_callable=fake_save_recorder(calls),
    )

    assert decision["status"] == VAULT_SAVED
    assert len(calls) == 2


def test_fake_vault_save_receives_exactly_two_credential_names() -> None:
    calls: list[dict] = []
    evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="save",
        runtime_demo_access_token=TOKEN,
        runtime_demo_account_id=VALID_ACCOUNT,
        vault_save_callable=fake_save_recorder(calls),
    )

    assert [call["credential_name"] for call in calls] == [
        ACCESS_TOKEN_CREDENTIAL_NAME,
        ACCOUNT_ID_CREDENTIAL_NAME,
    ]


def test_fake_vault_save_receives_no_live_credential_names() -> None:
    calls: list[dict] = []
    evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="save",
        runtime_demo_access_token=TOKEN,
        runtime_demo_account_id=VALID_ACCOUNT,
        vault_save_callable=fake_save_recorder(calls),
    )

    assert all("LIVE" not in call["credential_name"] for call in calls)


def test_load_uses_fake_callable_only() -> None:
    calls: list[dict] = []
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="load",
        vault_load_callable=fake_load_recorder(calls),
    )

    assert decision["status"] == VAULT_LOADED_REDACTED
    assert len(calls) == 2


def test_loaded_output_redacts_token() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="load",
        vault_load_callable=fake_load_recorder([]),
        runtime_demo_access_token=TOKEN,
    )

    assert TOKEN not in decision_text(decision)


def test_loaded_output_redacts_account_id() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="load",
        vault_load_callable=fake_load_recorder([]),
        runtime_demo_account_id=VALID_ACCOUNT,
    )

    assert VALID_ACCOUNT not in decision_text(decision)
    assert TOKEN_VISIBLE_DEMO_ACCOUNT_REFERENCE in decision_text(decision)


def test_status_uses_fake_callable_only() -> None:
    calls: list[dict] = []
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="status",
        vault_status_callable=fake_status_recorder(calls),
    )

    assert decision["status"] == VAULT_STATUS_REDACTED
    assert len(calls) == 2


def test_delete_uses_fake_callable_only() -> None:
    calls: list[dict] = []
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="delete",
        vault_delete_callable=fake_delete_recorder(calls),
    )

    assert decision["status"] == VAULT_DELETED
    assert len(calls) == 2


def test_delete_does_not_call_broker() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="delete",
        vault_delete_callable=fake_delete_recorder([]),
    )

    assert decision["vault_attempt"]["broker_call_performed"] is False
    assert decision["vault_attempt"]["broker_network_call_performed"] is False


def test_no_orders_endpoint_appears_in_output() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1()

    assert "/orders" not in decision_text(decision)


def test_no_broker_network_call_happens() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1()

    assert decision["vault_attempt"]["broker_network_call_performed"] is False


def test_all_execution_authority_fields_remain_false() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1()

    assert decision["execution_authority"]
    assert all(value is False for value in decision["execution_authority"].values())


def test_output_is_json_serializable() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1()

    json.dumps(decision, sort_keys=True)


def test_recursive_sanitizer_redacts_sensitive_keys() -> None:
    sanitized = sanitize_oanda_demo_vault_value_v1(
        {
            "token": TOKEN,
            "account_id": VALID_ACCOUNT,
            "password": "pw",
            "secret": "sec",
            "api_key": "api",
            "credential": "cred",
            "nested": {"Authorization": f"Bearer {TOKEN}"},
        },
        runtime_demo_access_token=TOKEN,
        runtime_demo_account_id=VALID_ACCOUNT,
    )
    text = json.dumps(sanitized, sort_keys=True)

    assert TOKEN not in text
    assert VALID_ACCOUNT not in text
    assert "pw" not in text
    assert '"secret": "sec"' not in text
    assert '"api_key": "api"' not in text
    assert '"credential": "cred"' not in text


def test_script_print_template_emits_no_secrets(capsys) -> None:
    exit_code = script_main(["--print-template"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert TOKEN not in output
    assert VALID_ACCOUNT not in output


def test_script_dry_run_performs_no_vault_mutation(capsys) -> None:
    exit_code = script_main(["--dry-run"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["decision"]["status"] == VAULT_DRY_RUN_READY
    assert payload["vault_mutation_performed"] is False


def test_script_save_without_confirmations_blocks(capsys) -> None:
    exit_code = script_main(["--save"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["script_status"] == "BLOCKED_MISSING_REQUIRED_CONFIRMATIONS"


def test_script_delete_without_confirmations_blocks(capsys) -> None:
    exit_code = script_main(["--delete"])
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["script_status"] == "BLOCKED_MISSING_REQUIRED_CONFIRMATIONS"


def test_script_status_does_not_require_token(capsys) -> None:
    exit_code = script_main(
        ["--status"],
        vault_status_callable=fake_status_recorder([]),
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 0
    assert payload["decision"]["status"] == VAULT_STATUS_REDACTED


def test_script_load_returns_redacted_values_only(capsys) -> None:
    exit_code = script_main(
        ["--load"],
        vault_load_callable=fake_load_recorder([]),
    )
    output = capsys.readouterr().out

    assert exit_code == 0
    assert TOKEN not in output
    assert VALID_ACCOUNT not in output
    assert json.loads(output)["decision"]["status"] == VAULT_LOADED_REDACTED


def test_rejected_account_id_appears_only_as_redacted_reference() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="save",
        runtime_demo_access_token=TOKEN,
        runtime_demo_account_id=MISMATCHED_DEMO_ACCOUNT_REFERENCE,
        vault_save_callable=fake_save_recorder([]),
    )
    text = decision_text(decision)

    assert MISMATCHED_DEMO_ACCOUNT_REFERENCE in text
    assert "001-001-" not in text


def test_accepted_account_id_appears_only_as_redacted_reference() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="save",
        runtime_demo_access_token=TOKEN,
        runtime_demo_account_id=VALID_ACCOUNT,
        vault_save_callable=fake_save_recorder([]),
    )
    text = decision_text(decision)

    assert TOKEN_VISIBLE_DEMO_ACCOUNT_REFERENCE in text
    assert VALID_ACCOUNT not in text


def test_no_env_strings_are_used_as_a_read_source() -> None:
    script_source = Path(
        "scripts/forex_delivery/run_oanda_demo_secure_credential_persistence_windows_vault_v1.py"
    ).read_text(encoding="utf-8")

    assert "dotenv" not in script_source.lower()
    assert "os.environ" not in script_source


def test_no_order_execution_path_exists() -> None:
    module_source = Path(
        "automation/forex_engine/oanda_demo_secure_credential_persistence_windows_vault_v1.py"
    ).read_text(encoding="utf-8")
    script_source = Path(
        "scripts/forex_delivery/run_oanda_demo_secure_credential_persistence_windows_vault_v1.py"
    ).read_text(encoding="utf-8")

    assert "/orders" not in module_source
    assert "/orders" not in script_source
    assert "urlopen" not in module_source
    assert "urlopen" not in script_source


def test_save_without_callable_blocks() -> None:
    decision = evaluate_oanda_demo_secure_credential_persistence_windows_vault_v1(
        requested_action="save",
        runtime_demo_access_token=TOKEN,
        runtime_demo_account_id=VALID_ACCOUNT,
    )

    assert decision["status"] == VAULT_BLOCKED_CALLABLE_REQUIRED
