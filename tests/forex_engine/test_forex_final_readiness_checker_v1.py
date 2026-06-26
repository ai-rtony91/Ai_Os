from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_closure_integration_bridge_v1 import run_forex_closure_integration_bridge  # noqa: E402
from automation.forex_engine.forex_final_readiness_checker_v1 import (  # noqa: E402
    FOREX_FINAL_READINESS_BLOCKED,
    FOREX_FINAL_READINESS_INCOMPLETE,
    FOREX_FINAL_READINESS_REVIEW_READY,
    build_sample_evidence_age_metadata,
    build_sample_validator_evidence,
    evaluate_forex_final_readiness,
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


def test_safe_review_path_passes_final_readiness_review() -> None:
    result = evaluate_forex_final_readiness(
        run_forex_closure_integration_bridge(),
        build_sample_validator_evidence(),
        build_sample_evidence_age_metadata(),
    )

    assert result["status"] == FOREX_FINAL_READINESS_REVIEW_READY
    assert result["closure_blockers"] == []
    assert_permissions_false(result)


def test_missing_input_blocks_as_incomplete() -> None:
    result = evaluate_forex_final_readiness(None, None, None)

    assert result["status"] == FOREX_FINAL_READINESS_INCOMPLETE
    assert result["missing_evidence"]
    assert_permissions_false(result)


def test_missing_required_evidence_blocks() -> None:
    evidence = build_sample_validator_evidence()
    evidence["persistent_profitability_proof"] = False

    result = evaluate_forex_final_readiness(
        run_forex_closure_integration_bridge(),
        evidence,
        build_sample_evidence_age_metadata(),
    )

    assert result["status"] == FOREX_FINAL_READINESS_BLOCKED
    assert "persistent_profitability_proof" in result["missing_evidence"]
    assert_permissions_false(result)


def test_conflicting_chain_status_blocks() -> None:
    chain = run_forex_closure_integration_bridge()
    chain["status"] = "FOREX_CLOSURE_CHAIN_BLOCKED"

    result = evaluate_forex_final_readiness(
        chain,
        build_sample_validator_evidence(),
        build_sample_evidence_age_metadata(),
    )

    assert result["status"] == FOREX_FINAL_READINESS_BLOCKED
    assert any("integrated chain" in item for item in result["closure_blockers"])
    assert_permissions_false(result)


def test_stale_evidence_blocks_final_readiness() -> None:
    ages = build_sample_evidence_age_metadata()
    ages["replay_proof"] = {"age_days": 20, "max_age_days": 7}

    result = evaluate_forex_final_readiness(
        run_forex_closure_integration_bridge(),
        build_sample_validator_evidence(),
        ages,
    )

    assert result["status"] == FOREX_FINAL_READINESS_BLOCKED
    assert any("replay_proof" in item for item in result["stale_evidence"])
    assert_permissions_false(result)


def test_unsafe_validator_flag_blocks_final_readiness() -> None:
    evidence = build_sample_validator_evidence()
    evidence["live_trading_allowed"] = True

    result = evaluate_forex_final_readiness(
        run_forex_closure_integration_bridge(),
        evidence,
        build_sample_evidence_age_metadata(),
    )

    assert result["status"] == FOREX_FINAL_READINESS_BLOCKED
    assert any("unsafe true" in item for item in result["closure_blockers"])
    assert_permissions_false(result)
