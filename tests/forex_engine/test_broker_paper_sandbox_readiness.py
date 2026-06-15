from __future__ import annotations

from pathlib import Path

import pytest

from automation.forex_engine import broker_paper_sandbox_readiness
from automation.forex_engine import paper_forward_evidence_v2


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


def test_default_readiness_result_is_watchlist_and_contract_only() -> None:
    result = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness()

    assert result["mode"] == "PAPER_ONLY_CONTRACT"
    assert result["readiness_status"] == "WATCHLIST"
    assert result["readiness_status"] in ALLOWED_STATUSES
    assert result["readiness_status"] != "LIVE_READY"
    assert result["broker_paper_sandbox_contract_ready"] is False
    assert result["live_trade_ready"] is False
    assert result["real_order_ready"] is False
    assert result["broker_integration_active"] is False
    assert result["credentials_required_now"] is False
    assert result["protected_gate_required"] is True
    assert result["future_broker_paper_packet_requires_approval"] is True
    assert result["blockers"]


def test_fail_evidence_returns_not_ready() -> None:
    evidence, stress_oos, risk_governor = _strong_contract_inputs()
    stress_oos["combined_classification"] = "FAIL"

    result = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness(
        evidence=evidence,
        stress_oos=stress_oos,
        risk_governor=risk_governor,
    )

    assert result["readiness_status"] == "NOT_READY"
    assert result["broker_paper_sandbox_contract_ready"] is False
    assert "gate_failed:combined_stress_oos_classification" in result["blockers"]


def test_strong_evidence_can_return_contract_ready() -> None:
    evidence, stress_oos, risk_governor = _strong_contract_inputs()

    result = broker_paper_sandbox_readiness.evaluate_broker_paper_sandbox_readiness(
        evidence=evidence,
        stress_oos=stress_oos,
        risk_governor=risk_governor,
    )

    assert result["readiness_status"] == "CONTRACT_READY_FOR_PROTECTED_BROKER_PAPER_SANDBOX_PACKET"
    assert result["broker_paper_sandbox_contract_ready"] is True
    assert result["live_trade_ready"] is False
    assert result["real_order_ready"] is False
    assert result["broker_integration_active"] is False
    assert result["credentials_required_now"] is False
    assert result["protected_gate_required"] is True


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
    assert summary["protected_gate_required"] is True


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
