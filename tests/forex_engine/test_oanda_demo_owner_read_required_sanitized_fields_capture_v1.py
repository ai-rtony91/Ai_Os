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
from automation.forex_engine.oanda_demo_sanitized_evidence_normalizer_acceptance_run_v1 import (  # noqa: E402
    SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED,
    run_sanitized_evidence_normalizer_acceptance,
)
from scripts.forex_delivery.run_oanda_demo_owner_read_required_sanitized_fields_capture_v1 import (  # noqa: E402
    main as script_main,
)


def complete_input() -> dict:
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


def write_json(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload), encoding="utf-8")
    return path


def run_script(args: list[str]) -> tuple[int, dict]:
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def test_default_result_does_not_call_broker_and_reports_not_requested():
    result = capture.capture_required_sanitized_fields_from_owner_read()

    assert result["capture_status"] == (
        capture.OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_NOT_REQUESTED
    )
    assert result["broker_read_performed"] is False
    assert result["broker_network_call_performed"] is False
    assert result["next_action"] == capture.DEFAULT_NEXT_ACTION


def test_default_does_not_write_json(tmp_path):
    result = capture.capture_required_sanitized_fields_from_owner_read(
        write_json=True,
        json_path=str(tmp_path / "packet09.json"),
    )

    assert result["json_written"] is False
    assert not (tmp_path / "packet09.json").exists()


def test_missing_required_fields_blocks_capture():
    payload = complete_input()
    payload.pop("realized_pl")
    payload.pop("open_trade_count")

    result = capture.capture_required_sanitized_fields_from_owner_read(payload)

    assert result["capture_status"] == (
        capture.OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_BLOCKED_MISSING_FIELDS
    )
    assert result["json_written"] is False
    assert "realized_pl" in result["missing_required_fields"]
    assert "open_trade_count" in result["missing_required_fields"]


def test_complete_safe_sanitized_input_is_ready():
    result = capture.capture_required_sanitized_fields_from_owner_read(
        complete_input(),
    )

    assert result["capture_status"] == (
        capture.OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_READY
    )
    assert result["sanitized_evidence_ready"] is True
    assert result["required_fields_present"] is True


def test_complete_safe_sanitized_input_writes_json_when_requested(tmp_path):
    output = tmp_path / "packet09.json"

    result = capture.capture_required_sanitized_fields_from_owner_read(
        complete_input(),
        write_json=True,
        json_path=str(output),
    )

    assert result["capture_status"] == (
        capture.OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_WRITTEN
    )
    assert result["json_written"] is True
    assert output.exists()


def test_exported_json_contains_only_accepted_safe_fields(tmp_path):
    payload = complete_input()
    payload["local_note"] = "not exported"
    output = tmp_path / "packet09.json"

    capture.capture_required_sanitized_fields_from_owner_read(
        payload,
        write_json=True,
        json_path=str(output),
    )
    exported = json.loads(output.read_text(encoding="utf-8"))

    assert set(exported) <= capture.EXPORT_FIELD_SET
    assert "local_note" not in exported
    assert "credential_read_performed" not in exported
    assert "account_id_read_performed" not in exported


def test_exported_json_works_with_packet11_acceptance_runner(tmp_path):
    output = tmp_path / "packet09.json"
    capture.capture_required_sanitized_fields_from_owner_read(
        complete_input(),
        write_json=True,
        json_path=str(output),
    )

    exported = json.loads(output.read_text(encoding="utf-8"))
    acceptance = run_sanitized_evidence_normalizer_acceptance(exported)

    assert acceptance["acceptance_status"] == (
        SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED
    )


def test_forbidden_token_secret_account_fields_reject():
    for field in ("access_token", "secret", "account_id"):
        payload = complete_input()
        payload[field] = "forbidden"

        result = capture.capture_required_sanitized_fields_from_owner_read(payload)

        assert result["capture_status"] == (
            capture.OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_REJECTED_SECRET_RISK
        )
        assert field in result["rejected_forbidden_fields"]


def test_raw_payload_raw_response_fields_reject():
    for field in ("raw_payload", "raw_response"):
        payload = complete_input()
        payload[field] = {"forbidden": "payload"}

        result = capture.capture_required_sanitized_fields_from_owner_read(payload)

        assert result["capture_status"] == (
            capture.OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_REJECTED_RAW_PAYLOAD_RISK
        )
        assert field in result["rejected_forbidden_fields"]


def test_nested_forbidden_fields_reject():
    payload = complete_input()
    payload["nested"] = {"authorization": "forbidden"}

    result = capture.capture_required_sanitized_fields_from_owner_read(payload)

    assert result["capture_status"] == (
        capture.OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_REJECTED_SECRET_RISK
    )
    assert "nested_authorization" in result["rejected_forbidden_fields"]


def test_unsafe_audit_true_flags_reject():
    payload = complete_input()
    payload["order_close_performed"] = True

    result = capture.capture_required_sanitized_fields_from_owner_read(payload)

    assert result["capture_status"] == (
        capture.OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_REJECTED_UNSAFE_AUDIT_FLAG
    )
    assert "order_close_performed" in result["unsafe_audit_flags"]


def test_safe_audit_false_flags_pass():
    result = capture.capture_required_sanitized_fields_from_owner_read(
        complete_input(),
    )

    assert result["capture_status"] == (
        capture.OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_READY
    )
    assert result["unsafe_audit_flags"] == []


def test_money_movement_remains_blocked():
    result = capture.capture_required_sanitized_fields_from_owner_read(
        complete_input(),
    )

    assert result["withdrawal_allowed_now"] is False
    assert result["transfer_allowed_now"] is False
    assert result["money_movement_allowed_now"] is False
    assert result["profit_reserve_bucket_mode"] == capture.INTERNAL_LEDGER_ONLY


def test_fake_mock_numbers_are_not_invented():
    payload = complete_input()
    payload["dashboard_fake_account_balance"] = "999999"

    result = capture.capture_required_sanitized_fields_from_owner_read(payload)

    assert result["json_written"] is False
    assert "dashboard_fake_account_balance" in result["rejected_forbidden_fields"]


def test_cli_default_emits_json_without_broker_call():
    code, payload = run_script(["--json"])

    assert code == 0
    assert payload["capture_status"] == (
        capture.OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_NOT_REQUESTED
    )
    assert payload["json_written"] is False
    assert payload["broker_read_performed"] is False
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["account_id_read_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["live_endpoint_used"] is False
    assert payload["secrets_written"] is False
    assert payload["raw_broker_payload_persisted"] is False


def test_cli_with_sanitized_input_writes_json_only_when_safe(tmp_path):
    source = write_json(tmp_path / "input.json", complete_input())
    output = tmp_path / "packet09.json"

    code, payload = run_script(
        [
            "--sanitized-input-file",
            str(source),
            "--write-json",
            "--json-path",
            str(output),
            "--json",
        ],
    )

    assert code == 0
    assert payload["capture_status"] == (
        capture.OWNER_READ_REQUIRED_SANITIZED_FIELDS_CAPTURE_WRITTEN
    )
    assert payload["json_written"] is True
    assert output.exists()


def test_report_writer_includes_safety_statements(tmp_path):
    result = capture.capture_required_sanitized_fields_from_owner_read()
    report = tmp_path / "report.md"

    capture.write_owner_read_required_sanitized_fields_capture_report(
        result,
        report,
    )
    text = report.read_text(encoding="utf-8")

    assert "- no new order placed" in text
    assert "- no live trade placed" in text
    assert "- no broker state modified" in text
    assert "- no secrets written" in text
    assert "- raw broker payload persisted: false" in text
