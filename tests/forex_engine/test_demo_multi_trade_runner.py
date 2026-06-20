from __future__ import annotations

import inspect

from automation.forex_engine import demo_multi_trade_runner as runner


def _promotion() -> dict:
    return {"allowed": True, "demo_promotion_ready": True, "mode": "PAPER_TO_DEMO_PROMOTION_ONLY"}


def _readonly() -> dict:
    return {"allowed": True, "fresh": True, "mode": "DEMO_READONLY"}


def _reconciliation() -> dict:
    return {"allowed": True, "matched": True, "match_score": 1.0, "mode": "DEMO_RECONCILIATION_ONLY"}


def _intent(key: str = "demo-map-1", pair: str = "EUR_USD") -> dict:
    return {
        "pair": pair,
        "side": "BUY",
        "units": 1000.0,
        "order_type": "MARKET",
        "entry_price": 1.1,
        "stop_loss": 1.095,
        "take_profit": 1.11,
        "client_order_id": f"client-{key}",
        "idempotency_key": key,
        "mode": "DEMO_MAPPING_ONLY",
        "submit_enabled": False,
        "broker_write_enabled": False,
        "live_trading": False,
    }


def _plan(**overrides) -> dict:
    payload = {
        "promotion_decision": _promotion(),
        "mapped_demo_order_intents": [_intent()],
        "readonly_snapshot": _readonly(),
        "reconciliation_result": _reconciliation(),
        "limits": {"max_demo_orders": 3},
    }
    payload.update(overrides)
    return runner.build_demo_run_plan(**payload)


def test_valid_run_plan() -> None:
    result = _plan()

    assert result["allowed"] is True
    assert result["decision"] == runner.DECISION_ALLOWED
    assert result["mode"] == runner.RUNNER_MODE
    assert result["submit_enabled"] is False
    assert result["broker_write_enabled"] is False
    assert result["live_trading"] is False
    assert len(result["selected_intents"]) == 1
    assert result["rejected_intents"] == []
    assert result["idempotency_keys"] == ["demo-map-1"]
    assert result["max_demo_orders"] == 3
    assert result["demo_run_plan"]["mode"] == runner.RUNNER_MODE


def test_promotion_block() -> None:
    promotion = _promotion()
    promotion["allowed"] = False
    result = _plan(promotion_decision=promotion)

    assert result["allowed"] is False
    assert runner.REASON_PROMOTION_NOT_ALLOWED in result["blocked_reasons"]


def test_readonly_block() -> None:
    readonly = _readonly()
    readonly["allowed"] = False
    result = _plan(readonly_snapshot=readonly)

    assert result["allowed"] is False
    assert runner.REASON_READONLY_NOT_ALLOWED in result["blocked_reasons"]


def test_reconciliation_block() -> None:
    reconciliation = _reconciliation()
    reconciliation["matched"] = False
    reconciliation["match_score"] = 0.5
    result = _plan(reconciliation_result=reconciliation)

    assert result["allowed"] is False
    assert runner.REASON_RECONCILIATION_NOT_READY in result["blocked_reasons"]


def test_submit_live_broker_sensitive_and_identifier_blockers() -> None:
    cases = (
        ("submit_enabled", True, runner.REASON_SUBMIT_ENABLED),
        ("broker_write_enabled", True, runner.REASON_BROKER_WRITE_ENABLED),
        ("live_trading", True, runner.REASON_LIVE_TRADING_ENABLED),
        ("credentials_loaded", True, runner.REASON_CREDENTIALS_PRESENT),
        ("account_id", "101-222-333333-001", runner.REASON_ACCOUNT_ID_PRESENT),
    )
    for field, value, reason in cases:
        intent = _intent()
        intent[field] = value
        result = _plan(mapped_demo_order_intents=[intent])
        assert result["allowed"] is False
        assert reason in result["blocked_reasons"]


def test_duplicate_idempotency_key_blocks() -> None:
    result = _plan(mapped_demo_order_intents=[_intent("same"), _intent("same", pair="GBP_USD")])

    assert result["allowed"] is False
    assert runner.REASON_DUPLICATE_IDEMPOTENCY_KEY in result["blocked_reasons"]


def test_cap_block() -> None:
    intents = [_intent("one"), _intent("two", pair="GBP_USD")]
    result = _plan(mapped_demo_order_intents=intents, limits={"max_demo_orders": 1})

    assert result["allowed"] is False
    assert runner.REASON_DEMO_ORDER_CAP_EXCEEDED in result["blocked_reasons"]


def test_invalid_intent_fields_block() -> None:
    intent = _intent()
    intent["units"] = 0
    intent["pair"] = "AUD_USD"
    intent["side"] = "HOLD"
    intent["order_type"] = "LIMIT"

    result = _plan(mapped_demo_order_intents=[intent])

    assert result["allowed"] is False
    assert runner.REASON_INVALID_UNITS in result["blocked_reasons"]
    assert runner.REASON_UNSUPPORTED_PAIR in result["blocked_reasons"]
    assert runner.REASON_UNSUPPORTED_SIDE in result["blocked_reasons"]
    assert runner.REASON_UNSUPPORTED_ORDER_TYPE in result["blocked_reasons"]


def test_run_id_is_deterministic() -> None:
    first = _plan(mapped_demo_order_intents=[_intent("one"), _intent("two", pair="GBP_USD")])
    second = _plan(mapped_demo_order_intents=[_intent("two", pair="GBP_USD"), _intent("one")])

    assert first["run_id"] == second["run_id"]
    assert first["run_id"].startswith("demo-run-")


def test_safety_dict() -> None:
    result = _plan()

    assert result["safety"] == {
        "paper_only": True,
        "demo_readonly": True,
        "submit_enabled": False,
        "broker_write_enabled": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_submit": False,
    }


def test_source_scan_has_no_broker_network_filesystem_or_sensitive_access() -> None:
    source = inspect.getsource(runner).lower()
    banned = (
        "import subprocess",
        "from subprocess",
        "import requests",
        "from requests",
        "import socket",
        "from socket",
        "import urllib",
        "from urllib",
        "import pathlib",
        "from pathlib",
        "open(",
        ".write(",
        "write_text(",
        "write_bytes(",
        "os.system",
        "os.getenv",
        "os.environ",
        "getenv(",
        "environ[",
        "api_key",
        "access_token",
        "refresh_token",
        "private_key",
        "password",
        "bearer ",
        "oanda",
        "broker_sdk",
    )
    for token in banned:
        assert token not in source
