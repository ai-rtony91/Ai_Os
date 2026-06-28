from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = ROOT / "Reports" / "forex_delivery"

COMPRESSION_JSON = REPORT_DIR / "AIOS_FOREX_PROFIT_EVIDENCE_COMPRESSION_P1_P2_V1.json"
COMPRESSION_REPORT = REPORT_DIR / "AIOS_FOREX_PROFIT_EVIDENCE_COMPRESSION_P1_P2_V1_REPORT.md"
SCOREBOARD_JSON = REPORT_DIR / "AIOS_FOREX_PROFIT_CANDIDATE_SCOREBOARD_P1_P2_V1.json"
GAP_QUEUE = REPORT_DIR / "AIOS_FOREX_PROFIT_EVIDENCE_GAP_QUEUE_P1_P2_V1.md"

ALLOWED_CAMPAIGN_STATUSES = {
    "P3_READY_WITH_CANDIDATE",
    "MORE_EVIDENCE_REQUIRED",
    "NO_VALID_CANDIDATE_FOUND",
}

BANNED_TOKENS = (
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
)


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_all_output_files_exist() -> None:
    for path in (COMPRESSION_JSON, COMPRESSION_REPORT, SCOREBOARD_JSON, GAP_QUEUE):
        assert path.exists(), path


def test_compression_required_fields_and_statuses() -> None:
    payload = _read_json(COMPRESSION_JSON)

    assert payload["target_date"] == "2026-06-30"
    assert payload["boundary_status"] == "COMPLETE_FOR_BOUNDARY_CLOSURE"
    assert payload["profit_track_status"] == "READY_FOR_SUPERVISED_PAPER_DEMO_REVIEW_ONLY"
    assert payload["operational_trading_status"] == "NOT_LIVE_APPROVED"
    assert "candidate_count" in payload
    assert payload["candidate_count"] >= 0
    assert payload["campaign_status"] in ALLOWED_CAMPAIGN_STATUSES
    assert payload["forbidden_actions"]
    assert any("broker/API access" == item for item in payload["forbidden_actions"])
    assert any("live trade" == item for item in payload["forbidden_actions"])
    assert payload["final_owner_sentence"]


def test_scoreboard_candidates_have_scores() -> None:
    payload = _read_json(SCOREBOARD_JSON)
    assert payload["campaign_status"] in ALLOWED_CAMPAIGN_STATUSES
    assert payload["candidate_count"] == len(payload["candidates"])

    for candidate in payload["candidates"]:
        assert candidate["scores"]
        assert "total_score" in candidate
        assert 0 <= candidate["total_score"] <= 100


def test_no_banned_tokens_in_output_artifacts() -> None:
    for path in (COMPRESSION_JSON, COMPRESSION_REPORT, SCOREBOARD_JSON, GAP_QUEUE):
        text = path.read_text(encoding="utf-8")
        for token in BANNED_TOKENS:
            assert token not in text, f"{token!r} found in {path}"
