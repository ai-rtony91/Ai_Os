"""Build non-executable human-review packet drafts from operator reports."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

SCHEMA = "AIOS_HUMAN_APPROVED_PACKET_DRAFT.v1"
REPORT_SCHEMA = "AIOS_OPERATOR_CHAIN_REPORT.v1"
COMPONENT = "human_approved_packet_draft_generator"
MODE = "READ_ONLY_NON_EXECUTABLE_PACKET_DRAFT"

ALLOWED_REPORT_VERDICTS = {
    "REPORT_HUMAN_APPROVAL_REQUIRED",
    "REPORT_APPLY_REVIEW_READY",
    "REPORT_CHAIN_REVIEW_COMPLETE",
}

EXECUTABLE_MARKERS = (
    "codex-only prompt",
    "ai_os execution token",
)

EXECUTABLE_TRUE_KEYS = {
    "executable",
    "execution_token_present",
    "codex_prompt_present",
    "executable_packet_emitted",
}

UNSAFE_TERMS = (
    "secret",
    "secrets",
    "credential",
    "credentials",
    "broker",
    "oanda",
    "live trading",
    "live-trading",
    "live order",
    "real order",
    "webhook execution",
    "production",
    "scheduler",
    "daemon",
    "worker launch",
    "dashboard mutation",
    "git add",
    "git commit",
    "git push",
    "commit",
    "push",
    "merge",
    "deployment",
    ".env",
)

SAFE_REFERENCE_KEYS = {
    "blocked_actions",
    "forbidden_files",
    "forbidden_paths",
}

HARD_SAFETY_FALSE_FIELDS = (
    "self_approval_allowed",
    "apply_allowed",
    "apply_performed",
    "commands_executed",
    "files_written",
    "mutations_performed",
    "executable_packet_emitted",
    "execution_token_emitted",
    "codex_prompt_emitted",
    "worker_launch_allowed",
    "scheduler_allowed",
    "daemon_allowed",
    "broker_allowed",
    "live_trading_allowed",
    "production_allowed",
    "dashboard_mutation_allowed",
    "commit_allowed",
    "push_allowed",
    "merge_allowed",
)

REQUIRED_REPORT_FIELDS = (
    "schema",
    "report_id",
    "verdict",
    "report_state",
    "inherited_chain_verdict",
    "inherited_chain_state",
    "hard_safety_all_false",
    "report_json",
    "next_safe_action",
)

DEFAULT_BLOCKED_ACTIONS = (
    "APPLY",
    "worker_launch",
    "scheduler",
    "broker_live_trading",
    "commit_push_merge",
)

DEFAULT_FINAL_REPORT_FIELDS = (
    "SUMMARY",
    "FILES CHANGED",
    "VALIDATORS",
    "SAFETY CONFIRMATION",
    "GIT STATUS",
    "COMMIT STATUS",
    "PUSH STATUS",
    "NEXT SAFE ACTION",
    "STATUS",
)


def build_human_approved_packet_draft(
    operator_report: Mapping[str, Any] | None,
    now_utc: str | None = None,
) -> dict[str, Any]:
    """Return a non-executable draft object for human review only."""

    generated_at = now_utc or _utc_now()
    draft_id = _draft_id(operator_report)

    if not isinstance(operator_report, Mapping):
        return _result(
            generated_at_utc=generated_at,
            draft_id=draft_id,
            verdict="BLOCKED_OPERATOR_REPORT_MISSING",
            draft_state="BLOCKED",
            operator_report=None,
            blockers=["operator_report_missing_or_non_object"],
            next_safe_action="Provide one object-shaped operator chain report.",
        )

    if _contains_executable_content(operator_report):
        return _result(
            generated_at_utc=generated_at,
            draft_id=draft_id,
            verdict="BLOCKED_EXECUTABLE_CONTENT",
            draft_state="BLOCKED",
            operator_report=None,
            blockers=["executable_content_detected"],
            next_safe_action="Remove executable markers and token-bearing fields before drafting.",
        )

    if _contains_unsafe_terms(operator_report):
        return _result(
            generated_at_utc=generated_at,
            draft_id=draft_id,
            verdict="BLOCKED_UNSAFE_CONTENT",
            draft_state="BLOCKED",
            operator_report=None,
            blockers=["unsafe_content_detected"],
            next_safe_action="Remove unsafe scope content before drafting.",
        )

    if not _is_well_formed_operator_report(operator_report):
        return _result(
            generated_at_utc=generated_at,
            draft_id=draft_id,
            verdict="BLOCKED_OPERATOR_REPORT_MALFORMED",
            draft_state="BLOCKED",
            operator_report=operator_report,
            blockers=["operator_report_malformed"],
            next_safe_action="Provide a complete AIOS_OPERATOR_CHAIN_REPORT.v1 object.",
        )

    report_verdict = _string(operator_report.get("verdict"))
    if report_verdict.startswith("BLOCKED") or report_verdict == "REPORT_BLOCKED_CHAIN" or report_verdict not in ALLOWED_REPORT_VERDICTS:
        return _result(
            generated_at_utc=generated_at,
            draft_id=draft_id,
            verdict="BLOCKED_OPERATOR_REPORT_NOT_READY",
            draft_state="BLOCKED",
            operator_report=operator_report,
            blockers=["operator_report_not_human_gated_ready"],
            next_safe_action="Use only human-gated non-blocked operator reports for draft generation.",
        )

    if not _hard_safety_valid(operator_report):
        return _result(
            generated_at_utc=generated_at,
            draft_id=draft_id,
            verdict="BLOCKED_HARD_SAFETY_VIOLATION",
            draft_state="BLOCKED",
            operator_report=operator_report,
            blockers=["hard_safety_violation"],
            next_safe_action="Stop until the operator report proves all hard safety fields are false.",
        )

    allowed_paths = _extract_scope_list(operator_report, "allowed_paths")
    forbidden_paths = _extract_scope_list(operator_report, "forbidden_paths")
    validator_chain = _extract_scope_list(operator_report, "validator_chain")
    if not allowed_paths or not forbidden_paths or not validator_chain:
        return _result(
            generated_at_utc=generated_at,
            draft_id=draft_id,
            verdict="BLOCKED_PACKET_SCOPE_UNKNOWN",
            draft_state="BLOCKED",
            operator_report=operator_report,
            blockers=["packet_scope_or_validators_unknown"],
            next_safe_action="Provide allowed_paths, forbidden_paths, and validator_chain in the operator report.",
        )

    packet_draft = _build_packet_draft(
        operator_report=operator_report,
        draft_id=draft_id,
        allowed_paths=allowed_paths,
        forbidden_paths=forbidden_paths,
        validator_chain=validator_chain,
    )
    return _result(
        generated_at_utc=generated_at,
        draft_id=draft_id,
        verdict="PACKET_DRAFT_READY",
        draft_state="READY_FOR_HUMAN_REVIEW",
        operator_report=operator_report,
        packet_draft=packet_draft,
        blockers=[],
        next_safe_action=packet_draft["next_safe_action"],
    )


def _build_packet_draft(
    *,
    operator_report: Mapping[str, Any],
    draft_id: str,
    allowed_paths: list[str],
    forbidden_paths: list[str],
    validator_chain: list[str],
) -> dict[str, Any]:
    report_json = operator_report.get("report_json")
    report_json = report_json if isinstance(report_json, Mapping) else {}
    apply_review_ready = bool(operator_report.get("apply_review_ready", False))
    suggested_mode = "APPLY_REVIEW" if apply_review_ready else "DRY_RUN"
    suggested_lane = "HUMAN_REVIEW"
    source_report_id = _string(operator_report.get("report_id"))
    source_chain_id = _string(operator_report.get("inherited_chain_id") or report_json.get("chain_id"))
    inherited_chain_verdict = _string(operator_report.get("inherited_chain_verdict") or report_json.get("chain_verdict"))
    return {
        "suggested_packet_id": "AIOS-HUMAN-REVIEW-DRAFT-" + draft_id.rsplit("-", 1)[-1].upper(),
        "source_report_id": source_report_id,
        "source_chain_id": source_chain_id,
        "inherited_chain_verdict": inherited_chain_verdict,
        "suggested_mode": suggested_mode,
        "suggested_lane": suggested_lane,
        "mission_summary": _mission_summary(operator_report),
        "allowed_paths": allowed_paths,
        "forbidden_paths": forbidden_paths,
        "validator_chain": validator_chain,
        "stop_point": _first_string(
            report_json.get("stop_point"),
            "Stop after human review; this draft does not authorize execution.",
        ),
        "rollback_note": _first_string(
            report_json.get("rollback_note"),
            _nested_string(report_json, ("dry_run_execution", "rollback_note")),
            _nested_string(report_json, ("apply_gate", "rollback_note")),
            "No mutation is performed by this non-executable draft.",
        ),
        "final_report_fields": list(DEFAULT_FINAL_REPORT_FIELDS),
        "blocked_actions": list(DEFAULT_BLOCKED_ACTIONS),
        "approval_required": True,
        "next_safe_action": (
            "Separate human approval is required before any future APPLY packet."
            if apply_review_ready
            else _first_string(
                operator_report.get("next_safe_action"),
                "Human review is required before converting this draft into any executable work.",
            )
        ),
        "executable": False,
        "execution_token_present": False,
        "codex_prompt_present": False,
        "human_approval_required_before_execution": True,
        "human_must_convert_to_codex_packet": True,
    }


def _result(
    *,
    generated_at_utc: str,
    draft_id: str,
    verdict: str,
    draft_state: str,
    operator_report: Mapping[str, Any] | None,
    blockers: list[str],
    next_safe_action: str,
    packet_draft: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    source_report_id = _string(operator_report.get("report_id")) if isinstance(operator_report, Mapping) else ""
    source_report_verdict = _string(operator_report.get("verdict")) if isinstance(operator_report, Mapping) else "UNKNOWN"
    source_chain_verdict = _string(operator_report.get("inherited_chain_verdict")) if isinstance(operator_report, Mapping) else "UNKNOWN"
    source_chain_state = _string(operator_report.get("inherited_chain_state")) if isinstance(operator_report, Mapping) else "UNKNOWN"
    output: dict[str, Any] = {
        "schema": SCHEMA,
        "generated_at_utc": generated_at_utc,
        "component": COMPONENT,
        "mode": MODE,
        "draft_id": draft_id,
        "verdict": verdict,
        "draft_state": draft_state,
        "source_report_id": source_report_id,
        "source_report_verdict": source_report_verdict,
        "source_chain_verdict": source_chain_verdict,
        "source_chain_state": source_chain_state,
        "packet_draft": dict(packet_draft) if isinstance(packet_draft, Mapping) else None,
        "packet_draft_created": isinstance(packet_draft, Mapping),
        "non_executable_draft_only": True,
        "human_approval_required_before_execution": True,
        "blockers": blockers,
        "evidence_inputs": _evidence_inputs(operator_report),
        "next_safe_action": next_safe_action,
        "safety": _safety(),
    }
    output.update({field: False for field in HARD_SAFETY_FALSE_FIELDS})
    return output


def _contains_executable_content(value: Any) -> bool:
    for item in _walk_values(value):
        if isinstance(item, str) and any(marker in item.lower() for marker in EXECUTABLE_MARKERS):
            return True
    return _contains_true_key(value, EXECUTABLE_TRUE_KEYS)


def _contains_unsafe_terms(value: Any) -> bool:
    for item in _walk_values(value, skip_keys=SAFE_REFERENCE_KEYS):
        if isinstance(item, str) and any(term in item.lower() for term in UNSAFE_TERMS):
            return True
    return False


def _walk_values(value: Any, skip_keys: set[str] | None = None) -> list[Any]:
    skip_keys = skip_keys or set()
    if isinstance(value, Mapping):
        values: list[Any] = []
        for key, child in value.items():
            if str(key).lower() in skip_keys:
                continue
            values.extend(_walk_values(child, skip_keys=skip_keys))
        return values
    if isinstance(value, (list, tuple, set)):
        values = []
        for child in value:
            values.extend(_walk_values(child, skip_keys=skip_keys))
        return values
    return [value]


def _contains_true_key(value: Any, names: set[str]) -> bool:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key).lower() in names and child is True:
                return True
            if _contains_true_key(child, names):
                return True
    elif isinstance(value, (list, tuple, set)):
        return any(_contains_true_key(child, names) for child in value)
    return False


def _is_well_formed_operator_report(value: Mapping[str, Any]) -> bool:
    if value.get("schema") != REPORT_SCHEMA:
        return False
    if any(field not in value for field in REQUIRED_REPORT_FIELDS):
        return False
    return isinstance(value.get("report_json"), Mapping)


def _hard_safety_valid(value: Mapping[str, Any]) -> bool:
    if value.get("hard_safety_all_false") is not True:
        return False
    for field in HARD_SAFETY_FALSE_FIELDS:
        if value.get(field, False) is not False:
            return False
    safety = value.get("safety")
    if isinstance(safety, Mapping):
        for field in HARD_SAFETY_FALSE_FIELDS:
            if safety.get(field, False) is not False:
                return False
    return True


def _extract_scope_list(operator_report: Mapping[str, Any], field: str) -> list[str]:
    report_json = operator_report.get("report_json")
    report_json = report_json if isinstance(report_json, Mapping) else {}
    candidates = (
        report_json.get(field),
        _nested_value(report_json, ("dry_run_execution", field)),
        _nested_value(report_json, ("apply_gate", field)),
        operator_report.get(field),
    )
    for candidate in candidates:
        values = _string_list(candidate)
        if values:
            return values
    return []


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if item not in (None, "", [], {})]


def _mission_summary(operator_report: Mapping[str, Any]) -> str:
    report_json = operator_report.get("report_json")
    report_json = report_json if isinstance(report_json, Mapping) else {}
    return _first_string(
        report_json.get("mission_summary"),
        f"Human review of {operator_report.get('inherited_chain_verdict', 'UNKNOWN')} operator report.",
    )


def _nested_value(value: Mapping[str, Any], keys: tuple[str, ...]) -> Any:
    current: Any = value
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def _nested_string(value: Mapping[str, Any], keys: tuple[str, ...]) -> str:
    return _string(_nested_value(value, keys))


def _first_string(*values: Any) -> str:
    for value in values:
        text = _string(value).strip()
        if text:
            return text
    return ""


def _evidence_inputs(operator_report: Mapping[str, Any] | None) -> list[dict[str, str]]:
    if not isinstance(operator_report, Mapping):
        return [{"name": "operator_report", "status": "missing_or_non_object", "schema": ""}]
    return [
        {
            "name": "operator_report",
            "status": "provided",
            "schema": _string(operator_report.get("schema")),
            "verdict": _string(operator_report.get("verdict")),
            "report_id": _string(operator_report.get("report_id")),
        }
    ]


def _safety() -> dict[str, Any]:
    safety = {
        "read_only": True,
        "side_effect_free": True,
        "writes_work_packets": False,
        "non_executable_draft_only": True,
        "self_approval_allowed": False,
        "commands_executed": False,
        "files_written": False,
        "mutations_performed": False,
    }
    safety.update({field: False for field in HARD_SAFETY_FALSE_FIELDS if field not in safety})
    return safety


def _draft_id(operator_report: Mapping[str, Any] | None) -> str:
    encoded = json.dumps(_jsonable(operator_report), sort_keys=True, separators=(",", ":"), default=str)
    return "packet-draft-" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(child) for key, child in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_jsonable(child) for child in value]
    if isinstance(value, set):
        return sorted(_jsonable(child) for child in value)
    return value


def _string(value: Any) -> str:
    if value in (None, [], {}):
        return ""
    return value if isinstance(value, str) else str(value)


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
