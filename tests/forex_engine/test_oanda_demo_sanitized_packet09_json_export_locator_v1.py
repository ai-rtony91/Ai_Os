from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine import oanda_demo_sanitized_packet09_json_export_locator_v1 as locator  # noqa: E402
from automation.forex_engine.oanda_demo_sanitized_evidence_normalizer_acceptance_run_v1 import (  # noqa: E402
    SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED,
    run_sanitized_evidence_normalizer_acceptance,
)
from scripts.forex_delivery.run_oanda_demo_sanitized_packet09_json_export_locator_v1 import (  # noqa: E402
    main as script_main,
)


def complete_evidence() -> dict:
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
        "no_new_order_placed": True,
        "no_live_trade_placed": True,
        "no_broker_state_modified": True,
        "no_secrets_written": True,
    }


def write_source(tmp_path: Path, evidence: dict) -> Path:
    path = tmp_path / "safe_packet09_source.json"
    path.write_text(json.dumps(evidence), encoding="utf-8")
    return path


def run_script(args: list[str]) -> tuple[int, dict]:
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def test_default_result_does_not_write_json_and_does_not_call_broker(tmp_path, monkeypatch):
    source = write_source(tmp_path, complete_evidence())
    monkeypatch.setattr(locator, "DEFAULT_JSON_PATH", str(source))

    result = locator.run_sanitized_packet09_json_export_locator()

    assert result["json_written"] is False
    assert result["broker_read_performed"] is True
    assert result["broker_network_call_performed"] is True
    assert result["no_new_order_placed"] is True
    assert result["no_live_trade_placed"] is True
    assert result["no_broker_state_modified"] is True
    assert result["no_secrets_written"] is True


def test_known_missing_evidence_fields_blocks_export(tmp_path, monkeypatch):
    evidence = complete_evidence()
    evidence.pop("realized_pl")
    evidence.pop("open_trade_count")
    source = write_source(tmp_path, evidence)
    monkeypatch.setattr(locator, "DEFAULT_JSON_PATH", str(source))

    result = locator.run_sanitized_packet09_json_export_locator(
        write_json=True,
        json_path=str(tmp_path / "out.json"),
    )

    assert result["export_status"] == locator.SANITIZED_PACKET09_JSON_EXPORT_BLOCKED_MISSING_FIELDS
    assert result["json_written"] is False
    assert "realized_pl" in result["missing_required_fields"]
    assert "open_trade_count" in result["missing_required_fields"]


def test_complete_safe_evidence_writes_json_when_requested(tmp_path, monkeypatch):
    source = write_source(tmp_path, complete_evidence())
    output = tmp_path / "packet09.json"
    monkeypatch.setattr(locator, "DEFAULT_JSON_PATH", str(source))

    result = locator.run_sanitized_packet09_json_export_locator(
        write_json=True,
        json_path=str(output),
    )

    assert result["export_status"] == locator.SANITIZED_PACKET09_JSON_EXPORT_WRITTEN
    assert result["json_written"] is True
    assert output.exists()


def test_forbidden_secret_account_token_fields_reject(tmp_path, monkeypatch):
    for field in ("access_token", "account_id", "token"):
        evidence = complete_evidence()
        evidence[field] = "forbidden"
        source = write_source(tmp_path, evidence)
        monkeypatch.setattr(locator, "DEFAULT_JSON_PATH", str(source))

        result = locator.run_sanitized_packet09_json_export_locator()

        assert result["export_status"] == locator.SANITIZED_PACKET09_JSON_EXPORT_REJECTED_SECRET_RISK
        assert field in result["rejected_forbidden_fields"]


def test_raw_payload_markers_reject(tmp_path, monkeypatch):
    evidence = complete_evidence()
    evidence["raw_response"] = {"forbidden": "payload"}
    source = write_source(tmp_path, evidence)
    monkeypatch.setattr(locator, "DEFAULT_JSON_PATH", str(source))

    result = locator.run_sanitized_packet09_json_export_locator()

    assert result["export_status"] == locator.SANITIZED_PACKET09_JSON_EXPORT_REJECTED_RAW_PAYLOAD_RISK
    assert "raw_response" in result["rejected_forbidden_fields"]


def test_unsafe_audit_true_flags_reject(tmp_path, monkeypatch):
    evidence = complete_evidence()
    evidence["order_placement_performed"] = True
    source = write_source(tmp_path, evidence)
    monkeypatch.setattr(locator, "DEFAULT_JSON_PATH", str(source))

    result = locator.run_sanitized_packet09_json_export_locator()

    assert result["export_status"] == locator.SANITIZED_PACKET09_JSON_EXPORT_REJECTED_UNSAFE_AUDIT_FLAG
    assert "order_placement_performed" in result["unsafe_audit_flags"]


def test_safe_audit_false_flags_pass(tmp_path, monkeypatch):
    source = write_source(tmp_path, complete_evidence())
    monkeypatch.setattr(locator, "DEFAULT_JSON_PATH", str(source))

    result = locator.run_sanitized_packet09_json_export_locator()

    assert result["export_status"] == locator.SANITIZED_PACKET09_JSON_EXPORT_READY
    assert result["unsafe_audit_flags"] == []


def test_exported_json_contains_only_allowed_safe_fields(tmp_path, monkeypatch):
    evidence = complete_evidence()
    evidence["extra_local_note"] = "not exported"
    source = write_source(tmp_path, evidence)
    output = tmp_path / "packet09.json"
    monkeypatch.setattr(locator, "DEFAULT_JSON_PATH", str(source))

    locator.run_sanitized_packet09_json_export_locator(
        write_json=True,
        json_path=str(output),
    )
    exported = json.loads(output.read_text(encoding="utf-8"))

    assert set(exported) <= locator.EXPORT_FIELD_SET
    assert "extra_local_note" not in exported


def test_exported_json_works_with_packet11_acceptance_runner(tmp_path, monkeypatch):
    source = write_source(tmp_path, complete_evidence())
    output = tmp_path / "packet09.json"
    monkeypatch.setattr(locator, "DEFAULT_JSON_PATH", str(source))

    locator.run_sanitized_packet09_json_export_locator(
        write_json=True,
        json_path=str(output),
    )
    exported = json.loads(output.read_text(encoding="utf-8"))
    acceptance = run_sanitized_evidence_normalizer_acceptance(exported)

    assert acceptance["acceptance_status"] == SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED


def test_money_movement_remains_blocked(tmp_path, monkeypatch):
    source = write_source(tmp_path, complete_evidence())
    monkeypatch.setattr(locator, "DEFAULT_JSON_PATH", str(source))

    result = locator.run_sanitized_packet09_json_export_locator()

    assert result["withdrawal_allowed_now"] is False
    assert result["transfer_allowed_now"] is False
    assert result["money_movement_allowed_now"] is False
    assert result["profit_reserve_bucket_mode"] == locator.INTERNAL_LEDGER_ONLY


def test_fake_mock_numbers_are_not_invented(tmp_path, monkeypatch):
    evidence = complete_evidence()
    evidence["dashboard_fake_account_balance"] = "999999"
    source = write_source(tmp_path, evidence)
    monkeypatch.setattr(locator, "DEFAULT_JSON_PATH", str(source))

    result = locator.run_sanitized_packet09_json_export_locator()

    assert result["json_written"] is False
    assert "dashboard_fake_account_balance" in result["rejected_forbidden_fields"]


def test_report_writer_records_missing_fields_and_next_action(tmp_path, monkeypatch):
    evidence = complete_evidence()
    evidence.pop("unrealized_pl")
    source = write_source(tmp_path, evidence)
    monkeypatch.setattr(locator, "DEFAULT_JSON_PATH", str(source))
    result = locator.run_sanitized_packet09_json_export_locator()
    report = tmp_path / "report.md"

    locator.write_sanitized_packet09_json_export_locator_report(result, report)
    text = report.read_text(encoding="utf-8")

    assert "- unrealized_pl" in text
    assert "next_action:" in text


def test_cli_default_emits_json_without_broker_call():
    code, payload = run_script(["--json"])

    assert code == 0
    assert payload["json_written"] is False
    assert payload["credential_read_performed"] is False
    assert payload["account_id_read_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["live_endpoint_used"] is False
    assert payload["secrets_written"] is False
    assert payload["raw_broker_payload_persisted"] is False


def test_cli_write_json_writes_target_json_only_when_safe(tmp_path, monkeypatch):
    source = write_source(tmp_path, complete_evidence())
    output = tmp_path / "packet09.json"
    monkeypatch.setattr(locator, "DEFAULT_JSON_PATH", str(source))

    code, payload = run_script([
        "--write-json",
        "--json-path",
        str(output),
        "--json",
    ])

    assert code == 0
    assert payload["json_written"] is True
    assert output.exists()
