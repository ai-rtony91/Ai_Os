"""Tests for the path-guard validator (enforcement-in-code)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
GUARD = REPO_ROOT / "automation" / "validators" / "aios_path_guard_validator.py"


def _load():
    spec = importlib.util.spec_from_file_location("aios_path_guard_validator", GUARD)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_pass_when_in_scope():
    m = _load()
    res = m.check_paths(
        ["automation/validators/x.py", "tests/orchestration/test_x.py"],
        allowed_paths=["automation/validators/", "tests/orchestration/"],
        forbidden_paths=["AGENTS.md", "broker/"],
    )
    assert res["status"] == "PASS"
    assert res["violations"] == []
    assert res["approves_protected_action"] is False


def test_block_out_of_scope():
    m = _load()
    res = m.check_paths(
        ["automation/orchestration/sneaky.py"],
        allowed_paths=["automation/validators/"],
        forbidden_paths=[],
    )
    assert res["status"] == "BLOCK"
    assert res["violations"][0]["reason"] == "OUT_OF_ALLOWED_SCOPE"


def test_block_forbidden_path():
    m = _load()
    res = m.check_paths(
        ["AGENTS.md"],
        allowed_paths=["AGENTS.md"],   # even if 'allowed', forbidden wins
        forbidden_paths=["AGENTS.md"],
    )
    assert res["status"] == "BLOCK"
    assert res["violations"][0]["reason"] == "FORBIDDEN_PATH"
    assert res["violations"][0]["matched"] == "AGENTS.md"


def test_forbidden_takes_precedence_over_allowed():
    m = _load()
    res = m.check_paths(
        ["broker/orders.py"],
        allowed_paths=["broker/"],
        forbidden_paths=["broker/"],
    )
    assert res["status"] == "BLOCK"
    assert res["violations"][0]["reason"] == "FORBIDDEN_PATH"


def test_no_allowed_list_only_forbidden_blocks():
    m = _load()
    # with no allowed list, anything not forbidden passes
    res = m.check_paths(["any/file.py"], allowed_paths=[], forbidden_paths=["secrets/"])
    assert res["status"] == "PASS"
    res2 = m.check_paths(["secrets/key.txt"], allowed_paths=[], forbidden_paths=["secrets/"])
    assert res2["status"] == "BLOCK"


def test_check_against_packet_extracts_paths():
    m = _load()
    packet = (
        "CODEX-ONLY PROMPT\n"
        "ALLOWED PATHS:\n- automation/validators/\n- tests/orchestration/\n"
        "FORBIDDEN PATHS:\n- AGENTS.md\n- broker/\n"
        "MISSION:\nx\n"
    )
    ok = m.check_against_packet(["automation/validators/v.py"], packet)
    assert ok["status"] == "PASS"
    assert "automation/validators" in ok["allowed_paths"]
    bad = m.check_against_packet(["AGENTS.md"], packet)
    assert bad["status"] == "BLOCK"


def test_exit_code_via_status():
    m = _load()
    # PASS -> would exit 0; BLOCK -> would exit 3 (hook-usable). Assert the status drives it.
    assert m.check_paths(["a/b.py"], allowed_paths=["a/"])["status"] == "PASS"
    assert m.check_paths(["c/d.py"], allowed_paths=["a/"])["status"] == "BLOCK"
