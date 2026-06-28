from __future__ import annotations

import json
from pathlib import Path

from automation.forex_engine.c1_walk_forward_repair_sample_expansion_v1 import (
    evaluate_c1_walk_forward_repair_sample_expansion,
)
from scripts.forex_delivery.run_c1_walk_forward_repair_sample_expansion_v1 import (
    generate_artifacts,
)


ALLOWED_REPAIR_STATUSES = {
    "REPAIRED_P3_READY",
    "PARTIAL_REPAIR_MORE_EVIDENCE_REQUIRED",
    "REPAIR_FAILED_REPLACEMENT_REVIEW_REQUIRED",
}

REQUIRED_REPAIR_TARGETS = {
    "wf-02",
    "wf-03",
    "wf-04",
    "drawdown_containment",
    "insufficient_sample",
    "mitigation_path",
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
    Path("Reports/forex_delivery/AIOS_FOREX_C1_WALK_FORWARD_REPAIR_SAMPLE_EXPANSION_V1.json"),
    Path("Reports/forex_delivery/AIOS_FOREX_C1_WALK_FORWARD_REPAIR_SAMPLE_EXPANSION_V1_REPORT.md"),
    Path("Reports/forex_delivery/AIOS_FOREX_C1_WALK_FORWARD_REPAIR_SAMPLE_EXPANSION_NEXT_ACTION_QUEUE_V1.md"),
]


def test_repair_contract() -> None:
    result = evaluate_c1_walk_forward_repair_sample_expansion()

    assert result["candidate_id"] == "c1-eur-buy"
    assert result["input_score"] == 85
    assert result["post_repair_score"] <= 100
    assert result["repair_status"] in ALLOWED_REPAIR_STATUSES
    assert result["p3_readiness"] in {"P3_READY", "NOT_READY"}

    if result["p3_readiness"] == "P3_READY":
        assert result["next_required_lane"] == "P3_WALK_FORWARD_OOS_PROOF"
    if result["p3_readiness"] == "NOT_READY":
        assert result["next_required_lane"] != "P3_WALK_FORWARD_OOS_PROOF"

    assert {"wf-02", "wf-03", "wf-04"}.issubset(set(result["failed_windows"]))
    assert REQUIRED_REPAIR_TARGETS.issubset(set(result["repair_assessments"]))
    assert result["forbidden_actions"]
    assert "broker/API access" in result["forbidden_actions"]
    assert "credentials" in result["forbidden_actions"]
    assert "live trading" in result["forbidden_actions"]
    assert result["final_owner_sentence"]


def test_p3_ready_contract_is_strict() -> None:
    result = evaluate_c1_walk_forward_repair_sample_expansion()

    if result["p3_readiness"] == "P3_READY":
        for target in REQUIRED_REPAIR_TARGETS:
            assert (
                result["repair_assessments"][target]["classification"]
                == "REPAIR_READY"
            )
        assert result["open_repairs"] == []
        assert result["repair_status"] == "REPAIRED_P3_READY"
    else:
        assert result["open_repairs"]
        assert result["repair_status"] != "REPAIRED_P3_READY"


def test_sample_expansion_target_is_concrete() -> None:
    result = evaluate_c1_walk_forward_repair_sample_expansion()
    sample = result["sample_expansion_target"]

    assert sample["minimum_windows"] == 4
    assert sample["minimum_trades_per_window"] == 5
    assert sample["minimum_total_closed_trades"] == 20
    assert set(sample["observed_closed_trades_by_window"]) >= {
        "wf-01",
        "wf-02",
        "wf-03",
        "wf-04",
    }


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
    assert generated["post_repair_score"] == result["post_repair_score"]
    assert generated["repair_status"] == result["repair_status"]
    assert generated["p3_readiness"] == result["p3_readiness"]
    assert generated["next_required_lane"] == result["next_required_lane"]
