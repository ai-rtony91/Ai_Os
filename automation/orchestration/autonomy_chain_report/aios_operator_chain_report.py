"""Compact operator report renderer for M16 chain harness output."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from datetime import UTC, datetime
from typing import Any

SCHEMA = "AIOS_OPERATOR_CHAIN_REPORT.v1"
CHAIN_SCHEMA = "AIOS_SELF_AUTONOMY_CHAIN_HARNESS.v1"
COMPONENT = "operator_chain_report"
MODE = "READ_ONLY_OPERATOR_CHAIN_REPORT"

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

REQUIRED_CHAIN_FIELDS = (
    "schema",
    "chain_id",
    "verdict",
    "chain_state",
    "component_verdicts",
    "component_states",
    "blockers",
    "next_safe_action",
)


def build_operator_chain_report(
    chain_result: Mapping[str, Any] | None,
    now_utc: str | None = None,
) -> dict[str, Any]:
    """Render a deterministic operator report from injected M16 output."""

    generated_at = now_utc or _utc_now()
    report_id = _report_id(chain_result)

    if not isinstance(chain_result, Mapping):
        return _report(
            generated_at_utc=generated_at,
            report_id=report_id,
            verdict="BLOCKED_CHAIN_RESULT_MISSING",
            report_state="BLOCKED",
            chain_result=None,
            hard_safety_all_false=False,
            blockers=["chain_result_missing_or_non_object"],
            next_safe_action="Provide an object-shaped M16 chain result before rendering.",
        )

    if _contains_executable_content(chain_result):
        return _report(
            generated_at_utc=generated_at,
            report_id=report_id,
            verdict="BLOCKED_EXECUTABLE_CONTENT",
            report_state="BLOCKED",
            chain_result=None,
            hard_safety_all_false=False,
            blockers=["executable_content_detected"],
            next_safe_action="Remove executable markers and token-bearing fields before rendering.",
        )

    if _contains_unsafe_terms(chain_result):
        return _report(
            generated_at_utc=generated_at,
            report_id=report_id,
            verdict="BLOCKED_UNSAFE_CONTENT",
            report_state="BLOCKED",
            chain_result=None,
            hard_safety_all_false=False,
            blockers=["unsafe_content_detected"],
            next_safe_action="Remove unsafe content before rendering an operator report.",
        )

    if not _is_well_formed_chain_result(chain_result):
        return _report(
            generated_at_utc=generated_at,
            report_id=report_id,
            verdict="BLOCKED_CHAIN_RESULT_MALFORMED",
            report_state="BLOCKED",
            chain_result=chain_result,
            hard_safety_all_false=False,
            blockers=["chain_result_malformed"],
            next_safe_action="Provide a complete AIOS_SELF_AUTONOMY_CHAIN_HARNESS.v1 result.",
        )

    hard_safety_all_false = _hard_safety_all_false(chain_result)
    if not hard_safety_all_false:
        return _report(
            generated_at_utc=generated_at,
            report_id=report_id,
            verdict="BLOCKED_HARD_SAFETY_VIOLATION",
            report_state="BLOCKED",
            chain_result=chain_result,
            hard_safety_all_false=False,
            blockers=["hard_safety_field_true_or_missing"],
            next_safe_action="Stop and review hard safety fields before rendering as safe.",
        )

    chain_verdict = _string(chain_result.get("verdict"))
    if chain_verdict.startswith("BLOCKED"):
        verdict = "REPORT_BLOCKED_CHAIN"
        report_state = "CHAIN_BLOCKED_REPORTED"
    elif chain_verdict == "CHAIN_HUMAN_APPROVAL_REQUIRED":
        verdict = "REPORT_HUMAN_APPROVAL_REQUIRED"
        report_state = "HUMAN_APPROVAL_REQUIRED_REPORTED"
    elif chain_verdict == "CHAIN_APPLY_REVIEW_READY":
        verdict = "REPORT_APPLY_REVIEW_READY"
        report_state = "APPLY_REVIEW_READY_REPORTED"
    elif chain_verdict == "CHAIN_REVIEW_COMPLETE":
        verdict = "REPORT_CHAIN_REVIEW_COMPLETE"
        report_state = "CHAIN_REVIEW_COMPLETE_REPORTED"
    else:
        verdict = "REPORT_REVIEW_REQUIRED"
        report_state = "REVIEW_REQUIRED"

    return _report(
        generated_at_utc=generated_at,
        report_id=report_id,
        verdict=verdict,
        report_state=report_state,
        chain_result=chain_result,
        hard_safety_all_false=True,
        blockers=_string_list(chain_result.get("blockers")),
        next_safe_action=_string(chain_result.get("next_safe_action")),
    )


def _report(
    *,
    generated_at_utc: str,
    report_id: str,
    verdict: str,
    report_state: str,
    chain_result: Mapping[str, Any] | None,
    hard_safety_all_false: bool,
    blockers: list[str],
    next_safe_action: str,
) -> dict[str, Any]:
    report_json = _report_json(
        chain_result=chain_result,
        hard_safety_all_false=hard_safety_all_false,
        blockers=blockers,
        next_safe_action=next_safe_action,
    )
    report_markdown = _report_markdown(
        report_verdict=verdict,
        report_state=report_state,
        report_json=report_json,
    )
    output: dict[str, Any] = {
        "schema": SCHEMA,
        "generated_at_utc": generated_at_utc,
        "component": COMPONENT,
        "mode": MODE,
        "report_id": report_id,
        "verdict": verdict,
        "report_state": report_state,
        "inherited_chain_id": report_json["chain_id"],
        "inherited_chain_verdict": report_json["chain_verdict"],
        "inherited_chain_state": report_json["chain_state"],
        "first_blocking_component": report_json["first_blocking_component"],
        "human_approval_required": report_json["human_approval_required"],
        "explicit_human_approval_present": report_json["explicit_human_approval_present"],
        "apply_review_ready": report_json["apply_review_ready"],
        "hard_safety_all_false": hard_safety_all_false,
        "component_verdicts": report_json["component_verdicts"],
        "component_states": report_json["component_states"],
        "blockers": blockers,
        "report_json": report_json,
        "report_markdown": report_markdown,
        "next_safe_action": next_safe_action,
        "safety": _safety(),
    }
    output.update({field: False for field in HARD_SAFETY_FALSE_FIELDS})
    return output


def _report_json(
    *,
    chain_result: Mapping[str, Any] | None,
    hard_safety_all_false: bool,
    blockers: list[str],
    next_safe_action: str,
) -> dict[str, Any]:
    if not isinstance(chain_result, Mapping):
        return {
            "chain_id": "",
            "chain_verdict": "UNKNOWN",
            "chain_state": "UNKNOWN",
            "first_blocking_component": None,
            "human_approval_required": True,
            "explicit_human_approval_present": False,
            "apply_review_ready": False,
            "hard_safety_all_false": hard_safety_all_false,
            "component_verdicts": {},
            "component_states": {},
            "blockers": blockers,
            "next_safe_action": next_safe_action,
        }
    return {
        "chain_id": _string(chain_result.get("chain_id")),
        "chain_verdict": _string(chain_result.get("verdict")),
        "chain_state": _string(chain_result.get("chain_state")),
        "first_blocking_component": _optional_string(chain_result.get("first_blocking_component")),
        "human_approval_required": bool(chain_result.get("human_approval_required", True)),
        "explicit_human_approval_present": bool(chain_result.get("explicit_human_approval_present", False)),
        "apply_review_ready": bool(chain_result.get("apply_review_ready", False)),
        "hard_safety_all_false": hard_safety_all_false,
        "component_verdicts": _mapping_of_strings(chain_result.get("component_verdicts")),
        "component_states": _mapping_of_strings(chain_result.get("component_states")),
        "blockers": blockers,
        "next_safe_action": next_safe_action,
    }


def _report_markdown(
    *,
    report_verdict: str,
    report_state: str,
    report_json: Mapping[str, Any],
) -> str:
    component_lines = []
    component_verdicts = report_json.get("component_verdicts", {})
    component_states = report_json.get("component_states", {})
    if isinstance(component_verdicts, Mapping) and isinstance(component_states, Mapping):
        for name in sorted(component_verdicts):
            component_lines.append(f"- {name}: {component_verdicts[name]} / {component_states.get(name, 'UNKNOWN')}")
    if not component_lines:
        component_lines.append("- none: UNKNOWN / UNKNOWN")

    blocker_lines = [f"- {blocker}" for blocker in report_json.get("blockers", [])] or ["- none"]

    lines = [
        "# AIOS Operator Chain Report",
        "",
        f"- Report verdict: {report_verdict}",
        f"- Report state: {report_state}",
        f"- Chain verdict: {report_json['chain_verdict']}",
        f"- Chain state: {report_json['chain_state']}",
        f"- First blocking component: {report_json['first_blocking_component'] or 'none'}",
        f"- Human approval required: {report_json['human_approval_required']}",
        f"- Explicit human approval present: {report_json['explicit_human_approval_present']}",
        f"- Apply review ready: {report_json['apply_review_ready']}",
        f"- Hard safety all false: {report_json['hard_safety_all_false']}",
        f"- Next safe action: {report_json['next_safe_action']}",
        "",
        "## Components",
        *component_lines,
        "",
        "## Blockers",
        *blocker_lines,
    ]
    return "\n".join(lines) + "\n"


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


def _is_well_formed_chain_result(value: Mapping[str, Any]) -> bool:
    if value.get("schema") != CHAIN_SCHEMA:
        return False
    if any(field not in value for field in REQUIRED_CHAIN_FIELDS):
        return False
    return isinstance(value.get("component_verdicts"), Mapping) and isinstance(value.get("component_states"), Mapping)


def _hard_safety_all_false(value: Mapping[str, Any]) -> bool:
    for field in HARD_SAFETY_FALSE_FIELDS:
        if value.get(field) is not False:
            return False
    safety = value.get("safety")
    if isinstance(safety, Mapping):
        for field in HARD_SAFETY_FALSE_FIELDS:
            if safety.get(field) is not False:
                return False
    return True


def _mapping_of_strings(value: Any) -> dict[str, str]:
    if not isinstance(value, Mapping):
        return {}
    return {str(key): _string(child) for key, child in value.items()}


def _string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "", [], {})]
    return []


def _optional_string(value: Any) -> str | None:
    if value in (None, "", [], {}):
        return None
    return str(value)


def _string(value: Any) -> str:
    if value in (None, [], {}):
        return ""
    return value if isinstance(value, str) else str(value)


def _safety() -> dict[str, Any]:
    safety = {
        "read_only": True,
        "side_effect_free": True,
        "injected_chain_result_only": True,
        "commands_executed": False,
        "files_written": False,
        "mutations_performed": False,
        "self_approval_allowed": False,
    }
    safety.update({field: False for field in HARD_SAFETY_FALSE_FIELDS if field not in safety})
    return safety


def _report_id(chain_result: Mapping[str, Any] | None) -> str:
    encoded = json.dumps(_jsonable(chain_result), sort_keys=True, separators=(",", ":"), default=str)
    return "operator-chain-report-" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()[:16]


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(child) for key, child in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)):
        return [_jsonable(child) for child in value]
    if isinstance(value, set):
        return sorted(_jsonable(child) for child in value)
    return value


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
