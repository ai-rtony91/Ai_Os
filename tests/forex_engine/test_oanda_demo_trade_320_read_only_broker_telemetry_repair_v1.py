from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_trade_320_read_only_broker_telemetry_repair_v1 import (  # noqa: E402
    BROKER_EVIDENCE_BLOCKED,
    INTERNAL_LEDGER_ONLY,
    READ_ONLY_BROKER_TELEMETRY_READY,
    READ_ONLY_HELPER_MISSING,
    READ_ONLY_HELPER_REJECTED_UNSANITIZED_RESULT,
    SECRET_RISK_DETECTED,
    build_sanitized_trade_320_broker_telemetry_result,
    diagnose_trade_320_read_only_broker_telemetry,
    write_trade_320_read_only_broker_telemetry_repair_report,
)
from scripts.forex_delivery.run_oanda_demo_trade_320_read_only_broker_telemetry_repair_v1 import (  # noqa: E402
    main as script_main,
)


def ready_evidence() -> dict:
    return {
        "safe_read_only_helper_available": True,
        "sanitized_evidence_only": True,
        "broker_read_method": "GET",
        "broker_read_mode": "OWNER_RUN_READ_ONLY_BROKER_REQUESTED",
        "broker_evidence_status": "OWNER_RUN_READ_ONLY_EVIDENCE_CLASSIFIED",
        "trade_id": 320,
        "instrument": "EUR_USD",
        "monitor_bucket": "OPEN_UNREALIZED_NEGATIVE",
        "result_bucket": "NO_PROFIT_EVIDENCE_OPEN_NEGATIVE",
        "realized_pl": "0.0000",
        "unrealized_pl": "-0.0004",
        "open_trade_count": 1,
        "open_position_count": 1,
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


def test_observed_packet_04_blocked_result_maps_to_broker_evidence_blocked() -> None:
    result = diagnose_trade_320_read_only_broker_telemetry()

    assert result["broker_evidence_status"] == BROKER_EVIDENCE_BLOCKED
    assert result["broker_evidence_blocked"] is True
    assert result["next_action"] == "REPAIR_READ_ONLY_HELPER_OR_RUNTIME_AUTH_BOUNDARY"


def test_missing_helper_maps_to_read_only_helper_missing() -> None:
    evidence = ready_evidence()
    evidence["safe_read_only_helper_available"] = False

    result = build_sanitized_trade_320_broker_telemetry_result(evidence)

    assert result["broker_evidence_status"] == READ_ONLY_HELPER_MISSING
    assert "safe_read_only_helper_available_false" in result["blockers"]


def test_unsanitized_helper_result_is_rejected() -> None:
    evidence = ready_evidence()
    evidence["sanitized_evidence_only"] = False

    result = build_sanitized_trade_320_broker_telemetry_result(evidence)

    assert (
        result["broker_evidence_status"]
        == READ_ONLY_HELPER_REJECTED_UNSANITIZED_RESULT
    )
    assert "sanitized_evidence_only_must_not_be_false" in result["blockers"]


def test_secret_like_fields_map_to_secret_risk_detected() -> None:
    evidence = ready_evidence()
    evidence["access_token"] = "SHOULD_NOT_BE_ACCEPTED"

    result = build_sanitized_trade_320_broker_telemetry_result(evidence)

    assert result["broker_evidence_status"] == SECRET_RISK_DETECTED
    assert result["sanitized_broker_telemetry_ready"] is False


def test_sanitized_read_only_telemetry_maps_to_ready() -> None:
    result = build_sanitized_trade_320_broker_telemetry_result(ready_evidence())

    assert result["broker_evidence_status"] == READ_ONLY_BROKER_TELEMETRY_READY
    assert result["sanitized_broker_telemetry_ready"] is True
    assert result["broker_read_mode"] == "OWNER_RUN_READ_ONLY_BROKER_REQUESTED"
    assert result["monitor_bucket"] == "OPEN_UNREALIZED_NEGATIVE"
    assert result["result_bucket"] == "NO_PROFIT_EVIDENCE_OPEN_NEGATIVE"


def test_fake_or_mock_dashboard_account_values_remain_forbidden() -> None:
    result = build_sanitized_trade_320_broker_telemetry_result(ready_evidence())

    assert result["dashboard_real_broker_telemetry_goal"] is True
    assert result["dashboard_fake_numbers_allowed"] is False
    assert result["dashboard_mock_numbers_allowed"] is False


def test_withdrawal_transfer_and_money_movement_remain_false() -> None:
    result = build_sanitized_trade_320_broker_telemetry_result(ready_evidence())

    assert result["withdrawal_allowed_now"] is False
    assert result["transfer_allowed_now"] is False
    assert result["money_movement_allowed_now"] is False


def test_profit_reserve_bucket_remains_internal_ledger_only() -> None:
    result = build_sanitized_trade_320_broker_telemetry_result(ready_evidence())

    assert result["profit_reserve_bucket_mode"] == INTERNAL_LEDGER_ONLY


def test_cli_default_emits_json_without_broker_call() -> None:
    code, payload = run_script(["--json"])

    assert code == 0
    assert payload["script_status"] == BROKER_EVIDENCE_BLOCKED
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["live_endpoint_used"] is False
    assert payload["secrets_written"] is False
    assert payload["result"]["broker_evidence_status"] == BROKER_EVIDENCE_BLOCKED


def test_report_writer_includes_no_order_no_live_no_broker_state_no_secrets(
    tmp_path: Path,
) -> None:
    result = diagnose_trade_320_read_only_broker_telemetry()
    report_path = tmp_path / "broker_telemetry_repair_report.md"

    write_trade_320_read_only_broker_telemetry_repair_report(result, report_path)

    text = report_path.read_text(encoding="utf-8")
    assert "no new order placed" in text
    assert "no live trade placed" in text
    assert "no broker state modified" in text
    assert "no secrets written" in text
    assert "fake/mock dashboard account values are forbidden" in text

