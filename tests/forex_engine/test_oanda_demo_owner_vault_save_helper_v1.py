from __future__ import annotations

import json
from pathlib import Path

import pytest

from automation.forex_engine.oanda_demo_owner_vault_save_helper_v1 import (
    ACCOUNT_ID_CREDENTIAL_NAME,
    ACCESS_TOKEN_CREDENTIAL_NAME,
    OWNER_VAULT_SAVE_BLOCKED_MISSING_CONFIRMATIONS,
    OWNER_VAULT_SAVE_BLOCKED_NON_WINDOWS,
    OWNER_VAULT_SAVE_BLOCKED_VALUES_MISSING,
    OWNER_VAULT_SAVE_SAVED,
    OWNER_VAULT_SAVE_TEMPLATE_ONLY,
    READ_ONLY_PREFLIGHT_RERUN_COMMAND,
    owner_vault_save_template_v1,
    save_owner_oanda_demo_values_to_windows_vault_v1,
    save_to_windows_credential_manager_v1,
)
from scripts.forex_delivery import run_oanda_demo_owner_vault_save_helper_v1 as runner


VALUE_ONE = "owner-runtime-hidden-one"
VALUE_TWO = "owner-runtime-hidden-two"

CONFIRMATIONS = [
    "--i-confirm-demo-only",
    "--i-confirm-windows-vault-only",
    "--i-confirm-no-env-file",
    "--i-confirm-no-repo-persistence",
    "--i-confirm-no-value-printing",
]


def test_template_reports_labels_and_no_values() -> None:
    payload = owner_vault_save_template_v1()
    text = json.dumps(payload, sort_keys=True)

    assert payload["script_status"] == OWNER_VAULT_SAVE_TEMPLATE_ONLY
    assert payload["labels_saved"] is False
    assert ACCESS_TOKEN_CREDENTIAL_NAME in payload["approved_labels"]
    assert ACCOUNT_ID_CREDENTIAL_NAME in payload["approved_labels"]
    assert "command_line_value_arguments_supported" in text
    assert VALUE_ONE not in text
    assert VALUE_TWO not in text


def test_missing_confirmations_blocks_before_prompt(capsys) -> None:
    def fail_prompt(prompt: str) -> str:
        raise AssertionError("prompt must not run without confirmations")

    exit_code = runner.main(
        ["--owner-save-to-windows-vault"],
        token_prompt_callable=fail_prompt,
        account_prompt_callable=fail_prompt,
        vault_save_callable=_fake_save([]),
    )
    payload = json.loads(capsys.readouterr().out)

    assert exit_code == 1
    assert payload["script_status"] == OWNER_VAULT_SAVE_BLOCKED_MISSING_CONFIRMATIONS
    assert payload["labels_saved"] is False


def test_owner_save_uses_hidden_prompts_and_fake_save_only(capsys) -> None:
    calls: list[dict] = []
    exit_code = runner.main(
        ["--owner-save-to-windows-vault", *CONFIRMATIONS],
        token_prompt_callable=lambda prompt: VALUE_ONE,
        account_prompt_callable=lambda prompt: VALUE_TWO,
        vault_save_callable=_fake_save(calls),
        platform_name="win32",
    )
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert exit_code == 0
    assert payload["script_status"] == OWNER_VAULT_SAVE_SAVED
    assert payload["labels_saved"] is True
    assert [call["credential_name"] for call in calls] == [
        ACCESS_TOKEN_CREDENTIAL_NAME,
        ACCOUNT_ID_CREDENTIAL_NAME,
    ]
    assert VALUE_ONE not in output
    assert VALUE_TWO not in output
    assert payload["read_only_preflight_rerun_command"] == READ_ONLY_PREFLIGHT_RERUN_COMMAND


def test_module_save_result_ignores_echoed_fake_values() -> None:
    calls: list[dict] = []
    payload = save_owner_oanda_demo_values_to_windows_vault_v1(
        runtime_demo_access_token=VALUE_ONE,
        runtime_demo_account_id=VALUE_TWO,
        vault_save_callable=_fake_save(calls, echo=True),
        platform_name="win32",
    )
    text = json.dumps(payload, sort_keys=True)

    assert payload["labels_saved"] is True
    assert VALUE_ONE not in text
    assert VALUE_TWO not in text


def test_missing_runtime_values_block_without_save_call() -> None:
    calls: list[dict] = []
    payload = save_owner_oanda_demo_values_to_windows_vault_v1(
        runtime_demo_access_token="",
        runtime_demo_account_id=VALUE_TWO,
        vault_save_callable=_fake_save(calls),
    )

    assert payload["script_status"] == OWNER_VAULT_SAVE_BLOCKED_VALUES_MISSING
    assert calls == []


def test_windows_adapter_blocks_non_windows_without_reading_vault() -> None:
    payload = save_to_windows_credential_manager_v1(
        {
            "credential_name": ACCESS_TOKEN_CREDENTIAL_NAME,
            "secret_value": VALUE_ONE,
            "platform_name": "linux",
        }
    )

    assert payload["value_saved"] is False
    assert payload["status"] == "blocked_non_windows_platform"


def test_non_windows_owner_save_reports_blocked() -> None:
    payload = save_owner_oanda_demo_values_to_windows_vault_v1(
        runtime_demo_access_token=VALUE_ONE,
        runtime_demo_account_id=VALUE_TWO,
        platform_name="linux",
    )

    assert payload["script_status"] == OWNER_VAULT_SAVE_BLOCKED_NON_WINDOWS
    assert payload["labels_saved"] is False


def test_cli_rejects_value_arguments_without_echo(capsys) -> None:
    with pytest.raises(SystemExit) as exc:
        runner.main(["--owner-save-to-windows-vault", "--demo-account-id", VALUE_TWO])
    output = capsys.readouterr().out
    payload = json.loads(output)

    assert exc.value.code == 2
    assert payload["script_status"] == "BLOCKED_INVALID_ARGUMENTS"
    assert VALUE_TWO not in output


def test_new_helper_sources_do_not_read_vault_or_environment() -> None:
    module_source = Path(
        "automation/forex_engine/oanda_demo_owner_vault_save_helper_v1.py"
    ).read_text(encoding="utf-8")
    script_source = Path(
        "scripts/forex_delivery/run_oanda_demo_owner_vault_save_helper_v1.py"
    ).read_text(encoding="utf-8")

    combined = module_source + script_source
    assert "CredRead" not in combined
    assert "os.environ" not in combined
    assert "load_dotenv" not in combined
    assert "python-dotenv" not in combined
    assert "subprocess" not in combined


def test_new_helper_sources_have_no_broker_call_path() -> None:
    module_source = Path(
        "automation/forex_engine/oanda_demo_owner_vault_save_helper_v1.py"
    ).read_text(encoding="utf-8")
    script_source = Path(
        "scripts/forex_delivery/run_oanda_demo_owner_vault_save_helper_v1.py"
    ).read_text(encoding="utf-8")

    combined = module_source + script_source
    assert "urlopen" not in combined
    assert "/orders" not in combined


def _fake_save(calls: list[dict], *, echo: bool = False):
    def save(payload: dict) -> dict:
        calls.append(payload)
        result = {
            "credential_name": payload["credential_name"],
            "value_saved": True,
            "status": "fake_saved",
        }
        if echo:
            result["secret_value"] = payload["secret_value"]
        return result

    return save
