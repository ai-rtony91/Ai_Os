from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_closure_integration_bridge_v1 import run_forex_closure_integration_bridge  # noqa: E402
from automation.forex_engine.forex_final_readiness_checker_v1 import (  # noqa: E402
    build_sample_evidence_age_metadata,
    build_sample_validator_evidence,
    evaluate_forex_final_readiness,
)
from automation.forex_engine.forex_owner_decision_brief_v1 import (  # noqa: E402
    OWNER_DECISION_BRIEF_BLOCKED,
    OWNER_DECISION_BRIEF_INCOMPLETE,
    OWNER_DECISION_BRIEF_REVIEW_READY,
    build_forex_owner_decision_brief,
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


def ready_chain_and_readiness() -> tuple[dict, dict]:
    chain = run_forex_closure_integration_bridge()
    readiness = evaluate_forex_final_readiness(
        chain,
        build_sample_validator_evidence(),
        build_sample_evidence_age_metadata(),
    )
    return chain, readiness


def test_safe_review_path_builds_owner_brief_without_approval() -> None:
    chain, readiness = ready_chain_and_readiness()

    result = build_forex_owner_decision_brief(chain, readiness)

    assert result["status"] == OWNER_DECISION_BRIEF_REVIEW_READY
    assert result["decision_brief"]["approval_created"] is False
    assert result["decision_brief"]["execution_authority"] == "none"
    assert_permissions_false(result)


def test_missing_input_blocks_as_incomplete() -> None:
    result = build_forex_owner_decision_brief(None, None)

    assert result["status"] == OWNER_DECISION_BRIEF_INCOMPLETE
    assert result["blockers"]
    assert_permissions_false(result)


def test_conflicting_readiness_status_blocks_brief() -> None:
    chain, readiness = ready_chain_and_readiness()
    readiness["status"] = "FOREX_FINAL_READINESS_BLOCKED"

    result = build_forex_owner_decision_brief(chain, readiness)

    assert result["status"] == OWNER_DECISION_BRIEF_BLOCKED
    assert any("final readiness" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_stale_evidence_gap_blocks_brief() -> None:
    chain, readiness = ready_chain_and_readiness()
    readiness["status"] = "FOREX_FINAL_READINESS_BLOCKED"
    readiness["stale_evidence"] = ["walk_forward_proof age 20 exceeds max 7"]

    result = build_forex_owner_decision_brief(chain, readiness)

    assert result["status"] == OWNER_DECISION_BRIEF_BLOCKED
    assert result["evidence_gaps"]
    assert_permissions_false(result)


def test_unsafe_chain_flag_blocks_brief() -> None:
    chain, readiness = ready_chain_and_readiness()
    chain["live_trading_allowed"] = True

    result = build_forex_owner_decision_brief(chain, readiness)

    assert result["status"] == OWNER_DECISION_BRIEF_BLOCKED
    assert any("unsafe true" in item for item in result["blockers"])
    assert_permissions_false(result)


def test_integration_fail_closed_reaches_brief_block() -> None:
    chain, readiness = ready_chain_and_readiness()
    chain["status"] = "FOREX_CLOSURE_CHAIN_BLOCKED"
    readiness["status"] = "FOREX_FINAL_READINESS_BLOCKED"

    result = build_forex_owner_decision_brief(chain, readiness)

    assert result["status"] == OWNER_DECISION_BRIEF_BLOCKED
    assert result["owner_approval_created"] is False
    assert_permissions_false(result)
