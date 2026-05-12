from pathlib import Path

from aios.modules.trader.payloads.alert_payload import build_mock_alert_payload
from aios.modules.trader.routes.paper_route_preview import build_paper_route_preview


def _preview(permission: str, signal: str) -> dict:
    payload = build_mock_alert_payload("EURUSD", "1h", permission, signal, 0.75)
    return build_paper_route_preview(payload)


def test_bullish_buy_creates_paper_buy_preview():
    assert _preview("bullish", "BUY")["action"] == "PAPER_BUY_PREVIEW"


def test_bearish_sell_creates_paper_sell_preview():
    assert _preview("bearish", "SELL")["action"] == "PAPER_SELL_PREVIEW"


def test_hold_creates_no_trade():
    assert _preview("bullish", "HOLD")["action"] == "NO_TRADE"


def test_blocked_permission_creates_blocked():
    assert _preview("blocked", "BUY")["action"] == "BLOCKED"


def test_mismatched_permission_signal_creates_blocked():
    assert _preview("bullish", "SELL")["action"] == "BLOCKED"


def test_route_status_is_always_paper_preview_only():
    assert _preview("bullish", "BUY")["route_status"] == "PAPER_PREVIEW_ONLY"


def test_paper_only_is_always_true():
    assert _preview("bullish", "BUY")["paper_only"] is True


def test_live_execution_status_is_always_blocked():
    assert _preview("bullish", "BUY")["live_execution_status"] == "BLOCKED"


def test_execution_allowed_is_always_false():
    assert _preview("bullish", "BUY")["execution_allowed"] is False


def test_implementation_files_contain_no_forbidden_live_execution_strings():
    files = [
        Path("aios/modules/trader/payloads/alert_payload.py"),
        Path("aios/modules/trader/routes/paper_route_preview.py"),
    ]
    blocked = [
        "webhook" + "_url",
        "api" + "_key",
        "secret" + "_key",
        "oanda",
        "alpaca",
        "binance",
        "coinbase",
        "live" + "_order",
        "real" + "_order",
    ]

    for path in files:
        content = path.read_text().lower()
        for token in blocked:
            assert token not in content
