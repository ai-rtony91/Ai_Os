from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "AIOS-FOREX-OANDA-DEMO-RUNTIME-EXECUTOR-DRYRUN-V1"
EXECUTOR_VERSION = "v1"

DRYRUN_BLOCKED_MISSING_FINAL_CLICK = "DRYRUN_BLOCKED_MISSING_FINAL_CLICK"
DRYRUN_BLOCKED_FINAL_CLICK_NOT_READY = "DRYRUN_BLOCKED_FINAL_CLICK_NOT_READY"
DRYRUN_BLOCKED_RUNTIME_CONTEXT = "DRYRUN_BLOCKED_RUNTIME_CONTEXT"
DRYRUN_BLOCKED_CONTROLS = "DRYRUN_BLOCKED_CONTROLS"
DRYRUN_READY_FOR_OWNER_REVIEW = "DRYRUN_READY_FOR_OWNER_REVIEW"
DRYRUN_REJECTED = "DRYRUN_REJECTED"

FINAL_CLICK_READY_STATUS = "FINAL_CLICK_READY_FOR_RUNTIME_ONLY_DEMO_EXECUTION_REVIEW"
PREPARED_REVIEW_STATUS = "READY_FOR_EXTERNAL_RUNTIME_EXECUTOR_REVIEW_ONLY"

EXECUTION_AUTHORITY_FIELDS = (
    "execution_allowed",
    "demo_order_allowed",
    "live_order_allowed",
    "broker_write_allowed",
    "autonomous_order_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "webhook_allowed",
)

SIMULATED_EXECUTION_STEPS = (
    "receive final owner-click review object",
    "verify demo broker target",
    "verify live trading blocked",
    "verify credentials are runtime-only and not read in dry-run",
    "verify SL/TP required",
    "verify pre-trade evidence required",
    "simulate order payload shape",
    "stop before broker call",
)


def evaluate_oanda_demo_runtime_executor_dryrun_v1(
    final_owner_click_result: dict | None = None,
    runtime_executor_context: dict | None = None,
    dryrun_controls: dict | None = None,
) -> dict:
    final_click = _mapping(final_owner_click_result)
    if not final_click:
        return _result(
            status=DRYRUN_BLOCKED_MISSING_FINAL_CLICK,
            blockers=["missing_final_owner_click_result"],
            warnings=_warnings(DRYRUN_BLOCKED_MISSING_FINAL_CLICK),
            final_click=final_click,
            runtime_context=_mapping(runtime_executor_context),
            controls=_mapping(dryrun_controls),
        )

    runtime_context = _mapping(runtime_executor_context)
    controls = _mapping(dryrun_controls)

    unsafe_blockers = _unsafe_execution_blockers(final_click, runtime_context, controls)
    final_click_blockers = _final_click_blockers(final_click)
    runtime_blockers = _runtime_context_blockers(runtime_context)
    control_blockers = _control_blockers(controls)

    blockers = _unique(unsafe_blockers + final_click_blockers + runtime_blockers + control_blockers)
    status = _status(
        unsafe_blockers=unsafe_blockers,
        final_click_blockers=final_click_blockers,
        runtime_blockers=runtime_blockers,
        control_blockers=control_blockers,
    )

    return _result(
        status=status,
        blockers=blockers,
        warnings=_warnings(status),
        final_click=final_click,
        runtime_context=runtime_context,
        controls=controls,
    )


def _status(
    *,
    unsafe_blockers: list[str],
    final_click_blockers: list[str],
    runtime_blockers: list[str],
    control_blockers: list[str],
) -> str:
    if unsafe_blockers:
        return DRYRUN_REJECTED
    if final_click_blockers:
        return DRYRUN_BLOCKED_FINAL_CLICK_NOT_READY
    if runtime_blockers:
        return DRYRUN_BLOCKED_RUNTIME_CONTEXT
    if control_blockers:
        return DRYRUN_BLOCKED_CONTROLS
    return DRYRUN_READY_FOR_OWNER_REVIEW


def _final_click_blockers(final_click: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    if final_click.get("status") != FINAL_CLICK_READY_STATUS:
        blockers.append("final_owner_click_status_not_ready")
    prepared = _prepared_review(final_click)
    if prepared.get("status") != PREPARED_REVIEW_STATUS:
        blockers.append("prepared_order_review_status_not_ready")
    blockers.extend(_authority_blockers(final_click, "final_owner_click"))
    return blockers


def _runtime_context_blockers(runtime_context: Mapping[str, Any]) -> list[str]:
    if not runtime_context:
        return ["missing_runtime_executor_context"]

    blockers: list[str] = []
    if runtime_context.get("broker") != "OANDA_DEMO":
        blockers.append("runtime_context_broker_must_be_oanda_demo")
    if runtime_context.get("environment") != "DEMO":
        blockers.append("runtime_context_environment_must_be_demo")

    required_true = (
        "demo_environment",
        "runtime_only_credentials_required",
    )
    required_false = (
        "live_environment",
        "runtime_only_credentials_present",
        "credential_persistence_detected",
        "account_id_persistence_detected",
        "broker_network_call_performed",
        "order_placement_performed",
    )
    for field in required_true:
        if not _bool(runtime_context.get(field)):
            blockers.append(f"runtime_context_{field}_required")
    for field in required_false:
        if _bool(runtime_context.get(field)):
            blockers.append(f"runtime_context_{field}_must_be_false")
    return blockers


def _control_blockers(controls: Mapping[str, Any]) -> list[str]:
    if not controls:
        return ["missing_dryrun_controls"]

    required_true = (
        "dryrun_mode",
        "require_pre_trade_evidence",
        "require_post_trade_evidence",
        "require_owner_review_before_real_executor",
    )
    required_false = (
        "allow_broker_network",
        "allow_order_placement",
        "allow_credential_read",
        "allow_account_id_read",
    )

    blockers: list[str] = []
    for field in required_true:
        if not _bool(controls.get(field)):
            blockers.append(f"dryrun_controls_{field}_required")
    for field in required_false:
        if _bool(controls.get(field)):
            blockers.append(f"dryrun_controls_{field}_must_be_false")
    return blockers


def _result(
    *,
    status: str,
    blockers: list[str],
    warnings: list[str],
    final_click: Mapping[str, Any],
    runtime_context: Mapping[str, Any],
    controls: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "packet_id": PACKET_ID,
        "executor_version": EXECUTOR_VERSION,
        "status": status,
        "blockers": blockers,
        "warnings": warnings,
        "dryrun_order_payload": _dryrun_order_payload(status, final_click),
        "runtime_preflight": _runtime_preflight(runtime_context, controls),
        "simulated_execution_steps": list(SIMULATED_EXECUTION_STEPS),
        "evidence_capture_plan": _evidence_capture_plan(controls),
        "execution_authority": _execution_authority(),
        "next_safe_action": _next_safe_action(status),
    }


def _dryrun_order_payload(status: str, final_click: Mapping[str, Any]) -> dict[str, Any]:
    prepared = dict(_prepared_review(final_click))
    prepared.update(
        {
            "status": "DRYRUN_ONLY_NOT_EXECUTABLE",
            "broker_network_call_performed": False,
            "order_placement_performed": False,
            "credential_read_performed": False,
            "account_id_read_performed": False,
        }
    )
    if status != DRYRUN_READY_FOR_OWNER_REVIEW:
        prepared["ready_for_owner_review"] = False
        prepared["executable"] = False
    else:
        prepared["ready_for_owner_review"] = True
        prepared["executable"] = False
    return prepared


def _runtime_preflight(runtime_context: Mapping[str, Any], controls: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "broker": _text(runtime_context.get("broker"), "MISSING"),
        "environment": _text(runtime_context.get("environment"), "MISSING"),
        "demo_environment": _bool(runtime_context.get("demo_environment")),
        "live_environment": _bool(runtime_context.get("live_environment")),
        "runtime_only_credentials_required": _bool(
            runtime_context.get("runtime_only_credentials_required")
        ),
        "runtime_only_credentials_present": _bool(
            runtime_context.get("runtime_only_credentials_present")
        ),
        "credential_persistence_detected": _bool(
            runtime_context.get("credential_persistence_detected")
        ),
        "account_id_persistence_detected": _bool(
            runtime_context.get("account_id_persistence_detected")
        ),
        "broker_network_call_allowed": _bool(controls.get("allow_broker_network")),
        "order_placement_allowed": _bool(controls.get("allow_order_placement")),
        "dryrun_mode": _bool(controls.get("dryrun_mode")),
    }


def _evidence_capture_plan(controls: Mapping[str, Any]) -> dict[str, bool]:
    return {
        "pre_trade_evidence_required": _bool(controls.get("require_pre_trade_evidence")),
        "post_trade_evidence_required": _bool(controls.get("require_post_trade_evidence")),
        "owner_review_before_real_executor_required": _bool(
            controls.get("require_owner_review_before_real_executor")
        ),
        "sanitized_evidence_only": True,
        "records_realized_pl_after_separate_execution": True,
    }


def _unsafe_execution_blockers(*payloads: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    for index, payload in enumerate(payloads):
        blockers.extend(_authority_blockers(payload, f"payload_{index}"))
    return blockers


def _authority_blockers(payload: Mapping[str, Any], label: str) -> list[str]:
    blockers: list[str] = []
    authority = _mapping(payload.get("execution_authority"))
    for field in EXECUTION_AUTHORITY_FIELDS:
        if _bool(payload.get(field)) or _bool(authority.get(field)):
            blockers.append(f"unsafe_{label}_{field}_true")
    return blockers


def _prepared_review(final_click: Mapping[str, Any]) -> Mapping[str, Any]:
    return _mapping(final_click.get("prepared_order_review"))


def _execution_authority() -> dict[str, bool]:
    return {field: False for field in EXECUTION_AUTHORITY_FIELDS}


def _warnings(status: str) -> list[str]:
    warnings = [
        "dryrun_only_not_executable",
        "execution_authority_false",
        "no_broker_call_performed",
        "no_credentials_or_account_ids_read",
        "no_order_placement_performed",
    ]
    if status == DRYRUN_READY_FOR_OWNER_REVIEW:
        warnings.append("separate_final_gated_runtime_executor_still_required")
    return warnings


def _next_safe_action(status: str) -> str:
    return {
        DRYRUN_BLOCKED_MISSING_FINAL_CLICK: "provide_ready_final_owner_click_result",
        DRYRUN_BLOCKED_FINAL_CLICK_NOT_READY: "repair_final_owner_click_bridge_before_dryrun",
        DRYRUN_BLOCKED_RUNTIME_CONTEXT: "provide_demo_only_dryrun_runtime_context_without_credentials",
        DRYRUN_BLOCKED_CONTROLS: "provide_strict_dryrun_controls_that_block_broker_and_order_paths",
        DRYRUN_READY_FOR_OWNER_REVIEW: "owner_review_dryrun_payload_before_separate_final_gated_executor",
        DRYRUN_REJECTED: "remove_execution_authority_request_before_dryrun_review",
    }.get(status, "stop_and_review_runtime_executor_dryrun_state")


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _bool(value: Any) -> bool:
    return value is True


def _text(value: Any, default: str = "") -> str:
    return value.strip() if isinstance(value, str) else default


def _unique(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique: list[str] = []
    for value in values:
        if value not in seen:
            unique.append(value)
            seen.add(value)
    return unique
