from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.dashboard_truth_summary_v1 import (  # noqa: E402
    DASHBOARD_TRUTH_BLOCKED,
    DASHBOARD_TRUTH_DISPLAY_READY,
    DASHBOARD_TRUTH_INCOMPLETE,
    build_dashboard_truth_summary,
)
from automation.forex_engine.forex_closure_integration_bridge_v1 import (  # noqa: E402
    build_sample_integration_input,
    run_forex_closure_integration_bridge,
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


def upstream() -> dict:
    stages = run_forex_closure_integration_bridge(build_sample_integration_input())["stage_results"]
    return {
        "risk": stages["risk"],
        "broker": stages["broker"],
        "profitability": stages["profitability"],
        "stop": stages["stop"],
        "demo_intent": stages["demo_intent"],
    }


def test_safe_review_path_builds_display_only_summary() -> None:
    result = build_dashboard_truth_summary(upstream())

    assert result["status"] == DASHBOARD_TRUTH_DISPLAY_READY
    assert result["display_only"] is True
    assert result["truth_summary"]["evidence_state"] == "DISPLAY_READY"
    assert_permissions_false(result)


def test_missing_input_blocks_as_incomplete() -> None:
    result = build_dashboard_truth_summary(None)

    assert result["status"] == DASHBOARD_TRUTH_INCOMPLETE
    assert result["blockers"]
    assert_permissions_false(result)


def test_conflicting_stage_status_blocks_summary() -> None:
    data = upstream()
    data["risk"] = dict(data["risk"])
    data["risk"]["status"] = "RISK_BUDGET_BLOCKED"

    result = build_dashboard_truth_summary(data)

    assert result["status"] == DASHBOARD_TRUTH_BLOCKED
    assert any("risk status" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_stale_upstream_evidence_blocks_summary() -> None:
    data = upstream()
    data["profitability"] = dict(data["profitability"])
    data["profitability"]["freshness"] = {"state": "STALE", "fresh": False}

    result = build_dashboard_truth_summary(data)

    assert result["status"] == DASHBOARD_TRUTH_BLOCKED
    assert any("stale" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_unsafe_dashboard_authority_blocks_summary() -> None:
    data = upstream()
    data["demo_intent"] = dict(data["demo_intent"])
    data["demo_intent"]["dashboard_execution_authority"] = True

    result = build_dashboard_truth_summary(data)

    assert result["status"] == DASHBOARD_TRUTH_BLOCKED
    assert any("unsafe true" in item for item in result["blockers"])
    assert_permissions_false(result)
