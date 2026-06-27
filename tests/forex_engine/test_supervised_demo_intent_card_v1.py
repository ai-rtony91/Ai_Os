from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_closure_integration_bridge_v1 import (  # noqa: E402
    build_sample_integration_input,
    run_forex_closure_integration_bridge,
)
from automation.forex_engine.supervised_demo_intent_card_v1 import (  # noqa: E402
    DEMO_INTENT_BLOCKED,
    DEMO_INTENT_INCOMPLETE,
    DEMO_INTENT_OWNER_REVIEW_READY,
    evaluate_supervised_demo_intent_card,
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


def stage_results(payload: dict | None = None) -> dict:
    return run_forex_closure_integration_bridge(payload or build_sample_integration_input())["stage_results"]


def test_safe_review_path_builds_owner_review_card() -> None:
    stages = stage_results()
    result = stages["demo_intent"]

    assert result["status"] == DEMO_INTENT_OWNER_REVIEW_READY
    assert result["owner_review_card"]["review_scope"] == "owner_review_only_no_execution"
    assert result["owner_approval_created"] is False
    assert_permissions_false(result)


def test_missing_input_blocks_as_incomplete() -> None:
    stages = stage_results()

    result = evaluate_supervised_demo_intent_card(
        None,
        stages["risk"],
        stages["broker"],
        stages["profitability"],
        stages["stop"],
    )

    assert result["status"] == DEMO_INTENT_INCOMPLETE
    assert result["blockers"]
    assert_permissions_false(result)


def test_conflicting_stop_state_blocks_card() -> None:
    stages = stage_results()
    stop = dict(stages["stop"])
    stop["status"] = "STOP_REQUIRED"

    result = evaluate_supervised_demo_intent_card(
        build_sample_integration_input()["candidate"],
        stages["risk"],
        stages["broker"],
        stages["profitability"],
        stop,
    )

    assert result["status"] == DEMO_INTENT_BLOCKED
    assert any("stop state" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_stale_candidate_blocks_card() -> None:
    payload = build_sample_integration_input()
    payload["candidate"]["evidence_age_days"] = 99

    result = run_forex_closure_integration_bridge(payload)["stage_results"]["demo_intent"]

    assert result["status"] == DEMO_INTENT_BLOCKED
    assert any("stale" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_unsafe_candidate_flag_blocks_card() -> None:
    payload = build_sample_integration_input()
    payload["candidate"]["live_trading_allowed"] = True

    result = run_forex_closure_integration_bridge(payload)["stage_results"]["demo_intent"]

    assert result["status"] == DEMO_INTENT_BLOCKED
    assert any("unsafe true" in item for item in result["blockers"])
    assert_permissions_false(result)
