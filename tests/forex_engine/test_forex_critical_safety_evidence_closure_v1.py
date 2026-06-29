from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

from automation.validators import aios_governance_validator
from automation.forex_engine import forex_critical_safety_evidence_closure_v1 as closure


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = (
    ROOT
    / "scripts"
    / "forex_delivery"
    / "run_forex_critical_safety_evidence_closure_v1.py"
)
STATE_OUTPUT_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_STATE.json"
)
REPORT_OUTPUT_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_REPORT.md"
)
NEXT_PACKET_OUTPUT_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_NEXT_CODEX_PACKET_V1.md"
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


def test_current_controller_output_keeps_all_critical_controls_blocked():
    result = closure.run_forex_critical_safety_evidence_closure_v1()

    assert result["controller_status"] == "SAFETY_CLOSURE_REQUIRED"
    assert result["controller_phase"] == "CRITICAL_SAFETY_EVIDENCE_CLOSURE"
    assert result["safety_completion_percent"] == 0.0
    assert result["readiness_delta"] == 100.0
    assert result["verified_controls"] == []
    assert result["blocked_controls"] == list(closure.CONTROL_FIELDS)
    assert result["missing_controls"] == []
    assert result["next_safe_action"].startswith(
        "Close controller-reported critical safety blockers"
    )
    assert result["order_execution"] is False
    assert result["broker_api_used"] is False
    assert result["credentials_used"] is False
    assert result["evidence_invented"] is False


def test_full_closure_requires_all_four_controls_verified():
    result = closure.run_forex_critical_safety_evidence_closure_v1(
        controller_output=_controller_output(
            critical_safety_blockers=[],
            missing_evidence_fields=[],
            critical_safety_closed=True,
        )
    )

    assert result["closure_status"] == "SAFETY_CLOSURE_VERIFIED"
    assert result["safety_completion_percent"] == 100.0
    assert result["readiness_delta"] == 0.0
    assert result["verified_controls"] == list(closure.CONTROL_FIELDS)
    assert result["remaining_blockers"] == []
    assert result["controller_routing_recommendation"] == (
        "ROUTE_TO_OFFLINE_AUTONOMY_GOVERNOR_RERUN"
    )


def test_verified_closure_packet_targets_autonomy_governor_rerun_artifacts():
    result = closure.run_forex_critical_safety_evidence_closure_v1(
        controller_output=_controller_output(
            critical_safety_blockers=[],
            missing_evidence_fields=[],
            critical_safety_closed=True,
        )
    )
    packet_text = closure.build_next_codex_packet(result)

    assert "forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py" in packet_text
    assert (
        "run_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py"
        in packet_text
    )
    assert (
        "test_forex_autonomy_completion_governor_rerun_and_bucket_policy_v1.py"
        in packet_text
    )
    assert (
        "AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_STATE.json"
        in packet_text
    )
    assert (
        "AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_REPORT.md"
        in packet_text
    )
    assert (
        "AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_NEXT_CODEX_PACKET_V1.md"
        in packet_text
    )
    assert (
        "forex_critical_safety_evidence_closure_v1.py" not in packet_text
    )
    assert (
        "run_forex_critical_safety_evidence_closure_v1.py" not in packet_text
    )
    validation = aios_governance_validator.validate_packet_text(
        packet_text,
        "<verified-closure-next-packet>",
    )
    assert validation["status"] == "PASS"


def test_partial_controller_output_can_report_present_without_verification():
    result = closure.run_forex_critical_safety_evidence_closure_v1(
        controller_output=_controller_output(
            critical_safety_blockers=["kill_switch_state"],
            missing_evidence_fields=[],
            critical_safety_closed=False,
        )
    )

    assert result["control_evaluations"]["kill_switch_state"]["status"] == (
        closure.STATUS_BLOCKED
    )
    assert result["control_evaluations"]["daily_stop_state"]["status"] == (
        closure.STATUS_PRESENT
    )
    assert result["safety_completion_percent"] == 0.0
    assert "kill_switch_state" in result["blocked_controls"]
    assert "daily_stop_state" in result["present_controls"]


def test_missing_and_unknown_controls_are_not_counted_as_verified():
    missing_result = closure.run_forex_critical_safety_evidence_closure_v1(
        controller_output=_controller_output(
            critical_safety_blockers=[],
            missing_evidence_fields=["daily_stop_state"],
            critical_safety_closed=False,
        )
    )
    unknown_result = closure.run_forex_critical_safety_evidence_closure_v1(
        controller_output={
            "controller_status": "UNKNOWN",
            "current_phase": "UNKNOWN",
            "starting_line_inputs": {"critical_safety_blockers_known": False},
            "blocker_summary": {},
            "finish_line_gates": {},
        }
    )

    assert missing_result["control_evaluations"]["daily_stop_state"]["status"] == (
        closure.STATUS_MISSING
    )
    assert missing_result["safety_completion_percent"] == 0.0
    assert unknown_result["unknown_controls"] == list(closure.CONTROL_FIELDS)
    assert unknown_result["safety_completion_percent"] == 0.0


def test_evidence_freshness_uses_controller_evidence_age_blocker():
    result = closure.run_forex_critical_safety_evidence_closure_v1(
        controller_output=_controller_output(
            critical_safety_blockers=[],
            missing_evidence_fields=["evidence_age_days"],
            critical_safety_closed=False,
        )
    )

    assert result["evidence_freshness"]["status"] == "STALE_OR_MISSING"
    assert result["evidence_freshness"]["freshness_blockers"] == ["evidence_age_days"]


def test_runner_writes_state_report_and_next_packet():
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
    assert state_payload["packet_id"] == closure.PACKET_ID
    assert "Safety completion percent: 0.0%" in report_text
    assert "No broker API was called." in report_text
    assert next_packet_text.startswith("CODEX-ONLY PROMPT")
    assert "MODE\nDRY_RUN" in next_packet_text
    assert "broker execution" not in next_packet_text.lower()
    assert "Do not invent evidence." in next_packet_text
    assert "Do not use broker API." in next_packet_text
    assert "Do not use credentials." in next_packet_text
    assert "Do not read .env." in next_packet_text
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
        / "forex_critical_safety_evidence_closure_v1.py",
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


def test_no_secret_or_account_identifier_fields_are_emitted():
    result = closure.run_forex_critical_safety_evidence_closure_v1()
    output = json.dumps(result, ensure_ascii=True).lower()

    for fragment in (
        '"api_key"',
        '"token"',
        '"password"',
        '"secret"',
        '"account_id"',
        '"broker_id"',
        "oanda",
    ):
        assert fragment not in output


def _controller_output(
    *,
    critical_safety_blockers: list[str],
    missing_evidence_fields: list[str],
    critical_safety_closed: bool,
) -> dict[str, object]:
    return {
        "controller_status": (
            "SAFETY_CLOSURE_CLEAR_FOR_OFFLINE_RERUN"
            if critical_safety_closed
            else "SAFETY_CLOSURE_REQUIRED"
        ),
        "selected_mode": "SAFETY_CLOSURE",
        "current_phase": (
            "SAFETY_CLOSURE_COMPLETE"
            if critical_safety_closed
            else "CRITICAL_SAFETY_EVIDENCE_CLOSURE"
        ),
        "next_safe_action": "controller supplied next action",
        "finish_line_readiness_percent": 0.0,
        "starting_line_readiness_percent": 100.0,
        "blocker_summary": {
            "critical_safety_blockers": critical_safety_blockers,
            "missing_evidence_fields": missing_evidence_fields,
        },
        "finish_line_gates": {
            "critical_safety_evidence_closed": critical_safety_closed,
        },
        "starting_line_inputs": {
            "critical_safety_blockers_known": True,
        },
        "source_artifacts": {
            "completion_state": "Reports/forex_delivery/completion.json",
        },
        "packet_id": "PKT-FOREX-FINISH-LINE-MISSION-CONTROLLER-V1",
        "mission_id": "MISSION-AIOS-FOREX-FINISH-LINE-V1",
    }
