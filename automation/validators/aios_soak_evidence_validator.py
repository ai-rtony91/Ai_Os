from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

DEFAULT_REPORT = REPO_ROOT / "Reports/endurance_soak/soak_evidence_report.example.json"
REQUIRED_TOP_LEVEL = [
    "packet_id",
    "run_id",
    "run_mode",
    "status",
    "started_utc",
    "completed_utc",
    "max_cycles",
    "interval_seconds",
    "run_timeout_seconds",
    "samples",
    "forbidden_actions_confirmed",
    "writable_roots",
    "reasons",
]

REQUIRED_SAMPLE_FIELDS = [
    "sample_utc",
    "marker_exists",
    "heartbeat_exists",
    "heartbeat_freshness_status",
    "process_rss_mb",
    "disk_samples",
    "stop_marker_detected",
]

ALLOWED_STATUSES = {"PASS", "STOPPED", "FAILED", "BLOCKED"}
ALLOWED_WRITABLE_ROOT_PREFIXES = [
    "telemetry/soak",
    "Reports/endurance_soak",
]


def _as_list(value: object) -> list[object]:
    return list(value) if isinstance(value, list) else []


def _read_json(path: Path) -> dict[str, object]:
    if not path.exists():
        raise FileNotFoundError(path)
    with path.open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError("Evidence payload is not a JSON object.")
    return data


def _normalize_root(value: object) -> str:
    text = str(value).replace("\\", "/").strip().strip("/")
    return text


def validate(report_path: Path) -> dict[str, object]:
    failures: list[str] = []
    try:
        evidence = _read_json(report_path)
    except Exception as exc:
        failures.append(f"Failed to read evidence JSON: {exc}")
        return {
            "validator": "aios_soak_evidence_validator",
            "status": "FAIL",
            "failures": failures,
            "safe_next_action": "Correct the evidence example JSON path and schema.",
        }

    for field in REQUIRED_TOP_LEVEL:
        if field not in evidence:
            failures.append(f"Missing required top-level field: {field}")

    if evidence.get("status") not in ALLOWED_STATUSES:
        failures.append(f"Invalid status value: {evidence.get('status')}")

    max_cycles = evidence.get("max_cycles")
    interval_seconds = evidence.get("interval_seconds")
    run_timeout_seconds = evidence.get("run_timeout_seconds")
    if not isinstance(max_cycles, int) or max_cycles < 1:
        failures.append("max_cycles must be a positive integer.")
    if not isinstance(interval_seconds, int) or interval_seconds < 1:
        failures.append("interval_seconds must be a positive integer.")
    if not isinstance(run_timeout_seconds, int) or run_timeout_seconds < 1:
        failures.append("run_timeout_seconds must be a positive integer.")

    samples = _as_list(evidence.get("samples"))
    if not samples:
        failures.append("samples must be a non-empty list.")

    forbidden = evidence.get("forbidden_actions_confirmed")
    if not isinstance(forbidden, dict):
        failures.append("forbidden_actions_confirmed must be an object.")

    writable_roots = _as_list(evidence.get("writable_roots"))
    if not writable_roots:
        failures.append("writable_roots must be a non-empty list.")
    else:
        for root in writable_roots:
            norm = _normalize_root(root).lower()
            if not any(norm == allowed.lower() or norm.startswith(f"{allowed.lower()}/") for allowed in ALLOWED_WRITABLE_ROOT_PREFIXES):
                failures.append(f"Writable root is outside allowed scope: {root}")

    for index, sample in enumerate(samples):
        if not isinstance(sample, dict):
            failures.append(f"Sample at index {index} is not an object.")
            continue
        for field in REQUIRED_SAMPLE_FIELDS:
            if field not in sample:
                failures.append(f"Sample at index {index} missing required field: {field}")

        if "heartbeat_freshness_status" in sample and sample["heartbeat_freshness_status"] not in {"MISSING", "FRESH", "STALE", "FUTURE", "MALFORMED"}:
            failures.append(f"Sample at index {index} has unexpected heartbeat_freshness_status value.")

    report = {
        "validator": "aios_soak_evidence_validator",
        "status": "PASS" if not failures else "FAIL",
        "failures": failures,
        "safe_next_action": "Use this evidence as DRY_RUN-only proof example." if not failures else "Fix the evidence JSON to satisfy schema.",
    }
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate soak evidence payload.")
    parser.add_argument("--sample-check", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT))
    args = parser.parse_args()

    if not args.sample_check:
        payload = {
            "status": "BLOCKED",
            "reason": "--sample-check required",
            "safe_next_action": "Run with --sample-check to validate example evidence.",
        }
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2

    payload = validate(Path(args.report_path))
    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        print(f"{payload['validator']}: {payload['status']}")
        for failure in payload["failures"]:
            print(f"FAIL: {failure}")
        print(f"safe_next_action: {payload['safe_next_action']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
