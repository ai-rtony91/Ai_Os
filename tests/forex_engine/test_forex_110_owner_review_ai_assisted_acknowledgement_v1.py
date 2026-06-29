from __future__ import annotations

import json
from pathlib import Path


ACK_REPORT = Path("Reports/forex_delivery/AIOS_FOREX_110_OWNER_REVIEW_AND_AI_ASSISTED_ACKNOWLEDGEMENT_V1.md")
DOC_REPORT = Path("docs/trading_lab/forex/FOREX_110_OWNER_REVIEW_AND_AI_ASSISTED_ACKNOWLEDGEMENT_V1.md")
STATE_FILE = Path("Reports/forex_delivery/AIOS_FOREX_110_OWNER_REVIEW_AND_AI_ASSISTED_ACKNOWLEDGEMENT_V1_STATE.json")


def _load_state():
    data = json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return data


def test_acknowledgement_files_exist():
    assert ACK_REPORT.exists()
    assert DOC_REPORT.exists()
    assert STATE_FILE.exists()


def test_forex_110_acknowledgement_state():
    data = _load_state()
    assert data["forex_110_repo_safe_closure_landed"] is True
    assert data["final_dashboard_closure_landed"] is True
    assert data["post_closure_cleanup_plan_apply_landed"] is True
    assert data["protected_authority_remains"] is True
    assert data["human_owner"] == "Anthony"
    assert data["trading_authority_granted"] is False
    assert data["coauthored_by_claim_created"] is False
    assert data["coauthored_by_identity_used"] is False


def test_ai_assistance_recorded_as_assisted_by_only():
    data = _load_state()
    assistants = data["ai_assisted_by"]
    assert "OpenAI ChatGPT" in assistants
    assert "Codex" in assistants
    for scope in (
        "planning",
        "packet_drafting",
        "review_guidance",
        "repo_safe_execution_support",
    ):
        assert scope in data["ai_assistance_scope"]
    assert data["final_authority"]["human_owner_final_authority"] is True
    assert data["final_authority"]["owner"] == "Anthony"


def test_acknowledgement_text_mentions_required_points():
    ack_text = ACK_REPORT.read_text(encoding="utf-8")
    doc_text = DOC_REPORT.read_text(encoding="utf-8")
    required_fragments = [
        "Forex 110 repo-safe closure landed",
        "Final dashboard closure landed",
        "Safe post-closure cleanup plan/apply is landed",
        "broker/demo/live/order/money/credential",
        "Human owner: `Anthony`",
        "OpenAI ChatGPT and Codex assisted",
        "not a GitHub `Co-authored-by` claim",
        "No OpenAI email",
        "No trading",
    ]
    for fragment in required_fragments:
        assert fragment in ack_text, f"Missing fragment in report: {fragment}"
        assert fragment.lower() in doc_text.lower(), f"Missing fragment in doc report: {fragment}"
