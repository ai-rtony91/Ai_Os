"""Multi-night evidence model for Night Supervisor Gate 5."""

from __future__ import annotations

from typing import Any


DEFAULT_REQUIRED_NIGHTS = 5
DEFAULT_REQUIRED_PASS_COUNT = 4
DEFAULT_ALLOWED_WARN_COUNT = 1


def evaluate_multi_night_evidence(
    nights: list[dict[str, Any]] | None = None,
    *,
    required_nights: int = DEFAULT_REQUIRED_NIGHTS,
    required_pass_count: int = DEFAULT_REQUIRED_PASS_COUNT,
    allowed_warn_count: int = DEFAULT_ALLOWED_WARN_COUNT,
) -> dict[str, Any]:
    """Evaluate evidence windows without pretending simulated nights are real."""
    rows = list(nights or [])
    pass_count = sum(1 for row in rows if str(row.get("status") or "").upper() == "PASS")
    warn_count = sum(1 for row in rows if str(row.get("status") or "").upper() == "WARN")
    fail_count = sum(1 for row in rows if str(row.get("status") or "").upper() == "FAIL")
    explicit_real_windows = all(bool(row.get("real_world_window")) for row in rows) if rows else False

    model_ready = True
    passed = (
        len(rows) >= required_nights
        and pass_count >= required_pass_count
        and warn_count <= allowed_warn_count
        and fail_count == 0
        and explicit_real_windows
    )
    classification = "PASSED_REAL_WORLD" if passed else "MODEL_READY_NOT_PASSED_REAL_WORLD"
    return {
        "schema": "AIOS_MULTI_NIGHT_EVIDENCE_MODEL.v1",
        "classification": classification,
        "model_ready": model_ready,
        "required_nights": required_nights,
        "required_pass_count": required_pass_count,
        "allowed_warn_count": allowed_warn_count,
        "disallowed_fail_count": 0,
        "observed_nights": len(rows),
        "pass_count": pass_count,
        "warn_count": warn_count,
        "fail_count": fail_count,
        "explicit_real_windows": explicit_real_windows,
        "required_evidence_paths": [
            "telemetry/qualification/AIOS_NIGHT_SUPERVISOR_QUALIFICATION_LEDGER.jsonl",
            "morning handoff reports for each night",
            "worker heartbeat evidence for each cycle",
            "packet integrity evidence for each cycle",
            "recovery awareness evidence for each warning or failure",
        ],
        "human_owner_approval_point": "After required real-world evidence windows are reviewed.",
        "write_performed": False,
    }
