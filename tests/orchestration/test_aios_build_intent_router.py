from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
ROUTER_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_build_intent_router.py"
REGISTRY_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_mode_capability_registry.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def registry():
    return load_module(REGISTRY_PATH, "aios_mode_capability_registry").build_mode_capability_registry()


def test_imports():
    module = load_module(ROUTER_PATH, "aios_build_intent_router")
    assert module.SCHEMA == "AIOS_BUILD_INTENT_ROUTER.v1"


def test_forex_goal_routes_to_active_proof_target():
    module = load_module(ROUTER_PATH, "aios_build_intent_router")
    route = module.route_build_intent("build forex bot", {}, {}, registry())
    assert route["detected_mode"] == "forex"
    assert route["detected_goal"] == "forex-paper-bot"
    assert route["proof_target"] is True
    assert route["route_status"] == "ready_for_forex_control_plane"


def test_live_or_broker_wording_is_blocked():
    module = load_module(ROUTER_PATH, "aios_build_intent_router")
    route = module.route_build_intent("build forex bot with broker live trading", {}, {}, registry())
    assert route["route_status"] == "blocked_live_trading"
    assert route["safety"]["broker"] is True
    assert route["safety"]["live_trading"] is True


def test_dashboard_mode_is_reserved():
    module = load_module(ROUTER_PATH, "aios_build_intent_router")
    route = module.route_build_intent("build dashboard", {}, {}, registry())
    assert route["detected_mode"] == "dashboard"
    assert route["route_status"] == "reserved_until_control_plane_reader"


def test_game_mode_is_future_not_enabled():
    module = load_module(ROUTER_PATH, "aios_build_intent_router")
    route = module.route_build_intent("build game", {}, {}, registry())
    assert route["detected_mode"] == "game"
    assert route["route_status"] == "future_mode_not_enabled"


def test_unknown_goal_needs_human_clarification():
    module = load_module(ROUTER_PATH, "aios_build_intent_router")
    route = module.route_build_intent("build an unrelated thing", {}, {}, registry())
    assert route["route_status"] == "needs_human_clarification"
    assert route["approval_required"]["human_clarification"] is True
