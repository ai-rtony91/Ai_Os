from pathlib import Path
from unittest.mock import patch

from automation.forex_engine import multi_trade_queue


def _candidate(candidate_id="c1", pair="EURUSD", direction="buy", score=60.0, dollar_risk=100.0, mode="PAPER_ONLY"):
    return {
        "candidate_id": candidate_id,
        "pair": pair,
        "direction": direction,
        "score": score,
        "dollar_risk": dollar_risk,
        "take_profit": 1.12,
        "stop_loss": 1.10,
        "entry_price": 1.11,
        "entry_type": "market",
        "risk_percent": 1.0,
        "mode": mode,
        "paper_only": True,
    }


def test_module_imports():
    assert multi_trade_queue.MULTI_TRADE_QUEUE_MODE == "PAPER_ONLY"


def test_ranked_candidates_sorted_by_score_then_pair_then_id():
    candidates = [
        _candidate("z", score=80.0),
        _candidate("a", pair="GBPUSD", score=80.0),
        _candidate("m", pair="EURUSD", score=80.0),
    ]
    result = multi_trade_queue.build_multi_trade_queue(candidates)
    ranked = [(c["candidate_id"], c["pair"]) for c in result["ranked_candidates"]]
    assert ranked == [("m", "EURUSD"), ("a", "GBPUSD"), ("z", "EURUSD")]


def test_selected_are_ranking_respected():
    candidates = [
        _candidate("low", score=40.0),
        _candidate("high", score=90.0),
        _candidate("mid", score=85.0),
    ]
    result = multi_trade_queue.build_multi_trade_queue(candidates)
    assert result["selected_count"] == 2
    selected = result["selected_candidates"]
    assert [c["candidate_id"] for c in selected] == ["high", "mid"]


def test_low_score_rejected():
    result = multi_trade_queue.build_multi_trade_queue([_candidate("low", score=10.0)])
    assert result["allowed"] is False
    assert result["selected_count"] == 0
    assert result["rejected_count"] == 1
    assert result["rejected_candidates"][0]["rejection_reasons"] == ["score_below_threshold"]


def test_duplicate_setup_rejected():
    candidates = [
        _candidate("a", pair="EURUSD", direction="buy", score=85.0),
        _candidate("b", pair="EURUSD", direction="buy", score=84.0),
        _candidate("c", pair="GBPUSD", direction="sell", score=83.0),
    ]
    result = multi_trade_queue.build_multi_trade_queue(candidates)
    assert result["selected_count"] == 2
    assert result["rejected_count"] == 1
    assert result["rejected_candidates"][0]["rejection_reasons"] == ["duplicate_setup"]


def test_max_selected_trades_enforced():
    result = multi_trade_queue.build_multi_trade_queue(
        [
            _candidate("a", score=80.0),
            _candidate("b", pair="GBPUSD", score=81.0),
            _candidate("c", pair="USDJPY", score=82.0),
            _candidate("d", pair="AUDUSD", score=83.0),
        ],
        limits={"max_selected_trades": 2},
    )
    assert result["selected_count"] == 2
    assert result["rejected_count"] == 2
    assert result["rejected_candidates"][0]["rejection_reasons"] == ["max_selected_trades_hit"]


def test_max_open_trades_enforced_using_open_trades():
    open_trades = [{"status": "active", "pair": "EURUSD", "direction": "buy"}]
    result = multi_trade_queue.build_multi_trade_queue(
        [_candidate("a", score=90.0), _candidate("b", pair="GBPUSD", score=89.0)],
        open_trades=open_trades,
        limits={"max_open_trades": 1},
    )
    assert result["selected_count"] == 0
    assert all("max_open_trades_hit" in c["rejection_reasons"] for c in result["rejected_candidates"])


def test_max_candidates_per_pair_enforced():
    result = multi_trade_queue.build_multi_trade_queue(
        [_candidate("a", pair="EURUSD", score=90.0), _candidate("b", pair="EURUSD", score=89.0), _candidate("c", pair="GBPUSD", score=88.0)],
        limits={"max_candidates_per_pair": 1},
    )
    assert result["selected_count"] == 2
    assert result["rejected_count"] == 1
    assert result["rejected_candidates"][0]["rejection_reasons"] == ["max_pair_candidate_hit"]


def test_cooldown_after_loss_blocks_selection():
    closed = [
        {
            "status": "closed",
            "pair": "EURUSD",
            "direction": "buy",
            "close_reason": "stop_loss",
            "realized_pnl": -50,
            "closed_timestamp": 1000,
        }
    ]
    result = multi_trade_queue.build_multi_trade_queue(
        [_candidate("a", score=90.0)],
        closed_trades=closed,
        limits={"cooldown_after_loss_seconds": 120},
        now_timestamp=1010,
    )
    assert result["allowed"] is False
    assert result["warnings"] == ["cooldown_active"]
    assert result["rejected_candidates"][0]["rejection_reasons"] == ["cooldown_active"]


def test_risk_governor_blocked_candidate_rejected():
    candidates = [_candidate("good", score=90.0), _candidate("bad", score=89.0)]

    def fake_risk(preview, *args, **kwargs):
        if preview.get("candidate_id") == "bad":
            return {"allowed": False, "blocked_reason": "max_open_risk_hit", "blocked_reasons": ["max_open_risk_hit"]}
        return {"allowed": True, "blocked_reason": "none", "blocked_reasons": []}

    with patch("automation.forex_engine.multi_trade_queue.evaluate_risk_preview", side_effect=fake_risk):
        result = multi_trade_queue.build_multi_trade_queue(candidates, limits={"require_risk_governor": True})
    assert result["selected_count"] == 1
    assert result["rejected_count"] == 1
    assert result["rejected_candidates"][0]["rejection_reasons"] == ["risk_governor_blocked"]


def test_order_preview_required_blocks_candidate():
    with patch(
        "automation.forex_engine.multi_trade_queue.build_order_preview",
        return_value={"allowed": False, "blocked_reason": "missing_entry_price", "blocked_reasons": ["missing_entry_price"]},
    ):
        result = multi_trade_queue.build_multi_trade_queue(
            [_candidate("a", score=90.0)],
            limits={"require_order_preview": True},
        )
    assert result["selected_count"] == 0
    assert result["rejected_candidates"][0]["rejection_reasons"] == ["order_preview_blocked"]


def test_live_demo_broker_mode_blocked():
    for mode in ["live", "demo", "broker"]:
        result = multi_trade_queue.build_multi_trade_queue([_candidate("a", score=80.0, mode=mode)])
        assert result["allowed"] is False
        assert result["blocked_reasons"] == ["live_trading_blocked"]


def test_paper_only_false_blocked():
    source = {"candidates": [_candidate("a", score=80.0)], "paper_only": False}
    result = multi_trade_queue.build_multi_trade_queue(source)
    assert result["allowed"] is False
    assert result["blocked_reasons"] == ["non_paper_mode"]


def test_missing_required_fields_blocked():
    candidates = [
        {"candidate_id": "", "pair": "EURUSD", "direction": "buy", "score": 80.0},
        {"candidate_id": "no_pair", "direction": "buy", "score": 80.0},
        {"candidate_id": "no_direction", "pair": "EURUSD", "score": 80.0},
        {"candidate_id": "bad_score", "pair": "EURUSD", "direction": "buy", "score": "bad"},
    ]
    result = multi_trade_queue.build_multi_trade_queue(candidates)
    reasons = sorted({reason for cand in result["rejected_candidates"] for reason in cand["rejection_reasons"]})
    assert "missing_candidate_id" in reasons
    assert "missing_pair" in reasons
    assert "missing_direction" in reasons
    assert "invalid_score" in reasons


def test_invalid_evidence_path_blocks():
    result = multi_trade_queue.build_multi_trade_queue([_candidate("a", score=80.0)], evidence_path="C:\\tmp\\bad.json")
    assert result["allowed"] is False
    assert result["blocked_reasons"] == ["evidence_path_invalid"]


def test_selected_candidates_contain_preview_fields():
    result = multi_trade_queue.build_multi_trade_queue([_candidate("a", score=80.0)])
    item = result["selected_candidates"][0]
    for key in ["candidate_id", "pair", "direction", "entry_price", "stop_loss", "take_profit", "risk_percent"]:
        assert key in item


def test_rejected_contains_rejection_reasons():
    result = multi_trade_queue.build_multi_trade_queue([_candidate("a", score=10.0)])
    assert "rejection_reasons" in result["rejected_candidates"][0]


def test_safety_dict_present():
    result = multi_trade_queue.build_multi_trade_queue([_candidate("a", score=80.0)])
    assert result["safety"] == {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def test_no_file_write_evidence():
    result = multi_trade_queue.build_multi_trade_queue([_candidate("a", score=80.0)])
    assert isinstance(result["evidence"], dict)
    assert result["evidence"]["selected_candidate_ids"] == ["a"]


def test_deterministic_rejected_reasons():
    result = multi_trade_queue.build_multi_trade_queue(
        [_candidate("a", score=10.0), _candidate("b", score=20.0)],
        limits={"max_selected_trades": 1},
    )
    assert result["blocked_reasons"][0] == "score_below_threshold"


def test_source_scan_no_forbidden_runtime_or_secret_access():
    source = Path("automation/forex_engine/multi_trade_queue.py").read_text(encoding="utf-8")
    forbidden = [
        "subprocess",
        "requests",
        "socket",
        "urllib",
        "open(",
        ".write_text",
        ".write_bytes",
        "pathlib",
        "os.system",
        "getenv",
        "environ",
        "credential",
        "account_id",
        "secret",
    ]
    for token in forbidden:
        assert token not in source
