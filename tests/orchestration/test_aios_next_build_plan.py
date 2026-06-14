from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_next_build_plan.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_next_build_plan", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def goal_decision(decision: str) -> dict[str, object]:
    return {
        "schema": "AIOS_FOREX_GOAL_DECISION.v1",
        "goal": "forex-paper-bot",
        "decision": decision,
        "reason_code": f"{decision}_reason",
        "decision_reasons": [f"{decision}_reason"],
    }


def test_router_imports():
    module = load_module()
    assert module.SCHEMA == "AIOS_NEXT_BUILD_PLAN.v1"
    assert callable(module.build_next_build_plan)


def test_continue_build_routes_to_forex_risk_controls():
    module = load_module()
    plan = module.build_next_build_plan(goal_decision("continue_build"))
    assert plan["route"] == "build_next_paper_component"
    assert plan["next_component"] == "forex_risk_controls"
    assert plan["next_packet_id"] == "PKT-AIOS-FOREX-RISK-CONTROLS-CONTINUATION-APPLY"


def test_improve_strategy_routes_to_strategy_review():
    module = load_module()
    plan = module.build_next_build_plan(goal_decision("improve_strategy"))
    assert plan["route"] == "improve_strategy_rules"
    assert plan["next_component"] == "forex_strategy_rules_review"


def test_improve_data_routes_to_data_quality_review():
    module = load_module()
    plan = module.build_next_build_plan(goal_decision("improve_data"))
    assert plan["route"] == "improve_data_quality"
    assert plan["next_component"] == "forex_data_quality_review"


def test_improve_risk_controls_routes_to_risk_controls():
    module = load_module()
    plan = module.build_next_build_plan(goal_decision("improve_risk_controls"))
    assert plan["route"] == "build_risk_controls"
    assert plan["next_component"] == "forex_risk_controls"


def test_stop_for_human_review_routes_to_stop():
    module = load_module()
    plan = module.build_next_build_plan(goal_decision("stop_for_human_review"))
    assert plan["route"] == "stop"
    assert plan["next_component"] == "none"
    assert plan["next_packet_id"] == "NONE"


def test_invalid_decision_routes_to_stop():
    module = load_module()
    plan = module.build_next_build_plan({"schema": "AIOS_FOREX_GOAL_DECISION.v1", "goal": "forex-paper-bot"})
    assert plan["input_decision"] == "invalid_decision"
    assert plan["route"] == "stop"
    assert plan["reason_code"] == "invalid_decision"


def test_safety_blocks_execution_and_mutation():
    module = load_module()
    plan = module.build_next_build_plan(goal_decision("continue_build"))
    assert all(value is False for value in plan["safety"].values())
    assert plan["approval_required"]["commit"] is True
    assert plan["approval_required"]["push"] is True
    assert plan["approval_required"]["merge"] is True


def test_no_file_writes_or_network_usage():
    source = MODULE_PATH.read_text(encoding="utf-8").lower()
    for forbidden in ["open(", "write_text", "write_bytes", "with open", "requests", "socket", "urllib", "http.client"]:
        assert forbidden not in source
