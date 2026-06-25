from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_sanitized_owner_run_read_only_telemetry_adapter_v1 import (  # noqa: E402
    INTERNAL_LEDGER_ONLY,
    SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED,
    SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE,
    SANITIZED_OWNER_RUN_TELEMETRY_MISSING,
)
from automation.forex_engine.oanda_demo_sanitized_telemetry_shape_normalizer_v1 import (  # noqa: E402
    NORMALIZED_OWNER_RUN_SANITIZED_TELEMETRY_READY,
    OWNER_RUN_READ_ONLY_BROKER_REQUESTED,
    SANITIZED_TELEMETRY_SHAPE_NORMALIZER_ACCEPTED,
    SANITIZED_TELEMETRY_SHAPE_NORMALIZER_INVALID_SHAPE,
    SANITIZED_TELEMETRY_SHAPE_NORMALIZER_NOT_REQUESTED,
    SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_RAW_PAYLOAD,
    SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_SECRET_RISK,
    SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_UNSAFE_AUDIT_FLAG,
    normalize_sanitized_owner_run_telemetry_shape,
    write_sanitized_telemetry_shape_normalizer_report,
)
from scripts.forex_delivery.run_oanda_demo_sanitized_telemetry_shape_normalizer_v1 import (  # noqa: E402
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


def test_default_result_does_not_call_broker_and_reports_not_requested() -> None:
    result = normalize_sanitized_owner_run_telemetry_shape()

    assert result["normalizer_status"] == SANITIZED_TELEMETRY_SHAPE_NORMALIZER_NOT_REQUESTED
    assert result["broker_read_performed"] is False
    assert result["broker_network_call_performed"] is False
    assert result["no_new_order_placed"] is True
    assert result["no_live_trade_placed"] is True
    assert result["no_broker_state_modified"] is True
    assert result["no_secrets_written"] is True


def test_default_adapter_status_remains_telemetry_missing() -> None:
    result = normalize_sanitized_owner_run_telemetry_shape()

    assert result["adapter_status"] == SANITIZED_OWNER_RUN_TELEMETRY_MISSING
    assert result["sanitized_broker_telemetry_ready"] is False


def test_packet_09_invalid_shape_missing_pl_and_counts_remains_invalid() -> None:
    result = normalize_sanitized_owner_run_telemetry_shape(
        invalid_packet_09_missing_pl_and_counts(),
    )

    assert result["normalizer_status"] == SANITIZED_TELEMETRY_SHAPE_NORMALIZER_INVALID_SHAPE
    assert result["adapter_status"] == SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE
    assert result["sanitized_broker_telemetry_ready"] is False
    assert "realized_pl_required" in result["missing_required_fields"]
    assert "open_trade_count_required" in result["missing_required_fields"]


def test_valid_nested_packet_09_style_result_normalizes_to_packet_07_shape() -> None:
    result = normalize_sanitized_owner_run_telemetry_shape(
        valid_packet_09_style_evidence(),
    )

    assert result["normalizer_status"] == SANITIZED_TELEMETRY_SHAPE_NORMALIZER_ACCEPTED
    assert result["adapter_status"] == SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED
    assert result["broker_read_mode"] == OWNER_RUN_READ_ONLY_BROKER_REQUESTED
    assert result["broker_evidence_status"] == NORMALIZED_OWNER_RUN_SANITIZED_TELEMETRY_READY


def test_accepted_normalized_evidence_sets_ready_true() -> None:
    result = normalize_sanitized_owner_run_telemetry_shape(
        valid_packet_09_style_evidence(),
    )

    assert result["sanitized_broker_telemetry_ready"] is True
    assert result["normalized_adapter_input_ready"] is True


def test_accepted_normalized_evidence_preserves_realized_and_unrealized_pl() -> None:
    result = normalize_sanitized_owner_run_telemetry_shape(
        valid_packet_09_style_evidence(),
    )

    assert result["realized_pl"] == "0.0000"
    assert result["unrealized_pl"] == "-0.0004"


def test_accepted_normalized_evidence_preserves_open_trade_and_position_counts() -> None:
    result = normalize_sanitized_owner_run_telemetry_shape(
        valid_packet_09_style_evidence(),
    )

    assert result["open_trade_count"] == 1
    assert result["open_position_count"] == 1


def test_accepted_normalized_evidence_preserves_trade_anchor_fields() -> None:
    result = normalize_sanitized_owner_run_telemetry_shape(
        valid_packet_09_style_evidence(),
    )

    assert result["trade_id"] == 320
    assert result["instrument"] == "EUR_USD"
    assert result["side"] == "long"
    assert result["units"] == 1
    assert result["entry_price"] == "1.13596"


def test_safe_audit_flags_do_not_reject() -> None:
    evidence = valid_packet_09_style_evidence()
    evidence["no_secrets_written"] = True
    evidence["credential_read_performed"] = False
    evidence["account_id_read_performed"] = False
    evidence["no_broker_state_modified"] = True
    evidence["no_new_order_placed"] = True
    evidence["no_live_trade_placed"] = True

    result = normalize_sanitized_owner_run_telemetry_shape(evidence)

    assert result["normalizer_status"] == SANITIZED_TELEMETRY_SHAPE_NORMALIZER_ACCEPTED


def test_unsafe_audit_flags_reject() -> None:
    for field in (
        "secrets_written",
        "raw_broker_payload_persisted",
        "credential_read_performed",
        "account_id_read_performed",
        "live_endpoint_used",
        "order_placement_performed",
        "order_mutation_performed",
        "order_close_performed",
        "position_mutation_performed",
        "trade_mutation_performed",
    ):
        evidence = valid_packet_09_style_evidence()
        evidence[field] = True

        result = normalize_sanitized_owner_run_telemetry_shape(evidence)

        assert (
            result["normalizer_status"]
            == SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_UNSAFE_AUDIT_FLAG
        )
        assert result["sanitized_broker_telemetry_ready"] is False


def test_token_secret_and_account_id_fields_reject_as_secret_risk() -> None:
    for field in ("access_token", "token", "account_id"):
        evidence = valid_packet_09_style_evidence()
        evidence[field] = "SHOULD_NOT_BE_ACCEPTED"

        result = normalize_sanitized_owner_run_telemetry_shape(evidence)

        assert (
            result["normalizer_status"]
            == SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_SECRET_RISK
        )
        assert result["sanitized_broker_telemetry_ready"] is False


def test_raw_broker_payload_and_raw_response_reject_as_raw_payload() -> None:
    for field in ("raw_broker_payload", "raw_response"):
        evidence = valid_packet_09_style_evidence()
        evidence[field] = {"anything": "forbidden"}

        result = normalize_sanitized_owner_run_telemetry_shape(evidence)

        assert (
            result["normalizer_status"]
            == SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_RAW_PAYLOAD
        )
        assert result["raw_broker_payload_persisted"] is False


def test_nested_forbidden_field_is_rejected() -> None:
    evidence = valid_packet_09_style_evidence()
    evidence["metadata"] = {"headers": {"authorization": "Bearer forbidden"}}

    result = normalize_sanitized_owner_run_telemetry_shape(evidence)

    assert (
        result["normalizer_status"]
        == SANITIZED_TELEMETRY_SHAPE_NORMALIZER_REJECTED_SECRET_RISK
    )
    assert "metadata_headers" in result["rejected_secret_fields"]


def test_fake_and_mock_dashboard_numbers_remain_forbidden() -> None:
    result = normalize_sanitized_owner_run_telemetry_shape(
        valid_packet_09_style_evidence(),
    )

    assert result["dashboard_real_broker_telemetry_goal"] is True
    assert result["dashboard_fake_numbers_allowed"] is False
    assert result["dashboard_mock_numbers_allowed"] is False

    evidence = valid_packet_09_style_evidence()
    evidence["dashboard_fake_account_balance"] = "1000000"
    rejected = normalize_sanitized_owner_run_telemetry_shape(evidence)

    assert rejected["normalizer_status"] == SANITIZED_TELEMETRY_SHAPE_NORMALIZER_INVALID_SHAPE


def test_money_movement_remains_blocked() -> None:
    result = normalize_sanitized_owner_run_telemetry_shape(
        valid_packet_09_style_evidence(),
    )

    assert result["withdrawal_allowed_now"] is False
    assert result["transfer_allowed_now"] is False
    assert result["money_movement_allowed_now"] is False
    assert result["profit_reserve_bucket_mode"] == INTERNAL_LEDGER_ONLY


def test_cli_default_emits_json_without_broker_call() -> None:
    code, payload = run_script(["--json"])

    assert code == 0
    assert payload["script_status"] == SANITIZED_TELEMETRY_SHAPE_NORMALIZER_NOT_REQUESTED
    assert payload["broker_read_performed"] is False
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["account_id_read_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["live_endpoint_used"] is False
    assert payload["secrets_written"] is False


def test_cli_with_evidence_file_normalizes_valid_sanitized_evidence(
    tmp_path: Path,
) -> None:
    evidence_path = tmp_path / "packet_09_sanitized.json"
    evidence_path.write_text(
        json.dumps(valid_packet_09_style_evidence()),
        encoding="utf-8",
    )

    code, payload = run_script(["--evidence-file", str(evidence_path), "--json"])

    assert code == 0
    assert payload["script_status"] == SANITIZED_TELEMETRY_SHAPE_NORMALIZER_ACCEPTED
    assert payload["adapter_status"] == SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED
    assert payload["sanitized_broker_telemetry_ready"] is True


def test_report_writer_includes_safety_statements_and_raw_payload_false(
    tmp_path: Path,
) -> None:
    result = normalize_sanitized_owner_run_telemetry_shape()
    report_path = tmp_path / "shape_normalizer_report.md"

    write_sanitized_telemetry_shape_normalizer_report(result, report_path)

    text = report_path.read_text(encoding="utf-8")
    assert "no new order placed" in text
    assert "no live trade placed" in text
    assert "no broker state modified" in text
    assert "no secrets written" in text
    assert "raw broker payload persisted: false" in text
