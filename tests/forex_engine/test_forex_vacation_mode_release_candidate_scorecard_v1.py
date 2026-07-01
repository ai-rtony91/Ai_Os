from automation.forex_engine.forex_vacation_mode_release_candidate_scorecard_v1 import (
    SCORECARD_BLOCKED_BY_EXTERNAL_EVIDENCE,
    SCORECARD_BLOCKED_BY_FINAL_RELEASE_CANDIDATE_READINESS,
    SCORECARD_BLOCKED_BY_LEGAL_COMPLIANCE,
    SCORECARD_BLOCKED_BY_MOBILE_PACKAGING,
    SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW,
    SCORE_AREAS,
    INCOMPLETE_INPUTS,
    evaluate_forex_vacation_mode_release_candidate_scorecard_v1,
)


def _scorecard_payload(**blocked):
    payload = {area: {"ready": True, "status": "READY"} for area in SCORE_AREAS}
    for area in blocked:
        payload[area] = {"ready": False, "status": "BLOCKED"}
    return payload


def test_incomplete_input_blocks():
    result = evaluate_forex_vacation_mode_release_candidate_scorecard_v1()

    assert result["status"] == INCOMPLETE_INPUTS


def test_ready_when_all_score_areas_ready():
    result = evaluate_forex_vacation_mode_release_candidate_scorecard_v1(
        _scorecard_payload()
    )

    assert result["status"] == SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW


def test_blocks_final_readiness_when_legal_compliance_missing():
    result = evaluate_forex_vacation_mode_release_candidate_scorecard_v1(
        _scorecard_payload(legal_compliance_review_readiness=True)
    )

    assert result["status"] == SCORECARD_BLOCKED_BY_LEGAL_COMPLIANCE
    assert result["final_release_candidate_ready"] is False


def test_blocks_final_readiness_when_broker_evidence_missing():
    result = evaluate_forex_vacation_mode_release_candidate_scorecard_v1(
        _scorecard_payload(broker_receipt_readiness=True)
    )

    assert result["status"] == SCORECARD_BLOCKED_BY_EXTERNAL_EVIDENCE
    assert result["final_release_candidate_ready"] is False


def test_blocks_final_readiness_when_mobile_packaging_missing():
    result = evaluate_forex_vacation_mode_release_candidate_scorecard_v1(
        _scorecard_payload(release_packaging_readiness=True)
    )

    assert result["status"] == SCORECARD_BLOCKED_BY_MOBILE_PACKAGING
    assert result["final_release_candidate_ready"] is False


def test_blocks_when_only_final_release_candidate_readiness_is_false():
    result = evaluate_forex_vacation_mode_release_candidate_scorecard_v1(
        _scorecard_payload(final_release_candidate_readiness=True)
    )

    assert result["status"] == SCORECARD_BLOCKED_BY_FINAL_RELEASE_CANDIDATE_READINESS
    assert result["status"] != SCORECARD_READY_FOR_CONTROL_PLANE_REVIEW
    assert result["ready"] is False
    assert result["final_release_candidate_ready"] is False
    assert "final_release_candidate_readiness" in result["blockers"]
