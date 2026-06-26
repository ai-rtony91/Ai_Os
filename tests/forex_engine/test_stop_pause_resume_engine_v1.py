from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.broker_health_readonly_v1 import build_sample_snapshot, evaluate_broker_health_readonly  # noqa: E402
from automation.forex_engine.profitability_evidence_v1 import (  # noqa: E402
    build_sample_closed_trades,
    build_sample_replay_summaries,
    build_sample_thresholds,
    build_sample_walk_forward_summaries,
    evaluate_profitability_evidence,
)
from automation.forex_engine.risk_budget_engine_v1 import build_sample_candidate, build_sample_risk_caps, evaluate_risk_budget  # noqa: E402
from automation.forex_engine.stop_pause_resume_engine_v1 import (  # noqa: E402
    PAUSE_REQUIRED,
    REVIEW_ONLY_RESUME,
    STOP_PAUSE_RESUME_INCOMPLETE,
    STOP_REQUIRED,
    build_sample_dashboard_state,
    build_sample_operator_halt_state,
    evaluate_stop_pause_resume,
)


PROTECTED_FLAGS = (
    "broker_execution_allowed",
    "live_trading_allowed",
    "order_submission_allowed",
    "credential_access_allowed",
    "account_access_allowed",
    "dashboard_execution_authority",
    "owner_approval_created",
)


def assert_permissions_false(result: dict) -> None:
    for flag in PROTECTED_FLAGS:
        assert result[flag] is False
        assert result["permissions"][flag] is False


def ready_inputs() -> tuple[dict, dict, dict, dict, dict]:
    risk = evaluate_risk_budget(build_sample_candidate(), build_sample_risk_caps())
    broker = evaluate_broker_health_readonly(build_sample_snapshot())
    profitability = evaluate_profitability_evidence(
        build_sample_closed_trades(),
        build_sample_replay_summaries(),
        build_sample_walk_forward_summaries(),
        build_sample_thresholds(),
    )
    return (
        risk,
        broker,
        profitability,
        build_sample_dashboard_state(),
        build_sample_operator_halt_state(),
    )


def test_safe_review_path_returns_review_only_resume() -> None:
    result = evaluate_stop_pause_resume(*ready_inputs())

    assert result["status"] == REVIEW_ONLY_RESUME
    assert result["control_state"] == "REVIEW_ONLY_RESUME"
    assert result["blockers"] == []
    assert_permissions_false(result)


def test_missing_input_blocks_as_incomplete() -> None:
    risk, broker, profitability, dashboard, _halt = ready_inputs()

    result = evaluate_stop_pause_resume(risk, broker, profitability, dashboard, None)

    assert result["status"] == STOP_PAUSE_RESUME_INCOMPLETE
    assert result["blockers"]
    assert_permissions_false(result)


def test_conflicting_dashboard_authority_stops_chain() -> None:
    risk, broker, profitability, dashboard, halt = ready_inputs()
    dashboard["dashboard_execution_authority"] = True

    result = evaluate_stop_pause_resume(risk, broker, profitability, dashboard, halt)

    assert result["status"] == STOP_REQUIRED
    assert any("unsafe true" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_stale_dashboard_evidence_pauses_chain() -> None:
    risk, broker, profitability, dashboard, halt = ready_inputs()
    dashboard["evidence_fresh"] = False

    result = evaluate_stop_pause_resume(risk, broker, profitability, dashboard, halt)

    assert result["status"] == PAUSE_REQUIRED
    assert any("stale" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_unsafe_upstream_flag_stops_chain() -> None:
    risk, broker, profitability, dashboard, halt = ready_inputs()
    risk["live_trading_allowed"] = True

    result = evaluate_stop_pause_resume(risk, broker, profitability, dashboard, halt)

    assert result["status"] == STOP_REQUIRED
    assert any("unsafe true" in item for item in result["blockers"])
    assert_permissions_false(result)
