from __future__ import annotations

import inspect

from automation.forex_engine import live_multi_trade_expansion_gate as gate


def _proof() -> dict:
    return {"proof_complete": True, "kill_switch_proof": True, "rollback_plan": True}


def _readiness() -> dict:
    return {"live_ready": True, "kill_switch_ok": True, "rollback_required": True}


def _promotion() -> dict:
    return {"allowed": True, "demo_promotion_ready": True}


def _runner() -> dict:
    return {"allowed": True, "mode": "DEMO_RUN_PLAN_ONLY"}


def _reconciliation() -> dict:
    return {"allowed": True, "matched": True, "match_score": 1.0}


def _replay() -> dict:
    return {"session_count": 6, "trade_count": 40, "max_drawdown_pct": 2.0, "risk_failures": []}


def _limits() -> dict:
    return {
        "max_live_trades_requested": 2,
        "max_live_trades_allowed_review_only": 2,
        "risk_cap": 0.5,
        "max_risk_cap": 1.0,
        "maximum_drawdown_pct": 5.0,
        "kill_switch_proof": True,
        "rollback_plan": True,
    }


def _approval() -> dict:
    return {"approved": True, "kill_switch_verified": True, "rollback_verified": True}


def _evaluate(**overrides) -> dict:
    payload = {
        "first_live_micro_trade_proof": _proof(),
        "live_readiness_review": _readiness(),
        "paper_to_demo_promotion": _promotion(),
        "demo_multi_trade_runner": _runner(),
        "demo_reconciliation": _reconciliation(),
        "session_replay": _replay(),
        "risk_limits": _limits(),
        "human_approval_record": _approval(),
    }
    payload.update(overrides)
    return gate.evaluate_live_multi_trade_expansion_gate(**payload)


def test_default_blocks() -> None:
    result = gate.evaluate_live_multi_trade_expansion_gate({}, {}, {}, {}, {}, {}, {}, {})

    assert result["allowed"] is False
    assert result["decision"] == gate.DECISION_REVIEW_ONLY
    assert result["expansion_ready"] is False
    assert gate.REASON_HUMAN_APPROVAL_MISSING in result["blocked_reasons"]


def test_human_approval_required() -> None:
    result = _evaluate(human_approval_record={})

    assert result["allowed"] is False
    assert gate.REASON_HUMAN_APPROVAL_MISSING in result["blocked_reasons"]


def test_proof_required() -> None:
    result = _evaluate(first_live_micro_trade_proof={})

    assert result["allowed"] is False
    assert gate.REASON_FIRST_LIVE_MICRO_PROOF_MISSING in result["blocked_reasons"]


def test_live_readiness_required() -> None:
    result = _evaluate(live_readiness_review={})

    assert result["allowed"] is False
    assert gate.REASON_LIVE_READINESS_REVIEW_MISSING in result["blocked_reasons"]


def test_kill_switch_required() -> None:
    result = _evaluate(first_live_micro_trade_proof={"proof_complete": True}, live_readiness_review={"live_ready": True}, risk_limits={"risk_cap": 0.5})

    assert result["allowed"] is False
    assert gate.REASON_KILL_SWITCH_MISSING in result["blocked_reasons"]


def test_rollback_required() -> None:
    proof = _proof()
    proof["rollback_plan"] = False
    readiness = _readiness()
    readiness["rollback_required"] = False
    approval = _approval()
    approval["rollback_verified"] = False
    limits = _limits()
    limits["rollback_plan"] = False

    result = _evaluate(first_live_micro_trade_proof=proof, live_readiness_review=readiness, human_approval_record=approval, risk_limits=limits)

    assert result["allowed"] is False
    assert gate.REASON_ROLLBACK_MISSING in result["blocked_reasons"]


def test_reconciliation_required() -> None:
    result = _evaluate(demo_reconciliation={"allowed": True, "matched": False, "match_score": 0.5})

    assert result["allowed"] is False
    assert gate.REASON_RECONCILIATION_UNRESOLVED in result["blocked_reasons"]


def test_risk_cap_blocks() -> None:
    limits = _limits()
    limits["risk_cap"] = 2.0

    result = _evaluate(risk_limits=limits)

    assert result["allowed"] is False
    assert gate.REASON_EXCESSIVE_RISK_CAP in result["blocked_reasons"]


def test_max_live_trade_count_blocks() -> None:
    limits = _limits()
    limits["max_live_trades_requested"] = 3
    limits["max_live_trades_allowed_review_only"] = 2

    result = _evaluate(risk_limits=limits)

    assert result["allowed"] is False
    assert gate.REASON_EXCESSIVE_LIVE_TRADE_COUNT in result["blocked_reasons"]


def test_sensitive_and_execution_flags_block() -> None:
    cases = (
        ("credentials_loaded", True, gate.REASON_CREDENTIALS_PRESENT),
        ("account_id", "101-222-333333-001", gate.REASON_ACCOUNT_ID_PRESENT),
        ("live_trading_enabled", True, gate.REASON_LIVE_TRADING_ENABLED),
        ("order_submit_enabled", True, gate.REASON_ORDER_SUBMIT_ENABLED),
        ("broker_write_enabled", True, gate.REASON_BROKER_WRITE_ENABLED),
        ("network_submit_enabled", True, gate.REASON_NETWORK_SUBMIT_ENABLED),
    )
    for field, value, reason in cases:
        proof = _proof()
        proof[field] = value
        result = _evaluate(first_live_micro_trade_proof=proof)
        assert result["allowed"] is False
        assert reason in result["blocked_reasons"]


def test_complete_review_keeps_execution_disabled() -> None:
    result = _evaluate()

    assert result["allowed"] is True
    assert result["decision"] == gate.DECISION_REQUIRES_HUMAN_APPROVAL
    assert result["expansion_ready"] is True
    assert result["live_multi_trade_allowed"] is False
    assert result["broker_submit_allowed"] is False


def test_safety_dict() -> None:
    result = _evaluate()

    assert result["safety"] == {
        "paper_only": True,
        "review_only": True,
        "broker_write": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_submit": False,
    }


def test_deterministic_blocked_reasons() -> None:
    result = gate.evaluate_live_multi_trade_expansion_gate({}, {}, {}, {}, {}, {}, {}, {})

    assert result["blocked_reasons"][:6] == [
        gate.REASON_HUMAN_APPROVAL_MISSING,
        gate.REASON_FIRST_LIVE_MICRO_PROOF_MISSING,
        gate.REASON_LIVE_READINESS_REVIEW_MISSING,
        gate.REASON_KILL_SWITCH_MISSING,
        gate.REASON_ROLLBACK_MISSING,
        gate.REASON_RECONCILIATION_UNRESOLVED,
    ]


def test_source_scan_has_no_broker_network_filesystem_or_sensitive_access() -> None:
    source = inspect.getsource(gate).lower()
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
