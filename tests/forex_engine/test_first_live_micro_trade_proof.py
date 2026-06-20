from __future__ import annotations

import inspect

from automation.forex_engine import first_live_micro_trade_proof as proof


def _readiness() -> dict:
    return {"allowed": True, "live_ready": True, "kill_switch_ok": True, "rollback_required": True}


def _promotion() -> dict:
    return {"allowed": True, "demo_promotion_ready": True}


def _runner() -> dict:
    return {"allowed": True, "mode": "DEMO_RUN_PLAN_ONLY"}


def _reconciliation() -> dict:
    return {"allowed": True, "matched": True, "match_score": 1.0}


def _limits() -> dict:
    return {
        "micro_trade_size_cap": 1.0,
        "max_micro_trade_size_cap": 1.0,
        "max_risk_pct": 0.25,
        "kill_switch_proof": True,
        "rollback_plan": True,
    }


def _approval() -> dict:
    return {"approved": True, "kill_switch_verified": True, "rollback_verified": True}


def _build(**overrides) -> dict:
    payload = {
        "live_readiness_review": _readiness(),
        "paper_to_demo_promotion": _promotion(),
        "demo_multi_trade_runner": _runner(),
        "demo_reconciliation": _reconciliation(),
        "risk_limits": _limits(),
        "human_approval_record": _approval(),
    }
    payload.update(overrides)
    return proof.build_first_live_micro_trade_proof(**payload)


def test_default_blocks() -> None:
    result = proof.build_first_live_micro_trade_proof({}, {}, {}, {}, {}, {})

    assert result["allowed"] is False
    assert result["decision"] == proof.DECISION_PROOF_ONLY
    assert result["proof_complete"] is False
    assert proof.REASON_HUMAN_APPROVAL_MISSING in result["blocked_reasons"]
    assert proof.REASON_MISSING_EVIDENCE in result["blocked_reasons"]


def test_human_approval_required() -> None:
    result = _build(human_approval_record={})

    assert result["allowed"] is False
    assert result["proof_complete"] is False
    assert proof.REASON_HUMAN_APPROVAL_MISSING in result["blocked_reasons"]


def test_proof_complete_still_does_not_enable_execution() -> None:
    result = _build()

    assert result["allowed"] is False
    assert result["decision"] == proof.DECISION_REQUIRES_HUMAN_APPROVAL
    assert result["proof_complete"] is True
    assert result["live_trade_allowed"] is False
    assert result["broker_submit_allowed"] is False
    assert result["blocked_reasons"] == []


def test_missing_kill_switch_blocks() -> None:
    limits = _limits()
    limits["kill_switch_proof"] = False
    approval = _approval()
    approval["kill_switch_verified"] = False
    readiness = _readiness()
    readiness["kill_switch_ok"] = False

    result = _build(risk_limits=limits, human_approval_record=approval, live_readiness_review=readiness)

    assert result["proof_complete"] is False
    assert proof.REASON_KILL_SWITCH_MISSING in result["blocked_reasons"]


def test_missing_rollback_blocks() -> None:
    limits = _limits()
    limits["rollback_plan"] = False
    approval = _approval()
    approval["rollback_verified"] = False
    readiness = _readiness()
    readiness["rollback_required"] = False

    result = _build(risk_limits=limits, human_approval_record=approval, live_readiness_review=readiness)

    assert result["proof_complete"] is False
    assert proof.REASON_ROLLBACK_MISSING in result["blocked_reasons"]


def test_account_id_credential_live_and_order_submit_blockers() -> None:
    cases = (
        ("account_id", "101-222-333333-001", proof.REASON_ACCOUNT_ID_PRESENT),
        ("credentials_loaded", True, proof.REASON_CREDENTIALS_PRESENT),
        ("live_trading_enabled", True, proof.REASON_LIVE_TRADING_ENABLED),
        ("order_submit_enabled", True, proof.REASON_ORDER_SUBMIT_ENABLED),
        ("broker_write_enabled", True, proof.REASON_BROKER_WRITE_ENABLED),
        ("network_submit_enabled", True, proof.REASON_NETWORK_SUBMIT_ENABLED),
    )
    for field, value, reason in cases:
        readiness = _readiness()
        readiness[field] = value
        result = _build(live_readiness_review=readiness)
        assert result["proof_complete"] is False
        assert reason in result["blocked_reasons"]


def test_risk_cap_blockers() -> None:
    limits = _limits()
    limits["micro_trade_size_cap"] = 2.0
    limits["max_risk_pct"] = 2.5

    result = _build(risk_limits=limits)

    assert result["proof_complete"] is False
    assert proof.REASON_EXCESSIVE_RISK in result["blocked_reasons"]


def test_safety_dict() -> None:
    result = _build()

    assert result["safety"] == {
        "paper_only": True,
        "proof_only": True,
        "broker_write": False,
        "live_trading": False,
        "credentials": False,
        "real_orders": False,
        "network_submit": False,
    }


def test_deterministic_reasons() -> None:
    result = proof.build_first_live_micro_trade_proof({}, {}, {}, {}, {}, {})

    assert result["blocked_reasons"][:6] == [
        proof.REASON_HUMAN_APPROVAL_MISSING,
        proof.REASON_KILL_SWITCH_MISSING,
        proof.REASON_ROLLBACK_MISSING,
        proof.REASON_EXCESSIVE_RISK,
        proof.REASON_MISSING_EVIDENCE,
    ]


def test_source_scan_has_no_broker_network_filesystem_or_sensitive_access() -> None:
    source = inspect.getsource(proof).lower()
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
