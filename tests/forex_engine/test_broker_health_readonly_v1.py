from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.broker_health_readonly_v1 import (  # noqa: E402
    BROKER_HEALTH_BLOCKED,
    BROKER_HEALTH_INCOMPLETE,
    BROKER_HEALTH_REVIEW_READY,
    build_sample_snapshot,
    evaluate_broker_health_readonly,
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


def test_safe_review_path_accepts_sanitized_readonly_snapshot() -> None:
    result = evaluate_broker_health_readonly(build_sample_snapshot())

    assert result["status"] == BROKER_HEALTH_REVIEW_READY
    assert result["broker_health"] == "HEALTHY"
    assert result["blockers"] == []
    assert_permissions_false(result)


def test_missing_snapshot_blocks_as_incomplete() -> None:
    result = evaluate_broker_health_readonly(None)

    assert result["status"] == BROKER_HEALTH_INCOMPLETE
    assert result["blockers"]
    assert_permissions_false(result)


def test_conflicting_market_and_spread_input_blocks() -> None:
    snapshot = build_sample_snapshot()
    snapshot["market_open"] = False
    snapshot["spread_pips"] = 4.0

    result = evaluate_broker_health_readonly(snapshot)

    assert result["status"] == BROKER_HEALTH_BLOCKED
    assert result["market_blockers"]
    assert result["spread_blockers"]
    assert_permissions_false(result)


def test_stale_snapshot_blocks() -> None:
    snapshot = build_sample_snapshot()
    snapshot["snapshot_age_minutes"] = 99

    result = evaluate_broker_health_readonly(snapshot)

    assert result["status"] == BROKER_HEALTH_BLOCKED
    assert any("stale" in item for item in result["stale_data_blockers"])
    assert_permissions_false(result)


def test_unsafe_flag_and_raw_payload_block() -> None:
    snapshot = build_sample_snapshot()
    snapshot["broker_execution_allowed"] = True
    snapshot["raw_payload_present"] = True

    result = evaluate_broker_health_readonly(snapshot)

    assert result["status"] == BROKER_HEALTH_BLOCKED
    assert any("unsafe true" in item for item in result["blockers"])
    assert any("raw_payload" in item for item in result["blockers"])
    assert_permissions_false(result)
