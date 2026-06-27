"""Deterministic replay evidence intake for AIOS Forex.

This module reads local repository evidence only and normalizes it for
``replay_proof_evidence_v1``. It does not call brokers, read credentials,
read environment variables, submit orders, mutate runtime state, or create
approval authority.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Mapping

from automation.forex_engine.replay_proof_evidence_v1 import (
    PROTECTED_PERMISSION_FLAGS,
    evaluate_replay_proof_evidence,
    result_to_jsonable_dict as replay_result_to_jsonable_dict,
)


REPLAY_EVIDENCE_INTAKE_VERSION = "replay_evidence_intake_v1"
DEFAULT_REPORT_ROOT = Path("Reports/forex_delivery")
READINESS_JSON = "readiness_state_recalculation_v1_report.json"
REPLAY_REPORTS = (
    "AIOS_FOREX_REPLAY_RECONCILIATION_PROOF_BUNDLE_V1_REPORT.md",
    "AIOS_FOREX_PROOF_BUNDLE_TO_CANDIDATE_BRIDGE_V1_REPORT.md",
    "AIOS_FOREX_SESSION_REPLAY_V1_REPORT.md",
    "AIOS_FOREX_SESSION_REPLAY_TEST_REGRESSION_FIX_V1_REPORT.md",
)
REPLAY_JSON_REPORTS = (
    "proof_bundle_to_candidate_bridge_report.json",
    "review_chain_end_to_end_candidate_journey.json",
)
REPLAY_MARKDOWN_DISCOVERY_PATTERN = re.compile(
    r"(?i)(replay proof|session replay|deterministic_replay|reconciliation proof|rollback proof)"
)
REPLAY_JSON_DISCOVERY_PATTERN = re.compile(r"(?i)(proof_bundle|review_chain|candidate_journey)")


def intake_replay_evidence(report_root: str | Path = DEFAULT_REPORT_ROOT) -> dict[str, Any]:
    """Discover, normalize, and validate replay proof evidence."""

    root = Path(report_root)
    sources: list[str] = []
    notes: list[str] = []
    summary: dict[str, Any] = {}

    readiness_path = root / READINESS_JSON
    readiness = _read_json(readiness_path)
    if readiness:
        sources.append(_display_path(readiness_path))
        _merge_if_present(summary, _summary_from_readiness_json(readiness, notes))

    for path in _candidate_report_paths(root, REPLAY_JSON_REPORTS, REPLAY_JSON_DISCOVERY_PATTERN, "*.json"):
        data = _read_json(path)
        if not data:
            continue
        sources.append(_display_path(path))
        _merge_if_present(summary, _summary_from_proof_bundle_json(data, notes, path.name))

    for path in _candidate_report_paths(root, REPLAY_REPORTS, REPLAY_MARKDOWN_DISCOVERY_PATTERN, "*.md"):
        sources.append(_display_path(path))
        _merge_if_present(summary, _summary_from_replay_markdown(path.read_text(encoding="utf-8"), notes))

    result = replay_result_to_jsonable_dict(evaluate_replay_proof_evidence(summary or None))
    return {
        "intake_version": REPLAY_EVIDENCE_INTAKE_VERSION,
        "status": result["replay_proof_status"],
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
    status = str(result.get("status", "REPLAY_PROOF_INCOMPLETE"))
    lines = [
        "AIOS Forex Replay Evidence Intake V1",
        f"status: {status}",
        f"evidence_found: {_bool_text(bool(result.get('evidence_found')))}",
        "source_files:",
    ]
    lines.extend(f"- {item}" for item in result.get("source_files", []) or ("none",))
    lines.append("blockers:")
    lines.extend(f"- {item}" for item in result.get("blockers", []) or ("none",))
    lines.append("missing_fields:")
    lines.extend(f"- {item}" for item in result.get("missing_fields", []) or ("none",))
    return "\n".join(lines) + "\n"


def _summary_from_readiness_json(data: Mapping[str, Any], notes: list[str]) -> dict[str, Any]:
    review_bundles = _review_bundles(data)
    review_bundle = _first_mapping(*review_bundles)
    candidate = _first_mapping(*(bundle.get("candidate") for bundle in review_bundles))
    proofs = _first_mapping(review_bundle.get("proofs"), {})
    proof_statuses = [
        _proof_status(proofs.get("replay")),
        _proof_status(proofs.get("reconciliation")),
        _proof_status(proofs.get("rollback")),
        _proof_status(proofs.get("demo_validation")),
    ]
    proof_statuses = [value for value in proof_statuses if value is not None]
    if not proof_statuses:
        proof_statuses = [
            _proof_status(candidate.get("replay_proof")),
            _proof_status(candidate.get("reconciliation_proof")),
            _proof_status(candidate.get("rollback_proof")),
            _proof_status(candidate.get("demo_validation_proof")),
        ]
        proof_statuses = [value for value in proof_statuses if value is not None]

    proof_bundle_status = str(_path(data, ("bridge_payload", "source_proof_bundle_status"), "") or "")
    if not proof_bundle_status:
        proof_bundle_status = str(_path(data, ("journey_payload", "source_proof_bundle_status"), "") or "")

    freshness = _first_mapping(
        *(_path(bundle, ("candidate", "freshness_proof")) for bundle in review_bundles),
        *(_path(bundle, ("proofs", "freshness", "evidence")) for bundle in review_bundles),
    )
    thresholds = _first_mapping(*(bundle.get("thresholds") for bundle in review_bundles))

    summary: dict[str, Any] = {}
    candidate_id = _text(
        data.get("candidate_id")
        or review_bundle.get("candidate_id")
        or candidate.get("candidate_id")
        or "unknown-candidate"
    )
    if proof_statuses:
        summary["replay_id"] = f"{READINESS_JSON}:{candidate_id}:replay-proof"
        summary["run_count"] = 1
        summary["event_count"] = len(proof_statuses) if proof_statuses else 1
        summary["mismatch_count"] = sum(1 for value in proof_statuses if value is False)
        summary["deterministic_replay"] = bool(proof_statuses and all(proof_statuses))
    elif proof_bundle_status:
        notes.append("proof bundle status existed without replay proof status records")
    if _safe_bool(_path(data, ("safety", "is_safe"), None)) is True:
        summary["sanitized"] = True
    age_hours = _number(freshness.get("age_hours"))
    if age_hours is not None:
        summary["evidence_age_days"] = age_hours / 24
    max_age_hours = _number(thresholds.get("max_freshness_age_hours"))
    if max_age_hours is not None:
        summary["max_evidence_age_days"] = max_age_hours / 24
    if not proof_statuses:
        notes.append("readiness JSON did not contain replay proof status records")
    return summary


def _summary_from_proof_bundle_json(
    data: Mapping[str, Any],
    notes: list[str],
    source_name: str,
) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    proof_values = _proof_values_from_bundle(data)
    if proof_values:
        summary["replay_id"] = f"{source_name}:proof-bundle"
        summary["run_count"] = 1
        summary["event_count"] = len(proof_values)
        summary["mismatch_count"] = sum(1 for value in proof_values if value is False)
        summary["deterministic_replay"] = all(proof_values)
    elif _text(data.get("source_proof_bundle_status") or data.get("candidate_bridge_status")):
        notes.append(f"{source_name} did not contain explicit replay proof booleans")

    safety = _first_mapping(data.get("safety"))
    if _safe_bool(safety.get("is_safe")) is True:
        summary["sanitized"] = True
    if _safe_bool(safety.get("paper_only")) is True and all(
        _safe_bool(safety.get(key)) is False
        for key in (
            "broker_connected",
            "credentials_used",
            "account_id_present",
            "network_used",
            "order_execution",
            "demo_trading",
            "live_trading",
            "live_trading_authorized",
        )
    ):
        summary["sanitized"] = True
    freshness = _first_mapping(
        _path(data, ("enriched_candidate", "freshness_proof")),
        _path(data, ("review_bundle", "proofs", "freshness", "evidence")),
        _path(data, ("canonical_review_bundle", "candidate", "freshness_proof")),
    )
    thresholds = _first_mapping(
        _path(data, ("canonical_review_bundle", "thresholds")),
        _path(data, ("review_bundle", "thresholds")),
        _path(data, ("bridge_payload", "canonical_review_bundle", "thresholds")),
        _path(data, ("journey_payload", "review_bundle", "thresholds")),
    )
    age_hours = _number(freshness.get("age_hours"))
    if age_hours is not None:
        summary["evidence_age_days"] = age_hours / 24
    max_age_hours = _number(thresholds.get("max_freshness_age_hours"))
    if max_age_hours is not None:
        summary["max_evidence_age_days"] = max_age_hours / 24
    return summary


def _proof_values_from_bundle(data: Mapping[str, Any]) -> list[bool]:
    candidates = (
        _first_mapping(data.get("enriched_candidate")),
        _first_mapping(_path(data, ("bridge_payload", "enriched_candidate"))),
        _first_mapping(_path(data, ("bridge_payload", "canonical_review_bundle", "candidate"))),
        _first_mapping(_path(data, ("review_bundle", "proofs"))),
        _first_mapping(_path(data, ("canonical_review_bundle", "candidate"))),
    )
    values: list[bool] = []
    for candidate in candidates:
        for key in (
            "replay_proof",
            "reconciliation_proof",
            "rollback_proof",
            "demo_validation_proof",
        ):
            value = _proof_status(candidate.get(key))
            if value is not None:
                values.append(value)
        if values:
            return values
        for key in ("replay", "reconciliation", "rollback", "demo_validation"):
            value = _proof_status(candidate.get(key))
            if value is not None:
                values.append(value)
        if values:
            return values
    return values


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


def _summary_from_replay_markdown(text: str, notes: list[str]) -> dict[str, Any]:
    fields = _key_values(text)
    summary: dict[str, Any] = {}
    for output_key, aliases in {
        "replay_id": ("replay_id", "replay id"),
        "run_count": ("run_count", "run count"),
        "event_count": ("event_count", "event count"),
        "mismatch_count": ("mismatch_count", "mismatch count"),
        "evidence_age_days": ("evidence_age_days", "evidence age days"),
        "max_evidence_age_days": ("max_evidence_age_days", "max evidence age days"),
    }.items():
        if output_key == "replay_id":
            text_value = _text_first(fields, *aliases)
            if text_value:
                summary[output_key] = text_value
            continue
        value = _number_first(fields, *aliases)
        if value is not None:
            summary[output_key] = value
    deterministic = _bool_first(fields, "deterministic_replay", "deterministic replay")
    if deterministic is not None:
        summary["deterministic_replay"] = deterministic
    sanitized = _bool_first(fields, "sanitized")
    if sanitized is not None:
        summary["sanitized"] = sanitized

    proof_values = []
    for name in ("replay", "reconciliation", "rollback", "demo_validation"):
        match = re.search(rf"(?im)^\s*-\s*{re.escape(name)}:\s*(true|false)\s*$", text)
        if match:
            proof_values.append(match.group(1).lower() == "true")
    if proof_values:
        defaults = {
            "replay_id": "AIOS_FOREX_REPLAY_RECONCILIATION_PROOF_BUNDLE_V1_REPORT:proofs",
            "run_count": 1,
            "event_count": len(proof_values),
            "mismatch_count": sum(1 for value in proof_values if not value),
            "deterministic_replay": all(proof_values),
        }
        _merge_if_present(summary, defaults)
    if re.search(r"(?i)no broker connectivity.*no credentials.*no .*network.*no .*order execution", text):
        summary["sanitized"] = True
    if not proof_values:
        notes.append("replay markdown did not contain proof status records")
    return summary


def _key_values(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    pattern = re.compile(r"(?im)^\s*-?\s*([A-Za-z0-9 _/\-]+):\s*`?([^`\n]+?)`?\s*\.?\s*$")
    for match in pattern.finditer(text):
        values[_key(match.group(1))] = match.group(2).strip()
    return values


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
    glob_pattern: str,
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
    for path in sorted(root.glob(glob_pattern)):
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


def _proof_status(value: Any) -> bool | None:
    if isinstance(value, Mapping):
        if "status" in value:
            return _safe_bool(value.get("status"))
        if "evidence" in value:
            return _safe_bool(value.get("evidence"))
    return _safe_bool(value)


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
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return None


def _number_first(values: Mapping[str, str], *keys: str) -> float | None:
    for key in keys:
        value = _number(values.get(_key(key)))
        if value is not None:
            return value
    return None


def _text_first(values: Mapping[str, str], *keys: str) -> str:
    for key in keys:
        value = _text(values.get(_key(key)))
        if value:
            return value
    return ""


def _bool_first(values: Mapping[str, str], *keys: str) -> bool | None:
    for key in keys:
        value = _safe_bool(values.get(_key(key)))
        if value is not None:
            return value
    return None


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


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
    "REPLAY_EVIDENCE_INTAKE_VERSION",
    "intake_replay_evidence",
    "result_to_jsonable_dict",
    "result_to_operator_text",
]
