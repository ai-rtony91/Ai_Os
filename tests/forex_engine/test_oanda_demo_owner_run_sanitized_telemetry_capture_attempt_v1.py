from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_owner_run_sanitized_telemetry_capture_attempt_v1 import (  # noqa: E402
    OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_ACCEPTED,
    OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_BROKER_BLOCKED,
    OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_INVALID_SHAPE,
    OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_NOT_REQUESTED,
    OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_RAW_PAYLOAD,
    OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_SECRET_RISK,
    run_owner_sanitized_telemetry_capture_attempt,
    write_owner_run_sanitized_telemetry_capture_attempt_report,
)
from automation.forex_engine.oanda_demo_sanitized_owner_run_read_only_telemetry_adapter_v1 import (  # noqa: E402
    BROKER_EVIDENCE_BLOCKED,
    INTERNAL_LEDGER_ONLY,
    SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED,
    SANITIZED_OWNER_RUN_TELEMETRY_MISSING,
)
from scripts.forex_delivery.run_oanda_demo_owner_run_sanitized_telemetry_capture_attempt_v1 import (  # noqa: E402
    main as script_main,
)


def valid_sanitized_trade_320_evidence() -> dict:
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
        "evidence_source": "owner_run_read_only_helper_sanitized",
    }


def run_script(args: list[str]) -> tuple[int, dict]:
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args)
    return code, json.loads(stream.getvalue())


def test_default_result_does_not_call_broker_and_reports_not_requested() -> None:
    result = run_owner_sanitized_telemetry_capture_attempt()

    assert result["capture_status"] == OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_NOT_REQUESTED
    assert result["broker_read_performed"] is False
    assert result["broker_network_call_performed"] is False
    assert result["no_new_order_placed"] is True
    assert result["no_live_trade_placed"] is True
    assert result["no_broker_state_modified"] is True
    assert result["no_secrets_written"] is True


def test_default_adapter_status_remains_telemetry_missing() -> None:
    result = run_owner_sanitized_telemetry_capture_attempt()

    assert result["adapter_status"] == SANITIZED_OWNER_RUN_TELEMETRY_MISSING
    assert result["sanitized_broker_telemetry_ready"] is False


def test_valid_sanitized_trade_320_evidence_is_accepted() -> None:
    result = run_owner_sanitized_telemetry_capture_attempt(
        valid_sanitized_trade_320_evidence()
    )

    assert result["capture_status"] == OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_ACCEPTED
    assert result["adapter_status"] == SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED
    assert result["trade_id"] == 320


def test_accepted_evidence_sets_ready_true() -> None:
    result = run_owner_sanitized_telemetry_capture_attempt(
        valid_sanitized_trade_320_evidence()
    )

    assert result["sanitized_broker_telemetry_ready"] is True


def test_accepted_evidence_preserves_pl_values() -> None:
    result = run_owner_sanitized_telemetry_capture_attempt(
        valid_sanitized_trade_320_evidence()
    )

    assert result["realized_pl"] == "0.0000"
    assert result["unrealized_pl"] == "-0.0004"


def test_accepted_evidence_preserves_open_counts() -> None:
    result = run_owner_sanitized_telemetry_capture_attempt(
        valid_sanitized_trade_320_evidence()
    )

    assert result["open_trade_count"] == 1
    assert result["open_position_count"] == 1


def test_token_secret_and_account_id_fields_reject_as_secret_risk() -> None:
    for field in ("access_token", "secret", "account_id"):
        evidence = valid_sanitized_trade_320_evidence()
        evidence[field] = "SHOULD_NOT_BE_ACCEPTED"

        result = run_owner_sanitized_telemetry_capture_attempt(evidence)

        assert (
            result["capture_status"]
            == OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_SECRET_RISK
        )
        assert result["sanitized_broker_telemetry_ready"] is False


def test_raw_broker_payload_and_raw_response_reject_as_raw_payload() -> None:
    for field in ("raw_broker_payload", "raw_response"):
        evidence = valid_sanitized_trade_320_evidence()
        evidence[field] = {"anything": "forbidden"}

        result = run_owner_sanitized_telemetry_capture_attempt(evidence)

        assert (
            result["capture_status"]
            == OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_RAW_PAYLOAD
        )
        assert result["raw_broker_payload_persisted"] is False


def test_nested_forbidden_field_is_rejected() -> None:
    evidence = valid_sanitized_trade_320_evidence()
    evidence["metadata"] = {"headers": {"authorization": "Bearer forbidden"}}

    result = run_owner_sanitized_telemetry_capture_attempt(evidence)

    assert (
        result["capture_status"]
        == OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_REJECTED_SECRET_RISK
    )


def test_invalid_or_missing_trade_id_rejects_invalid_shape() -> None:
    evidence = valid_sanitized_trade_320_evidence()
    evidence.pop("trade_id")

    result = run_owner_sanitized_telemetry_capture_attempt(evidence)

    assert result["capture_status"] == OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_INVALID_SHAPE


def test_broker_blocked_evidence_maps_to_capture_broker_blocked() -> None:
    evidence = valid_sanitized_trade_320_evidence()
    evidence["broker_evidence_status"] = BROKER_EVIDENCE_BLOCKED

    result = run_owner_sanitized_telemetry_capture_attempt(evidence)

    assert result["capture_status"] == OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_BROKER_BLOCKED
    assert result["broker_evidence_status"] == BROKER_EVIDENCE_BLOCKED


def test_fake_and_mock_dashboard_numbers_remain_forbidden() -> None:
    result = run_owner_sanitized_telemetry_capture_attempt(
        valid_sanitized_trade_320_evidence()
    )

    assert result["dashboard_real_broker_telemetry_goal"] is True
    assert result["dashboard_fake_numbers_allowed"] is False
    assert result["dashboard_mock_numbers_allowed"] is False


def test_money_movement_remains_blocked() -> None:
    result = run_owner_sanitized_telemetry_capture_attempt(
        valid_sanitized_trade_320_evidence()
    )

    assert result["withdrawal_allowed_now"] is False
    assert result["transfer_allowed_now"] is False
    assert result["money_movement_allowed_now"] is False
    assert result["profit_reserve_bucket_mode"] == INTERNAL_LEDGER_ONLY


def test_cli_default_emits_json_without_broker_call() -> None:
    code, payload = run_script(["--json"])

    assert code == 0
    assert payload["script_status"] == OWNER_RUN_SANITIZED_TELEMETRY_CAPTURE_NOT_REQUESTED
    assert payload["broker_read_performed"] is False
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["account_id_read_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["live_endpoint_used"] is False
    assert payload["secrets_written"] is False


def test_report_writer_includes_safety_statements_and_raw_payload_false(
    tmp_path: Path,
) -> None:
    result = run_owner_sanitized_telemetry_capture_attempt()
    report_path = tmp_path / "capture_attempt_report.md"

    write_owner_run_sanitized_telemetry_capture_attempt_report(
        result,
        report_path,
    )

    text = report_path.read_text(encoding="utf-8")
    assert "no new order placed" in text
    assert "no live trade placed" in text
    assert "no broker state modified" in text
    assert "no secrets written" in text
    assert "raw broker payload persisted: false" in text
