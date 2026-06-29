from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from automation.forex_engine.flow2_supervised_demo_evidence_countdown_capture_v1 import (
    EvidenceCountdownResult,
    EvidenceItem,
    EVIDENCE_BLOCKED,
    EVIDENCE_IN_PROGRESS,
    EVIDENCE_NOT_STARTED,
    EVIDENCE_READY_FOR_REVIEW,
    build_default_flow2_required_evidence,
    capture_flow2_supervised_demo_evidence_countdown,
)


def test_build_default_flow2_required_evidence_has_minimum_items():
    evidence = build_default_flow2_required_evidence()
    evidence_ids = {item.evidence_id for item in evidence}

    assert "broker_connection_readiness_sanitized" in evidence_ids
    assert "supervised_demo_trade_plan" in evidence_ids
    assert "risk_controls_snapshot" in evidence_ids
    assert "kill_switch_state" in evidence_ids
    assert "demo_execution_transcript_sanitized" in evidence_ids
    assert "post_trade_pl_capture_sanitized" in evidence_ids
    assert "evidence_quality_review" in evidence_ids
    assert "owner_review_handoff" in evidence_ids


def test_empty_capture_returns_evidence_not_started():
    evidence = build_default_flow2_required_evidence()
    result = capture_flow2_supervised_demo_evidence_countdown(evidence)

    assert result.status == EVIDENCE_NOT_STARTED
    assert result.required_evidence_count == len(evidence)
    assert result.captured_evidence_count == 0
    assert result.remaining_evidence_count == result.required_evidence_count
    assert result.missing_evidence_ids == tuple(item.evidence_id for item in evidence)


def test_partial_capture_returns_evidence_in_progress():
    evidence = list(build_default_flow2_required_evidence())
    evidence[0] = replace(evidence[0], captured=True)
    result = capture_flow2_supervised_demo_evidence_countdown(tuple(evidence))

    assert result.status == EVIDENCE_IN_PROGRESS
    assert result.captured_evidence_count == 1
    assert result.remaining_evidence_count == result.required_evidence_count - 1
    assert result.captured_evidence_ids == ("broker_connection_readiness_sanitized",)


def test_full_capture_returns_evidence_ready_for_review():
    evidence = tuple(
        EvidenceItem(
            evidence_id=item.evidence_id,
            label=item.label,
            captured=True,
            blocker="",
            sanitized_reference=item.sanitized_reference,
        )
        for item in build_default_flow2_required_evidence()
    )
    result = capture_flow2_supervised_demo_evidence_countdown(evidence)

    assert result.status == EVIDENCE_READY_FOR_REVIEW
    assert result.captured_evidence_count == result.required_evidence_count
    assert result.remaining_evidence_count == 0
    assert result.blockers == ()


def test_any_blocker_returns_evidence_blocked():
    evidence = list(build_default_flow2_required_evidence())
    evidence[0] = replace(evidence[0], blocker="missing broker connection screenshot")
    result = capture_flow2_supervised_demo_evidence_countdown(tuple(evidence))

    assert result.status == EVIDENCE_BLOCKED
    assert result.blockers == ("missing broker connection screenshot",)
    assert result.next_action == "RESOLVE_EVIDENCE_BLOCKERS"


def test_to_dict_returns_json_safe_payload():
    result = capture_flow2_supervised_demo_evidence_countdown(
        (
            EvidenceItem(
                evidence_id="broker_connection_readiness_sanitized",
                label="Broker connection readiness (sanitized)",
                captured=True,
            ),
            EvidenceItem(
                evidence_id="supervised_demo_trade_plan",
                label="Supervised demo trade plan",
                captured=False,
            ),
        )
    )
    payload: dict[str, object] = result.to_dict()

    json.loads(json.dumps(payload))

    assert isinstance(payload["flow_id"], str)
    assert isinstance(payload["required_evidence_count"], int)
    assert isinstance(payload["captured_evidence_ids"], list)
    assert isinstance(payload["missing_evidence_ids"], list)
    assert isinstance(payload["blockers"], list)
    assert payload["status"] in {
        EVIDENCE_NOT_STARTED,
        EVIDENCE_IN_PROGRESS,
        EVIDENCE_READY_FOR_REVIEW,
        EVIDENCE_BLOCKED,
    }


def test_counts_are_exact_with_mixed_capture_states():
    evidence = [
        EvidenceItem(
            evidence_id="broker_connection_readiness_sanitized",
            label="Broker connection readiness (sanitized)",
            captured=True,
        ),
        EvidenceItem(
            evidence_id="supervised_demo_trade_plan",
            label="Supervised demo trade plan",
            captured=False,
        ),
        EvidenceItem(
            evidence_id="risk_controls_snapshot",
            label="Risk controls snapshot",
            captured=True,
        ),
        EvidenceItem(
            evidence_id="kill_switch_state",
            label="Kill-switch state",
            captured=False,
        ),
    ]
    result = capture_flow2_supervised_demo_evidence_countdown(tuple(evidence))

    assert result.captured_evidence_count == 2
    assert result.remaining_evidence_count == 2
    assert result.missing_evidence_ids == ("supervised_demo_trade_plan", "kill_switch_state")


def test_no_forbidden_imports_in_module_source():
    source = Path("automation/forex_engine/flow2_supervised_demo_evidence_countdown_capture_v1.py").read_text(
        encoding="utf-8"
    )

    forbidden = [
        "import requests",
        "import httpx",
        "import socket",
        "import subprocess",
        "import os",
        "import pathlib",
        "import dotenv",
        "from requests",
        "from httpx",
        "from socket",
        "from subprocess",
        "from os",
        "from pathlib",
        "from dotenv",
    ]

    for token in forbidden:
        assert token not in source
