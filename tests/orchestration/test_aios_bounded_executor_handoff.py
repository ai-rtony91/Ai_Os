from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_bounded_executor_handoff.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_bounded_executor_handoff", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def plan(
    next_component: str,
    route: str = "build_next_paper_component",
    next_packet_id: str = "PKT-AIOS-FOREX-RISK-CONTROLS-CONTINUATION-APPLY",
) -> dict[str, object]:
    return {
        "schema": "AIOS_NEXT_BUILD_PLAN.v1",
        "goal": "forex-paper-bot",
        "route": route,
        "next_component": next_component,
        "next_packet_id": next_packet_id,
    }


def test_handoff_module_imports():
    module = load_module()
    assert module.SCHEMA == "AIOS_BOUNDED_EXECUTOR_HANDOFF.v1"
    assert callable(module.build_bounded_executor_handoff)


def test_forex_risk_controls_handoff_is_ready():
    module = load_module()
    handoff = module.build_bounded_executor_handoff(plan("forex_risk_controls"))
    assert handoff["handoff_status"] == "ready"
    assert handoff["executor_mode"] == "local_apply_after_human_review"
    assert handoff["allowed_action"] == "build_forex_risk_controls"
    assert handoff["next_component"] == "forex_risk_controls"


def test_allowed_paths_are_exactly_bounded_and_deterministic():
    module = load_module()
    handoff = module.build_bounded_executor_handoff(plan("forex_risk_controls"))
    assert handoff["allowed_paths"] == [
        "apps/trading_lab/trading_lab/forex_risk_controls.py",
        "tests/trading_lab/test_forex_risk_controls.py",
        "docs/orchestration/AIOS_FOREX_RISK_CONTROLS.md",
        "automation/orchestration/aios_autonomy_execute.py",
        "tests/orchestration/test_aios_autonomy_execute.py",
        "automation/orchestration/aios_wake_continue.py",
        "tests/orchestration/test_aios_wake_continue.py",
    ]


def test_execution_simulator_handoff_is_ready_with_exact_paths():
    module = load_module()
    handoff = module.build_bounded_executor_handoff(
        plan(
            "forex_paper_execution_simulator",
            next_packet_id="PKT-AIOS-FOREX-PAPER-EXECUTION-SIMULATOR-CONTINUATION-APPLY",
        )
    )
    assert handoff["handoff_status"] == "ready"
    assert handoff["executor_mode"] == "local_apply_after_human_review"
    assert handoff["allowed_action"] == "build_forex_paper_execution_simulator"
    assert handoff["next_component"] == "forex_paper_execution_simulator"
    assert handoff["next_packet_id"] == "PKT-AIOS-FOREX-PAPER-EXECUTION-SIMULATOR-CONTINUATION-APPLY"
    assert handoff["allowed_paths"] == [
        "apps/trading_lab/trading_lab/forex_paper_execution_simulator.py",
        "tests/trading_lab/test_forex_paper_execution_simulator.py",
        "docs/orchestration/AIOS_FOREX_PAPER_EXECUTION_SIMULATOR.md",
        "automation/orchestration/aios_productive_bounded_executor.py",
        "tests/orchestration/test_aios_productive_bounded_executor.py",
        "automation/orchestration/aios_wake_continue.py",
        "tests/orchestration/test_aios_wake_continue.py",
    ]


def test_execution_ledger_integration_handoff_is_ready_with_exact_paths():
    module = load_module()
    handoff = module.build_bounded_executor_handoff(
        plan(
            "forex_execution_ledger_integration",
            next_packet_id="PKT-AIOS-FOREX-EXECUTION-LEDGER-INTEGRATION-APPLY",
        )
    )
    assert handoff["handoff_status"] == "ready"
    assert handoff["executor_mode"] == "local_apply_after_human_review"
    assert handoff["allowed_action"] == "build_forex_execution_ledger_integration"
    assert handoff["next_component"] == "forex_execution_ledger_integration"
    assert handoff["next_packet_id"] == "PKT-AIOS-FOREX-EXECUTION-LEDGER-INTEGRATION-APPLY"
    assert handoff["allowed_paths"] == [
        "apps/trading_lab/trading_lab/forex_execution_ledger_integration.py",
        "tests/trading_lab/test_forex_execution_ledger_integration.py",
        "docs/orchestration/AIOS_FOREX_EXECUTION_LEDGER_INTEGRATION.md",
        "automation/orchestration/aios_productive_bounded_executor.py",
        "tests/orchestration/test_aios_productive_bounded_executor.py",
        "automation/orchestration/aios_wake_continue.py",
        "tests/orchestration/test_aios_wake_continue.py",
    ]


def test_validators_are_present_and_deterministic():
    module = load_module()
    handoff = module.build_bounded_executor_handoff(plan("forex_risk_controls"))
    assert handoff["validators"] == [
        "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_autonomy_execute.py tests/orchestration/test_aios_wake_continue.py tests/trading_lab/test_forex_risk_controls.py",
    ]
    assert handoff["command_preview"][-1] == handoff["validators"][0]


def test_execution_simulator_validators_are_pytest_only():
    module = load_module()
    handoff = module.build_bounded_executor_handoff(plan("forex_paper_execution_simulator"))
    assert handoff["validators"] == [
        "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_productive_bounded_executor.py tests/orchestration/test_aios_wake_continue.py tests/trading_lab/test_forex_paper_execution_simulator.py",
    ]
    assert handoff["command_preview"][-1] == handoff["validators"][0]


def test_execution_ledger_integration_validators_are_pytest_only():
    module = load_module()
    handoff = module.build_bounded_executor_handoff(plan("forex_execution_ledger_integration"))
    assert handoff["validators"] == [
        "python -m pytest -p no:cacheprovider tests/orchestration/test_aios_productive_bounded_executor.py tests/orchestration/test_aios_wake_continue.py tests/trading_lab/test_forex_execution_ledger_integration.py",
    ]
    assert handoff["command_preview"][-1] == handoff["validators"][0]


def test_strategy_review_handoff_is_ready():
    module = load_module()
    handoff = module.build_bounded_executor_handoff(plan("forex_strategy_rules_review", route="improve_strategy_rules"))
    assert handoff["handoff_status"] == "ready"
    assert handoff["allowed_action"] == "review_forex_strategy_rules"


def test_data_quality_review_handoff_is_ready():
    module = load_module()
    handoff = module.build_bounded_executor_handoff(plan("forex_data_quality_review", route="improve_data_quality"))
    assert handoff["handoff_status"] == "ready"
    assert handoff["allowed_action"] == "review_forex_data_quality"


def test_stop_route_produces_stopped_status():
    module = load_module()
    handoff = module.build_bounded_executor_handoff(plan("none", route="stop"))
    assert handoff["handoff_status"] == "stopped"
    assert handoff["allowed_paths"] == []
    assert handoff["validators"] == []


def test_unsupported_component_produces_blocked_status():
    module = load_module()
    handoff = module.build_bounded_executor_handoff(plan("unknown_component"))
    assert handoff["handoff_status"] == "blocked"
    assert handoff["reason_code"] == "unsupported_component"
    assert handoff["allowed_action"] == "none"


def test_no_unsafe_flags_are_enabled():
    module = load_module()
    handoff = module.build_bounded_executor_handoff(plan("forex_risk_controls"))
    assert all(value is False for value in handoff["safety"].values())
    assert handoff["approval_required"]["human_review_before_local_apply"] is True
    assert handoff["approval_required"]["commit"] is True
    assert handoff["approval_required"]["push"] is True
    assert handoff["approval_required"]["merge"] is True


def test_no_subprocess_file_or_network_usage_in_source():
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
