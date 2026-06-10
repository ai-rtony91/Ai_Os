"""Tests for the AI_OS completion evidence validator."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "automation" / "validators" / "aios_completion_evidence_validator.py"


def _load():
    spec = importlib.util.spec_from_file_location("aios_completion_evidence_validator", VALIDATOR)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    # Register before exec so @dataclass can resolve cls.__module__ (py3.11 importlib gotcha).
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PACKET = (
    "CODEX-ONLY PROMPT\n"
    "ALLOWED PATHS:\n- automation/validators/\n- tests/orchestration/\n"
    "FORBIDDEN PATHS:\n- AGENTS.md\n- broker/\n- live_trading/\n"
    "MISSION:\nsample\n"
)
EVIDENCE = "pytest: 5 passed. git diff --check PASS. validation complete."


def _seed(root: Path) -> str:
    (root / "automation/validators").mkdir(parents=True)
    rel = "automation/validators/built_thing.py"
    (root / rel).write_text("print('real deliverable')\n", encoding="utf-8")
    (root / "AGENTS.md").write_text("authority\n", encoding="utf-8")
    return rel


def test_verified_when_real_inscope_and_evidence(tmp_path):
    m = _load()
    rel = _seed(tmp_path)
    res = m.evaluate_completion(PACKET, [rel], tmp_path, EVIDENCE)
    assert res["verdict"] == "COMPLETION_VERIFIED"
    assert res["approves_protected_action"] is False
    assert res["contradictions"] == []


def test_unproven_when_evidence_missing(tmp_path):
    m = _load()
    rel = _seed(tmp_path)
    res = m.evaluate_completion(PACKET, [rel], tmp_path, None)
    assert res["verdict"] == "COMPLETION_UNPROVEN"


def test_unproven_when_no_deliverables_declared(tmp_path):
    m = _load()
    _seed(tmp_path)
    res = m.evaluate_completion(PACKET, [], tmp_path, EVIDENCE)
    assert res["verdict"] == "COMPLETION_UNPROVEN"


def test_contradicted_when_claimed_file_missing(tmp_path):
    m = _load()
    _seed(tmp_path)
    res = m.evaluate_completion(PACKET, ["automation/validators/ghost.py"], tmp_path, EVIDENCE)
    assert res["verdict"] == "COMPLETION_CONTRADICTED"


def test_contradicted_when_claimed_file_empty(tmp_path):
    m = _load()
    _seed(tmp_path)
    rel = "automation/validators/empty.py"
    (tmp_path / rel).write_text("", encoding="utf-8")
    res = m.evaluate_completion(PACKET, [rel], tmp_path, EVIDENCE)
    assert res["verdict"] == "COMPLETION_CONTRADICTED"


def test_contradicted_when_forbidden_path_changed(tmp_path):
    m = _load()
    _seed(tmp_path)  # AGENTS.md exists and is forbidden
    res = m.evaluate_completion(PACKET, ["AGENTS.md"], tmp_path, EVIDENCE)
    assert res["verdict"] == "COMPLETION_CONTRADICTED"


def test_contradicted_when_out_of_allowed_scope(tmp_path):
    m = _load()
    _seed(tmp_path)
    rel = "automation/orchestration/sneaky.py"
    (tmp_path / "automation/orchestration").mkdir(parents=True)
    (tmp_path / rel).write_text("print('out of scope')\n", encoding="utf-8")
    res = m.evaluate_completion(PACKET, [rel], tmp_path, EVIDENCE)
    assert res["verdict"] == "COMPLETION_CONTRADICTED"


def test_sample_check_function_returns_all_three_verdicts():
    m = _load()
    result = m._sample_check()
    assert result["verified"] == "COMPLETION_VERIFIED"
    assert result["unproven"] == "COMPLETION_UNPROVEN"
    assert result["contradicted_missing"] == "COMPLETION_CONTRADICTED"
    assert result["contradicted_forbidden"] == "COMPLETION_CONTRADICTED"
