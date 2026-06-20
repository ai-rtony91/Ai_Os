import pytest
from pathlib import Path

from automation.forex_engine.paper_trade_lifecycle import (
    PAPER_TRADE_ALLOWED_TRANSITIONS,
    PAPER_TRADE_STATUSES,
    TradeCloseReason,
    TradeDirection,
    TradeEntryType,
    PaperTradeStatus,
    build_paper_trade,
    paper_trade_from_dict,
    paper_trade_to_dict,
    transition_paper_trade,
    validate_paper_trade,
)

MODULE_PATH = Path(__file__).resolve().parents[2] / "automation" / "forex_engine" / "paper_trade_lifecycle.py"


def _valid_candidate_payload():
    return dict(
        trade_id="trade-1",
        pair="eurusd",
        direction=TradeDirection.BUY,
        entry_type=TradeEntryType.MARKET,
        entry_price=1.105,
        stop_loss=1.1,
        take_profit=1.12,
        units=1000.0,
        dollar_risk=10.0,
        percent_risk=0.5,
        created_timestamp="2026-06-20T00:00:00Z",
    )


def test_module_imports():
    assert PAPER_TRADE_ALLOWED_TRANSITIONS
    assert PAPER_TRADE_STATUSES
    assert PaperTradeStatus.CANDIDATE == "candidate"


def test_build_valid_candidate_trade_has_canonical_fields():
    trade = build_paper_trade(**_valid_candidate_payload())
    assert trade.trade_id == "trade-1"
    assert trade.pair == "EURUSD"
    assert trade.status == PaperTradeStatus.CANDIDATE
    assert trade.created_timestamp == "2026-06-20T00:00:00Z"
    assert trade.safety == {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }
    assert trade.paper_only is True
    assert trade.blocked_reason == "none"


def test_validate_paper_trade_requires_required_fields():
    trade = build_paper_trade(**_valid_candidate_payload())
    validation = validate_paper_trade(trade)
    assert validation["valid"] is True
    assert validation["paper_only"] is True
    assert validation["next_safe_action"]


def test_validate_rejects_empty_trade_id():
    trade = build_paper_trade(**_valid_candidate_payload(), trade_id="")
    validation = validate_paper_trade(trade)
    assert validation["valid"] is False
    assert any("trade_id" in error for error in validation["errors"])


def test_validate_rejects_bad_direction():
    trade = build_paper_trade(**_valid_candidate_payload(), direction="sideways")
    validation = validate_paper_trade(trade)
    assert validation["valid"] is False
    assert any("direction" in error for error in validation["errors"])


def test_validate_rejects_bad_entry_type():
    trade = build_paper_trade(**_valid_candidate_payload(), entry_type="market_plus")
    validation = validate_paper_trade(trade)
    assert validation["valid"] is False
    assert any("entry_type" in error for error in validation["errors"])


def test_validate_rejects_invalid_prices_and_units():
    assert validate_paper_trade(build_paper_trade(**_valid_candidate_payload(), entry_price=0.0))["valid"] is False
    assert validate_paper_trade(build_paper_trade(**_valid_candidate_payload(), stop_loss=0.0))["valid"] is False
    assert validate_paper_trade(build_paper_trade(**_valid_candidate_payload(), take_profit=-1.0))["valid"] is False
    assert validate_paper_trade(build_paper_trade(**_valid_candidate_payload(), units=0.0))["valid"] is False


def test_validate_rejects_negative_risks():
    assert validate_paper_trade(build_paper_trade(**_valid_candidate_payload(), dollar_risk=-1.0))["valid"] is False
    assert validate_paper_trade(build_paper_trade(**_valid_candidate_payload(), percent_risk=-0.5))["valid"] is False


def test_transitions_and_timestamps():
    trade = build_paper_trade(**_valid_candidate_payload())
    preview = transition_paper_trade(trade, PaperTradeStatus.PREVIEWED, reason="reviewed")
    queued = transition_paper_trade(preview, PaperTradeStatus.QUEUED, reason="queued")
    opened = transition_paper_trade(queued, PaperTradeStatus.OPENED)
    active = transition_paper_trade(opened, PaperTradeStatus.ACTIVE)
    closed = transition_paper_trade(
        active,
        PaperTradeStatus.CLOSED,
        reason=TradeCloseReason.TAKE_PROFIT,
        realized_pnl=42.5,
    )

    assert active.status == PaperTradeStatus.ACTIVE
    assert opened.opened_timestamp is not None
    assert active.opened_timestamp == opened.opened_timestamp
    assert closed.closed_timestamp is not None
    assert closed.close_reason == TradeCloseReason.TAKE_PROFIT
    assert closed.realized_pnl == 42.5
    assert len(closed.lifecycle_history) == 4


def test_blocked_transitions():
    trade = build_paper_trade(**_valid_candidate_payload())
    preview = transition_paper_trade(trade, PaperTradeStatus.PREVIEWED)
    with pytest.raises(ValueError):
        transition_paper_trade(trade, PaperTradeStatus.ACTIVE)
    with pytest.raises(ValueError):
        transition_paper_trade(preview, PaperTradeStatus.ACTIVE)
    queued = transition_paper_trade(preview, PaperTradeStatus.QUEUED)
    rejected = transition_paper_trade(queued, PaperTradeStatus.REJECTED, reason="rejected")
    with pytest.raises(ValueError):
        transition_paper_trade(rejected, PaperTradeStatus.QUEUED)
    opened = transition_paper_trade(queued, PaperTradeStatus.OPENED)
    closed = transition_paper_trade(opened, PaperTradeStatus.CLOSED, reason=TradeCloseReason.MANUAL_CLOSE)
    with pytest.raises(ValueError):
        transition_paper_trade(closed, PaperTradeStatus.ACTIVE)
    killed = transition_paper_trade(
        transition_paper_trade(
            transition_paper_trade(queued, PaperTradeStatus.OPENED),
            PaperTradeStatus.ACTIVE,
        ),
        PaperTradeStatus.KILLED,
    )
    with pytest.raises(ValueError):
        transition_paper_trade(killed, PaperTradeStatus.ACTIVE)


def test_lifecycle_dict_round_trip_rounds_trip():
    trade = build_paper_trade(**_valid_candidate_payload())
    trade = transition_paper_trade(trade, PaperTradeStatus.PREVIEWED, reason="screened")
    payload = paper_trade_to_dict(trade)
    assert payload["trade_id"] == trade.trade_id
    assert payload["safety"]["paper_only"] is True
    assert payload["safety"]["broker"] is False

    rebuilt = paper_trade_from_dict(payload)
    rebuilt_payload = paper_trade_to_dict(rebuilt)
    assert rebuilt_payload["trade_id"] == trade.trade_id
    assert rebuilt_payload["pair"] == trade.pair
    assert rebuilt_payload["status"] == trade.status


def test_evidence_path_is_metadata_only_and_no_file_write():
    trade = build_paper_trade(**_valid_candidate_payload(), evidence_path="proofs/eurusd/trade-1.json")
    payload = paper_trade_to_dict(trade)
    assert payload["evidence_path"] == "proofs/eurusd/trade-1.json"
    assert ".." not in payload["evidence_path"]


def test_blocked_terminal_transition_and_status_graph_shape():
    assert PaperTradeStatus.CANDIDATE in PAPER_TRADE_STATUSES
    assert PaperTradeStatus.CLOSED in PAPER_TRADE_STATUSES
    for source, targets in PAPER_TRADE_ALLOWED_TRANSITIONS.items():
        assert source in PAPER_TRADE_STATUSES
        for target in targets:
            assert target in PAPER_TRADE_STATUSES


def test_module_source_is_paper_only_no_network_or_broker_runtime_calls():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for token in ("subprocess", "socket", "urllib", "requests"):
        assert token not in source

    for token in ("open(", "write_text(", "write_bytes(", "os.system", "pathlib", "credential", "api_key", "broker"):
        assert token not in source
