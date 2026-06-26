from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.candidate_scoring_v1 import (  # noqa: E402
    BLOCKED_BY_DEMO_READINESS,
    BLOCKED_BY_EVIDENCE,
    BLOCKED_BY_RISK,
    REJECT,
    REQUIRE_MORE_EVIDENCE,
    REVIEW_READY,
    SCORE_DIMENSIONS,
    candidate_score_to_jsonable_dict,
    score_candidates,
)


def candidate(candidate_id: str, **overrides: object) -> dict[str, object]:
    base: dict[str, object] = {
        "candidate_id": candidate_id,
        "expectancy": 0.45,
        "profit_factor": 1.85,
        "max_drawdown": 0.03,
        "sample_size": 60,
        "evidence_age_days": 3,
        "regime_alignment_score": 88,
        "risk_quality_score": 92,
        "evidence_quality_score": 90,
        "demo_readiness_score": 86,
        "operator_confidence_score": 80,
        "evidence_present": True,
        "required_evidence_complete": True,
        "demo_readiness": True,
    }
    base.update(overrides)
    return base


def test_highest_quality_candidate_ranks_first() -> None:
    results = score_candidates(
        [
            candidate("weaker", expectancy=0.22, profit_factor=1.30, operator_confidence_score=40),
            candidate("stronger", expectancy=0.55, profit_factor=2.10, operator_confidence_score=95),
        ]
    )

    assert results[0].candidate_id == "stronger"
    assert results[0].rank == 1
    assert results[0].decision == REVIEW_READY


def test_missing_evidence_blocks_candidate() -> None:
    result = score_candidates(
        [
            candidate(
                "missing-evidence",
                evidence_quality_score=None,
                evidence_present=False,
                required_evidence_complete=False,
            )
        ]
    )[0]

    assert result.decision == BLOCKED_BY_EVIDENCE
    assert any("evidence" in blocker for blocker in result.blockers)


def test_negative_expectancy_rejects_candidate() -> None:
    result = score_candidates([candidate("negative", expectancy=-0.01)])[0]

    assert result.decision == REJECT
    assert "negative expectancy" in result.blockers


def test_excessive_drawdown_blocks_by_risk() -> None:
    result = score_candidates([candidate("risk", max_drawdown=0.30)])[0]

    assert result.decision == BLOCKED_BY_RISK
    assert "excessive drawdown" in result.blockers


def test_insufficient_sample_requires_more_evidence() -> None:
    result = score_candidates([candidate("small-sample", sample_size=12)])[0]

    assert result.decision == REQUIRE_MORE_EVIDENCE
    assert any("sample_size" in reason for reason in result.decision_reasons)


def test_stale_evidence_reduces_score_before_block_threshold() -> None:
    fresh = score_candidates([candidate("fresh", evidence_age_days=3)])[0]
    stale = score_candidates([candidate("stale", evidence_age_days=20)])[0]

    assert stale.decision == REVIEW_READY
    assert stale.normalized_score < fresh.normalized_score
    assert stale.score_breakdown["recency_score"] < fresh.score_breakdown["recency_score"]


def test_stale_evidence_blocks_candidate_at_threshold() -> None:
    result = score_candidates([candidate("expired", evidence_age_days=30)])[0]

    assert result.decision == BLOCKED_BY_EVIDENCE
    assert any("stale" in reason for reason in result.decision_reasons)


def test_demo_readiness_missing_blocks_candidate() -> None:
    result = score_candidates(
        [
            candidate(
                "missing-demo",
                demo_readiness_score=None,
                demo_readiness=None,
            )
        ]
    )[0]

    assert result.decision == BLOCKED_BY_DEMO_READINESS
    assert any("demo readiness" in blocker for blocker in result.blockers)


def test_tie_breaking_is_deterministic() -> None:
    results = score_candidates([candidate("b-candidate"), candidate("a-candidate")])

    assert results[0].normalized_score == results[1].normalized_score
    assert [result.candidate_id for result in results] == ["a-candidate", "b-candidate"]
    assert [result.rank for result in results] == [1, 2]


def test_score_normalization_remains_within_zero_to_100() -> None:
    results = score_candidates(
        [
            candidate(
                "oversized",
                expectancy_score=500,
                profit_factor_score=500,
                drawdown_score=500,
                sample_size_score=500,
                recency_score=500,
                regime_alignment_score=500,
                risk_quality_score=500,
                evidence_quality_score=500,
                demo_readiness_score=500,
                operator_confidence_score=500,
            ),
            candidate("weak", expectancy_score=-10, profit_factor_score=-5),
        ]
    )

    for result in results:
        assert 0 <= result.normalized_score <= 100
        assert 0 <= result.total_score <= 100
        for score in result.score_breakdown.values():
            assert 0 <= score <= 100


def test_all_decisions_produce_decision_reasons() -> None:
    results = [
        score_candidates([candidate("ready")])[0],
        score_candidates([candidate("more", sample_size=2)])[0],
        score_candidates([candidate("reject", expectancy=-0.5)])[0],
        score_candidates([candidate("risk", max_drawdown=0.5)])[0],
        score_candidates([candidate("evidence", evidence_present=False)])[0],
        score_candidates([candidate("demo", demo_readiness_score=None, demo_readiness=None)])[0],
    ]

    assert {result.decision for result in results} == {
        REVIEW_READY,
        REQUIRE_MORE_EVIDENCE,
        REJECT,
        BLOCKED_BY_RISK,
        BLOCKED_BY_EVIDENCE,
        BLOCKED_BY_DEMO_READINESS,
    }
    assert all(result.decision_reasons for result in results)


def test_result_contains_required_engine_fields_and_dimensions() -> None:
    result = score_candidates([candidate("ready")])[0]
    payload = candidate_score_to_jsonable_dict(result)

    for key in (
        "candidate_id",
        "total_score",
        "normalized_score",
        "rank",
        "decision",
        "decision_reasons",
        "blockers",
        "score_breakdown",
        "recommended_next_action",
    ):
        assert key in payload
    assert tuple(payload["score_breakdown"]) == SCORE_DIMENSIONS
    assert payload["safety"]["broker_called"] is False
    assert payload["safety"]["orders_placed"] is False
