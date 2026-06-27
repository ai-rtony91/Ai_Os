"""Deterministic 22H/6D observation evidence intake for AIOS Forex."""

from __future__ import annotations

import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Mapping


OBSERVATION_EVIDENCE_INTAKE_VERSION = "observation_evidence_intake_v1"
SUPERVISED_OBSERVATION_READY = "SUPERVISED_OBSERVATION_READY"
SUPERVISED_OBSERVATION_BLOCKED = "SUPERVISED_OBSERVATION_BLOCKED"
SUPERVISED_OBSERVATION_INCOMPLETE = "SUPERVISED_OBSERVATION_INCOMPLETE"
DEFAULT_REPORT_ROOT = Path("Reports/forex_delivery")
PROTECTED_PERMISSION_FLAGS = {
    "broker_execution_allowed": False,
    "live_trading_allowed": False,
    "order_submission_allowed": False,
    "credential_access_allowed": False,
    "account_access_allowed": False,
    "dashboard_execution_authority": False,
    "owner_approval_created": False,
}
REQUIRED_OBSERVATION_FIELDS = (
    "observed_hours",
    "required_hours",
    "observed_sessions",
    "required_sessions",
    "observed_days",
    "required_days",
    "interruption_count",
    "max_interruption_count",
    "manual_override_count",
    "max_manual_override_count",
    "sanitized",
    "evidence_age_days",
    "max_evidence_age_days",
)
SECRET_OR_ACCOUNT_FIELD_FRAGMENTS = (
    "api_key",
    "access_token",
    "refresh_token",
    "authorization",
    "bearer",
    "password",
    "secret",
    "credential",
    "account_id",
    "accountid",
    "account_number",
    "account_reference",
    "broker_order_id",
    "raw_order_id",
    "raw_transaction_id",
    "raw_payload",
    "order_payload",
)
UNSAFE_TRUE_FIELDS = (
    "broker_execution_allowed",
    "live_trading_allowed",
    "order_submission_allowed",
    "credential_access_allowed",
    "account_access_allowed",
    "dashboard_execution_authority",
    "owner_approval_created",
    "execution_allowed",
    "trade_allowed",
    "broker_access_allowed",
    "money_movement_allowed",
    "vacation_mode_execution_allowed",
)
OBSERVATION_REPORTS = (
    "AIOS_FOREX_TRUSTED_PROFIT_22_6_READINESS_V1.md",
    "AIOS_FOREX_TRUSTED_PROFIT_22_6_EPIC_REPORT_V1.md",
    "AIOS_FOREX_EPC004_22H6D_AUGMENTATION_V1_REPORT.md",
    "AIOS_FOREX_UPTIME_RANGE_PLANNER_80_22_5_22_6_V1.md",
    "AIOS_FOREX_DEMO_READINESS_SPINE_V1_REPORT.md",
    "AIOS_FOREX_REMAINING_WORK_INVENTORY_V1_REPORT.md",
    "AIOS_FOREX_REAL_EVIDENCE_DEPTH_ENGINE_V1.md",
    "AIOS_FOREX_FINAL_GAP_ANALYSIS_V1_REPORT.md",
)
OBSERVATION_DISCOVERY_PATTERN = re.compile(
    r"(?i)(22H|22/6|22\s*hours|6\s*days|supervised observation|"
    r"observed_hours|observed sessions|observed days|interruption_count|"
    r"max_interruption_count|manual_override_count|max_manual_override_count|"
    r"evidence_age_days|max_evidence_age_days)"
)
OBSERVATION_FIELD_ALIASES = {
    "observed_hours": ("observed_hours", "observed hours", "observed hour count"),
    "required_hours": ("required_hours", "required hours", "required hour count"),
    "observed_sessions": (
        "observed_sessions",
        "observed sessions",
        "observed session count",
    ),
    "required_sessions": (
        "required_sessions",
        "required sessions",
        "required session count",
    ),
    "observed_days": ("observed_days", "observed days", "observed day count"),
    "required_days": ("required_days", "required days", "required day count"),
    "interruption_count": ("interruption_count", "interruption count", "interruptions"),
    "max_interruption_count": (
        "max_interruption_count",
        "max interruption count",
        "maximum interruption count",
        "interruption limit",
    ),
    "manual_override_count": (
        "manual_override_count",
        "manual override count",
        "manual overrides",
    ),
    "max_manual_override_count": (
        "max_manual_override_count",
        "max manual override count",
        "maximum manual override count",
        "manual override limit",
    ),
    "evidence_age_days": (
        "evidence_age_days",
        "evidence age days",
        "freshness age days",
    ),
    "max_evidence_age_days": (
        "max_evidence_age_days",
        "max evidence age days",
        "maximum evidence age days",
        "freshness limit days",
    ),
}
OBSERVATION_TARGET_FIELDS = (
    "observed_hours",
    "observed_sessions",
    "observed_days",
    "interruption_count",
    "max_interruption_count",
    "manual_override_count",
    "max_manual_override_count",
    "evidence_age_days",
    "max_evidence_age_days",
)


def intake_observation_evidence(report_root: str | Path = DEFAULT_REPORT_ROOT) -> dict[str, Any]:
    """Discover, normalize, and validate 22H/6D supervised observation evidence."""

    root = Path(report_root)
    sources: list[str] = []
    notes: list[str] = []
    summary: dict[str, Any] = {}
    field_sources: dict[str, str] = {}
    for path in _candidate_report_paths(root, OBSERVATION_REPORTS, OBSERVATION_DISCOVERY_PATTERN):
        display_path = _display_path(path)
        sources.append(display_path)
        parsed = _summary_from_markdown(path.read_text(encoding="utf-8"), notes)
        for key, value in parsed.items():
            if key not in field_sources and value is not None:
                field_sources[key] = display_path
        _merge_if_present(summary, parsed)

    result = result_to_jsonable_dict(
        evaluate_supervised_observation_22h6d_evidence(summary or None)
    )
    return {
        "intake_version": OBSERVATION_EVIDENCE_INTAKE_VERSION,
        "status": result["observation_status"],
        "evidence_found": bool(sources),
        "source_files": _dedupe(sources),
        "normalized_summary": summary,
        "field_sources": field_sources,
        "parse_notes": _dedupe(notes),
        "adapter_result": result,
        "blockers": list(result.get("blockers", [])),
        "missing_fields": list(result.get("missing_fields", [])),
        "owner_collection_requirements": _owner_collection_requirements(summary),
        "sanitized": summary.get("sanitized") is True,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return dict(result)


def evaluate_supervised_observation_22h6d_evidence(
    observation_summary: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Evaluate sanitized 22H/6D observation evidence for review only."""

    if observation_summary is None:
        return _observation_result(
            status=SUPERVISED_OBSERVATION_INCOMPLETE,
            blockers=["22H/6D observation summary is required"],
            missing_fields=list(REQUIRED_OBSERVATION_FIELDS),
            metrics={},
            next_safe_action="Provide sanitized 22H/6D supervised observation evidence.",
        )
    if not isinstance(observation_summary, Mapping):
        return _observation_result(
            status=SUPERVISED_OBSERVATION_INCOMPLETE,
            blockers=["22H/6D observation summary must be a dictionary"],
            missing_fields=list(REQUIRED_OBSERVATION_FIELDS),
            metrics={},
            next_safe_action="Provide 22H/6D observation evidence as a dictionary.",
        )

    summary = dict(observation_summary)
    safety_blockers = _unsafe_fragments(summary, "observation_summary")
    missing_fields = _missing_fields(summary, REQUIRED_OBSERVATION_FIELDS)
    if missing_fields:
        return _observation_result(
            status=SUPERVISED_OBSERVATION_INCOMPLETE,
            blockers=safety_blockers + [f"missing field: {name}" for name in missing_fields],
            missing_fields=missing_fields,
            metrics={},
            next_safe_action="Provide all required 22H/6D observation fields and rerun locally.",
        )

    numeric_names = (
        "observed_hours",
        "required_hours",
        "observed_sessions",
        "required_sessions",
        "observed_days",
        "required_days",
        "interruption_count",
        "max_interruption_count",
        "manual_override_count",
        "max_manual_override_count",
        "evidence_age_days",
        "max_evidence_age_days",
    )
    numeric = {name: _decimal(summary.get(name)) for name in numeric_names}
    numeric_errors = [name for name, value in numeric.items() if value is None]
    if numeric_errors:
        return _observation_result(
            status=SUPERVISED_OBSERVATION_INCOMPLETE,
            blockers=safety_blockers + [f"field must be numeric: {name}" for name in numeric_errors],
            missing_fields=[],
            metrics={},
            next_safe_action="Repair numeric 22H/6D observation fields and rerun locally.",
        )

    observed_hours = numeric["observed_hours"] or Decimal("0")
    required_hours = numeric["required_hours"] or Decimal("0")
    observed_sessions = numeric["observed_sessions"] or Decimal("0")
    required_sessions = numeric["required_sessions"] or Decimal("0")
    observed_days = numeric["observed_days"] or Decimal("0")
    required_days = numeric["required_days"] or Decimal("0")
    interruption_count = numeric["interruption_count"] or Decimal("0")
    max_interruption_count = numeric["max_interruption_count"] or Decimal("0")
    manual_override_count = numeric["manual_override_count"] or Decimal("0")
    max_manual_override_count = numeric["max_manual_override_count"] or Decimal("0")
    evidence_age = numeric["evidence_age_days"] or Decimal("0")
    max_age = numeric["max_evidence_age_days"] or Decimal("0")

    blockers = list(safety_blockers)
    if required_hours <= 0:
        blockers.append("required_hours must be positive")
    if required_sessions <= 0:
        blockers.append("required_sessions must be positive")
    if required_days <= 0:
        blockers.append("required_days must be positive")
    if observed_hours < required_hours:
        blockers.append("observed_hours is below required_hours")
    if observed_sessions < required_sessions:
        blockers.append("observed_sessions is below required_sessions")
    if observed_days < required_days:
        blockers.append("observed_days is below required_days")
    if interruption_count < 0 or max_interruption_count < 0:
        blockers.append("interruption count fields cannot be negative")
    if interruption_count > max_interruption_count:
        blockers.append("interruption_count exceeds max_interruption_count")
    if manual_override_count < 0 or max_manual_override_count < 0:
        blockers.append("manual override count fields cannot be negative")
    if manual_override_count > max_manual_override_count:
        blockers.append("manual_override_count exceeds max_manual_override_count")
    if summary.get("sanitized") is not True:
        blockers.append("22H/6D observation summary is not marked sanitized")
    if evidence_age < 0 or max_age < 0:
        blockers.append("evidence age fields cannot be negative")
    if max_age >= 0 and evidence_age > max_age:
        blockers.append("22H/6D observation evidence is stale")

    metrics = {
        "observed_hours": _float(observed_hours),
        "required_hours": _float(required_hours),
        "observed_sessions": int(observed_sessions),
        "required_sessions": int(required_sessions),
        "observed_days": int(observed_days),
        "required_days": int(required_days),
        "interruption_count": int(interruption_count),
        "max_interruption_count": int(max_interruption_count),
        "manual_override_count": int(manual_override_count),
        "max_manual_override_count": int(max_manual_override_count),
        "freshness": {
            "evidence_age_days": _float(evidence_age),
            "max_evidence_age_days": _float(max_age),
            "fresh": max_age >= 0 and evidence_age <= max_age,
        },
    }
    status = SUPERVISED_OBSERVATION_BLOCKED if blockers else SUPERVISED_OBSERVATION_READY
    next_safe_action = (
        "Continue to final evidence closure; observation evidence creates no trading approval."
        if status == SUPERVISED_OBSERVATION_READY
        else "Repair 22H/6D observation blockers before relying on this evidence."
    )
    return _observation_result(
        status=status,
        blockers=_dedupe(blockers),
        missing_fields=[],
        metrics=metrics,
        next_safe_action=next_safe_action,
    )


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    lines = [
        "AIOS Forex Observation Evidence Intake V1",
        f"status: {result.get('status', 'SUPERVISED_OBSERVATION_INCOMPLETE')}",
        f"evidence_found: {_bool_text(bool(result.get('evidence_found')))}",
        "source_files:",
    ]
    lines.extend(f"- {item}" for item in result.get("source_files", []) or ("none",))
    lines.append("blockers:")
    lines.extend(f"- {item}" for item in result.get("blockers", []) or ("none",))
    lines.append("missing_fields:")
    lines.extend(f"- {item}" for item in result.get("missing_fields", []) or ("none",))
    return "\n".join(lines) + "\n"


def _summary_from_markdown(text: str, notes: list[str]) -> dict[str, Any]:
    fields = _field_values(text)
    summary: dict[str, Any] = {}
    for output_key, aliases in OBSERVATION_FIELD_ALIASES.items():
        value = _number_first(fields, *aliases)
        if value is not None:
            summary[output_key] = value
    sanitized = _bool_first(fields, "sanitized")
    if sanitized is not None:
        summary["sanitized"] = sanitized

    if "required_hours" not in summary and re.search(r"(?i)22\s*hours", text):
        summary["required_hours"] = 22
    if "required_days" not in summary and re.search(r"(?i)6\s*days", text):
        summary["required_days"] = 6
    if "required_sessions" not in summary and re.search(r"(?i)multi-session|6\s*days", text):
        summary["required_sessions"] = 6
    if re.search(r"(?i)not a trade approval|not approved to trade|broker_action_allowed:\s*false", text):
        summary["sanitized"] = True
    if re.search(r"(?i)minimum 22/6 observation window", text):
        notes.append("report explicitly lists minimum 22/6 observation window as missing")
    for field_name in OBSERVATION_TARGET_FIELDS:
        if field_name not in summary:
            notes.append(f"no {field_name} value found in observation reports")
    return summary


def _field_values(text: str) -> dict[str, str]:
    searchable = _strip_fenced_code(text)
    values = _key_values(searchable)
    for key, value in _assignment_values(searchable).items():
        values.setdefault(key, value)
    for key, value in _markdown_table_values(searchable).items():
        values.setdefault(key, value)
    return values


def _key_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    pattern = re.compile(
        r"(?im)^\s*[-*]?\s*[`\"']?\*{0,2}\s*([A-Za-z0-9 _/\-]+?)\s*\*{0,2}[`\"']?"
        r"\s*:\s*`?\"?([^`\"\n,|]+?)\"?`?\s*,?\.?\s*$"
    )
    for match in pattern.finditer(text):
        values[_key(match.group(1))] = match.group(2).strip()
    return values


def _assignment_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    pattern = re.compile(
        r"(?im)^\s*[-*]?\s*[`\"']?\*{0,2}\s*([A-Za-z0-9 _/\-]+?)\s*\*{0,2}[`\"']?"
        r"\s*=\s*`?\"?([^`\"\n,|]+?)\"?`?\s*,?\.?\s*$"
    )
    for match in pattern.finditer(text):
        canonical = _canonical_observation_field(match.group(1))
        if canonical is not None:
            values[_key(canonical)] = match.group(2).strip()
    return values


def _markdown_table_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    lines = text.splitlines()
    index = 0
    while index < len(lines) - 1:
        header = _table_cells(lines[index])
        separator = _table_cells(lines[index + 1])
        if not header or not _is_table_separator(separator):
            index += 1
            continue

        key_index = _table_header_index(header, ("field", "metric", "name", "key", "measure"))
        value_index = _table_header_index(
            header,
            ("value", "actual", "observed", "current", "count", "days", "hours"),
            start=1,
        )
        if key_index is None:
            key_index = 0
        if value_index is None:
            value_index = 1 if len(header) > 1 else None
        if value_index is None:
            index += 2
            continue

        row_index = index + 2
        while row_index < len(lines):
            cells = _table_cells(lines[row_index])
            if not cells:
                break
            if _is_table_separator(cells):
                row_index += 1
                continue
            if max(key_index, value_index) < len(cells):
                canonical = _canonical_observation_field(cells[key_index])
                if canonical is not None:
                    values[_key(canonical)] = cells[value_index].strip()
            row_index += 1
        index = row_index
    return values


def _strip_fenced_code(text: str) -> str:
    without_backticks = re.sub(r"(?ms)^```.*?^```", "", text)
    return re.sub(r"(?ms)^~~~.*?^~~~", "", without_backticks)


def _table_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [_strip_markdown_cell(cell) for cell in stripped.strip("|").split("|")]


def _strip_markdown_cell(value: str) -> str:
    return value.strip().strip("`").strip("*").strip()


def _is_table_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def _table_header_index(headers: list[str], aliases: tuple[str, ...], start: int = 0) -> int | None:
    normalized_aliases = {_key(alias) for alias in aliases}
    for index, header in enumerate(headers[start:], start=start):
        if _key(header) in normalized_aliases:
            return index
    return None


def _canonical_observation_field(label: str) -> str | None:
    normalized = _key(label)
    for canonical, aliases in OBSERVATION_FIELD_ALIASES.items():
        if normalized in {_key(alias) for alias in aliases}:
            return canonical
    return None


def _number_first(values: Mapping[str, str], *keys: str) -> float | None:
    for key in keys:
        value = _number(values.get(_key(key)))
        if value is not None:
            return value
    return None


def _bool_first(values: Mapping[str, str], *keys: str) -> bool | None:
    for key in keys:
        value = _safe_bool(values.get(_key(key)))
        if value is not None:
            return value
    return None


def _safe_bool(value: Any) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in {"true", "1", "yes", "pass", "passed", "ready", "ok"}:
            return True
        if lowered in {"false", "0", "no", "fail", "failed", "blocked"}:
            return False
    return None


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    match = re.search(r"-?[0-9]+(?:\.[0-9]+)?", str(value))
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
        return None


def _candidate_report_paths(
    root: Path,
    preferred_names: tuple[str, ...],
    discovery_pattern: re.Pattern[str],
) -> list[Path]:
    paths: list[Path] = []
    seen: set[Path] = set()

    def add(path: Path) -> None:
        resolved = path.resolve()
        if resolved not in seen and path.exists() and path.is_file():
            seen.add(resolved)
            paths.append(path)

    for name in preferred_names:
        add(root / name)
    if not root.exists():
        return paths
    for path in sorted(root.glob("*.md")):
        if path.resolve() in seen:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if discovery_pattern.search(path.name) or discovery_pattern.search(text):
            add(path)
    return paths


def _merge_if_present(target: dict[str, Any], incoming: Mapping[str, Any]) -> None:
    for key, value in incoming.items():
        if key not in target and value is not None:
            target[key] = value


def _owner_collection_requirements(summary: Mapping[str, Any]) -> list[str]:
    missing = [field for field in OBSERVATION_TARGET_FIELDS if field not in summary]
    requirements = [f"Collect repository-backed value for {field}." for field in missing]
    if "sanitized" not in summary:
        requirements.append("Mark the observation evidence sanitized without secrets or account identifiers.")
    return requirements


def _observation_result(
    *,
    status: str,
    blockers: list[str],
    missing_fields: list[str],
    metrics: Mapping[str, Any],
    next_safe_action: str,
) -> dict[str, Any]:
    return {
        "engine_version": OBSERVATION_EVIDENCE_INTAKE_VERSION,
        "status": status,
        "observation_status": status,
        "metrics": dict(metrics),
        "blockers": list(blockers),
        "missing_fields": list(missing_fields),
        "next_safe_action": next_safe_action,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def _missing_fields(payload: Mapping[str, Any], required: tuple[str, ...]) -> list[str]:
    return [name for name in required if name not in payload]


def _unsafe_fragments(value: Any, prefix: str) -> list[str]:
    fragments: list[str] = []
    _scan_payload(value, prefix, fragments)
    return fragments


def _scan_payload(value: Any, path: str, fragments: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            lowered = key_text.lower()
            if lowered in UNSAFE_TRUE_FIELDS:
                if _truthy(item):
                    fragments.append(f"{path}.{key_text} is unsafe true")
                continue
            if any(fragment in lowered for fragment in SECRET_OR_ACCOUNT_FIELD_FRAGMENTS):
                fragments.append(f"{path}.{key_text} contains secret-like or account-like data")
            _scan_payload(item, f"{path}.{key_text}", fragments)
    elif isinstance(value, (list, tuple, set)):
        for index, item in enumerate(value):
            _scan_payload(item, f"{path}[{index}]", fragments)
    elif isinstance(value, str):
        lowered = value.lower()
        if any(fragment in lowered for fragment in SECRET_OR_ACCOUNT_FIELD_FRAGMENTS):
            fragments.append(f"{path} contains secret-like or account-like text")


def _decimal(value: Any) -> Decimal | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return Decimal(str(value).strip())
    except (InvalidOperation, ValueError, AttributeError):
        return None


def _truthy(value: Any) -> bool:
    if value is True:
        return True
    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "yes", "y"}
    return False


def _float(value: Decimal) -> float:
    return float(value.quantize(Decimal("0.000001")))


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", value.strip().lower()).strip("_")


def _display_path(path: Path) -> str:
    return path.as_posix()


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def _bool_text(value: bool) -> str:
    return "true" if value else "false"


__all__ = [
    "OBSERVATION_EVIDENCE_INTAKE_VERSION",
    "SUPERVISED_OBSERVATION_BLOCKED",
    "SUPERVISED_OBSERVATION_INCOMPLETE",
    "SUPERVISED_OBSERVATION_READY",
    "evaluate_supervised_observation_22h6d_evidence",
    "intake_observation_evidence",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
