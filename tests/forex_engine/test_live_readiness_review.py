from __future__ import annotations

import inspect

from automation.forex_engine import live_readiness_review as review


def _promotion() -> dict:
    return {"allowed": True, "demo_promotion_ready": True, "mode": "PAPER_TO_DEMO_PROMOTION_ONLY"}


def _runner() -> dict:
    return {"allowed": True, "mode": "DEMO_RUN_PLAN_ONLY", "selected_intents": [{"idempotency_key": "demo-map-1"}]}


def _reconciliation() -> dict:
    return {"allowed": True, "matched": True, "match_score": 1.0, "mode": "DEMO_RECONCILIATION_ONLY"}


def _replay() -> dict:
    return {"trade_count": 30, "session_count": 5, "max_drawdown_pct": 2.0, "risk_failures": []}


def _ledger() -> dict:
    return {"allowed": True, "validation_passed": True, "entries": [{"id": "evidence-1"}]}


def _risk() -> dict:
    return {"drawdown_pct": 2.0, "risk_failures": [], "risk_ok": True}


def _kill_switch() -> dict:
    return {"present": True, "verified": True}


def _evaluate(**overrides) -> dict:
    payload = {
        "paper_to_demo_promotion": _promotion(),
        "demo_multi_trade_runner": _runner(),
        "demo_reconciliation": _reconciliation(),
        "session_replay": _replay(),
        "evidence_ledger": _ledger(),
        "risk_metrics": _risk(),
        "kill_switch_proof": _kill_switch(),
        "human_approval": False,
        "limits": {"maximum_drawdown_pct": 5.0},
    }
    payload.update(overrides)
    return review.review_live_readiness(**payload)


def test_review_only_by_default() -> None:
    result = _evaluate()

    assert result["allowed"] is False
    assert result["decision"] == review.DECISION_REVIEW_ONLY
    assert result["live_ready"] is False
    assert result["approval_required"] is True
    assert review.REASON_HUMAN_APPROVAL_MISSING in result["blocked_reasons"]


def test_human_approval_required() -> None:
    result = _evaluate(human_approval=False)

    assert result["allowed"] is False
    assert result["blocked_reason"] == review.REASON_HUMAN_APPROVAL_MISSING
    assert result["next_safe_action"] == "continue_paper_demo_evidence_collection"


def test_mature_evidence_can_request_live_micro_review_only_with_approval() -> None:
    result = _evaluate(human_approval=True)

    assert result["allowed"] is True
    assert result["decision"] == review.DECISION_REQUIRES_HUMAN_APPROVAL
    assert result["live_ready"] is True
    assert result["readiness_score"] == 1.0
    assert result["paper_evidence_ok"] is True
    assert result["demo_evidence_ok"] is True
    assert result["reconciliation_ok"] is True
    assert result["risk_ok"] is True
    assert result["kill_switch_ok"] is True
    assert result["next_safe_action"] == "request_human_live_micro_trade_exception_review"


def test_missing_approval_blocks() -> None:
    result = _evaluate(human_approval=False)

    assert result["allowed"] is False
    assert review.REASON_HUMAN_APPROVAL_MISSING in result["blocked_reasons"]


def test_missing_kill_switch_blocks() -> None:
    result = _evaluate(human_approval=True, kill_switch_proof={})

    assert result["allowed"] is False
    assert review.REASON_KILL_SWITCH_PROOF_MISSING in result["blocked_reasons"]
    assert result["kill_switch_ok"] is False


def test_drawdown_blocks() -> None:
    risk = _risk()
    risk["drawdown_pct"] = 8.0

    result = _evaluate(human_approval=True, risk_metrics=risk)

    assert result["allowed"] is False
    assert review.REASON_DRAWDOWN_TOO_HIGH in result["blocked_reasons"]
    assert result["risk_ok"] is False


def test_risk_failure_blocks() -> None:
    risk = _risk()
    risk["risk_failures"] = ["spread_too_high"]

    result = _evaluate(human_approval=True, risk_metrics=risk)

    assert result["allowed"] is False
    assert review.REASON_RISK_FAILURES_UNRESOLVED in result["blocked_reasons"]
    assert result["risk_ok"] is False


def test_reconciliation_blocks() -> None:
    reconciliation = _reconciliation()
    reconciliation["matched"] = False
    reconciliation["match_score"] = 0.25

    result = _evaluate(human_approval=True, demo_reconciliation=reconciliation)

    assert result["allowed"] is False
    assert review.REASON_RECONCILIATION_MISSING in result["blocked_reasons"]
    assert result["reconciliation_ok"] is False


def test_credentials_account_id_live_and_order_submit_flags_block() -> None:
    cases = (
        ("credentials_loaded", True, review.REASON_CREDENTIALS_PRESENT),
        ("account_id", "101-222-333333-001", review.REASON_ACCOUNT_ID_PRESENT),
        ("live_trading_enabled", True, review.REASON_LIVE_TRADING_ENABLED),
        ("order_submit_enabled", True, review.REASON_ORDER_SUBMIT_ENABLED),
        ("broker_write_enabled", True, review.REASON_BROKER_WRITE_ENABLED),
        ("network_submit_enabled", True, review.REASON_NETWORK_SUBMIT_ENABLED),
    )
    for field, value, reason in cases:
        replay = _replay()
        replay[field] = value
        result = _evaluate(human_approval=True, session_replay=replay)
        assert result["allowed"] is False
        assert reason in result["blocked_reasons"]


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


def test_blocked_reasons_are_deterministic() -> None:
    result = _evaluate(
        paper_to_demo_promotion={},
        demo_multi_trade_runner={},
        demo_reconciliation={},
        session_replay={},
        evidence_ledger={},
        risk_metrics={"risk_failures": ["risk_blocked"]},
        kill_switch_proof={},
        human_approval=False,
    )

    assert result["blocked_reasons"][:6] == [
        review.REASON_HUMAN_APPROVAL_MISSING,
        review.REASON_PAPER_EVIDENCE_INSUFFICIENT,
        review.REASON_DEMO_EVIDENCE_INSUFFICIENT,
        review.REASON_RECONCILIATION_MISSING,
        review.REASON_RISK_FAILURES_UNRESOLVED,
        review.REASON_KILL_SWITCH_PROOF_MISSING,
    ]


def test_source_scan_has_no_broker_network_filesystem_or_sensitive_access() -> None:
    source = inspect.getsource(review).lower()
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
