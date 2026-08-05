from src.forex_delivery.readiness_consolidation import (
    build_readiness_consolidation_evidence,
    render_readiness_consolidation_report,
)


def test_consolidation_evidence_is_sanitized_and_non_executing():
    evidence = build_readiness_consolidation_evidence(
        now_utc="2026-08-05T00:00:00+00:00"
    )

    assert evidence["sanitized"] is True
    assert evidence["live_execution_allowed"] is False
    assert evidence["preflight_bundle"]["execution_requested"] is False
    assert evidence["preflight_bundle"]["order_executed"] is False
    assert evidence["preflight_bundle"]["broker_call_performed"] is False
    assert evidence["protected_command_package"]["command_released"] is False
    assert (
        evidence["post_trade_package"]["ledger_template_status"]
        == "SANITIZED_TEMPLATE_READY"
    )
    assert evidence["history_writeback_status"] in {
        "PAPER_HISTORY_WRITTEN",
        "PAPER_HISTORY_UNAVAILABLE",
    }
    assert evidence["remaining_blockers"]


def test_consolidation_report_contains_no_sensitive_markers():
    evidence = build_readiness_consolidation_evidence(
        now_utc="2026-08-05T00:00:00+00:00"
    )
    report = render_readiness_consolidation_report(evidence).lower()

    assert "live_execution_allowed" in report
    assert "api_token" not in report
    assert "oanda_" + "account_id" not in report
    assert "raw_" + "payload" not in report
    assert "bearer" + " " not in report
