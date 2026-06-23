import json
from pathlib import Path

from automation.forex_engine import micro_batch_campaign_ladder_v1 as ladder


def campaign(**overrides):
    payload = {
        "campaign_id": "CAMP-001",
        "micro_execution_ids": [f"MICRO-{index:03d}" for index in range(1, 13)],
        "strategy_id": "STRATEGY-001",
        "candidate_id": "CANDIDATE-001",
        "instrument": "EUR_USD",
        "side": "BUY",
        "start_time": "2026-06-23T00:00:00Z",
        "end_time": "2026-06-23T01:00:00Z",
        "gross_pl": 75.0,
        "net_pl": 52.0,
        "return_percent": 52.0,
        "max_drawdown": 4.0,
        "win_count": 9,
        "loss_count": 2,
        "breakeven_count": 1,
        "average_r": 1.8,
        "profit_factor": 2.7,
        "fees": 1.0,
        "spread": 0.8,
        "slippage": 0.2,
        "stop_loss_compliance": True,
        "take_profit_compliance": True,
        "risk_governor_state": "PASS",
        "broker_proof_state": "CURRENT",
        "reconciliation_state": "RECONCILED",
        "evidence_path": "Reports/forex_delivery/SANITIZED_CAMPAIGN_EVIDENCE.md",
        "proof_mode": "PAPER",
    }
    payload.update(overrides)
    return payload


def test_missing_campaigns_are_planning_only_and_safe():
    result = ladder.run_micro_batch_campaign_ladder()

    assert result["campaign_count"] == 0
    assert result["micro_execution_count"] == 0
    assert result["classifications"]["CAMPAIGN_TARGET_STATUS"] == ladder.CAMPAIGN_TARGET_NOT_MET
    assert result["classifications"]["PROFIT_PROOF_STATUS"] == ladder.PROFIT_TARGET_PLANNING_ONLY
    assert result["safety_summary"]["network_call_performed"] is False
    assert result["safety_summary"]["broker_api_called"] is False


def test_campaign_with_12_executions_reports_campaign_and_micro_counts():
    result = ladder.run_micro_batch_campaign_ladder({"campaigns": [campaign()]})

    assert result["campaign_count"] == 1
    assert result["micro_execution_count"] == 12
    assert result["classifications"]["CAMPAIGN_TARGET_STATUS"] == ladder.CAMPAIGN_50_PERCENT_REACHED
    assert result["classifications"]["PROFIT_PROOF_STATUS"] == ladder.PROFIT_TARGET_PAPER_ONLY
    assert result["profit_doctrine"]["campaign_count_visible"] is True
    assert result["profit_doctrine"]["micro_execution_count_visible"] is True


def test_campaign_with_99_executions_is_supported():
    payload = campaign(
        campaign_id="CAMP-099",
        micro_execution_ids=[f"MICRO-{index:03d}" for index in range(1, 100)],
        return_percent=25.0,
    )

    result = ladder.run_micro_batch_campaign_ladder({"campaigns": [payload]})

    assert result["micro_execution_count"] == 99
    assert result["campaigns"][0]["execution_count_supported"] is True
    assert result["classifications"]["CAMPAIGN_TARGET_STATUS"] == ladder.CAMPAIGN_25_PERCENT_REACHED


def test_50_percent_target_remains_evidence_gated_when_proof_is_incomplete():
    payload = campaign(broker_proof_state="MISSING", reconciliation_state="MISSING")

    result = ladder.run_micro_batch_campaign_ladder({"campaigns": [payload]})

    assert result["classifications"]["CAMPAIGN_TARGET_STATUS"] == ladder.CAMPAIGN_50_PERCENT_REACHED
    assert "CAMP-001:50_percent_target_requires_complete_evidence" in result["blocked_reasons"]
    assert result["target_evidence"]["evidence_ready_50_percent_campaigns"] == 0


def test_100_percent_target_does_not_prove_repeatability_from_one_campaign():
    result = ladder.run_micro_batch_campaign_ladder({"campaigns": [campaign(return_percent=120.0)]})

    assert result["classifications"]["CAMPAIGN_TARGET_STATUS"] == ladder.CAMPAIGN_100_PERCENT_REACHED
    assert result["classifications"]["REPEATABILITY_STATUS"] == ladder.REPEATABILITY_CANDIDATE
    assert result["target_evidence"]["evidence_ready_50_percent_campaigns"] == 1


def test_two_proven_50_percent_campaigns_can_prove_repeatability():
    result = ladder.run_micro_batch_campaign_ladder(
        {
            "campaigns": [
                campaign(campaign_id="CAMP-001"),
                campaign(campaign_id="CAMP-002", micro_execution_ids=[f"C2-MICRO-{index:03d}" for index in range(1, 13)]),
            ]
        }
    )

    assert result["classifications"]["REPEATABILITY_STATUS"] == ladder.REPEATABILITY_PROVEN
    assert result["target_evidence"]["evidence_ready_50_percent_campaigns"] == 2


def test_credentials_account_ids_and_broker_order_ids_are_redacted():
    payload = campaign(account_id="123456", api_key="EXAMPLE_LEAKME_API_KEY", broker_order_id="ORDER-1")

    result = ladder.run_micro_batch_campaign_ladder({"campaigns": [payload]})
    serialized = json.dumps(result, sort_keys=True)

    assert "123456" not in serialized
    assert "EXAMPLE_LEAKME_API_KEY" not in serialized
    assert "ORDER-1" not in serialized
    assert result["sanitization"]["sensitive_input_rejected_or_redacted"] is True


def test_write_reports_only_writes_allowed_paths(monkeypatch, tmp_path):
    reports = tmp_path / "Reports" / "forex_delivery"
    monkeypatch.setattr(ladder, "REPORTS_DIR", reports)
    monkeypatch.setattr(
        ladder,
        "REPORT_PATHS",
        {
            "campaign_ladder": reports / "AIOS_FOREX_MICRO_BATCH_CAMPAIGN_LADDER_V1.md",
            "target_50": reports / "AIOS_FOREX_50_PERCENT_CAMPAIGN_TARGET_V1.md",
            "target_100": reports / "AIOS_FOREX_100_PERCENT_REPEATABILITY_TARGET_V1.md",
        },
    )

    result = ladder.run_micro_batch_campaign_ladder({"campaigns": [campaign()]}, write_reports=True)
    written_names = {Path(path).name for path in result["reports"]["written"]}

    assert written_names == {path.name for path in ladder.REPORT_PATHS.values()}

