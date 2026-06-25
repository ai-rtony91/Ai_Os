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
    BROKER_EVIDENCE_BLOCKED,
    INTERNAL_LEDGER_ONLY,
    SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED,
    SANITIZED_OWNER_RUN_TELEMETRY_BROKER_BLOCKED,
    SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE,
    SANITIZED_OWNER_RUN_TELEMETRY_MISSING,
    SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_RAW_PAYLOAD,
    SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_SECRET_RISK,
    adapt_sanitized_owner_run_oanda_telemetry,
    validate_owner_run_telemetry_shape,
    write_sanitized_owner_run_read_only_telemetry_adapter_report,
)
from scripts.forex_delivery.run_oanda_demo_sanitized_owner_run_read_only_telemetry_adapter_v1 import (  # noqa: E402
    main as script_main,
)


def valid_sanitized_trade_320_telemetry() -> dict:
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


def test_default_result_reports_telemetry_missing_and_does_not_call_broker() -> None:
    result = adapt_sanitized_owner_run_oanda_telemetry()

    assert result["adapter_status"] == SANITIZED_OWNER_RUN_TELEMETRY_MISSING
    assert result["sanitized_broker_telemetry_ready"] is False
    assert result["broker_evidence_status"] == BROKER_EVIDENCE_BLOCKED
    assert result["broker_network_call_performed"] is False
    assert result["broker_read_performed"] is False
    assert result["no_new_order_placed"] is True
    assert result["no_live_trade_placed"] is True
    assert result["no_broker_state_modified"] is True
    assert result["no_secrets_written"] is True


def test_valid_sanitized_trade_320_telemetry_is_accepted() -> None:
    result = validate_owner_run_telemetry_shape(
        valid_sanitized_trade_320_telemetry()
    )

    assert result["adapter_status"] == SANITIZED_OWNER_RUN_TELEMETRY_ACCEPTED
    assert result["trade_id"] == 320
    assert result["instrument"] == "EUR_USD"
    assert result["next_action"] == "FEED_SANITIZED_TELEMETRY_TO_TRADE_320_PL_REFRESH"


def test_accepted_telemetry_sets_ready_true() -> None:
    result = adapt_sanitized_owner_run_oanda_telemetry(
        valid_sanitized_trade_320_telemetry()
    )

    assert result["sanitized_broker_telemetry_ready"] is True


def test_accepted_telemetry_preserves_pl_values() -> None:
    result = adapt_sanitized_owner_run_oanda_telemetry(
        valid_sanitized_trade_320_telemetry()
    )

    assert result["realized_pl"] == "0.0000"
    assert result["unrealized_pl"] == "-0.0004"


def test_accepted_telemetry_preserves_open_counts() -> None:
    result = adapt_sanitized_owner_run_oanda_telemetry(
        valid_sanitized_trade_320_telemetry()
    )

    assert result["open_trade_count"] == 1
    assert result["open_position_count"] == 1


def test_token_secret_and_account_id_fields_reject_as_secret_risk() -> None:
    for field in ("access_token", "token", "account_id"):
        evidence = valid_sanitized_trade_320_telemetry()
        evidence[field] = "SHOULD_NOT_BE_ACCEPTED"

        result = validate_owner_run_telemetry_shape(evidence)

        assert (
            result["adapter_status"]
            == SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_SECRET_RISK
        )
        assert result["sanitized_broker_telemetry_ready"] is False


def test_raw_broker_payload_and_raw_response_reject_as_raw_payload() -> None:
    for field in ("raw_broker_payload", "raw_response"):
        evidence = valid_sanitized_trade_320_telemetry()
        evidence[field] = {"anything": "forbidden"}

        result = validate_owner_run_telemetry_shape(evidence)

        assert (
            result["adapter_status"]
            == SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_RAW_PAYLOAD
        )
        assert result["sanitized_broker_telemetry_ready"] is False


def test_nested_forbidden_field_is_rejected() -> None:
    evidence = valid_sanitized_trade_320_telemetry()
    evidence["metadata"] = {"headers": {"authorization": "Bearer forbidden"}}

    result = validate_owner_run_telemetry_shape(evidence)

    assert (
        result["adapter_status"]
        == SANITIZED_OWNER_RUN_TELEMETRY_REJECTED_SECRET_RISK
    )
    assert "metadata_headers" in result["rejected_secret_fields"]


def test_invalid_or_missing_trade_id_rejects_invalid_shape() -> None:
    evidence = valid_sanitized_trade_320_telemetry()
    evidence.pop("trade_id")

    result = validate_owner_run_telemetry_shape(evidence)

    assert result["adapter_status"] == SANITIZED_OWNER_RUN_TELEMETRY_INVALID_SHAPE
    assert "trade_id_required" in result["invalid_shape_blockers"]


def test_broker_blocked_evidence_maps_to_broker_blocked() -> None:
    evidence = valid_sanitized_trade_320_telemetry()
    evidence["broker_evidence_status"] = BROKER_EVIDENCE_BLOCKED

    result = validate_owner_run_telemetry_shape(evidence)

    assert result["adapter_status"] == SANITIZED_OWNER_RUN_TELEMETRY_BROKER_BLOCKED
    assert result["broker_evidence_status"] == BROKER_EVIDENCE_BLOCKED
    assert result["sanitized_broker_telemetry_ready"] is False


def test_fake_and_mock_dashboard_numbers_remain_forbidden() -> None:
    result = adapt_sanitized_owner_run_oanda_telemetry(
        valid_sanitized_trade_320_telemetry()
    )

    assert result["dashboard_real_broker_telemetry_goal"] is True
    assert result["dashboard_fake_numbers_allowed"] is False
    assert result["dashboard_mock_numbers_allowed"] is False


def test_money_movement_remains_blocked() -> None:
    result = adapt_sanitized_owner_run_oanda_telemetry(
        valid_sanitized_trade_320_telemetry()
    )

    assert result["withdrawal_allowed_now"] is False
    assert result["transfer_allowed_now"] is False
    assert result["money_movement_allowed_now"] is False
    assert result["profit_reserve_bucket_mode"] == INTERNAL_LEDGER_ONLY


def test_cli_default_emits_json_without_broker_call() -> None:
    code, payload = run_script(["--json"])

    assert code == 0
    assert payload["script_status"] == SANITIZED_OWNER_RUN_TELEMETRY_MISSING
    assert payload["broker_network_call_performed"] is False
    assert payload["credential_read_performed"] is False
    assert payload["account_id_read_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["live_endpoint_used"] is False
    assert payload["secrets_written"] is False


def test_report_writer_includes_no_order_no_live_no_broker_state_no_secrets(
    tmp_path: Path,
) -> None:
    result = adapt_sanitized_owner_run_oanda_telemetry()
    report_path = tmp_path / "packet_07_adapter_report.md"

    write_sanitized_owner_run_read_only_telemetry_adapter_report(
        result,
        report_path,
    )

    text = report_path.read_text(encoding="utf-8")
    assert "no new order placed" in text
    assert "no live trade placed" in text
    assert "no broker state modified" in text
    assert "no secrets written" in text
    assert "fake/mock dashboard account values are forbidden" in text
