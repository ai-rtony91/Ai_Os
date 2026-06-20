"""Tests for paper-only order preview hardening."""
from __future__ import annotations

import inspect

from automation.forex_engine import order_preview as op


def _base_candidate() -> dict:
    return {
        "paper_only": True,
        "pair": "EURUSD",
        "direction": "buy",
        "entry_type": "market",
        "entry_price": 1.1000,
        "stop_loss": 1.0950,
        "take_profit": 1.1100,
        "risk_percent": 1.0,
        "spread": 0.0001,
        "data_timestamp": 1761000000.0,
    }


def test_module_imports():
    assert op.ORDER_PREVIEW_MODE == "PAPER_ONLY"
    assert op.ORDER_PREVIEW_ALLOWED == "allowed"
    assert op.ORDER_PREVIEW_BLOCKED == "blocked"


def test_valid_preview_allowed():
    result = op.build_order_preview(
        _base_candidate(),
        account_state={"equity": 10000},
        limits={
            "max_risk_percent": 5.0,
            "max_risk_dollars": 500.0,
            "max_units": 0,
            "min_units": 1,
            "rounding_increment": 1,
            "default_risk_percent": 1.0,
        },
    )
    assert result["allowed"] is True
    assert result["decision"] == op.ORDER_PREVIEW_ALLOWED
    assert result["approval_state"] == "paper_preview_ready"


def test_result_shape():
    result = op.build_order_preview(_base_candidate(), account_state={"equity": 10000})
    required_keys = {
        "allowed",
        "decision",
        "preview_id",
        "blocked_reason",
        "blocked_reasons",
        "warnings",
        "paper_only",
        "mode",
        "pair",
        "direction",
        "entry_type",
        "entry_price",
        "stop_loss",
        "take_profit",
        "units",
        "raw_units",
        "dollar_risk",
        "percent_risk",
        "reward_estimate",
        "risk_reward",
        "spread",
        "data_freshness",
        "sizing_result",
        "risk_governor_result",
        "approval_state",
        "evidence_path",
        "safety",
        "next_safe_action",
        "metadata",
    }
    assert required_keys.issubset(set(result))
    assert result["safety"] == {
        "paper_only": True,
        "broker": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_access": False,
    }


def test_candidate_paper_only_false_blocks():
    candidate = _base_candidate()
    candidate["paper_only"] = False
    result = op.build_order_preview(candidate, account_state={"equity": 10000})
    assert result["allowed"] is False
    assert op.REASON_NON_PAPER_MODE in result["blocked_reasons"]


def test_candidate_live_mode_blocks():
    candidate = _base_candidate()
    candidate["mode"] = "live"
    result = op.build_order_preview(candidate, account_state={"equity": 10000})
    assert result["allowed"] is False
    assert op.REASON_LIVE_TRADING_BLOCKED in result["blocked_reasons"]


def test_demo_mode_blocks():
    candidate = _base_candidate()
    candidate["mode"] = "demo"
    result = op.build_order_preview(candidate, account_state={"equity": 10000})
    assert result["allowed"] is False
    assert op.REASON_LIVE_TRADING_BLOCKED in result["blocked_reasons"]


def test_broker_mode_blocks():
    candidate = _base_candidate()
    candidate["mode"] = "broker"
    result = op.build_order_preview(candidate, account_state={"equity": 10000})
    assert result["allowed"] is False
    assert op.REASON_LIVE_TRADING_BLOCKED in result["blocked_reasons"]


def test_missing_pair_blocks():
    candidate = _base_candidate()
    candidate.pop("pair", None)
    result = op.build_order_preview(candidate, account_state={"equity": 10000})
    assert result["allowed"] is False
    assert op.REASON_MISSING_PAIR in result["blocked_reasons"]


def test_missing_direction_blocks():
    candidate = _base_candidate()
    candidate.pop("direction", None)
    result = op.build_order_preview(candidate, account_state={"equity": 10000})
    assert result["allowed"] is False
    assert op.REASON_MISSING_DIRECTION in result["blocked_reasons"]


def test_missing_entry_price_blocks():
    candidate = _base_candidate()
    candidate.pop("entry_price", None)
    result = op.build_order_preview(candidate, account_state={"equity": 10000})
    assert result["allowed"] is False
    assert op.REASON_MISSING_ENTRY_PRICE in result["blocked_reasons"]


def test_missing_stop_loss_blocks():
    candidate = _base_candidate()
    candidate.pop("stop_loss", None)
    result = op.build_order_preview(candidate, account_state={"equity": 10000})
    assert result["allowed"] is False
    assert op.REASON_MISSING_STOP_LOSS in result["blocked_reasons"]


def test_missing_take_profit_blocks():
    candidate = _base_candidate()
    candidate.pop("take_profit", None)
    result = op.build_order_preview(candidate, account_state={"equity": 10000})
    assert result["allowed"] is False
    assert op.REASON_MISSING_TAKE_PROFIT in result["blocked_reasons"]


def test_invalid_account_state_propagates_sizing_blocked():
    result = op.build_order_preview(_base_candidate(), account_state={"equity": -10000})
    assert result["allowed"] is False
    assert op.REASON_SIZING_BLOCKED in result["blocked_reasons"]


def test_risk_block_propagates():
    candidate = _base_candidate()
    result = op.build_order_preview(
        candidate,
        account_state={"equity": 10000},
        limits={"max_risk_per_trade_pct": 1.0},
        market_state={"kill_switch_active": True},
    )
    assert result["allowed"] is False
    assert op.REASON_RISK_BLOCKED in result["blocked_reasons"]


def test_approval_ready_only_when_sizing_and_risk_allow():
    bad_candidate = _base_candidate()
    bad_candidate["risk_percent"] = 99.0
    blocked = op.build_order_preview(bad_candidate, account_state={"equity": 10000}, limits={"max_risk_per_trade_pct": 1.0})
    assert blocked["approval_state"] == op.ORDER_PREVIEW_BLOCKED
    assert blocked["allowed"] is False

    good = op.build_order_preview(
        _base_candidate(),
        account_state={"equity": 10000},
        limits={"max_risk_percent": 10.0},
    )
    assert good["approval_state"] == "paper_preview_ready"
    assert good["allowed"] is True


def test_units_from_sizing_result():
    result = op.build_order_preview(_base_candidate(), account_state={"equity": 10000})
    assert result["raw_units"] == result["sizing_result"]["raw_units"]
    assert result["units"] == result["sizing_result"]["units"]
    assert result["dollar_risk"] == result["sizing_result"]["risk_dollars"]
    assert result["percent_risk"] == result["sizing_result"]["risk_percent"]


def test_reward_and_risk_reward_deterministic():
    result = op.build_order_preview(_base_candidate(), account_state={"equity": 10000})
    expected_reward = abs(result["take_profit"] - result["entry_price"]) * result["units"]
    assert result["reward_estimate"] == expected_reward
    if result["dollar_risk"] > 0:
        assert result["risk_reward"] == expected_reward / result["dollar_risk"]


def test_spread_and_data_freshness_propagated():
    candidate = _base_candidate()
    candidate["spread"] = 0.0002
    result = op.build_order_preview(candidate, account_state={"equity": 10000})
    assert result["spread"] == candidate["spread"]
    assert "data_freshness" in result


def test_evidence_path_is_metadata_only():
    result = op.build_order_preview(_base_candidate(), account_state={"equity": 10000}, evidence_path="runs/preview-eurusd.json")
    assert result["evidence_path"] == "runs/preview-eurusd.json"


def test_evidence_path_rejected_if_absolute():
    result = op.build_order_preview(_base_candidate(), account_state={"equity": 10000}, evidence_path="/tmp/evidence.json")
    assert result["allowed"] is False
    assert op.REASON_EVIDENCE_PATH_INVALID in result["blocked_reasons"]


def test_preview_id_deterministic():
    first = op.build_order_preview(_base_candidate(), account_state={"equity": 10000}, now_timestamp=1700000000)
    second = op.build_order_preview(_base_candidate(), account_state={"equity": 10000}, now_timestamp=1700000000)
    assert first["preview_id"] == second["preview_id"]


def test_multiple_blocked_reasons_deterministic():
    candidate = _base_candidate()
    candidate.pop("pair", None)
    candidate["paper_only"] = False
    candidate["mode"] = "live"
    result = op.build_order_preview(candidate, account_state={"equity": 10000})
    assert result["blocked_reasons"] == [
        op.REASON_MISSING_PAIR,
        op.REASON_NON_PAPER_MODE,
        op.REASON_LIVE_TRADING_BLOCKED,
        op.REASON_INVALID_CANDIDATE,
    ]


def test_order_preview_source_scan_no_network_or_io():
    source = inspect.getsource(op)
    banned = (
        "subprocess",
        "requests",
        "socket",
        "urllib",
        "open(",
        ".write_text",
        ".write_bytes",
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
