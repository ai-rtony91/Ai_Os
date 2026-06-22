"""Paper-only planner that converts journey blockers into deterministic follow-up packets."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from automation.forex_engine import review_chain_end_to_end_candidate_journey

MODE = "FOREX_PROOF_GAP_CLOSURE_PLAN_V1"
PACKET_ID = "AIOS_FOREX_PROOF_GAP_CLOSURE_PLAN_V1"
REPORT_PATH = Path("Reports/forex_delivery/AIOS_FOREX_PROOF_GAP_CLOSURE_PLAN_V1_REPORT.md")

NO_GAP_DETECTED = "NO_GAP_DETECTED"

SAFETY_PACKET_ID = "AIOS_FOREX-SAFETY-BLOCKER-CONTAINMENT-V1"
PROOF_PACKET_ID = "AIOS_FOREX-REPLAY-RECONCILIATION-PROOF-BUNDLE-V1"
EVIDENCE_PACKET_ID = "AIOS_FOREX-CANDIDATE-EVIDENCE-REPAIR-LOOP-V1"
DEMO_CONTRACT_PACKET_ID = "AIOS_FOREX-DEMO-VALIDATION-CONTRACT-FROM-CANDIDATE-BRIDGE-V1"
ONE_SHOT_PACKET_ID = "AIOS_FOREX-ONE-SHOT-PACKAGE-FROM-DEMO-CONTRACT-V1"
CERTIFICATE_PACKET_ID = "AIOS_FOREX-LIVE-REVIEW-CERTIFICATE-FROM-ONE-SHOT-V1"
HUMAN_PACKET_ID = "AIOS_FOREX-HUMAN-REVIEW-READINESS-HANDOFF-V1"


def _safe_get(mapping: dict[str, Any], aliases: tuple[str, ...], default: Any = None) -> Any:
    for alias in aliases:
        if alias in mapping:
            return mapping[alias]
    return default


def _to_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, tuple):
        return [str(v) for v in value]
    return [str(value)]


def normalize_blockers(raw_blockers: Any) -> list[str]:
    normalized: list[str] = []
    for raw in _to_list(raw_blockers):
        item = str(raw).strip()
        if item and item not in normalized:
            normalized.append(item)
    return normalized


def _normalise_safety(safety: Any) -> dict[str, bool]:
    if not isinstance(safety, dict):
        safety = {}
    return {
        "paper_only": bool(safety.get("paper_only", False)),
        "broker_connected": bool(safety.get("broker_connected", False)),
        "credentials_used": bool(safety.get("credentials_used", False)),
        "account_id_present": bool(safety.get("account_id_present", False)),
        "network_used": bool(safety.get("network_used", False)),
        "order_execution": bool(safety.get("order_execution", False)),
        "demo_trading": bool(safety.get("demo_trading", False)),
        "live_trading": bool(safety.get("live_trading", False)),
    }


def _bucket_from_blockers(blockers: list[str]) -> dict[str, list[str]]:
    buckets = {
        "evidence_proof_gaps": [],
        "strategy_quality_gaps": [],
        "demo_contract_gaps": [],
        "review_package_gaps": [],
        "safety_gaps": [],
        "human_review_gaps": [],
    }

    evidence_aliases = {
        "missing_replay_proof",
        "missing_reconciliation_proof",
        "missing_rollback_proof",
        "missing_demo_validation_proof",
        "missing_risk_proof",
    }
    strategy_aliases = {"walk_forward_failed", "paper_evidence_not_ready", "mitigation_worsened"}
    demo_aliases = {"missing_demo_validation_contract"}
    review_aliases = {"missing_one_shot_exception_package", "missing_live_review_readiness_certificate"}
    human_aliases = {"missing_live_readiness_candidate", "missing_human_review_ready"}

    for blocker in blockers:
        if blocker in evidence_aliases:
            buckets["evidence_proof_gaps"].append(blocker)
        elif blocker in strategy_aliases:
            buckets["strategy_quality_gaps"].append(blocker)
        elif blocker in demo_aliases:
            buckets["demo_contract_gaps"].append(blocker)
        elif blocker in review_aliases:
            buckets["review_package_gaps"].append(blocker)
        elif blocker in human_aliases:
            buckets["human_review_gaps"].append(blocker)

    return buckets


def _bucket_safety_gaps(safety: dict[str, bool], blockers: list[str]) -> list[str]:
    gaps: list[str] = []
    for key in (
        "broker_connected",
        "credentials_used",
        "account_id_present",
        "network_used",
        "order_execution",
        "demo_trading",
        "live_trading",
    ):
        if safety.get(key):
            gaps.append(f"unsafe_{key}")

    for blocker in blockers:
        if blocker in {
            "broker_connection_active",
            "network_access_detected",
            "credential_access_detected",
            "account_identifier_access_detected",
            "order_execution_enabled_detected",
            "live_trading_authorization_detected",
            "execution_authority_detected",
            "capital_allocation_detected",
        } and blocker not in gaps:
            gaps.append(blocker)

    return gaps


def _recommended_sequence(blockers: dict[str, list[str]], safety_gaps: list[str]) -> list[dict[str, Any]]:
    if safety_gaps:
        return [
            {
                "packet_id": SAFETY_PACKET_ID,
                "purpose": "contain and clear safety blockers before any review progression.",
                "priority": 0,
            }
        ]

    sequence: list[dict[str, Any]] = []
    if blockers["evidence_proof_gaps"]:
        sequence.append(
            {
                "packet_id": PROOF_PACKET_ID,
                "purpose": "emit deterministic paper-only replay, reconciliation, rollback, and demo-validation proof bundle.",
                "priority": 1,
            }
        )
    if blockers["strategy_quality_gaps"]:
        sequence.append(
            {
                "packet_id": EVIDENCE_PACKET_ID,
                "purpose": "repair/normalize candidate evidence maturity before demo-review progression.",
                "priority": 2,
            }
        )
    if blockers["demo_contract_gaps"]:
        sequence.append(
            {
                "packet_id": DEMO_CONTRACT_PACKET_ID,
                "purpose": "produce demo-validation contract input from canonical candidate verdict after proof bundle exists.",
                "priority": 3,
            }
        )
    if "missing_one_shot_exception_package" in blockers["review_package_gaps"]:
        sequence.append(
            {
                "packet_id": ONE_SHOT_PACKET_ID,
                "purpose": "assemble review-only one-shot package from completed demo validation contract.",
                "priority": 4,
            }
        )
    if "missing_live_review_readiness_certificate" in blockers["review_package_gaps"]:
        sequence.append(
            {
                "packet_id": CERTIFICATE_PACKET_ID,
                "purpose": "assemble review-only live readiness certificate from one-shot package without live authorization.",
                "priority": 5,
            }
        )
    if blockers["human_review_gaps"]:
        sequence.append(
            {
                "packet_id": HUMAN_PACKET_ID,
                "purpose": "produce final human-review handoff when all upstream paper-only review proofs exist.",
                "priority": 6,
            }
        )

    sequence.sort(key=lambda entry: entry["priority"])
    return sequence


def _highest_value(recommended: list[dict[str, Any]], safety_gaps: list[str]) -> str:
    if safety_gaps:
        return SAFETY_PACKET_ID
    if not recommended:
        return NO_GAP_DETECTED
    return str(recommended[0]["packet_id"])


def _blocked_flags(blockers: dict[str, list[str]], safety_gaps: list[str]) -> tuple[bool, bool]:
    blocked_for_demo_review = bool(
        blockers["evidence_proof_gaps"]
        or blockers["strategy_quality_gaps"]
        or blockers["demo_contract_gaps"]
        or safety_gaps
    )
    blocked_for_live_review = bool(
        blockers["review_package_gaps"]
        or blockers["human_review_gaps"]
        or safety_gaps
        or blocked_for_demo_review
    )
    return blocked_for_demo_review, blocked_for_live_review


def write_report(payload: dict[str, Any]) -> str:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(_build_report_text(payload), encoding="utf-8")
    return str(REPORT_PATH)


def _build_report_text(payload: dict[str, Any]) -> str:
    buckets = [
        "evidence_proof_gaps: " + ", ".join(payload.get("closure_buckets", {}).get("evidence_proof_gaps", [])),
        "strategy_quality_gaps: " + ", ".join(payload.get("closure_buckets", {}).get("strategy_quality_gaps", [])),
        "demo_contract_gaps: " + ", ".join(payload.get("closure_buckets", {}).get("demo_contract_gaps", [])),
        "review_package_gaps: " + ", ".join(payload.get("closure_buckets", {}).get("review_package_gaps", [])),
        "safety_gaps: " + ", ".join(payload.get("closure_buckets", {}).get("safety_gaps", [])),
        "human_review_gaps: " + ", ".join(payload.get("closure_buckets", {}).get("human_review_gaps", [])),
    ]
    sequence = ", ".join(entry["packet_id"] for entry in payload.get("recommended_packet_sequence", []))
    return "\n".join(
        [
            "# AIOS Forex Proof Gap Closure Plan V1",
            "",
            "## Purpose",
            "Convert deterministic end-to-end journey blockers into ordered follow-up review packets.",
            "",
            "## Source journey consumed",
            "- automation/forex_engine/review_chain_end_to_end_candidate_journey.py",
            "",
            "## Blocker buckets",
            *[f"- {line}" for line in buckets],
            "",
            "## Recommended packet sequence",
            "- " + sequence,
            "",
            "## Highest value packet",
            "- " + str(payload.get("highest_value_next_packet")),
            "",
            "## Safety boundary",
            "- paper_only: " + str(payload.get("safety", {}).get("paper_only", False)),
            "- broker_connected: " + str(payload.get("safety", {}).get("broker_connected", False)),
            "- credentials_used: " + str(payload.get("safety", {}).get("credentials_used", False)),
            "- network_used: " + str(payload.get("safety", {}).get("network_used", False)),
            "- order_execution: " + str(payload.get("safety", {}).get("order_execution", False)),
            "- demo_trading: " + str(payload.get("safety", {}).get("demo_trading", False)),
            "- live_trading: " + str(payload.get("safety", {}).get("live_trading", False)),
            "",
            "## CLI usage",
            "- python scripts/run_forex_proof_gap_closure_plan.py [--json] [--write-report]",
            "",
            "## Validation",
            "- placeholder",
            "",
            "## Explicit security statement",
            "No broker connectivity, no credentials, no env reads, no network access, no demo trade, no live trade, no order execution introduced.",
            "",
        ]
    )


def run_proof_gap_closure_plan(
    *,
    write_reports: bool = True,
    journey_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    journey = journey_payload or review_chain_end_to_end_candidate_journey.run_review_chain_end_to_end_candidate_journey(
        write_reports=False,
    )
    candidate_blockers = normalize_blockers(_safe_get(journey, ("candidate_demo_review_blockers",), default=[]))
    chain_blockers = normalize_blockers(_safe_get(journey, ("review_chain_blockers",), default=[]))
    all_blockers = candidate_blockers + [b for b in chain_blockers if b not in candidate_blockers]

    safety = _normalise_safety(_safe_get(journey, ("safety",), default={}))
    closure_buckets = _bucket_from_blockers(all_blockers)
    closure_buckets["safety_gaps"] = _bucket_safety_gaps(safety, all_blockers)

    recommended = _recommended_sequence(closure_buckets, closure_buckets["safety_gaps"])
    highest = _highest_value(recommended, closure_buckets["safety_gaps"])
    blocked_for_demo_review, blocked_for_live_review = _blocked_flags(closure_buckets, closure_buckets["safety_gaps"])

    result: dict[str, Any] = {
        "mode": MODE,
        "packet_id": PACKET_ID,
        "safety": safety,
        "source_journey_final_verdict": str(_safe_get(journey, ("final_verdict",), default="")),
        "source_candidate_verdict": str(_safe_get(journey, ("candidate_demo_review_verdict",), default="")),
        "source_review_chain_status": str(_safe_get(journey, ("review_chain_status",), default="")),
        "selected_candidate_id": str(_safe_get(journey, ("selected_candidate_id",), default="")),
        "selected_strategy": str(_safe_get(journey, ("selected_strategy",), default="")),
        "selected_direction": str(_safe_get(journey, ("selected_direction",), default="")),
        "normalized_blockers": all_blockers,
        "closure_buckets": closure_buckets,
        "recommended_packet_sequence": recommended,
        "highest_value_next_packet": highest,
        "blocked_for_demo_review": blocked_for_demo_review,
        "blocked_for_live_review": blocked_for_live_review,
        "next_safe_action": str(_safe_get(journey, ("final_next_safe_action",), default="")),
    }

    if write_reports:
        result["report_path"] = write_report(result)
    return result


__all__ = ["run_proof_gap_closure_plan", "normalize_blockers", "write_report"]
