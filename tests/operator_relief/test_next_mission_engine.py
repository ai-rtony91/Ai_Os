from __future__ import annotations

import json
from pathlib import Path

from automation.operator_relief.next_mission_engine import generate_next_mission_queue
from automation.operator_relief.packet_queue import TOKEN_PLACEHOLDER, default_packet_candidates


def test_packet_queue_generates_at_least_5_and_no_more_than_10_candidates(tmp_path: Path) -> None:
    report = generate_next_mission_queue(tmp_path).to_dict()

    assert report["status"] == "PACKET_QUEUE_READY"
    assert 5 <= report["candidate_count"] <= 10
    assert Path(report["queue_path"]).is_file()


def test_packet_candidates_have_required_safety_fields() -> None:
    candidates = [candidate.to_dict() for candidate in default_packet_candidates()]

    assert len(candidates) == 10
    for candidate in candidates:
        payload = json.dumps(candidate, sort_keys=True)
        assert candidate["executable"] is False
        assert candidate["human_review_required"] is True
        assert candidate["approval_token"] == TOKEN_PLACEHOLDER
        assert "AI_OS EXECUTION TOKEN" not in payload
        assert "[ANTHONY_APPROVAL_REQUIRED]" in payload
        assert candidate["allowed_paths"]
        assert candidate["forbidden_paths"]
        assert candidate["validators"]
        assert candidate["stop_point"]
        assert candidate["copy_paste_burden_removed"]
