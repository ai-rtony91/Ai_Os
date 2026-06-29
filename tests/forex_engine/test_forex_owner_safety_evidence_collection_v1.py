from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

from automation.validators import aios_governance_validator
from automation.forex_engine import (
    forex_owner_safety_evidence_collection_v1 as collection,
)


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = (
    ROOT
    / "scripts"
    / "forex_delivery"
    / "run_forex_owner_safety_evidence_collection_v1.py"
)
STATE_OUTPUT_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_STATE.json"
)
REPORT_OUTPUT_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_V1_REPORT.md"
)
NEXT_PACKET_OUTPUT_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_OWNER_SAFETY_EVIDENCE_COLLECTION_NEXT_CODEX_PACKET_V1.md"
)

FORBIDDEN_IMPORT_ROOTS = {
    "requests",
    "socket",
    "urllib",
    "dotenv",
    "os",
    "oanda",
    "oandapyV20",
    "apscheduler",
    "schedule",
    "sched",
    "daemon",
    "webhook",
}


def test_current_state_reports_all_four_controls_as_owner_evidence_missing():
    result = collection.run_forex_owner_safety_evidence_collection_v1()

    assert result["owner_evidence_collection_status"] == "OWNER_EVIDENCE_REQUIRED"
    assert result["controller_status"] == "SAFETY_CLOSURE_REQUIRED"
    assert result["controller_phase"] == "CRITICAL_SAFETY_EVIDENCE_CLOSURE"
    assert result["critical_safety_closure_status"] == "SAFETY_CLOSURE_OPEN"
    assert result["owner_evidence_required"] == list(collection.CONTROL_FIELDS)
    assert result["owner_evidence_complete"] == []
    assert result["owner_evidence_missing"] == list(collection.CONTROL_FIELDS)
    assert result["owner_evidence_completion_percent"] == 0.0
    assert result["evidence_verified_by_this_packet"] is False
    assert result["evidence_invented"] is False
    assert result["order_execution"] is False
    assert result["broker_api_used"] is False
    assert result["credentials_used"] is False


def test_complete_synthetic_closure_state_reports_full_owner_evidence_completion():
    result = collection.run_forex_owner_safety_evidence_collection_v1(
        controller_state=_controller_state(),
        closure_state=_closure_state(
            closure_status="SAFETY_CLOSURE_VERIFIED",
            verified_controls=list(collection.CONTROL_FIELDS),
            blocked_controls=[],
        ),
    )

    assert result["owner_evidence_collection_status"] == (
        "OWNER_EVIDENCE_COMPLETE_PENDING_VERIFICATION"
    )
    assert result["owner_evidence_complete"] == list(collection.CONTROL_FIELDS)
    assert result["owner_evidence_missing"] == []
    assert result["owner_evidence_completion_percent"] == 100.0
    assert result["evidence_verified_by_this_packet"] is False
    assert result["next_safe_action"].startswith(
        "Owner evidence is complete according to the closure state"
    )


def test_partial_or_present_closure_state_is_not_counted_as_verified():
    result = collection.run_forex_owner_safety_evidence_collection_v1(
        controller_state=_controller_state(),
        closure_state={
            "closure_status": "SAFETY_CLOSURE_OPEN",
            "controller_status": "SAFETY_CLOSURE_REQUIRED",
            "controller_phase": "CRITICAL_SAFETY_EVIDENCE_CLOSURE",
            "present_controls": ["daily_stop_state"],
            "blocked_controls": ["kill_switch_state"],
            "missing_controls": ["max_loss_state"],
            "unknown_controls": ["monitoring_ready"],
            "verified_controls": [],
        },
    )

    assert result["owner_evidence_complete"] == []
    assert result["owner_evidence_missing"] == list(collection.CONTROL_FIELDS)
    assert result["owner_evidence_completion_percent"] == 0.0
    assert (
        result["required_evidence_by_control_detail"]["daily_stop_state"][
            "governing_recommendation"
        ]
        == "CLOSURE_STATE_MUST_PROVE_CONTROL_BEFORE_PROGRESSION"
    )


def test_required_evidence_and_acceptable_types_are_listed_for_each_control():
    result = collection.run_forex_owner_safety_evidence_collection_v1()

    for control in collection.CONTROL_FIELDS:
        assert result["required_evidence_by_control"][control]
        assert result["acceptable_evidence_types_by_control"][control]
        assert result["verification_required_by_control"][control] is True
        detail = result["required_evidence_by_control_detail"][control]
        assert detail["required_owner_evidence"]
        assert detail["acceptable_evidence_types"]
        assert detail["evidence_freshness_requirement"]
        assert detail["verification_required"] is True
        assert detail["missing_status"] == "OWNER_EVIDENCE_MISSING"


def test_safety_boundary_blocks_execution_and_runtime_activation():
    result = collection.run_forex_owner_safety_evidence_collection_v1()
    safety_boundary = result["safety_boundary"]

    assert safety_boundary["order_execution_allowed"] is False
    assert safety_boundary["broker_api_allowed"] is False
    assert safety_boundary["credentials_allowed"] is False
    assert safety_boundary["account_identifier_persistence_allowed"] is False
    assert safety_boundary["scheduler_allowed"] is False
    assert safety_boundary["daemon_allowed"] is False
    assert safety_boundary["webhook_allowed"] is False
    assert safety_boundary["live_trading_authorized"] is False
    assert result["live_trading_authorized"] is False


def test_runner_writes_valid_state_report_and_next_packet():
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "--write-state",
            "--write-report",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    stdout_payload = json.loads(completed.stdout)
    state_payload = json.loads(STATE_OUTPUT_PATH.read_text(encoding="utf-8"))
    report_text = REPORT_OUTPUT_PATH.read_text(encoding="utf-8")
    next_packet_text = NEXT_PACKET_OUTPUT_PATH.read_text(encoding="utf-8")

    assert stdout_payload["state_output_path"] == str(STATE_OUTPUT_PATH)
    assert stdout_payload["report_output_path"] == str(REPORT_OUTPUT_PATH)
    assert stdout_payload["next_packet_output_path"] == str(NEXT_PACKET_OUTPUT_PATH)
    assert state_payload["packet_id"] == collection.PACKET_ID
    assert state_payload["owner_evidence_completion_percent"] == 0.0
    assert "Owner evidence completion percent: 0.0%" in report_text
    assert "No broker API was called." in report_text
    assert next_packet_text.startswith("CODEX-ONLY PROMPT")
    assert "@filename" not in next_packet_text
    assert "MODE\nDRY_RUN" in next_packet_text
    assert "\nPREFLIGHT\n" in next_packet_text
    assert "\nALLOWED PATHS\n" in next_packet_text
    assert "\nVALIDATOR CHAIN\n" in next_packet_text
    assert "\nFINAL REPORT FORMAT\n" in next_packet_text
    assert "\nSAFE NEXT ACTION\n" in next_packet_text
    assert "\nREAD ONLY\n" not in next_packet_text
    assert "\nVALIDATORS\n" not in next_packet_text
    assert "\nFINAL REPORT\n" not in next_packet_text
    assert "Do not invent evidence." in next_packet_text
    assert "Do not verify evidence." in next_packet_text
    validation = aios_governance_validator.validate_packet_text(
        next_packet_text,
        str(NEXT_PACKET_OUTPUT_PATH),
    )
    assert validation["status"] == "PASS"


def test_no_forbidden_imports_or_environment_access():
    for path in [
        ROOT
        / "automation"
        / "forex_engine"
        / "forex_owner_safety_evidence_collection_v1.py",
        RUNNER_PATH,
    ]:
        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source)
        imports = {
            alias.name.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.Import)
            for alias in node.names
        }
        imports.update(
            node.module.split(".")[0]
            for node in ast.walk(tree)
            if isinstance(node, ast.ImportFrom) and node.module
        )

        assert imports.isdisjoint(FORBIDDEN_IMPORT_ROOTS)
        assert "os.environ" not in source
        assert "dotenv" not in source
        assert ".env" not in source or "Do not read .env." in source


def test_no_secret_bearing_fields_are_emitted():
    result = collection.run_forex_owner_safety_evidence_collection_v1()
    output = json.dumps(result, ensure_ascii=True).lower()

    for fragment in (
        '"api_key"',
        '"access_token"',
        '"refresh_token"',
        '"password"',
        '"secret"',
        '"account_id"',
        '"broker_id"',
        "oanda",
    ):
        assert fragment not in output


def _controller_state() -> dict[str, object]:
    return {
        "controller_status": "STARTING_LINE_READY_WITH_SAFETY_BLOCKERS",
        "current_phase": "SAFETY_EVIDENCE_CLOSURE_PENDING",
    }


def _closure_state(
    *,
    closure_status: str,
    verified_controls: list[str],
    blocked_controls: list[str],
) -> dict[str, object]:
    return {
        "closure_status": closure_status,
        "controller_status": "SAFETY_CLOSURE_REQUIRED",
        "controller_phase": "CRITICAL_SAFETY_EVIDENCE_CLOSURE",
        "verified_controls": verified_controls,
        "blocked_controls": blocked_controls,
        "missing_controls": [],
        "unknown_controls": [],
        "present_controls": [],
        "control_evaluations": {
            control: {
                "status": "VERIFIED" if control in verified_controls else "BLOCKED",
            }
            for control in collection.CONTROL_FIELDS
        },
    }
