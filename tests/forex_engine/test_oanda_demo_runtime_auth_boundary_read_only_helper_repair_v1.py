from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_runtime_auth_boundary_read_only_helper_repair_v1 import (  # noqa: E402
    BROKER_EVIDENCE_BLOCKED,
    INTERNAL_LEDGER_ONLY,
    READ_ONLY_HELPER_CONTRACT_READY,
    READ_ONLY_HELPER_MISSING,
    READ_ONLY_HELPER_RESULT_ACCEPTED_SANITIZED,
    READ_ONLY_HELPER_RESULT_REJECTED_UNSANITIZED,
    SECRET_RISK_DETECTED,
    evaluate_runtime_auth_boundary_read_only_helper_repair,
    validate_sanitized_read_only_helper_result,
    write_runtime_auth_boundary_read_only_helper_repair_report,
)
from scripts.forex_delivery.run_oanda_demo_runtime_auth_boundary_read_only_helper_repair_v1 import (  # noqa: E402
    main as script_main,
)


def sanitized_helper_result() -> dict:
    return {
        "trade_id": 320,
        "instrument": "EUR_USD",
        "side": "long",
        "units": 1,
        "entry_price": "1.13596",
        "realized_pl": "0.0000",
        "unrealized_pl": "-0.0004",
        "open_trade_count": 1,
        "open_position_count": 1,
        "monitor_bucket": "OPEN_UNREALIZED_NEGATIVE",
        "result_bucket": "NO_PROFIT_EVIDENCE_OPEN_NEGATIVE",
        "broker_read_mode": "OWNER_RUN_READ_ONLY_BROKER_REQUESTED",
        "broker_evidence_status": "OWNER_RUN_READ_ONLY_EVIDENCE_CLASSIFIED",
        "evidence_timestamp_utc": "2026-06-25T00:00:00Z",
        "evidence_source": "owner_run_read_only_helper_sanitized",
        "broker_read_method": "GET",
        "sanitized_evidence_only": True,
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
        "withdrawal_allowed_now": False,
        "transfer_allowed_now": False,
        "money_movement_allowed_now": False,
        "profit_reserve_bucket_mode": INTERNAL_LEDGER_ONLY,
    }


def run_script(args: list[str]) -> tuple[int, dict]:
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def test_default_contract_ready_but_broker_read_not_allowed_by_default() -> None:
    result = evaluate_runtime_auth_boundary_read_only_helper_repair()

    assert result["runtime_auth_boundary_status"] == READ_ONLY_HELPER_CONTRACT_READY
    assert result["read_only_helper_contract_ready"] is True
    assert result["broker_read_allowed_by_default"] is False
    assert result["broker_evidence_status"] == BROKER_EVIDENCE_BLOCKED


def test_owner_run_flag_is_required() -> None:
    result = evaluate_runtime_auth_boundary_read_only_helper_repair()

    assert result["owner_run_required"] is True
    assert result["broker_read_requires_owner_flag"] is True


def test_get_read_only_is_required() -> None:
    result = validate_sanitized_read_only_helper_result(sanitized_helper_result())

    assert result["broker_read_must_be_get_only"] is True
    rejected = sanitized_helper_result()
    rejected["broker_read_method"] = "POST"
    assert (
        "broker_read_method_must_be_get"
        in validate_sanitized_read_only_helper_result(rejected)["blockers"]
    )


def test_raw_broker_payload_persistence_is_false() -> None:
    result = evaluate_runtime_auth_boundary_read_only_helper_repair()

    assert result["raw_broker_payload_persistence_allowed"] is False


def test_account_identifier_auth_and_token_logging_are_false() -> None:
    result = evaluate_runtime_auth_boundary_read_only_helper_repair()

    assert result["account_identifier_logging_allowed"] is False
    assert result["auth_header_logging_allowed"] is False
    assert result["token_logging_allowed"] is False


def test_sanitized_helper_result_with_allowed_fields_is_accepted() -> None:
    result = validate_sanitized_read_only_helper_result(sanitized_helper_result())

    assert (
        result["runtime_auth_boundary_status"]
        == READ_ONLY_HELPER_RESULT_ACCEPTED_SANITIZED
    )
    assert result["sanitized_broker_telemetry_ready"] is True
    assert "trade_id" in result["accepted_sanitized_fields"]
    assert "unrealized_pl" in result["accepted_sanitized_fields"]


def test_helper_result_with_token_secret_account_or_raw_payload_is_rejected() -> None:
    for field in ("token", "secret", "account_id"):
        evidence = sanitized_helper_result()
        evidence[field] = "SHOULD_NOT_BE_ACCEPTED"
        result = validate_sanitized_read_only_helper_result(evidence)
        assert result["runtime_auth_boundary_status"] == SECRET_RISK_DETECTED

    evidence = sanitized_helper_result()
    evidence["raw_broker_payload"] = {"anything": "forbidden"}
    result = validate_sanitized_read_only_helper_result(evidence)
    assert (
        result["runtime_auth_boundary_status"]
        == READ_ONLY_HELPER_RESULT_REJECTED_UNSANITIZED
    )


def test_nested_secret_like_field_is_rejected() -> None:
    evidence = sanitized_helper_result()
    evidence["metadata"] = {"auth_header": "Bearer SHOULD_NOT_BE_ACCEPTED"}

    result = validate_sanitized_read_only_helper_result(evidence)

    assert result["runtime_auth_boundary_status"] == SECRET_RISK_DETECTED
    assert "metadata_auth_header" in result["rejected_secret_fields"]


def test_missing_helper_or_broker_blocked_evidence_maps_to_expected_status() -> None:
    missing = validate_sanitized_read_only_helper_result(
        {"read_only_helper_missing": True}
    )
    blocked = validate_sanitized_read_only_helper_result(
        {
            "broker_evidence_status": BROKER_EVIDENCE_BLOCKED,
            "blockers": ["broker_evidence_blocked"],
            "sanitized_evidence_only": True,
            "no_new_order_placed": True,
            "no_live_trade_placed": True,
            "no_broker_state_modified": True,
            "no_secrets_written": True,
        }
    )

    assert missing["runtime_auth_boundary_status"] == READ_ONLY_HELPER_MISSING
    assert blocked["runtime_auth_boundary_status"] == BROKER_EVIDENCE_BLOCKED


def test_fake_or_mock_dashboard_numbers_remain_forbidden() -> None:
    result = evaluate_runtime_auth_boundary_read_only_helper_repair()

    assert result["dashboard_real_broker_telemetry_goal"] is True
    assert result["dashboard_fake_numbers_allowed"] is False
    assert result["dashboard_mock_numbers_allowed"] is False


def test_money_movement_remains_blocked() -> None:
    result = evaluate_runtime_auth_boundary_read_only_helper_repair()

    assert result["withdrawal_allowed_now"] is False
    assert result["transfer_allowed_now"] is False
    assert result["money_movement_allowed_now"] is False
    assert result["profit_reserve_bucket_mode"] == INTERNAL_LEDGER_ONLY


def test_cli_default_emits_json_without_broker_call() -> None:
    code, payload = run_script(["--json"])

    assert code == 0
    assert payload["script_status"] == READ_ONLY_HELPER_CONTRACT_READY
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["live_endpoint_used"] is False
    assert payload["secrets_written"] is False


def test_report_writer_includes_no_order_no_live_no_broker_state_no_secrets(
    tmp_path: Path,
) -> None:
    result = evaluate_runtime_auth_boundary_read_only_helper_repair()
    report_path = tmp_path / "runtime_auth_boundary_report.md"

    write_runtime_auth_boundary_read_only_helper_repair_report(result, report_path)

    text = report_path.read_text(encoding="utf-8")
    assert "no new order placed" in text
    assert "no live trade placed" in text
    assert "no broker state modified" in text
    assert "no secrets written" in text
    assert "fake/mock dashboard account values are forbidden" in text

