from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path

import pytest

from automation.validators import aios_governance_validator
from automation.forex_engine import forex_finish_line_mission_controller_v1 as controller


ROOT = Path(__file__).resolve().parents[2]
RUNNER_PATH = (
    ROOT / "scripts" / "forex_delivery" / "run_forex_finish_line_mission_controller_v1.py"
)
STATE_OUTPUT_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json"
)
REPORT_OUTPUT_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_REPORT.md"
)
DASHBOARD_OUTPUT_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_FINISH_LINE_EMOJI_DASHBOARD_PROJECTION_V1.json"
)
NEXT_PACKET_OUTPUT_PATH = (
    ROOT
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_NEXT_CODEX_PACKET_V1.md"
)

REQUIRED_DASHBOARD_TILES = {
    "controller",
    "evidence",
    "safety",
    "broker",
    "proof",
    "live_micro",
    "live_trading",
    "vacation_mode",
    "audit",
    "next_action",
}
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
FORBIDDEN_OUTPUT_FRAGMENTS = {
    '"api_key"',
    '"token"',
    '"password"',
    '"secret"',
    '"account_id"',
    '"broker_id"',
    "oanda",
}


def test_starting_line_runs_without_execution_actions():
    result = controller.run_forex_finish_line_mission_controller_v1()

    assert result["selected_mode"] == controller.STARTING_LINE
    assert result["starting_line_readiness_percent"] > 0
    assert result["finish_line_readiness_percent"] < controller.LIVE_READY_THRESHOLD_PERCENT
    assert result["next_safe_action"]
    assert all(value is False for value in result["safety_boundary"].values())
    assert result["safety_boundary"] == controller.SAFETY_BOUNDARY


@pytest.mark.parametrize("mode", controller.LOCKED_EXECUTION_MODES)
def test_locked_modes_remain_locked(mode: str):
    result = controller.run_forex_finish_line_mission_controller_v1(mode=mode)

    assert result["controller_status"] == "MODE_LOCKED"
    assert result["selected_mode"] == mode
    assert result["locked_modes"][mode]
    assert mode not in result["unlocked_modes"]
    assert all(value is False for value in result["safety_boundary"].values())


@pytest.mark.parametrize(
    "mode",
    [
        controller.LIVE_MICRO_LOCKED,
        controller.LIVE_TRADING_LOCKED,
        controller.VACATION_MODE_LOCKED,
    ],
)
def test_live_and_vacation_modes_stay_locked(mode: str):
    result = controller.run_forex_finish_line_mission_controller_v1(mode=mode)

    assert result["controller_status"] == "MODE_LOCKED"
    assert result["emoji_dashboard_projection"]["live_trading"]["locked"] is True
    assert result["emoji_dashboard_projection"]["vacation_mode"]["locked"] is True
    assert result["live_trading_finish_line_target"]["live_trading_authorized"] is False
    assert result["vacation_mode_target"]["locked"] is True


def test_dashboard_projection_is_emoji_first_and_contains_required_tiles():
    result = controller.run_forex_finish_line_mission_controller_v1()
    dashboard = result["emoji_dashboard_projection"]

    assert set(dashboard) == REQUIRED_DASHBOARD_TILES
    for tile_name, tile in dashboard.items():
        assert list(tile.keys())[0] == "emoji", tile_name
        assert tile["emoji"] == controller.EMOJI_BY_TILE[tile_name]
        assert isinstance(tile["locked"], bool)
        assert isinstance(tile["context_box_required"], bool)
        assert "context_box_text" in tile


def test_context_boxes_are_only_used_when_needed():
    result = controller.run_forex_finish_line_mission_controller_v1()
    dashboard = result["emoji_dashboard_projection"]
    expected_context_boxes = {}

    for tile_name, tile in dashboard.items():
        if tile["context_box_required"]:
            assert tile["context_box_text"]
            expected_context_boxes[tile_name] = tile["context_box_text"]
        else:
            assert tile["context_box_text"] == ""

    assert result["context_boxes"] == expected_context_boxes


def test_unknown_mode_is_rejected():
    with pytest.raises(ValueError, match="unknown finish-line mission controller mode"):
        controller.run_forex_finish_line_mission_controller_v1(mode="UNKNOWN")

    completed = subprocess.run(
        [sys.executable, str(RUNNER_PATH), "--mode", "UNKNOWN"],
        capture_output=True,
        encoding="utf-8",
        text=True,
    )
    assert completed.returncode != 0


def test_runner_prints_valid_json():
    completed = subprocess.run(
        [sys.executable, str(RUNNER_PATH), "--mode", controller.STARTING_LINE],
        check=True,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )

    payload = json.loads(completed.stdout)
    assert payload["selected_mode"] == controller.STARTING_LINE
    assert payload["emoji_dashboard_projection"]["controller"]["emoji"]


def test_runner_writes_valid_artifacts():
    completed = subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "--mode",
            controller.STARTING_LINE,
            "--write-state",
            "--write-report",
            "--write-dashboard",
        ],
        check=True,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )
    stdout_payload = json.loads(completed.stdout)

    state_payload = json.loads(STATE_OUTPUT_PATH.read_text(encoding="utf-8"))
    dashboard_payload = json.loads(DASHBOARD_OUTPUT_PATH.read_text(encoding="utf-8"))
    report_text = REPORT_OUTPUT_PATH.read_text(encoding="utf-8")
    next_packet_text = NEXT_PACKET_OUTPUT_PATH.read_text(encoding="utf-8")

    assert stdout_payload["state_output_path"] == str(STATE_OUTPUT_PATH)
    assert stdout_payload["report_output_path"] == str(REPORT_OUTPUT_PATH)
    assert stdout_payload["dashboard_output_path"] == str(DASHBOARD_OUTPUT_PATH)
    assert state_payload["selected_mode"] == controller.STARTING_LINE
    assert set(dashboard_payload) == REQUIRED_DASHBOARD_TILES
    assert report_text.startswith("# AIOS Forex Finish Line Mission Controller V1 Report")
    assert "No broker API was called." in report_text
    assert next_packet_text.startswith("CODEX-ONLY PROMPT")
    assert "MODE\nDRY_RUN" in next_packet_text
    assert "BRANCH\nresolve after preflight" in next_packet_text
    assert "BRANCH\nmain" not in next_packet_text
    assert "\nPREFLIGHT\n" in next_packet_text
    assert "\nPRECHECK\n" not in next_packet_text
    assert "\nSAFE NEXT ACTION\n" in next_packet_text
    assert "--write-state" not in next_packet_text
    assert "--write-report" not in next_packet_text
    assert "--write-dashboard" not in next_packet_text
    assert (
        "python scripts/forex_delivery/run_forex_finish_line_mission_controller_v1.py --mode STARTING_LINE" in next_packet_text
        or "python scripts/forex_delivery/run_forex_critical_safety_evidence_closure_v1.py" in next_packet_text
        or "python scripts/forex_delivery/run_forex_autonomy_sanitized_evidence_intake_update_v1.py" in next_packet_text
    )
    assert "Do not place trades." in next_packet_text
    assert "Do not use broker API." in next_packet_text
    assert "Do not use credentials." in next_packet_text
    assert "Do not authorize live trading." in next_packet_text
    validation = aios_governance_validator.validate_packet_text(
        next_packet_text,
        str(NEXT_PACKET_OUTPUT_PATH),
    )
    assert validation["status"] == "PASS"


def test_state_and_dashboard_json_validate_after_runner_write():
    subprocess.run(
        [
            sys.executable,
            str(RUNNER_PATH),
            "--mode",
            controller.STARTING_LINE,
            "--write-state",
            "--write-report",
            "--write-dashboard",
        ],
        check=True,
        capture_output=True,
        encoding="utf-8",
        text=True,
    )

    state_payload = json.loads(STATE_OUTPUT_PATH.read_text(encoding="utf-8"))
    dashboard_payload = json.loads(DASHBOARD_OUTPUT_PATH.read_text(encoding="utf-8"))

    assert isinstance(state_payload, dict)
    assert isinstance(dashboard_payload, dict)
    assert state_payload["emoji_dashboard_projection"] == dashboard_payload


def test_explicit_empty_blocked_evidence_fields_are_honored():
    stale_completion_state = {
        "governor_blockers": [
            "kill switch state is 'UNKNOWN'",
            "daily stop state is 'UNKNOWN'",
            "max loss state is not configured",
            "monitoring readiness is false",
        ]
    }

    assert (
        controller._critical_safety_blockers(
            {"blocked_evidence_fields": []},
            stale_completion_state,
        )
        == []
    )


def test_explicit_blocked_evidence_fields_filter_to_critical_safety_controls():
    stale_completion_state = {
        "governor_blockers": [
            "daily stop state is 'UNKNOWN'",
            "max loss state is not configured",
        ]
    }

    assert controller._critical_safety_blockers(
        {"blocked_evidence_fields": ["kill_switch_state", "owner_approval_status"]},
        stale_completion_state,
    ) == ["kill_switch_state"]


def test_explicit_noncritical_blocked_evidence_fields_are_not_safety_blockers():
    stale_completion_state = {
        "governor_blockers": [
            "kill switch state is 'UNKNOWN'",
            "daily stop state is 'UNKNOWN'",
        ]
    }

    assert (
        controller._critical_safety_blockers(
            {
                "blocked_evidence_fields": [
                    "owner_approval_status",
                    "order_count_last_24h",
                ]
            },
            stale_completion_state,
        )
        == []
    )


def test_empty_blocked_fields_with_missing_evidence_age_keeps_safety_gate_open():
    intake_state = {
        "blocked_evidence_fields": [],
        "missing_evidence_fields": ["evidence_age_days"],
    }
    critical_blockers = controller._critical_safety_blockers(intake_state, {})
    gates = controller._build_finish_line_gates(
        completion_state={},
        intake_state=intake_state,
        critical_safety_blockers=critical_blockers,
        missing_evidence_fields=["evidence_age_days"],
    )

    assert critical_blockers == []
    assert gates["critical_safety_evidence_closed"] is False


def test_noncritical_blocked_fields_with_missing_evidence_age_keep_safety_gate_open():
    intake_state = {
        "blocked_evidence_fields": ["owner_approval_status"],
        "missing_evidence_fields": ["evidence_age_days"],
    }
    critical_blockers = controller._critical_safety_blockers(intake_state, {})
    gates = controller._build_finish_line_gates(
        completion_state={},
        intake_state=intake_state,
        critical_safety_blockers=critical_blockers,
        missing_evidence_fields=["evidence_age_days"],
    )

    assert critical_blockers == []
    assert gates["critical_safety_evidence_closed"] is False


@pytest.mark.parametrize(
    ("missing_fields", "expected_closed"),
    [
        (["sample_size"], True),
        (["profit_factor"], True),
        (["evidence_age_days"], False),
        (["kill_switch_state"], False),
        (["daily_stop_state"], False),
        (["max_loss_state"], False),
        (["monitoring_ready"], False),
        (["order_count_last_24h", "candidate_id", "sample_size", "profit_factor"], True),
    ],
)
def test_critical_safety_evidence_gate_ignores_unrelated_missing_fields(
    missing_fields: list[str],
    expected_closed: bool,
) -> None:
    intake_state = {
        "blocked_evidence_fields": [],
    }
    critical_blockers = controller._critical_safety_blockers(intake_state, {})
    gates = controller._build_finish_line_gates(
        completion_state={},
        intake_state=intake_state,
        critical_safety_blockers=critical_blockers,
        missing_evidence_fields=missing_fields,
    )

    assert gates["critical_safety_evidence_closed"] is expected_closed


def test_critical_safety_evidence_gate_fails_on_stale_blockers_in_completion_state():
    completion_state = {"governor_blockers": ["evidence freshness is 40 days"]}
    intake_state = {
        "blocked_evidence_fields": [],
    }
    gates = controller._build_finish_line_gates(
        completion_state=completion_state,
        intake_state=intake_state,
        critical_safety_blockers=[],
        missing_evidence_fields=[],
    )

    assert gates["critical_safety_evidence_closed"] is False


def test_completion_stale_freshness_blocker_exposed_to_status_phase_summary_and_next_packet_route():
    completion_state = {
        "governor_blockers": ["evidence freshness is 40 days"],
    }
    intake_state = {
        "blocked_evidence_fields": [],
    }
    critical_safety_blockers = controller._critical_safety_blockers(
        intake_state,
        completion_state,
    )
    effective_missing_evidence_fields = controller._safety_missing_evidence_fields(
        completion_state=completion_state,
        intake_state=intake_state,
        missing_evidence_fields=[],
    )
    gates = controller._build_finish_line_gates(
        completion_state=completion_state,
        intake_state=intake_state,
        critical_safety_blockers=critical_safety_blockers,
        missing_evidence_fields=effective_missing_evidence_fields,
    )

    assert critical_safety_blockers == []
    assert effective_missing_evidence_fields == ["evidence freshness is 40 days"]
    assert gates["critical_safety_evidence_closed"] is False
    assert (
        controller._controller_status(
            controller.SAFETY_CLOSURE,
            critical_safety_blockers,
            effective_missing_evidence_fields,
        )
        == "SAFETY_CLOSURE_MISSING_EVIDENCE_COLLECTION_REQUIRED"
    )
    assert (
        controller._current_phase(
            controller.SAFETY_CLOSURE,
            critical_safety_blockers,
            effective_missing_evidence_fields,
        )
        == "MISSING_SANITIZED_EVIDENCE_COLLECTION_PENDING"
    )

    blocker_summary = controller._build_blocker_summary(
        completion_state=completion_state,
        intake_state=intake_state,
        critical_safety_blockers=critical_safety_blockers,
        missing_evidence_fields=effective_missing_evidence_fields,
        finish_line_gates=gates,
    )

    assert (
        "evidence freshness is 40 days"
        in blocker_summary["missing_evidence_fields"]
    )
    packet_text = controller.build_next_codex_packet(
        {"blocker_summary": blocker_summary}
    )

    assert (
        "Missing Sanitized Evidence Collection Dry Run V1"
        in packet_text
    )
    assert (
        "Collect missing sanitized evidence for"
        in packet_text
    )
    assert "Offline Autonomy Controller Rerun" not in packet_text
    assert (
        "PKT-FOREX-MISSING-SANITIZED-EVIDENCE-COLLECTION-DRY-RUN-V1"
        in packet_text
    )
    assert (
        "forex_autonomy_sanitized_evidence_intake_update_v1.py"
        in packet_text
    )
    assert "forex_finish_line_mission_controller_v1.py" not in packet_text
    validation = aios_governance_validator.validate_packet_text(
        packet_text,
        "<derived-stale-next-packet>",
    )
    assert validation["status"] == "PASS"


def test_raw_non_safety_missing_fields_do_not_block_safety_closure_status_and_phase():
    for missing_fields in (["sample_size"], ["profit_factor"]):
        critical_safety_blockers = controller._critical_safety_blockers(
            {"blocked_evidence_fields": []},
            {},
        )
        effective_missing_evidence_fields = controller._safety_missing_evidence_fields(
            completion_state={},
            intake_state={},
            missing_evidence_fields=missing_fields,
        )
        gates = controller._build_finish_line_gates(
            completion_state={},
            intake_state={"blocked_evidence_fields": []},
            critical_safety_blockers=critical_safety_blockers,
            missing_evidence_fields=effective_missing_evidence_fields,
        )

        assert effective_missing_evidence_fields == []
        assert gates["critical_safety_evidence_closed"] is True
        assert (
            controller._controller_status(
                controller.SAFETY_CLOSURE,
                critical_safety_blockers,
                effective_missing_evidence_fields,
            )
            == "SAFETY_CLOSURE_CLEAR_FOR_OFFLINE_RERUN"
        )
        assert (
            controller._current_phase(
                controller.SAFETY_CLOSURE,
                critical_safety_blockers,
                effective_missing_evidence_fields,
            )
            == "SAFETY_CLOSURE_COMPLETE"
        )


def test_raw_evidence_age_days_missing_blocks_safety_status_phase():
    critical_safety_blockers = controller._critical_safety_blockers(
        {"blocked_evidence_fields": []},
        {},
    )
    effective_missing_evidence_fields = controller._safety_missing_evidence_fields(
        completion_state={},
        intake_state={},
        missing_evidence_fields=["evidence_age_days"],
    )
    gates = controller._build_finish_line_gates(
        completion_state={},
        intake_state={"blocked_evidence_fields": []},
        critical_safety_blockers=critical_safety_blockers,
        missing_evidence_fields=effective_missing_evidence_fields,
    )

    assert effective_missing_evidence_fields == ["evidence_age_days"]
    assert gates["critical_safety_evidence_closed"] is False
    assert (
        controller._controller_status(
            controller.SAFETY_CLOSURE,
            critical_safety_blockers,
            effective_missing_evidence_fields,
        )
        == "SAFETY_CLOSURE_MISSING_EVIDENCE_COLLECTION_REQUIRED"
    )
    assert (
        controller._current_phase(
            controller.SAFETY_CLOSURE,
            critical_safety_blockers,
            effective_missing_evidence_fields,
        )
        == "MISSING_SANITIZED_EVIDENCE_COLLECTION_PENDING"
    )


def test_critical_safety_blocker_next_packet_targets_closure_artifacts():
    packet_text = controller.build_next_codex_packet(
        {
            "blocker_summary": {
                "critical_safety_blockers": ["kill_switch_state"],
                "missing_evidence_fields": [],
            }
        }
    )

    assert "forex_critical_safety_evidence_closure_v1.py" in packet_text
    assert "run_forex_critical_safety_evidence_closure_v1.py" in packet_text
    assert "test_forex_critical_safety_evidence_closure_v1.py" in packet_text
    assert (
        "AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_STATE.json" in packet_text
    )
    assert (
        "AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_V1_REPORT.md" in packet_text
    )
    assert (
        "AIOS_FOREX_CRITICAL_SAFETY_EVIDENCE_CLOSURE_NEXT_CODEX_PACKET_V1.md"
        in packet_text
    )
    assert (
        "AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_V1_STATE.json"
        not in packet_text
    )
    assert (
        "forex_finish_line_mission_controller_v1.py" not in packet_text
    )
    assert (
        "run_forex_finish_line_mission_controller_v1.py" not in packet_text
    )
    assert (
        "AIOS_FOREX_FINISH_LINE_MISSION_CONTROLLER_NEXT_CODEX_PACKET_V1.md"
        not in packet_text
    )
    validation = aios_governance_validator.validate_packet_text(
        packet_text,
        "<critical-safety-blocker-next-packet>",
    )
    assert validation["status"] == "PASS"


@pytest.mark.parametrize(
    ("mode", "expected_status"),
    [
        (
            controller.STARTING_LINE,
            "STARTING_LINE_MISSING_EVIDENCE_COLLECTION_REQUIRED",
        ),
        (
            controller.SAFETY_CLOSURE,
            "SAFETY_CLOSURE_MISSING_EVIDENCE_COLLECTION_REQUIRED",
        ),
    ],
)
def test_missing_evidence_status_and_phase_do_not_claim_rerun_ready(
    mode,
    expected_status,
):
    missing_fields = ["sample_size"]

    assert controller._controller_status(mode, [], missing_fields) == expected_status
    assert (
        controller._current_phase(mode, [], missing_fields)
        == "MISSING_SANITIZED_EVIDENCE_COLLECTION_PENDING"
    )


@pytest.mark.parametrize("missing_fields", [["sample_size"], ["evidence_age_days"]])
def test_missing_evidence_routes_to_collection_packet_before_rerun(missing_fields):
    packet_text = controller.build_next_codex_packet(
        {
            "blocker_summary": {
                "critical_safety_blockers": [],
                "missing_evidence_fields": missing_fields,
            }
        }
    )

    assert "Offline Autonomy Controller Rerun" not in packet_text
    assert "PKT-FOREX-OFFLINE-AUTONOMY-CONTROLLER-RERUN" not in packet_text
    assert "Missing Sanitized Evidence Collection Dry Run V1" in packet_text
    assert "Collect missing sanitized evidence" in packet_text
    assert "forex_autonomy_sanitized_evidence_intake_update_v1.py" in packet_text
    assert "run_forex_autonomy_sanitized_evidence_intake_update_v1.py" in packet_text
    assert "forex_finish_line_mission_controller_v1.py" not in packet_text
    assert "run_forex_finish_line_mission_controller_v1.py" not in packet_text
    assert "\nPREFLIGHT\n" in packet_text
    assert "\nALLOWED PATHS\n" in packet_text
    assert "\nVALIDATOR CHAIN\n" in packet_text
    assert "\nFINAL REPORT FORMAT\n" in packet_text
    assert "\nSAFE NEXT ACTION\n" in packet_text
    assert "scheduler, daemon, and webhook paths locked" in packet_text

    validation = aios_governance_validator.validate_packet_text(
        packet_text,
        "<missing-evidence-next-packet>",
    )
    assert validation["status"] == "PASS"


def test_missing_blocked_evidence_fields_falls_back_to_governor_blockers():
    completion_state = {
        "governor_blockers": [
            "kill switch state is 'UNKNOWN'",
            "daily stop state is 'UNKNOWN'",
            "max loss state is not configured",
            "monitoring readiness is false",
        ]
    }

    assert controller._critical_safety_blockers({}, completion_state) == [
        "kill_switch_state",
        "daily_stop_state",
        "max_loss_state",
        "monitoring_ready",
    ]


def test_starting_line_reports_current_real_safety_blockers():
    result = controller.run_forex_finish_line_mission_controller_v1()

    assert result["controller_status"] == "STARTING_LINE_READY_WITH_SAFETY_BLOCKERS"
    assert result["current_phase"] == "SAFETY_EVIDENCE_CLOSURE_PENDING"
    assert result["blocker_summary"]["critical_safety_blockers"] == [
        "kill_switch_state",
        "daily_stop_state",
        "max_loss_state",
        "monitoring_ready",
    ]


def test_no_forbidden_imports_or_environment_access():
    for path in [
        controller.ROOT
        / "automation"
        / "forex_engine"
        / "forex_finish_line_mission_controller_v1.py",
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
    result = controller.run_forex_finish_line_mission_controller_v1()
    output = json.dumps(result, ensure_ascii=False).lower()

    for fragment in FORBIDDEN_OUTPUT_FRAGMENTS:
        assert fragment not in output
