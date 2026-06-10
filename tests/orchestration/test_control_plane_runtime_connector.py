"""Tests for the autonomy control-plane runtime connector (Theme 1 CONNECT, observe-only)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
CONNECTOR = (
    REPO_ROOT / "automation" / "orchestration" / "autonomy_control_plane"
    / "aios_control_plane_runtime_connector.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("aios_control_plane_runtime_connector", CONNECTOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


CP_OK = {"status": "PASS", "validator": {"status": "PASS"}, "packet_runner": {"status": "PASS"}}
ROUTER_OK = {
    "next_action": "OPEN_PR",
    "safe_command": "echo open a PR for review",
    "requires_anthony": False,
    "protected_action": False,
    "live_risk": False,
}


def _seed_packet_and_deliverable(root: Path):
    (root / "automation/validators").mkdir(parents=True, exist_ok=True)
    rel = "automation/validators/built.py"
    (root / rel).write_text("print('real')\n", encoding="utf-8")
    packet = (
        "CODEX-ONLY PROMPT\nALLOWED PATHS:\n- automation/validators/\n"
        "FORBIDDEN PATHS:\n- broker/\nMISSION:\nx\n"
    )
    return packet, rel


def test_observe_only_safety_flags_always_set(tmp_path):
    m = _load()
    view = m.build_runtime_view(CP_OK, ROUTER_OK, tmp_path)
    assert view["observe_only"] is True
    s = view["safety"]
    assert s["apply"] is False and s["merge"] is False and s["live_trading"] is False
    assert s["broker"] is False and s["secrets"] is False and s["mutated_repo_state"] is False


def test_control_plane_evidence_surfaced_into_runtime_view(tmp_path):
    m = _load()
    view = m.build_runtime_view(CP_OK, ROUTER_OK, tmp_path)
    assert view["control_plane"]["status"] == "PASS"
    assert view["control_plane"]["validator_status"] == "PASS"
    assert view["next_action"]["action"] == "OPEN_PR"
    assert view["runtime_gate"] == "READY_TO_REPORT"


def test_completion_validator_wired_as_trust_gate_verified(tmp_path):
    m = _load()
    packet, rel = _seed_packet_and_deliverable(tmp_path)
    view = m.build_runtime_view(
        CP_OK, ROUTER_OK, tmp_path,
        packet_text=packet, changed_files=[rel],
        evidence_text="pytest passed; git diff --check PASS; validation complete",
    )
    assert view["trust_gate_completion"]["verdict"] == "COMPLETION_VERIFIED"
    assert view["runtime_gate"] == "READY_TO_REPORT"


def test_trust_gate_blocks_when_completion_contradicted(tmp_path):
    m = _load()
    packet, _ = _seed_packet_and_deliverable(tmp_path)
    # claim a file that does not exist -> completion CONTRADICTED -> TRUST_FAILED gate
    view = m.build_runtime_view(
        CP_OK, ROUTER_OK, tmp_path,
        packet_text=packet, changed_files=["automation/validators/ghost.py"],
        evidence_text="pytest passed",
    )
    assert view["trust_gate_completion"]["verdict"] == "COMPLETION_CONTRADICTED"
    assert view["runtime_gate"] == "TRUST_FAILED"


def test_prohibited_command_is_never_surfaced(tmp_path):
    m = _load()
    bad_router = dict(ROUTER_OK, safe_command="gh pr merge 999 --merge")
    view = m.build_runtime_view(CP_OK, bad_router, tmp_path)
    assert view["next_action"]["command_was_prohibited_and_held"] is True
    assert "merge" not in view["next_action"]["surfaced_command"].lower()
    assert view["next_action"]["requires_human"] is True
    assert view["runtime_gate"] == "HUMAN_REQUIRED"


def test_apply_command_held(tmp_path):
    m = _load()
    bad_router = dict(ROUTER_OK, safe_command="run something --apply now")
    view = m.build_runtime_view(CP_OK, bad_router, tmp_path)
    assert view["next_action"]["command_was_prohibited_and_held"] is True
    assert view["runtime_gate"] == "HUMAN_REQUIRED"


def test_protected_action_requires_human(tmp_path):
    m = _load()
    router = dict(ROUTER_OK, protected_action=True)
    view = m.build_runtime_view(CP_OK, router, tmp_path)
    assert view["runtime_gate"] == "HUMAN_REQUIRED"


def test_blocked_control_plane_yields_blocked_gate(tmp_path):
    m = _load()
    view = m.build_runtime_view({"status": "BLOCKED"}, ROUTER_OK, tmp_path)
    assert view["runtime_gate"] == "BLOCKED"


def test_build_runtime_view_mutates_no_input_files(tmp_path):
    m = _load()
    packet, rel = _seed_packet_and_deliverable(tmp_path)
    before = (tmp_path / rel).read_text(encoding="utf-8")
    m.build_runtime_view(CP_OK, ROUTER_OK, tmp_path, packet_text=packet, changed_files=[rel], evidence_text="passed")
    after = (tmp_path / rel).read_text(encoding="utf-8")
    assert before == after  # observe-only: deliverables untouched
