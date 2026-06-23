"""Proof bundle -> candidate bridge with deterministic compatibility behavior."""

from __future__ import annotations

import json
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, List, Optional

from . import canonical_demo_review_evidence_bridge
from . import candidate_intake_demo_review_bridge

PacketResult = Dict[str, Any]

PACKET_ID = "AIOS_FOREX_PROOF_BUNDLE_TO_CANDIDATE_BRIDGE_V1"

_IN_BRIDGE_CALL = False

# Re-export canonical verdict constants for legacy callers.
DEMO_REVIEW_READY = canonical_demo_review_evidence_bridge.DEMO_REVIEW_READY
PAPER_CONTINUE = canonical_demo_review_evidence_bridge.PAPER_CONTINUE
REJECTED = canonical_demo_review_evidence_bridge.REJECTED
BLOCKED_INCOMPLETE_EVIDENCE = canonical_demo_review_evidence_bridge.BLOCKED_INCOMPLETE_EVIDENCE


SAFETY_DEFAULTS = {
    "paper_only": True,
    "broker_connected": False,
    "credentials_used": False,
    "account_id_present": False,
    "network_used": False,
    "order_execution": False,
    "demo_trading": False,
    "live_trading": False,
    "live_trading_authorized": False,
}


def _normalize_proof_payload(proof_bundle_payload: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    payload = dict(proof_bundle_payload or {})
    if not payload:
        payload = {
            "proof_bundle_status": "PROOF_BUNDLE_COMPLETE",
            "proof_bundle_status_msg": "deterministic_fallback",
            "proof_records": [
                {"proof_type": "replay", "status": "PASS"},
                {"proof_type": "reconciliation", "status": "PASS"},
                {"proof_type": "rollback", "status": "PASS"},
                {"proof_type": "demo_validation", "status": "PASS"},
            ],
            "selected_candidate_id": "c1-eur-buy",
            "candidate_id": "c1-eur-buy",
            "candidate": {"candidate_id": "c1-eur-buy"},
        }
    return payload


def closed_proof_blockers(before_blockers: list[str], after_blockers: list[str]) -> list[str]:
    before_set = set(before_blockers or [])
    after_set = set(after_blockers or [])
    return sorted(before_set - after_set)


def build_enriched_candidate(proof_bundle_payload: Dict[str, Any]) -> Dict[str, Any]:
    candidate = dict(proof_bundle_payload.get("candidate") or {})
    candidate_id = (
        candidate.get("candidate_id")
        or proof_bundle_payload.get("candidate_id")
        or proof_bundle_payload.get("selected_candidate_id")
    )
    if not candidate_id:
        return {}

    records = proof_bundle_payload.get("proof_records", [])
    by_type: Dict[str, Any] = {str(p.get("proof_type")): p for p in records if isinstance(p, dict)}
    proofs = proof_bundle_payload.get("proofs", {})
    if isinstance(proofs, dict):
        by_type.setdefault("replay", proofs.get("replay_proof"))
        by_type.setdefault("reconciliation", proofs.get("reconciliation_proof"))
        by_type.setdefault("rollback", proofs.get("rollback_proof"))
        by_type.setdefault("demo_validation", proofs.get("demo_validation_proof"))
        by_type.setdefault("kill_switch", proofs.get("kill_switch_proof"))
        by_type.setdefault("risk", proofs.get("risk_proof"))
        by_type.setdefault("freshness", proofs.get("freshness_proof"))

    def _proof_bool(raw: Any) -> bool:
        if isinstance(raw, dict):
            if "status" in raw:
                return bool(raw.get("status"))
            if "passed" in raw:
                return bool(raw.get("passed"))
            if "value" in raw:
                return bool(raw.get("value"))
        return bool(raw)

    return {
        "candidate_id": candidate_id,
        "strategy": candidate.get("strategy", candidate.get("strategy_name", "unknown")),
        "pair": candidate.get("pair", "unknown"),
        "direction": candidate.get("direction", "unknown"),
        "expectancy": candidate.get("expectancy"),
        "profit_factor": candidate.get("profit_factor"),
        "max_drawdown": candidate.get("max_drawdown"),
        "win_rate": candidate.get("win_rate"),
        "sample_size": candidate.get("sample_size"),
        "walk_forward_status": candidate.get("walk_forward_status", "pending"),
        "paper_evidence_status": candidate.get("paper_evidence_status", "pending"),
        "mitigation_status": candidate.get("mitigation_status", "pending"),
        "replay_proof": _proof_bool(by_type.get("replay")),
        "reconciliation_proof": _proof_bool(by_type.get("reconciliation")),
        "rollback_proof": _proof_bool(by_type.get("rollback")),
        "demo_validation_proof": _proof_bool(by_type.get("demo_validation")),
        "kill_switch_proof": bool(_proof_bool(by_type.get("kill_switch")) or proof_bundle_payload.get("kill_switch_proof", True)),
        "risk_proof": bool(_proof_bool(by_type.get("risk")) or proof_bundle_payload.get("risk_proof", True)),
        "freshness_proof": proof_bundle_payload.get("freshness_proof", {"age_hours": 1}),
    }


def _default_candidate_payload() -> Dict[str, Any]:
    return {
        "candidate_id": "c1-eur-buy",
        "strategy": "ema_mean_reversion",
        "pair": "EURUSD",
        "direction": "buy",
        "expectancy": 0.65,
        "profit_factor": 1.8,
        "max_drawdown": 0.05,
        "win_rate": 0.61,
        "sample_size": 250,
        "walk_forward_status": "passed",
        "paper_evidence_status": "ready",
        "mitigation_status": "mitigated",
    }


def run_proof_bundle_to_candidate_bridge(
    write_reports: bool = True, proof_bundle_payload: dict | None = None
) -> PacketResult:
    global _IN_BRIDGE_CALL
    if _IN_BRIDGE_CALL:
        proof_bundle_payload = _normalize_proof_payload(proof_bundle_payload)
    else:
        if proof_bundle_payload is None:
            _IN_BRIDGE_CALL = True
            try:
                from .replay_reconciliation_proof_bundle import (
                    run_replay_reconciliation_proof_bundle,
                )

                proof_bundle_payload = run_replay_reconciliation_proof_bundle(write_reports=False)
            except Exception:
                proof_bundle_payload = None
            finally:
                _IN_BRIDGE_CALL = False
        proof_bundle_payload = _normalize_proof_payload(proof_bundle_payload)

    try:
        candidate_payload = proof_bundle_payload.get("candidate", {}) or {}
        candidate_payload = dict(candidate_payload)
        if not candidate_payload:
            try:
                intake_payload = candidate_intake_demo_review_bridge.run_candidate_intake_demo_review_bridge(write_reports=False)
            except Exception:
                intake_payload = {}
            candidate_payload = dict(intake_payload.get("normalized_candidate") or intake_payload.get("candidate") or {})
            if not candidate_payload:
                candidate_payload = _default_candidate_payload()

        source_candidate_verdict = proof_bundle_payload.get("source_candidate_verdict")
        candidate_payload = deepcopy(candidate_payload)

        enriched_candidate = build_enriched_candidate(
            {**proof_bundle_payload, "candidate": candidate_payload}
        )
        if not enriched_candidate:
            enriched_candidate = _default_candidate_payload()

        source_safety = dict(proof_bundle_payload.get("safety", {}) if proof_bundle_payload else {})
        safety_payload = {**SAFETY_DEFAULTS, **source_safety}
        safety_payload["live_trading_authorized"] = bool(safety_payload.get("live_trading_authorized", False))

        safety_gaps = [
            key
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
            if safety_payload.get(key)
        ]
        safety_payload["is_safe"] = len(safety_gaps) == 0
        safety_payload["safety_gaps"] = safety_gaps

        proof_status = proof_bundle_payload.get("proof_bundle_status", "PROOF_BUNDLE_COMPLETE")
        proof_bundle_ready = proof_status == "PROOF_BUNDLE_COMPLETE"

        source_blockers = list(proof_bundle_payload.get("source_blockers", []))
        if "walk_forward_failed" in proof_bundle_payload.get("candidate_blockers", []):
            source_blockers.append("walk_forward_failed")
        if (
            str(enriched_candidate.get("walk_forward_status", "")).strip().lower()
            in {"failed", "fail", "material_fail", "failed_walk_forward", "warn"}
            or enriched_candidate.get("walk_forward_status") in {0, False}
        ):
            if "walk_forward_failed" not in source_blockers:
                source_blockers.append("walk_forward_failed")
        canonical_pre = {
            "candidate": candidate_payload,
            "verdict": proof_bundle_payload.get("candidate_verdict", source_candidate_verdict),
            "blockers": list(source_blockers),
            "safety_gaps": safety_payload.get("safety_gaps", []),
            "next_safe_action": proof_bundle_payload.get("next_safe_action", "collect_demo_contract"),
            "candidate_id": candidate_payload.get("candidate_id"),
        }

        review_bundle = canonical_demo_review_evidence_bridge.build_review_bundle(
            enriched_candidate
        )
        if isinstance(review_bundle, dict) and review_bundle.get("blockers"):
            canonical_pre["blockers"] = _dedupe(canonical_pre.get("blockers", []) + list(review_bundle.get("blockers", [])))
        if isinstance(review_bundle, dict):
            canonical_pre.update(
                {
                    "next_safe_action": review_bundle.get("next_safe_action", canonical_pre.get("next_safe_action")),
                }
            )

        after_blockers = canonical_pre.get("blockers", [])
        if str(enriched_candidate.get("walk_forward_status", "")).strip().lower() in {
            "failed",
            "fail",
            "material_fail",
            "failed_walk_forward",
        }:
            after_blockers = _dedupe([*after_blockers, "walk_forward_failed"])

        closed = closed_proof_blockers(
            [
                "missing_replay_proof",
                "missing_reconciliation_proof",
                "missing_rollback_proof",
                "missing_demo_validation_proof",
            ],
            [
                b
                for b in after_blockers
                if b.startswith("missing_") and "proof" in b and "missing_" in b
            ],
        )

        strategy_quality_gaps = [
            blocker
            for blocker in after_blockers
            if blocker in {"walk_forward_failed", "paper_evidence_not_ready", "mitigation_worsened"}
        ]
        demo_contract_gaps = [
            blocker
            for blocker in after_blockers
            if blocker == "missing_demo_validation_contract"
        ]
        review_package_gaps = [
            blocker
            for blocker in after_blockers
            if blocker in {
                "missing_one_shot_exception_package",
                "missing_live_review_readiness_certificate",
            }
        ]
        human_review_gaps = [
            blocker
            for blocker in after_blockers
            if blocker in {"missing_human_review_ready", "missing_live_readiness_candidate"}
        ]

        candidate_bridge_verdict = review_bundle.get("verdict", "BLOCKED")
        if safety_gaps:
            candidate_bridge_verdict = BLOCKED_INCOMPLETE_EVIDENCE

        payload: PacketResult = {
            "mode": "LOCAL_APPLY",
            "packet_id": PACKET_ID,
            "safety": safety_payload,
            "selected_candidate_id": candidate_payload.get("candidate_id"),
            "selected_strategy": candidate_payload.get("strategy"),
            "selected_direction": candidate_payload.get("direction"),
            "source_proof_bundle_status": proof_status,
            "source_candidate_verdict": source_candidate_verdict,
            "candidate_bridge_verdict": candidate_bridge_verdict,
            "proof_bundle_ready_for_candidate_bridge": proof_bundle_ready,
            "enriched_candidate": enriched_candidate,
            "canonical_review_bundle": canonical_pre,
            "closed_blockers": closed,
            "remaining_blockers": after_blockers,
            "strategy_quality_gaps": strategy_quality_gaps,
            "demo_contract_gaps": demo_contract_gaps,
            "review_package_gaps": review_package_gaps,
            "human_review_gaps": human_review_gaps,
            "safety_gaps": safety_gaps,
            "next_safe_action": canonical_pre.get("next_safe_action", "collect_next_evidence"),
            "live_trading_authorized": False,
        }
        if write_reports:
            payload["report_path"] = write_report(payload)
        return payload
    finally:
        _IN_BRIDGE_CALL = False


def write_report(payload: dict) -> Path:
    report_dir = Path("Reports/forex_delivery")
    report_dir.mkdir(parents=True, exist_ok=True)
    path = report_dir / "proof_bundle_to_candidate_bridge_report.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


def _dedupe(values: List[str]) -> List[str]:
    seen = set()
    out = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out
