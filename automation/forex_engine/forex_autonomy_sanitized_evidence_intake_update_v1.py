"""Sanitized evidence intake updater for the Forex autonomy completion lane.

The module sanitizes explicit evidence updates and prepares a previewed governor
input payload for the next offline governor rerun.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Iterable, Mapping

from . import supervised_autonomy_governor_v1 as governor


PACKET_ID = "PKT-FOREX-AUTONOMY-COMPLETION-SANITIZED-EVIDENCE-INTAKE-UPDATE-V1"
MISSION_ID = "MISSION-AIOS-FOREX-AUTONOMY-COMPLETION-V1"
PROGRAM_ID = "PROGRAM-FOREX-PROFIT-AUTONOMY-V1"
EPIC_ID = "EPC-FOREX-AUTONOMY-COMPLETION-001"
BUCKET_ID = "BKT-FOREX-SANITIZED-EVIDENCE-INTAKE-001"

INTAKE_NO_EVIDENCE = "NO_EVIDENCE_APPLIED"
INTAKE_SANITIZED_APPLIED = "SANITIZED_EVIDENCE_APPLIED"
INTAKE_SANITIZED_REJECTED = "SANITIZED_EVIDENCE_REJECTED"

VALIDATOR_CHAIN = (
    "python -m py_compile automation/forex_engine/forex_autonomy_sanitized_evidence_intake_update_v1.py",
    "python -m py_compile scripts/forex_delivery/run_forex_autonomy_sanitized_evidence_intake_update_v1.py",
    "python -m pytest tests/forex_engine/test_forex_autonomy_sanitized_evidence_intake_update_v1.py -q",
    "python scripts/forex_delivery/run_forex_autonomy_sanitized_evidence_intake_update_v1.py --write-state --write-report --write-input-template",
    "python -m json.tool Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_INPUT_TEMPLATE.json",
    "python -m json.tool Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_STATE.json",
    "git diff --check -- automation/forex_engine/forex_autonomy_sanitized_evidence_intake_update_v1.py scripts/forex_delivery/run_forex_autonomy_sanitized_evidence_intake_update_v1.py tests/forex_engine/test_forex_autonomy_sanitized_evidence_intake_update_v1.py Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_INPUT_TEMPLATE.json Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_STATE.json Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_REPORT.md Reports/forex_delivery/AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_NEXT_CODEX_PACKET_V1.md Reports/forex_delivery/AIOS_FOREX_SANITIZED_EVIDENCE_INTAKE_P1_HARDENING_V1_REPORT.md",
)

FORBIDDEN_INPUT_PATH_FRAGMENTS = (
    ".env",
    "secret",
    "secrets",
    "credential",
    "credentials",
    "account",
    "oanda",
    "broker",
    "runtime",
    "scheduler",
    "daemon",
    "webhook",
    "production",
)

FORBIDDEN_FIELD_NAME_FRAGMENTS = (
    "account",
    "credential",
    "credentials",
    "token",
    "password",
    "secret",
    "key",
    "api",
    "oanda",
    "broker_id",
    "account_id",
)
SUPPRESSED_FIELD_NAMES_OUTPUT_MARKER = "field_names_suppressed_for_output"
CANDIDATE_ID_FORBIDDEN_VALUE_FRAGMENTS = (
    "account",
    "token",
    "secret",
    "credential",
    "password",
    "api",
    "oanda",
    "broker",
)

ALLOWED_EVIDENCE_FIELDS = (
    "profitability_evidence_status",
    "sample_size",
    "walk_forward_windows",
    "max_drawdown",
    "profit_factor",
    "expectancy",
    "broker_readiness",
    "live_bridge_eligibility",
    "kill_switch_state",
    "daily_stop_state",
    "max_loss_state",
    "order_count_last_24h",
    "tp_sl_present",
    "monitoring_ready",
    "evidence_age_days",
    "owner_approval_status",
    "live_exception_requested",
    "live_bridge_external_evidence",
    "owner_live_micro_exception_approved",
    "realized_broker_evidence",
)
SAFE_GOVERNOR_INPUT_FIELDS = ("candidate_id", *ALLOWED_EVIDENCE_FIELDS)

ALLOWED_SAFETY_STATES = {"ARMED", "READY", "ENABLED"}
GOVERNOR_MISSING_GATE_FIELDS = {
    governor.GATE_PROFITABILITY_EVIDENCE: ("profitability_evidence_status",),
    governor.GATE_SAMPLE_SUFFICIENCY: ("sample_size",),
    governor.GATE_WALK_FORWARD: ("walk_forward_windows",),
    governor.GATE_DRAWDOWN: ("max_drawdown",),
    governor.GATE_PROFIT_FACTOR: ("profit_factor",),
    governor.GATE_EXPECTANCY: ("expectancy",),
    governor.GATE_BROKER_READINESS: ("broker_readiness",),
    governor.GATE_LIVE_BRIDGE: ("live_bridge_eligibility",),
    governor.GATE_TP_SL: ("tp_sl_present",),
    governor.GATE_EVIDENCE_FRESHNESS: ("evidence_age_days",),
}
GOVERNOR_BLOCKED_GATE_FIELDS = {
    governor.GATE_KILL_SWITCH: ("kill_switch_state",),
    governor.GATE_DAILY_STOP: ("daily_stop_state",),
    governor.GATE_MAX_LOSS: ("max_loss_state",),
    governor.GATE_MONITORING: ("monitoring_ready",),
}
DEFAULT_STATE_JSON_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_AUTONOMY_COMPLETION_GOVERNOR_RERUN_AND_BUCKET_POLICY_V1_STATE.json"
)
DEFAULT_GOVERNOR_INPUT_JSON_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_LIVE_MICRO_EXCEPTION_GOVERNOR_INPUT_TEMPLATE_V1.json"
)
DEFAULT_INPUT_TEMPLATE_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_INPUT_TEMPLATE.json"
)
DEFAULT_STATE_OUTPUT_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_STATE.json"
)
DEFAULT_REPORT_OUTPUT_PATH = (
    Path(__file__).resolve().parents[2]
    / "Reports"
    / "forex_delivery"
    / "AIOS_FOREX_AUTONOMY_COMPLETION_SANITIZED_EVIDENCE_INTAKE_UPDATE_V1_REPORT.md"
)


def run_forex_autonomy_sanitized_evidence_intake_update_v1(
    *,
    state_json: Path | str | None = None,
    governor_input_json: Path | str | None = None,
    evidence_json: Path | str | None = None,
    evidence_mapping: Mapping[str, Any] | None = None,
    state_mapping: Mapping[str, Any] | None = None,
    governor_input_mapping: Mapping[str, Any] | None = None,
    write_state: bool = False,
    write_state_path: Path | str | None = None,
    write_report: bool = False,
    write_report_path: Path | str | None = None,
    write_input_template: bool = False,
    write_input_template_path: Path | str | None = None,
) -> dict[str, Any]:
    state = _load_json_mapping(
        state_mapping,
        _coerce_path(state_json) if state_json is not None else DEFAULT_STATE_JSON_PATH,
    )
    governor_input = _load_json_mapping(
        governor_input_mapping,
        _coerce_path(governor_input_json)
        if governor_input_json is not None
        else DEFAULT_GOVERNOR_INPUT_JSON_PATH,
    )

    evidence_payload = None
    if evidence_mapping is not None:
        evidence_payload = dict(evidence_mapping)
    elif evidence_json is not None:
        evidence_payload = _load_json_mapping(None, _coerce_path(evidence_json))

    controller_candidate_status = _text(
        state.get("candidate_status"), default=governor.AUTONOMY_BLOCKED
    )
    controller_bucket_status = _text(state.get("bucket_status"), default="UNKNOWN")
    controller_next_autonomy_action = _text(
        state.get("next_autonomy_action"), default="UNKNOWN"
    )

    (
        sanitized_governor_input,
        rejected_base_governor_input_fields,
    ) = _sanitize_base_governor_input(governor_input)
    rejected_base_governor_input_fields = _dedupe_list(
        rejected_base_governor_input_fields
    )

    updated_preview = dict(sanitized_governor_input)
    applied_fields: list[str] = []
    rejected_fields: list[str] = []
    intake_status = INTAKE_NO_EVIDENCE
    missing_evidence_fields, blocked_evidence_fields = _classify_evidence_gaps(
        sanitized_governor_input
    )

    if evidence_payload:
        accepted_updates, rejected_updates = _validate_evidence_payload(evidence_payload)
        if rejected_updates:
            intake_status = INTAKE_SANITIZED_REJECTED
            rejected_fields = rejected_updates
        else:
            owner_approval_status = _canonical_status(
                evidence_payload.get(
                    "owner_approval_status",
                    sanitized_governor_input.get("owner_approval_status"),
                )
            )
            if (
                _as_bool_or_none(
                    evidence_payload.get("owner_live_micro_exception_approved"),
                    default=False,
                )
                and owner_approval_status != "APPROVED_FOR_LIVE_MICRO"
            ):
                intake_status = INTAKE_SANITIZED_REJECTED
                rejected_fields = ["owner_live_micro_exception_approved"]
            else:
                for key, value in accepted_updates.items():
                    updated_preview[key] = value
                applied_fields = sorted(accepted_updates.keys())
                intake_status = INTAKE_SANITIZED_APPLIED
                missing_evidence_fields, blocked_evidence_fields = _classify_evidence_gaps(
                    updated_preview
                )

    rerun_recommended = (
        intake_status == INTAKE_SANITIZED_APPLIED
        and not missing_evidence_fields
        and not blocked_evidence_fields
    )
    if blocked_evidence_fields:
        next_safe_action = (
            "Critical safety blockers are present; gather critical safety evidence "
            "and pause evidence progression until safety gates are resolved."
        )
    elif missing_evidence_fields:
        next_safe_action = "Collect missing sanitized evidence and rerun the governor intake update."
    elif intake_status == INTAKE_NO_EVIDENCE:
        next_safe_action = (
            "Collect owner-sanitized evidence for missing readiness fields before rerun."
        )
    elif intake_status == INTAKE_SANITIZED_APPLIED:
        next_safe_action = "Rerun the autonomy completion governor with sanitized evidence updates."
    else:
        next_safe_action = (
            "Correct evidence update payload issues, then rerun the evidence intake check."
        )

    safety_boundary = {
        "order_execution_allowed": False,
        "broker_api_allowed": False,
        "credentials_allowed": False,
        "account_identifier_persistence_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "webhook_allowed": False,
    }

    result = {
        "intake_status": intake_status,
        "controller_candidate_status": controller_candidate_status,
        "controller_bucket_status": controller_bucket_status,
        "controller_next_autonomy_action": controller_next_autonomy_action,
        "missing_evidence_fields": _dedupe_list(missing_evidence_fields),
        "blocked_evidence_fields": _dedupe_list(blocked_evidence_fields),
        "applied_evidence_fields": _dedupe_list(applied_fields),
        "rejected_evidence_fields": _dedupe_list(rejected_fields),
        "rejected_base_governor_input_fields": rejected_base_governor_input_fields,
        "rejected_base_governor_input_field_count": len(
            rejected_base_governor_input_fields
        ),
        "updated_governor_input_preview": _sorted_payload(updated_preview),
        "rerun_recommended": bool(rerun_recommended),
        "next_safe_action": next_safe_action,
        "safety_boundary": safety_boundary,
        "validator_chain": list(VALIDATOR_CHAIN),
        "packet_id": PACKET_ID,
        "mission_id": MISSION_ID,
        "program_id": PROGRAM_ID,
        "epic_id": EPIC_ID,
        "bucket_id": BUCKET_ID,
    }

    if write_state:
        state_output = (
            Path(write_state_path)
            if write_state_path is not None
            else DEFAULT_STATE_OUTPUT_PATH
        )
        state_output.write_text(
            json.dumps(build_safe_output_result_payload(result), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        result["state_output_path"] = str(state_output)

    if write_input_template:
        input_template_output = (
            Path(write_input_template_path)
            if write_input_template_path is not None
            else DEFAULT_INPUT_TEMPLATE_PATH
        )
        input_template_output.write_text(
            json.dumps(_build_input_template_payload(), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        result["input_template_output_path"] = str(input_template_output)

    if write_report:
        report_output = (
            Path(write_report_path)
            if write_report_path is not None
            else DEFAULT_REPORT_OUTPUT_PATH
        )
        report_output.write_text(
            _build_report_markdown(
                result=result,
                branch=_git_value("rev-parse", "--abbrev-ref", "HEAD"),
                head=_git_value("rev-parse", "HEAD"),
                state_json_path=_coerce_path(
                    state_json if state_json is not None else DEFAULT_STATE_JSON_PATH
                ),
                governor_input_json_path=_coerce_path(
                    governor_input_json
                    if governor_input_json is not None
                    else DEFAULT_GOVERNOR_INPUT_JSON_PATH
                ),
                evidence_json_path=_coerce_optional_path(evidence_json),
            ),
            encoding="utf-8",
        )
        result["report_output_path"] = str(report_output)

    return result


def build_safe_output_result_payload(
    result: Mapping[str, Any],
    *,
    include_safety_boundary: bool = True,
) -> dict[str, Any]:
    payload = dict(result)
    payload["rejected_evidence_fields"] = _safe_field_names_for_output(
        payload.get("rejected_evidence_fields", ())
    )
    payload["rejected_base_governor_input_fields"] = _safe_field_names_for_output(
        payload.get("rejected_base_governor_input_fields", ())
    )
    if not include_safety_boundary:
        payload.pop("safety_boundary", None)
    return payload


def _build_report_markdown(
    *,
    result: Mapping[str, Any],
    branch: str,
    head: str,
    state_json_path: Path,
    governor_input_json_path: Path,
    evidence_json_path: Path | None,
) -> str:
    lines: list[str] = [
        "# AIOS Forex Autonomy Completion Sanitized Evidence Intake Update V1 Report",
        "",
        f"Status: {result['intake_status']}",
        f"Current branch: {branch}",
        f"Current head: {head}",
        f"Input files used: {state_json_path}, {governor_input_json_path}",
        f"Evidence update file used: {evidence_json_path if evidence_json_path is not None else 'None'}",
        "",
        f"Controller candidate status: {result['controller_candidate_status']}",
        f"Controller bucket status: {result['controller_bucket_status']}",
        f"Controller next autonomy action: {result['controller_next_autonomy_action']}",
        "",
        "Missing evidence fields:",
    ]
    for name in result["missing_evidence_fields"]:
        lines.append(f"- {name}")
    if not result["missing_evidence_fields"]:
        lines.append("- none")

    lines.append("Blocked evidence fields:")
    for name in result["blocked_evidence_fields"]:
        lines.append(f"- {name}")
    if not result["blocked_evidence_fields"]:
        lines.append("- none")

    lines.extend(
        [
            f"Applied evidence fields: {result['applied_evidence_fields']}",
            (
                "Rejected evidence fields: "
                f"{_safe_field_names_for_output(result['rejected_evidence_fields'])}"
            ),
            "Rejected base governor input field names: suppressed from persisted report output",
            (
                "Rejected base governor input field count: "
                f"{result.get('rejected_base_governor_input_field_count', 0)}"
            ),
            f"Rerun recommended: {result['rerun_recommended']}",
            f"Next safe action: {result['next_safe_action']}",
            "Safety boundary:",
        ]
    )
    for key in _sorted_keys(result["safety_boundary"]):
        lines.append(f"- {key}: {result['safety_boundary'][key]}")

    lines.extend(["", "Validators:"])
    for validator in result["validator_chain"]:
        lines.append(f"- {validator}")
    return "\n".join(lines) + "\n"


def _sorted_payload(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {key: payload[key] for key in _sorted_keys(payload)}


def _sorted_keys(payload: Mapping[str, Any]) -> list[str]:
    return sorted(payload.keys(), key=str.lower)


def _sanitize_base_governor_input(
    governor_input: Mapping[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    sanitized: dict[str, Any] = {}
    rejected: list[str] = []

    for key, value in governor_input.items():
        if not isinstance(key, str):
            rejected.append(str(key))
            continue
        normalized_key = key.strip()
        if normalized_key in SAFE_GOVERNOR_INPUT_FIELDS:
            if normalized_key == "candidate_id":
                safe_candidate_id = _safe_candidate_id(value)
                if safe_candidate_id is None:
                    rejected.append(normalized_key)
                    continue
                sanitized[normalized_key] = safe_candidate_id
                continue
            sanitized[normalized_key] = value
        else:
            rejected.append(normalized_key)

    return sanitized, _dedupe_list(rejected)


def _safe_candidate_id(value: Any) -> str | int | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    lowered = normalized.lower()
    if any(
        fragment in lowered for fragment in CANDIDATE_ID_FORBIDDEN_VALUE_FRAGMENTS
    ):
        return None
    return normalized


def _classify_evidence_gaps(
    governor_input: Mapping[str, Any],
) -> tuple[list[str], list[str]]:
    missing: list[str] = []
    blocked: list[str] = []
    order_count_gap = _classify_order_count_gap(
        governor_input.get("order_count_last_24h")
    )

    if _canonical_status(governor_input.get("profitability_evidence_status")) != "READY":
        missing.append("profitability_evidence_status")

    sample_size = _as_float(governor_input.get("sample_size"))
    if sample_size is None or sample_size < governor.MIN_SAMPLE_SIZE:
        missing.append("sample_size")

    walk_forward_windows = _as_float(governor_input.get("walk_forward_windows"))
    if walk_forward_windows is None or walk_forward_windows < governor.MIN_WALK_FORWARD_WINDOWS:
        missing.append("walk_forward_windows")

    profit_factor = _as_float(governor_input.get("profit_factor"))
    if profit_factor is None or profit_factor < governor.MIN_PROFIT_FACTOR:
        missing.append("profit_factor")

    expectancy = _as_float(governor_input.get("expectancy"))
    if expectancy is None or expectancy < governor.MIN_EXPECTANCY:
        missing.append("expectancy")

    max_drawdown = _as_float(governor_input.get("max_drawdown"))
    if max_drawdown is None or max_drawdown > governor.MAX_DRAWDOWN_RATIO:
        missing.append("max_drawdown")

    if not _as_bool_or_none(governor_input.get("live_bridge_eligibility"), default=False):
        missing.append("live_bridge_eligibility")

    if _canonical_status(governor_input.get("kill_switch_state")) not in ALLOWED_SAFETY_STATES:
        blocked.append("kill_switch_state")

    if _canonical_status(governor_input.get("daily_stop_state")) not in ALLOWED_SAFETY_STATES:
        blocked.append("daily_stop_state")

    if _canonical_status(governor_input.get("max_loss_state")) not in ALLOWED_SAFETY_STATES:
        blocked.append("max_loss_state")

    if not _as_bool_or_none(governor_input.get("tp_sl_present"), default=False):
        missing.append("tp_sl_present")

    if not _as_bool_or_none(governor_input.get("monitoring_ready"), default=False):
        blocked.append("monitoring_ready")

    if order_count_gap == "missing":
        missing.append("order_count_last_24h")
    elif order_count_gap == "blocked":
        blocked.append("order_count_last_24h")

    evidence_age_days = _as_float(governor_input.get("evidence_age_days"))
    if (
        evidence_age_days is None
        or evidence_age_days > governor.MAX_EVIDENCE_AGE_DAYS
    ):
        missing.append("evidence_age_days")

    if _canonical_status(governor_input.get("owner_approval_status")) == "PENDING":
        missing.append("owner_approval_status")

    governor_missing, governor_blocked = _classify_governor_failed_gates(
        _governor_input_with_safe_order_count(governor_input),
        skip_order_count_gate=order_count_gap is not None,
    )
    missing.extend(governor_missing)
    blocked.extend(governor_blocked)

    return _dedupe_list(missing), _dedupe_list(blocked)


def _classify_governor_failed_gates(
    governor_input: Mapping[str, Any],
    *,
    skip_order_count_gate: bool = False,
) -> tuple[list[str], list[str]]:
    governor_result = governor.evaluate_supervised_autonomy_candidate(governor_input)
    failed_gates = tuple(str(gate) for gate in governor_result.get("failed_gates", ()))
    missing: list[str] = []
    blocked: list[str] = []

    for gate in failed_gates:
        if gate == governor.GATE_ORDER_COUNT:
            if skip_order_count_gate:
                continue
            count = _as_float(governor_input.get("order_count_last_24h"))
            target = missing if count is None else blocked
            target.append("order_count_last_24h")
            continue
        if gate == governor.GATE_OWNER_APPROVAL:
            owner_status = _canonical_status(governor_input.get("owner_approval_status"))
            target = blocked if owner_status in {"DENIED", "REJECTED"} else missing
            target.append("owner_approval_status")
            continue
        for field in GOVERNOR_MISSING_GATE_FIELDS.get(gate, ()):
            missing.append(field)
        for field in GOVERNOR_BLOCKED_GATE_FIELDS.get(gate, ()):
            blocked.append(field)

    candidate_status = str(governor_result.get("candidate_status", ""))
    if candidate_status == governor.LIVE_BLOCKED_BY_POLICY and _as_bool_or_none(
        governor_input.get("live_exception_requested"), default=False
    ):
        if not _as_bool_or_none(
            governor_input.get("live_bridge_external_evidence"), default=False
        ):
            missing.append("live_bridge_external_evidence")
        if not _as_bool_or_none(
            governor_input.get("owner_live_micro_exception_approved"), default=False
        ):
            missing.append("owner_live_micro_exception_approved")

    return _dedupe_list(missing), _dedupe_list(blocked)


def _validate_evidence_payload(
    evidence_payload: Mapping[str, Any],
) -> tuple[dict[str, Any], list[str]]:
    if not isinstance(evidence_payload, Mapping):
        raise ValueError("evidence JSON payload must be an object")

    accepted: dict[str, Any] = {}
    rejected: list[str] = []

    for key, value in evidence_payload.items():
        if not isinstance(key, str):
            rejected.append(str(key))
            continue
        normalized_key = key.strip()
        lowered = normalized_key.lower()
        if _is_sensitive_field_name(lowered):
            rejected.append(normalized_key)
            continue
        if normalized_key not in ALLOWED_EVIDENCE_FIELDS:
            rejected.append(normalized_key)
            continue
        accepted[normalized_key] = value

    if rejected:
        return {}, _dedupe_list(rejected)

    field_errors = _validate_evidence_fields(accepted)
    if field_errors:
        return {}, _dedupe_list(field_errors)

    return accepted, []


def _validate_evidence_fields(evidence_payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    for key, value in evidence_payload.items():
        if value is None:
            errors.append(key)
            continue

        if key in {"sample_size", "walk_forward_windows", "evidence_age_days"}:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(key)
                continue
            if value < 0:
                errors.append(key)
        elif key == "order_count_last_24h":
            if not _is_non_negative_integer(value):
                errors.append(key)
        elif key in {"max_drawdown", "profit_factor", "expectancy"}:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                errors.append(key)
                continue
        elif key in {
            "broker_readiness",
            "live_bridge_eligibility",
            "tp_sl_present",
            "monitoring_ready",
            "live_exception_requested",
            "live_bridge_external_evidence",
            "owner_live_micro_exception_approved",
            "realized_broker_evidence",
        }:
            if not isinstance(value, bool):
                errors.append(key)
        elif key in {
            "profitability_evidence_status",
            "kill_switch_state",
            "daily_stop_state",
            "max_loss_state",
            "owner_approval_status",
        }:
            if not isinstance(value, str) or not value.strip():
                errors.append(key)
        else:
            errors.append(key)
    return _dedupe_list(errors)


def _is_non_negative_integer(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool) and value >= 0


def _classify_order_count_gap(value: Any) -> str | None:
    if value is None:
        return "missing"
    if not _is_non_negative_integer(value):
        return "blocked"
    if value > governor.MAX_ORDERS_24H:
        return "blocked"
    return None


def _governor_input_with_safe_order_count(
    governor_input: Mapping[str, Any],
) -> dict[str, Any]:
    payload = dict(governor_input)
    order_count = payload.get("order_count_last_24h")
    if order_count is not None and not _is_non_negative_integer(order_count):
        payload["order_count_last_24h"] = None
    return payload


def _is_sensitive_field_name(field_name: str) -> bool:
    lowered = field_name.strip().lower()
    return any(marker in lowered for marker in FORBIDDEN_FIELD_NAME_FRAGMENTS)


def _safe_field_names_for_output(field_names: Iterable[Any]) -> list[str]:
    safe_names: list[str] = []
    sensitive_seen = False
    for field_name in field_names:
        name = str(field_name)
        if _is_sensitive_field_name(name):
            sensitive_seen = True
            continue
        safe_names.append(name)
    if sensitive_seen:
        safe_names.append(SUPPRESSED_FIELD_NAMES_OUTPUT_MARKER)
    return _dedupe_list(safe_names)


def _as_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _as_bool_or_none(value: Any, *, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "on", "armed", "ready", "enabled"}


def _canonical_status(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip().upper()
    return str(value).strip().upper()


def _text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value)


def _dedupe_list(values: Iterable[str]) -> list[str]:
    deduped: list[str] = []
    seen: set[str] = set()
    for item in values:
        if item in seen:
            continue
        seen.add(item)
        deduped.append(item)
    return deduped


def _build_input_template_payload() -> dict[str, Any]:
    return {
        "profitability_evidence_status": "PENDING",
        "sample_size": 0,
        "walk_forward_windows": 0,
        "max_drawdown": 0.0,
        "profit_factor": 0.0,
        "expectancy": 0.0,
        "broker_readiness": False,
        "live_bridge_eligibility": False,
        "kill_switch_state": "UNKNOWN",
        "daily_stop_state": "UNKNOWN",
        "max_loss_state": "UNSET",
        "order_count_last_24h": 0,
        "tp_sl_present": False,
        "monitoring_ready": False,
        "evidence_age_days": 0,
        "owner_approval_status": "PENDING",
        "live_exception_requested": False,
        "live_bridge_external_evidence": False,
        "owner_live_micro_exception_approved": False,
        "realized_broker_evidence": False,
    }


def _load_json_mapping(
    payload: Mapping[str, Any] | None,
    json_path: Path,
) -> dict[str, Any]:
    if payload is not None:
        if isinstance(payload, Mapping):
            return dict(payload)
        raise ValueError("state/governor payload must be an object")

    loaded = json.loads(json_path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"JSON payload at {json_path} must be an object")
    return loaded


def _coerce_path(value: Path | str | None) -> Path:
    resolved = Path("." if value is None else value)
    resolved_path = resolved.resolve()
    _reject_forbidden_input_path(resolved_path)
    return resolved_path


def _coerce_optional_path(value: Any) -> Path | None:
    if value is None:
        return None
    if isinstance(value, (dict, list)):
        return None
    if isinstance(value, Path):
        _reject_forbidden_input_path(value)
        return value
    if not isinstance(value, str):
        return None
    path = Path(value).resolve()
    _reject_forbidden_input_path(path)
    return path


def _reject_forbidden_input_path(path: Path) -> None:
    normalized = str(path).replace("\\", "/").lower()
    if any(fragment in normalized for fragment in FORBIDDEN_INPUT_PATH_FRAGMENTS):
        raise ValueError(f"refusing forbidden local input path: {path}")


def _git_value(*command: str) -> str:
    try:
        return subprocess.check_output(["git", *command], text=True).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


__all__ = [
    "run_forex_autonomy_sanitized_evidence_intake_update_v1",
    "DEFAULT_STATE_JSON_PATH",
    "DEFAULT_GOVERNOR_INPUT_JSON_PATH",
    "DEFAULT_INPUT_TEMPLATE_PATH",
    "DEFAULT_STATE_OUTPUT_PATH",
    "build_safe_output_result_payload",
]
