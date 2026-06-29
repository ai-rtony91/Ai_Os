from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from automation.forex_engine import supervised_autonomy_governor_v1 as governor


RUNNER_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "forex_delivery"
    / "run_supervised_autonomy_governor_v1.py"
)


def test_insufficient_sample_blocks_autonomy():
    result = governor.evaluate_supervised_autonomy_candidate(
        ready_input(sample_size=12, walk_forward_windows=2)
    )

    assert result["candidate_status"] == governor.REQUIRE_MORE_EVIDENCE
    assert "sample_sufficiency" in result["failed_gates"]


def test_negative_expectancy_blocks_autonomy():
    result = governor.evaluate_supervised_autonomy_candidate(
        ready_input(expectancy=-0.75)
    )

    assert result["candidate_status"] == governor.REQUIRE_MORE_EVIDENCE
    assert "expectancy_threshold" in result["failed_gates"]


def test_low_profit_factor_blocks_autonomy():
    result = governor.evaluate_supervised_autonomy_candidate(
        ready_input(profit_factor=1.10)
    )

    assert result["candidate_status"] == governor.REQUIRE_MORE_EVIDENCE
    assert "profit_factor_threshold" in result["failed_gates"]


def test_missing_order_count_last_24h_fails_order_count_gate():
    base = ready_input()
    base.pop("order_count_last_24h", None)
    result = governor.evaluate_supervised_autonomy_candidate(base)

    assert governor.GATE_ORDER_COUNT in result["failed_gates"]
    assert "order_count_last_24h is required" in result["blockers"]


def test_malformed_order_count_last_24h_fails_order_count_gate():
    result = governor.evaluate_supervised_autonomy_candidate(
        ready_input(order_count_last_24h="bad-value")
    )

    assert governor.GATE_ORDER_COUNT in result["failed_gates"]
    assert "order_count_last_24h is required" in result["blockers"]


def test_zero_order_count_last_24h_passes_order_count_gate():
    result = governor.evaluate_supervised_autonomy_candidate(
        ready_input(order_count_last_24h=0)
    )

    assert governor.GATE_ORDER_COUNT in result["passed_gates"]


def test_excessive_drawdown_blocks_autonomy():
    result = governor.evaluate_supervised_autonomy_candidate(
        ready_input(max_drawdown=0.40)
    )

    assert result["candidate_status"] == governor.REQUIRE_MORE_EVIDENCE
    assert "drawdown_limits" in result["failed_gates"]


def test_missing_kill_switch_blocks_autonomy():
    result = governor.evaluate_supervised_autonomy_candidate(
        ready_input(kill_switch_state="DISARMED")
    )

    assert result["candidate_status"] == governor.AUTONOMY_BLOCKED
    assert "kill_switch_state" in result["failed_gates"]


def test_missing_tp_sl_blocks_live_review():
    result = governor.evaluate_supervised_autonomy_candidate(
        ready_input(
            live_exception_requested=True,
            owner_approval_status="APPROVED_FOR_LIVE_MICRO",
            owner_live_micro_exception_approved=True,
            live_bridge_external_evidence=True,
            live_bridge_eligibility=True,
            tp_sl_present=False,
        )
    )

    assert result["candidate_status"] == governor.LIVE_BLOCKED_BY_POLICY
    assert "tp_sl_presence" in result["failed_gates"]


def test_demo_supervised_readiness_path():
    result = governor.evaluate_supervised_autonomy_candidate(
        ready_input(owner_approval_status="APPROVED_FOR_DEMO", live_exception_requested=False)
    )

    assert result["candidate_status"] == governor.DEMO_SUPERVISED_READY
    assert result["live_trading_allowed"] is False
    assert result["profit_claim_allowed"] is False


def test_live_micro_exception_review_ready_path_with_sanitized_approval_evidence():
    result = governor.evaluate_supervised_autonomy_candidate(
        ready_input(
            live_exception_requested=True,
            owner_approval_status="APPROVED_FOR_LIVE_MICRO",
            owner_live_micro_exception_approved=True,
            live_bridge_external_evidence=True,
            live_bridge_eligibility=True,
        )
    )

    assert result["candidate_status"] == governor.LIVE_MICRO_EXCEPTION_REVIEW_READY
    assert result["live_trading_allowed"] is True
    assert result["profit_claim_allowed"] is False

    assert "live_order_permission" not in result


def test_no_credential_or_account_persistence_fields_appear():
    payload = governor.evaluate_supervised_autonomy_candidate(ready_input())
    lowered_json = json.dumps(payload).lower()

    assert "api_key" not in lowered_json
    assert "api token" not in lowered_json
    assert not _contains_key(payload, "account_id")
    assert not _contains_key(payload, "credential")


def test_no_broker_network_or_credentials_by_source():
    module_source = Path(governor.__file__).read_text(encoding="utf-8").lower()
    script_source = Path(RUNNER_PATH).read_text(encoding="utf-8").lower()
    combined = module_source + "\n" + script_source
    forbidden_snippets = (
        "os.environ",
        "dotenv",
        "requests",
        "urllib",
        "socket",
        "import broker",
        "from broker",
        "import oanda",
        "from oanda",
    )

    assert not [snippet for snippet in forbidden_snippets if snippet in combined]


def test_cli_prints_json_for_default_sample():
    completed = subprocess.run(
        [sys.executable, str(RUNNER_PATH)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["candidate_status"] == governor.REQUIRE_MORE_EVIDENCE
    assert payload["autonomy_window_target"] == governor.AUTONOMY_WINDOW_TARGET
    assert payload["live_trading_allowed"] is False


def test_cli_supports_input_json(tmp_path: Path) -> None:
    input_file = tmp_path / "supervised_autonomy_candidate.json"
    input_file.write_text(
        json.dumps(ready_input(owner_approval_status="APPROVED_FOR_DEMO")),
        encoding="utf-8",
    )
    completed = subprocess.run(
        [sys.executable, str(RUNNER_PATH), "--input-json", str(input_file)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["candidate_status"] == governor.DEMO_SUPERVISED_READY


def test_cli_rejects_non_dict_json_payload(tmp_path: Path) -> None:
    input_file = tmp_path / "supervised_autonomy_candidate.json"
    input_file.write_text(json.dumps(["not-a-dict"]), encoding="utf-8")
    completed = subprocess.run(
        [sys.executable, str(RUNNER_PATH), "--input-json", str(input_file)],
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert "input JSON payload must be a JSON object" in completed.stderr


def test_run_function_can_write_report_to_temp_path(tmp_path: Path) -> None:
    report_path = tmp_path / "AIOS_FOREX_SUPERVISED_AUTONOMY_GOVERNOR_V1_REPORT.md"
    output = governor.run_supervised_autonomy_governor(
        ready_input(),
        write_report=True,
        report_path=report_path,
    )
    payload = governor.evaluate_supervised_autonomy_candidate(ready_input())

    assert output["candidate_status"] == payload["candidate_status"]
    assert report_path.exists()
    assert report_path.read_text(encoding="utf-8").startswith(
        "# AIOS Forex Supervised Autonomy Governor V1 Report"
    )


def _contains_key(value: object, needle: str) -> bool:
    if isinstance(value, dict):
        return any(
            key == needle or _contains_key(sub, needle)
            for key, sub in value.items()
        )
    if isinstance(value, list):
        return any(_contains_key(item, needle) for item in value)
    return False


def ready_input(**overrides: object) -> dict[str, object]:
    base = {
        "candidate_id": "sample-demo-ready",
        "profitability_evidence_status": "READY",
        "sample_size": 120,
        "walk_forward_windows": 4,
        "max_drawdown": 0.08,
        "profit_factor": 2.5,
        "expectancy": 0.75,
        "broker_readiness": True,
        "live_bridge_eligibility": False,
        "kill_switch_state": "ARMED",
        "daily_stop_state": "ARMED",
        "max_loss_state": "ARMED",
        "order_count_last_24h": 2,
        "tp_sl_present": True,
        "monitoring_ready": True,
        "evidence_age_days": 2,
        "owner_approval_status": "APPROVED_FOR_DEMO",
        "live_exception_requested": False,
        "live_bridge_external_evidence": False,
        "owner_live_micro_exception_approved": False,
        "realized_broker_evidence": False,
    }
    base.update(overrides)
    return base
