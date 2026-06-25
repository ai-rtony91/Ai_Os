from __future__ import annotations

from contextlib import redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from automation.forex_engine.oanda_demo_trade_320_owner_run_read_only_refresh_gate_v1 import (  # noqa: E402
    BROKER_EVIDENCE_BLOCKED,
    INVALID_GATE_EVIDENCE,
    OWNER_RUN_FLAG_REQUIRED,
    OWNER_RUN_READ_ONLY_REFRESH_READY,
    SECRET_RISK_DETECTED,
    evaluate_trade_320_owner_run_read_only_refresh_gate,
    write_trade_320_owner_run_read_only_refresh_gate_report,
)
from scripts.forex_delivery.run_oanda_demo_trade_320_owner_run_read_only_refresh_gate_v1 import (  # noqa: E402
    main as script_main,
)


def ready_evidence() -> dict:
    return {
        "owner_run_read_broker_now": True,
        "safe_read_only_helper_available": True,
        "sanitized_evidence_only": True,
        "broker_read_method": "GET",
        "trade_id": "320",
        "instrument": "EUR_USD",
        "helper_status": "OWNER_RUN_READ_ONLY_EVIDENCE_CLASSIFIED",
        "broker_evidence_status": "OWNER_RUN_READ_ONLY_EVIDENCE_CLASSIFIED",
        "order_placement_performed": False,
        "order_close_performed": False,
        "order_mutation_performed": False,
        "trade_mutation_performed": False,
        "position_mutation_performed": False,
        "live_endpoint_used": False,
        "secrets_written": False,
    }


def run_script(args: list[str], *, owner_run_helper=None) -> tuple[int, dict]:
    stream = StringIO()
    with redirect_stdout(stream):
        code = script_main(args, owner_run_helper=owner_run_helper)
    return code, json.loads(stream.getvalue())


def test_default_gate_requires_owner_run_flag() -> None:
    result = evaluate_trade_320_owner_run_read_only_refresh_gate()

    assert result["gate_status"] == OWNER_RUN_FLAG_REQUIRED
    assert result["owner_run_flag_required"] is True
    assert result["next_action"] == (
        "RUN_OWNER_READ_ONLY_REFRESH_WITH_EXPLICIT_FLAG_OR_KEEP_OFFLINE_MONITORING"
    )


def test_default_gate_does_not_allow_broker_read_now() -> None:
    result = evaluate_trade_320_owner_run_read_only_refresh_gate()

    assert result["broker_read_allowed_now"] is False
    assert result["broker_read_mode"] == "NOT_REQUESTED"
    assert "no broker read was requested" in result["notes"][0]
    assert "Owner-authorized read-only broker telemetry remains" in result["notes"][0]


def test_default_gate_declares_real_broker_telemetry_dashboard_goal() -> None:
    result = evaluate_trade_320_owner_run_read_only_refresh_gate()

    assert result["dashboard_real_broker_telemetry_goal"] is True
    assert (
        result["broker_data_source_required"]
        == "OWNER_AUTHORIZED_READ_ONLY_BROKER_SOURCE"
    )


def test_fake_or_mock_dashboard_account_numbers_are_not_allowed() -> None:
    result = evaluate_trade_320_owner_run_read_only_refresh_gate()

    assert result["dashboard_fake_numbers_allowed"] is False
    assert result["dashboard_mock_numbers_allowed"] is False


def test_withdrawal_transfer_and_money_movement_are_blocked_now() -> None:
    result = evaluate_trade_320_owner_run_read_only_refresh_gate()

    assert result["withdrawal_allowed_now"] is False
    assert result["transfer_allowed_now"] is False
    assert result["money_movement_allowed_now"] is False
    assert (
        result["bank_data_source_required"]
        == "FUTURE_OWNER_AUTHORIZED_READ_ONLY_BANK_SOURCE"
    )


def test_profit_reserve_bucket_is_internal_ledger_only() -> None:
    result = evaluate_trade_320_owner_run_read_only_refresh_gate()

    assert result["profit_reserve_bucket_mode"] == "INTERNAL_LEDGER_ONLY"
    assert (
        result[
            "profit_reserve_bucket_money_movement_requires_future_owner_gate"
        ]
        is True
    )


def test_owner_run_flag_can_produce_ready_status_with_sanitized_prerequisites() -> None:
    result = evaluate_trade_320_owner_run_read_only_refresh_gate(ready_evidence())

    assert result["gate_status"] == OWNER_RUN_READ_ONLY_REFRESH_READY
    assert result["broker_read_allowed_now"] is True
    assert result["owner_run_flag_required"] is False
    assert result["broker_read_mode"] == "OWNER_RUN_READ_ONLY_BROKER_REQUESTED"


def test_missing_safe_helper_maps_to_broker_evidence_blocked() -> None:
    evidence = ready_evidence()
    evidence["safe_read_only_helper_available"] = False

    result = evaluate_trade_320_owner_run_read_only_refresh_gate(evidence)

    assert result["gate_status"] == BROKER_EVIDENCE_BLOCKED
    assert result["broker_read_allowed_now"] is False
    assert "safe_read_only_helper_available_required" in result["blockers"]


def test_secret_like_fields_map_to_secret_risk_detected() -> None:
    evidence = ready_evidence()
    evidence["access_token"] = "SHOULD_NOT_BE_ACCEPTED"

    result = evaluate_trade_320_owner_run_read_only_refresh_gate(evidence)

    assert result["gate_status"] == SECRET_RISK_DETECTED
    assert result["forbidden_secret_fields_absent"] is False
    assert result["broker_read_allowed_now"] is False


def test_account_identifying_fields_map_to_secret_risk_detected() -> None:
    evidence = ready_evidence()
    evidence["broker_account_id"] = "SHOULD_NOT_BE_ACCEPTED"

    result = evaluate_trade_320_owner_run_read_only_refresh_gate(evidence)

    assert result["gate_status"] == SECRET_RISK_DETECTED
    assert result["forbidden_secret_fields_absent"] is False
    assert result["broker_read_allowed_now"] is False


def test_invalid_evidence_maps_to_invalid_gate_evidence() -> None:
    result = evaluate_trade_320_owner_run_read_only_refresh_gate(["not", "mapping"])

    assert result["gate_status"] == INVALID_GATE_EVIDENCE
    assert result["broker_read_allowed_now"] is False


def test_cli_default_emits_json_without_broker_calls() -> None:
    def fail_if_called() -> dict:
        raise AssertionError("owner-run helper must not be called by default")

    code, payload = run_script(["--json"], owner_run_helper=fail_if_called)

    assert code == 0
    assert payload["script_status"] == OWNER_RUN_FLAG_REQUIRED
    assert payload["broker_read_allowed_now"] is False
    assert payload["dashboard_real_broker_telemetry_goal"] is True
    assert payload["dashboard_fake_numbers_allowed"] is False
    assert payload["money_movement_allowed_now"] is False
    assert payload["broker_network_call_performed"] is False
    assert payload["order_placement_performed"] is False
    assert payload["live_endpoint_used"] is False
    assert payload["secrets_written"] is False


def test_report_writer_includes_safety_statements(tmp_path: Path) -> None:
    result = evaluate_trade_320_owner_run_read_only_refresh_gate()
    report_path = tmp_path / "owner_run_gate_report.md"

    write_trade_320_owner_run_read_only_refresh_gate_report(result, report_path)

    text = report_path.read_text(encoding="utf-8")
    assert "no new order placed" in text
    assert "no live trade placed" in text
    assert "no broker state modified" in text
    assert "no secrets written" in text
    assert "Dashboard Real Data Doctrine" in text
    assert "no fake balances" in text
    assert "profit reserve bucket is internal ledger only" in text
