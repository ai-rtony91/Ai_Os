from __future__ import annotations

import inspect

from automation.forex_engine import paper_to_demo_promotion as promotion


def _replay() -> dict:
    return {
        "trade_count": 25,
        "session_count": 4,
        "max_drawdown_pct": 3.2,
        "risk_failures": [],
    }


def _ledger() -> dict:
    return {
        "allowed": True,
        "validation_passed": True,
        "entries": [{"id": "paper-evidence-1"}],
    }


def _supervisor() -> dict:
    return {
        "completed_sessions": 4,
        "risk_compliance_met": True,
    }


def _review() -> dict:
    return {
        "allowed": True,
        "risk_failures": [],
    }


def _readonly() -> dict:
    return {
        "allowed": True,
        "fresh": True,
        "mode": "DEMO_READONLY",
    }


def _mapping() -> dict:
    return {
        "allowed": True,
        "mode": "DEMO_MAPPING_ONLY",
    }


def _reconciliation() -> dict:
    return {
        "allowed": True,
        "matched": True,
        "match_score": 1.0,
        "mode": "DEMO_RECONCILIATION_ONLY",
    }


def _limits() -> dict:
    return {
        "minimum_trade_count": 20,
        "minimum_session_count": 3,
        "maximum_drawdown_pct": 5.0,
    }


def _evaluate(**overrides) -> dict:
    payloads = {
        "session_replay": _replay(),
        "evidence_ledger": _ledger(),
        "long_run_supervisor": _supervisor(),
        "self_improvement_review": _review(),
        "demo_connector_readonly": _readonly(),
        "demo_order_mapping": _mapping(),
        "demo_reconciliation": _reconciliation(),
        "limits": _limits(),
    }
    payloads.update(overrides)
    return promotion.evaluate_paper_to_demo_promotion(**payloads)


def test_mature_paper_evidence_allows_demo_promotion() -> None:
    result = _evaluate()

    assert result["allowed"] is True
    assert result["decision"] == promotion.DECISION_ALLOWED
    assert result["demo_promotion_ready"] is True
    assert result["evidence_score"] == 1.0
    assert result["minimum_trade_count_met"] is True
    assert result["minimum_session_count_met"] is True
    assert result["risk_compliance_met"] is True
    assert result["drawdown_within_limit"] is True
    assert result["readonly_ready"] is True
    assert result["mapping_ready"] is True
    assert result["reconciliation_ready"] is True


def test_immature_evidence_blocks() -> None:
    replay = _replay()
    replay["trade_count"] = 2
    replay["session_count"] = 1

    result = _evaluate(session_replay=replay)

    assert result["allowed"] is False
    assert promotion.REASON_TRADE_COUNT_LOW in result["blocked_reasons"]
    assert promotion.REASON_SESSION_COUNT_LOW in result["blocked_reasons"]
    assert "minimum_trade_count" in result["missing_requirements"]
    assert "minimum_session_count" in result["missing_requirements"]


def test_missing_replay_blocks() -> None:
    result = _evaluate(session_replay={})

    assert result["allowed"] is False
    assert promotion.REASON_MISSING_REPLAY in result["blocked_reasons"]


def test_missing_ledger_blocks() -> None:
    result = _evaluate(evidence_ledger={})

    assert result["allowed"] is False
    assert promotion.REASON_MISSING_EVIDENCE in result["blocked_reasons"]


def test_drawdown_blocks() -> None:
    replay = _replay()
    replay["max_drawdown_pct"] = 9.5

    result = _evaluate(session_replay=replay)

    assert result["allowed"] is False
    assert promotion.REASON_DRAWDOWN_TOO_HIGH in result["blocked_reasons"]
    assert result["drawdown_within_limit"] is False


def test_risk_failures_block() -> None:
    replay = _replay()
    replay["risk_failures"] = ["spread_too_high"]

    result = _evaluate(session_replay=replay)

    assert result["allowed"] is False
    assert promotion.REASON_RISK_FAILURES_UNRESOLVED in result["blocked_reasons"]
    assert result["risk_compliance_met"] is False


def test_readonly_failure_blocks() -> None:
    readonly = _readonly()
    readonly["allowed"] = False

    result = _evaluate(demo_connector_readonly=readonly)

    assert result["allowed"] is False
    assert promotion.REASON_READONLY_FAILED in result["blocked_reasons"]


def test_mapping_failure_blocks() -> None:
    mapping = _mapping()
    mapping["allowed"] = False

    result = _evaluate(demo_order_mapping=mapping)

    assert result["allowed"] is False
    assert promotion.REASON_MAPPING_FAILED in result["blocked_reasons"]


def test_reconciliation_failure_blocks() -> None:
    reconciliation = _reconciliation()
    reconciliation["allowed"] = False

    result = _evaluate(demo_reconciliation=reconciliation)

    assert result["allowed"] is False
    assert promotion.REASON_RECONCILIATION_FAILED in result["blocked_reasons"]


def test_live_broker_sensitive_and_submit_flags_block() -> None:
    cases = (
        ("account_id", "101-222-333333-001", promotion.REASON_ACCOUNT_ID_PRESENT),
        ("credentials_loaded", True, promotion.REASON_CREDENTIALS_LOADED),
        ("live_trading_enabled", True, promotion.REASON_LIVE_TRADING_ENABLED),
        ("broker_write_enabled", True, promotion.REASON_BROKER_WRITE_ENABLED),
        ("order_submit_enabled", True, promotion.REASON_ORDER_SUBMIT_ENABLED),
        ("network_submit_enabled", True, promotion.REASON_NETWORK_SUBMIT_ENABLED),
        ("requested_action", "submit broker order", promotion.REASON_REQUESTED_LIVE_OR_BROKER_ACTION),
    )
    for field, value, reason in cases:
        replay = _replay()
        replay[field] = value
        result = _evaluate(session_replay=replay)
        assert result["allowed"] is False
        assert reason in result["blocked_reasons"]


def test_safety_dict_denies_execution_capabilities() -> None:
    result = _evaluate()

    assert result["safety"]["paper_only"] is True
    assert result["safety"]["demo_promotion_only"] is True
    assert result["safety"]["broker_write"] is False
    assert result["safety"]["live_trading"] is False
    assert result["safety"]["credentials"] is False
    assert result["safety"]["real_orders"] is False
    assert result["safety"]["network_submit"] is False


def test_blocked_reasons_are_deterministic() -> None:
    result = _evaluate(session_replay={}, evidence_ledger={})

    assert result["blocked_reasons"][:4] == [
        promotion.REASON_MISSING_REPLAY,
        promotion.REASON_MISSING_EVIDENCE,
        promotion.REASON_TRADE_COUNT_LOW,
        promotion.REASON_SESSION_COUNT_LOW,
    ]


def test_source_scan_has_no_broker_network_filesystem_or_sensitive_access() -> None:
    source = inspect.getsource(promotion).lower()
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
