from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from automation.orchestration.dashboard.aios_dashboard_state_projector import project_dashboard_state


CONTRACT_SCHEMA = "AIOS_DASHBOARD_STATE_CONTRACT.v1"

SECTION_NAMES = (
    "system_state",
    "security_state",
    "continuation_state",
    "governor_state",
    "watchtower_state",
    "validator_state",
    "control_plane_state",
    "active_mission_state",
    "resume_state",
    "worker_state",
)

SUMMARY_SECTION_NAMES = (
    "security_state",
    "continuation_state",
    "watchtower_state",
    "control_plane_state",
)

FAIL_CLOSED_MARKERS = (
    "NEEDS_REVIEW",
    "STALE",
    "UNSUPPORTED",
    "MISSING",
    "UNKNOWN",
    "BLOCKED",
    "STOP",
    "SOS",
)


def render_dashboard_state_report(
    projected_state: Mapping[str, Any] | None = None,
    evidence: Mapping[str, Any] | None = None,
    now_utc: str | None = None,
) -> str:
    """Return a deterministic Markdown report for a display-only dashboard state."""

    state = _resolve_state(projected_state=projected_state, evidence=evidence, now_utc=now_utc)
    lines = [
        "# AIOS Dashboard State Report",
        "",
        "## Contract",
        f"- schema: `{_field(state, 'schema')}`",
        f"- schema_version: `{_field(state, 'schema_version')}`",
        f"- generated_at_utc: `{_field(state, 'generated_at_utc')}`",
        f"- mode: `{_field(state, 'mode')}`",
        "",
        "## System",
        f"- system_health: `{_field(state, 'system_health')}`",
        f"- system_readiness: `{_field(state, 'system_readiness')}`",
        f"- risk_level: `{_field(state, 'risk_level')}`",
        f"- blocked_actions: {_format_list(state.get('blocked_actions'))}",
        f"- next_safe_action: {_text(state.get('next_safe_action'))}",
        f"- source_count: `{_source_count(state.get('source_index'))}`",
        "",
        "## Required Summaries",
    ]

    for section_name in SUMMARY_SECTION_NAMES:
        lines.append(_summary_line(section_name, state.get(section_name)))

    lines.extend(["", "## Fail-Closed Findings"])
    findings = _fail_closed_findings(state)
    if findings:
        lines.extend(findings)
    else:
        lines.append("- none")

    return "\n".join(lines) + "\n"


def _resolve_state(
    *,
    projected_state: Mapping[str, Any] | None,
    evidence: Mapping[str, Any] | None,
    now_utc: str | None,
) -> Mapping[str, Any]:
    if isinstance(projected_state, Mapping) and projected_state.get("schema") == CONTRACT_SCHEMA:
        return projected_state
    if evidence is not None:
        return project_dashboard_state(evidence, now_utc=now_utc)
    return project_dashboard_state({}, now_utc=now_utc)


def _summary_line(section_name: str, section_value: Any) -> str:
    section = section_value if isinstance(section_value, Mapping) else {}
    display_state = _field(section, "display_state")
    evidence_state = _evidence_state(section)
    summary = _text(section.get("summary"))
    next_safe_action = _text(section.get("next_safe_action"))
    blocked_actions = _format_list(section.get("blocked_actions"))
    return (
        f"- {section_name}: display_state=`{display_state}`; "
        f"evidence_state=`{evidence_state}`; summary={summary}; "
        f"blocked_actions={blocked_actions}; next_safe_action={next_safe_action}"
    )


def _fail_closed_findings(state: Mapping[str, Any]) -> list[str]:
    findings: list[str] = []

    for field_name in ("system_health", "system_readiness", "risk_level"):
        value = _field(state, field_name)
        if value in FAIL_CLOSED_MARKERS:
            findings.append(f"- {field_name}: `{value}`")

    for section_name in SECTION_NAMES:
        section_value = state.get(section_name)
        section = section_value if isinstance(section_value, Mapping) else {}
        markers = _section_markers(section)
        if not markers:
            continue
        findings.append(
            f"- {section_name}: {_format_list(markers)}; "
            f"display_state=`{_field(section, 'display_state')}`; "
            f"evidence_state=`{_evidence_state(section)}`; "
            f"blocked_actions={_format_list(section.get('blocked_actions'))}; "
            f"next_safe_action={_text(section.get('next_safe_action'))}"
        )

    blocked_actions = _as_text_list(state.get("blocked_actions"))
    if blocked_actions:
        findings.append(f"- blocked_actions: {_format_list(blocked_actions)}")

    return findings


def _section_markers(section: Mapping[str, Any]) -> list[str]:
    values = [
        _field(section, "display_state"),
        _field(section, "authority_state"),
        _field(section, "evidence_state"),
        _evidence_state(section),
    ]
    return [value for value in FAIL_CLOSED_MARKERS if value in values]


def _evidence_state(section: Mapping[str, Any]) -> str:
    freshness = section.get("freshness")
    if isinstance(freshness, Mapping):
        value = freshness.get("evidence_state")
        if value is not None:
            return str(value)
    value = section.get("evidence_state")
    if value is not None:
        return str(value)
    return "UNKNOWN"


def _source_count(source_index: Any) -> int:
    if not isinstance(source_index, Mapping):
        return 0
    total = 0
    for key in ("primary_sources", "backing_schemas"):
        value = source_index.get(key)
        if isinstance(value, list):
            total += len(value)
    return total


def _field(mapping: Mapping[str, Any], name: str) -> str:
    value = mapping.get(name)
    if value is None:
        return "UNKNOWN"
    return str(value)


def _text(value: Any) -> str:
    if value is None:
        return "`UNKNOWN`"
    text = str(value).strip()
    if not text:
        return "`UNKNOWN`"
    return text


def _format_list(value: Any) -> str:
    items = _as_text_list(value)
    if not items:
        return "`none`"
    return ", ".join(f"`{item}`" for item in items)


def _as_text_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if str(item).strip()]


__all__ = ["render_dashboard_state_report"]
