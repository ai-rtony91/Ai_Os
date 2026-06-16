from __future__ import annotations

from pathlib import Path

import pytest

from automation.forex_engine import broker_paper_sandbox_readiness
from automation.forex_engine import broker_paper_adapter_stub_contract
from automation.forex_engine import broker_paper_dryrun_intent_ledger
from automation.forex_engine import broker_paper_dryrun_risk_governor
from automation.forex_engine import broker_paper_presecurity_gate
from automation.forex_engine import low_vol_edge_redesign
from automation.forex_engine import oos_expansion
from automation.forex_engine import oos_repair
from automation.forex_engine import paper_forward_evidence_v2
from automation.forex_engine import stress_repair


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "forex_engine" / "broker_paper_sandbox_readiness.py"
DEMO_PATH = REPO_ROOT / "automation" / "forex_engine" / "run_broker_paper_sandbox_readiness_demo.py"
ALLOWED_STATUSES = {
    "NOT_READY",
    "WATCHLIST",
    "CONTRACT_READY_FOR_PROTECTED_BROKER_PAPER_SANDBOX_PACKET",
}


def _strong_contract_inputs() -> tuple[dict[str, object], dict[str, object], dict[str, object]]:
    bundle = paper_forward_evidence_v2.build_paper_forward_evidence_v2()
    evidence = dict(bundle)
    evidence["blockers"] = []
    evidence["classification"] = "PAPER_FORWARD_READY"
    evidence["stress_repair"] = {
        "repaired_classification": "PAPER_FORWARD_READY",
        "stress_repair_status": "PAPER_FORWARD_READY",
        "blockers": [],
        "live_ready": False,
        "protected_gate_required": True,
    }
    evidence["expanded_oos"] = {
        "classification": "PAPER_FORWARD_READY",
        "heldout_consistency_pct": 100.0,
        "blockers": [],
        "live_ready": False,
        "protected_gate_required": True,
    }
    evidence["oos_repair"] = {
        "repaired_classification": "PAPER_FORWARD_READY",
        "classification": "PAPER_FORWARD_READY",
        "original_max_degradation_pct": 45.0,
        "repaired_max_degradation_pct": 30.0,
        "degradation_improvement_pct": 15.0,
        "repair_plan": {"max_allowed_degradation_pct": 35.0},
        "blockers": [],
        "broker_paper_ready": False,
        "broker_paper_contract_ready": False,
        "live_ready": False,
        "protected_gate_required": True,
    }
    evidence.pop("low_vol_edge_redesign", None)
    evidence.pop("low_vol_edge_summary", None)

    stress_oos = dict(evidence["combined_stress_oos_gate"])
    stress_oos.update(
        {
            "stress_classification": "PAPER_FORWARD_READY",
            "oos_classification": "PAPER_FORWARD_READY",
            "combined_classification": "PAPER_FORWARD_READY",
            "heldout_consistency_pct": 100.0,
            "blockers": [],
        }
    )

    risk_governor = dict(evidence["risk_governor"])
    risk_governor.update({"classification": "PAPER_FORWARD_READY", "blockers": []})
    return evidence, stress_oos, risk_governor


def test_default_policy_exists_and_preserves_contract_boundaries() -> None:
    policy = broker_paper_sandbox_readiness.default_broker_paper_sandbox_readiness_policy()

    assert policy["minimum_fixture_count"] >= 9
    assert policy["minimum_regime_count"] >= 7
    assert policy["minimum_total_intents"] >= 50
    assert policy["minimum_simulated_ledger_entries"] >= 50
    assert policy["minimum_consistency_pct"] >= 70
    assert policy["minimum_oos_consistency_pct"] >= 70
    assert policy["future_broker_paper_packet_requires_approval"] is True
    assert policy["live_trade_ready_must_be_false"] is True
    assert policy["real_order_ready_must_be_false"] is True
    assert policy["broker_integration_active_must_be_false"] is True
    assert policy["credentials_required_now_must_be_false"] is True
    assert policy["protected_gate_required_must_be_true"] is True
    assert policy["presecurity_gate_landed"] is False


def test_default_readiness_result_is_watchlist_and_contract_only() -> None:
    result = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness()

    assert result["mode"] == "PAPER_ONLY_CONTRACT"
    assert result["readiness_status"] == "WATCHLIST"
    assert result["readiness_status"] in ALLOWED_STATUSES
    assert result["readiness_status"] != "LIVE_READY"
    assert result["broker_paper_sandbox_contract_ready"] is False
    assert result["stress_repair_status"] in {"WATCHLIST", "PAPER_FORWARD_READY", "not_run"}
    assert result["stress_repair_classification"] in {"WATCHLIST", "PAPER_FORWARD_READY", "not_run"}
    assert result["expanded_oos_status"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY", "not_run"}
    assert result["expanded_oos_classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY", "not_run"}
    assert result["oos_repair_classification"] in {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY", "not_run"}
    assert result["presecurity_gate_classification"] in {"FAIL", "WATCHLIST", "PRESECURITY_READY", "not_run"}
    assert result["broker_paper_stub_contract_classification"] in {
        "FAIL",
        "WATCHLIST",
        "STUB_CONTRACT_READY",
        "not_run",
    }
    assert result["broker_paper_stub_contract_ready"] is False
    assert result["broker_paper_dryrun_ledger_classification"] in {
        "FAIL",
        "WATCHLIST",
        "DRYRUN_LEDGER_READY",
        "not_run",
    }
    assert result["broker_paper_dryrun_ledger_ready"] is False
    assert result["dryrun_ledger_records"] >= 0
    assert result["dryrun_ledger_accepted"] >= 0
    assert result["dryrun_ledger_rejected"] >= 0
    assert result["broker_paper_dryrun_risk_governor_classification"] in {
        "FAIL",
        "WATCHLIST",
        "DRYRUN_RISK_GOVERNOR_READY",
        "not_run",
    }
    assert result["broker_paper_dryrun_risk_governor_ready"] is False
    assert result["dryrun_risk_records"] >= 0
    assert result["dryrun_risk_accepted"] >= 0
    assert result["dryrun_risk_rejected"] >= 0
    assert result["aggregate_max_loss_usd"] >= 0.0
    assert result["max_daily_loss_usd"] >= 0.0
    assert result["kill_switch_armed"] in {True, False}
    assert result["credential_boundary_required"] is True
    assert result["kill_switch_required"] is True
    assert result["max_loss_guard_required"] is True
    assert result["audit_log_required"] is True
    assert result["live_trade_ready"] is False
    assert result["real_order_ready"] is False
    assert result["broker_integration_active"] is False
    assert result["credentials_required_now"] is False
    assert result["protected_gate_required"] is True
    assert result["future_broker_paper_packet_requires_approval"] is True
    assert result["security_gate_required_before_broker_paper"] is True
    assert result["required_security_packet"] == "PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1"
    assert result["blockers"]


def test_fail_evidence_returns_not_ready() -> None:
    evidence, stress_oos, risk_governor = _strong_contract_inputs()
    stress_oos["combined_classification"] = "FAIL"

    result = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness(
        evidence=evidence,
        stress_oos=stress_oos,
        risk_governor=risk_governor,
        expanded_oos=evidence["expanded_oos"],
        oos_repair=evidence["oos_repair"],
    )

    assert result["readiness_status"] == "NOT_READY"
    assert result["broker_paper_sandbox_contract_ready"] is False
    assert "gate_failed:combined_stress_oos_classification" in result["blockers"]


def test_strong_evidence_stays_blocked_when_presecurity_gate_is_missing() -> None:
    evidence, stress_oos, risk_governor = _strong_contract_inputs()

    result = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness(
        evidence=evidence,
        stress_oos=stress_oos,
        risk_governor=risk_governor,
        expanded_oos=evidence["expanded_oos"],
        oos_repair=evidence["oos_repair"],
    )

    assert result["readiness_status"] == "WATCHLIST"
    assert result["broker_paper_sandbox_contract_ready"] is False
    assert result["broker_paper_contract_ready"] is False
    assert result["presecurity_gate_classification"] == "not_run"
    assert "gate_watchlist:presecurity_gate_present" in result["blockers"]
    assert result["live_trade_ready"] is False
    assert result["real_order_ready"] is False
    assert result["broker_integration_active"] is False
    assert result["credentials_required_now"] is False
    assert result["protected_gate_required"] is True
    assert result["security_gate_required_before_broker_paper"] is True


def test_presecurity_ready_routes_only_to_adapter_stub_contract() -> None:
    evidence, stress_oos, risk_governor = _strong_contract_inputs()
    presecurity = broker_paper_presecurity_gate.evaluate_broker_paper_presecurity_gate()

    result = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness(
        evidence=evidence,
        stress_oos=stress_oos,
        risk_governor=risk_governor,
        stress_repair=evidence["stress_repair"],
        expanded_oos=evidence["expanded_oos"],
        oos_repair=evidence["oos_repair"],
        presecurity_gate=presecurity,
    )

    assert result["readiness_status"] == "WATCHLIST"
    assert result["presecurity_gate_classification"] == "PRESECURITY_READY"
    assert result["adapter_stub_contract_ready"] is False
    assert result["broker_paper_stub_contract_ready"] is False
    assert result["next_safe_packet"] == "PKT-AIOS-BROKER-PAPER-SANDBOX-ADAPTER-STUB-CONTRACT"
    assert "gate_watchlist:broker_paper_stub_contract_present" in result["blockers"]
    assert result["broker_paper_sandbox_contract_ready"] is False
    assert result["broker_paper_orders_allowed"] is False
    assert result["live_orders_allowed"] is False
    assert result["live_trade_ready"] is False


def test_stub_contract_ready_routes_only_to_dryrun_intent_ledger() -> None:
    evidence, stress_oos, risk_governor = _strong_contract_inputs()
    presecurity = broker_paper_presecurity_gate.evaluate_broker_paper_presecurity_gate()
    stub = broker_paper_adapter_stub_contract.simulate_broker_paper_stub_adapter(
        {
            "symbol": "EURUSD_FAKE",
            "side": "buy",
            "quantity_units": 1000,
            "order_type": "market_stub",
            "stop_loss_pips": 8.0,
            "take_profit_pips": 12.0,
            "max_loss_usd": 10.0,
            "dry_run": True,
            "approved_by_operator": True,
        }
    )

    result = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness(
        evidence=evidence,
        stress_oos=stress_oos,
        risk_governor=risk_governor,
        stress_repair=evidence["stress_repair"],
        expanded_oos=evidence["expanded_oos"],
        oos_repair=evidence["oos_repair"],
        presecurity_gate=presecurity,
        adapter_stub_contract=stub,
    )

    assert result["readiness_status"] == "WATCHLIST"
    assert result["presecurity_gate_classification"] == "PRESECURITY_READY"
    assert result["broker_paper_stub_contract_classification"] == "STUB_CONTRACT_READY"
    assert result["adapter_stub_contract_ready"] is True
    assert result["broker_paper_stub_contract_ready"] is True
    assert result["broker_paper_dryrun_ledger_classification"] == "not_run"
    assert result["broker_paper_dryrun_ledger_ready"] is False
    assert result["next_safe_packet"] == "PKT-AIOS-BROKER-PAPER-DRYRUN-INTENT-LEDGER-V1"
    assert "gate_watchlist:broker_paper_dryrun_ledger_present" in result["blockers"]
    assert result["broker_paper_sandbox_contract_ready"] is False
    assert result["broker_paper_contract_ready"] is False
    assert result["broker_paper_orders_allowed"] is False
    assert result["network_api_allowed"] is False
    assert result["credentials_allowed"] is False
    assert result["live_orders_allowed"] is False
    assert result["live_trade_ready"] is False


def test_dryrun_intent_ledger_ready_routes_only_to_dryrun_risk_governor() -> None:
    evidence, stress_oos, risk_governor = _strong_contract_inputs()
    presecurity = broker_paper_presecurity_gate.evaluate_broker_paper_presecurity_gate()
    stub = broker_paper_adapter_stub_contract.simulate_broker_paper_stub_adapter(
        {
            "symbol": "EURUSD_FAKE",
            "side": "buy",
            "quantity_units": 1000,
            "order_type": "market_stub",
            "stop_loss_pips": 8.0,
            "take_profit_pips": 12.0,
            "max_loss_usd": 10.0,
            "dry_run": True,
            "approved_by_operator": True,
        }
    )
    ledger = broker_paper_dryrun_intent_ledger.replay_dryrun_intent_batch()

    result = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness(
        evidence=evidence,
        stress_oos=stress_oos,
        risk_governor=risk_governor,
        stress_repair=evidence["stress_repair"],
        expanded_oos=evidence["expanded_oos"],
        oos_repair=evidence["oos_repair"],
        presecurity_gate=presecurity,
        adapter_stub_contract=stub,
        dryrun_intent_ledger=ledger,
    )

    assert result["readiness_status"] == "WATCHLIST"
    assert result["adapter_stub_contract_ready"] is True
    assert result["broker_paper_stub_contract_ready"] is True
    assert result["broker_paper_dryrun_ledger_classification"] == "DRYRUN_LEDGER_READY"
    assert result["broker_paper_dryrun_ledger_ready"] is True
    assert result["dryrun_ledger_records"] == 2
    assert result["dryrun_ledger_accepted"] == 1
    assert result["dryrun_ledger_rejected"] == 1
    assert result["broker_paper_dryrun_risk_governor_classification"] == "not_run"
    assert result["broker_paper_dryrun_risk_governor_ready"] is False
    assert result["next_safe_packet"] == "PKT-AIOS-BROKER-PAPER-DRYRUN-RISK-GOVERNOR-V1"
    assert "gate_watchlist:broker_paper_dryrun_risk_governor_present" in result["blockers"]
    assert result["broker_paper_sandbox_contract_ready"] is False
    assert result["broker_paper_contract_ready"] is False
    assert result["broker_paper_orders_allowed"] is False
    assert result["network_api_allowed"] is False
    assert result["credentials_allowed"] is False
    assert result["broker_sdk_allowed"] is False
    assert result["live_orders_allowed"] is False
    assert result["live_trade_ready"] is False


def test_dryrun_risk_governor_ready_routes_only_to_dryrun_replay_harness() -> None:
    evidence, stress_oos, risk_governor = _strong_contract_inputs()
    presecurity = broker_paper_presecurity_gate.evaluate_broker_paper_presecurity_gate()
    stub = broker_paper_adapter_stub_contract.simulate_broker_paper_stub_adapter(
        {
            "symbol": "EURUSD_FAKE",
            "side": "buy",
            "quantity_units": 500,
            "order_type": "market_stub",
            "stop_loss_pips": 8.0,
            "take_profit_pips": 12.0,
            "max_loss_usd": 1.0,
            "dry_run": True,
            "approved_by_operator": True,
        }
    )
    ledger = broker_paper_dryrun_intent_ledger.replay_dryrun_intent_batch(
        [
            {
                "symbol": "EURUSD_FAKE",
                "side": "buy",
                "quantity_units": 500,
                "order_type": "market_stub",
                "stop_loss_pips": 8.0,
                "take_profit_pips": 12.0,
                "max_loss_usd": 1.0,
                "dry_run": True,
                "approved_by_operator": True,
            },
            {
                "symbol": "BTCUSD",
                "side": "buy",
                "quantity_units": 500,
                "order_type": "market_stub",
                "stop_loss_pips": None,
                "take_profit_pips": 12.0,
                "max_loss_usd": 3.5,
                "dry_run": True,
                "approved_by_operator": True,
            },
        ]
    )
    dryrun_risk = broker_paper_dryrun_risk_governor.evaluate_dryrun_ledger_risk(ledger)

    result = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness(
        evidence=evidence,
        stress_oos=stress_oos,
        risk_governor=risk_governor,
        stress_repair=evidence["stress_repair"],
        expanded_oos=evidence["expanded_oos"],
        oos_repair=evidence["oos_repair"],
        presecurity_gate=presecurity,
        adapter_stub_contract=stub,
        dryrun_intent_ledger=ledger,
        dryrun_risk_governor=dryrun_risk,
    )

    assert result["readiness_status"] == "CONTRACT_READY_FOR_PROTECTED_BROKER_PAPER_SANDBOX_PACKET"
    assert result["broker_paper_dryrun_ledger_ready"] is True
    assert result["broker_paper_dryrun_risk_governor_classification"] == "DRYRUN_RISK_GOVERNOR_READY"
    assert result["broker_paper_dryrun_risk_governor_ready"] is True
    assert result["dryrun_risk_records"] == 2
    assert result["dryrun_risk_accepted"] == 1
    assert result["dryrun_risk_rejected"] == 1
    assert result["aggregate_max_loss_usd"] == 1.0
    assert result["max_daily_loss_usd"] == 5.0
    assert result["kill_switch_armed"] is True
    assert result["next_safe_packet"] == "PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-HARNESS-V1"
    assert result["broker_paper_orders_allowed"] is False
    assert result["network_api_allowed"] is False
    assert result["credentials_allowed"] is False
    assert result["broker_sdk_allowed"] is False
    assert result["live_orders_allowed"] is False
    assert result["live_trade_ready"] is False


def test_readiness_accepts_stress_repair_result_and_stays_watchlist_when_repair_is_watchlist() -> None:
    bundle = paper_forward_evidence_v2.build_paper_forward_evidence_v2()
    repair = stress_repair.apply_local_stress_repair_policy(bundle)

    result = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness(
        evidence=bundle,
        stress_oos=bundle["combined_stress_oos_gate"],
        risk_governor=bundle["risk_governor"],
        stress_repair=repair,
    )

    assert result["readiness_status"] == "WATCHLIST"
    assert result["broker_paper_sandbox_contract_ready"] is False
    assert result["stress_repair_status"] == repair["stress_repair_status"]
    assert "gate_watchlist:stress_repair_classification" in result["blockers"]
    assert result["live_trade_ready"] is False


def test_readiness_accepts_expanded_oos_and_blocks_contract_when_oos_is_watchlist() -> None:
    bundle = paper_forward_evidence_v2.build_paper_forward_evidence_v2()
    expanded = oos_expansion.run_expanded_oos_validation()
    expanded["classification"] = "WATCHLIST"
    expanded["blockers"] = ["expanded_oos_degradation_exceeds_policy"]

    result = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness(
        evidence=bundle,
        stress_oos=bundle["combined_stress_oos_gate"],
        risk_governor=bundle["risk_governor"],
        stress_repair=bundle["stress_repair"],
        expanded_oos=expanded,
    )

    assert result["readiness_status"] == "WATCHLIST"
    assert result["broker_paper_sandbox_contract_ready"] is False
    assert result["expanded_oos_classification"] == "WATCHLIST"
    assert "gate_watchlist:expanded_oos_classification" in result["blockers"]
    assert result["live_trade_ready"] is False


def test_readiness_accepts_oos_repair_and_blocks_contract_when_repair_is_watchlist() -> None:
    bundle = paper_forward_evidence_v2.build_paper_forward_evidence_v2()
    expanded = oos_expansion.run_expanded_oos_validation()
    repair = oos_repair.apply_oos_repair_policy(expanded)

    result = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness(
        evidence=bundle,
        stress_oos=bundle["combined_stress_oos_gate"],
        risk_governor=bundle["risk_governor"],
        stress_repair=bundle["stress_repair"],
        expanded_oos=expanded,
        oos_repair=repair,
    )

    assert result["readiness_status"] == "WATCHLIST"
    assert result["broker_paper_sandbox_contract_ready"] is False
    assert result["oos_repair_classification"] == "WATCHLIST"
    assert "gate_watchlist:oos_repair_classification" in result["blockers"]
    assert result["broker_paper_contract_ready"] is False
    assert result["live_trade_ready"] is False
    assert result["security_gate_required_before_broker_paper"] is True


def test_readiness_includes_low_vol_redesign_and_requires_presecurity_gate() -> None:
    evidence, stress_oos, risk_governor = _strong_contract_inputs()
    low_vol = low_vol_edge_redesign.apply_low_vol_edge_redesign(evidence["oos_repair"])

    result = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness(
        evidence=evidence,
        stress_oos=stress_oos,
        risk_governor=risk_governor,
        stress_repair=evidence["stress_repair"],
        expanded_oos=evidence["expanded_oos"],
        oos_repair=evidence["oos_repair"],
        low_vol_edge_redesign=low_vol,
    )

    assert result["readiness_status"] == "WATCHLIST"
    assert result["broker_paper_sandbox_contract_ready"] is False
    assert result["low_vol_edge_classification"] == "PAPER_FORWARD_READY"
    assert result["low_vol_policy_action"] == "NO_TRADE_GATE"
    assert result["redesigned_max_degradation_pct"] <= result["repaired_max_degradation_pct"]
    assert result["low_vol_rejected_intents"] > 0
    assert "gate_watchlist:presecurity_gate_landed_before_broker_paper" in result["blockers"]
    assert result["live_trade_ready"] is False


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("broker_integration_active", True),
        ("credentials_required_now", True),
        ("real_order_ready", True),
    ),
)
def test_side_effect_assertion_rejects_forbidden_states(field: str, value: bool) -> None:
    result = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness()
    result[field] = value

    with pytest.raises(ValueError):
        broker_paper_sandbox_readiness.assert_no_broker_paper_side_effects(result)


def test_boundary_summary_blocks_broker_paper_live_credentials_network_and_orders() -> None:
    summary = broker_paper_sandbox_readiness.broker_paper_sandbox_boundary_summary()

    assert summary["readiness_contract_only"] is True
    assert summary["broker_integration_active"] is False
    assert summary["broker_paper_orders"] is False
    assert summary["live_trade_ready"] is False
    assert summary["real_order_ready"] is False
    assert summary["credentials_required_now"] is False
    assert summary["network_allowed"] is False
    assert summary["network_api_allowed"] is False
    assert summary["broker_sdk_allowed"] is False
    assert summary["broker_paper_orders_allowed"] is False
    assert summary["credentials_allowed"] is False
    assert summary["protected_gate_required"] is True
    assert summary["security_gate_required_before_broker_paper"] is True
    assert summary["required_security_packet"] == "PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1"
    assert summary["next_safe_packet_after_stub_contract"] == "PKT-AIOS-BROKER-PAPER-DRYRUN-INTENT-LEDGER-V1"
    assert summary["next_safe_packet_after_dryrun_ledger"] == "PKT-AIOS-BROKER-PAPER-DRYRUN-RISK-GOVERNOR-V1"
    assert (
        summary["next_safe_packet_after_dryrun_risk_governor"]
        == "PKT-AIOS-BROKER-PAPER-DRYRUN-REPLAY-HARNESS-V1"
    )


def test_demo_function_exists_and_prints_safety_note(capsys) -> None:
    from automation.forex_engine import run_broker_paper_sandbox_readiness_demo

    assert run_broker_paper_sandbox_readiness_demo.main([]) == 0
    output = capsys.readouterr().out

    assert "AIOS Broker-Paper Sandbox Readiness Contract" in output
    assert "Mode: PAPER_ONLY_CONTRACT" in output
    assert "Readiness: WATCHLIST" in output
    assert "Live ready: false" in output
    assert "Real order ready: false" in output
    assert "Broker integration active: false" in output
    assert "Credentials required now: false" in output
    assert "Protected gate required: true" in output
    assert "Safety: no broker/API/network/orders/secrets/live execution." in output


def test_modules_have_no_forbidden_imports_or_calls() -> None:
    for path in (MODULE_PATH, DEMO_PATH):
        source = path.read_text(encoding="utf-8").lower()
        import_lines = "\n".join(
            line.strip()
            for line in source.splitlines()
            if line.startswith("import ") or line.startswith("from ")
        )

        for forbidden_import in ("requests", "socket", "urllib", "subprocess"):
            assert forbidden_import not in import_lines
        for line in import_lines.splitlines():
            assert not line.startswith("import broker")
            assert not line.startswith("from broker")
            assert not line.startswith("import oanda")
            assert not line.startswith("from oanda")
        for forbidden_call in (
            "os.environ",
            "getenv",
            "open(",
            "write_text(",
            "write_bytes(",
            "start-process",
            "schedule.every",
            "daemon.daemoncontext",
        ):
            assert forbidden_call not in source
