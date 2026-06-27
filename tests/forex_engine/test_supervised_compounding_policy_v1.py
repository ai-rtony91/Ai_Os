from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.persistent_profitability_evidence_v1 import (  # noqa: E402
    build_sample_persistent_profitability_summary,
    evaluate_persistent_profitability_evidence,
)
from automation.forex_engine.supervised_compounding_policy_v1 import (  # noqa: E402
    SUPERVISED_COMPOUNDING_POLICY_BLOCKED,
    SUPERVISED_COMPOUNDING_POLICY_INCOMPLETE,
    SUPERVISED_COMPOUNDING_POLICY_REVIEW_READY,
    build_sample_compounding_policy_input,
    evaluate_supervised_compounding_policy,
)


PROTECTED_FLAGS = (
    "broker_execution_allowed",
    "broker_connection_allowed",
    "broker_api_call_allowed",
    "live_trading_allowed",
    "order_submission_allowed",
    "credential_access_allowed",
    "account_access_allowed",
    "money_movement_allowed",
    "all_money_control_allowed",
    "bank_movement_allowed",
    "withdrawal_allowed",
    "deposit_allowed",
    "compounding_allowed",
    "compounding_execution_allowed",
    "autonomous_compounding_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
    "dashboard_execution_authority",
    "owner_approval_created",
)


def _profitability() -> dict:
    return evaluate_persistent_profitability_evidence(
        build_sample_persistent_profitability_summary()
    )


def assert_permissions_false(result: dict) -> None:
    for flag in PROTECTED_FLAGS:
        assert result[flag] is False
        assert result["permissions"][flag] is False


def test_sample_policy_is_review_ready_only() -> None:
    result = evaluate_supervised_compounding_policy(
        _profitability(),
        build_sample_compounding_policy_input(),
    )

    assert result["status"] == SUPERVISED_COMPOUNDING_POLICY_REVIEW_READY
    assert result["compounding_review_ready"] is True
    assert result["autonomous_compounding_ready"] is False
    assert result["compounding_execution_authorized"] is False
    assert result["blockers"] == []
    assert_permissions_false(result)


def test_missing_inputs_fail_closed_as_incomplete() -> None:
    result = evaluate_supervised_compounding_policy(None, None)

    assert result["status"] == SUPERVISED_COMPOUNDING_POLICY_INCOMPLETE
    assert result["missing_fields"]
    assert_permissions_false(result)


def test_insufficient_profitability_blocks_policy() -> None:
    profitability_summary = build_sample_persistent_profitability_summary()
    profitability_summary["expectancy"] = -0.1
    persistent = evaluate_persistent_profitability_evidence(profitability_summary)

    result = evaluate_supervised_compounding_policy(
        persistent,
        build_sample_compounding_policy_input(),
    )

    assert result["status"] == SUPERVISED_COMPOUNDING_POLICY_BLOCKED
    assert any("persistent profitability" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_compounding_request_without_owner_approval_blocks_policy() -> None:
    policy = build_sample_compounding_policy_input()
    policy["compounding_requested"] = True
    policy["owner_compounding_approval_present"] = False

    result = evaluate_supervised_compounding_policy(_profitability(), policy)

    assert result["status"] == SUPERVISED_COMPOUNDING_POLICY_BLOCKED
    assert "compounding requested without owner approval" in result["blockers"]
    assert_permissions_false(result)


def test_kill_switch_gap_blocks_policy() -> None:
    policy = build_sample_compounding_policy_input()
    policy["kill_switch_ready"] = False

    result = evaluate_supervised_compounding_policy(_profitability(), policy)

    assert result["status"] == SUPERVISED_COMPOUNDING_POLICY_BLOCKED
    assert "kill_switch_ready must be true" in result["blockers"]
    assert_permissions_false(result)


def test_unsafe_true_flags_block_policy() -> None:
    policy = build_sample_compounding_policy_input()
    policy["money_movement_allowed"] = True
    policy["scheduler_allowed"] = True

    result = evaluate_supervised_compounding_policy(_profitability(), policy)

    assert result["status"] == SUPERVISED_COMPOUNDING_POLICY_BLOCKED
    assert any("money_movement_allowed is unsafe true" in item for item in result["blockers"])
    assert any("scheduler_allowed is unsafe true" in item for item in result["blockers"])
    assert_permissions_false(result)
