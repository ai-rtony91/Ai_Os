"""AI_OS autonomy gap reassessment (report-only).

This module reads the current proof spine, runtime queue spine, human gate
packet, dogfood evidence, queue validation output, operator dependency ledger,
and reduction target selector output, then ranks the remaining gaps that keep
AI_OS in observe-only proof mode.

It does not launch runtime, dispatch workers, enqueue or dequeue work, mutate
queues or telemetry, touch credentials, or approve execution. It produces a
report-only reassessment and writes JSON/Markdown evidence under
Reports/autonomy_gap/ by default.

Pure standard library. JSON-only CLI. Deterministic with injected evidence and
timestamp.
"""

from __future__ import annotations

import argparse
import copy
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from automation.orchestration.autonomy_reports.aios_operator_dependency_ledger import (
    build_operator_dependency_ledger,
    summarize_operator_dependency_ledger,
    validate_operator_dependency_ledger,
)
from automation.orchestration.autonomy_reports.aios_reduction_target_selector import (
    build_reduction_target_selector,
    summarize_reduction_target_selector,
    validate_reduction_target_selector,
)
from automation.orchestration.runtime_closure.aios_human_gate_execution_readiness_packet import (
    build_human_gate_execution_readiness_packet,
    summarize_human_gate_execution_readiness_packet,
    validate_human_gate_execution_readiness_packet,
)
from automation.orchestration.runtime_closure.aios_human_gate_packet_dogfood_runner import (
    REPORT_JSON_NAME as DOGFOOD_REPORT_JSON_NAME,
    REPORT_MD_NAME as DOGFOOD_REPORT_MD_NAME,
)
from automation.orchestration.runtime_closure.aios_runtime_proof_gate import (
    build_runtime_proof_gate,
    summarize_runtime_proof_gate,
    validate_runtime_proof_gate,
)
from automation.validators.aios_runtime_execution_queue_validator import validate_queue_view


SCHEMA = "AIOS_AUTONOMY_GAP_REASSESSMENT.v1"
MODE = "REASSESSMENT_REPORT"
REASSESSMENT_TYPE = "autonomy_gap"
REPORT_JSON_NAME = "autonomy_gap_reassessment_report.json"
REPORT_MD_NAME = "autonomy_gap_reassessment_summary.md"
DEFAULT_REPORT_SUBDIR = Path("Reports") / "autonomy_gap"
DEFAULT_HUMAN_GATE_REPORT = Path("Reports") / "human_gate" / DOGFOOD_REPORT_JSON_NAME
DEFAULT_HUMAN_GATE_REPORT_MD = Path("Reports") / "human_gate" / DOGFOOD_REPORT_MD_NAME
DEFAULT_QUEUE_VIEW = Path("Reports") / "runtime_queue" / "runtime_execution_queue_view.json"
DEFAULT_QUEUE_VIEW_MD = Path("Reports") / "runtime_queue" / "runtime_execution_queue_view.md"

ALLOWED_REASSESSMENT_STATUSES = {"PASS", "ATTENTION", "BLOCKED", "INVALID"}
FORBIDDEN_STATUSES = {
    "APPROVED",
    "EXECUTE",
    "EXECUTE_NOW",
    "COMPLETE",
    "AUTONOMOUS",
    "VACATION_READY",
    "VACATION_MODE_COMPLETE",
    "SCHEDULER_READY",
    "SOS_READY",
    "LIVE_READY",
    "LIVE_TRADING_READY",
}
UNSAFE_BOOL_KEYS = {
    "approval_granted",
    "apply_allowed",
    "archive_executed",
    "credentials_accessed",
    "delete_executed",
    "dispatch_allowed",
    "execution_allowed",
    "live_trading_allowed",
    "queue_mutation_allowed",
    "queue_mutated",
    "restart_executed",
    "runtime_launch_allowed",
    "runtime_launched",
    "runtime_mutation_allowed",
    "scheduler_creation_allowed",
    "service_creation_allowed",
    "soak_executed",
    "sos_allowed",
    "telemetry_mutation_allowed",
    "timeout_executed",
    "truncate_executed",
    "unsafe_autonomy_claim",
    "vacation_mode_complete",
    "rotation_executed",
}

DEFAULT_POLICY = {
    "require_dogfood_report": True,
    "require_runtime_queue_view": True,
    "require_runtime_proof_gate": True,
    "require_human_gate_packet": True,
    "require_operator_dependency_ledger": True,
    "require_reduction_target_selector": True,
    "block_on_queue_validation_block": True,
    "block_on_packet_block": True,
    "block_on_runtime_gate_block": True,
    "block_on_live_readiness": True,
    "allow_operator_control_design": True,
}

SECRET_PATTERNS = [
    "secret" + "=",
    "token" + "=",
    "pass" + "word" + "=",
    "api" + "_key" + "=",
    "api" + "key" + "=",
    "bear" + "er ",
    "sk" + "-",
]

COMMAND_PREFIXES = (
    "git ",
    "python ",
    "gh ",
    "powershell ",
    "pwsh ",
    "cmd ",
    "bash ",
    "sh ",
    "curl ",
    "wget ",
    "npm ",
    "pip ",
    "pytest ",
    "make ",
)


def _now(now: str | None = None) -> str:
    if now:
        return now
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _deepcopy(value: Any) -> Any:
    return copy.deepcopy(value)


def _ensure_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _load_json(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None
    return data if isinstance(data, dict) else None


def _load_text(path: Path) -> str | None:
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return None


def _walk_strings(value: Any, path: str = "$"):
    if isinstance(value, dict):
        for key, item in value.items():
            yield from _walk_strings(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            yield from _walk_strings(item, f"{path}[{index}]")
    elif isinstance(value, str):
        yield path, value


def _contains_command_string(value: Any) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path, text in _walk_strings(value):
        stripped = text.strip().lower()
        if any(stripped.startswith(prefix) for prefix in COMMAND_PREFIXES):
            findings.append({"path": path, "value": text})
            continue
        if any(sep in text for sep in ("&&", "||", " | ", "$(", "`", ">>", " <", " > ")):
            findings.append({"path": path, "value": text})
    return findings


def _contains_secret_assignment_string(value: Any) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    for path, text in _walk_strings(value):
        lowered = text.lower()
        if any(pattern in lowered for pattern in SECRET_PATTERNS):
            findings.append({"path": path, "value": text})
    return findings


def _source_path(repo_root: Path, relative: str) -> Path:
    return repo_root / relative


def load_default_evidence(repo_root: str | Path = ".", now: str | None = None) -> dict[str, Any]:
    repo_root = Path(repo_root)
    evidence: dict[str, Any] = {
        "repo_state": {
            "repo_root": str(repo_root),
            "generated_at_utc": _now(now),
        },
        "evidence_loaded": {},
        "evidence_missing": [],
    }

    dogfood_report_path = _source_path(repo_root, str(DEFAULT_HUMAN_GATE_REPORT))
    dogfood_md_path = _source_path(repo_root, str(DEFAULT_HUMAN_GATE_REPORT_MD))
    queue_view_path = _source_path(repo_root, str(DEFAULT_QUEUE_VIEW))
    queue_view_md_path = _source_path(repo_root, str(DEFAULT_QUEUE_VIEW_MD))

    dogfood_report = _load_json(dogfood_report_path)
    if dogfood_report is not None:
        evidence["dogfood_report"] = dogfood_report
        evidence["evidence_loaded"]["dogfood_report"] = {
            "path": str(dogfood_report_path),
            "loaded": True,
        }
        for key in (
            "human_gate_packet_summary",
            "runtime_proof_gate_summary",
            "queue_validation_summary",
            "canonical_queue_summary",
            "operator_dependency_summary",
            "reduction_target_summary",
            "runtime_queue_summary",
            "relay_processor_summary",
            "relay_review_summary",
            "restart_timeouts_summary",
            "retention_rotation_summary",
            "soak_summary",
            "packet_validation_summary",
            "validation",
        ):
            if isinstance(dogfood_report.get(key), dict):
                evidence[key] = dogfood_report[key]
                evidence["evidence_loaded"][key] = {"source": "dogfood_report", "loaded": True}
    else:
        evidence["evidence_missing"].append(str(dogfood_report_path))
        evidence["evidence_loaded"]["dogfood_report"] = {"path": str(dogfood_report_path), "loaded": False}

    dogfood_md = _load_text(dogfood_md_path)
    evidence["evidence_loaded"]["dogfood_report_md"] = {
        "path": str(dogfood_md_path),
        "loaded": dogfood_md is not None,
    }
    if dogfood_md is None:
        evidence["evidence_missing"].append(str(dogfood_md_path))

    queue_view = _load_json(queue_view_path)
    if queue_view is not None:
        evidence["runtime_queue_view"] = queue_view
        evidence["evidence_loaded"]["runtime_queue_view"] = {"path": str(queue_view_path), "loaded": True}
    else:
        evidence["evidence_missing"].append(str(queue_view_path))
        evidence["evidence_loaded"]["runtime_queue_view"] = {"path": str(queue_view_path), "loaded": False}

    queue_view_md = _load_text(queue_view_md_path)
    evidence["evidence_loaded"]["runtime_queue_view_md"] = {
        "path": str(queue_view_md_path),
        "loaded": queue_view_md is not None,
    }
    if queue_view_md is None:
        evidence["evidence_missing"].append(str(queue_view_md_path))

    if "operator_dependency_ledger" not in evidence:
        evidence["operator_dependency_ledger"] = build_operator_dependency_ledger(now=_now(now))
        evidence["evidence_loaded"]["operator_dependency_ledger"] = {"source": "builder", "loaded": True}
    if "reduction_target_selector" not in evidence:
        evidence["reduction_target_selector"] = build_reduction_target_selector(now=_now(now))
        evidence["evidence_loaded"]["reduction_target_selector"] = {"source": "builder", "loaded": True}
    if "runtime_proof_gate_summary" not in evidence:
        gate = build_runtime_proof_gate(now=_now(now))
        evidence["runtime_proof_gate_summary"] = summarize_runtime_proof_gate(gate)
        evidence["evidence_loaded"]["runtime_proof_gate_summary"] = {"source": "builder", "loaded": True}
    if "human_gate_packet_summary" not in evidence:
        packet = build_human_gate_execution_readiness_packet(
            runtime_proof_gate=build_runtime_proof_gate(now=_now(now)),
            canonical_runtime_queue_view=queue_view or {"schema": "AIOS_RUNTIME_EXECUTION_QUEUE.v1", "items": []},
            runtime_queue_validation=validate_queue_view(queue_view or {"schema": "AIOS_RUNTIME_EXECUTION_QUEUE.v1", "items": []}),
            operator_dependency_ledger=evidence["operator_dependency_ledger"],
            reduction_target_selector=evidence["reduction_target_selector"],
            now=_now(now),
        )
        evidence["human_gate_packet_summary"] = summarize_human_gate_execution_readiness_packet(packet)
        evidence["evidence_loaded"]["human_gate_packet_summary"] = {"source": "builder", "loaded": True}

    return evidence


def _score_from_impact(impact_score: int) -> str:
    if impact_score >= 100:
        return "CRITICAL"
    if impact_score >= 85:
        return "HIGH"
    if impact_score >= 50:
        return "MEDIUM"
    return "LOW"


def _gap(
    *,
    gap_id: str,
    title: str,
    domain: str,
    impact_score: int,
    source: str,
    evidence: Any,
    why_it_matters: str,
    next_safe_lane: str,
    blocked_until: str,
    forbidden_shortcut: str,
    reduces_operator_burden: bool,
    burden_category: str,
    approval_required: bool = False,
) -> dict[str, Any]:
    return {
        "id": gap_id,
        "title": title,
        "domain": domain,
        "severity": _score_from_impact(impact_score),
        "impact_score": int(impact_score),
        "source": source,
        "evidence": evidence,
        "why_it_matters": why_it_matters,
        "next_safe_lane": next_safe_lane,
        "blocked_until": blocked_until,
        "forbidden_shortcut": forbidden_shortcut,
        "reduces_operator_burden": bool(reduces_operator_burden),
        "burden_category": burden_category,
        "approval_required": bool(approval_required),
        "execution_allowed": False,
    }


def _scorecard_item(status: str, reason: str, evidence: Any, next_safe_lane: str) -> dict[str, Any]:
    return {
        "status": status,
        "reason": reason,
        "evidence": evidence,
        "next_safe_lane": next_safe_lane,
    }


def _maybe_section(source: dict[str, Any], key: str) -> dict[str, Any]:
    return _ensure_dict(source.get(key))


def _queue_validation_status(queue_validation: dict[str, Any]) -> str:
    status = str(queue_validation.get("queue_validation_status") or queue_validation.get("status") or "").upper()
    if status in {"PASS", "BLOCK", "ATTENTION", "INVALID"}:
        return status
    return "INVALID" if queue_validation else "BLOCKED"


def _readiness_status_from_text(value: Any, *, ready_token: str) -> str:
    if not isinstance(value, dict):
        return "BLOCKED"
    status = str(value.get("status") or value.get("packet_status") or value.get("final_verdict") or value.get("proof_status") or "").upper()
    if status == ready_token:
        return "READY"
    if status in {"ATTENTION", "REVIEWABLE", "PASS", "READY_FOR_HUMAN_GATE", "READY_FOR_HUMAN_REVIEW"}:
        if ready_token in {"READY", "ATTENTION"}:
            return "ATTENTION" if status != ready_token else ready_token
        return "ATTENTION"
    if status in {"BLOCK", "BLOCKED", "INVALID"}:
        return "BLOCKED" if status != "INVALID" else "INVALID"
    if status in {"READY", "READY_FOR_HUMAN_GATE", "READY_FOR_HUMAN_REVIEW"}:
        return "READY"
    return "BLOCKED"


def _compare_runtime_queue_views(dogfood_report: dict[str, Any], runtime_queue_view: dict[str, Any]) -> dict[str, Any]:
    canonical = _maybe_section(dogfood_report, "canonical_queue_summary")
    report_count = canonical.get("canonical_queue_item_count")
    queue_count = runtime_queue_view.get("item_count")
    mismatch = isinstance(report_count, int) and isinstance(queue_count, int) and report_count != queue_count
    return {
        "report_item_count": report_count,
        "queue_view_item_count": queue_count,
        "mismatch": mismatch,
        "source_map": runtime_queue_view.get("source_map") if isinstance(runtime_queue_view.get("source_map"), dict) else {},
        "sources_missing": list(runtime_queue_view.get("sources_missing") or []),
        "sources_read": list(runtime_queue_view.get("sources_read") or []),
    }


def _readiness_scorecard(
    *,
    dogfood_report: dict[str, Any],
    runtime_queue_view: dict[str, Any],
    queue_validation: dict[str, Any],
    runtime_proof_gate_summary: dict[str, Any],
    human_gate_packet_summary: dict[str, Any],
    operator_dependency_summary: dict[str, Any],
    reduction_target_summary: dict[str, Any],
) -> dict[str, Any]:
    canonical = _maybe_section(dogfood_report, "canonical_queue_summary")
    canonical_count = canonical.get("canonical_queue_item_count")
    queue_mismatch = _compare_runtime_queue_views(dogfood_report, runtime_queue_view).get("mismatch", False)

    canonical_status = "READY"
    canonical_evidence = {
        "canonical_queue_item_count": canonical_count,
        "protected_item_count": canonical.get("canonical_queue_protected_item_count"),
        "duplicate_id_count": canonical.get("canonical_queue_duplicate_id_count"),
        "unknown_state_count": canonical.get("canonical_queue_unknown_state_count"),
        "queue_view_mismatch": queue_mismatch,
    }
    if queue_mismatch or int(canonical.get("canonical_queue_protected_item_count") or 0) > 0:
        canonical_status = "ATTENTION"
    if not canonical and not runtime_queue_view:
        canonical_status = "BLOCKED"

    queue_status = _queue_validation_status(queue_validation)
    if queue_status == "PASS":
        queue_score = "READY"
    elif queue_status == "ATTENTION":
        queue_score = "ATTENTION"
    elif queue_status == "INVALID":
        queue_score = "INVALID"
    else:
        queue_score = "BLOCKED"

    proof_verdict = str(runtime_proof_gate_summary.get("final_verdict") or "").upper()
    if proof_verdict == "READY_FOR_HUMAN_GATE":
        proof_status = "READY"
    elif proof_verdict == "ATTENTION":
        proof_status = "ATTENTION"
    elif proof_verdict == "INVALID":
        proof_status = "INVALID"
    else:
        proof_status = "BLOCKED"

    packet_status = str(human_gate_packet_summary.get("packet_status") or "").upper()
    if packet_status == "READY_FOR_HUMAN_REVIEW":
        packet_score = "READY"
    elif packet_status == "ATTENTION":
        packet_score = "ATTENTION"
    elif packet_status == "INVALID":
        packet_score = "INVALID"
    else:
        packet_score = "BLOCKED"

    dogfood_status = str(dogfood_report.get("dogfood_status") or "").upper()
    dogfood_ready = "READY" if dogfood_status in {"PASS", "ATTENTION"} and not int(dogfood_report.get("mutated_source_count") or 0) else "ATTENTION"
    if dogfood_status == "BLOCKED":
        dogfood_ready = "ATTENTION"

    reduced_count = len(_ensure_dict(operator_dependency_summary).get("reduced_burdens") or [])
    human_burden_level = "HIGH" if int(_ensure_dict(operator_dependency_summary).get("remaining_human_burdens", []) and len(operator_dependency_summary.get("remaining_human_burdens") or [])) else "LOW"
    operator_reduced = "ATTENTION" if str(operator_dependency_summary.get("autonomy_shift") or "").upper() == "PARTIAL" else "BLOCKED"

    p2_ready = "BLOCKED"
    if queue_score == "READY" and packet_score == "READY" and proof_status == "READY":
        p2_ready = "ATTENTION"

    control_switch_ready = "ATTENTION" if dogfood_status in {"BLOCKED", "ATTENTION"} else "READY"
    if queue_score == "BLOCKED" or packet_score == "BLOCKED" or proof_status == "BLOCKED":
        control_switch_ready = "ATTENTION"
    if dogfood_status == "BLOCKED":
        control_switch_ready = "ATTENTION"

    scheduler_ready = "BLOCKED"
    sos_ready = "BLOCKED"
    live_execution_ready = "BLOCKED"
    vacation_mode_ready = "BLOCKED"

    return {
        "canonical_queue_ready": _scorecard_item(
            canonical_status,
            (
                "Canonical queue exists, but the queue view and dogfood summary are not fully aligned and the protected item keeps the queue in review mode."
                if canonical_status == "ATTENTION"
                else "Canonical queue is not yet stable enough for downstream use."
            ),
            canonical_evidence,
            "QUEUE_BLOCKER_TRIAGE_V1",
        ),
        "queue_validation_ready": _scorecard_item(
            queue_score,
            (
                "Queue validation is BLOCK, so the canonical queue still carries a protected item and cannot be treated as ready."
                if queue_score == "BLOCKED"
                else "Queue validation is not yet a clean PASS."
            ),
            queue_validation,
            "PROTECTED_QUEUE_ITEM_REVIEW_V1",
        ),
        "runtime_proof_gate_ready": _scorecard_item(
            proof_status,
            (
                "Runtime proof gate is BLOCKED, so the proof spine is not yet ready for human gate review."
                if proof_status == "BLOCKED"
                else "Runtime proof gate still needs review."
            ),
            runtime_proof_gate_summary,
            "RUNTIME_PROOF_GATE_BLOCKER_TRIAGE_V1",
        ),
        "human_gate_packet_ready": _scorecard_item(
            packet_score,
            (
                "Human gate packet is BLOCKED because the proof gate and queue validation are blocked."
                if packet_score == "BLOCKED"
                else "Human gate packet still carries blockers or attention."
            ),
            human_gate_packet_summary,
            "HUMAN_GATE_BLOCKER_EXPLAINER_V1",
        ),
        "dogfood_runner_ready": _scorecard_item(
            "READY" if dogfood_ready == "READY" else "ATTENTION",
            "Dogfood runner produced evidence safely and left mutation blocked."
            if dogfood_ready == "READY"
            else "Dogfood runner is safe, but the evidence it produced is blocked.",
            {
                "dogfood_status": dogfood_status,
                "mutation_check_status": dogfood_report.get("mutation_check_status"),
                "mutated_source_count": dogfood_report.get("mutated_source_count"),
            },
            "HUMAN_GATE_BLOCKER_EXPLAINER_V1",
        ),
        "operator_dependency_reduced": _scorecard_item(
            operator_reduced,
            "Operator dependency tracking shows a partial autonomy shift, but manual burdens remain."
            if operator_reduced == "ATTENTION"
            else "Operator dependency reduction has not yet moved far enough.",
            {
                "autonomy_shift": operator_dependency_summary.get("autonomy_shift"),
                "remaining_human_burdens": list(operator_dependency_summary.get("remaining_human_burdens") or []),
                "reduced_burdens": list(operator_dependency_summary.get("reduced_burdens") or []),
            },
            "OPERATOR_DEPENDENCY_LEDGER_REVIEW_V1",
        ),
        "p2_enqueue_bridge_ready": _scorecard_item(
            p2_ready,
            "P2 review-to-queue enqueue bridge is blocked until queue validation and human gate readiness clear."
            if p2_ready == "BLOCKED"
            else "P2 enqueue bridge could only be discussed after the proof chain is clean."
            if p2_ready == "ATTENTION"
            else "P2 enqueue bridge is not ready.",
            {
                "queue_validation_status": queue_score,
                "runtime_proof_gate_verdict": proof_verdict,
                "human_gate_packet_status": packet_status,
            },
            "QUEUE_BLOCKER_TRIAGE_V1",
        ),
        "operator_control_switch_ready": _scorecard_item(
            control_switch_ready,
            "A report-only operator control switch is worth designing later, but live control is not ready."
            if control_switch_ready == "ATTENTION"
            else "Operator control switch is not ready.",
            {
                "recommended_scope": "REPORT_ONLY / OBSERVE_ONLY",
                "blocked_by": [
                    "queue_validation_block",
                    "human_gate_packet_blocked",
                    "runtime_proof_gate_blocked",
                ],
            },
            "HUMAN_GATE_BLOCKER_EXPLAINER_V1",
        ),
        "scheduler_ready": _scorecard_item(
            scheduler_ready,
            "Scheduler creation stays blocked until the proof chain clears.",
            {"scheduler_creation_allowed": False},
            "REPORT_ONLY",
        ),
        "sos_ready": _scorecard_item(
            sos_ready,
            "SOS arming stays blocked until the human gate packet is reviewable.",
            {"sos_allowed": False},
            "REPORT_ONLY",
        ),
        "live_execution_ready": _scorecard_item(
            live_execution_ready,
            "Live execution remains blocked because queue validation, proof gate, and human gate are not ready.",
            {
                "queue_validation_status": queue_score,
                "runtime_proof_gate_verdict": proof_verdict,
                "packet_status": packet_status,
            },
            "QUEUE_BLOCKER_TRIAGE_V1",
        ),
        "vacation_mode_ready": _scorecard_item(
            vacation_mode_ready,
            "Vacation mode remains false and must stay blocked until the evidence chain is clean.",
            {"vacation_mode_complete": False},
            "REPORT_ONLY",
        ),
    }


def _burden_section(
    *,
    category: str,
    level: str,
    evidence: list[str],
    already_reduced: list[str],
    remains_manual: list[str],
    next_safe_lane: str,
) -> dict[str, Any]:
    return {
        "current_level": level,
        "evidence": evidence,
        "already_reduced": already_reduced,
        "remains_manual": remains_manual,
        "next_safe_lane": next_safe_lane,
        "burden_category": category,
    }


def _build_gap_items(
    *,
    dogfood_report: dict[str, Any],
    runtime_queue_view: dict[str, Any],
    queue_validation: dict[str, Any],
    runtime_proof_gate_summary: dict[str, Any],
    human_gate_packet_summary: dict[str, Any],
    operator_dependency_summary: dict[str, Any],
    reduction_target_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    canonical = _maybe_section(dogfood_report, "canonical_queue_summary")
    queue_compare = _compare_runtime_queue_views(dogfood_report, runtime_queue_view)
    queue_validation_status = _queue_validation_status(queue_validation)
    proof_verdict = str(runtime_proof_gate_summary.get("final_verdict") or "").upper()
    packet_status = str(human_gate_packet_summary.get("packet_status") or "").upper()
    dogfood_status = str(dogfood_report.get("dogfood_status") or "").upper()
    protected_count = int(canonical.get("canonical_queue_protected_item_count") or 0)

    if queue_compare.get("mismatch") or protected_count > 0 or queue_validation_status == "BLOCK":
        gaps.append(
            _gap(
                gap_id="live_execution_gap",
                title="Live execution remains unavailable",
                domain="live_execution_gap",
                impact_score=100,
                source="Reports/human_gate/human_gate_packet_dogfood_report.json and Reports/runtime_queue/runtime_execution_queue_view.json",
                evidence={
                    "queue_validation_status": queue_validation_status,
                    "runtime_proof_gate_verdict": proof_verdict,
                    "packet_status": packet_status,
                    "dogfood_status": dogfood_status,
                    "canonical_queue_item_count": canonical.get("canonical_queue_item_count"),
                    "queue_view_item_count": queue_compare.get("queue_view_item_count"),
                },
                why_it_matters="AI_OS cannot move past observe-only proof into live execution while the queue, proof gate, and human gate are still blocked.",
                next_safe_lane="QUEUE_BLOCKER_TRIAGE_V1",
                blocked_until=(
                    "Queue validation passes, the human gate packet becomes READY_FOR_HUMAN_REVIEW, the runtime proof gate becomes READY_FOR_HUMAN_GATE, and scheduler/SOS/live paths remain blocked until reviewed."
                ),
                forbidden_shortcut="Do not infer live readiness from report generation or from partial proof coverage.",
                reduces_operator_burden=True,
                burden_category="decide",
            )
        )

    if queue_validation_status == "BLOCK" or protected_count > 0:
        gaps.append(
            _gap(
                gap_id="queue_integrity_gap",
                title="Canonical queue integrity still fails the validator",
                domain="queue_integrity_gap",
                impact_score=95,
                source="Reports/human_gate/human_gate_packet_dogfood_report.json#queue_validation_summary",
                evidence={
                    "queue_validation_status": queue_validation_status,
                    "queue_validation_blockers": list(queue_validation.get("queue_validation_blockers") or queue_validation.get("blocking_findings") or []),
                    "protected_item_count": protected_count,
                    "duplicate_id_count": canonical.get("canonical_queue_duplicate_id_count"),
                    "unknown_state_count": canonical.get("canonical_queue_unknown_state_count"),
                    "canonical_queue_fail_soft_errors": list(canonical.get("canonical_queue_fail_soft_errors") or []),
                },
                why_it_matters="A protected queue item and validator BLOCK mean the canonical queue still needs human review before anything downstream can treat it as trustworthy.",
                next_safe_lane="PROTECTED_QUEUE_ITEM_REVIEW_V1",
                blocked_until="Queue validation is PASS and the protected item is explained or resolved without mutating the source queue.",
                forbidden_shortcut="Do not remove or mutate queue evidence to make the validator pass.",
                reduces_operator_burden=True,
                burden_category="route",
            )
        )

    if proof_verdict == "BLOCKED":
        gaps.append(
            _gap(
                gap_id="proof_gate_gap",
                title="Runtime proof gate remains blocked",
                domain="proof_gate_gap",
                impact_score=90,
                source="Reports/human_gate/human_gate_packet_dogfood_report.json#runtime_proof_gate_summary",
                evidence={
                    "final_verdict": proof_verdict,
                    "blocker_count": runtime_proof_gate_summary.get("blocker_count"),
                    "attention_count": runtime_proof_gate_summary.get("attention_count"),
                    "safe_next_action": runtime_proof_gate_summary.get("safe_next_action"),
                },
                why_it_matters="The proof spine cannot yet support a human gate readiness claim while the runtime proof gate is blocked.",
                next_safe_lane="RUNTIME_PROOF_GATE_BLOCKER_TRIAGE_V1",
                blocked_until="Runtime proof gate reaches READY_FOR_HUMAN_GATE with no unsafe claims or forbidden statuses.",
                forbidden_shortcut="Do not promote a blocked proof gate into a readiness claim.",
                reduces_operator_burden=True,
                burden_category="recover",
            )
        )

    if packet_status == "BLOCKED":
        gaps.append(
            _gap(
                gap_id="human_gate_gap",
                title="Human gate packet remains blocked",
                domain="human_gate_gap",
                impact_score=90,
                source="Reports/human_gate/human_gate_packet_dogfood_report.json#human_gate_packet_summary",
                evidence={
                    "packet_status": packet_status,
                    "queue_validation_status": queue_validation_status,
                    "runtime_proof_gate_verdict": proof_verdict,
                    "human_review_question_count": human_gate_packet_summary.get("human_review_question_count"),
                    "human_stop_condition_count": human_gate_packet_summary.get("human_stop_condition_count"),
                },
                why_it_matters="Tony still has to review blockers rather than a readiness packet, so the human gate is not yet at the review-only threshold.",
                next_safe_lane="HUMAN_GATE_BLOCKER_EXPLAINER_V1",
                blocked_until="The packet becomes READY_FOR_HUMAN_REVIEW or at least ATTENTION without blockers.",
                forbidden_shortcut="Do not approve or execute from a blocked packet.",
                reduces_operator_burden=True,
                burden_category="decide",
            )
        )

    if str(operator_dependency_summary.get("autonomy_shift") or "").upper() == "PARTIAL":
        gaps.append(
            _gap(
                gap_id="operator_dependency_gap",
                title="Operator dependency is still partially manual",
                domain="operator_dependency_gap",
                impact_score=75,
                source="Reports/human_gate/human_gate_packet_dogfood_report.json#operator_dependency_summary",
                evidence={
                    "autonomy_shift": operator_dependency_summary.get("autonomy_shift"),
                    "remaining_human_burdens": list(operator_dependency_summary.get("remaining_human_burdens") or []),
                    "next_reduction_target": _ensure_dict(operator_dependency_summary.get("next_reduction_target")),
                },
                why_it_matters="AI_OS has reduced some queue and proof burden, but Tony still has to remember and recover from upstream relay proof bottlenecks.",
                next_safe_lane="OPERATOR_DEPENDENCY_LEDGER_REVIEW_V1",
                blocked_until="Remaining human burdens are reduced further and the next dependency target is unambiguous.",
                forbidden_shortcut="Do not treat partial autonomy shift as full autonomy.",
                reduces_operator_burden=True,
                burden_category="remember",
            )
        )

    selected_target = str(reduction_target_summary.get("selected_target") or "")
    next_target = _ensure_dict(_ensure_dict(operator_dependency_summary).get("next_reduction_target"))
    next_target_id = str(next_target.get("component_id") or "")
    if selected_target and selected_target != "relay_proof_acceptance_packet":
        gaps.append(
            _gap(
                gap_id="reduction_target_gap",
                title="Reduction target selector still points to a planning lane",
                domain="reduction_target_gap",
                impact_score=70,
                source="Reports/human_gate/human_gate_packet_dogfood_report.json#reduction_target_summary",
                evidence={
                    "selected_target": selected_target,
                    "selected_category": reduction_target_summary.get("selected_category"),
                    "selected_reason": reduction_target_summary.get("selected_reason"),
                    "safe_next_action_from_selector": reduction_target_summary.get("safe_next_action_from_selector"),
                },
                why_it_matters="The selector is still pointing at planning rather than the relay acceptance packet, so Tony must still decide which reduction lane to use next.",
                next_safe_lane="REDUCTION_TARGET_SELECTOR_REVIEW_V1",
                blocked_until="The selector converges on the right proof-to-review target and the upstream blockers are described cleanly.",
                forbidden_shortcut="Do not claim the next lane is execution or live control.",
                reduces_operator_burden=True,
                burden_category="route",
            )
        )

    if queue_compare.get("mismatch") or (next_target_id and next_target_id != selected_target):
        gaps.append(
            _gap(
                gap_id="documentation_gap",
                title="Evidence views still need alignment",
                domain="documentation_gap",
                impact_score=35,
                source="Reports/human_gate/human_gate_packet_dogfood_report.json and Reports/runtime_queue/runtime_execution_queue_view.json",
                evidence={
                    "runtime_queue_view_item_count": queue_compare.get("queue_view_item_count"),
                    "canonical_queue_item_count": queue_compare.get("report_item_count"),
                    "operator_dependency_next_target": next_target_id,
                    "reduction_selector_target": selected_target,
                },
                why_it_matters="The evidence story is split across views and the next dependency target is not yet perfectly aligned between the ledger and selector.",
                next_safe_lane="HUMAN_GATE_BLOCKER_EXPLAINER_V1",
                blocked_until="The evidence views are aligned and the next reduction target is clearly explained.",
                forbidden_shortcut="Do not paper over evidence mismatches by editing the reports to agree.",
                reduces_operator_burden=True,
                burden_category="notice",
            )
        )

    if not queue_compare.get("mismatch") and not queue_validation_status and not dogfood_report:
        gaps.append(
            _gap(
                gap_id="evidence_gap",
                title="Required evidence is missing",
                domain="evidence_gap",
                impact_score=25,
                source="Reassessment evidence bundle",
                evidence={"missing": ["dogfood_report", "runtime_queue_view"]},
                why_it_matters="When the source evidence is absent, Tony has to remember too much and the report cannot infer readiness.",
                next_safe_lane="EVIDENCE_LOADING_REPAIR_V1",
                blocked_until="The missing evidence is present or explicitly marked unavailable.",
                forbidden_shortcut="Do not guess the missing evidence.",
                reduces_operator_burden=True,
                burden_category="remember",
            )
        )

    return gaps


def _rank_gaps(gaps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ordered = sorted(gaps, key=lambda gap: (-int(gap.get("impact_score") or 0), str(gap.get("id") or "")))
    ranked: list[dict[str, Any]] = []
    for index, gap in enumerate(ordered, start=1):
        ranked.append(
            {
                "rank": index,
                "id": gap.get("id"),
                "title": gap.get("title"),
                "domain": gap.get("domain"),
                "severity": gap.get("severity"),
                "impact_score": gap.get("impact_score"),
                "source": gap.get("source"),
            }
        )
    return ranked


def _burden_summary(
    *,
    operator_dependency_summary: dict[str, Any],
    reduction_target_summary: dict[str, Any],
    dogfood_report: dict[str, Any],
    queue_validation: dict[str, Any],
    runtime_proof_gate_summary: dict[str, Any],
    human_gate_packet_summary: dict[str, Any],
) -> dict[str, Any]:
    dogfood_status = str(dogfood_report.get("dogfood_status") or "").upper()
    packet_status = str(human_gate_packet_summary.get("packet_status") or "").upper()
    queue_validation_status = _queue_validation_status(queue_validation)
    proof_verdict = str(runtime_proof_gate_summary.get("final_verdict") or "").upper()
    selected_target = str(reduction_target_summary.get("selected_target") or "")
    next_target = _ensure_dict(_ensure_dict(operator_dependency_summary).get("next_reduction_target"))
    next_target_name = str(next_target.get("component_name") or "Relay dry-run proof review")

    remember = _burden_section(
        category="remember",
        level="HIGH",
        evidence=[
            f"dogfood_status={dogfood_status or 'UNKNOWN'}",
            f"packet_status={packet_status or 'UNKNOWN'}",
            f"queue_validation_status={queue_validation_status}",
        ],
        already_reduced=[
            "The dogfood runner now writes a ranked evidence bundle.",
            "The human gate packet and proof gate are both machine-readable.",
        ],
        remains_manual=[
            "Tony still has to remember that the queue is blocked until the protected item is reviewed.",
            "Tony still has to remember the next blocker from the proof chain summary.",
        ],
        next_safe_lane="QUEUE_BLOCKER_TRIAGE_V1",
    )

    notice = _burden_section(
        category="notice",
        level="MEDIUM",
        evidence=[
            f"canonical_queue_protected_item_count={_maybe_section(dogfood_report, 'canonical_queue_summary').get('canonical_queue_protected_item_count', 0)}",
            f"queue_validation_blockers={list(queue_validation.get('queue_validation_blockers') or [])}",
        ],
        already_reduced=[
            "Canonical queue and dogfood reports now surface the protected item and fail-soft warning.",
            "A single reassessment report now collates the queue, proof, and packet state.",
        ],
        remains_manual=[
            "Tony still has to notice the protected queue item and the queue validation blocker.",
            "Tony still has to notice whether the evidence views are aligned.",
        ],
        next_safe_lane="PROTECTED_QUEUE_ITEM_REVIEW_V1",
    )

    decide = _burden_section(
        category="decide",
        level="HIGH",
        evidence=[
            f"runtime_proof_gate_verdict={proof_verdict or 'UNKNOWN'}",
            f"packet_status={packet_status or 'UNKNOWN'}",
        ],
        already_reduced=[
            "The packet and dogfood runner now tell Tony whether the chain is ready, attention-only, or blocked.",
            "The report ranks the blocker impact so Tony does not have to do that mentally.",
        ],
        remains_manual=[
            "Tony still has to decide which report-only lane to open next.",
            "Tony still has to decide that live execution remains blocked.",
        ],
        next_safe_lane="HUMAN_GATE_BLOCKER_EXPLAINER_V1",
    )

    route = _burden_section(
        category="route",
        level="MEDIUM",
        evidence=[
            f"selected_target={selected_target or 'UNKNOWN'}",
            f"next_reduction_target={next_target_name}",
        ],
        already_reduced=[
            "The reduction selector already proposes a next safe lane.",
            "The reassessment report now maps blockers to next lanes.",
        ],
        remains_manual=[
            "Tony still has to route the work to the next report-only lane.",
            "Tony still has to keep P2, scheduler, SOS, and live paths out of scope.",
        ],
        next_safe_lane="REDUCTION_TARGET_SELECTOR_REVIEW_V1",
    )

    recover = _burden_section(
        category="recover",
        level="HIGH",
        evidence=[
            f"operator_dependency_autonomy_shift={operator_dependency_summary.get('autonomy_shift')}",
            f"next_dependency_target={next_target_name}",
        ],
        already_reduced=[
            "The operator dependency ledger already identifies the remaining manual burden categories.",
            "The reassessment report collapses multiple evidence files into one ranked action map.",
        ],
        remains_manual=[
            "Tony still has to recover from the relay proof bottleneck before any readiness claim improves.",
            "Tony still has to recover from blocked queue validation before a P2 bridge can be discussed.",
        ],
        next_safe_lane="RUNTIME_PROOF_GATE_BLOCKER_TRIAGE_V1",
    )

    return {
        "remember_burden": remember,
        "notice_burden": notice,
        "decide_burden": decide,
        "route_burden": route,
        "recover_burden": recover,
    }


def _recommended_next_lanes(all_gaps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    lanes: list[dict[str, Any]] = []
    lane_defs = [
        ("QUEUE_BLOCKER_TRIAGE_V1", "Triaging the queue validator blocker and protected item", "Resolve the queue integrity blocker without mutating the source queue.", "queue_integrity_gap", "REPORT_ONLY"),
        ("PROTECTED_QUEUE_ITEM_REVIEW_V1", "Reviewing the protected queue item", "Explain why the protected item is present and whether it needs human review.", "queue_integrity_gap", "OBSERVE_ONLY"),
        ("HUMAN_GATE_BLOCKER_EXPLAINER_V1", "Explaining the human gate blockers", "Collapse the blocked proof and packet state into one human-readable explanation.", "human_gate_gap", "REPORT_ONLY"),
        ("RUNTIME_PROOF_GATE_BLOCKER_TRIAGE_V1", "Triage the runtime proof gate blocker", "Summarize what keeps the proof gate blocked and what is still missing.", "proof_gate_gap", "DRY_RUN_ONLY"),
        ("REDUCTION_TARGET_SELECTOR_REVIEW_V1", "Review the reduction target selector", "Align the next reduction target with the current proof chain state.", "reduction_target_gap", "REPORT_ONLY"),
        ("OPERATOR_DEPENDENCY_LEDGER_REVIEW_V1", "Review operator dependency burden", "Reduce the remember/notice/decide/route/recover burden in one place.", "operator_dependency_gap", "REPORT_ONLY"),
    ]
    gap_ids = {gap.get("domain") for gap in all_gaps}
    for lane_id, title, purpose, blocked_by, mode in lane_defs:
        if blocked_by not in gap_ids and lane_id not in {"QUEUE_BLOCKER_TRIAGE_V1", "HUMAN_GATE_BLOCKER_EXPLAINER_V1"}:
            continue
        lanes.append(
            {
                "lane_id": lane_id,
                "title": title,
                "purpose": purpose,
                "why_now": "This lane reduces the largest current blocker without touching execution paths.",
                "blocked_by": blocked_by,
                "allowed_scope": "Report-only / observe-only",
                "forbidden_scope": "No approval, no runtime launch, no dispatch, no queue mutation, no scheduler/SOS/live operations.",
                "expected_output": "A clearer blocker map and a smaller Tony review burden.",
                "reduces_operator_burden_category": "remember",
                "recommended_mode": mode,
                "readiness_to_start": "READY" if lane_id in {"QUEUE_BLOCKER_TRIAGE_V1", "PROTECTED_QUEUE_ITEM_REVIEW_V1", "HUMAN_GATE_BLOCKER_EXPLAINER_V1"} else "ATTENTION",
            }
        )
    return lanes


def _not_ready_lanes(
    *,
    queue_validation_status: str,
    human_gate_packet_status: str,
    runtime_proof_gate_verdict: str,
) -> list[dict[str, Any]]:
    return [
        {
            "lane_id": "P2_REVIEW_TO_QUEUE_ENQUEUE_BRIDGE_V1",
            "status": "BLOCKED",
            "reason": "Queue validation is BLOCK and the human gate packet is BLOCKED, so there is no safe enqueue bridge yet.",
            "blocked_by": [queue_validation_status, human_gate_packet_status, runtime_proof_gate_verdict],
            "forbidden_scope": "No real enqueue, dequeue, dispatch, or queue mutation.",
        },
        {
            "lane_id": "OPERATOR_CONTROL_MODE_SWITCH_V1",
            "status": "ATTENTION",
            "reason": "A report-only or observe-only switch may be worth designing later, but live control is not ready.",
            "blocked_by": [queue_validation_status, human_gate_packet_status, runtime_proof_gate_verdict],
            "forbidden_scope": "No live control, no runtime toggle, no approval automation.",
        },
        {
            "lane_id": "SCHEDULER_REGISTRATION_V1",
            "status": "BLOCKED",
            "reason": "Scheduler readiness remains blocked while the proof chain and queue validation are blocked.",
            "blocked_by": [queue_validation_status, human_gate_packet_status, runtime_proof_gate_verdict],
            "forbidden_scope": "No scheduler creation or registration.",
        },
        {
            "lane_id": "SOS_ARMING_V1",
            "status": "BLOCKED",
            "reason": "SOS arming remains blocked while the human gate packet is blocked.",
            "blocked_by": [queue_validation_status, human_gate_packet_status, runtime_proof_gate_verdict],
            "forbidden_scope": "No SOS arming or SOS delivery claims.",
        },
        {
            "lane_id": "LIVE_EXECUTION_V1",
            "status": "BLOCKED",
            "reason": "Live execution remains blocked because queue validation, proof gate, and human gate are not ready.",
            "blocked_by": [queue_validation_status, human_gate_packet_status, runtime_proof_gate_verdict],
            "forbidden_scope": "No live broker, trading, or runtime execution.",
        },
        {
            "lane_id": "VACATION_MODE_COMPLETE_V1",
            "status": "BLOCKED",
            "reason": "Vacation mode complete must remain false until the entire proof chain is clean.",
            "blocked_by": [queue_validation_status, human_gate_packet_status, runtime_proof_gate_verdict],
            "forbidden_scope": "No vacation mode completion claim.",
        },
    ]


def _readiness_section(
    *,
    readiness_scorecard: dict[str, Any],
    all_gaps: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "canonical_queue_ready": readiness_scorecard["canonical_queue_ready"],
        "queue_validation_ready": readiness_scorecard["queue_validation_ready"],
        "runtime_proof_gate_ready": readiness_scorecard["runtime_proof_gate_ready"],
        "human_gate_packet_ready": readiness_scorecard["human_gate_packet_ready"],
        "dogfood_runner_ready": readiness_scorecard["dogfood_runner_ready"],
        "operator_dependency_reduced": readiness_scorecard["operator_dependency_reduced"],
        "p2_enqueue_bridge_ready": readiness_scorecard["p2_enqueue_bridge_ready"],
        "operator_control_switch_ready": readiness_scorecard["operator_control_switch_ready"],
        "scheduler_ready": readiness_scorecard["scheduler_ready"],
        "sos_ready": readiness_scorecard["sos_ready"],
        "live_execution_ready": readiness_scorecard["live_execution_ready"],
        "vacation_mode_ready": readiness_scorecard["vacation_mode_ready"],
        "all_gaps": all_gaps,
    }


def build_autonomy_gap_reassessment_report(
    *,
    repo_root: str | Path = ".",
    evidence: dict[str, Any] | None = None,
    now: str | None = None,
    output_dir: str | Path | None = None,
) -> dict[str, Any]:
    timestamp = _now(now)
    repo_root_path = Path(repo_root)
    output_dir_path = Path(output_dir) if output_dir else repo_root_path / DEFAULT_REPORT_SUBDIR
    loaded = load_default_evidence(repo_root_path, timestamp)
    source_evidence = copy.deepcopy(loaded)
    if evidence:
        source_evidence.update({key: _deepcopy(value) for key, value in evidence.items()})

    dogfood_report = _ensure_dict(source_evidence.get("dogfood_report"))
    if not dogfood_report:
        dogfood_report = _ensure_dict(source_evidence.get("dogfood_report"))
    runtime_queue_view = _ensure_dict(source_evidence.get("runtime_queue_view"))
    queue_validation = _ensure_dict(source_evidence.get("queue_validation_summary")) or _ensure_dict(dogfood_report.get("queue_validation_summary"))
    runtime_proof_gate_summary = _ensure_dict(source_evidence.get("runtime_proof_gate_summary")) or _ensure_dict(dogfood_report.get("runtime_proof_gate_summary"))
    human_gate_packet_summary = _ensure_dict(source_evidence.get("human_gate_packet_summary")) or _ensure_dict(dogfood_report.get("human_gate_packet_summary"))
    operator_dependency_summary = _ensure_dict(source_evidence.get("operator_dependency_summary")) or _ensure_dict(dogfood_report.get("operator_dependency_summary"))
    reduction_target_summary = _ensure_dict(source_evidence.get("reduction_target_summary")) or _ensure_dict(dogfood_report.get("reduction_target_summary"))
    canonical_queue_summary = _ensure_dict(source_evidence.get("canonical_queue_summary")) or _ensure_dict(dogfood_report.get("canonical_queue_summary"))
    runtime_queue_summary = _ensure_dict(source_evidence.get("runtime_queue_summary")) or _ensure_dict(dogfood_report.get("runtime_queue_summary"))

    if not runtime_queue_view and dogfood_report.get("runtime_queue_summary"):
        runtime_queue_view = _ensure_dict(dogfood_report.get("runtime_queue_summary"))

    if not queue_validation and runtime_queue_view:
        queue_validation = validate_queue_view(runtime_queue_view)
    if not runtime_proof_gate_summary:
        runtime_proof_gate = build_runtime_proof_gate(
            runtime_queue_readout=runtime_queue_summary or runtime_queue_view,
            operator_dependency_ledger=operator_dependency_summary,
            reduction_target_selector=reduction_target_summary,
            now=timestamp,
        )
        runtime_proof_gate_summary = summarize_runtime_proof_gate(runtime_proof_gate)
    if not human_gate_packet_summary:
        human_gate_packet = build_human_gate_execution_readiness_packet(
            runtime_proof_gate=runtime_proof_gate_summary,
            canonical_runtime_queue_view=canonical_queue_summary or runtime_queue_view or {"schema": "AIOS_RUNTIME_EXECUTION_QUEUE.v1", "items": []},
            runtime_queue_validation=queue_validation or validate_queue_view(runtime_queue_view or {"schema": "AIOS_RUNTIME_EXECUTION_QUEUE.v1", "items": []}),
            operator_dependency_ledger=operator_dependency_summary,
            reduction_target_selector=reduction_target_summary,
            runtime_queue_readout=runtime_queue_summary or runtime_queue_view,
            now=timestamp,
        )
        human_gate_packet_summary = summarize_human_gate_execution_readiness_packet(human_gate_packet)

    queue_compare = _compare_runtime_queue_views(dogfood_report, runtime_queue_view)
    evidence_missing = list(source_evidence.get("evidence_missing") or [])
    evidence_attention = list(_ensure_dict(dogfood_report).get("evidence_attention") or [])
    evidence_blockers = list(_ensure_dict(dogfood_report).get("evidence_blockers") or [])
    evidence_items = list(_ensure_dict(dogfood_report).get("evidence_items") or [])

    scorecard = _readiness_scorecard(
        dogfood_report=dogfood_report,
        runtime_queue_view=runtime_queue_view,
        queue_validation=queue_validation,
        runtime_proof_gate_summary=runtime_proof_gate_summary,
        human_gate_packet_summary=human_gate_packet_summary,
        operator_dependency_summary=operator_dependency_summary,
        reduction_target_summary=reduction_target_summary,
    )
    all_gaps = _build_gap_items(
        dogfood_report=dogfood_report,
        runtime_queue_view=runtime_queue_view,
        queue_validation=queue_validation,
        runtime_proof_gate_summary=runtime_proof_gate_summary,
        human_gate_packet_summary=human_gate_packet_summary,
        operator_dependency_summary=operator_dependency_summary,
        reduction_target_summary=reduction_target_summary,
    )
    blocker_rankings = _rank_gaps(all_gaps)
    top_blockers = all_gaps[:3]

    queue_validation_status = _queue_validation_status(queue_validation)
    proof_verdict = str(runtime_proof_gate_summary.get("final_verdict") or "").upper()
    packet_status = str(human_gate_packet_summary.get("packet_status") or "").upper()
    dogfood_status = str(dogfood_report.get("dogfood_status") or "").upper()
    mutation_check_status = str(dogfood_report.get("mutation_check_status") or "BLOCK").upper()
    mutated_sources = list(dogfood_report.get("mutated_sources") or [])
    canonical_count = canonical_queue_summary.get("canonical_queue_item_count")
    protected_count = int(canonical_queue_summary.get("canonical_queue_protected_item_count") or 0)
    duplicate_count = int(canonical_queue_summary.get("canonical_queue_duplicate_id_count") or 0)
    collision_count = int(canonical_queue_summary.get("canonical_queue_collisions") and len(canonical_queue_summary.get("canonical_queue_collisions")) or 0)
    unknown_count = int(canonical_queue_summary.get("canonical_queue_unknown_state_count") or 0)

    if mutation_check_status == "BLOCK" or mutated_sources:
        reassessment_status = "INVALID"
    elif queue_validation_status == "BLOCK" or proof_verdict == "BLOCKED" or packet_status == "BLOCKED" or any(g.get("severity") in {"HIGH", "CRITICAL"} for g in all_gaps):
        reassessment_status = "BLOCKED"
    elif any(g.get("severity") == "MEDIUM" for g in all_gaps) or evidence_attention or queue_compare.get("mismatch"):
        reassessment_status = "ATTENTION"
    else:
        reassessment_status = "PASS"

    if not all_gaps and evidence_missing:
        reassessment_status = "ATTENTION"
    reassessment_status_reason = (
        "Queue validation is BLOCK, the runtime proof gate is BLOCKED, and the human gate packet is BLOCKED."
        if reassessment_status == "BLOCKED"
        else "Report produced safely with attention items."
        if reassessment_status == "ATTENTION"
        else "No blockers remain in the reassessment evidence."
        if reassessment_status == "PASS"
        else "Mutation or invalid evidence prevents a clean reassessment."
    )

    operator_control_switch_readiness = scorecard["operator_control_switch_ready"]
    p2_enqueue_bridge_readiness = scorecard["p2_enqueue_bridge_ready"]
    live_execution_readiness = scorecard["live_execution_ready"]
    scheduler_readiness = scorecard["scheduler_ready"]
    sos_readiness = scorecard["sos_ready"]
    vacation_mode_readiness = scorecard["vacation_mode_ready"]

    report = {
        "schema": SCHEMA,
        "generated_at_utc": timestamp,
        "mode": MODE,
        "reassessment_type": REASSESSMENT_TYPE,
        "reassessment_status": reassessment_status,
        "reassessment_status_reason": reassessment_status_reason,
        "repo_root": str(repo_root_path),
        "evidence_loaded": source_evidence.get("evidence_loaded", {}),
        "evidence_missing": evidence_missing,
        "top_blockers": top_blockers,
        "all_gaps": all_gaps,
        "blocker_rankings": blocker_rankings,
        "readiness_scorecard": scorecard,
        "operator_burden_summary": _burden_summary(
            operator_dependency_summary=operator_dependency_summary,
            reduction_target_summary=reduction_target_summary,
            dogfood_report=dogfood_report,
            queue_validation=queue_validation,
            runtime_proof_gate_summary=runtime_proof_gate_summary,
            human_gate_packet_summary=human_gate_packet_summary,
        ),
        "recommended_next_lanes": _recommended_next_lanes(all_gaps),
        "not_ready_lanes": _not_ready_lanes(
            queue_validation_status=queue_validation_status,
            human_gate_packet_status=packet_status,
            runtime_proof_gate_verdict=proof_verdict,
        ),
        "operator_control_switch_readiness": operator_control_switch_readiness,
        "p2_enqueue_bridge_readiness": p2_enqueue_bridge_readiness,
        "live_execution_readiness": live_execution_readiness,
        "unsafe_flags_detected": [],
        "forbidden_claims_detected": [],
        "approval_granted": False,
        "execution_allowed": False,
        "dispatch_allowed": False,
        "apply_allowed": False,
        "runtime_launch_allowed": False,
        "queue_mutation_allowed": False,
        "telemetry_mutation_allowed": False,
        "scheduler_creation_allowed": False,
        "service_creation_allowed": False,
        "sos_allowed": False,
        "live_trading_allowed": False,
        "credentials_accessed": False,
        "unsafe_autonomy_claim": False,
        "vacation_mode_complete": False,
        "canonical_queue_summary": canonical_queue_summary,
        "queue_validation_summary": queue_validation,
        "runtime_proof_gate_summary": runtime_proof_gate_summary,
        "human_gate_packet_summary": human_gate_packet_summary,
        "operator_dependency_summary": operator_dependency_summary,
        "reduction_target_summary": reduction_target_summary,
        "runtime_queue_summary": runtime_queue_summary,
        "dogfood_report_status": dogfood_status,
        "report_paths": [
            str((output_dir_path / REPORT_JSON_NAME)),
            str((output_dir_path / REPORT_MD_NAME)),
        ],
        "safe_next_action": "Anthony reviews the ranked autonomy gap report and chooses the next report-only lane.",
        "stop_condition": "Stop before approval or execution; keep scheduler, SOS, and live paths blocked until blockers are resolved.",
        "summary": {},
    }

    report["validation"] = validate_autonomy_gap_reassessment_report(report)
    report["summary"] = summarize_autonomy_gap_reassessment_report(report)
    report["readiness_scorecard"] = _readiness_section(readiness_scorecard=scorecard, all_gaps=all_gaps)
    return report


def build_autonomy_gap_markdown_summary(report: dict[str, Any]) -> str:
    summary = summarize_autonomy_gap_reassessment_report(report)
    scorecard = _ensure_dict(report.get("readiness_scorecard"))
    lines = [
        "# AI_OS Autonomy Gap Reassessment",
        "",
        f"- generated_at_utc: `{report.get('generated_at_utc')}`",
        f"- reassessment_status: `{report.get('reassessment_status')}`",
        f"- top_blocker: `{summary.get('top_blocker')}`",
        f"- top_blocker_domain: `{summary.get('top_blocker_domain')}`",
        f"- top_blocker_impact_score: `{summary.get('top_blocker_impact_score')}`",
        f"- recommended_next_lane: `{summary.get('recommended_next_lane')}`",
        f"- queue_validation_ready: `{scorecard.get('queue_validation_ready', {}).get('status')}`",
        f"- runtime_proof_gate_ready: `{scorecard.get('runtime_proof_gate_ready', {}).get('status')}`",
        f"- human_gate_packet_ready: `{scorecard.get('human_gate_packet_ready', {}).get('status')}`",
        f"- dogfood_runner_ready: `{scorecard.get('dogfood_runner_ready', {}).get('status')}`",
        f"- p2_enqueue_bridge_ready: `{scorecard.get('p2_enqueue_bridge_ready', {}).get('status')}`",
        f"- operator_control_switch_ready: `{scorecard.get('operator_control_switch_ready', {}).get('status')}`",
        f"- live_execution_ready: `{scorecard.get('live_execution_ready', {}).get('status')}`",
        "",
        "## Top Blocker",
        f"- {summary.get('top_blocker')} ({summary.get('top_blocker_domain')}, impact {summary.get('top_blocker_impact_score')})",
        "",
        "## Why It Matters",
        f"- {summary.get('top_blocker')}",
        "",
        "## Current Scorecard",
    ]
    for key in (
        "canonical_queue_ready",
        "queue_validation_ready",
        "runtime_proof_gate_ready",
        "human_gate_packet_ready",
        "dogfood_runner_ready",
        "operator_dependency_reduced",
        "p2_enqueue_bridge_ready",
        "operator_control_switch_ready",
        "scheduler_ready",
        "sos_ready",
        "live_execution_ready",
        "vacation_mode_ready",
    ):
        item = scorecard.get(key) or {}
        lines.append(f"- {key}: {item.get('status')} - {item.get('reason')}")
    lines.extend(
        [
            "",
            "## Recommended Next Lanes",
        ]
    )
    for lane in report.get("recommended_next_lanes") or []:
        lines.append(f"- {lane.get('lane_id')}: {lane.get('purpose')}")
    lines.extend(
        [
            "",
            "## Not Ready",
        ]
    )
    for lane in report.get("not_ready_lanes") or []:
        lines.append(f"- {lane.get('lane_id')}: {lane.get('reason')}")
    lines.extend(
        [
            "",
            "## Operator Burden",
        ]
    )
    burden_summary = _ensure_dict(report.get("operator_burden_summary"))
    for key in ("remember_burden", "notice_burden", "decide_burden", "route_burden", "recover_burden"):
        item = burden_summary.get(key) or {}
        lines.append(f"- {key}: {item.get('current_level')} - {', '.join(item.get('remains_manual') or [])}")
    lines.extend(
        [
            "",
            "## Safety",
            "- This reassessment does not approve execution.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_autonomy_gap_reassessment_reports(
    report: dict[str, Any],
    *,
    output_dir: str | Path | None = None,
) -> dict[str, str]:
    output_dir_path = Path(output_dir) if output_dir else Path(report.get("repo_root") or ".") / DEFAULT_REPORT_SUBDIR
    output_dir_path.mkdir(parents=True, exist_ok=True)
    json_path = output_dir_path / REPORT_JSON_NAME
    md_path = output_dir_path / REPORT_MD_NAME
    report["report_paths"] = [str(json_path), str(md_path)]
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(build_autonomy_gap_markdown_summary(report), encoding="utf-8")
    return {"json_path": str(json_path), "md_path": str(md_path)}


def validate_autonomy_gap_reassessment_report(report: dict[str, Any]) -> dict[str, object]:
    checked_fields = [
        "schema",
        "generated_at_utc",
        "mode",
        "reassessment_type",
        "reassessment_status",
        "reassessment_status_reason",
        "repo_root",
        "evidence_loaded",
        "evidence_missing",
        "top_blockers",
        "all_gaps",
        "blocker_rankings",
        "readiness_scorecard",
        "operator_burden_summary",
        "recommended_next_lanes",
        "not_ready_lanes",
        "operator_control_switch_readiness",
        "p2_enqueue_bridge_readiness",
        "live_execution_readiness",
        "unsafe_flags_detected",
        "forbidden_claims_detected",
        "approval_granted",
        "execution_allowed",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_launch_allowed",
        "queue_mutation_allowed",
        "telemetry_mutation_allowed",
        "scheduler_creation_allowed",
        "service_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
        "credentials_accessed",
        "unsafe_autonomy_claim",
        "vacation_mode_complete",
        "safe_next_action",
        "stop_condition",
        "report_paths",
    ]
    blockers: list[str] = []
    unsafe_flags: list[dict[str, Any]] = []
    forbidden_claims: list[dict[str, Any]] = []

    if not isinstance(report, dict):
        return {
            "status": "BLOCK",
            "blockers": ["report is not a dictionary"],
            "checked_fields": checked_fields,
            "unsafe_flags": [],
            "forbidden_claims": [],
            "reassessment_status": None,
        }

    mode = str(report.get("mode") or "")
    reassessment_type = str(report.get("reassessment_type") or "")
    reassessment_status = str(report.get("reassessment_status") or "").upper()
    if mode != MODE:
        blockers.append("mode must be REASSESSMENT_REPORT")
    if reassessment_type != REASSESSMENT_TYPE:
        blockers.append("reassessment_type must be autonomy_gap")
    if reassessment_status not in ALLOWED_REASSESSMENT_STATUSES:
        blockers.append("reassessment_status must be PASS, ATTENTION, BLOCKED, or INVALID")
    if reassessment_status in FORBIDDEN_STATUSES:
        blockers.append("reassessment_status is forbidden")

    if not report.get("safe_next_action"):
        blockers.append("safe_next_action is empty")
    if not report.get("stop_condition"):
        blockers.append("stop_condition is empty")
    if not report.get("report_paths"):
        blockers.append("report_paths is empty")

    bool_fields = [
        "approval_granted",
        "execution_allowed",
        "dispatch_allowed",
        "apply_allowed",
        "runtime_launch_allowed",
        "queue_mutation_allowed",
        "telemetry_mutation_allowed",
        "scheduler_creation_allowed",
        "service_creation_allowed",
        "sos_allowed",
        "live_trading_allowed",
        "credentials_accessed",
        "unsafe_autonomy_claim",
        "vacation_mode_complete",
    ]
    for field in bool_fields:
        if bool(report.get(field)):
            blockers.append(f"{field} must remain false")

    scorecard = _ensure_dict(report.get("readiness_scorecard"))
    p2 = _ensure_dict(report.get("p2_enqueue_bridge_readiness"))
    control = _ensure_dict(report.get("operator_control_switch_readiness"))
    live = _ensure_dict(report.get("live_execution_readiness"))
    scheduler = _ensure_dict(scorecard.get("scheduler_ready"))
    sos = _ensure_dict(scorecard.get("sos_ready"))
    vacation = _ensure_dict(scorecard.get("vacation_mode_ready"))

    if _queue_validation_status(_ensure_dict(report.get("queue_validation_summary"))) == "BLOCK":
        if _ensure_dict(report.get("readiness_scorecard")).get("p2_enqueue_bridge_ready", {}).get("status") == "READY":
            blockers.append("P2 is ready while queue validation is BLOCK")
    if scorecard.get("human_gate_packet_ready", {}).get("status") == "READY" and str(_ensure_dict(report.get("human_gate_packet_summary")).get("packet_status") or "").upper() != "READY_FOR_HUMAN_REVIEW":
        blockers.append("human gate packet readiness is inconsistent")
    if live.get("status") == "READY":
        blockers.append("live_execution_readiness must not be READY")
    if scheduler.get("status") == "READY":
        blockers.append("scheduler_ready must not be READY")
    if sos.get("status") == "READY":
        blockers.append("sos_ready must not be READY")
    if vacation.get("status") == "READY":
        blockers.append("vacation_mode_ready must not be READY")
    if p2.get("status") == "READY" and (_queue_validation_status(_ensure_dict(report.get("queue_validation_summary"))) == "BLOCK" or str(_ensure_dict(report.get("human_gate_packet_summary")).get("packet_status") or "").upper() == "BLOCKED"):
        blockers.append("P2 enqueue bridge must not be READY while the gate/queue remain blocked")
    if control.get("status") == "READY" and (_queue_validation_status(_ensure_dict(report.get("queue_validation_summary"))) == "BLOCK" or str(_ensure_dict(report.get("human_gate_packet_summary")).get("packet_status") or "").upper() == "BLOCKED"):
        blockers.append("operator control switch must not be READY for live control while blockers remain")

    unsafe_flags.extend(_collect_unsafe_flags(report))
    forbidden_claims.extend(_collect_forbidden_claims(report))

    if reassessment_status == "PASS" and blockers:
        blockers.append("PASS cannot be claimed while blockers remain")
    if reassessment_status == "PASS" and report.get("reassessment_status_reason") is None:
        blockers.append("PASS requires a reason")

    command_findings = _contains_command_string(report)
    if command_findings:
        blockers.append("output contains shell command strings")
    secret_findings = _contains_secret_assignment_string(report)
    if secret_findings:
        blockers.append("output contains obvious secret assignment strings")

    status = "PASS" if not blockers else "BLOCK"
    return {
        "status": status,
        "blockers": blockers,
        "checked_fields": checked_fields,
        "unsafe_flags": unsafe_flags,
        "forbidden_claims": forbidden_claims,
        "reassessment_status": report.get("reassessment_status"),
    }


def _collect_unsafe_flags(value: Any, path: str = "$") -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            next_path = f"{path}.{key}"
            if key in UNSAFE_BOOL_KEYS and isinstance(item, bool) and item:
                findings.append({"path": next_path, "value": item})
            findings.extend(_collect_unsafe_flags(item, next_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(_collect_unsafe_flags(item, f"{path}[{index}]"))
    return findings


def _collect_forbidden_claims(value: Any, path: str = "$") -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            next_path = f"{path}.{key}"
            if isinstance(item, str) and item.upper() in FORBIDDEN_STATUSES:
                findings.append({"path": next_path, "value": item})
            findings.extend(_collect_forbidden_claims(item, next_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            findings.extend(_collect_forbidden_claims(item, f"{path}[{index}]"))
    elif isinstance(value, str) and value.upper() in FORBIDDEN_STATUSES:
        findings.append({"path": path, "value": value})
    return findings


def summarize_autonomy_gap_reassessment_report(report: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(report, dict):
        return {
            "reassessment_status": None,
            "top_blocker": None,
            "top_blocker_domain": None,
            "top_blocker_impact_score": 0,
            "recommended_next_lane": None,
            "queue_validation_ready": None,
            "runtime_proof_gate_ready": None,
            "human_gate_packet_ready": None,
            "dogfood_runner_ready": None,
            "p2_enqueue_bridge_ready": None,
            "operator_control_switch_ready": None,
            "scheduler_ready": None,
            "sos_ready": None,
            "live_execution_ready": None,
            "vacation_mode_ready": None,
            "remember_burden": None,
            "notice_burden": None,
            "decide_burden": None,
            "route_burden": None,
            "recover_burden": None,
            "approval_granted": None,
            "execution_allowed": None,
            "dispatch_allowed": None,
            "queue_mutation_allowed": None,
            "safe_next_action": None,
            "stop_condition": None,
            "report_paths": [],
        }

    all_gaps = list(report.get("all_gaps") or [])
    ranked = _rank_gaps(all_gaps)
    top = ranked[0] if ranked else {}
    scorecard = _ensure_dict(report.get("readiness_scorecard"))
    burden = _ensure_dict(report.get("operator_burden_summary"))
    return {
        "reassessment_status": report.get("reassessment_status"),
        "top_blocker": top.get("title"),
        "top_blocker_domain": top.get("domain"),
        "top_blocker_impact_score": top.get("impact_score", 0),
        "recommended_next_lane": (report.get("recommended_next_lanes") or [{}])[0].get("lane_id") if report.get("recommended_next_lanes") else None,
        "queue_validation_ready": scorecard.get("queue_validation_ready", {}).get("status"),
        "runtime_proof_gate_ready": scorecard.get("runtime_proof_gate_ready", {}).get("status"),
        "human_gate_packet_ready": scorecard.get("human_gate_packet_ready", {}).get("status"),
        "dogfood_runner_ready": scorecard.get("dogfood_runner_ready", {}).get("status"),
        "p2_enqueue_bridge_ready": scorecard.get("p2_enqueue_bridge_ready", {}).get("status"),
        "operator_control_switch_ready": scorecard.get("operator_control_switch_ready", {}).get("status"),
        "scheduler_ready": scorecard.get("scheduler_ready", {}).get("status"),
        "sos_ready": scorecard.get("sos_ready", {}).get("status"),
        "live_execution_ready": scorecard.get("live_execution_ready", {}).get("status"),
        "vacation_mode_ready": scorecard.get("vacation_mode_ready", {}).get("status"),
        "remember_burden": burden.get("remember_burden"),
        "notice_burden": burden.get("notice_burden"),
        "decide_burden": burden.get("decide_burden"),
        "route_burden": burden.get("route_burden"),
        "recover_burden": burden.get("recover_burden"),
        "approval_granted": report.get("approval_granted"),
        "execution_allowed": report.get("execution_allowed"),
        "dispatch_allowed": report.get("dispatch_allowed"),
        "queue_mutation_allowed": report.get("queue_mutation_allowed"),
        "safe_next_action": report.get("safe_next_action"),
        "stop_condition": report.get("stop_condition"),
        "report_paths": list(report.get("report_paths") or []),
    }


def run_autonomy_gap_reassessment(
    *,
    repo_root: str | Path = ".",
    output_dir: str | Path | None = None,
    now: str | None = None,
    evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    report = build_autonomy_gap_reassessment_report(
        repo_root=repo_root,
        output_dir=output_dir,
        evidence=evidence,
        now=now,
    )
    write_autonomy_gap_reassessment_reports(report, output_dir=output_dir)
    report["validation"] = validate_autonomy_gap_reassessment_report(report)
    report["summary"] = summarize_autonomy_gap_reassessment_report(report)
    json_path = Path(report["report_paths"][0])
    md_path = Path(report["report_paths"][1])
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    md_path.write_text(build_autonomy_gap_markdown_summary(report), encoding="utf-8")
    return report


def _load_json_arg(text: str | None) -> dict[str, Any] | None:
    if not text:
        return None
    data = json.loads(text)
    return data if isinstance(data, dict) else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the AI_OS autonomy gap reassessment (JSON only).")
    parser.add_argument("--repo-root", default=".", help="repository root")
    parser.add_argument("--output-dir", default=None, help="optional output directory")
    parser.add_argument("--now", default=None, help="optional ISO-8601 timestamp for deterministic output")
    parser.add_argument("--evidence-json", default=None, help="optional JSON string with evidence sections")
    args = parser.parse_args()

    evidence = _load_json_arg(args.evidence_json)
    report = run_autonomy_gap_reassessment(
        repo_root=args.repo_root,
        output_dir=args.output_dir,
        now=args.now,
        evidence=evidence,
    )
    print(json.dumps(report["summary"], indent=2, sort_keys=True))
    return 0 if report["validation"]["status"] == "PASS" else 3


if __name__ == "__main__":
    raise SystemExit(main())
