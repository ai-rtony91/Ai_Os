"""Deterministic Forex evidence depth and walk-forward sufficiency gate."""

from __future__ import annotations

from typing import Any, Mapping


PACKET_ID = "PKT-FOREX-EVIDENCE-CANDIDATE-DEMO-READINESS-CONSOLIDATED-V1"
MISSION_ID = "MISSION-AIOS-FOREX-FINISH-LINE-V1"
PROGRAM_ID = "PROGRAM-FOREX-PROFIT-AUTONOMY-V1"
EPIC_ID = "EPC-FOREX-AUTONOMY-COMPLETION-001"
BUCKET_ID = "BKT-FOREX-EVIDENCE-CANDIDATE-DEMO-READINESS-001"

MINIMUM_REQUIRED_TRADE_COUNT = 30
MINIMUM_REQUIRED_WALKFORWARD_WINDOWS = 6

PROTECTED_FALSE_FIELDS = (
    "broker_api_used",
    "credentials_used",
    "env_read",
    "account_identifiers_used",
    "order_execution",
    "demo_authorized",
    "live_authorized",
    "scheduler_started",
    "daemon_started",
    "webhook_started",
    "background_loop_started",
)


def run_evidence_depth_walkforward_sufficiency_v1(
    evidence: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    sample = dict(evidence or _default_evidence_sample())
    observed_trade_count = int(sample.get("observed_trade_count", 0))
    observed_walkforward_windows = int(sample.get("observed_walkforward_windows", 0))
    sufficient_sample = observed_trade_count >= MINIMUM_REQUIRED_TRADE_COUNT
    sufficient_walkforward = observed_walkforward_windows >= MINIMUM_REQUIRED_WALKFORWARD_WINDOWS
    evidence_depth_score = _score_depth(observed_trade_count, observed_walkforward_windows)
    blockers: list[str] = []
    flags: list[str] = []
    if not sufficient_sample:
        blockers.append("insufficient_sample")
        flags.append("trade_count_below_minimum")
    if not sufficient_walkforward:
        blockers.append("walkforward_window_insufficiency")
        flags.append("walkforward_windows_below_minimum")
    if evidence_depth_score < 75:
        blockers.append("weak_evidence_depth")
        flags.append("evidence_depth_score_below_promotion_threshold")

    result: dict[str, Any] = {
        "sufficiency_status": "INSUFFICIENT_EVIDENCE_DEPTH_BLOCKED"
        if blockers
        else "EVIDENCE_DEPTH_SUFFICIENT_REVIEW_READY",
        "minimum_required_trade_count": MINIMUM_REQUIRED_TRADE_COUNT,
        "observed_trade_count": observed_trade_count,
        "minimum_required_walkforward_windows": MINIMUM_REQUIRED_WALKFORWARD_WINDOWS,
        "observed_walkforward_windows": observed_walkforward_windows,
        "insufficient_sample_block": not sufficient_sample,
        "walkforward_gate_cleared": sufficient_walkforward,
        "evidence_depth_score": evidence_depth_score,
        "evidence_quality_flags": flags or ["minimum_depth_and_walkforward_evidence_present"],
        "promotion_allowed": not blockers,
        "promotion_blockers": blockers,
        "required_next_evidence": _required_next_evidence(
            sufficient_sample,
            sufficient_walkforward,
            evidence_depth_score,
        ),
        "mission_id": MISSION_ID,
        "program_id": PROGRAM_ID,
        "epic_id": EPIC_ID,
        "bucket_id": BUCKET_ID,
        "packet_id": PACKET_ID,
    }
    result.update({field: False for field in PROTECTED_FALSE_FIELDS})
    return result


def _default_evidence_sample() -> dict[str, int]:
    return {
        "observed_trade_count": 24,
        "observed_walkforward_windows": 4,
    }


def _score_depth(observed_trade_count: int, observed_walkforward_windows: int) -> int:
    trade_ratio = min(observed_trade_count / MINIMUM_REQUIRED_TRADE_COUNT, 1.0)
    window_ratio = min(observed_walkforward_windows / MINIMUM_REQUIRED_WALKFORWARD_WINDOWS, 1.0)
    return int(round((trade_ratio * 50) + (window_ratio * 50)))


def _required_next_evidence(
    sufficient_sample: bool,
    sufficient_walkforward: bool,
    evidence_depth_score: int,
) -> list[str]:
    required: list[str] = []
    if not sufficient_sample:
        required.append("add_more_reviewed_trade_samples_until_minimum_count_is_met")
    if not sufficient_walkforward:
        required.append("add_more_walkforward_windows_until_minimum_window_count_is_met")
    if evidence_depth_score < 75:
        required.append("raise_evidence_depth_score_before_promotion")
    return required or ["owner_review_of_review_ready_evidence_depth"]


def build_report_markdown(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# AIOS Forex Evidence Depth Walkforward Sufficiency V1 Report",
            "",
            f"Sufficiency status: {result.get('sufficiency_status')}",
            f"Observed trade count: {result.get('observed_trade_count')}",
            f"Observed walkforward windows: {result.get('observed_walkforward_windows')}",
            f"Evidence depth score: {result.get('evidence_depth_score')}",
            f"Promotion allowed: {result.get('promotion_allowed')}",
            "",
            "Promotion blockers:",
            *[f"- {item}" for item in result.get("promotion_blockers", [])],
            "",
            "Required next evidence:",
            *[f"- {item}" for item in result.get("required_next_evidence", [])],
            "",
            "Protected fields remain false.",
            "",
        ]
    )


__all__ = [
    "PROTECTED_FALSE_FIELDS",
    "build_report_markdown",
    "run_evidence_depth_walkforward_sufficiency_v1",
]
