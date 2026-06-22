"""Consolidated readiness blocker closure contract for Forex review progression."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .proof_bundle_to_candidate_bridge import run_proof_bundle_to_candidate_bridge

PACKET_ID = "AIOS_FOREX_CONSOLIDATED_READINESS_BLOCKER_CLOSURE_V1"
REPORT_PATH = Path("Reports/forex_delivery/AIOS_FOREX_CONSOLIDATED_READINESS_BLOCKER_CLOSURE_V1_REPORT.md")

CANONICAL_BLOCKERS: list[str] = [
    "walk_forward_failed",
    "paper_evidence_not_ready",
    "mitigation_worsened",
    "missing_validation_results",
    "candidate_not_approved_for_demo_validation",
    "demo_contract_not_complete",
    "missing_live_readiness_candidate",
    "missing_approval_trace",
    "missing_risk_limits",
    "missing_kill_switch_proof",
    "missing_rollback_proof",
    "missing_reconciliation_proof",
    "missing_evidence_freshness",
    "missing_replayability_proof",
    "missing_final_disarm_proof",
    "missing_post_trade_journal_path",
    "demo_validation_contract_not_complete",
    "one_shot_exception_package_not_review_ready",
    "live_review_certificate_not_review_ready",
    "missing_human_review_ready",
]

DEFAULT_MIN_SAMPLE_SIZE = 10
DEFAULT_MAX_EXPECTANCY = 0.0
DEFAULT_MIN_PROFIT_FACTOR = 1.0
DEFAULT_MAX_FRESHNESS_HOURS = 24


def _to_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    text = str(value).strip().lower()
    if not text:
        return default
    return text in {"1", "true", "yes", "ok", "passed", "pass", "complete"}


def _to_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    if isinstance(value, tuple):
        return [str(item) for item in value]
    return [str(value)]


def _read_time(value: Any) -> datetime | None:
    if not value:
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        try:
            dt = datetime.fromisoformat(str(value))
        except Exception:
            return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _parse_evidence_timestamp(state: dict[str, Any], now: datetime) -> bool:
    raw = state.get("evidence_timestamp", state.get("updated_at", state.get("created_at")))
    ts = _read_time(raw)
    if ts is None:
        return False
    age_hours = (now - ts).total_seconds() / 3600.0
    return age_hours <= DEFAULT_MAX_FRESHNESS_HOURS


def _proof_true(value: Any) -> bool:
    if isinstance(value, dict):
        if "status" in value:
            return str(value.get("status")).lower() in {"pass", "passed", "complete", "ready", "true", "1"}
        if "passed" in value:
            return _to_bool(value.get("passed"), default=False)
        if "value" in value:
            return bool(value.get("value"))
    if isinstance(value, str):
        return str(value).strip().lower() not in {"", "none", "false", "0", "missing"}
    return bool(value)


def _approval_ready(approval_trace: dict[str, Any] | None) -> bool:
    if not isinstance(approval_trace, dict) or not approval_trace:
        return False
    return (
        _to_bool(approval_trace.get("signed"), default=False)
        or _to_bool(approval_trace.get("approved"), default=False)
        or _to_bool(approval_trace.get("human_review_ready"), default=False)
        or "reviewed_by" in approval_trace
    )


def _ensure_demo_candidate(state: dict[str, Any], candidate_id: str) -> dict[str, Any]:
    candidate = state.get("candidate")
    if not isinstance(candidate, dict):
        candidate = {}
    if not candidate and state.get("normalized_candidate"):
        candidate = state.get("normalized_candidate") or {}
    if not isinstance(candidate, dict):
        candidate = {}
    if not candidate.get("candidate_id"):
        candidate["candidate_id"] = candidate_id
    return candidate


def _safety_defaults() -> dict[str, bool]:
    return {
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


@dataclass
class _EvidenceContract:
    candidate_id: str
    strategy_name: str
    symbol: str
    direction: str
    walk_forward_status: str
    mitigation_status: str
    candidate_approved_for_demo_validation: bool
    validation_results: list[dict[str, Any]]
    paper_metrics: dict[str, Any]
    demo_validation_contract: dict[str, Any]
    live_readiness_candidate: dict[str, Any]
    approval_trace: dict[str, Any]
    risk_limits: dict[str, Any]
    kill_switch_proof: Any
    rollback_proof: Any
    reconciliation_proof: Any
    evidence_timestamp: Any
    replayability_proof: Any
    final_disarm_proof: Any
    post_trade_journal_path: str | None
    one_shot_exception_package: dict[str, Any]
    live_review_certificate: dict[str, Any]
    human_review_ready: bool


def _normalise(raw: dict[str, Any], candidate_id: str) -> _EvidenceContract:
    candidate = _ensure_demo_candidate(raw, candidate_id)
    paper_metrics = raw.get("paper_metrics", {})
    if not isinstance(paper_metrics, dict):
        paper_metrics = {}
    return _EvidenceContract(
        candidate_id=str(candidate.get("candidate_id", candidate_id)),
        strategy_name=str(candidate.get("strategy", candidate.get("strategy_name", ""))),
        symbol=str(candidate.get("pair", candidate.get("symbol", ""))),
        direction=str(candidate.get("direction", "")),
        walk_forward_status=str(candidate.get("walk_forward_status", raw.get("walk_forward_status", ""))),
        mitigation_status=str(candidate.get("mitigation_status", candidate.get("mitigation", ""))).strip().lower(),
        candidate_approved_for_demo_validation=_to_bool(
            raw.get(
                "approved_for_demo_validation",
                raw.get("candidate_approved", raw.get("candidate_approved_for_demo_validation")),
            ),
            default=False,
        ) or _to_bool(candidate.get("approved_for_demo_validation"), default=False),
        validation_results=_to_list(raw.get("validation_results")),
        paper_metrics=paper_metrics,
        demo_validation_contract=raw.get("demo_validation_contract", {}) if isinstance(raw.get("demo_validation_contract", {}), dict) else {},
        live_readiness_candidate=raw.get("live_readiness_candidate", {}) if isinstance(raw.get("live_readiness_candidate", {}), dict) else {},
        approval_trace=raw.get("approval_trace", {}) if isinstance(raw.get("approval_trace", {}), dict) else {},
        risk_limits=raw.get("risk_limits", {}) if isinstance(raw.get("risk_limits", {}), dict) else {},
        kill_switch_proof=raw.get("kill_switch_proof"),
        rollback_proof=raw.get("rollback_proof"),
        reconciliation_proof=raw.get("reconciliation_proof"),
        evidence_timestamp=raw.get("evidence_timestamp"),
        replayability_proof=raw.get("replayability_proof"),
        final_disarm_proof=raw.get("final_disarm_proof"),
        post_trade_journal_path=raw.get("post_trade_journal_path"),
        one_shot_exception_package=raw.get("one_shot_exception_package", {}) if isinstance(raw.get("one_shot_exception_package", {}), dict) else {},
        live_review_certificate=raw.get("live_review_certificate", {}) if isinstance(raw.get("live_review_certificate", {}), dict) else {},
        human_review_ready=_to_bool(raw.get("human_review_ready"), default=False),
    )


def _collect_blocker_details(
    candidate: _EvidenceContract,
    evidence_fresh: bool,
    now: datetime,
) -> dict[str, list[str]]:
    details: dict[str, list[str]] = {}
    if candidate.walk_forward_status.strip().lower() in {"failed", "fail", "failed_walk_forward"}:
        details["walk_forward_failed"] = ["Walk-forward status indicates failed."]
    paper_metrics = candidate.paper_metrics
    total_trades = paper_metrics.get("total_trades")
    closed_trades = paper_metrics.get("closed_trades")
    expectancy = paper_metrics.get("expectancy")
    profit_factor = paper_metrics.get("profit_factor")
    max_drawdown = paper_metrics.get("max_drawdown")
    sample_size = paper_metrics.get("sample_size", paper_metrics.get("closed_trades"))
    if (
        total_trades in (None, "")
        or closed_trades in (None, "")
        or expectancy in (None, "")
        or profit_factor in (None, "")
        or max_drawdown in (None, "")
        or sample_size in (None, "")
        or not candidate.validation_results
    ):
        details.setdefault("paper_evidence_not_ready", []).append("Missing required paper metrics.")
    else:
        try:
            total_trades_i = int(total_trades)
            sample_size_i = int(sample_size)
            expectancy_f = float(expectancy)
            pf = float(profit_factor)
            drawdown_f = float(max_drawdown)
        except (TypeError, ValueError):
            details.setdefault("paper_evidence_not_ready", []).append(
                "Paper metrics cannot be converted to required numeric ranges."
            )
        else:
            if total_trades_i <= 0:
                details.setdefault("paper_evidence_not_ready", []).append("Closed trades must be positive.")
            if expectancy_f <= DEFAULT_MAX_EXPECTANCY:
                details.setdefault("paper_evidence_not_ready", []).append("Expectancy must be positive.")
            if pf <= DEFAULT_MIN_PROFIT_FACTOR:
                details.setdefault("paper_evidence_not_ready", []).append("Profit factor must exceed 1.")
            if sample_size_i < DEFAULT_MIN_SAMPLE_SIZE:
                details.setdefault("paper_evidence_not_ready", []).append("Sample size below minimum threshold.")

    if candidate.human_review_ready is False:
        details["missing_human_review_ready"] = ["human_review_ready flag not true."]

    if candidate.replayability_proof is None or not _proof_true(candidate.replayability_proof):
        details["missing_replayability_proof"] = ["Replayability proof not present or stale."]

    if not evidence_fresh:
        details["missing_evidence_freshness"] = ["Freshness proof cannot be established."]

    if not candidate.validation_results:
        details["missing_validation_results"] = ["No validation results payload available."]

    if not _approval_ready(candidate.approval_trace):
        details["missing_approval_trace"] = ["Approval trace missing."]

    risk_limits = candidate.risk_limits
    if not isinstance(risk_limits, dict) or not risk_limits:
        details["missing_risk_limits"] = ["Risk limits record missing."]
    else:
        max_drawdown_limit = risk_limits.get("max_drawdown_limit", risk_limits.get("max_drawdown"))
        if max_drawdown_limit not in (None, ""):
            try:
                drawdown_limit = float(max_drawdown_limit)
            except (TypeError, ValueError):
                drawdown_limit = None
            else:
                try:
                    drawdown_f = float(candidate.paper_metrics.get("max_drawdown", 0.0))
                except (TypeError, ValueError):
                    drawdown_f = None
                if drawdown_f is not None and drawdown_f > drawdown_limit:
                    details["paper_evidence_not_ready"] = details.get("paper_evidence_not_ready", [])
                    details["paper_evidence_not_ready"].append("Drawdown exceeds configured risk limits.")

        else:
            details.setdefault("missing_risk_limits", []).append("Risk limit fields incomplete.")

    if candidate.mitigation_status == "worsened":
        details.setdefault("mitigation_worsened", []).append("Mitigation has worsened metrics.")

    if not candidate.live_readiness_candidate:
        details["missing_live_readiness_candidate"] = ["No live readiness candidate artifact."]
    elif not _to_bool(
        candidate.live_readiness_candidate.get("live_readiness_candidate", candidate.live_readiness_candidate.get("live_ready")),
        default=False,
    ):
        details["missing_live_readiness_candidate"] = ["No explicit live readiness candidate record."]

    contract = candidate.demo_validation_contract
    contract_complete = _proof_true(contract.get("demo_validation_contract_completed")) if isinstance(contract, dict) else False
    contract_status = str(contract.get("status", "")).lower() if isinstance(contract, dict) else ""
    if not contract or not contract_complete and contract_status not in {"complete", "approved", "ready", "passed"}:
        details["demo_contract_not_complete"] = ["Demo validation contract incomplete."]
        details["demo_validation_contract_not_complete"] = ["Demo validation contract incomplete."]

    if not candidate.candidate_approved_for_demo_validation:
        details["candidate_not_approved_for_demo_validation"] = [
            "Candidate approval marker not present."
        ]

    if not _proof_true(candidate.kill_switch_proof):
        details["missing_kill_switch_proof"] = ["Kill switch proof missing."]
    if not _proof_true(candidate.rollback_proof):
        details["missing_rollback_proof"] = ["Rollback proof missing."]
    if not _proof_true(candidate.reconciliation_proof):
        details["missing_reconciliation_proof"] = ["Reconciliation proof missing."]

    if not candidate.post_trade_journal_path:
        details["missing_post_trade_journal_path"] = ["post_trade_journal_path missing."]

    if not candidate.final_disarm_proof:
        details["missing_final_disarm_proof"] = ["Final disarm proof missing."]

    if not _to_bool(candidate.one_shot_exception_package.get("exception_package_completed"), default=False):
        details["one_shot_exception_package_not_review_ready"] = [
            "One-shot package not review ready."
        ]

    if not _to_bool(candidate.live_review_certificate.get("certificate_completed"), default=False):
        details["live_review_certificate_not_review_ready"] = [
            "Live review certificate not review ready."
        ]

    if not details:
        details = {}
    return details


def run_consolidated_readiness_blocker_closure_v1(
    candidate_id: str = "c1-eur-buy",
    *,
    evidence_payload: dict[str, Any] | None = None,
    proof_bundle_payload: dict[str, Any] | None = None,
    evidence_path: str | None = None,
    write_reports: bool = True,
) -> dict[str, Any]:
    if evidence_path:
        raw: dict[str, Any] = {}
        try:
            raw = json.loads(Path(evidence_path).read_text(encoding="utf-8"))
        except Exception:
            raw = {}
    else:
        raw = evidence_payload or {}

    if not raw:
        if proof_bundle_payload is not None:
            raw = proof_bundle_payload
        else:
            raw = run_proof_bundle_to_candidate_bridge(write_reports=False)

    evidence = _normalise(raw or {}, candidate_id)

    now = datetime.now(timezone.utc)
    evidence_fresh = _parse_evidence_timestamp(raw or {}, now)

    blocker_details = _collect_blocker_details(evidence, evidence_fresh, now)
    unresolved = [name for name in CANONICAL_BLOCKERS if blocker_details.get(name)]
    # remove duplicate literal entry
    unresolved = list(dict.fromkeys([b for b in unresolved if b]))

    resolved = [b for b in CANONICAL_BLOCKERS if b not in unresolved]

    ready_for_demo_validation = (
        "walk_forward_failed" not in unresolved
        and "paper_evidence_not_ready" not in unresolved
        and "missing_validation_results" not in unresolved
        and "candidate_not_approved_for_demo_validation" not in unresolved
        and "demo_contract_not_complete" not in unresolved
        and "demo_validation_contract_not_complete" not in unresolved
    )

    live_readiness_requirements = {
        "missing_live_readiness_candidate",
        "missing_approval_trace",
        "missing_risk_limits",
        "missing_kill_switch_proof",
        "missing_rollback_proof",
        "missing_reconciliation_proof",
        "missing_replayability_proof",
        "missing_final_disarm_proof",
        "missing_post_trade_journal_path",
        "one_shot_exception_package_not_review_ready",
        "live_review_certificate_not_review_ready",
        "missing_human_review_ready",
    }
    ready_for_live_review = ready_for_demo_validation and not (
        any(item in unresolved for item in live_readiness_requirements)
    )

    safety = _safety_defaults()
    safety.update(
        {
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
    )

    status = "READY" if not unresolved else "BLOCKED"
    decision = "advance" if status == "READY" else "blocked"
    next_safe_action = unresolved[0] if unresolved else "candidate_promo_recommended"

    result: dict[str, Any] = {
        "status": status,
        "decision": decision,
        "ready_for_demo_validation": bool(ready_for_demo_validation),
        "ready_for_live_review": bool(ready_for_live_review),
        "blockers": resolved + unresolved,
        "resolved_blockers": resolved,
        "unresolved_blockers": unresolved,
        "blocker_details": blocker_details,
        "required_evidence": {name: _required_fields_for_blocker(name) for name in unresolved},
        "approval_trace": evidence.approval_trace,
        "risk_limits": evidence.risk_limits,
        "kill_switch_proof": evidence.kill_switch_proof,
        "rollback_proof": evidence.rollback_proof,
        "reconciliation_proof": evidence.reconciliation_proof,
        "evidence_freshness": {"fresh": evidence_fresh},
        "replayability_proof": evidence.replayability_proof,
        "final_disarm_proof": evidence.final_disarm_proof,
        "post_trade_journal_path": evidence.post_trade_journal_path,
        "human_review_ready": bool(evidence.human_review_ready),
        "next_safe_action": str(next_safe_action),
        "packet_id": PACKET_ID,
        "mode": "LOCAL_APPLY",
        "safety": safety,
        "candidate_id": evidence.candidate_id,
        "strategy_name": evidence.strategy_name,
        "symbol": evidence.symbol,
        "direction": evidence.direction,
        "walk_forward_status": evidence.walk_forward_status,
        "validation_results": evidence.validation_results,
    }

    if write_reports:
        result["report_path"] = _write_report(result)
    return result


def _required_fields_for_blocker(blocker: str) -> list[str]:
    mapping = {
        "walk_forward_failed": ["walk_forward_status"],
        "paper_evidence_not_ready": ["paper_metrics.total_trades", "paper_metrics.expectancy", "paper_metrics.profit_factor", "paper_metrics.max_drawdown"],
        "mitigation_worsened": ["mitigation_status"],
        "missing_validation_results": ["validation_results"],
        "candidate_not_approved_for_demo_validation": ["candidate_approved", "approved_for_demo_validation"],
        "demo_contract_not_complete": ["demo_validation_contract"],
        "missing_live_readiness_candidate": ["live_readiness_candidate"],
        "missing_approval_trace": ["approval_trace.signed", "approval_trace.reviewed_by"],
        "missing_risk_limits": ["risk_limits"],
        "missing_kill_switch_proof": ["kill_switch_proof"],
        "missing_rollback_proof": ["rollback_proof"],
        "missing_reconciliation_proof": ["reconciliation_proof"],
        "missing_evidence_freshness": ["evidence_timestamp"],
        "missing_replayability_proof": ["replayability_proof"],
        "missing_final_disarm_proof": ["final_disarm_proof"],
        "missing_post_trade_journal_path": ["post_trade_journal_path"],
        "demo_validation_contract_not_complete": ["demo_validation_contract"],
        "one_shot_exception_package_not_review_ready": ["one_shot_exception_package.exception_package_completed"],
        "live_review_certificate_not_review_ready": ["live_review_certificate.certificate_completed"],
        "missing_human_review_ready": ["human_review_ready"],
    }
    return mapping.get(blocker, ["evidence_field"])


def _write_report(payload: dict[str, Any]) -> str:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report = [
        "# AIOS FOREX Consolidated Readiness Blocker Closure V1",
        "",
        f"- candidate_id: {payload.get('candidate_id')}",
        f"- status: {payload.get('status')}",
        f"- ready_for_demo_validation: {payload.get('ready_for_demo_validation')}",
        f"- ready_for_live_review: {payload.get('ready_for_live_review')}",
        "",
        "## Resolved blockers",
        "- " + ", ".join(payload.get("resolved_blockers", [])),
        "",
        "## Unresolved blockers",
        "- " + ", ".join(payload.get("unresolved_blockers", [])),
    ]
    REPORT_PATH.write_text("\n".join(report), encoding="utf-8")
    return str(REPORT_PATH)


def main() -> dict[str, Any]:  # pragma: no cover
    return run_consolidated_readiness_blocker_closure_v1(write_reports=True)


if __name__ == "__main__":  # pragma: no cover
    print(main())
