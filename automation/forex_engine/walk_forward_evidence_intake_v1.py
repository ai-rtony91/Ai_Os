"""Deterministic walk-forward/OOS evidence intake for AIOS Forex."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from automation.forex_engine.walk_forward_oos_evidence_v1 import (
    PROTECTED_PERMISSION_FLAGS,
    evaluate_walk_forward_oos_evidence,
    result_to_jsonable_dict as walk_forward_result_to_jsonable_dict,
)


WALK_FORWARD_EVIDENCE_INTAKE_VERSION = "walk_forward_evidence_intake_v1"
DEFAULT_REPORT_ROOT = Path("Reports/forex_delivery")
READINESS_JSON = "readiness_state_recalculation_v1_report.json"
WALK_FORWARD_REPORTS = (
    "AIOS_FOREX_WALK_FORWARD_DEPTH_PACKET_R_V1_REPORT.md",
    "AIOS_FOREX_WALK_FORWARD_WINDOW_MATRIX_V1.md",
    "AIOS_FOREX_C1_EUR_BUY_WALK_FORWARD_STABILITY_SCOREBOARD_V1.md",
    "AIOS_FOREX_WALK_FORWARD_FAILURE_ROOT_CAUSE_MATRIX_V1.md",
    "AIOS_FOREX_EXPECTANCY_TICKET_GATE_CLOSURE_V1.md",
    "AIOS_FOREX_LIVE_EXECUTION_TO_80_UPTIME_MASTER_V2.md",
    "AIOS_FOREX_BEFORE_AFTER_WALK_FORWARD_COMPARISON_V1.md",
    "AIOS_FOREX_WALKFORWARD_VALIDATION_HARNESS_V1_REPORT.md",
)
WALK_FORWARD_DISCOVERY_PATTERN = re.compile(
    r"(?i)(walk[- ]forward|out[_ -]of[_ -]sample|out-of-sample|\bOOS\b|"
    r"oos_segments|out_of_sample_folds)"
)


def intake_walk_forward_evidence(report_root: str | Path = DEFAULT_REPORT_ROOT) -> dict[str, Any]:
    """Discover, normalize, and validate walk-forward/OOS evidence."""

    root = Path(report_root)
    sources: list[str] = []
    notes: list[str] = []
    summary: dict[str, Any] = {}

    readiness_path = root / READINESS_JSON
    readiness = _read_json(readiness_path)
    if readiness:
        sources.append(_display_path(readiness_path))
        _merge_if_present(summary, _thresholds_from_readiness_json(readiness))

    for path in _candidate_report_paths(root, WALK_FORWARD_REPORTS, WALK_FORWARD_DISCOVERY_PATTERN):
        sources.append(_display_path(path))
        text = path.read_text(encoding="utf-8")
        _merge_if_present(summary, _summary_from_markdown(text, notes))

    result = walk_forward_result_to_jsonable_dict(evaluate_walk_forward_oos_evidence(summary or None))
    return {
        "intake_version": WALK_FORWARD_EVIDENCE_INTAKE_VERSION,
        "status": result["walk_forward_oos_status"],
        "evidence_found": bool(sources),
        "source_files": _dedupe(sources),
        "normalized_summary": summary,
        "parse_notes": _dedupe(notes),
        "adapter_result": result,
        "blockers": list(result.get("blockers", [])),
        "missing_fields": list(result.get("missing_fields", [])),
        "sanitized": summary.get("sanitized") is True,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
    }


def result_to_jsonable_dict(result: Mapping[str, Any]) -> dict[str, Any]:
    return dict(result)


def result_to_operator_text(result: Mapping[str, Any]) -> str:
    lines = [
        "AIOS Forex Walk Forward Evidence Intake V1",
        f"status: {result.get('status', 'WALK_FORWARD_OOS_INCOMPLETE')}",
        f"evidence_found: {_bool_text(bool(result.get('evidence_found')))}",
        "source_files:",
    ]
    lines.extend(f"- {item}" for item in result.get("source_files", []) or ("none",))
    lines.append("blockers:")
    lines.extend(f"- {item}" for item in result.get("blockers", []) or ("none",))
    lines.append("missing_fields:")
    lines.extend(f"- {item}" for item in result.get("missing_fields", []) or ("none",))
    return "\n".join(lines) + "\n"


def _thresholds_from_readiness_json(data: Mapping[str, Any]) -> dict[str, Any]:
    review_bundles = _review_bundles(data)
    thresholds = _first_mapping(*(bundle.get("thresholds") for bundle in review_bundles))
    freshness = _first_mapping(
        *(_path(bundle, ("candidate", "freshness_proof")) for bundle in review_bundles),
        *(_path(bundle, ("proofs", "freshness", "evidence")) for bundle in review_bundles),
    )
    summary: dict[str, Any] = {}
    max_drawdown = _number(thresholds.get("max_drawdown"))
    if max_drawdown is not None:
        summary["max_allowed_drawdown"] = max_drawdown
    if thresholds.get("require_walk_forward_pass") is True:
        summary["min_pass_rate"] = 1.0
    max_age_hours = _number(thresholds.get("max_freshness_age_hours"))
    if max_age_hours is not None:
        summary["max_evidence_age_days"] = max_age_hours / 24
    age_hours = _number(freshness.get("age_hours"))
    if age_hours is not None:
        summary["evidence_age_days"] = age_hours / 24
    if _safe_bool(_path(data, ("safety", "is_safe"))) is True:
        summary["sanitized"] = True
    return summary


def _review_bundles(data: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        value
        for value in (
            _first_mapping(_path(data, ("bridge_payload", "canonical_review_bundle"))),
            _first_mapping(_path(data, ("journey_payload", "review_bundle"))),
            _first_mapping(_path(data, ("journey_payload", "canonical_review_bundle"))),
        )
        if value
    ]


def _summary_from_markdown(text: str, notes: list[str]) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    fields = _key_values(text)
    for output_key, aliases in {
        "windows_total": ("windows_total", "total_windows", "total windows"),
        "windows_passed": ("windows_passed", "passing_windows", "passing windows"),
        "oos_segments_total": (
            "oos_segments_total",
            "out_of_sample_segments_total",
            "out_of_sample_folds",
            "out of sample folds",
            "out-of-sample folds",
        ),
        "oos_segments_passed": (
            "oos_segments_passed",
            "out_of_sample_segments_passed",
            "out_of_sample_folds_passed",
            "out of sample folds passed",
            "out-of-sample folds passed",
        ),
        "min_pass_rate": ("min_pass_rate", "minimum_pass_rate"),
        "max_drawdown": ("max_drawdown", "controlled_drawdown", "max drawdown"),
        "max_allowed_drawdown": ("max_allowed_drawdown", "maximum_allowed_drawdown"),
        "evidence_age_days": ("evidence_age_days", "evidence age days"),
        "max_evidence_age_days": ("max_evidence_age_days", "max evidence age days"),
    }.items():
        value = _number_first(fields, *aliases)
        if value is not None:
            summary[output_key] = value
    sanitized = _bool_first(fields, "sanitized")
    if sanitized is not None:
        summary["sanitized"] = sanitized
    total = summary.get("windows_total")
    if total is None:
        total = _number_first(fields, "total windows")
    if total is None:
        total = _count_window_rows(text)
    passed = summary.get("windows_passed")
    if passed is None:
        passed = _count_passing_windows(text)
    drawdown = summary.get("max_drawdown")
    if drawdown is None:
        drawdown = _max_table_number(text, ("max_drawdown", "max drawdown"))
    if total is not None:
        summary["windows_total"] = total
    if passed is not None:
        summary["windows_passed"] = passed
    if drawdown is not None:
        summary["max_drawdown"] = drawdown
    oos_counts = _oos_segment_counts_from_markdown(text)
    for key, value in oos_counts.items():
        if key not in summary:
            summary[key] = value
    if "min_pass_rate" not in summary and re.search(r"(?i)only when all evaluated windows pass", text):
        summary["min_pass_rate"] = 1.0
    if re.search(r"(?i)no broker connectivity.*no credentials.*no .*network.*no .*order execution", text):
        summary["sanitized"] = True
    if re.search(r"(?i)walk[- ]forward (?:evidence )?(?:failed|materially failed|gate cleared:\s*`?false)", text):
        notes.append("walk-forward report explicitly records a failed walk-forward gate")
    if "oos_segments_total" not in summary:
        notes.append("no out-of-sample segment counts found in walk-forward reports")
    return summary


def _oos_segment_counts_from_markdown(text: str) -> dict[str, float]:
    """Parse combined OOS count phrases and segment tables."""

    counts = _oos_segment_counts_from_phrases(text)
    table_counts = _oos_segment_counts_from_tables(text)
    for key, value in table_counts.items():
        counts.setdefault(key, value)
    return counts


def _oos_segment_counts_from_phrases(text: str) -> dict[str, float]:
    patterns = (
        re.compile(
            r"(?im)^\s*-?\s*(?:oos|out[-_ ]of[-_ ]sample)\s+"
            r"(?:segments?|folds?|windows?|coverage|pass(?:ing)? segments?)"
            r"(?:\s+(?:passed|passing|summary|count|counts|result|results))?\s*:\s*"
            r"(?P<passed>\d+(?:\.\d+)?)\s*/\s*(?P<total>\d+(?:\.\d+)?)\s*"
            r"(?:passed|pass|ok|ready)?\b"
        ),
        re.compile(
            r"(?im)^\s*-?\s*(?:oos|out[-_ ]of[-_ ]sample)\s+"
            r"(?:segments?|folds?|windows?|coverage|pass(?:ing)? segments?)"
            r"(?:\s+(?:passed|passing|summary|count|counts|result|results))?\s*:\s*"
            r"(?P<passed>\d+(?:\.\d+)?)\s+(?:of|out\s+of)\s+"
            r"(?P<total>\d+(?:\.\d+)?)\s*(?:passed|pass|ok|ready)?\b"
        ),
        re.compile(
            r"(?im)^\s*-?\s*(?:oos|out[-_ ]of[-_ ]sample)\s+"
            r"(?:segments?|folds?|windows?|coverage|pass(?:ing)? segments?)"
            r"(?:\s+(?:passed|passing|summary|count|counts|result|results))?\s*:\s*"
            r"(?P<passed>\d+(?:\.\d+)?)\s*(?:passed|passing|ok|ready)\s+"
            r"(?:of|out\s+of|/)\s*(?P<total>\d+(?:\.\d+)?)\s*"
            r"(?:total|segments?|folds?|windows?)?\b"
        ),
        re.compile(
            r"(?im)^\s*-?\s*(?:oos|out[-_ ]of[-_ ]sample)\s+"
            r"(?:segments?|folds?|windows?|coverage|pass(?:ing)? segments?)"
            r"(?:\s+(?:passed|passing|summary|count|counts|result|results))?\s*:\s*"
            r"(?P<total>\d+(?:\.\d+)?)\s*(?:total|segments?|folds?|windows?)\s*[,;/]\s*"
            r"(?P<passed>\d+(?:\.\d+)?)\s*(?:passed|passing|ok|ready)\b"
        ),
    )
    for pattern in patterns:
        match = pattern.search(text)
        if match:
            return {
                "oos_segments_total": float(match.group("total")),
                "oos_segments_passed": float(match.group("passed")),
            }
    return {}


def _oos_segment_counts_from_tables(text: str) -> dict[str, float]:
    rows = [
        row
        for row in _table_rows(text)
        if row.get("oos_segment_id")
        or row.get("out_of_sample_segment_id")
        or row.get("out_of_sample_fold")
        or row.get("oos_fold")
        or row.get("segment_id")
    ]
    if not rows:
        return {}
    passed = 0
    for row in rows:
        status = str(
            row.get("status")
            or row.get("result")
            or row.get("readiness")
            or row.get("promotion_status")
            or row.get("pass")
            or row.get("passed")
            or ""
        ).lower()
        blockers = str(row.get("blocker_reasons", row.get("blockers", ""))).lower()
        if status in {"pass", "passed", "ready", "ok", "true", "profit_objective_ready"} or blockers == "none":
            passed += 1
    return {
        "oos_segments_total": float(len(rows)),
        "oos_segments_passed": float(passed),
    }


def _key_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    pattern = re.compile(r"(?im)^\s*-?\s*([A-Za-z0-9 _/\-]+):\s*`?([^`\n]+?)`?\s*\.?\s*$")
    for match in pattern.finditer(text):
        values[_key(match.group(1))] = match.group(2).strip()
    return values


def _count_passing_windows(text: str) -> float | None:
    rows = _table_rows(text)
    if not rows:
        return None
    count = 0
    for row in rows:
        status = str(row.get("promotion_status", row.get("readiness", ""))).lower()
        blockers = str(row.get("blocker_reasons", row.get("blockers", ""))).lower()
        if status in {"profit_objective_ready", "pass", "passed", "ready"} or blockers == "none":
            count += 1
    return float(count)


def _count_window_rows(text: str) -> float | None:
    rows = [row for row in _table_rows(text) if row.get("window_id")]
    return float(len(rows)) if rows else None


def _max_table_number(text: str, headers: tuple[str, ...]) -> float | None:
    values: list[float] = []
    for row in _table_rows(text):
        for header in headers:
            value = _number(row.get(_key(header)))
            if value is not None:
                values.append(value)
    return max(values) if values else None


def _table_rows(text: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    rows: list[dict[str, str]] = []
    headers: list[str] = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells:
            continue
        if not headers:
            headers = [_key(cell) for cell in cells]
            continue
        if all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        if len(cells) != len(headers):
            continue
        rows.append(dict(zip(headers, cells)))
    return rows


def _read_json(path: Path) -> Mapping[str, Any]:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, Mapping) else {}


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


def _path(data: Any, keys: tuple[str, ...], default: Any = None) -> Any:
    current = data
    for key in keys:
        if not isinstance(current, Mapping):
            return default
        current = current.get(key)
    return default if current is None else current


def _first_mapping(*values: Any) -> dict[str, Any]:
    for value in values:
        if isinstance(value, Mapping):
            return dict(value)
    return {}


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


def _number(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    text = str(value).strip().strip("`")
    match = re.fullmatch(r"(-?[0-9]+(?:\.[0-9]+)?)[%.,]?", text)
    if match:
        return float(match.group(1))
    try:
        return float(text)
    except (TypeError, ValueError):
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
    "WALK_FORWARD_EVIDENCE_INTAKE_VERSION",
    "intake_walk_forward_evidence",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
