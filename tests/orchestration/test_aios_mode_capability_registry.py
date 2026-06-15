from __future__ import annotations

import importlib.util
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = REPO_ROOT / "automation" / "orchestration" / "aios_mode_capability_registry.py"


def load_module():
    spec = importlib.util.spec_from_file_location("aios_mode_capability_registry", MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_imports():
    module = load_module()
    assert module.SCHEMA == "AIOS_MODE_CAPABILITY_REGISTRY.v1"


def test_registry_includes_all_modes():
    module = load_module()
    registry = module.build_mode_capability_registry()
    assert set(registry["modes"]) == {
        "forex",
        "platform",
        "dashboard",
        "game",
        "automation",
        "security",
        "infrastructure",
    }


def test_forex_active_proof_target_exists():
    module = load_module()
    registry = module.build_mode_capability_registry()
    forex = registry["modes"]["forex"]
    assert registry["active_mode"] == "forex"
    assert registry["active_goal"] == "forex-paper-bot"
    assert forex["status"] == "active_proof_target"
    assert "build_forex_risk_controls" in forex["allowed_actions"]
    assert "build_forex_paper_execution_simulator" in forex["allowed_actions"]


def test_future_modes_are_not_active():
    module = load_module()
    registry = module.build_mode_capability_registry()
    for mode_id, contract in registry["modes"].items():
        if mode_id != "forex":
            assert contract["status"] in {"reserved", "future"}


def test_hard_blocked_actions_are_blocked_in_every_mode():
    module = load_module()
    registry = module.build_mode_capability_registry()
    blocked = set(registry["hard_blocked_actions"])
    for mode in registry["modes"].values():
        assert blocked.issubset(set(mode["blocked_actions"]))
