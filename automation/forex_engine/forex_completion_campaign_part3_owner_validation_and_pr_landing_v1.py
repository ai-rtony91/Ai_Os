"""Forex Completion Campaign Part 3 owner-validation landing evaluator."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime, timezone
from typing import Any


SCHEMA = "AIOS_FOREX_COMPLETION_CAMPAIGN_PART3_OWNER_VALIDATION_AND_PR_LANDING_V1"
MODE = "READ_ONLY_METADATA_ONLY_OWNER_VALIDATION_AND_PR_LANDING_PREP"

PART3_OWNER_VALIDATION_READY = "PART3_OWNER_VALIDATION_READY"
PART3_READY_FOR_COMMIT_APPROVAL = "PART3_READY_FOR_COMMIT_APPROVAL"
PART3_READY_FOR_PR_LANDING_APPROVAL = "PART3_READY_FOR_PR_LANDING_APPROVAL"
BLOCKED_BY_MISSING_PART1_FILES = "BLOCKED_BY_MISSING_PART1_FILES"
BLOCKED_BY_MISSING_PART2_FILES = "BLOCKED_BY_MISSING_PART2_FILES"
BLOCKED_BY_VALIDATION_FAILURE = "BLOCKED_BY_VALIDATION_FAILURE"
BLOCKED_BY_SENSITIVE_DATA = "BLOCKED_BY_SENSITIVE_DATA"
BLOCKED_BY_UNRELATED_DIRTY_FILES = "BLOCKED_BY_UNRELATED_DIRTY_FILES"
BLOCKED_BY_SAFETY_BOUNDARY = "BLOCKED_BY_SAFETY_BOUNDARY"
INCOMPLETE_INPUTS = "INCOMPLETE_INPUTS"

NEXT_PACKET_PART4 = (
    "AIOS_FOREX_COMPLETION_CAMPAIGN_PART4_COMMIT_PUSH_PR_AFTER_OWNER_APPROVAL_V1"
)

PART1_FILES = (
    "automation/forex_engine/live_execution_and_capital_operation_campaign_v1.py",
    "tests/forex_engine/test_live_execution_and_capital_operation_campaign_v1.py",
    "docs/trading_lab/FOREX_LIVE_EXECUTION_AND_CAPITAL_OPERATION_CAMPAIGN_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_LIVE_EXECUTION_AND_CAPITAL_OPERATION_CAMPAIGN_V1_REPORT.md",
)

PART2_FILES = (
    "automation/forex_engine/oanda_demo_owner_approved_one_order_protected_runtime_execution_v1.py",
    "automation/forex_engine/owner_runtime_credential_session_bridge_v1.py",
    "automation/forex_engine/forex_post_execution_review_loop_v1.py",
    "automation/forex_engine/forex_22h6d_supervised_operation_readiness_v1.py",
    "automation/forex_engine/forex_completion_campaign_part2_v1.py",
    "tests/forex_engine/test_oanda_demo_owner_approved_one_order_protected_runtime_execution_v1.py",
    "tests/forex_engine/test_owner_runtime_credential_session_bridge_v1.py",
    "tests/forex_engine/test_forex_post_execution_review_loop_v1.py",
    "tests/forex_engine/test_forex_22h6d_supervised_operation_readiness_v1.py",
    "tests/forex_engine/test_forex_completion_campaign_part2_v1.py",
    "scripts/forex_delivery/run_forex_completion_campaign_part2_v1.py",
    "docs/trading_lab/FOREX_COMPLETION_CAMPAIGN_PART2_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_COMPLETION_CAMPAIGN_PART2_V1_REPORT.md",
)

PART3_FILES = (
    "automation/forex_engine/forex_completion_campaign_part3_owner_validation_and_pr_landing_v1.py",
    "tests/forex_engine/test_forex_completion_campaign_part3_owner_validation_and_pr_landing_v1.py",
    "scripts/forex_delivery/run_forex_completion_campaign_part3_owner_validation_v1.py",
    "docs/trading_lab/FOREX_COMPLETION_CAMPAIGN_PART3_OWNER_VALIDATION_AND_PR_LANDING_V1.md",
    "Reports/forex_delivery/AIOS_FOREX_COMPLETION_CAMPAIGN_PART3_OWNER_VALIDATION_AND_PR_LANDING_V1_REPORT.md",
)

HARD_FALSE_FIELDS = (
    "live_trade_executed",
    "demo_trade_executed",
    "money_moved",
    "bank_access_used",
    "broker_api_called",
    "credential_read",
    "credential_stored",
    "api_key_stored",
    "master_password_used",
    "vault_password_used",
    "scheduler_created",
    "daemon_created",
    "webhook_created",
    "dashboard_runtime_created",
    "commit_executed",
    "push_executed",
    "pr_created",
    "merge_executed",
)

SAFETY_FALSE_FIELDS = (
    "real_broker_call_allowed",
    "direct_broker_api_allowed",
    "broker_api_import_allowed",
    "network_call_allowed",
    "live_trading_allowed",
    "real_money_allowed",
    "money_movement_allowed",
    "bank_access_allowed",
    "credential_storage_allowed",
    "credential_request_allowed",
    "account_identifier_storage_allowed",
    "account_identifier_read_allowed",
    "live_execution_allowed",
    "live_capital_action_authorized",
    "deposit_allowed",
    "withdrawal_allowed",
    "ach_allowed",
    "wire_allowed",
    "card_transfer_allowed",
    "fixed_return_target_promised",
    "profit_claim_authorized",
)

SENSITIVE_KEY_PARTS = (
    "api_key",
    "token_value",
    "secret",
    "password",
    "master_password",
    "vault_password",
    "account_number",
    "routing_number",
    "card_number",
    "debit_card_number",
    "cvv",
    "account_id",
    "oanda_account_id",
    "bearer",
    "broker_token",
    "access_token",
    "private_key",
)

SAFE_METADATA_KEYS = frozenset(
    {
        "approval_token_required",
        "approval_token_metadata_present",
        "approval_token_id_present",
        "approval_token_unexpired",
        "approval_token_unused",
        "approval_challenge_hash_present",
        "approval_timestamp_present",
        "secret_scan_required",
        "secrets_manager_required",
        "no_raw_secret_logging",
        "credential_redaction_required",
        "credential_storage_allowed",
        "credential_read_allowed",
        "credential_request_allowed",
        "credential_stored",
        "credential_read",
        "api_key_stored",
        "master_password_used",
        "vault_password_used",
        "account_identifier_storage_allowed",
        "account_identifier_read_allowed",
        "account_id_provided",
        "account_identifier_values_provided",
        "no_stored_account_id",
    }
)


def evaluate_forex_completion_campaign_part3_owner_validation_and_pr_landing_v1(
    payload: dict | None = None,
) -> dict[str, Any]:
    """Evaluate Part 1/2/3 landing metadata without runtime side effects."""

    source = payload if isinstance(payload, Mapping) else {}
    sensitive_data_blockers = _sensitive_data_blockers(source)
    sensitive_data_detected = bool(sensitive_data_blockers)
    if sensitive_data_detected:
        part1_file_manifest = _redacted_file_manifest(PART1_FILES)
        part2_file_manifest = _redacted_file_manifest(PART2_FILES)
        part3_file_manifest = _redacted_file_manifest(PART3_FILES)
        validation_summary = _redacted_validation_summary(sensitive_data_blockers)
        dirty_state_summary = _redacted_dirty_state_summary(sensitive_data_blockers)
        safety_boundary_summary = _redacted_safety_boundary_summary(
            sensitive_data_blockers
        )
        owner_validation_summary = _redacted_owner_validation_summary(
            sensitive_data_blockers
        )
    else:
        part1_file_manifest = _file_manifest(source.get("part1_files"), PART1_FILES)
        part2_file_manifest = _file_manifest(source.get("part2_files"), PART2_FILES)
        part3_file_manifest = _file_manifest(source.get("part3_files"), PART3_FILES)
        validation_summary = _validation_summary(source.get("validation_results"))
        dirty_state_summary = _dirty_state_summary(source.get("dirty_state"))
        safety_boundary_summary = _safety_boundary_summary(source)
        owner_validation_summary = _owner_validation_summary(
            source.get("owner_validation")
        )
    landing_status, landing_blockers, missing_inputs = _landing_status(
        source=source,
        sensitive_data_blockers=sensitive_data_blockers,
        part1_file_manifest=part1_file_manifest,
        part2_file_manifest=part2_file_manifest,
        part3_file_manifest=part3_file_manifest,
        validation_summary=validation_summary,
        dirty_state_summary=dirty_state_summary,
        safety_boundary_summary=safety_boundary_summary,
        owner_validation_summary=owner_validation_summary,
    )
    landing_ready = landing_status in {
        PART3_READY_FOR_COMMIT_APPROVAL,
        PART3_READY_FOR_PR_LANDING_APPROVAL,
    }
    next_best_packet = _next_best_packet(landing_status)

    result: dict[str, Any] = {
        "schema": SCHEMA,
        "mode": MODE,
        "landing_status": landing_status,
        "landing_ready": landing_ready,
        "owner_decision_required": True,
        "commit_approval_required": True,
        "push_approval_required": True,
        "pr_approval_required": True,
        "merge_approval_required": True,
        "read_only": True,
        "metadata_only": True,
        "part1_file_manifest": part1_file_manifest,
        "part2_file_manifest": part2_file_manifest,
        "part3_file_manifest": part3_file_manifest,
        "validation_summary": validation_summary,
        "dirty_state_summary": dirty_state_summary,
        "safety_boundary_summary": safety_boundary_summary,
        "owner_validation_summary": owner_validation_summary,
        "landing_command_preview": _landing_command_preview(),
        "blocked_commands": _blocked_commands(),
        "landing_blockers": list(landing_blockers),
        "missing_inputs": list(missing_inputs),
        "sensitive_data_detected": sensitive_data_detected,
        "sensitive_data_blockers": list(sensitive_data_blockers),
        "owner_action_queue": _owner_action_queue(
            landing_status=landing_status,
            landing_blockers=landing_blockers,
            next_best_packet=next_best_packet,
        ),
        "next_best_packet": next_best_packet,
        "safe_manual_next_action": _safe_manual_next_action(landing_status),
        "audit_record": _audit_record(
            source=source,
            landing_status=landing_status,
            landing_ready=landing_ready,
            sensitive_data_detected=sensitive_data_detected,
            next_best_packet=next_best_packet,
            landing_blockers=landing_blockers,
        ),
        "safety": _safety_summary(),
    }
    result.update(_false_map(HARD_FALSE_FIELDS))
    result.update(_false_map(SAFETY_FALSE_FIELDS))
    return result


def _landing_status(
    *,
    source: Mapping[str, Any],
    sensitive_data_blockers: Sequence[str],
    part1_file_manifest: Mapping[str, Any],
    part2_file_manifest: Mapping[str, Any],
    part3_file_manifest: Mapping[str, Any],
    validation_summary: Mapping[str, Any],
    dirty_state_summary: Mapping[str, Any],
    safety_boundary_summary: Mapping[str, Any],
    owner_validation_summary: Mapping[str, Any],
) -> tuple[str, list[str], list[str]]:
    if not source:
        return INCOMPLETE_INPUTS, ["payload_mapping_required"], [
            "payload_mapping_required"
        ]
    if sensitive_data_blockers:
        return BLOCKED_BY_SENSITIVE_DATA, list(sensitive_data_blockers), []
    if not part1_file_manifest["all_present"]:
        missing = _missing_file_inputs("part1_files", part1_file_manifest)
        return BLOCKED_BY_MISSING_PART1_FILES, missing, missing
    if not part2_file_manifest["all_present"]:
        missing = _missing_file_inputs("part2_files", part2_file_manifest)
        return BLOCKED_BY_MISSING_PART2_FILES, missing, missing
    if not part3_file_manifest["all_present"]:
        missing = _missing_file_inputs("part3_files", part3_file_manifest)
        return INCOMPLETE_INPUTS, missing, missing
    if validation_summary["failed_validators"]:
        blockers = list(validation_summary["failed_validators"])
        return BLOCKED_BY_VALIDATION_FAILURE, blockers, []
    if dirty_state_summary["unrelated_dirty_files_present"] is True:
        return (
            BLOCKED_BY_UNRELATED_DIRTY_FILES,
            ["unrelated_dirty_files_present"],
            [],
        )
    if dirty_state_summary["staged_files_present"] is True:
        return BLOCKED_BY_UNRELATED_DIRTY_FILES, ["staged_files_present"], []
    if safety_boundary_summary["safety_boundary_breached"]:
        blockers = list(safety_boundary_summary["safety_boundary_blockers"])
        return BLOCKED_BY_SAFETY_BOUNDARY, blockers, []

    if not owner_validation_summary["metadata_complete"]:
        missing = list(owner_validation_summary["missing_fields"])
        return PART3_OWNER_VALIDATION_READY, missing, missing

    if not validation_summary["all_passed"]:
        blockers = list(validation_summary["non_passing_validators"])
        return PART3_OWNER_VALIDATION_READY, blockers, blockers

    if dirty_state_summary["same_mission_or_clean"] is not True:
        return (
            PART3_OWNER_VALIDATION_READY,
            ["dirty_state_metadata_not_confirmed_same_mission_or_clean"],
            ["dirty_state_metadata_not_confirmed_same_mission_or_clean"],
        )

    if (
        owner_validation_summary["owner_commit_approval_recorded"] is True
        and (
            owner_validation_summary["push_approval_recorded"] is not True
            or owner_validation_summary["pr_approval_recorded"] is not True
        )
    ):
        return PART3_READY_FOR_PR_LANDING_APPROVAL, [], []

    if owner_validation_summary["owner_commit_approval_recorded"] is True:
        return PART3_READY_FOR_PR_LANDING_APPROVAL, [], []

    return PART3_READY_FOR_COMMIT_APPROVAL, [], []


def _file_manifest(value: Any, expected_paths: Sequence[str]) -> dict[str, Any]:
    observed = value if isinstance(value, Mapping) else {}
    present = [path for path in expected_paths if observed.get(path) is True]
    missing = [path for path in expected_paths if observed.get(path) is not True]
    extra = sorted(
        str(path)
        for path in observed.keys()
        if str(path) not in set(expected_paths)
    )
    return {
        "expected_count": len(expected_paths),
        "present_count": len(present),
        "missing_count": len(missing),
        "all_present": not missing,
        "expected_paths": list(expected_paths),
        "present_paths": present,
        "missing_paths": missing,
        "extra_paths": extra,
    }


def _validation_summary(value: Any) -> dict[str, Any]:
    results = value if isinstance(value, Mapping) else {}
    normalized = {str(key): str(status).upper() for key, status in results.items()}
    failed = [name for name, status in normalized.items() if status == "FAIL"]
    passed = [name for name, status in normalized.items() if status == "PASS"]
    non_passing = [
        name for name, status in normalized.items() if status != "PASS"
    ]
    return {
        "results": normalized,
        "validator_count": len(normalized),
        "passed_validators": sorted(passed),
        "failed_validators": sorted(failed),
        "non_passing_validators": sorted(non_passing),
        "all_passed": bool(normalized) and not non_passing,
    }


def _redacted_file_manifest(expected_paths: Sequence[str]) -> dict[str, Any]:
    return {
        "expected_count": len(expected_paths),
        "present_count": 0,
        "missing_count": 0,
        "all_present": False,
        "expected_paths": list(expected_paths),
        "present_paths": [],
        "missing_paths": [],
        "extra_paths": [],
        "input_redacted": True,
    }


def _redacted_validation_summary(blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "results": {},
        "validator_count": 0,
        "passed_validators": [],
        "failed_validators": [],
        "non_passing_validators": [],
        "all_passed": False,
        "input_redacted": True,
        "blockers": list(blockers),
    }


def _redacted_dirty_state_summary(blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "branch": None,
        "same_mission_untracked_only": None,
        "unrelated_dirty_files_present": None,
        "staged_files_present": None,
        "same_mission_or_clean": False,
        "input_redacted": True,
        "blockers": list(blockers),
    }


def _redacted_safety_boundary_summary(blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "observed_hard_false_fields": _false_map(HARD_FALSE_FIELDS),
        "safety_boundary_breached": False,
        "safety_boundary_blockers": [],
        "hard_false_fields_intact": True,
        "read_only": True,
        "metadata_only": True,
        "input_redacted": True,
        "blockers": list(blockers),
    }


def _redacted_owner_validation_summary(blockers: Sequence[str]) -> dict[str, Any]:
    return {
        "metadata_complete": False,
        "missing_fields": [],
        "owner_review_required": None,
        "commit_approval_required": None,
        "push_approval_required": None,
        "pr_approval_required": None,
        "merge_approval_required": None,
        "owner_has_not_approved_commit_yet": None,
        "owner_commit_approval_recorded": False,
        "push_approval_recorded": False,
        "pr_approval_recorded": False,
        "merge_approval_recorded": False,
        "input_redacted": True,
        "blockers": list(blockers),
    }


def _dirty_state_summary(value: Any) -> dict[str, Any]:
    data = value if isinstance(value, Mapping) else {}
    unrelated = _bool(data.get("unrelated_dirty_files_present"), default=None)
    staged = _bool(data.get("staged_files_present"), default=None)
    same_mission = _bool(data.get("same_mission_untracked_only"), default=None)
    branch = _text(data.get("branch"))
    same_mission_or_clean = (
        unrelated is False and staged is False and same_mission in {True, False}
    )
    return {
        "branch": branch,
        "same_mission_untracked_only": same_mission,
        "unrelated_dirty_files_present": unrelated,
        "staged_files_present": staged,
        "same_mission_or_clean": same_mission_or_clean,
    }


def _safety_boundary_summary(source: Mapping[str, Any]) -> dict[str, Any]:
    boundary = _mapping(source.get("safety_boundary"))
    observed: dict[str, bool] = {}
    blockers: list[str] = []
    for field in HARD_FALSE_FIELDS:
        value = _bool(boundary.get(field), default=_bool(source.get(field), default=False))
        observed[field] = bool(value)
        if value is True:
            blockers.append(f"{field}_true")
    return {
        "observed_hard_false_fields": observed,
        "safety_boundary_breached": bool(blockers),
        "safety_boundary_blockers": blockers,
        "hard_false_fields_intact": not blockers,
        "read_only": True,
        "metadata_only": True,
    }


def _owner_validation_summary(value: Any) -> dict[str, Any]:
    data = value if isinstance(value, Mapping) else {}
    required_true = (
        "owner_review_required",
        "commit_approval_required",
        "push_approval_required",
        "pr_approval_required",
        "merge_approval_required",
    )
    missing: list[str] = []
    for field in required_true:
        if _bool(data.get(field), default=None) is not True:
            missing.append(field)
    owner_commit_approval_recorded = _bool(
        data.get("owner_commit_approval_recorded"), default=False
    )
    owner_has_not_approved_commit_yet = _bool(
        data.get("owner_has_not_approved_commit_yet"), default=None
    )
    if (
        owner_commit_approval_recorded is not True
        and owner_has_not_approved_commit_yet is not True
    ):
        missing.append("owner_has_not_approved_commit_yet_or_commit_record")
    return {
        "metadata_complete": bool(data) and not missing,
        "missing_fields": missing,
        "owner_review_required": _bool(data.get("owner_review_required")),
        "commit_approval_required": _bool(data.get("commit_approval_required")),
        "push_approval_required": _bool(data.get("push_approval_required")),
        "pr_approval_required": _bool(data.get("pr_approval_required")),
        "merge_approval_required": _bool(data.get("merge_approval_required")),
        "owner_has_not_approved_commit_yet": owner_has_not_approved_commit_yet,
        "owner_commit_approval_recorded": owner_commit_approval_recorded,
        "push_approval_recorded": _bool(
            data.get("push_approval_recorded"), default=False
        ),
        "pr_approval_recorded": _bool(data.get("pr_approval_recorded"), default=False),
        "merge_approval_recorded": _bool(
            data.get("merge_approval_recorded"), default=False
        ),
    }


def _landing_command_preview() -> dict[str, Any]:
    paths = [*PART1_FILES, *PART2_FILES, *PART3_FILES]
    feature_branch = "feature/forex-completion-campaign-owner-validation-v1"
    return {
        "text_only": True,
        "inert_preview_only": True,
        "commands": [
            "git status --short --branch",
            f"git switch -c {feature_branch}",
            "git add " + " ".join(paths),
            'git commit -m "feat: add forex completion campaign owner validation"',
            f"git push -u origin {feature_branch}",
            (
                f"gh pr create --base main --head {feature_branch} "
                '--title "feat: add forex completion campaign owner validation" '
                '--body "Owner validation and PR landing prep for Forex completion campaign."'
            ),
        ],
    }


def _blocked_commands() -> list[str]:
    return [
        "not executed by this packet",
        "requires Anthony approval",
        "no staging occurred",
        "no commit occurred",
        "no push occurred",
        "no PR occurred",
        "no merge occurred",
    ]


def _owner_action_queue(
    *,
    landing_status: str,
    landing_blockers: Sequence[str],
    next_best_packet: str,
) -> list[dict[str, Any]]:
    return [
        {
            "action_id": action_id,
            "owner_decision_required": True,
            "landing_status": landing_status,
            "blocked_by": list(landing_blockers),
            "next_best_packet": next_best_packet if action_id == "REVIEW_NEXT_PACKET" else None,
            **_false_map(HARD_FALSE_FIELDS),
            **_false_map(SAFETY_FALSE_FIELDS),
        }
        for action_id in (
            "REVIEW_PART1_MANIFEST",
            "REVIEW_PART2_MANIFEST",
            "REVIEW_PART3_MANIFEST",
            "REVIEW_VALIDATOR_BUNDLE",
            "REVIEW_DIRTY_STATE",
            "REVIEW_COMMAND_PREVIEW",
            "REVIEW_NEXT_PACKET",
        )
    ]


def _next_best_packet(status: str) -> str:
    if status in {
        PART3_OWNER_VALIDATION_READY,
        PART3_READY_FOR_COMMIT_APPROVAL,
        PART3_READY_FOR_PR_LANDING_APPROVAL,
    }:
        return NEXT_PACKET_PART4
    return SCHEMA


def _safe_manual_next_action(status: str) -> str:
    if status == PART3_READY_FOR_COMMIT_APPROVAL:
        return (
            "Anthony reviews the exact diff and may approve a separate commit packet; "
            "this packet executed no staging."
        )
    if status == PART3_READY_FOR_PR_LANDING_APPROVAL:
        return (
            "Anthony reviews push and PR landing approval in a separate protected packet."
        )
    if status == PART3_OWNER_VALIDATION_READY:
        return "Review owner validation metadata, validator evidence, and inert commands."
    if status == BLOCKED_BY_SENSITIVE_DATA:
        return "Remove sensitive keys or values and rerun with metadata only."
    if status == BLOCKED_BY_VALIDATION_FAILURE:
        return "Repair the failing validator before owner commit approval."
    if status == BLOCKED_BY_UNRELATED_DIRTY_FILES:
        return "Classify or remove unrelated/staged dirty state before landing review."
    if status == BLOCKED_BY_SAFETY_BOUNDARY:
        return "Stop and repair the breached safety metadata before continuing."
    return "Provide the missing manifest metadata and rerun."


def _audit_record(
    *,
    source: Mapping[str, Any],
    landing_status: str,
    landing_ready: bool,
    sensitive_data_detected: bool,
    next_best_packet: str,
    landing_blockers: Sequence[str],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "evaluated_at_utc": _fixed_utc_iso(),
        "input_fields_seen": _safe_input_fields_seen(
            source, redacted=sensitive_data_detected
        ),
        "landing_status": landing_status,
        "landing_ready": landing_ready,
        "input_redacted": sensitive_data_detected,
        "next_best_packet": next_best_packet,
        "landing_blockers": list(landing_blockers),
        "read_only": True,
        "metadata_only": True,
        **_false_map(HARD_FALSE_FIELDS),
        **_false_map(SAFETY_FALSE_FIELDS),
    }


def _safety_summary() -> dict[str, Any]:
    return {
        "read_only": True,
        "metadata_only": True,
        "owner_gate_required": True,
        "commit_gate_required": True,
        "push_gate_required": True,
        "pr_gate_required": True,
        "merge_gate_required": True,
        "command_preview_inert_text_only": True,
        **_false_map(HARD_FALSE_FIELDS),
        **_false_map(SAFETY_FALSE_FIELDS),
    }


def _sensitive_data_blockers(value: Any, path: str = "payload") -> list[str]:
    blockers: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            normalized = _normalize_key(str(key))
            child_path = f"{path}.{_safe_key_label(normalized)}"
            if normalized in SAFE_METADATA_KEYS:
                if not _safe_metadata_value_allowed(child):
                    blockers.append(f"unsafe_metadata_value:{child_path}")
                continue
            matched = _matched_sensitive_part(normalized)
            if matched:
                blockers.append(f"sensitive_key:{path}.{matched}")
                continue
            blockers.extend(_sensitive_data_blockers(child, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            blockers.extend(_sensitive_data_blockers(child, f"{path}[{index}]"))
    elif isinstance(value, str) and _looks_like_sensitive_value(value):
        blockers.append(f"sensitive_value:{path}")
    return _unique(blockers)


def _matched_sensitive_part(normalized_key: str) -> str | None:
    for part in SENSITIVE_KEY_PARTS:
        if part in normalized_key:
            return part
    return None


def _safe_metadata_value_allowed(value: Any) -> bool:
    if isinstance(value, bool | int | float) or value is None:
        return True
    if isinstance(value, str):
        return not _looks_like_sensitive_value(value)
    if isinstance(value, Mapping):
        return not _sensitive_data_blockers(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return all(_safe_metadata_value_allowed(item) for item in value)
    return False


def _looks_like_sensitive_value(value: str) -> bool:
    lowered = value.strip().lower()
    if not lowered:
        return False
    sensitive_markers = (
        "sk-",
        "bearer ",
        "api key",
        "token value",
        "broker token",
        "access token",
        "private key",
        "password",
        "secret",
        "-----begin",
    )
    if any(marker in lowered for marker in sensitive_markers):
        return True
    return _has_long_digit_run(lowered, minimum=8)


def _missing_file_inputs(
    prefix: str, manifest: Mapping[str, Any]
) -> list[str]:
    return [f"{prefix}:{path}" for path in _list(manifest.get("missing_paths"))]


def _safe_input_fields_seen(
    source: Mapping[str, Any], *, redacted: bool
) -> list[str]:
    if not redacted:
        return sorted(str(key) for key in source.keys())
    return sorted(
        str(key)
        for key in source.keys()
        if not _matched_sensitive_part(_normalize_key(str(key)))
    )


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[str]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [str(item) for item in value]
    return []


def _bool(value: Any, default: bool | None = None) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "y", "on"}:
            return True
        if lowered in {"false", "0", "no", "n", "off"}:
            return False
    return default


def _text(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _false_map(fields: Sequence[str]) -> dict[str, bool]:
    return {field: False for field in fields}


def _normalize_key(value: str) -> str:
    return value.strip().lower().replace("-", "_").replace(" ", "_")


def _safe_key_label(normalized_key: str) -> str:
    matched = _matched_sensitive_part(normalized_key)
    return matched if matched else normalized_key


def _has_long_digit_run(text: str, *, minimum: int) -> bool:
    run = 0
    for char in text:
        if char.isdigit():
            run += 1
            if run >= minimum:
                return True
        else:
            run = 0
    return False


def _unique(values: Sequence[Any]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        text = str(value)
        if text and text not in seen:
            seen.add(text)
            output.append(text)
    return output


def _fixed_utc_iso() -> str:
    return (
        datetime(1970, 1, 1, tzinfo=timezone.utc)
        .isoformat()
        .replace("+00:00", "Z")
    )


__all__ = [
    "SCHEMA",
    "MODE",
    "PART3_OWNER_VALIDATION_READY",
    "PART3_READY_FOR_COMMIT_APPROVAL",
    "PART3_READY_FOR_PR_LANDING_APPROVAL",
    "BLOCKED_BY_MISSING_PART1_FILES",
    "BLOCKED_BY_MISSING_PART2_FILES",
    "BLOCKED_BY_VALIDATION_FAILURE",
    "BLOCKED_BY_SENSITIVE_DATA",
    "BLOCKED_BY_UNRELATED_DIRTY_FILES",
    "BLOCKED_BY_SAFETY_BOUNDARY",
    "INCOMPLETE_INPUTS",
    "NEXT_PACKET_PART4",
    "PART1_FILES",
    "PART2_FILES",
    "PART3_FILES",
    "HARD_FALSE_FIELDS",
    "SAFETY_FALSE_FIELDS",
    "evaluate_forex_completion_campaign_part3_owner_validation_and_pr_landing_v1",
]
