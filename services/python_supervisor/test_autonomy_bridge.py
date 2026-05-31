from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from autonomy_bridge import build_bridge_state, classify_item, collect_source_files


SAFETY_ORDER = {"PASS": 0, "UNKNOWN": 1, "WARN": 2, "NEEDS_APPROVAL": 3, "BLOCKED": 4}


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def test_operation_glue_approval_reaches_must_see(tmp_path: Path) -> None:
    approval_path = tmp_path / "control" / "operation_glue" / "APPROVAL_INBOX.json"
    write_json(
        approval_path,
        {
            "schema": "AIOS_OPERATION_GLUE_APPROVAL_INBOX.v0_1",
            "status": "WAITING_APPROVAL",
            "item_count": 1,
            "approval_required_count": 1,
            "entries": [
                {
                    "item_id": "APPROVAL_ITEM_SMOKE",
                    "status": "WAITING_APPROVAL",
                    "approval_required": True,
                    "reason": "Smoke Glue item requires Human Owner review.",
                    "next_safe_action": "Review Glue approval before execution.",
                }
            ],
            "next_safe_action": "Review Glue approval before execution.",
        },
    )

    result_path = tmp_path / "telemetry" / "operation_glue" / "worker_results" / "WORKER_RESULT_SMOKE.json"
    write_json(
        result_path,
        {
            "schema": "AIOS_OPERATION_GLUE_WORKER_RESULT.v0_1",
            "status": "PASS",
            "summary": "Worker result exists so Glue telemetry is visible.",
        },
    )

    source_paths = {path.relative_to(tmp_path).as_posix() for path in collect_source_files(tmp_path)}
    assert "control/operation_glue/APPROVAL_INBOX.json" in source_paths
    assert "telemetry/operation_glue/worker_results/WORKER_RESULT_SMOKE.json" in source_paths

    state = build_bridge_state(tmp_path)

    glue_approval = [
        item
        for item in state["items_needing_approval"]
        if item["source_path"] == "control/operation_glue/APPROVAL_INBOX.json"
    ]
    assert glue_approval
    assert glue_approval[0]["status"] == "NEEDS_APPROVAL"
    assert glue_approval[0]["status"] != "PASS"
    assert state["approval_needed_count"] >= 1
    assert "Review Glue approval before execution." in state["must_see"]


def test_glue_approval_classification_prefers_safer_status() -> None:
    classification = classify_item(
        {
            "source_path": "control/operation_glue/APPROVAL_INBOX.json",
            "status": "READY_FOR_NEXT_SAFE_ACTION",
            "text": json.dumps(
                {
                    "entries": [
                        {
                            "status": "WAITING_APPROVAL",
                            "approval_required": True,
                            "reason": "Human approval required.",
                        }
                    ]
                }
            ),
        }
    )

    assert classification["status"] == "NEEDS_APPROVAL"
    assert classification["status"] != "PASS"


def test_explicit_blocked_status_beats_pass_text() -> None:
    classification = classify_item(
        {
            "source_path": "relay/done/example.task.json",
            "status": "BLOCKED",
            "summary": "Worker says PASS and complete.",
        }
    )

    assert classification["status"] == "BLOCKED"


def test_explicit_risk_and_gate_flags_are_safe() -> None:
    classification = classify_item(
        {
            "source_path": "control/operation_glue/APPROVAL_INBOX.json",
            "status": "PASS",
            "risk_level": "HIGH",
            "gate_flags": ["HUMAN_APPROVAL_REQUIRED"],
            "summary": "Looks routine.",
        }
    )

    assert classification["status"] == "NEEDS_APPROVAL"


def test_new_blocker_language_is_not_pass() -> None:
    classification = classify_item(
        {
            "source_path": "relay/inbox/new.task.txt",
            "summary": "Execute live trading through broker execution immediately.",
        }
    )

    assert classification["status"] == "BLOCKED"


def test_ambiguous_input_defaults_safe() -> None:
    classification = classify_item({"source_path": "telemetry/unknown/item.json", "summary": "unclear"})

    assert classification["status"] == "NEEDS_APPROVAL"
    assert classification["status"] != "PASS"


def test_prior_cases_same_or_safer() -> None:
    cases = [
        ({"source_path": "relay/error/danger.task.txt", "summary": "Please place a buy order for EURUSD live now."}, "BLOCKED"),
        ({"source_path": "relay/approvals/example.approval.json", "status": "WAITING"}, "NEEDS_APPROVAL"),
        ({"source_path": "relay/done/example.task.json", "status": "PASS"}, "PASS"),
        ({"source_path": "relay/outbox/repo-summary.report.txt", "summary": "review stale unknown"}, "WARN"),
    ]

    for item, previous_status in cases:
        current = classify_item(item)["status"]
        assert SAFETY_ORDER[current] >= SAFETY_ORDER[previous_status]


class AutonomyBridgeGlueTests(unittest.TestCase):
    def test_operation_glue_approval_reaches_must_see(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            test_operation_glue_approval_reaches_must_see(Path(temp_dir))

    def test_glue_approval_classification_prefers_safer_status(self) -> None:
        test_glue_approval_classification_prefers_safer_status()

    def test_explicit_blocked_status_beats_pass_text(self) -> None:
        test_explicit_blocked_status_beats_pass_text()

    def test_explicit_risk_and_gate_flags_are_safe(self) -> None:
        test_explicit_risk_and_gate_flags_are_safe()

    def test_new_blocker_language_is_not_pass(self) -> None:
        test_new_blocker_language_is_not_pass()

    def test_ambiguous_input_defaults_safe(self) -> None:
        test_ambiguous_input_defaults_safe()

    def test_prior_cases_same_or_safer(self) -> None:
        test_prior_cases_same_or_safer()


if __name__ == "__main__":
    unittest.main()
