from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.risk_budget_engine_v1 import (  # noqa: E402
    RISK_BUDGET_ACCEPTED,
    RISK_BUDGET_BLOCKED,
    RISK_BUDGET_INCOMPLETE,
    build_sample_candidate,
    build_sample_risk_caps,
    evaluate_risk_budget,
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


def test_safe_review_path_accepts_risk_budget() -> None:
    result = evaluate_risk_budget(build_sample_candidate(), build_sample_risk_caps())

    assert result["status"] == RISK_BUDGET_ACCEPTED
    assert result["blockers"] == []
    assert result["risk_budget"]["review_only"] is True
    assert_permissions_false(result)


def test_missing_input_blocks_as_incomplete() -> None:
    result = evaluate_risk_budget(None, build_sample_risk_caps())

    assert result["status"] == RISK_BUDGET_INCOMPLETE
    assert result["blockers"]
    assert_permissions_false(result)


def test_conflicting_input_blocks_when_risk_exceeds_cap() -> None:
    candidate = build_sample_candidate()
    candidate["risk_per_trade_pct"] = 4.0

    result = evaluate_risk_budget(candidate, build_sample_risk_caps())

    assert result["status"] == RISK_BUDGET_BLOCKED
    assert any("exceeds risk cap" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_stale_evidence_blocks_risk_budget() -> None:
    candidate = build_sample_candidate()
    candidate["evidence_age_days"] = 99

    result = evaluate_risk_budget(candidate, build_sample_risk_caps())

    assert result["status"] == RISK_BUDGET_BLOCKED
    assert any("stale" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_unsafe_flag_and_account_like_field_block() -> None:
    candidate = build_sample_candidate()
    candidate["live_trading_allowed"] = True
    candidate["account_id"] = "blocked-account-like-value"

    result = evaluate_risk_budget(candidate, build_sample_risk_caps())

    assert result["status"] == RISK_BUDGET_BLOCKED
    assert any("unsafe true" in item for item in result["blockers"])
    assert any("account-like" in item for item in result["blockers"])
    assert_permissions_false(result)
