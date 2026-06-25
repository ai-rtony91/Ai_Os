from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_sanitized_evidence_normalizer_acceptance_run_v1 import (  # noqa: E402
    INTERNAL_LEDGER_ONLY,
    SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED,
    SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_NOT_REQUESTED,
    SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_REJECTED,
    run_sanitized_evidence_normalizer_acceptance,
    write_sanitized_evidence_normalizer_acceptance_report,
)
from automation.forex_engine.oanda_demo_sanitized_owner_run_read_only_telemetry_adapter_v1 import (  # noqa: E402
    SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED,
    SANITIZED_OWNER_RUN_TELEMETRY_MISSING,
)
from automation.forex_engine.oanda_demo_sanitized_telemetry_shape_normalizer_v1 import (  # noqa: E402
    SANITIZED_TELEMETRY_SHAPE_NORMALIZER_ACCEPTED,
    SANITIZED_TELEMETRY_SHAPE_NORMALIZER_NOT_REQUESTED,
)
from scripts.forex_delivery.run_oanda_demo_sanitized_evidence_normalizer_acceptance_run_v1 import (  # noqa: E402
    main as script_main,
)


def valid_packet_09_style_evidence() -> dict:
    return {
        "exercise_status": "OWNER_RUN_SANITIZED_TELEMETRY_EXERCISE_INVALID_SHAPE",
        "capture_status": "OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_INVALID_SHAPE",
        "adapter_status": "SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE",
        "broker_read_performed": True,
        "broker_network_call_performed": True,
        "live_endpoint_used": False,
        "order_placement_performed": False,
        "order_mutation_performed": False,
        "order_close_performed": False,
        "position_mutation_performed": False,
        "trade_mutation_performed": False,
        "raw_broker_payload_persisted": False,
        "secrets_written": False,
        "result": {
            "trade_id": "320",
            "instrument": "EUR_USD",
            "side": "long",
            "units": "1",
            "entry_price": "1.13596",
            "realized_pl": "0.0000",
            "unrealized_pl": "-0.0004",
            "open_trade_count": "1",
            "open_position_count": "1",
            "monitor_bucket": "OPEN_UNREALIZED_NEGATIVE",
            "result_bucket": "NO_PROFIT_EVIDENCE_OPEN_NEGATIVE",
            "repeat_proof_lane_status": "NOT_STARTED_NO_PROFIT_EVIDENCE",
            "repeat_proof_eligible": False,
            "profit_evidence": False,
            "evidence_timestamp_utc": "2026-06-25T00:00:00Z",
        },
    }


def invalid_packet_09_missing_pl_and_counts() -> dict:
    evidence = valid_packet_09_style_evidence()
    result = dict(evidence["result"])
    result["realized_pl"] = "UNKNOWN"
    result["unrealized_pl"] = "UNKNOWN"
    result["open_trade_count"] = "UNKNOWN"
    result["open_position_count"] = "UNKNOWN"
    evidence["result"] = result
    return evidence


def run_script(args: list[str]) -> tuple[int, dict]:
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def test_default_acceptance_run_does_not_call_broker_and_is_not_requested() -> None:
    result = run_sanitized_evidence_normalizer_acceptance()

    assert result["acceptance_status"] == SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_NOT_REQUESTED
    assert result["normalizer_status"] == SANITIZED_TELEMETRY_SHAPE_NORMALIZER_NOT_REQUESTED
    assert result["adapter_status"] == SANITIZED_OWNER_RUN_TELEMETRY_MISSING
    assert result["broker_read_performed"] is False
    assert result["broker_network_call_performed"] is False


def test_valid_evidence_is_accepted_through_packet_10_normalizer() -> None:
    result = run_sanitized_evidence_normalizer_acceptance(
        valid_packet_09_style_evidence(),
        evidence_file_path="packet_09_sanitized.json",
    )

    assert result["acceptance_status"] == SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED
    assert result["normalizer_status"] == SANITIZED_TELEMETRY_SHAPE_NORMALIZER_ACCEPTED
    assert result["adapter_status"] == SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED
    assert result["sanitized_broker_telemetry_ready"] is True
    assert result["normalized_adapter_input_ready"] is True
    assert result["evidence_file_path"] == "packet_09_sanitized.json"


def test_missing_required_fields_are_reported_without_raw_payload() -> None:
    result = run_sanitized_evidence_normalizer_acceptance(
        invalid_packet_09_missing_pl_and_counts(),
        evidence_file_path="packet_09_sanitized.json",
    )

    assert result["acceptance_status"] == SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_REJECTED
    assert result["sanitized_broker_telemetry_ready"] is False
    assert "realized_pl_required" in result["missing_required_fields"]
    assert result["raw_broker_payload_persisted"] is False


def test_forbidden_fields_are_reported_as_rejected_without_persisting_payload() -> None:
    evidence = valid_packet_09_style_evidence()
    evidence["raw_response"] = {"forbidden": "payload"}

    result = run_sanitized_evidence_normalizer_acceptance(evidence)

    assert result["acceptance_status"] == SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_REJECTED
    assert result["rejected_forbidden_fields"] == ["raw_response"]
    assert result["raw_broker_payload_persisted"] is False


def test_fake_mock_numbers_and_money_movement_remain_blocked() -> None:
    result = run_sanitized_evidence_normalizer_acceptance(
        valid_packet_09_style_evidence(),
    )

    assert result["dashboard_fake_numbers_allowed"] is False
    assert result["dashboard_mock_numbers_allowed"] is False
    assert result["withdrawal_allowed_now"] is False
    assert result["transfer_allowed_now"] is False
    assert result["money_movement_allowed_now"] is False
    assert result["profit_reserve_bucket_mode"] == INTERNAL_LEDGER_ONLY


def test_cli_default_emits_json_without_broker_call() -> None:
    code, payload = run_script(["--json"])

    assert code == 0
    assert payload["script_status"] == SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_NOT_REQUESTED
    assert payload["broker_read_performed"] is False
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["account_id_read_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["live_endpoint_used"] is False
    assert payload["secrets_written"] is False


def test_cli_with_evidence_file_records_path_and_accepts_valid_evidence(
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "packet_09_sanitized.json"
    evidence_path.write_text(
        json.dumps(valid_packet_09_style_evidence()),
        encoding="utf-8",
    )

    code, payload = run_script(["--evidence-file", str(evidence_path), "--json"])

    assert code == 0
    assert payload["script_status"] == SANITIZED_EVIDENCE_NORMALIZER_ACCEPTANCE_ACCEPTED
    assert payload["evidence_file_path"] == str(evidence_path)
    assert payload["adapter_status"] == SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED


def test_report_writer_includes_path_outcome_and_safety_statements(
    tmp_path: Path,
) -> None:
    result = run_sanitized_evidence_normalizer_acceptance(
        valid_packet_09_style_evidence(),
        evidence_file_path="packet_09_sanitized.json",
    )
    report_path = tmp_path / "acceptance_report.md"

    write_sanitized_evidence_normalizer_acceptance_report(result, report_path)

    text = report_path.read_text(encoding="utf-8")
    assert "evidence_file_path_supplied: packet_09_sanitized.json" in text
    assert "sanitized_evidence_accepted: yes" in text
    assert "raw owner evidence payload persisted: false" in text
    assert "no new order placed" in text
    assert "no live trade placed" in text
    assert "no broker state modified" in text
    assert "no secrets written" in text
    assert "raw broker payload persisted: false" in text
