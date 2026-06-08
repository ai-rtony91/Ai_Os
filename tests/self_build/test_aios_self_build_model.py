from __future__ import annotations

from automation.bridge.aios_self_build_model import build_recommendations


def test_self_build_recommendations_do_not_execute():
    recommendations = build_recommendations("2026-06-08T00:00:00Z", {})
    assert recommendations
    assert all("execute automatically" not in item.safe_next_prompt.lower() for item in recommendations)
    assert any(item.risk_tier == "PRODUCTION_OR_LIVE_BLOCKED" for item in recommendations)


def test_missing_expected_files_adds_wait_recommendation():
    recommendations = build_recommendations(
        "2026-06-08T00:00:00Z",
        {"missing_expected_files": ["docs/workflows/example.md"]},
    )
    assert any(item.status == "WAIT" for item in recommendations)

