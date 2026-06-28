from __future__ import annotations

import json
from pathlib import Path

from automation.forex_engine.c1_walk_forward_oos_proof_v1 import (
    evaluate_c1_walk_forward_oos_proof,
)
from scripts.forex_delivery.run_c1_walk_forward_oos_proof_v1 import (
    generate_artifacts,
)


ALLOWED_P3_PROOF_STATUSES = {
    "P3_PROOF_PASSED_FOR_P4_REVIEW",
    "P3_PROOF_FAILED_REPAIR_REQUIRED",
    "P3_PROOF_FAILED_REPLACEMENT_REVIEW_REQUIRED",
}

REQUIRED_PROOF_CATEGORIES = {
    "windows",
    "sample",
    "drawdown",
    "mitigation",
    "no_open_blockers",
    "no_demo_live_approval",
}

BANNED_TOKENS = [
    "TODO",
    "TBD",
    "@filename",
    "probably",
    "roughly",
    "approximately",
    "I estimate",
    "live ready",
    "profitable trading readiness: true",
    "autonomous trading readiness: true",
]

GENERATED_PATHS = [
    Path("Reports/forex_delivery/AIOS_FOREX_C1_WALK_FORWARD_OOS_PROOF_V1.json"),
    Path("Reports/forex_delivery/AIOS_FOREX_C1_WALK_FORWARD_OOS_PROOF_V1_REPORT.md"),
    Path("Reports/forex_delivery/AIOS_FOREX_C1_WALK_FORWARD_OOS_PROOF_NEXT_ACTION_QUEUE_V1.md"),
]


def test_p3_proof_contract() -> None:
    result = evaluate_c1_walk_forward_oos_proof()

    assert result["candidate_id"] == "c1-eur-buy"
    assert result["input_score"] in [85, 100]
    assert result["post_p3_score"] <= 100
    assert result["p3_proof_status"] in ALLOWED_P3_PROOF_STATUSES
    assert result["p4_readiness"] in {"P4_READY", "NOT_READY"}

    if result["p4_readiness"] == "P4_READY":
        assert result["next_required_lane"] == "P4_RISK_POSITION_SIZING_REVIEW"
    if result["p4_readiness"] == "NOT_READY":
        assert result["next_required_lane"] != "P4_RISK_POSITION_SIZING_REVIEW"

    assert REQUIRED_PROOF_CATEGORIES.issubset(set(result["proof_requirements"]))
    assert REQUIRED_PROOF_CATEGORIES.issubset(set(result["proof_assessments"]))
    assert result["forbidden_actions"]
    assert "broker/API access" in result["forbidden_actions"]
    assert "credentials" in result["forbidden_actions"]
    assert "live trading" in result["forbidden_actions"]
    assert result["final_owner_sentence"]


def test_p4_ready_contract_is_strict() -> None:
    result = evaluate_c1_walk_forward_oos_proof()

    if result["p4_readiness"] == "P4_READY":
        assert result["failed_requirements"] == []
        assert set(result["passed_requirements"]) == REQUIRED_PROOF_CATEGORIES
        assert result["p3_proof_status"] == "P3_PROOF_PASSED_FOR_P4_REVIEW"
        assert result["post_p3_status"] == "P4_READY"
    else:
        assert result["failed_requirements"]
        assert result["p3_proof_status"] != "P3_PROOF_PASSED_FOR_P4_REVIEW"


def test_proof_summaries_are_concrete() -> None:
    result = evaluate_c1_walk_forward_oos_proof()

    sample = result["sample_proof_summary"]
    assert sample["minimum_windows"] == 4
    assert sample["minimum_trades_per_window"] == 5
    assert sample["minimum_total_closed_trades"] == 20
    assert sample["observed_total_closed_trades"] >= 20
    assert set(sample["observed_closed_trades_by_window"]) >= {
        "wf-01",
        "wf-02",
        "wf-03",
        "wf-04",
    }

    window_summary = result["window_proof_summary"]
    assert {"wf-02", "wf-03", "wf-04"}.issubset(
        set(window_summary["repaired_failed_windows"])
    )
    assert result["drawdown_proof_summary"]["maximum_optimized_drawdown"] <= 10.0
    assert result["mitigation_proof_summary"]["remaining_blockers"] == []


def test_generated_artifacts_are_present_and_clean() -> None:
    generate_artifacts()

    for path in GENERATED_PATHS:
        assert path.exists(), f"Missing generated artifact: {path}"
        text = path.read_text(encoding="utf-8")
        for token in BANNED_TOKENS:
            assert token not in text


def test_generated_json_matches_evaluator() -> None:
    result = generate_artifacts()
    generated = json.loads(GENERATED_PATHS[0].read_text(encoding="utf-8"))

    assert generated["campaign_id"] == result["campaign_id"]
    assert generated["candidate_id"] == result["candidate_id"]
    assert generated["input_score"] == result["input_score"]
    assert generated["post_p3_score"] == result["post_p3_score"]
    assert generated["p3_proof_status"] == result["p3_proof_status"]
    assert generated["p4_readiness"] == result["p4_readiness"]
    assert generated["next_required_lane"] == result["next_required_lane"]
