from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from automation.forex_engine import (
    forex_autonomy_completion_governor_rerun_and_bucket_policy_v1 as controller,
)

from automation.forex_engine import supervised_autonomy_governor_v1 as governor


RUNNER_PATH = (
    Path(__file__).resolve().parents[2]
    / "scripts"
    / "forex_delivery"
    / "run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py"
)

STATE_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_AUTONOMY_COMPLETION_STATE_MODEL_V1.json"
)

GOVERNOR_INPUT_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_LIVE_MICRO_EXCEPTION_GOVERNOR_INPUT_TEMPLATE_V1.json"
)


def test_kill_switch_disarmed_preserves_autonomy_block_and_risk_reset():
    result = controller.run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1(
        governor_input_mapping=_policy_ready_governor_input(
            {"kill_switch_state": "DISARMED"},
        ),
    )

    assert result["candidate_status"] == governor.AUTONOMY_BLOCKED
    assert result["next_autonomy_action"] == controller.HOLD_FOR_RISK_RESET
    assert result["bucket_status"] == controller.BUCKET_MAX_LOSS_HOLD


def test_daily_stop_disarmed_preserves_autonomy_block_and_risk_reset():
    result = controller.run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1(
        governor_input_mapping=_policy_ready_governor_input(
            {"daily_stop_state": "DISARMED"},
        ),
    )

    assert result["candidate_status"] == governor.AUTONOMY_BLOCKED
    assert result["next_autonomy_action"] == controller.HOLD_FOR_RISK_RESET
    assert result["bucket_status"] == controller.BUCKET_MAX_LOSS_HOLD


def test_max_loss_state_unset_preserves_autonomy_block_and_risk_reset():
    result = controller.run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1(
        governor_input_mapping=_policy_ready_governor_input(
            {"max_loss_state": "UNSET"},
        ),
    )

    assert result["candidate_status"] == governor.AUTONOMY_BLOCKED
    assert result["next_autonomy_action"] == controller.HOLD_FOR_RISK_RESET
    assert result["bucket_status"] == controller.BUCKET_MAX_LOSS_HOLD


def test_ordinary_evidence_shortfall_routes_require_more_and_collect_more():
    result = controller.run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1(
        governor_input_mapping=_evidence_shortfall_governor_input(),
    )

    assert result["candidate_status"] == governor.REQUIRE_MORE_EVIDENCE
    assert result["next_autonomy_action"] == controller.COLLECT_MORE_EVIDENCE


def test_live_bridge_policy_failure_routes_policy_hold():
    result = controller.run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1(
        governor_input_mapping=_policy_ready_governor_input(
            {"live_bridge_eligibility": False},
        ),
    )

    assert result["next_autonomy_action"] == controller.HOLD_FOR_POLICY_REVIEW
    assert result["bucket_status"] == controller.BUCKET_POLICY_BLOCKED


def test_tp_sl_policy_failure_routes_policy_hold():
    result = controller.run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1(
        governor_input_mapping=_policy_ready_governor_input(
            {"tp_sl_present": False},
        ),
    )

    assert result["next_autonomy_action"] == controller.HOLD_FOR_POLICY_REVIEW
    assert result["bucket_status"] == controller.BUCKET_POLICY_BLOCKED


def test_owner_denied_routes_owner_gate():
    result = controller.run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1(
        governor_input_mapping=_policy_ready_governor_input(
            {"owner_approval_status": "DENIED"},
        ),
    )

    assert result["candidate_status"] == governor.AUTONOMY_BLOCKED
    assert result["next_autonomy_action"] == controller.HOLD_FOR_OWNER_GATE
    assert result["bucket_status"] == controller.BUCKET_POLICY_BLOCKED


def test_live_micro_exception_review_ready_routes_owner_review_without_execution():
    result = controller.run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1(
        governor_input_mapping=_live_micro_ready_input(),
    )

    assert result["candidate_status"] == governor.LIVE_MICRO_EXCEPTION_REVIEW_READY
    assert result["next_autonomy_action"] == controller.ROUTE_OWNER_LIVE_MICRO_REVIEW
    assert result["safety_boundary"]["order_execution_allowed"] is False
    assert result["safety_boundary"]["broker_api_allowed"] is False
    assert result["safety_boundary"]["credentials_allowed"] is False
    assert result["safety_boundary"]["account_identifier_persistence_allowed"] is False
    assert result["safety_boundary"]["scheduler_allowed"] is False
    assert result["safety_boundary"]["daemon_allowed"] is False
    assert result["safety_boundary"]["webhook_allowed"] is False


def test_bucket_target_reached_routes_to_target_hold():
    result = controller.run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1(
        state_mapping={
            "cumulative_return_percent": 100,
            "cumulative_return_target_percent_low": 100,
            "cumulative_return_target_percent_high": 120,
            "capital_bucket_mode": "FIXED_DAILY_BUCKET",
        },
        governor_input_mapping=_policy_ready_governor_input(),
    )

    assert result["bucket_status"] == controller.BUCKET_TARGET_HOLD
    assert result["cumulative_return_percent"] == 100.0
    assert result["cumulative_return_target_percent_low"] == 100.0
    assert result["cumulative_return_target_percent_high"] == 120.0
    assert result["bucket_blockers"] == ["cumulative_return_target_low_reached"]


def test_bucket_stretch_target_reached_routes_to_target_hold():
    result = controller.run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1(
        state_mapping={
            "cumulative_return_percent": 120,
            "cumulative_return_target_percent_low": 100,
            "cumulative_return_target_percent_high": 120,
            "capital_bucket_mode": "FIXED_DAILY_BUCKET",
        },
        governor_input_mapping=_policy_ready_governor_input(),
    )

    assert result["bucket_status"] == controller.BUCKET_TARGET_HOLD
    assert result["bucket_blockers"] == ["cumulative_return_target_high_reached"]


def test_max_loss_state_routes_to_max_loss_hold():
    result = controller.run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1(
        governor_input_mapping=_policy_ready_governor_input(
            {"max_loss_state": "UNSET"},
        ),
    )

    assert result["bucket_status"] == controller.BUCKET_MAX_LOSS_HOLD


def test_bucket_not_ready_when_critical_safety_failures_exist():
    cases = [
        _policy_ready_governor_input({"kill_switch_state": "DISARMED"}),
        _policy_ready_governor_input({"daily_stop_state": "DISARMED"}),
        _policy_ready_governor_input({"max_loss_state": "UNSET"}),
    ]

    for governor_input in cases:
        result = controller.run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1(
            governor_input_mapping=governor_input,
        )
        assert result["bucket_status"] != controller.BUCKET_READY


def test_no_forbidden_source_imports_in_controller_and_runner() -> None:
    source = Path(
        "automation/forex_engine/forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py"
    ).read_text(encoding="utf-8").lower()
    runner_source = Path(
        "scripts/forex_delivery/run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py"
    ).read_text(encoding="utf-8").lower()
    forbidden = (
        "requests",
        "socket",
        "urllib",
        "dotenv",
        "os.environ",
        "import oanda",
        "from oanda",
        "import broker",
        "from broker",
    )

    assert not [fragment for fragment in forbidden if fragment in source + "\n" + runner_source]


def test_default_sanitized_inputs_require_more_evidence():
    result = controller.run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1(
        state_json=STATE_PATH,
        governor_input_json=GOVERNOR_INPUT_PATH,
    )

    assert result["candidate_status"] == governor.AUTONOMY_BLOCKED
    assert result["next_autonomy_action"] == controller.HOLD_FOR_RISK_RESET


def test_runner_rejects_non_dict_input_payload(tmp_path: Path) -> None:
    state_path = tmp_path / "state.json"
    governor_path = tmp_path / "governor.json"
    state_path.write_text(json.dumps({"current_stage": "ready"}), encoding="utf-8")
    governor_path.write_text(json.dumps(["not-a-dict"]), encoding="utf-8")
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "--state-json",
            str(state_path),
            "--governor-input-json",
            str(governor_path),
        ],
        capture_output=True,
        text=True,
    )

    assert completed.returncode != 0
    assert "JSON payload at" in completed.stderr
    assert "must be an object" in completed.stderr


def test_runner_prints_valid_json() -> None:
    completed = subprocess.run(
        [sys.executable, str(RUNNER_PATH)],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(completed.stdout)

    assert payload["candidate_status"] == governor.AUTONOMY_BLOCKED
    assert "next_safe_action" in payload


def _policy_ready_governor_input(overrides: dict[str, object] | None = None) -> dict[str, object]:
    payload: dict[str, object] = {
        "candidate_id": "test-autonomy-controller",
        "profitability_evidence_status": "READY",
        "sample_size": 60,
        "walk_forward_windows": 4,
        "max_drawdown": 0.08,
        "profit_factor": 2.5,
        "expectancy": 0.75,
        "broker_readiness": True,
        "live_bridge_eligibility": True,
        "kill_switch_state": "ARMED",
        "daily_stop_state": "ARMED",
        "max_loss_state": "ARMED",
        "order_count_last_24h": 2,
        "tp_sl_present": True,
        "monitoring_ready": True,
        "evidence_age_days": 5,
        "owner_approval_status": "APPROVED_FOR_DEMO",
        "live_exception_requested": False,
        "live_bridge_external_evidence": True,
        "owner_live_micro_exception_approved": False,
        "realized_broker_evidence": False,
    }
    if overrides:
        payload.update(overrides)
    return payload


def _evidence_shortfall_governor_input() -> dict[str, object]:
    return _policy_ready_governor_input(
        {
            "profitability_evidence_status": "PENDING",
            "sample_size": 10,
            "walk_forward_windows": 1,
            "max_drawdown": 0.21,
            "profit_factor": 1.0,
            "expectancy": -0.1,
            "evidence_age_days": 40,
        }
    )


def _live_micro_ready_input() -> dict[str, object]:
    return _policy_ready_governor_input(
        {
            "candidate_id": "test-live-ready",
            "profitability_evidence_status": "READY",
            "sample_size": 120,
            "walk_forward_windows": 4,
            "max_drawdown": 0.08,
            "profit_factor": 2.5,
            "expectancy": 0.75,
            "live_exception_requested": True,
            "live_bridge_external_evidence": True,
            "owner_live_micro_exception_approved": True,
            "owner_approval_status": "APPROVED_FOR_LIVE_MICRO",
            "live_bridge_eligibility": True,
        }
    )
