from __future__ import annotations

import io
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from automation.forex_engine.forex_p1_supervised_paper_campaign_v1 import (
    CampaignHalt, CampaignPaths, CampaignWait, LONG_RUN_LIMITS, MAX_OPEN_PAPER_POSITIONS,
    SAFETY_FLAGS, TARGET_QUALIFYING_TRADES, run_campaign,
)

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def paths(tmp_path: Path) -> CampaignPaths:
    return CampaignPaths(*(tmp_path / name for name in (
        "candidate.json", "ledger.json", "replay-state.json", "replay.md",
        "events.jsonl", "campaign-state.json", "campaign.md",
    )))


def trade(number: int, pnl: float = 10.0) -> dict:
    opened = datetime(2026, 8, 10, 10, tzinfo=timezone.utc) + timedelta(minutes=number * 2)
    closed = opened + timedelta(minutes=1)
    direction = "buy"
    return {
        "trade_id": f"campaign-{number:03d}", "evidence_type": "paper",
        "strategy_id": "strategy-c1", "instrument": "EUR_USD", "direction": direction,
        "entry_timestamp_utc": opened.isoformat(), "exit_timestamp_utc": closed.isoformat(),
        "entry_price": 1.1, "exit_price": 1.101 if pnl >= 0 else 1.099,
        "stop_price": 1.099, "target_price": 1.101, "quantity_or_units": 100,
        "realized_pl": pnl, "fees": 0, "risk_amount": 10,
        "exit_reason": "paper_target" if pnl >= 0 else "paper_stop",
        "entry_rationale": "fresh supervised paper strategy signal",
        "evidence_source": "long_run_paper_supervisor", "reviewed_by": "human_owner",
        "review_timestamp_utc": closed.isoformat(),
    }


def run(records, paths, **kwargs):
    output = io.StringIO()
    result = run_campaign(records, paths, repository_root=ROOT, output=output, **kwargs)
    return result, output.getvalue()


def test_campaign_reuses_long_run_limit_and_is_one_at_a_time(paths):
    assert TARGET_QUALIFYING_TRADES == LONG_RUN_LIMITS["max_session_trades"] == 30
    assert MAX_OPEN_PAPER_POSITIONS == 1
    observed = []
    def candidates():
        for number in range(1, 3):
            if paths.campaign_state.exists():
                observed.append(json.loads(paths.campaign_state.read_text())["active_position"])
            yield trade(number)
    state, _ = run(candidates(), paths)
    assert state["accepted_qualifying_trades"] == 2
    assert state["active_position"] is None
    assert all(item is None for item in observed)


def test_stops_at_30_and_never_consumes_31st(paths):
    consumed = []
    def candidates():
        for number in range(1, 32):
            consumed.append(number)
            yield trade(number)
    state, output = run(candidates(), paths)
    assert state["stop_reason"] == "TARGET_REACHED"
    assert state["accepted_qualifying_trades"] == 30
    assert consumed == list(range(1, 31))
    assert "TRADE: 30/30" in output
    assert state["p1_status"] == "READY_FOR_P2_REVIEW"


def test_no_signal_preserves_count(paths):
    state, _ = run([], paths)
    assert state["stop_reason"] == "WAITING_FOR_VALID_SIGNAL"
    assert state["accepted_qualifying_trades"] == 0


def test_no_signal_cycle_waits_without_evidence_or_count(paths):
    state, output = run([CampaignWait(1, 288), CampaignWait(2, 288)], paths)
    assert state["accepted_qualifying_trades"] == 0
    assert not paths.ledger.exists()
    assert output.count("ACTION: WAIT_FOR_NEXT_CYCLE") == 2
    assert "CYCLE: 2/288" in output


@pytest.mark.parametrize(("kwargs", "reason"), [
    ({"kill_switch_active": True}, "KILL_SWITCH_ACTIVE"),
    ({"risk_halt_active": True}, "RISK_HALT"),
])
def test_pretrade_halts(paths, kwargs, reason):
    state, _ = run([trade(1)], paths, **kwargs)
    assert state["stop_reason"] == reason
    assert state["accepted_qualifying_trades"] == 0


def test_stale_market_data_halt_is_propagated(paths):
    state, _ = run([CampaignHalt("STALE_MARKET_DATA")], paths)
    assert state["stop_reason"] == "STALE_MARKET_DATA"
    assert state["accepted_qualifying_trades"] == 0


def test_duplicate_and_malformed_evidence_stop_fail_closed(paths):
    duplicate, _ = run([trade(1), trade(1)], paths)
    assert duplicate["stop_reason"] == "DUPLICATE_TRADE_ID_REJECTED"
    assert duplicate["accepted_qualifying_trades"] == 1
    other_paths = CampaignPaths(*(paths.campaign_state.parent / f"bad-{index}" for index in range(7)))
    malformed = trade(2)
    del malformed["strategy_id"]
    rejected, _ = run([malformed], other_paths)
    assert rejected["stop_reason"] == "EVIDENCE_VALIDATION_FAILED"
    assert rejected["rejected_records"] == 1


def test_metrics_progression_and_session_loss(paths):
    state, output = run([trade(1, -4), trade(2, -3), trade(3, 10)], paths, maximum_session_loss=7)
    assert state["stop_reason"] == "MAXIMUM_SESSION_LOSS_HIT"
    assert state["net_pl"] == -7
    assert state["profit_factor"] == 0
    assert state["maximum_drawdown"] == 7
    assert state["consecutive_losses"] == 2
    assert state["expectancy"] == -3.5
    assert "REALIZED PAPER P/L: -3.0" in output
    assert "MAX DRAWDOWN: 7.0" in output


def test_all_persisted_safety_flags_are_false(paths):
    state, _ = run([trade(1)], paths)
    persisted = json.loads(paths.campaign_state.read_text())
    assert all(state[key] is False and persisted[key] is False for key in SAFETY_FLAGS)
    assert not paths.candidate.exists()
