"""Tests for paper-only completion sweep and DRY_RUN behavior."""

from __future__ import annotations

from pathlib import Path

from automation.trading.runner.paper_replay_runner import run_paper_replay
from automation.trading.safety.paper_only_validator import validate_paper_payload
from automation.trading.runner.paper_replay_runner import build_replay_result


def test_fixture_replay_is_paper_only_and_not_live():
    fixture = Path("automation/trading/fixtures/paper_signal_fixture.json")
    result = run_paper_replay(fixture_path=fixture, dry_run=True)

    assert result["paper_only"] is True
    assert result["mode"] == "paper_only"
    assert result["execution_quality"]["execution_quality_score"] >= 0
    assert all(item["paper_only"] for item in result["ledger"])
    assert all(item["live_execution_status"] == "BLOCKED" for item in result["ledger"])
    assert all(item["execution_allowed"] is False for item in result["ledger"])


def test_replay_route_preview_matches_payload():
    fixture = Path("automation/trading/fixtures/paper_signal_fixture.json")
    result = run_paper_replay(fixture_path=fixture, dry_run=True)
    first = result["previews"][0]

    assert first["action"] == "PAPER_BUY_PREVIEW"
    assert first["route_status"] == "PAPER_PREVIEW_ONLY"


def test_regime_filter_blocker_blocks_mismatch(tmp_path):
    fixture = tmp_path / "paper_signal_fixture.json"
    fixture.write_text(
        """
{
  "signal_id": "AIOS_PAPER_SIGNAL_2026_06_09_002",
  "symbol": "EURUSD",
  "timeframe": "1h",
  "source": "TradingViewMock",
  "permission": "bullish",
  "signal": "BUY",
  "confidence": 0.88,
  "generated_at": "2026-06-09T10:00:00Z",
  "received_at": "2026-06-09T10:00:00Z",
  "regime": "trend_down",
  "trend_score": 0.82,
  "metadata": {"fill_price": 1.0950},
  "notes": "paper-only dry-run fixture"
}
""".strip(),
        encoding="utf-8",
    )
    result = run_paper_replay(fixture_path=fixture, dry_run=True)

    assert result["ledger"][0]["paper_decision"] == "BLOCKED"
    assert result["ledger"][0]["blocked_reason"] == "regime_filter_blocked"


def test_validator_catches_forbidden_tokens():
    payload = {
        "paper_only": True,
        "live_execution_status": "BLOCKED",
        "execution_allowed": False,
        "metadata": {"api_key": "should_not_exist"},
    }
    assert "forbidden routing tokens detected in payload" in validate_paper_payload(payload)


def test_build_replay_result_maps_ledger_to_model():
    fixture = Path("automation/trading/fixtures/paper_signal_fixture.json")
    result = run_paper_replay(fixture_path=fixture, dry_run=True)
    mapped = build_replay_result(result)

    assert mapped[0].paper_only is True
    assert mapped[0].execution_allowed is False
    assert mapped[0].route_action == "PAPER_BUY_PREVIEW"
