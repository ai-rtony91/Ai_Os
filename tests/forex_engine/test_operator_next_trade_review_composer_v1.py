from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.operator_next_trade_review_composer_v1 import (  # noqa: E402
    BLOCK_REVIEW_INVALID_EVIDENCE,
    BLOCK_REVIEW_LATENCY_UNKNOWN,
    BLOCK_REVIEW_MISSING_PROOF,
    BLOCK_REVIEW_RISK_OR_SAFETY_NOT_CLEAR,
    REVIEW_READY_FOR_OWNER_APPROVAL,
    compose_operator_next_trade_review,
)


def conservative_safety() -> dict:
    return {
        "local_only": True,
        "broker_calls_allowed": False,
        "credential_access_allowed": False,
        "order_placement_allowed": False,
        "order_close_allowed": False,
        "live_endpoint_allowed": False,
        "repo_mutation_outside_allowed_files": False,
        "uses_network": False,
    }


def passing_loss_result() -> dict:
    return {
        "allowed": True,
        "decision": "REVIEW_READY_FOR_OWNER_APPROVAL",
        "blocked_reasons": [],
        "missing_metrics": {},
        "safety": conservative_safety(),
    }


def passing_latency_result() -> dict:
    return {
        "allowed": True,
        "decision": "LATENCY_READY_FOR_REVIEW",
        "blocked_reasons": [],
        "missing_timestamps": [],
        "invalid_timestamps": [],
        "slow_segments": [],
        "safety": conservative_safety(),
    }


def operator_context() -> dict:
    return {
        "operator_name": "Anthony",
        "instrument": "EUR_USD",
        "direction": "LONG",
        "strategy_name": "paper_edge_candidate",
        "candidate_id": "c1-eur-buy",
        "last_trade_id": 334,
        "last_trade_result": "FILLED_TRADE_PL_NEGATIVE",
        "wants_next_demo_review": True,
    }


def passing_evidence() -> dict:
    return {
        "loss_review_metrics_gate": passing_loss_result(),
        "trade_latency_baseline": passing_latency_result(),
        "operator_context": operator_context(),
    }


def test_missing_evidence_blocks() -> None:
    result = compose_operator_next_trade_review()

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_REVIEW_INVALID_EVIDENCE


def test_missing_operator_context_blocks() -> None:
    evidence = passing_evidence()
    del evidence["operator_context"]

    result = compose_operator_next_trade_review(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_REVIEW_MISSING_PROOF
    assert "operator_context" in result["missing_for_review"]


def test_incomplete_operator_context_blocks() -> None:
    evidence = passing_evidence()
    del evidence["operator_context"]["candidate_id"]

    result = compose_operator_next_trade_review(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_REVIEW_INVALID_EVIDENCE
    assert "candidate_id" in result["missing_for_review"]


def test_wants_next_demo_review_false_blocks() -> None:
    evidence = passing_evidence()
    evidence["operator_context"]["wants_next_demo_review"] = False

    result = compose_operator_next_trade_review(evidence)

    assert result["allowed"] is False
    assert result["operator_answer"] == "Blocked: no next demo review was requested."


def test_loss_gate_blocked_causes_review_block() -> None:
    evidence = passing_evidence()
    evidence["loss_review_metrics_gate"] = {
        "allowed": False,
        "decision": "BLOCK_NEXT_DEMO_ORDER_MISSING_METRICS",
        "blocked_reasons": ["required loss-review metrics are missing"],
        "missing_metrics": {"entry_metrics": ["bid"]},
        "safety": conservative_safety(),
    }

    result = compose_operator_next_trade_review(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_REVIEW_MISSING_PROOF
    assert "entry_metrics.bid" in result["missing_for_review"]


def test_latency_baseline_blocked_causes_review_block() -> None:
    evidence = passing_evidence()
    evidence["trade_latency_baseline"] = {
        "allowed": False,
        "decision": "BLOCK_LATENCY_MISSING_TIMESTAMPS",
        "blocked_reasons": ["timestamps missing"],
        "missing_timestamps": ["quote_received_utc"],
        "safety": conservative_safety(),
    }

    result = compose_operator_next_trade_review(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_REVIEW_LATENCY_UNKNOWN
    assert result["operator_answer"] == (
        "Blocked: timing is not clear enough for you to review this trade."
    )


def test_unsafe_nested_safety_blocks_review() -> None:
    evidence = passing_evidence()
    unsafe_loss = passing_loss_result()
    unsafe_loss["safety"] = {**conservative_safety(), "order_placement_allowed": True}
    evidence["loss_review_metrics_gate"] = unsafe_loss

    result = compose_operator_next_trade_review(evidence)

    assert result["allowed"] is False
    assert result["decision"] == BLOCK_REVIEW_RISK_OR_SAFETY_NOT_CLEAR
    assert result["risk_or_safety_clear"] is False


def test_complete_passing_nested_results_returns_review_ready() -> None:
    result = compose_operator_next_trade_review(passing_evidence())

    assert result["allowed"] is True
    assert result["decision"] == REVIEW_READY_FOR_OWNER_APPROVAL
    assert result["trade_evidence_clear"] is True
    assert result["timing_clear"] is True


def test_review_ready_still_has_broker_action_allowed_false() -> None:
    result = compose_operator_next_trade_review(passing_evidence())

    assert result["broker_action_allowed"] is False


def test_review_ready_still_has_owner_approval_required_true() -> None:
    result = compose_operator_next_trade_review(passing_evidence())

    assert result["owner_approval_still_required"] is True
    assert result["safety"]["owner_approval_required"] is True


def test_operator_answer_is_short_and_front_end_useful() -> None:
    result = compose_operator_next_trade_review(passing_evidence())

    assert result["operator_answer"].startswith("Review-ready:")
    assert "no broker action is authorized" in result["operator_answer"]
    assert len(result["operator_answer"]) < 140


def test_operator_benefit_references_anthony_operator_usefulness() -> None:
    result = compose_operator_next_trade_review(passing_evidence())
    benefit = result["operator_benefit"].lower()

    assert "anthony" in benefit
    assert "operator" in benefit
    assert "one plain review/not-review answer" in benefit
    assert "broker action blocked" in benefit


def test_function_never_raises_for_malformed_input() -> None:
    malformed_inputs = [
        ["not", "a", "mapping"],
        {"operator_context": object()},
        {
            "loss_review_metrics_gate": object(),
            "trade_latency_baseline": object(),
            "operator_context": {"wants_next_demo_review": object()},
        },
    ]

    for value in malformed_inputs:
        result = compose_operator_next_trade_review(value)  # type: ignore[arg-type]
        assert result["allowed"] is False
        assert result["decision"] in {
            BLOCK_REVIEW_INVALID_EVIDENCE,
            BLOCK_REVIEW_MISSING_PROOF,
        }


def test_safety_flags_remain_conservative() -> None:
    result = compose_operator_next_trade_review(passing_evidence())
    safety = result["safety"]

    assert safety["local_only"] is True
    assert safety["broker_calls_allowed"] is False
    assert safety["credential_access_allowed"] is False
    assert safety["order_placement_allowed"] is False
    assert safety["order_close_allowed"] is False
    assert safety["live_endpoint_allowed"] is False
    assert safety["owner_approval_required"] is True
    assert safety["uses_network"] is False
