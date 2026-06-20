"""Tests for paper fill simulator."""
from __future__ import annotations

import inspect

from automation.forex_engine import paper_fill_simulator as pfs


def _approved_preview() -> dict:
    return {
        "allowed": True,
        "approval_state": "paper_preview_ready",
        "paper_only": True,
        "mode": "paper_only",
        "preview_id": "preview-eurusd-buy-market-1",
        "pair": "EURUSD",
        "direction": "buy",
        "entry_type": "market",
        "entry_price": 1.1000,
        "stop_loss": 1.0950,
        "take_profit": 1.1100,
        "units": 1000.0,
        "raw_units": 1000.0,
        "dollar_risk": 100.0,
        "percent_risk": 1.0,
    }


def test_module_imports():
    assert pfs.PAPER_FILL_MODE == "PAPER_ONLY"


def test_valid_buy_fill_allowed():
    result = pfs.simulate_paper_fill(_approved_preview(), market_state={"bid": 1.0998, "ask": 1.1002}, timestamp=1700000000)
    assert result["allowed"] is True
    assert result["decision"] == pfs.PAPER_FILL_ALLOWED
    assert result["status"] == "active"
    assert result["trade"]
    assert result["lifecycle_result"]["status"] == "active"
    assert result["lifecycle_result"]["history"][:3] == ["previewed", "queued", "opened"]


def test_valid_sell_fill_allowed():
    preview = _approved_preview()
    preview["direction"] = "sell"
    result = pfs.simulate_paper_fill(preview, market_state={"bid": 1.0998, "ask": 1.1002}, timestamp=1700000000)
    assert result["allowed"] is True
    assert result["direction"] == "sell"


def test_result_shape():
    result = pfs.simulate_paper_fill(_approved_preview())
    required = {
        "allowed",
        "decision",
        "blocked_reason",
        "blocked_reasons",
        "warnings",
        "paper_only",
        "mode",
        "fill_id",
        "preview_id",
        "trade_id",
        "pair",
        "direction",
        "entry_type",
        "requested_price",
        "fill_price",
        "filled_units",
        "slippage",
        "spread",
        "opened_timestamp",
        "status",
        "trade",
        "lifecycle_result",
        "evidence",
        "evidence_path",
        "safety",
        "next_safe_action",
        "metadata",
    }
    assert required.issubset(set(result))
    assert result["safety"] == {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def test_block_when_not_allowed():
    preview = _approved_preview()
    preview["allowed"] = False
    result = pfs.simulate_paper_fill(preview)
    assert result["allowed"] is False
    assert pfs.REASON_PREVIEW_NOT_APPROVED in result["blocked_reasons"]


def test_block_when_approval_state_not_ready():
    preview = _approved_preview()
    preview["approval_state"] = "blocked"
    result = pfs.simulate_paper_fill(preview)
    assert result["allowed"] is False
    assert pfs.REASON_PREVIEW_NOT_APPROVED in result["blocked_reasons"]


def test_block_paper_only_false():
    preview = _approved_preview()
    preview["paper_only"] = False
    result = pfs.simulate_paper_fill(preview)
    assert result["allowed"] is False
    assert pfs.REASON_NON_PAPER_MODE in result["blocked_reasons"]


def test_block_live_demo_broker_modes():
    for mode in ("live", "demo", "broker"):
        preview = _approved_preview()
        preview["mode"] = mode
        result = pfs.simulate_paper_fill(preview)
        assert result["allowed"] is False
        assert pfs.REASON_LIVE_TRADING_BLOCKED in result["blocked_reasons"]


def test_block_missing_pair():
    preview = _approved_preview()
    preview.pop("pair", None)
    result = pfs.simulate_paper_fill(preview)
    assert result["allowed"] is False
    assert pfs.REASON_MISSING_PAIR in result["blocked_reasons"]


def test_block_missing_direction():
    preview = _approved_preview()
    preview.pop("direction", None)
    result = pfs.simulate_paper_fill(preview)
    assert result["allowed"] is False
    assert pfs.REASON_MISSING_DIRECTION in result["blocked_reasons"]


def test_block_missing_units():
    preview = _approved_preview()
    preview["units"] = 0
    result = pfs.simulate_paper_fill(preview)
    assert result["allowed"] is False
    assert pfs.REASON_MISSING_UNITS in result["blocked_reasons"]


def test_block_missing_entry_price():
    preview = _approved_preview()
    preview["entry_price"] = 0
    result = pfs.simulate_paper_fill(preview)
    assert result["allowed"] is False
    assert pfs.REASON_MISSING_ENTRY_PRICE in result["blocked_reasons"]


def test_missing_market_price_falls_back_to_entry():
    result = pfs.simulate_paper_fill(_approved_preview())
    assert result["allowed"] is True
    assert result["fill_price"] == _approved_preview()["entry_price"]


def test_market_bid_ask_fill_deterministic():
    preview = _approved_preview()
    result = pfs.simulate_paper_fill(preview, market_state={"bid": 1.2000, "ask": 1.2005}, fill_config={"slippage": 0.0002}, timestamp=1700000000)
    assert result["fill_price"] == 1.2007
    assert result["slippage"] == 0.0002

    preview["direction"] = "sell"
    result = pfs.simulate_paper_fill(preview, market_state={"bid": 1.2000, "ask": 1.2005}, fill_config={"slippage": 0.0001}, timestamp=1700000000)
    assert result["fill_price"] == 1.1999


def test_spread_cap_blocks():
    result = pfs.simulate_paper_fill(_approved_preview(), market_state={"bid": 1.2, "ask": 1.25}, fill_config={"max_spread": 0.01})
    assert result["allowed"] is False
    assert pfs.REASON_SPREAD_TOO_HIGH in result["blocked_reasons"]


def test_slippage_cap_blocks():
    result = pfs.simulate_paper_fill(_approved_preview(), market_state={"bid": 1.2, "ask": 1.2005}, fill_config={"slippage": 0.1, "max_slippage": 0.01})
    assert result["allowed"] is False
    assert pfs.REASON_SLIPPAGE_TOO_HIGH in result["blocked_reasons"]


def test_invalid_absolute_evidence_path_blocks():
    result = pfs.simulate_paper_fill(_approved_preview(), evidence_path="/tmp/evidence.json")
    assert result["allowed"] is False
    assert pfs.REASON_EVIDENCE_PATH_INVALID in result["blocked_reasons"]


def test_fill_id_deterministic():
    first = pfs.simulate_paper_fill(_approved_preview(), market_state={"bid": 1.2, "ask": 1.2001}, timestamp=1700001111)
    second = pfs.simulate_paper_fill(_approved_preview(), market_state={"bid": 1.2, "ask": 1.2001}, timestamp=1700001111)
    assert first["fill_id"] == second["fill_id"]


def test_blocked_result_deterministic_order():
    preview = _approved_preview()
    preview["pair"] = None
    preview["direction"] = None
    preview["units"] = 0
    preview["paper_only"] = False
    result = pfs.simulate_paper_fill(preview)
    assert result["blocked_reasons"] == [
        pfs.REASON_PREVIEW_NOT_APPROVED,
        pfs.REASON_NON_PAPER_MODE,
        pfs.REASON_MISSING_PAIR,
        pfs.REASON_MISSING_DIRECTION,
        pfs.REASON_MISSING_UNITS,
    ]


def test_source_scan_no_network_or_io():
    source = inspect.getsource(pfs)
    banned = (
        "subprocess",
        "requests",
        "socket",
        "urllib",
        "open(",
        ".write_text",
        "write_bytes",
        "pathlib",
        "os.system",
        "getenv(",
        "environ",
        "secret",
        "credential",
        "account_id",
    )
    for token in banned:
        assert token not in source
