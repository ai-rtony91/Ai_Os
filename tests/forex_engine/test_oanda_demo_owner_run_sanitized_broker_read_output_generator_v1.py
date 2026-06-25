from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine import oanda_demo_owner_read_required_sanitized_fields_capture_v1 as capture  # noqa: E402
from automation.forex_engine import oanda_demo_owner_run_sanitized_broker_read_output_generator_v1 as generator  # noqa: E402
from automation.forex_engine.oanda_demo_sanitized_evidence_normalizer_acceptance_run_v1 import (  # noqa: E402
    SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED,
    run_sanitized_evidence_normalizer_acceptance,
)
from scripts.forex_delivery.run_oanda_demo_owner_run_sanitized_broker_read_output_generator_v1 import (  # noqa: E402
    main as script_main,
)


def complete_owner_read_result() -> dict:
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
        "repeat_proof_lane_status": "NOT_STARTED_NO_PROFIT_EVIDENCE",
        "repeat_proof_eligible": False,
        "profit_evidence": False,
        "broker_read_mode": "OWNER_RUN_READ_ONLY_BROKER_REQUESTED",
        "broker_evidence_status": "OWNER_RUN_READ_ONLY_EVIDENCE_CLASSIFIED",
        "evidence_timestamp_utc": "2026-06-25T00:00:00Z",
        "evidence_source": "OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_V1",
        "broker_network_call_performed": True,
        "broker_read_performed": True,
        "live_endpoint_used": False,
        "order_placement_performed": False,
        "order_mutation_performed": False,
        "order_close_performed": False,
        "position_mutation_performed": False,
        "trade_mutation_performed": False,
        "raw_broker_payload_persisted": False,
        "secrets_written": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
    }


def packet12d_alias_owner_read_result() -> dict:
    return {
        "trade_id": 320,
        "instrument": "EUR_USD",
        "signed_units": "-1",
        "openTradePrice": "1.13596",
        "realizedPL": "0.0000",
        "trueUnrealizedPL": "-0.0004",
        "openTradeCount": 1,
        "openPositionCount": 1,
        "current_bucket_result": "OPEN_UNREALIZED_NEGATIVE",
        "pl_capture_classification": "NO_PROFIT_EVIDENCE_OPEN_NEGATIVE",
        "repeat_proof_lane_status": "NOT_STARTED_NO_PROFIT_EVIDENCE",
        "repeat_proof_eligible": False,
        "profit_evidence": False,
        "broker_read_mode": "OWNER_RUN_READ_ONLY_BROKER_REQUESTED",
        "lastTransactionTime": "2026-06-25T00:00:00Z",
        "evidence_source": "OWNER_RUN_OPEN_TRADE_MONITOR_PL_REFRESH_HELPER",
        "broker_network_call_performed": True,
        "broker_read_performed": True,
        "live_endpoint_used": False,
        "order_placement_performed": False,
        "order_mutation_performed": False,
        "order_close_performed": False,
        "position_mutation_performed": False,
        "trade_mutation_performed": False,
        "raw_broker_payload_persisted": False,
        "secrets_written": False,
        "credential_read_performed": False,
        "account_id_read_performed": False,
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
    }


def write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def run_script(args: list[str]) -> tuple[int, dict]:
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def test_default_result_does_not_call_broker_and_reports_not_requested():
    result = generator.generate_owner_run_sanitized_broker_read_output()

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_READY_FOR_OWNER_RUN
    )
    assert result["safe_owner_read_helper_status"] == (
        generator.SAFE_OWNER_READ_HELPER_BOUND
    )
    assert result["safe_owner_read_helper_bound"] is True
    assert result["owner_run_read_broker_now"] is False
    assert result["broker_read_performed"] is False
    assert result["broker_network_call_performed"] is False
    assert result["next_action"] == generator.OWNER_RUN_READY_NEXT_ACTION


def test_default_does_not_write_json(tmp_path):
    result = generator.generate_owner_run_sanitized_broker_read_output(
        write_json=True,
        json_path=str(tmp_path / "owner_read_output.json"),
    )

    assert result["json_written"] is False
    assert not (tmp_path / "owner_read_output.json").exists()


def test_helper_is_not_called_when_owner_run_flag_is_absent():
    calls: list[str] = []

    def helper() -> dict:
        calls.append("called")
        return complete_owner_read_result()

    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_read_helper=helper,
        owner_read_helper_name="mock_safe_owner_read_helper",
        owner_read_helper_proven_safe=True,
    )

    assert calls == []
    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_READY_FOR_OWNER_RUN
    )
    assert result["safe_owner_read_helper_bound"] is True


def test_owner_run_flag_with_no_proven_safe_helper_fails_closed(monkeypatch):
    def blocked_binding() -> dict:
        return generator._unbound_safe_owner_read_helper(
            generator.SAFE_OWNER_READ_HELPER_NOT_PROVEN_SAFE,
            "mock_unproven_helper",
            "mock_helper_not_proven_safe",
        )

    monkeypatch.setattr(
        generator,
        "_resolve_safe_owner_read_helper",
        blocked_binding,
    )

    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_run_read_broker_now=True,
        write_json=True,
        json_path="never_written.json",
    )

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_HELPER_NOT_PROVEN_SAFE
    )
    assert result["safe_owner_read_helper_bound"] is False
    assert result["broker_read_performed"] is False
    assert result["broker_network_call_performed"] is False


def test_proven_safe_helper_can_be_injected_and_marked_bound():
    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_run_read_broker_now=True,
        owner_read_helper=complete_owner_read_result,
        owner_read_helper_name="mock_safe_owner_read_helper",
        owner_read_helper_proven_safe=True,
    )

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_READY
    )
    assert result["safe_owner_read_helper_status"] == (
        generator.SAFE_OWNER_READ_HELPER_BOUND
    )
    assert result["safe_owner_read_helper_name"] == "mock_safe_owner_read_helper"
    assert result["safe_owner_read_helper_bound"] is True


def test_missing_required_fields_blocks_output():
    payload = complete_owner_read_result()
    payload.pop("realized_pl")
    payload.pop("open_trade_count")

    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_read_result=payload,
    )

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_MISSING_FIELDS
    )
    assert result["json_written"] is False
    assert "realized_pl" in result["missing_required_fields"]
    assert "open_trade_count" in result["missing_required_fields"]


def test_complete_safe_injected_owner_read_result_is_ready():
    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_read_result=complete_owner_read_result(),
    )

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_READY
    )
    assert result["sanitized_output_ready"] is True
    assert result["required_fields_present"] is True


def test_complete_safe_injected_owner_read_result_writes_json_when_requested(tmp_path):
    output = tmp_path / "owner_read_output.json"

    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_read_result=complete_owner_read_result(),
        write_json=True,
        json_path=str(output),
    )

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_WRITTEN
    )
    assert result["json_written"] is True
    assert output.exists()


def test_packet12d_alias_output_completes_required_fields_and_writes_json(tmp_path):
    output = tmp_path / "owner_read_output.json"

    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_read_result=packet12d_alias_owner_read_result(),
        write_json=True,
        json_path=str(output),
    )
    exported = json.loads(output.read_text(encoding="utf-8"))

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_WRITTEN
    )
    assert result["json_written"] is True
    assert result["sanitized_output_ready"] is True
    assert result["required_fields_present"] is True
    assert result["missing_required_fields"] == []
    assert exported["side"] == "short"
    assert exported["units"] == -1
    assert exported["entry_price"] == "1.13596"
    assert exported["realized_pl"] == "0.0000"
    assert exported["unrealized_pl"] == "-0.0004"
    assert exported["monitor_bucket"] == "OPEN_UNREALIZED_NEGATIVE"
    assert exported["result_bucket"] == "NO_PROFIT_EVIDENCE_OPEN_NEGATIVE"
    assert exported["broker_evidence_status"] == (
        generator.SAFE_INTERNAL_BROKER_EVIDENCE_STATUS
    )
    assert exported["evidence_timestamp_utc"] == "2026-06-25T00:00:00Z"


def test_packet12d_alias_output_still_blocks_when_true_market_field_absent(tmp_path):
    payload = packet12d_alias_owner_read_result()
    payload.pop("openTradePrice")
    output = tmp_path / "owner_read_output.json"

    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_read_result=payload,
        write_json=True,
        json_path=str(output),
    )

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_MISSING_FIELDS
    )
    assert result["json_written"] is False
    assert "entry_price" in result["missing_required_fields"]
    assert not output.exists()


def test_exported_json_contains_only_accepted_safe_fields(tmp_path):
    payload = complete_owner_read_result()
    payload["local_note"] = "not exported"
    output = tmp_path / "owner_read_output.json"

    generator.generate_owner_run_sanitized_broker_read_output(
        owner_read_result=payload,
        write_json=True,
        json_path=str(output),
    )
    exported = json.loads(output.read_text(encoding="utf-8"))

    assert set(exported) <= generator.EXPORT_FIELD_SET
    assert "local_note" not in exported
    assert "credential_read_performed" not in exported
    assert "account_id_read_performed" not in exported


def test_proven_safe_helper_output_is_reduced_to_sanitized_fields_only(tmp_path):
    payload = complete_owner_read_result()
    payload["local_note"] = "not exported"
    output = tmp_path / "owner_read_output.json"

    generator.generate_owner_run_sanitized_broker_read_output(
        owner_run_read_broker_now=True,
        owner_read_helper=lambda: payload,
        owner_read_helper_name="mock_safe_owner_read_helper",
        owner_read_helper_proven_safe=True,
        write_json=True,
        json_path=str(output),
    )
    exported = json.loads(output.read_text(encoding="utf-8"))

    assert set(exported) <= generator.EXPORT_FIELD_SET
    assert "local_note" not in exported


def test_merged_monitor_pl_helper_output_writes_required_packet12d_fields(tmp_path):
    monitor_payload = {
        "broker_network_call_performed": True,
        "lastTransactionTime": "2026-06-25T00:00:00Z",
        "live_endpoint_used": False,
        "order_placement_performed": False,
        "order_mutation_performed": False,
        "order_close_performed": False,
        "position_mutation_performed": False,
        "trade_mutation_performed": False,
        "secrets_written": False,
    }
    monitor_result = {
        "tradeID": 320,
        "pair": "EUR_USD",
        "currentUnits": "-1",
        "openTradePrice": "1.13596",
        "openTradeCount": 1,
        "openPositionCount": 1,
        "current_bucket_result": "OPEN_UNREALIZED_NEGATIVE",
    }
    pl_result = {
        "realizedPL": "0.0000",
        "trueUnrealizedPL": "-0.0004",
        "pl_result_bucket": "NO_PROFIT_EVIDENCE_OPEN_NEGATIVE",
        "repeat_proof_lane_status": "NOT_STARTED_NO_PROFIT_EVIDENCE",
        "repeat_proof_eligible": False,
        "profit_evidence": False,
        "broker_read_mode": "OWNER_RUN_READ_ONLY_BROKER_REQUESTED",
        "source": "OWNER_RUN_OPEN_TRADE_MONITOR_PL_REFRESH_HELPER",
    }
    helper_output = generator._merged_monitor_pl_output(
        monitor_payload,
        monitor_result,
        pl_result,
    )
    output = tmp_path / "owner_read_output.json"

    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_run_read_broker_now=True,
        owner_read_helper=lambda: helper_output,
        owner_read_helper_name="mock_safe_owner_read_helper",
        owner_read_helper_proven_safe=True,
        write_json=True,
        json_path=str(output),
    )
    exported = json.loads(output.read_text(encoding="utf-8"))

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_WRITTEN
    )
    assert result["json_written"] is True
    assert result["broker_read_performed"] is True
    assert exported["side"] == "short"
    assert exported["monitor_bucket"] == "OPEN_UNREALIZED_NEGATIVE"
    assert exported["result_bucket"] == "NO_PROFIT_EVIDENCE_OPEN_NEGATIVE"
    assert exported["broker_evidence_status"] == (
        generator.SAFE_INTERNAL_BROKER_EVIDENCE_STATUS
    )
    assert exported["evidence_timestamp_utc"] == "2026-06-25T00:00:00Z"


def test_raw_helper_output_is_never_persisted(tmp_path):
    payload = complete_owner_read_result()
    payload["raw_response"] = {"forbidden": "payload"}
    output = tmp_path / "owner_read_output.json"

    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_run_read_broker_now=True,
        owner_read_helper=lambda: payload,
        owner_read_helper_name="mock_safe_owner_read_helper",
        owner_read_helper_proven_safe=True,
        write_json=True,
        json_path=str(output),
    )

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_RAW_PAYLOAD_RISK
    )
    assert result["json_written"] is False
    assert not output.exists()


def test_exported_json_works_with_packet12b_capture_wrapper(tmp_path):
    output = tmp_path / "owner_read_output.json"
    generator.generate_owner_run_sanitized_broker_read_output(
        owner_read_result=complete_owner_read_result(),
        write_json=True,
        json_path=str(output),
    )

    exported = json.loads(output.read_text(encoding="utf-8"))
    capture_result = capture.capture_required_sanitized_fields_from_owner_read(
        exported,
    )

    assert capture_result["capture_status"] == (
        capture.OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_READY
    )
    assert capture_result["sanitized_evidence_ready"] is True


def test_packet12b_output_works_with_packet11_acceptance_wrapper(tmp_path):
    owner_output = tmp_path / "owner_read_output.json"
    packet09_output = tmp_path / "packet09.json"
    generator.generate_owner_run_sanitized_broker_read_output(
        owner_read_result=complete_owner_read_result(),
        write_json=True,
        json_path=str(owner_output),
    )
    exported = json.loads(owner_output.read_text(encoding="utf-8"))

    capture.capture_required_sanitized_fields_from_owner_read(
        exported,
        write_json=True,
        json_path=str(packet09_output),
    )
    packet09 = json.loads(packet09_output.read_text(encoding="utf-8"))
    acceptance = run_sanitized_evidence_normalizer_acceptance(packet09)

    assert acceptance["acceptance_status"] == (
        SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED
    )


def test_forbidden_token_secret_account_fields_reject():
    for field in ("access_token", "secret", "account_id"):
        payload = complete_owner_read_result()
        payload[field] = "forbidden"

        result = generator.generate_owner_run_sanitized_broker_read_output(
            owner_read_result=payload,
        )

        assert result["output_status"] == (
            generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_SECRET_RISK
        )
        assert field in result["rejected_forbidden_fields"]


def test_raw_payload_raw_response_fields_reject():
    for field in ("raw_payload", "raw_response"):
        payload = complete_owner_read_result()
        payload[field] = {"forbidden": "payload"}

        result = generator.generate_owner_run_sanitized_broker_read_output(
            owner_read_result=payload,
        )

        assert result["output_status"] == (
            generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_RAW_PAYLOAD_RISK
        )
        assert field in result["rejected_forbidden_fields"]


def test_helper_output_with_forbidden_fields_rejects():
    payload = complete_owner_read_result()
    payload["secret"] = "forbidden"

    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_run_read_broker_now=True,
        owner_read_helper=lambda: payload,
        owner_read_helper_name="mock_safe_owner_read_helper",
        owner_read_helper_proven_safe=True,
    )

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_SECRET_RISK
    )


def test_helper_output_with_raw_payload_markers_rejects():
    payload = complete_owner_read_result()
    payload["raw_payload"] = {"forbidden": "payload"}

    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_run_read_broker_now=True,
        owner_read_helper=lambda: payload,
        owner_read_helper_name="mock_safe_owner_read_helper",
        owner_read_helper_proven_safe=True,
    )

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_RAW_PAYLOAD_RISK
    )


def test_nested_forbidden_fields_reject():
    payload = complete_owner_read_result()
    payload["nested"] = {"authorization": "forbidden"}

    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_read_result=payload,
    )

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_SECRET_RISK
    )
    assert "nested_authorization" in result["rejected_forbidden_fields"]


def test_unsafe_audit_true_flags_reject():
    payload = complete_owner_read_result()
    payload["order_close_performed"] = True

    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_read_result=payload,
    )

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_UNSAFE_AUDIT_FLAG
    )
    assert "order_close_performed" in result["unsafe_audit_flags"]


def test_helper_output_with_unsafe_audit_flags_rejects():
    payload = complete_owner_read_result()
    payload["trade_mutation_performed"] = True

    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_run_read_broker_now=True,
        owner_read_helper=lambda: payload,
        owner_read_helper_name="mock_safe_owner_read_helper",
        owner_read_helper_proven_safe=True,
    )

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_REJECTED_UNSAFE_AUDIT_FLAG
    )
    assert "trade_mutation_performed" in result["unsafe_audit_flags"]


def test_safe_audit_false_flags_pass():
    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_read_result=complete_owner_read_result(),
    )

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_READY
    )
    assert result["unsafe_audit_flags"] == []


def test_money_movement_remains_blocked():
    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_read_result=complete_owner_read_result(),
    )

    assert result["withdrawal_allowed_now"] is False
    assert result["transfer_allowed_now"] is False
    assert result["money_movement_allowed_now"] is False
    assert result["profit_reserve_bucket_mode"] == generator.INTERNAL_LEDGER_ONLY


def test_fake_mock_numbers_are_not_invented():
    payload = complete_owner_read_result()
    payload["dashboard_fake_account_balance"] = "999999"

    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_read_result=payload,
    )

    assert result["json_written"] is False
    assert "dashboard_fake_account_balance" in result["rejected_forbidden_fields"]


def test_complete_safe_helper_output_writes_json_with_owner_run_flag(tmp_path):
    output = tmp_path / "owner_read_output.json"

    result = generator.generate_owner_run_sanitized_broker_read_output(
        owner_run_read_broker_now=True,
        owner_read_helper=complete_owner_read_result,
        owner_read_helper_name="mock_safe_owner_read_helper",
        owner_read_helper_proven_safe=True,
        write_json=True,
        json_path=str(output),
    )

    assert result["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_WRITTEN
    )
    assert result["broker_read_performed"] is True
    assert result["broker_network_call_performed"] is True
    assert output.exists()


def test_cli_default_emits_json_without_broker_call():
    code, payload = run_script(["--json"])

    assert code == 0
    assert payload["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_READY_FOR_OWNER_RUN
    )
    assert payload["safe_owner_read_helper_status"] == (
        generator.SAFE_OWNER_READ_HELPER_BOUND
    )
    assert payload["safe_owner_read_helper_bound"] is True
    assert payload["json_written"] is False
    assert payload["owner_run_read_broker_now"] is False
    assert payload["broker_read_performed"] is False
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["account_id_read_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["live_endpoint_used"] is False
    assert payload["secrets_written"] is False
    assert payload["raw_broker_payload_persisted"] is False


def test_cli_with_owner_read_result_file_writes_json_only_when_safe(tmp_path):
    source = write_json(tmp_path / "owner_result.json", complete_owner_read_result())
    output = tmp_path / "owner_read_output.json"

    code, payload = run_script(
        [
            "--owner-read-result-file",
            str(source),
            "--write-json",
            "--json-path",
            str(output),
            "--json",
        ],
    )

    assert code == 0
    assert payload["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_WRITTEN
    )
    assert payload["json_written"] is True
    assert output.exists()


def test_cli_owner_run_flag_path_is_covered_with_mocked_helper_only(
    tmp_path,
    monkeypatch,
):
    def mocked_binding() -> dict:
        return generator._bound_safe_owner_read_helper(
            "mock_safe_owner_read_helper",
            complete_owner_read_result,
        )

    monkeypatch.setattr(
        generator,
        "_resolve_safe_owner_read_helper",
        mocked_binding,
    )

    output = tmp_path / "owner_read_output.json"

    code, payload = run_script(
        [
            "--owner-run-read-broker-now",
            "--write-json",
            "--json-path",
            str(output),
            "--json",
        ],
    )

    assert code == 0
    assert payload["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_WRITTEN
    )
    assert payload["safe_owner_read_helper_name"] == "mock_safe_owner_read_helper"
    assert payload["safe_owner_read_helper_bound"] is True
    assert payload["json_written"] is True
    assert payload["broker_read_performed"] is True
    assert payload["broker_network_call_performed"] is True
    assert output.exists()


def test_cli_with_owner_run_read_broker_now_without_proven_helper_fails_closed(
    tmp_path,
    monkeypatch,
):
    def blocked_binding() -> dict:
        return generator._unbound_safe_owner_read_helper(
            generator.SAFE_OWNER_READ_HELPER_NOT_PROVEN_SAFE,
            "mock_unproven_helper",
            "mock_helper_not_proven_safe",
        )

    monkeypatch.setattr(
        generator,
        "_resolve_safe_owner_read_helper",
        blocked_binding,
    )
    output = tmp_path / "owner_read_output.json"

    code, payload = run_script(
        [
            "--owner-run-read-broker-now",
            "--write-json",
            "--json-path",
            str(output),
            "--json",
        ],
    )

    assert code == 0
    assert payload["output_status"] == (
        generator.OWNER_RUN_SANITIZED_BROKER_READ_OUTPUT_BLOCKED_HELPER_NOT_PROVEN_SAFE
    )
    assert payload["safe_owner_read_helper_bound"] is False
    assert payload["json_written"] is False
    assert payload["broker_read_performed"] is False
    assert payload["broker_network_call_performed"] is False
    assert not output.exists()


def test_report_writer_includes_safety_statements(tmp_path):
    result = generator.generate_owner_run_sanitized_broker_read_output()
    report = tmp_path / "report.md"

    generator.write_owner_run_sanitized_broker_read_output_generator_report(
        result,
        report,
    )
    text = report.read_text(encoding="utf-8")

    assert "- safe_owner_read_helper_status:" in text
    assert "- safe_owner_read_helper_name:" in text
    assert "- safe_owner_read_helper_bound:" in text
    assert "- no new order placed" in text
    assert "- no live trade placed" in text
    assert "- no broker state modified" in text
    assert "- no secrets written" in text
    assert "- raw broker payload persisted: false" in text
