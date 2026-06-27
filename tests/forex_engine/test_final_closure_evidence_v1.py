from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.final_closure_evidence_v1 import (  # noqa: E402
    FINAL_CLOSURE_BLOCKED,
    FINAL_CLOSURE_INCOMPLETE,
    FINAL_CLOSURE_REVIEW_READY,
    build_sample_final_closure_inputs,
    evaluate_final_closure_evidence,
    result_to_jsonable_dict,
    result_to_operator_text,
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


def test_safe_ready_path_accepts_complete_final_closure_inputs() -> None:
    result = evaluate_final_closure_evidence(build_sample_final_closure_inputs())

    assert result["final_closure_status"] == FINAL_CLOSURE_REVIEW_READY
    assert result["owner_review_required"] is True
    assert result["trading_approval_created"] is False
    assert result["blockers"] == []
    assert_permissions_false(result)


def test_missing_input_is_incomplete() -> None:
    result = evaluate_final_closure_evidence(None)

    assert result["final_closure_status"] == FINAL_CLOSURE_INCOMPLETE
    assert result["missing_evidence"]
    assert_permissions_false(result)


def test_stale_evidence_blocks() -> None:
    inputs = build_sample_final_closure_inputs()
    inputs["replay_evidence"]["evidence_age_days"] = 99

    result = evaluate_final_closure_evidence(inputs)

    assert result["final_closure_status"] == FINAL_CLOSURE_BLOCKED
    assert result["stale_evidence"]
    assert_permissions_false(result)


def test_unsafe_true_permission_blocks() -> None:
    inputs = build_sample_final_closure_inputs()
    inputs["owner_brief_evidence"]["live_trading_allowed"] = True

    result = evaluate_final_closure_evidence(inputs)

    assert result["final_closure_status"] == FINAL_CLOSURE_BLOCKED
    assert any("unsafe true" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_secret_like_or_account_like_field_blocks() -> None:
    inputs = build_sample_final_closure_inputs()
    inputs["final_readiness_evidence"]["account_reference"] = "not-allowed"

    result = evaluate_final_closure_evidence(inputs)

    assert result["final_closure_status"] == FINAL_CLOSURE_BLOCKED
    assert any("secret-like or account-like" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_labeled_secret_like_text_blocks() -> None:
    inputs = build_sample_final_closure_inputs()
    inputs["final_readiness_evidence"]["operator_note"] = "account_id: not-allowed"

    result = evaluate_final_closure_evidence(inputs)

    assert result["final_closure_status"] == FINAL_CLOSURE_BLOCKED
    assert any("secret-like or account-like" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_metadata_paths_and_validator_names_do_not_create_secret_false_positive() -> None:
    inputs = build_sample_final_closure_inputs()
    inputs["final_readiness_evidence"]["source_files"] = [
        "Reports/forex_delivery/AIOS_FOREX_BROKER_DEMO_CREDENTIAL_BOUNDARY_V1_REPORT.md",
        "Reports/forex_delivery/AIOS_FOREX_BROKER_DEMO_ACCOUNT_BOUNDARY_V1_REPORT.md",
    ]
    inputs["final_readiness_evidence"]["auxiliary_evidence"] = {
        "validator_evidence": {
            "source_files": [
                "Reports/forex_delivery/AIOS_FOREX_BROKER_DEMO_CREDENTIAL_BOUNDARY_V1_REPORT.md",
            ],
            "validators": [
                {"name": "tests/forex_engine/test_credential_boundary_runtime_contract_h_v1.py: PASS"},
            ],
        }
    }

    result = evaluate_final_closure_evidence(inputs)

    assert result["final_closure_status"] == FINAL_CLOSURE_REVIEW_READY
    assert result["blockers"] == []
    assert_permissions_false(result)


def test_unsanitized_input_blocks() -> None:
    inputs = build_sample_final_closure_inputs()
    inputs["persistent_profitability_evidence"]["sanitized"] = False

    result = evaluate_final_closure_evidence(inputs)

    assert result["final_closure_status"] == FINAL_CLOSURE_BLOCKED
    assert any("sanitized" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_blocked_upstream_status_blocks_final_closure() -> None:
    inputs = build_sample_final_closure_inputs()
    inputs["walk_forward_oos_evidence"]["status"] = "WALK_FORWARD_OOS_BLOCKED"
    inputs["walk_forward_oos_evidence"]["blockers"] = ["drawdown exceeds allowed threshold"]

    result = evaluate_final_closure_evidence(inputs)

    assert result["final_closure_status"] == FINAL_CLOSURE_BLOCKED
    assert any("not ready" in blocker for blocker in result["blockers"])
    assert_permissions_false(result)


def test_operator_text_and_json_conversion() -> None:
    result = evaluate_final_closure_evidence(build_sample_final_closure_inputs())

    assert result_to_jsonable_dict(result)["final_closure_status"] == FINAL_CLOSURE_REVIEW_READY
    assert "no trading approval" in result_to_operator_text(result)
