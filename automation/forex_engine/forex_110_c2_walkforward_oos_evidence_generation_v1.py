"""Classify C2 walk-forward/OOS evidence availability for Forex 110.

This module is local-only. It does not create proof from samples, tests, broker
data, credentials, or live execution paths.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Mapping

from automation.forex_engine.forex_110_profit_evidence_truth_lock_v1 import (
    run_profit_evidence_truth_lock,
)
from automation.forex_engine.walk_forward_depth_r_v1 import ANCHOR_CANDIDATE_ID
from automation.forex_engine.walk_forward_evidence_intake_v1 import (
    DEFAULT_REPORT_ROOT,
    intake_walk_forward_evidence,
    result_to_jsonable_dict as intake_result_to_jsonable_dict,
)
from automation.forex_engine.walk_forward_oos_evidence_v1 import WALK_FORWARD_OOS_READY


PACKET_ID = "PKT-FOREX-110-C2-WALKFORWARD-OOS-EVIDENCE-GENERATION-V1"
ENGINE_VERSION = "forex_110_c2_walkforward_oos_evidence_generation_v1"
TARGET_CANDIDATE_ID = "c2-eur-buy-stronger-review-ready"

C2_OOS_EVIDENCE_PROVEN = "PROVEN"
BLOCKED_NO_REAL_C2_OOS_SOURCE = "BLOCKED_NO_REAL_C2_OOS_SOURCE"
BLOCKED_TOP_CANDIDATE_MISMATCH = "BLOCKED_TOP_CANDIDATE_MISMATCH"

EVIDENCE_SOURCE_REAL_LOCAL_DETERMINISTIC = "REAL_LOCAL_DETERMINISTIC"
EVIDENCE_SOURCE_SAMPLE_TEST_ONLY = "SAMPLE_TEST_ONLY"
EVIDENCE_SOURCE_MISSING = "MISSING"

REQUIRED_PROOF_FIELDS = (
    "candidate",
    "windows_total",
    "windows_passed",
    "oos_segments_total",
    "oos_segments_passed",
    "min_pass_rate",
    "max_drawdown",
    "max_allowed_drawdown",
    "sanitized",
    "evidence_age_days",
    "max_evidence_age_days",
    "candidate_alignment",
)

PROTECTED_PERMISSION_FLAGS = {
    "next_demo_trade_allowed": False,
    "broker_action_allowed": False,
    "real_money_allowed": False,
    "compounding_allowed": False,
    "bank_movement_allowed": False,
    "live_trading_allowed": False,
    "credential_access_allowed": False,
    "order_submission_allowed": False,
    "owner_approval_created": False,
}

CANONICAL_OWNER_FILE = "automation/forex_engine/walk_forward_evidence_intake_v1.py"
TEST_FILE = "tests/forex_engine/test_forex_110_c2_walkforward_oos_evidence_generation_v1.py"
RUNNER_SCRIPT = "scripts/forex_delivery/run_forex_110_c2_walkforward_oos_evidence_generation_v1.py"


def run_c2_walkforward_oos_evidence_generation(
    report_root: str | Path = DEFAULT_REPORT_ROOT,
) -> dict[str, Any]:
    """Return the local deterministic C2 walk-forward/OOS evidence state."""

    root = Path(report_root)
    profit_lock = run_profit_evidence_truth_lock(root)
    intake = intake_result_to_jsonable_dict(intake_walk_forward_evidence(root))
    top_candidate_id = str(profit_lock.get("top_candidate_id") or "NONE")
    source_files = list(intake.get("source_files") or [])
    source_candidate_ids = _candidate_ids_from_sources(root, source_files)
    normalized = dict(intake.get("normalized_summary") or {})
    complete_fields = _complete_proof_fields(
        top_candidate_id=top_candidate_id,
        source_candidate_ids=source_candidate_ids,
        intake=intake,
        normalized=normalized,
    )
    sample_or_test_references = _sample_or_test_references(root)
    has_sample_or_test_c2 = bool(sample_or_test_references)
    c2_source_aligned = TARGET_CANDIDATE_ID in source_candidate_ids
    top_candidate_matches = top_candidate_id == TARGET_CANDIDATE_ID
    has_real_c2_oos = (
        top_candidate_matches
        and c2_source_aligned
        and intake.get("status") == WALK_FORWARD_OOS_READY
        and not _missing_required_fields(complete_fields)
    )

    if has_real_c2_oos:
        c2_status = C2_OOS_EVIDENCE_PROVEN
        source_classification = EVIDENCE_SOURCE_REAL_LOCAL_DETERMINISTIC
        candidate_alignment = "ALIGNED"
        blockers: list[str] = []
        safe_next_action = (
            "Rerun the Forex 110 walk-forward/OOS sufficiency truth lock. "
            "No trading authority is created."
        )
    elif not top_candidate_matches:
        c2_status = BLOCKED_TOP_CANDIDATE_MISMATCH
        source_classification = (
            EVIDENCE_SOURCE_SAMPLE_TEST_ONLY if has_sample_or_test_c2 else EVIDENCE_SOURCE_MISSING
        )
        candidate_alignment = "TOP_CANDIDATE_MISMATCH"
        blockers = [f"profit truth-lock top candidate is {top_candidate_id}, not {TARGET_CANDIDATE_ID}"]
        safe_next_action = "Resolve the profit truth-lock top candidate before collecting C2 OOS proof."
    else:
        c2_status = BLOCKED_NO_REAL_C2_OOS_SOURCE
        source_classification = (
            EVIDENCE_SOURCE_SAMPLE_TEST_ONLY if has_sample_or_test_c2 else EVIDENCE_SOURCE_MISSING
        )
        candidate_alignment = (
            "BLOCKED_NO_REAL_C2_OOS_SOURCE"
            if not c2_source_aligned
            else "BLOCKED_INCOMPLETE_C2_OOS_SOURCE"
        )
        blockers = _dedupe(
            [
                "no real sanitized walk-forward/OOS source for c2-eur-buy-stronger-review-ready",
                *[f"missing field: {field}" for field in _missing_required_fields(complete_fields)],
                (
                    f"canonical walk-forward depth anchor is {ANCHOR_CANDIDATE_ID}, "
                    f"not {TARGET_CANDIDATE_ID}"
                ),
                "C2 references found only in sample/test-style proof builders or examples",
            ]
        )
        safe_next_action = (
            "Provide or generate a real sanitized C2 walk-forward/OOS source with segment "
            "counts before rerunning the sufficiency truth lock. Do not trade."
        )

    proof_fields = dict(complete_fields)
    proof_fields["candidate_alignment"] = candidate_alignment
    return {
        "packet_id": PACKET_ID,
        "engine_version": ENGINE_VERSION,
        "target_candidate_id": TARGET_CANDIDATE_ID,
        "top_candidate_id": top_candidate_id,
        "c2_oos_evidence_status": c2_status,
        "walk_forward_oos_status": "READY_FOR_TRUTH_LOCK_RERUN" if has_real_c2_oos else c2_status,
        "profit_persistence_unlocked": False,
        "truth_lock_status": "NOT_RUN_BY_C2_GENERATOR",
        "candidate_alignment": candidate_alignment,
        "evidence_source_classification": source_classification,
        "required_proof_fields": proof_fields,
        "windows_total": proof_fields.get("windows_total"),
        "windows_passed": proof_fields.get("windows_passed"),
        "oos_segments_total": proof_fields.get("oos_segments_total"),
        "oos_segments_passed": proof_fields.get("oos_segments_passed"),
        "min_pass_rate": proof_fields.get("min_pass_rate"),
        "max_drawdown": proof_fields.get("max_drawdown"),
        "max_allowed_drawdown": proof_fields.get("max_allowed_drawdown"),
        "sanitized": proof_fields.get("sanitized"),
        "evidence_age_days": proof_fields.get("evidence_age_days"),
        "max_evidence_age_days": proof_fields.get("max_evidence_age_days"),
        "blockers": blockers,
        "sample_or_test_references": sample_or_test_references,
        "walkforward_source_candidate_ids": source_candidate_ids,
        "walkforward_intake_status": intake.get("status"),
        "walkforward_intake_missing_fields": list(intake.get("missing_fields") or []),
        "walkforward_intake_blockers": list(intake.get("blockers") or []),
        "walkforward_intake_parse_notes": list(intake.get("parse_notes") or []),
        "source_files": source_files,
        "permissions": dict(PROTECTED_PERMISSION_FLAGS),
        **PROTECTED_PERMISSION_FLAGS,
        "attack_to_finish": _attack_to_finish(c2_status, candidate_alignment, blockers),
        "next_safe_action": safe_next_action,
    }


def build_report_markdown(result: Mapping[str, Any]) -> str:
    """Build the C2 evidence classification report."""

    attack = result.get("attack_to_finish") if isinstance(result.get("attack_to_finish"), Mapping) else {}
    proof = result.get("required_proof_fields") if isinstance(result.get("required_proof_fields"), Mapping) else {}
    lines = [
        "# AIOS Forex 110 C2 Walk-Forward OOS Evidence Generation V1",
        "",
        f"Packet ID: `{result.get('packet_id', PACKET_ID)}`",
        f"C2 evidence status: `{result.get('c2_oos_evidence_status')}`",
        f"Target candidate id: `{result.get('target_candidate_id', TARGET_CANDIDATE_ID)}`",
        f"Top candidate id: `{result.get('top_candidate_id')}`",
        f"Candidate alignment: `{result.get('candidate_alignment')}`",
        f"Evidence source classification: `{result.get('evidence_source_classification')}`",
        "",
        "## Required Proof Fields",
    ]
    for field in REQUIRED_PROOF_FIELDS:
        label = "proof_candidate" if field == "candidate" else field
        lines.append(f"- {label}: `{_markdown_value(proof.get(field))}`")
    lines.extend(["", "## Blockers"])
    lines.extend(f"- {item}" for item in result.get("blockers") or ["none"])
    lines.extend(["", "## Source Classification"])
    lines.append(
        "- Real C2 walk-forward/OOS proof was not created unless complete sanitized local evidence was already present."
    )
    lines.append("- Sample/test-style C2 references were not promoted into proof.")
    lines.append("- No broker, credential, demo, live, scheduler, commit, push, PR, or merge action was performed.")
    lines.extend(["", "## Permission Locks"])
    for key, value in (result.get("permissions") or {}).items():
        lines.append(f"- {key}: `{str(value).lower()}`")
    lines.extend(
        [
            "",
            "## ATTACK_TO_FINISH",
            f"- blocker_id: {attack.get('blocker_id', 'UNKNOWN')}",
            f"- blocker_status: {attack.get('blocker_status', 'UNKNOWN')}",
            f"- exact_blocker: {attack.get('exact_blocker', 'UNKNOWN')}",
            f"- canonical_owner_file: {attack.get('canonical_owner_file', 'UNKNOWN')}",
            f"- test_file: {attack.get('test_file', 'UNKNOWN')}",
            f"- runner_script: {attack.get('runner_script', 'UNKNOWN')}",
            f"- missing_evidence_field: {attack.get('missing_evidence_field', 'UNKNOWN')}",
            f"- unlock_status_required: {attack.get('unlock_status_required', 'UNKNOWN')}",
            f"- next_packet_name: {attack.get('next_packet_name', 'UNKNOWN')}",
            f"- owner_action_required: {attack.get('owner_action_required', 'UNKNOWN')}",
            f"- stop_condition: {attack.get('stop_condition', 'UNKNOWN')}",
            f"- no_bloat_guard: {attack.get('no_bloat_guard', 'UNKNOWN')}",
            "",
            "## Next Safe Action",
            str(result.get("next_safe_action", "")),
            "",
        ]
    )
    return "\n".join(lines)


def _complete_proof_fields(
    *,
    top_candidate_id: str,
    source_candidate_ids: list[str],
    intake: Mapping[str, Any],
    normalized: Mapping[str, Any],
) -> dict[str, Any]:
    aligned = top_candidate_id == TARGET_CANDIDATE_ID and TARGET_CANDIDATE_ID in source_candidate_ids
    if not aligned:
        return {
            "candidate": None,
            "windows_total": None,
            "windows_passed": None,
            "oos_segments_total": None,
            "oos_segments_passed": None,
            "min_pass_rate": None,
            "max_drawdown": None,
            "max_allowed_drawdown": None,
            "sanitized": None,
            "evidence_age_days": None,
            "max_evidence_age_days": None,
        }
    return {
        "candidate": TARGET_CANDIDATE_ID,
        "windows_total": normalized.get("windows_total"),
        "windows_passed": normalized.get("windows_passed"),
        "oos_segments_total": normalized.get("oos_segments_total"),
        "oos_segments_passed": normalized.get("oos_segments_passed"),
        "min_pass_rate": normalized.get("min_pass_rate"),
        "max_drawdown": normalized.get("max_drawdown"),
        "max_allowed_drawdown": normalized.get("max_allowed_drawdown"),
        "sanitized": normalized.get("sanitized") if intake.get("sanitized") is True else None,
        "evidence_age_days": normalized.get("evidence_age_days"),
        "max_evidence_age_days": normalized.get("max_evidence_age_days"),
    }


def _missing_required_fields(fields: Mapping[str, Any]) -> list[str]:
    return [field for field in REQUIRED_PROOF_FIELDS[:-1] if fields.get(field) is None]


def _sample_or_test_references(root: Path) -> list[str]:
    repo_root = root.parents[1] if root.name == "forex_delivery" else Path.cwd()
    candidate_paths = [
        repo_root / "automation" / "forex_engine" / "profit_proof_ledger_v1.py",
        repo_root / "automation" / "forex_engine" / "strategy_proof_engine_v1.py",
        repo_root / "automation" / "forex_engine" / "review_ready_candidate_selector_v1.py",
    ]
    references: list[str] = []
    for path in candidate_paths:
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if TARGET_CANDIDATE_ID in text:
            references.append(path.as_posix())
    return references


def _candidate_ids_from_sources(root: Path, source_files: list[str]) -> list[str]:
    candidates: list[str] = []
    for source in source_files:
        path = Path(source)
        if not path.is_absolute():
            path = root.parents[1] / source if source.startswith("Reports/") else root / path
        if not path.exists() or not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        candidates.extend(_candidate_ids_from_text(text))
    return _dedupe(candidates)


def _candidate_ids_from_text(text: str) -> list[str]:
    patterns = (
        re.compile(r"(?im)^\s*-\s*(?:candidate|candidate_id|anchor candidate|selected_candidate_id)\s*:\s*`?([^`\n.]+?)`?\s*$"),
        re.compile(r"(?im)\|\s*(c[0-9]+-[a-z0-9-]+)\s*\|"),
    )
    candidates: list[str] = []
    for pattern in patterns:
        for match in pattern.finditer(text):
            value = match.group(1).strip()
            if re.fullmatch(r"c[0-9]+-[a-z0-9-]+", value):
                candidates.append(value)
    return _dedupe(candidates)


def _attack_to_finish(status: str, candidate_alignment: str, blockers: list[str]) -> dict[str, str]:
    if status == C2_OOS_EVIDENCE_PROVEN:
        return {
            "blocker_id": "NO_BLOCKER",
            "blocker_status": "PROVEN",
            "exact_blocker": "NONE",
            "canonical_owner_file": CANONICAL_OWNER_FILE,
            "test_file": TEST_FILE,
            "runner_script": RUNNER_SCRIPT,
            "missing_evidence_field": "NONE",
            "unlock_status_required": "PROVEN",
            "next_packet_name": "NONE",
            "owner_action_required": "NONE",
            "stop_condition": "NONE",
            "no_bloat_guard": "Reuse existing walk-forward intake and do not promote sample/test C2 data into proof.",
        }
    missing = "oos_segments_total,oos_segments_passed,candidate_alignment"
    return {
        "blocker_id": "MISSING_EVIDENCE_FIELD",
        "blocker_status": "BLOCKED",
        "exact_blocker": "; ".join(blockers) if blockers else status,
        "canonical_owner_file": CANONICAL_OWNER_FILE,
        "test_file": TEST_FILE,
        "runner_script": RUNNER_SCRIPT,
        "missing_evidence_field": missing,
        "unlock_status_required": "PROVEN",
        "next_packet_name": "PKT-FOREX-110-C2-WALKFORWARD-OOS-SOURCE-COLLECTION-V1",
        "owner_action_required": f"provide missing field {missing}",
        "stop_condition": candidate_alignment,
        "no_bloat_guard": "Reuse existing walk-forward intake and do not promote sample/test C2 data into proof.",
    }


def _dedupe(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return result


def _markdown_value(value: Any) -> str:
    return "MISSING" if value is None else str(value)


__all__ = [
    "BLOCKED_NO_REAL_C2_OOS_SOURCE",
    "C2_OOS_EVIDENCE_PROVEN",
    "ENGINE_VERSION",
    "PACKET_ID",
    "TARGET_CANDIDATE_ID",
    "build_report_markdown",
    "run_c2_walkforward_oos_evidence_generation",
]
