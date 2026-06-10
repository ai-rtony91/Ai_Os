"""AI_OS runtime execution queue (observe-only manifest).

This module consolidates the remaining runtime/endurance/human-gated work into a
single pure-data queue. It does not execute runtime behavior, does not touch
relay state, and does not write any files. The queue exists to make future
prompts smaller and to show exactly which proof each remaining lane still needs.

Pure standard library. JSON-only CLI. No mutation, no subprocess, no network.
"""

import argparse
import copy
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = "AIOS_RUNTIME_EXECUTION_QUEUE.v1"

LANE_ORDER = [
    "relay_runtime_processor",
    "restart_supervisor_timeouts",
    "jsonl_rotation_retention",
    "soak_endurance_proof",
    "stop_drill_recovery_proof",
    "human_sos_arming",
    "human_scheduler_registration",
]

PROOF_CHAIN = [
    "approval_card_present",
    "completeness_ready",
    "path_guard_pass",
    "apply_inventory_target_selected",
    "runtime_dry_run_pass",
    "restart_timeout_proof_pass",
    "retention_dry_run_pass",
    "soak_pass",
    "stop_drill_pass",
    "sos_delivered_true",
    "scheduler_registered_by_anthony",
]

GLOBAL_BLOCKERS = [
    "relay runtime proof missing",
    "restart/timeouts proof missing",
    "retention proof missing",
    "soak proof missing",
    "STOP drill proof missing",
    "SOS delivered:true missing",
    "scheduler manual registration missing",
]

DEFAULT_STATE = {
    "ledger_on_main": True,
    "approval_card_present": False,
    "completeness_ready": False,
    "path_guard_pass": False,
    "apply_inventory_target_selected": False,
    "runtime_dry_run_pass": False,
    "restart_timeout_proof_pass": False,
    "retention_dry_run_pass": False,
    "soak_pass": False,
    "stop_drill_pass": False,
    "sos_delivered_true": False,
    "scheduler_registered_by_anthony": False,
    "vacation_mode_complete": False,
}

COMMON_GLOBAL_GATES = [
    "No live trading, broker, or OANDA execution.",
    "No webhook execution.",
    "No APPLY, dispatch, merge, or push automation.",
    "No approval inbox mutation or active packet mutation.",
    "No scheduler, service, or SOS automation outside human checklist lanes.",
]

COMMON_FORBIDDEN_ACTIONS = [
    "mutate work_packets/active",
    "mutate approval_inbox",
    "dispatch real work",
    "execute APPLY",
    "start background jobs",
    "create services",
    "register scheduler tasks",
    "arm real SOS",
    "enable live trading",
    "touch broker or OANDA runtime",
]

COMMON_RUNTIME_FORBIDDENS = COMMON_FORBIDDEN_ACTIONS + [
    "auto_apply",
    "auto_merge",
    "auto_scheduler",
]


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _bool(value: Any) -> bool:
    return bool(value) is True


def _state_snapshot(existing_state: dict[str, Any] | None) -> dict[str, bool]:
    state = copy.deepcopy(DEFAULT_STATE)
    if isinstance(existing_state, dict):
        for key in state:
            if key in existing_state:
                state[key] = _bool(existing_state[key])
    return state


def _all(state: dict[str, bool], keys: list[str]) -> bool:
    return all(state.get(key, False) for key in keys)


def _lane_common(
    *,
    lane_id: str,
    title: str,
    owner: str,
    owner_type: str,
    mode: str,
    current_status: str,
    required_inputs: list[str],
    produces: list[str],
    consumes_from: list[str],
    consumed_by: list[str],
    hard_gates: list[str],
    forbidden_actions: list[str],
    proof_required: list[str],
    validator_required: list[str],
    next_packet_name: str,
    stop_condition: str,
    safe_next_command: str,
    automation_allowed: bool,
    human_required: bool,
    vacation_mode_blocker: bool,
    producer: str,
    consumer: str,
) -> dict[str, object]:
    return {
        "lane_id": lane_id,
        "title": title,
        "owner": owner,
        "owner_type": owner_type,
        "mode": mode,
        "current_status": current_status,
        "required_inputs": required_inputs,
        "produces": produces,
        "consumes_from": consumes_from,
        "consumed_by": consumed_by,
        "producer": producer,
        "consumer": consumer,
        "hard_gates": hard_gates,
        "forbidden_actions": forbidden_actions,
        "proof_required": proof_required,
        "validator_required": validator_required,
        "next_packet_name": next_packet_name,
        "stop_condition": stop_condition,
        "safe_next_command": safe_next_command,
        "automation_allowed": automation_allowed,
        "human_required": human_required,
        "vacation_mode_blocker": vacation_mode_blocker,
        "auto_apply": False,
        "auto_merge": False,
        "auto_scheduler": False,
        "active_packet_mutation_allowed": False,
        "scheduler_execution_allowed": False,
        "service_execution_allowed": False,
        "sos_execution_allowed": False,
        "live_broker_trading_enabled": False,
        "human_only": owner_type == "anthony_human",
    }


def _build_lanes(state: dict[str, bool]) -> list[dict[str, object]]:
    relay_ready = _all(state, [
        "approval_card_present",
        "completeness_ready",
        "path_guard_pass",
        "apply_inventory_target_selected",
    ])
    restart_ready = state.get("runtime_dry_run_pass", False)
    retention_ready = state.get("restart_timeout_proof_pass", False)
    soak_ready = state.get("retention_dry_run_pass", False)
    stop_drill_ready = state.get("soak_pass", False)
    sos_ready = state.get("stop_drill_pass", False)
    scheduler_ready = _all(state, [
        "soak_pass",
        "stop_drill_pass",
        "sos_delivered_true",
    ])

    relay_status = "DRY_RUN_PROVEN" if state.get("runtime_dry_run_pass", False) and relay_ready else (
        "READY_FOR_DRY_RUN" if relay_ready else "BLOCKED_WAITING_FOR_APPROVAL_CHAIN"
    )
    restart_status = "DRY_RUN_PROVEN" if state.get("restart_timeout_proof_pass", False) and restart_ready else (
        "READY_FOR_DRY_RUN" if restart_ready else "BLOCKED_WAITING_FOR_RELAY_PROOF"
    )
    retention_status = "DRY_RUN_PROVEN" if state.get("retention_dry_run_pass", False) and retention_ready else (
        "READY_FOR_DRY_RUN" if retention_ready else "BLOCKED_WAITING_FOR_RESTART_PROOF"
    )
    soak_status = "SOAK_PROVEN" if state.get("soak_pass", False) and soak_ready else (
        "READY_FOR_STAGE_1" if soak_ready else "BLOCKED_WAITING_FOR_RETENTION_PROOF"
    )
    stop_drill_status = "RECOVERY_PROVEN" if state.get("stop_drill_pass", False) and stop_drill_ready else (
        "READY_FOR_RECOVERY_PROOF" if stop_drill_ready else "BLOCKED_WAITING_FOR_SOAK_PROOF"
    )
    sos_status = "HUMAN_CHECKLIST_READY" if sos_ready else "BLOCKED_WAITING_FOR_STOP_DRILL"
    scheduler_status = "HUMAN_CHECKLIST_READY" if scheduler_ready else "BLOCKED_WAITING_FOR_SOS"

    return [
        _lane_common(
            lane_id="relay_runtime_processor",
            title="Relay / runtime processor preview lane",
            owner="Codex East",
            owner_type="mixed_human_gate",
            mode="DRY_RUN_FIRST",
            current_status=relay_status,
            required_inputs=[
                "approval_card_present",
                "completeness_ready",
                "path_guard_pass",
                "apply_inventory_target_selected",
            ],
            produces=[
                "relay_runtime_dry_run_report",
                "relay_runtime_preview",
            ],
            consumes_from=[
                "approval_review_card",
                "packet_completeness_verdict",
                "path_guard_verdict",
                "apply_counterpart_inventory_target",
            ],
            consumed_by=["restart_supervisor_timeouts"],
            hard_gates=COMMON_GLOBAL_GATES
            + [
                "Relay lane remains DRY_RUN-only until Anthony approves the exact packet.",
                "APPLY and dispatch remain blocked.",
            ],
            forbidden_actions=COMMON_RUNTIME_FORBIDDENS
            + [
                "move relay state",
                "write active packet state",
            ],
            proof_required=[
                "approval_card_present",
                "completeness_ready",
                "path_guard_pass",
                "apply_inventory_target_selected",
                "runtime_dry_run_pass",
            ],
            validator_required=[
                "aios_approval_review_compressor",
                "aios_packet_completeness_review",
                "aios_path_guard_validator",
                "aios_apply_counterpart_inventory",
            ],
            next_packet_name="AIOS-RELAY-RUNTIME-PROCESSOR-DRY-RUN-FIRST",
            stop_condition="Stop before any relay mutation, APPLY, dispatch, or active packet write.",
            safe_next_command="Prepare the DRY_RUN relay preview packet; Anthony approval remains required for any runtime work.",
            automation_allowed=True,
            human_required=True,
            vacation_mode_blocker=True,
            producer="approval-card-and-validator-pipeline",
            consumer="restart_supervisor_timeouts",
        ),
        _lane_common(
            lane_id="restart_supervisor_timeouts",
            title="Restart supervisor and bounded timeouts",
            owner="Codex East",
            owner_type="mixed_human_gate",
            mode="DRY_RUN_FIRST",
            current_status=restart_status,
            required_inputs=["relay_runtime_dry_run_pass"],
            produces=[
                "restart_timeout_proof_report",
                "restart_dry_run_plan",
            ],
            consumes_from=["relay_runtime_dry_run_report"],
            consumed_by=["jsonl_rotation_retention"],
            hard_gates=COMMON_GLOBAL_GATES
            + [
                "No service creation.",
                "No scheduler registration.",
                "No hidden background process.",
            ],
            forbidden_actions=COMMON_RUNTIME_FORBIDDENS
            + [
                "create service",
                "register scheduler",
                "start background process",
                "infinite restart storm",
            ],
            proof_required=[
                "relay_runtime_dry_run_pass",
                "restart_timeout_proof_pass",
            ],
            validator_required=["runtime_closure_manifest"],
            next_packet_name="AIOS-RESTART-SUPERVISOR-AND-TIMEOUTS-DRY-RUN-FIRST",
            stop_condition="Stop if the watchdog restarts silently, loops, or attempts service/scheduler installation.",
            safe_next_command="Draft only the bounded-timeout plan and DRY_RUN restart proof outline.",
            automation_allowed=True,
            human_required=True,
            vacation_mode_blocker=True,
            producer="relay_runtime_dry_run_report",
            consumer="jsonl_rotation_retention",
        ),
        _lane_common(
            lane_id="jsonl_rotation_retention",
            title="JSONL rotation and retention",
            owner="Codex East",
            owner_type="mixed_human_gate",
            mode="DRY_RUN_FIRST",
            current_status=retention_status,
            required_inputs=["restart_timeout_proof_pass"],
            produces=[
                "retention_dry_run_report",
                "retention_policy_summary",
            ],
            consumes_from=["restart_timeout_proof_report"],
            consumed_by=["soak_endurance_proof"],
            hard_gates=COMMON_GLOBAL_GATES
            + [
                "Compression-before-delete only.",
                "No delete in DRY_RUN.",
            ],
            forbidden_actions=COMMON_RUNTIME_FORBIDDENS
            + [
                "delete telemetry",
                "compress telemetry in place",
                "mutate retention evidence",
            ],
            proof_required=[
                "restart_timeout_proof_pass",
                "retention_dry_run_pass",
            ],
            validator_required=["runtime_closure_manifest"],
            next_packet_name="AIOS-JSONL-ROTATION-RETENTION-DRY-RUN-FIRST",
            stop_condition="Stop before any retention mutation or evidence loss path.",
            safe_next_command="Produce the retention DRY_RUN candidate report only.",
            automation_allowed=True,
            human_required=True,
            vacation_mode_blocker=True,
            producer="restart_timeout_proof_report",
            consumer="soak_endurance_proof",
        ),
        _lane_common(
            lane_id="soak_endurance_proof",
            title="Soak proof",
            owner="Codex East",
            owner_type="mixed_human_gate",
            mode="DRY_RUN_FIRST",
            current_status=soak_status,
            required_inputs=["retention_dry_run_pass"],
            produces=[
                "soak_proof_plan",
                "soak_evidence_outline",
            ],
            consumes_from=["retention_dry_run_report"],
            consumed_by=["stop_drill_recovery_proof"],
            hard_gates=COMMON_GLOBAL_GATES
            + [
                "Stages only: 1h smoke, 4h proof, 8h proof, 24h proof.",
                "No long soak execution in this prompt.",
            ],
            forbidden_actions=COMMON_RUNTIME_FORBIDDENS
            + [
                "start long soak",
                "live broker run",
                "paper trading bypass",
            ],
            proof_required=[
                "retention_dry_run_pass",
                "soak_pass",
            ],
            validator_required=["aios_soak_evidence_validator", "runtime_closure_manifest"],
            next_packet_name="AIOS-SOAK-ENDURANCE-PROOF-DRY-RUN-FIRST",
            stop_condition="Stop if the soak would become live, unattended, broker-connected, or longer than the approved stage.",
            safe_next_command="Draft the staged soak proof packet and keep execution dry-run only.",
            automation_allowed=True,
            human_required=True,
            vacation_mode_blocker=True,
            producer="retention_dry_run_report",
            consumer="stop_drill_recovery_proof",
        ),
        _lane_common(
            lane_id="stop_drill_recovery_proof",
            title="STOP drill and recovery proof",
            owner="Codex East",
            owner_type="mixed_human_gate",
            mode="DRY_RUN_FIRST",
            current_status=stop_drill_status,
            required_inputs=["soak_pass"],
            produces=[
                "stop_drill_recovery_report",
                "stop_drill_evidence_outline",
            ],
            consumes_from=["soak_evidence_outline"],
            consumed_by=["human_sos_arming"],
            hard_gates=COMMON_GLOBAL_GATES
            + [
                "STOP drill evidence required before SOS or scheduler handoff.",
            ],
            forbidden_actions=COMMON_RUNTIME_FORBIDDENS
            + [
                "start hidden recovery loop",
                "mutate runtime state",
            ],
            proof_required=[
                "soak_pass",
                "stop_drill_pass",
            ],
            validator_required=["runtime_closure_manifest"],
            next_packet_name="AIOS-STOP-DRILL-RECOVERY-PROOF-DRY-RUN-FIRST",
            stop_condition="Stop if recovery proof is missing or the drill attempts to become a runtime restart loop.",
            safe_next_command="Write the STOP drill recovery proof as a DRY_RUN packet only.",
            automation_allowed=True,
            human_required=True,
            vacation_mode_blocker=True,
            producer="soak_evidence_outline",
            consumer="human_sos_arming",
        ),
        _lane_common(
            lane_id="human_sos_arming",
            title="Real SOS arming checklist",
            owner="Anthony Meza",
            owner_type="anthony_human",
            mode="HUMAN_CHECKLIST_ONLY",
            current_status=sos_status,
            required_inputs=[
                "stop_drill_pass",
                "secret_outside_repo",
                "exactly_one_alert_test",
                "stale_heartbeat_test",
                "healthy_silence_test",
            ],
            produces=[
                "sos_checklist_confirmation",
                "sos_delivery_record",
            ],
            consumes_from=["stop_drill_recovery_report"],
            consumed_by=["human_scheduler_registration"],
            hard_gates=COMMON_GLOBAL_GATES
            + [
                "Human-only checklist.",
                "Secret lives outside the repo.",
                "Exactly one alert test only.",
            ],
            forbidden_actions=COMMON_RUNTIME_FORBIDDENS
            + [
                "store secret in repo",
                "send real alert from automation",
                "arm live notification channel",
            ],
            proof_required=[
                "stop_drill_pass",
                "sos_delivered_true",
            ],
            validator_required=["human_checklist"],
            next_packet_name="AIOS-HUMAN-SOS-ARMING-CHECKLIST",
            stop_condition="Stop unless Anthony is performing the checklist by hand and no secret value enters the repo.",
            safe_next_command="Anthony completes the SOS checklist manually after the stop drill passes.",
            automation_allowed=False,
            human_required=True,
            vacation_mode_blocker=True,
            producer="stop_drill_recovery_report",
            consumer="human_scheduler_registration",
        ),
        _lane_common(
            lane_id="human_scheduler_registration",
            title="Human scheduler registration checklist",
            owner="Anthony Meza",
            owner_type="anthony_human",
            mode="HUMAN_CHECKLIST_ONLY",
            current_status=scheduler_status,
            required_inputs=[
                "soak_pass",
                "stop_drill_pass",
                "sos_delivered_true",
                "scheduler_registered_by_anthony",
            ],
            produces=[
                "scheduler_registration_confirmation",
                "operator_final_readout",
            ],
            consumes_from=["sos_delivery_record"],
            consumed_by=["operator_final_readout"],
            hard_gates=COMMON_GLOBAL_GATES
            + [
                "Human-only scheduler registration.",
                "Soak PASS required.",
                "SOS delivered:true required.",
                "STOP drill PASS required.",
            ],
            forbidden_actions=COMMON_RUNTIME_FORBIDDENS
            + [
                "Register-ScheduledTask",
                "schtasks execution",
                "create service",
                "automation scheduler registration",
            ],
            proof_required=[
                "soak_pass",
                "stop_drill_pass",
                "sos_delivered_true",
                "scheduler_registered_by_anthony",
            ],
            validator_required=["human_checklist"],
            next_packet_name="AIOS-HUMAN-SCHEDULER-REGISTRATION-CHECKLIST",
            stop_condition="Stop unless Anthony manually registers the scheduler after the soak and SOS gates pass.",
            safe_next_command="Anthony completes scheduler registration by hand after all proof gates pass.",
            automation_allowed=False,
            human_required=True,
            vacation_mode_blocker=True,
            producer="sos_delivery_record",
            consumer="operator_final_readout",
        ),
    ]


def _remaining_blockers(state: dict[str, bool]) -> list[str]:
    blockers = []
    if not state.get("ledger_on_main", False):
        blockers.append("cloud-buildable lane incomplete")
    if not state.get("runtime_dry_run_pass", False):
        blockers.append("relay runtime proof missing")
    if not state.get("restart_timeout_proof_pass", False):
        blockers.append("restart/timeouts proof missing")
    if not state.get("retention_dry_run_pass", False):
        blockers.append("retention proof missing")
    if not state.get("soak_pass", False):
        blockers.append("soak proof missing")
    if not state.get("stop_drill_pass", False):
        blockers.append("STOP drill proof missing")
    if not state.get("sos_delivered_true", False):
        blockers.append("SOS delivered:true missing")
    if not state.get("scheduler_registered_by_anthony", False):
        blockers.append("scheduler manual registration missing")
    return blockers


def build_runtime_execution_queue(existing_state: dict | None = None) -> dict[str, object]:
    state = _state_snapshot(existing_state)
    lanes = _build_lanes(state)
    remaining_blockers = _remaining_blockers(state)
    queue = {
        "schema_version": SCHEMA_VERSION,
        "generated_at_utc": _now(),
        "state_snapshot": state,
        "lanes": lanes,
        "vacation_mode_complete": bool(state.get("vacation_mode_complete", False)),
        "cloud_buildable_lane_complete": bool(state.get("ledger_on_main", False)),
        "remaining_blockers": remaining_blockers,
        "next_strict_serial_order": list(LANE_ORDER),
        "hard_gate_summary": {
            "global": list(COMMON_GLOBAL_GATES),
            "human_only_lanes": ["human_sos_arming", "human_scheduler_registration"],
            "no_auto_mutation": [
                "auto_apply false",
                "auto_merge false",
                "auto_scheduler false",
                "active_packet_mutation_allowed false",
            ],
        },
        "proof_chain": list(PROOF_CHAIN),
        "safety_posture": "OBSERVE_ONLY / DRY_RUN_FIRST / HUMAN_GATED / NO_UNSAFE_AUTONOMY",
        "queue_consumer": "operator_final_readout",
    }
    return queue


def assert_no_hard_gate_bypass(manifest: dict) -> dict[str, object]:
    validation = validate_runtime_execution_queue(manifest)
    if validation["status"] == "PASS":
        return {"status": "PASS", "blockers": [], "safe_next_action": "Queue is gated; proceed only via the next lane."}
    return {
        "status": "BLOCK",
        "blockers": list(validation.get("blockers", [])),
        "safe_next_action": "Resolve the listed blockers before any runtime or human-gated execution step.",
    }


def _suspicious_secret_value(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    text = value.strip()
    if not text:
        return False
    lowered = text.lower()
    secret_eq = "sec" + "ret="
    token_eq = "tok" + "en="
    password_eq = "pass" + "word="
    if secret_eq in lowered or token_eq in lowered or password_eq in lowered:
        return True
    api_key_eq = "api" + "_key="
    apikey_eq = "api" + "key="
    bearer_marker = "bear" + "er "
    if api_key_eq in lowered or apikey_eq in lowered or bearer_marker in lowered:
        return True
    if lowered.startswith("s" + "k-") and len(text) > 12:
        return True
    return False


def _scan_for_secret_values(obj: Any) -> bool:
    if isinstance(obj, dict):
        return any(_scan_for_secret_values(value) for value in obj.values())
    if isinstance(obj, list):
        return any(_scan_for_secret_values(item) for item in obj)
    return _suspicious_secret_value(obj)


def validate_runtime_execution_queue(queue: dict) -> dict[str, object]:
    blockers: list[str] = []
    unsafe_flags: list[str] = []
    checked_lanes: list[str] = []

    if not isinstance(queue, dict):
        return {
            "status": "BLOCK",
            "blockers": ["queue must be an object"],
            "checked_lanes": [],
            "vacation_mode_complete": False,
            "unsafe_flags": ["queue_not_object"],
        }

    lanes = queue.get("lanes", [])
    if not isinstance(lanes, list):
        blockers.append("lanes must be a list")
        lanes = []

    lane_ids = [lane.get("lane_id") for lane in lanes if isinstance(lane, dict)]
    checked_lanes = [lane_id for lane_id in lane_ids if isinstance(lane_id, str)]
    if checked_lanes != LANE_ORDER:
        blockers.append("lanes must appear in the required strict serial order")
        unsafe_flags.append("lane_order_mismatch")

    expected_fields = {
        "lane_id",
        "title",
        "owner",
        "owner_type",
        "mode",
        "current_status",
        "required_inputs",
        "produces",
        "consumes_from",
        "consumed_by",
        "producer",
        "consumer",
        "hard_gates",
        "forbidden_actions",
        "proof_required",
        "validator_required",
        "next_packet_name",
        "stop_condition",
        "safe_next_command",
        "automation_allowed",
        "human_required",
        "vacation_mode_blocker",
        "auto_apply",
        "auto_merge",
        "auto_scheduler",
        "active_packet_mutation_allowed",
        "scheduler_execution_allowed",
        "service_execution_allowed",
        "sos_execution_allowed",
        "live_broker_trading_enabled",
    }

    lane_map = {}
    for lane in lanes:
        if not isinstance(lane, dict):
            blockers.append("lane entry must be an object")
            continue
        missing = [field for field in expected_fields if field not in lane]
        if missing:
            blockers.append(f"lane {lane.get('lane_id', '<unknown>')} missing fields: {', '.join(sorted(missing))}")
        lane_id = lane.get("lane_id")
        if isinstance(lane_id, str):
            lane_map[lane_id] = lane

    if len(lane_map) != len(LANE_ORDER):
        blockers.append("each required lane must appear exactly once")

    relay = lane_map.get("relay_runtime_processor")
    if relay:
        required_inputs = set(relay.get("required_inputs", []))
        required_relay_inputs = {
            "approval_card_present",
            "completeness_ready",
            "path_guard_pass",
            "apply_inventory_target_selected",
        }
        if not required_relay_inputs.issubset(required_inputs):
            blockers.append("relay lane lacks the required approval/completeness/path-guard inputs")
            unsafe_flags.append("relay_prerequisites_missing")
        proof_required = set(relay.get("proof_required", []))
        if "runtime_dry_run_pass" not in proof_required:
            blockers.append("relay lane lacks runtime_dry_run_pass proof requirement")
            unsafe_flags.append("relay_runtime_proof_missing")

    scheduler = lane_map.get("human_scheduler_registration")
    if scheduler:
        if scheduler.get("human_required") is not True:
            blockers.append("scheduler lane must be human_required")
            unsafe_flags.append("scheduler_not_human_required")
        if scheduler.get("automation_allowed") is not False:
            blockers.append("scheduler lane must not allow automation")
            unsafe_flags.append("scheduler_automation_allowed")

    sos_lane = lane_map.get("human_sos_arming")
    if sos_lane and _scan_for_secret_values(sos_lane):
        blockers.append("SOS lane contains a secret-like value")
        unsafe_flags.append("sos_secret_value_detected")

    for lane in lanes:
        if not isinstance(lane, dict):
            continue
        lane_id = str(lane.get("lane_id", "<unknown>"))
        if lane.get("auto_apply") is True:
            blockers.append(f"{lane_id}: auto_apply must be false")
            unsafe_flags.append("auto_apply_true")
        if lane.get("auto_merge") is True:
            blockers.append(f"{lane_id}: auto_merge must be false")
            unsafe_flags.append("auto_merge_true")
        if lane.get("auto_scheduler") is True:
            blockers.append(f"{lane_id}: auto_scheduler must be false")
            unsafe_flags.append("auto_scheduler_true")
        if lane.get("active_packet_mutation_allowed") is True:
            blockers.append(f"{lane_id}: active packet mutation is not allowed")
            unsafe_flags.append("active_packet_mutation_allowed")
        if lane.get("scheduler_execution_allowed") is True:
            blockers.append(f"{lane_id}: scheduler execution must stay human-only")
            unsafe_flags.append("scheduler_execution_allowed")
        if lane.get("service_execution_allowed") is True:
            blockers.append(f"{lane_id}: service execution must stay human-only")
            unsafe_flags.append("service_execution_allowed")
        if lane.get("sos_execution_allowed") is True:
            blockers.append(f"{lane_id}: SOS execution must stay human-only")
            unsafe_flags.append("sos_execution_allowed")
        if lane.get("live_broker_trading_enabled") is True:
            blockers.append(f"{lane_id}: live/broker/trading must remain disabled")
            unsafe_flags.append("live_broker_trading_enabled")

    vacation_mode_complete = bool(queue.get("vacation_mode_complete", False))
    remaining_blockers = list(queue.get("remaining_blockers", []))
    if vacation_mode_complete and remaining_blockers:
        blockers.append("vacation_mode_complete cannot be true while proof blockers remain")
        unsafe_flags.append("vacation_mode_complete_with_blockers")

    cloud_complete = bool(queue.get("cloud_buildable_lane_complete", False))
    state_snapshot = queue.get("state_snapshot") or {}
    if cloud_complete and not bool(state_snapshot.get("ledger_on_main", False)):
        blockers.append("cloud_buildable_lane_complete true requires ledger_on_main true")
        unsafe_flags.append("cloud_lane_state_mismatch")

    if queue.get("vacation_mode_complete") is True and not remaining_blockers and len(blockers) == 0:
        status = "PASS"
    elif blockers:
        status = "BLOCK"
    else:
        status = "PASS"

    return {
        "status": status,
        "blockers": blockers,
        "checked_lanes": checked_lanes,
        "vacation_mode_complete": vacation_mode_complete,
        "unsafe_flags": unsafe_flags,
    }


def summarize_next_actions(queue: dict) -> dict[str, object]:
    lanes = queue.get("lanes", [])
    next_actions: list[dict[str, object]] = []
    for lane in lanes if isinstance(lanes, list) else []:
        if not isinstance(lane, dict):
            continue
        next_actions.append(
            {
                "lane_id": lane.get("lane_id"),
                "title": lane.get("title"),
                "owner": lane.get("owner"),
                "next_packet_name": lane.get("next_packet_name"),
                "current_status": lane.get("current_status"),
                "consumer": lane.get("consumer"),
                "safe_next_command": lane.get("safe_next_command"),
            }
        )

    return {
        "status": "OK",
        "next_actions": next_actions,
        "primary_lane": next_actions[0] if next_actions else None,
        "remaining_blockers": list(queue.get("remaining_blockers", [])),
        "proof_chain": list(queue.get("proof_chain", [])),
        "human_only_gates": [
            lane.get("lane_id")
            for lane in lanes
            if isinstance(lane, dict) and lane.get("human_required") and lane.get("automation_allowed") is False
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Print the AI_OS runtime execution queue (JSON only).")
    parser.add_argument(
        "--state-json",
        default=None,
        help="optional JSON string containing proof state booleans; defaults to current cloud-buildable state",
    )
    args = parser.parse_args()

    state = None
    if args.state_json:
        state = json.loads(args.state_json)

    queue = build_runtime_execution_queue(state)
    payload = {
        "queue": queue,
        "validation": validate_runtime_execution_queue(queue),
        "next_actions": summarize_next_actions(queue),
        "hard_gate_check": assert_no_hard_gate_bypass(queue),
    }
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0 if payload["validation"]["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
