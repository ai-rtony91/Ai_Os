from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_closure_integration_bridge_v1 import (  # noqa: E402
    FOREX_CLOSURE_CHAIN_BLOCKED,
    FOREX_CLOSURE_CHAIN_INCOMPLETE,
    FOREX_CLOSURE_CHAIN_REVIEW_READY,
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


def test_safe_review_path_runs_full_chain() -> None:
    result = run_forex_closure_integration_bridge(build_sample_integration_input())

    assert result["status"] == FOREX_CLOSURE_CHAIN_REVIEW_READY
    assert result["blockers"] == []
    assert result["stage_statuses"]["dashboard_truth"] == "DASHBOARD_TRUTH_DISPLAY_READY"
    assert_permissions_false(result)


def test_missing_input_fails_closed_as_incomplete() -> None:
    payload = build_sample_integration_input()
    payload.pop("risk_caps")

    result = run_forex_closure_integration_bridge(payload)

    assert result["status"] == FOREX_CLOSURE_CHAIN_INCOMPLETE
    assert "risk" in result["not_ready_stages"]
    assert_permissions_false(result)


def test_conflicting_broker_input_blocks_chain() -> None:
    payload = build_sample_integration_input()
    payload["broker_snapshot"]["market_open"] = False

    result = run_forex_closure_integration_bridge(payload)

    assert result["status"] == FOREX_CLOSURE_CHAIN_BLOCKED
    assert any("market" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_stale_candidate_evidence_blocks_chain() -> None:
    payload = build_sample_integration_input()
    payload["candidate"]["evidence_age_days"] = 99

    result = run_forex_closure_integration_bridge(payload)

    assert result["status"] == FOREX_CLOSURE_CHAIN_BLOCKED
    assert any("stale" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_unsafe_flag_blocks_chain() -> None:
    payload = build_sample_integration_input()
    payload["candidate"]["live_trading_allowed"] = True

    result = run_forex_closure_integration_bridge(payload)

    assert result["status"] == FOREX_CLOSURE_CHAIN_BLOCKED
    assert any("unsafe true" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_operator_halt_integration_fails_closed() -> None:
    payload = build_sample_integration_input()
    payload["operator_halt_state"]["halt_requested"] = True

    result = run_forex_closure_integration_bridge(payload)

    assert result["status"] == FOREX_CLOSURE_CHAIN_BLOCKED
    assert result["stage_statuses"]["stop"] == "STOP_REQUIRED"
    assert any("operator halt" in item for item in result["blockers"])
    assert_permissions_false(result)
