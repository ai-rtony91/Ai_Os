"""Tests for the approval review compressor (observe-only)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
COMPRESSOR = (
    REPO_ROOT / "automation" / "orchestration" / "autonomy_review"
    / "aios_approval_review_compressor.py"
)


def _load():
    spec = importlib.util.spec_from_file_location("aios_approval_review_compressor", COMPRESSOR)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PACKET = {
    "packet_id": "AIOS-DRAFT-CLOSE-GAP-X",
    "objective": "Close autonomy gap: build the schema reconciliation validator",
    "allowed_paths": ["automation/validators/", "tests/orchestration/"],
    "protected_action_expected": False,
}
GOV_CLEAN = {"status": "WARN", "errors": [], "warnings": [{"rule_id": "commit"}]}
COMP_READY = {"verdict": "READY_FOR_HUMAN_REVIEW", "promotion_ready": True, "reasons": []}


def test_clean_nonprotected_recommends_ready_for_human_approval():
    m = _load()
    card = m.build_approval_card(PACKET, governance=GOV_CLEAN, completeness=COMP_READY)
    assert card["recommended_decision"] == "READY_FOR_HUMAN_APPROVAL"
    assert card["risk_level"] == "LOW"
    assert card["requires_human"] is True
    assert card["approves_protected_action"] is False


def test_protected_packet_escalates():
    m = _load()
    card = m.build_approval_card({**PACKET, "protected_action_expected": True},
                                 governance=GOV_CLEAN, completeness=COMP_READY)
    assert card["recommended_decision"] == "HUMAN_REVIEW_REQUIRED_PROTECTED"
    assert card["risk_level"] == "HIGH"


def test_incomplete_holds_for_rework():
    m = _load()
    comp = {"verdict": "INCOMPLETE", "promotion_ready": False, "reasons": ["paths not scoped"]}
    card = m.build_approval_card(PACKET, governance=GOV_CLEAN, completeness=comp)
    assert card["recommended_decision"] == "HOLD_FOR_REWORK"
    assert "paths not scoped" in card["blocking_reasons"]


def test_hazard_block_rejects():
    m = _load()
    gov = {"status": "BLOCKED", "errors": [{"rule_id": "AIOS-PACKET-024-LIVE-TRADING-BLOCK", "severity": "BLOCK"}]}
    comp = {"verdict": "PROMOTION_BLOCKED", "promotion_ready": False, "reasons": ["hazard"]}
    card = m.build_approval_card(PACKET, governance=gov, completeness=comp)
    assert card["recommended_decision"] == "REJECT_OR_REWORK"
    assert card["risk_level"] == "HIGH"
    assert any("BLOCK" in r for r in card["blocking_reasons"])


def test_card_markdown_is_compact_and_states_gates():
    m = _load()
    card = m.build_approval_card(PACKET, governance=GOV_CLEAN, completeness=COMP_READY)
    md = card["card_markdown"]
    assert "Approval Card" in md
    assert "merge" in md  # permanent hard gate surfaced
    assert "decides nothing" in md


def test_recommended_decision_is_a_known_label():
    m = _load()
    card = m.build_approval_card(PACKET, governance=GOV_CLEAN, completeness=COMP_READY)
    assert card["recommended_decision"] in m.DECISION_LABELS


def test_missing_verdicts_fail_closed_not_ready():
    m = _load()
    # no governance, no completeness -> not promotion_ready -> HOLD, never auto-ready
    card = m.build_approval_card(PACKET)
    assert card["recommended_decision"] == "HOLD_FOR_REWORK"
    assert card["approves_protected_action"] is False
