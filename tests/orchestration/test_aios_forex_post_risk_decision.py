from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_forex_post_risk_decision.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_forex_post_risk_decision", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def inventory(*, risk_controls: bool = True, execution_simulator: bool = False) -> dict[str, bool]:
    return {
        "forex_paper_bot": True,
        "forex_backtest": True,
        "forex_paper_ledger": True,
        "forex_strategy_rules": True,
        "forex_data_import": True,
        "forex_report": True,
        "forex_decision_policy": True,
        "forex_risk_controls": risk_controls,
        "forex_paper_execution_simulator": execution_simulator,
    }


def test_post_risk_decision_module_imports():
    module = load_module()
    assert module.SCHEMA == "AIOS_FOREX_POST_RISK_DECISION.v1"
    assert callable(module.build_post_risk_decision)


def test_risk_controls_present_execution_simulator_missing_selects_execution_simulator():
    module = load_module()
    decision = module.build_post_risk_decision(inventory())
    assert decision["schema"] == "AIOS_FOREX_POST_RISK_DECISION.v1"
    assert decision["selected_next_component"] == "forex_paper_execution_simulator"
    assert decision["selected_action"] == "build_forex_paper_execution_simulator"
    assert decision["selected_packet_id"] == "PKT-AIOS-FOREX-PAPER-EXECUTION-SIMULATOR-CONTINUATION-APPLY"
    assert decision["reason_code"] == "risk_controls_validated_execution_simulator_missing"


def test_execution_simulator_present_routes_to_current_scope_complete():
    module = load_module()
    decision = module.build_post_risk_decision(inventory(execution_simulator=True))
    assert decision["selected_next_component"] == "none"
    assert decision["selected_action"] == "none"
    assert decision["selected_packet_id"] == "NONE"
    assert decision["reason_code"] == "current_inventory_complete_for_defined_scope"


def test_risk_controls_missing_selects_risk_controls():
    module = load_module()
    decision = module.build_post_risk_decision(inventory(risk_controls=False))
    assert decision["selected_next_component"] == "forex_risk_controls"
    assert decision["selected_action"] == "build_forex_risk_controls"
    assert decision["reason_code"] == "risk_controls_missing"


def test_no_unsafe_flags_are_enabled():
    module = load_module()
    decision = module.build_post_risk_decision(inventory())
    assert all(value is False for value in decision["safety"].values())
    assert decision["approval_required"]["commit"] is True
    assert decision["approval_required"]["push"] is True
    assert decision["approval_required"]["merge"] is True


def test_no_file_write_runtime_or_network_usage_in_source():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in [
        "subprocess",
        "open(",
        "write_text",
        "write_bytes",
        "with open",
        "requests",
        "socket",
        "urllib",
        "http.client",
    ]:
        assert forbidden not in source
