from __future__ import annotations

import json
from pathlib import Path

from automation.forex_engine.c1_eur_buy_evidence_gap_closure_v1 import (
    evaluate_c1_eur_buy_gap_closure,
)


ALLOWED_GAP_CLOSURE_STATUSES = {
    "COMPLETE_P3_READY",
    "PARTIAL_CLOSURE_NEXT_REPAIR_REQUIRED",
    "NO_CLOSURE_SOURCE_CONFLICTS_REMAIN",
}

ALLOWED_POST_CLOSURE_STATUSES = {
    "P3_READY",
    "NEEDS_MORE_EVIDENCE",
    "REJECTED_NEGATIVE_EXPECTANCY",
    "REJECTED_LOW_PROFIT_FACTOR",
    "REJECTED_INSUFFICIENT_SAMPLE",
    "REJECTED_EXCESSIVE_DRAWDOWN",
}

KNOWN_GAP_TARGETS = {
    "readiness_conflict",
    "wf_02_failed_window",
    "wf_03_failed_window",
    "wf_04_failed_window",
    "drawdown_containment",
    "insufficient_sample",
    "mitigation_path",
    "p3_readiness",
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
    Path("Reports/forex_delivery/AIOS_FOREX_C1_EUR_BUY_EVIDENCE_GAP_CLOSURE_V1.json"),
    Path("Reports/forex_delivery/AIOS_FOREX_C1_EUR_BUY_EVIDENCE_GAP_CLOSURE_V1_REPORT.md"),
    Path("Reports/forex_delivery/AIOS_FOREX_C1_EUR_BUY_EVIDENCE_GAP_CLOSURE_NEXT_ACTION_QUEUE_V1.md"),
]


def test_evaluate_c1_eur_buy_gap_closure_contract() -> None:
    result = evaluate_c1_eur_buy_gap_closure()

    assert result["candidate_id"] == "c1-eur-buy"
    assert result["input_score"] == 85
    assert result["post_closure_score"] <= 100
    assert result["gap_closure_status"] in ALLOWED_GAP_CLOSURE_STATUSES
    assert result["p3_readiness"] in {"P3_READY", "NOT_READY"}
    assert result["post_closure_status"] in ALLOWED_POST_CLOSURE_STATUSES

    if result["p3_readiness"] == "NOT_READY":
        assert result["next_required_lane"] != "P3_WALK_FORWARD_OOS_PROOF"

    assert KNOWN_GAP_TARGETS.issubset(set(result["gap_assessments"]))
    assert "broker/API access" in result["forbidden_actions"]
    assert "credentials" in result["forbidden_actions"]
    assert "live trading" in result["forbidden_actions"]
    assert "money movement" in result["forbidden_actions"]
    assert "autonomous trading" in result["forbidden_actions"]
    assert result["final_owner_sentence"]


def test_generated_artifacts_are_present_and_clean() -> None:
    for path in GENERATED_PATHS:
        assert path.exists(), f"Missing generated artifact: {path}"
        text = path.read_text(encoding="utf-8")
        for token in BANNED_TOKENS:
            assert token not in text


def test_generated_json_matches_evaluator() -> None:
    generated = json.loads(GENERATED_PATHS[0].read_text(encoding="utf-8"))
    evaluated = evaluate_c1_eur_buy_gap_closure()

    assert generated["candidate_id"] == evaluated["candidate_id"]
    assert generated["input_score"] == evaluated["input_score"]
    assert generated["post_closure_score"] == evaluated["post_closure_score"]
    assert generated["gap_closure_status"] == evaluated["gap_closure_status"]
    assert generated["p3_readiness"] == evaluated["p3_readiness"]
    assert generated["next_required_lane"] == evaluated["next_required_lane"]
