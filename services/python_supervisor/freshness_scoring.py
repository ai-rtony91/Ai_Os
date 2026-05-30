"""Freshness scoring helpers for AI_OS read-only evidence.

The functions in this module classify already-supplied evidence payloads. They
do not write files, launch child processes, call networks, change scheduler
state, mutate runtime, move packets, or repair evidence.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from typing import Any


FRESH = "fresh"
USABLE = "usable"
STALE = "stale"
MISSING = "missing"
UNKNOWN = "unknown"

TIMESTAMP_FIELDS = (
    "generated_at",
    "generated_utc",
    "timestamp_utc",
    "created_utc",
    "updated_utc",
    "lastUpdatedAt",
    "startedAt",
    "completedAt",
)

FRESH_SECONDS = 2 * 60 * 60
USABLE_SECONDS = 24 * 60 * 60
_MAX_ITER_DEPTH = 10


def _normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def parse_timestamp(value: object) -> datetime | None:
    if isinstance(value, datetime):
        return _normalize_datetime(value)
    if not isinstance(value, str):
        return None

    text = value.strip()
    if not text:
        return None
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"

    candidates = [text]
    if "." in text and "+" not in text and text.count(":") >= 2:
        candidates.append(text.split(".", 1)[0])

    for candidate in candidates:
        try:
            return _normalize_datetime(datetime.fromisoformat(candidate))
        except ValueError:
            continue

    for pattern in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d_%H%M"):
        try:
            return datetime.strptime(text, pattern).replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    return None


def _iter_values(payload: object, _depth: int = 0) -> list[object]:
    if _depth >= _MAX_ITER_DEPTH:
        return []
    if isinstance(payload, dict):
        values: list[object] = []
        for field in TIMESTAMP_FIELDS:
            if field in payload:
                values.append(payload[field])
        for value in payload.values():
            values.extend(_iter_values(value, _depth + 1))
        return values
    if isinstance(payload, list):
        values = []
        for item in payload:
            values.extend(_iter_values(item, _depth + 1))
        return values
    return []


def find_freshness_timestamp(payload: object) -> datetime | None:
    timestamps = [parsed for parsed in (parse_timestamp(value) for value in _iter_values(payload)) if parsed]
    if not timestamps:
        return None
    return max(timestamps)


def classify_freshness(timestamp: object, now: object | None = None) -> str:
    parsed_timestamp = parse_timestamp(timestamp)
    if parsed_timestamp is None:
        return UNKNOWN

    parsed_now = parse_timestamp(now) if now is not None else datetime.now(timezone.utc)
    if parsed_now is None:
        parsed_now = datetime.now(timezone.utc)

    age_seconds = (_normalize_datetime(parsed_now) - parsed_timestamp).total_seconds()
    if age_seconds < 0:
        return FRESH
    if age_seconds <= FRESH_SECONDS:
        return FRESH
    if age_seconds <= USABLE_SECONDS:
        return USABLE
    return STALE


def score_evidence_freshness(
    payload: object,
    expected: bool = True,
    now: object | None = None,
) -> dict[str, Any]:
    if payload is None:
        freshness = MISSING if expected else UNKNOWN
        return {
            "freshness": freshness,
            "timestamp": None,
            "age_seconds": None,
            "expected": expected,
            "reason": "expected evidence is absent" if expected else "evidence not supplied",
        }

    timestamp = find_freshness_timestamp(payload)
    if timestamp is None:
        return {
            "freshness": UNKNOWN,
            "timestamp": None,
            "age_seconds": None,
            "expected": expected,
            "reason": "evidence has no recognized timestamp field",
        }

    parsed_now = parse_timestamp(now) if now is not None else datetime.now(timezone.utc)
    if parsed_now is None:
        parsed_now = datetime.now(timezone.utc)
    age_seconds = max(0, int((_normalize_datetime(parsed_now) - timestamp).total_seconds()))

    return {
        "freshness": classify_freshness(timestamp, parsed_now),
        "timestamp": timestamp.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "age_seconds": age_seconds,
        "expected": expected,
        "reason": "recognized timestamp field found",
    }


def summarize_freshness(items: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {FRESH: 0, USABLE: 0, STALE: 0, MISSING: 0, UNKNOWN: 0}
    for item in items:
        freshness = str(item.get("freshness", UNKNOWN))
        counts[freshness] = counts.get(freshness, 0) + 1

    worst = FRESH
    for candidate in (MISSING, STALE, UNKNOWN, USABLE, FRESH):
        if counts.get(candidate, 0):
            worst = candidate
            break

    return {
        "schema": "AIOS_FRESHNESS_SUMMARY.v1",
        "item_count": len(items),
        "counts": counts,
        "worst_freshness": worst,
        "fresh_threshold_seconds": FRESH_SECONDS,
        "usable_threshold_seconds": USABLE_SECONDS,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Print a sample AI_OS freshness scoring model.")
    parser.add_argument("--pretty", action="store_true", help="Pretty-print JSON output.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sample_payload = {"generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}
    sample = score_evidence_freshness(sample_payload)
    output = {
        "schema": "AIOS_FRESHNESS_SCORING_PREVIEW.v1",
        "classes": [FRESH, USABLE, STALE, MISSING, UNKNOWN],
        "timestamp_fields": list(TIMESTAMP_FIELDS),
        "sample": sample,
        "summary": summarize_freshness([sample]),
        "blocked_capabilities": [
            "file_writes",
            "child_process_launch",
            "network_calls",
            "runtime_mutation",
            "scheduler_mutation",
        ],
    }
    print(json.dumps(output, indent=2 if args.pretty else None))


if __name__ == "__main__":
    main()
