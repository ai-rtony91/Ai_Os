"""Deterministic persistent profitability evidence intake for AIOS Forex."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from automation.forex_engine.persistent_profitability_evidence_v1 import (
    PROTECTED_PERMISSION_FLAGS,
    evaluate_persistent_profitability_evidence,
    result_to_jsonable_dict as profitability_result_to_jsonable_dict,
)


PROFITABILITY_EVIDENCE_INTAKE_VERSION = "profitability_evidence_intake_v1"
DEFAULT_REPORT_ROOT = Path("Reports/forex_delivery")
READINESS_JSON = "readiness_state_recalculation_v1_report.json"
PROFITABILITY_REPORTS = (
    "AIOS_FOREX_PROFITABILITY_VERDICT_V1.md",
    "AIOS_FOREX_PROFIT_PROOF_LEDGER_V1.md",
    "AIOS_FOREX_STRATEGY_PROOF_ENGINE_V1.md",
    "AIOS_FOREX_TOP_10_PROFIT_CANDIDATES_V1.md",
    "AIOS_FOREX_EXPECTANCY_STRENGTH_ROUTER_V1.md",
    "AIOS_FOREX_EVIDENCE_DEPTH_QUALITY_GATE_V1.md",
    "AIOS_FOREX_OANDA_LIVE_MICROTRADE_PROFIT_PROOF_EVIDENCE_DEPTH_COLLECTION_V1.md",
    "AIOS_FOREX_STATISTICAL_PROFIT_PROOF_GATE_V1.md",
    "AIOS_FOREX_REAL_EVIDENCE_DEPTH_ENGINE_V1.md",
    "AIOS_FOREX_C1_EUR_BUY_EVIDENCE_DEPTH_SCOREBOARD_V1.md",
    "AIOS_FOREX_EVIDENCE_DEPTH_EXPANSION_PACKET_Q_V1_REPORT.md",
    "AIOS_FOREX_WALK_FORWARD_DEPTH_PACKET_R_V1_REPORT.md",
    "AIOS_FOREX_WALK_FORWARD_WINDOW_MATRIX_V1.md",
    "AIOS_FOREX_DEMO_READINESS_PROFIT_TRUST_SPINE_V1.md",
)
HIGH_PRECEDENCE_PROFITABILITY_REPORTS = frozenset(
    {
        "AIOS_FOREX_110_PERSISTENT_PROFITABILITY_PERIOD_SOURCE_V1.md",
    }
)
PROFITABILITY_DISCOVERY_PATTERN = re.compile(
    r"(?i)(persistent profitability|profitability|profit proof|profit[_ -]?factor|"
    r"expectancy|net_pnl_after_costs|after[-_ ]cost|consecutive profitable)"
)


def intake_profitability_evidence(report_root: str | Path = DEFAULT_REPORT_ROOT) -> dict[str, Any]:
    """Discover, normalize, and validate persistent profitability evidence."""

    root = Path(report_root)
    sources: list[str] = []
    notes: list[str] = []
    summary: dict[str, Any] = {}

    readiness_path = root / READINESS_JSON
    readiness = _read_json(readiness_path)
    if readiness:
        sources.append(_display_path(readiness_path))
        _merge_if_present(summary, _freshness_from_readiness_json(readiness))

    for path in _candidate_report_paths(root, PROFITABILITY_REPORTS, PROFITABILITY_DISCOVERY_PATTERN):
        sources.append(_display_path(path))
        parsed = _summary_from_markdown(path.read_text(encoding="utf-8"), notes)
        if path.name in HIGH_PRECEDENCE_PROFITABILITY_REPORTS:
            _merge_with_precedence(summary, parsed)
        else:
            _merge_if_present(summary, parsed)

    notes = _active_parse_notes(notes, summary)
    result = profitability_result_to_jsonable_dict(evaluate_persistent_profitability_evidence(summary or None))
    return {
        "intake_version": PROFITABILITY_EVIDENCE_INTAKE_VERSION,
        "status": result["persistent_profitability_status"],
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
        "AIOS Forex Profitability Evidence Intake V1",
        f"status: {result.get('status', 'PERSISTENT_PROFITABILITY_INCOMPLETE')}",
        f"evidence_found: {_bool_text(bool(result.get('evidence_found')))}",
        "source_files:",
    ]
    lines.extend(f"- {item}" for item in result.get("source_files", []) or ("none",))
    lines.append("blockers:")
    lines.extend(f"- {item}" for item in result.get("blockers", []) or ("none",))
    lines.append("missing_fields:")
    lines.extend(f"- {item}" for item in result.get("missing_fields", []) or ("none",))
    return "\n".join(lines) + "\n"


def _freshness_from_readiness_json(data: Mapping[str, Any]) -> dict[str, Any]:
    review_bundles = _review_bundles(data)
    review_bundle = _first_mapping(*review_bundles)
    candidate = _first_mapping(*(bundle.get("candidate") for bundle in review_bundles))
    metrics = _first_mapping(review_bundle.get("metrics"), candidate)
    thresholds = _first_mapping(*(bundle.get("thresholds") for bundle in review_bundles))
    freshness = _first_mapping(
        *(_path(bundle, ("candidate", "freshness_proof")) for bundle in review_bundles),
        *(_path(bundle, ("proofs", "freshness", "evidence")) for bundle in review_bundles),
    )
    summary: dict[str, Any] = {}
    field_map = {
        "closed_trade_count": ("sample_size",),
        "expectancy": ("expectancy",),
        "profit_factor": ("profit_factor",),
        "max_drawdown": ("max_drawdown",),
    }
    for output_key, source_keys in field_map.items():
        value = _number_first(metrics, *source_keys)
        if value is not None:
            summary[output_key] = value
    threshold_map = {
        "min_closed_trade_count": ("min_sample_size",),
        "min_expectancy": ("min_expectancy",),
        "min_profit_factor": ("min_profit_factor",),
        "max_allowed_drawdown": ("max_drawdown",),
    }
    for output_key, source_keys in threshold_map.items():
        value = _number_first(thresholds, *source_keys)
        if value is not None:
            summary[output_key] = value
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
        "closed_trade_count": ("closed_trade_count", "closed trade count", "closed_trades"),
        "min_closed_trade_count": ("min_closed_trade_count", "minimum closed trade count"),
        "expectancy": ("expectancy", "actual expectancy", "best candidate expectancy", "top_expectancy"),
        "min_expectancy": ("min_expectancy", "minimum expectancy"),
        "profit_factor": ("profit_factor", "actual profit factor", "top_profit_factor"),
        "min_profit_factor": ("min_profit_factor", "minimum profit factor"),
        "max_drawdown": ("max_drawdown", "actual drawdown", "max drawdown"),
        "max_allowed_drawdown": ("max_allowed_drawdown", "maximum allowed drawdown"),
        "consecutive_profitable_periods": (
            "consecutive_profitable_periods",
            "consecutive profitable periods",
        ),
        "min_profitable_periods": ("min_profitable_periods", "minimum profitable periods"),
        "evidence_age_days": ("evidence_age_days", "evidence age days"),
        "max_evidence_age_days": ("max_evidence_age_days", "max evidence age days"),
    }.items():
        value = _number_first(fields, *aliases)
        if value is not None:
            summary[output_key] = value
    after_costs = _bool_first(fields, "after_costs", "after costs", "after-costs")
    if after_costs is not None:
        summary["after_costs"] = after_costs
    sanitized = _bool_first(fields, "sanitized")
    if sanitized is not None:
        summary["sanitized"] = sanitized

    closed = _extract_closed_trade_count(text)
    if closed is not None and "closed_trade_count" not in summary:
        summary["closed_trade_count"] = closed
    best_expectancy = _number_first(fields, "best candidate expectancy", "actual expectancy", "top_expectancy")
    if best_expectancy is not None and "expectancy" not in summary:
        summary["expectancy"] = best_expectancy
    profit_factor = _number_first(fields, "actual profit factor", "top_profit_factor")
    if profit_factor is not None and "profit_factor" not in summary:
        summary["profit_factor"] = profit_factor
    drawdown = _number_first(fields, "actual drawdown", "max drawdown", "max_drawdown")
    if drawdown is not None and "max_drawdown" not in summary:
        summary["max_drawdown"] = drawdown
    periods = _profitable_periods_from_window_table(text)
    if periods is not None and "consecutive_profitable_periods" not in summary:
        summary["consecutive_profitable_periods"] = periods
    min_periods = _number_first(
        fields,
        "minimum profitable periods",
        "minimum_walk_forward_folds",
        "minimum walk forward folds",
    )
    if min_periods is not None and "min_profitable_periods" not in summary:
        summary["min_profitable_periods"] = min_periods

    defaults = _proof_gate_defaults(text)
    _merge_if_present(summary, defaults)
    if "after_costs" not in summary and _after_costs(text, fields):
        summary["after_costs"] = True
    periods = _number_first(fields, "consecutive_profitable_periods")
    if periods is not None and "consecutive_profitable_periods" not in summary:
        summary["consecutive_profitable_periods"] = periods
    min_periods = _number_first(fields, "min_profitable_periods")
    if min_periods is not None and "min_profitable_periods" not in summary:
        summary["min_profitable_periods"] = min_periods
    if re.search(r"(?i)does not .*call brokers.*does not use credentials", text):
        summary["sanitized"] = True
    if "consecutive_profitable_periods" not in summary:
        notes.append("no consecutive profitable period count found in profitability reports")
    if "after_costs" not in summary:
        notes.append("no after-cost profitability marker found in profitability reports")
    return summary


def _profitable_periods_from_window_table(text: str) -> float | None:
    rows = _table_rows(text)
    if not rows:
        return None
    best_streak = 0
    current_streak = 0
    saw_period = False
    for row in rows:
        if not row.get("window_id"):
            continue
        saw_period = True
        expectancy = _number(row.get("expectancy"))
        status = str(row.get("promotion_status", "")).lower()
        blockers = str(row.get("blocker_reasons", row.get("blockers", ""))).lower()
        profitable = (
            expectancy is not None
            and expectancy > 0
            and (status in {"profit_objective_ready", "pass", "passed", "ready"} or blockers == "none")
        )
        if profitable:
            current_streak += 1
            best_streak = max(best_streak, current_streak)
        else:
            current_streak = 0
    return float(best_streak) if saw_period else None


def _extract_closed_trade_count(text: str) -> float | None:
    match = re.search(r"(?i)measurable paper edge exists on\s+([0-9]+)\s+closed trades", text)
    if match:
        return float(match.group(1))
    match = re.search(r"(?i)minimum total trades default:\s*([0-9]+)", text)
    if match and re.search(r"(?i)real candidate profitability proof: not yet established", text):
        return 0.0
    rows = _table_rows(text)
    if rows:
        best = rows[0]
        value = _number(best.get("sample_size") or best.get("sample") or best.get("closed_trades"))
        if value is not None:
            return value
    return None


def _proof_gate_defaults(text: str) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    patterns = {
        "min_profit_factor": r"(?i)minimum profit factor default:\s*(`?-?[0-9][^\s]*)",
        "min_closed_trade_count": r"(?i)minimum total trades default:\s*(`?-?[0-9][^\s]*)",
        "max_allowed_drawdown": r"(?i)maximum drawdown default:\s*(`?-?[0-9][^\s]*)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text)
        if match:
            value = _normalized_numeric_token(match.group(1))
            if value is not None:
                summary[key] = value
    if re.search(r"(?i)positive expectancy required", text):
        summary["min_expectancy"] = 0.0
    match = re.search(r"`<\s*([0-9]+)`\s+closed trades", text)
    if match and "min_closed_trade_count" not in summary:
        summary["min_closed_trade_count"] = float(match.group(1))
    return summary


def _normalized_numeric_token(value: Any) -> float | None:
    text = str(value).strip()
    match = re.fullmatch(r"(?:`(-?[0-9]+(?:\.[0-9]+)?)`|(-?[0-9]+(?:\.[0-9]+)?)[%.,]?)", text)
    if not match:
        return None
    return float(match.group(1) or match.group(2))


def _after_costs(text: str, fields: Mapping[str, str]) -> bool:
    total_pnl = _number_first(
        fields,
        "source total net pnl after costs",
        "total net pnl after costs",
        "complete sample total net pnl after costs",
    )
    return bool(
        re.search(r"(?i)after[- ]cost(?:s)?\s*:\s*(?:true|yes|pass|passed)", text)
        or re.search(r"(?i)profitability is after[- ]cost", text)
        or re.search(r"(?i)\bnet_pnl_after_costs\b", text)
        or re.search(r"(?i)\bpositive_total_net_pnl_after_costs\b", text)
        or (total_pnl is not None and total_pnl > 0)
    )


def _key_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    pattern = re.compile(r"(?im)^\s*-?\s*([A-Za-z0-9 _/\-]+):\s*`?([^`\n]+?)`?\s*\.?\s*$")
    for match in pattern.finditer(text):
        values[_key(match.group(1))] = match.group(2).strip()
    return values


def _table_rows(text: str) -> list[dict[str, str]]:
    lines = [line.strip() for line in text.splitlines() if line.strip().startswith("|")]
    rows: list[dict[str, str]] = []
    headers: list[str] = []
    for line in lines:
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not headers:
            headers = [_key(cell) for cell in cells]
            continue
        if all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        if len(cells) == len(headers):
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


def _active_parse_notes(notes: list[str], summary: Mapping[str, Any]) -> list[str]:
    filtered: list[str] = []
    for note in notes:
        if "consecutive profitable period" in note and "consecutive_profitable_periods" in summary:
            continue
        if "after-cost profitability marker" in note and "after_costs" in summary:
            continue
        filtered.append(note)
    return filtered


def _merge_if_present(target: dict[str, Any], incoming: Mapping[str, Any]) -> None:
    for key, value in incoming.items():
        if key not in target and value is not None:
            target[key] = value


def _merge_with_precedence(target: dict[str, Any], incoming: Mapping[str, Any]) -> None:
    for key, value in incoming.items():
        if value is not None:
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
    match = re.search(r"-?[0-9]+(?:\.[0-9]+)?", text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except ValueError:
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
    "PROFITABILITY_EVIDENCE_INTAKE_VERSION",
    "intake_profitability_evidence",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
