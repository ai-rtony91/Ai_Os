from __future__ import annotations

from automation.forex_engine import forex_profit_repeatability_evidence_v1 as repeatability


def _evidence(sample_count: float = 20, min_sample_count: float = 20) -> dict:
    return {
        "sample_count": sample_count,
        "min_sample_count": min_sample_count,
        "expectancy_positive": True,
        "profit_factor": 1.9,
        "min_profit_factor": 1.4,
        "max_drawdown_pct": 0.02,
        "max_allowed_drawdown_pct": 0.03,
        "walk_forward_gate_cleared": True,
        "out_of_sample_passed": True,
        "daily_review_count": 1,
        "weekly_review_count": 1,
        "monthly_review_count": 1,
        "yearly_review_ready": True,
        "guaranteed_profit_claimed": False,
        "fixed_return_promised": False,
    }


def _result(payload: dict | None = None) -> dict:
    return repeatability.evaluate_forex_profit_repeatability_evidence_v1(payload)


def test_empty_payload_is_incomplete():
    result = _result({})
    assert result["status"] == repeatability.INCOMPLETE_INPUTS


def test_insufficient_sample_continues_demo_proof_capture():
    result = _result({"evidence": _evidence(sample_count=2, min_sample_count=20)})
    assert result["status"] == repeatability.CONTINUE_DEMO_PROOF_CAPTURE


def test_negative_expectancy_blocks():
    bad = _evidence()
    bad["expectancy_positive"] = False
    result = _result({"evidence": bad})
    assert result["status"] == repeatability.BLOCKED_BY_NEGATIVE_EXPECTANCY


def test_drawdown_above_limit_is_blocked():
    bad = _evidence()
    bad["max_drawdown_pct"] = 0.12
    bad["max_allowed_drawdown_pct"] = 0.05
    result = _result({"evidence": bad})
    assert result["status"] == repeatability.BLOCKED_BY_DRAWDOWN


def test_unrealistic_return_claim_is_blocked():
    bad = _evidence()
    bad["fixed_return_promised"] = True
    result = _result({"evidence": bad})
    assert result["status"] == repeatability.BLOCKED_BY_UNREALISTIC_RETURN_CLAIM


def test_ready_status_returns_scored_repeatability():
    result = _result({"evidence": _evidence()})
    assert result["status"] == repeatability.REPEATABILITY_EVIDENCE_READY_FOR_REVIEW
    assert result["ready"] is True
    assert result["ready_for_live_micro_review"] is True
    assert result["repeatability_score"] >= 70


def test_sensitive_data_is_blocked():
    evidence = _evidence()
    evidence["api_key"] = "sk-very-sensitive"
    result = _result({"evidence": evidence})
    rendered = str(result).lower()
    assert result["status"] == repeatability.BLOCKED_BY_SENSITIVE_DATA
    assert "sk-very-sensitive" not in rendered


def test_banking_focus_is_blocked():
    evidence = _evidence()
    evidence["deposit"] = 100
    result = _result({"evidence": evidence})
    assert result["status"] == repeatability.BLOCKED_BY_BANKING_FOCUS


def test_hard_false_fields_remain_false():
    result = _result({"evidence": _evidence()})
    assert result["status"] == repeatability.REPEATABILITY_EVIDENCE_READY_FOR_REVIEW
    for field in (
        "live_trade_executed",
        "live_execution_authorized",
        "demo_trade_executed_by_this_module",
        "broker_api_called",
        "credential_read",
        "credential_stored",
        "api_key_stored",
        "master_password_used",
        "vault_password_used",
        "money_moved",
        "bank_access_used",
        "scheduler_created",
        "daemon_created",
        "webhook_created",
        "dashboard_runtime_created",
        "banking_work_built",
        "withdrawal_work_built",
        "transfer_work_built",
    ):
        assert result[field] is False
        assert result["safety"][field] is False
