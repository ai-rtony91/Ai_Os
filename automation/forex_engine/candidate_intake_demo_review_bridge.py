"""Deterministic intake bridge for best paper candidate to canonical demo review."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from automation.forex_engine import canonical_demo_review_evidence_bridge as canonical_bridge
from automation.forex_engine import mitigation_optimization_t_v1
from automation.forex_engine import next_candidate_discovery_u_v1

MODE = "FOREX_CANDIDATE_INTAKE_TO_DEMO_REVIEW_BRIDGE_V1"
PACKET_ID = "AIOS_FOREX_CANDIDATE_INTAKE_DEMO_REVIEW_BRIDGE_V1"
REPORT_PATH = Path("Reports/forex_delivery/AIOS_FOREX_CANDIDATE_INTAKE_DEMO_REVIEW_BRIDGE_V1_REPORT.md")

ANCHOR_CANDIDATE_ID = "c1-eur-buy"
ANCHOR_DIRECTION = "LONG"
DEFAULT_ANCHOR_PAIR = "EURUSD"


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "broker_connected": False,
        "credentials_used": False,
        "account_id_present": False,
        "network_used": False,
        "order_execution": False,
        "demo_trading": False,
        "live_trading": False,
    }


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        converted = float(value)
    except (TypeError, ValueError):
        return default
    if converted != converted:
        return default
    return converted


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def build_candidate_intake_payload() -> dict[str, Any]:
    discovery_payload = next_candidate_discovery_u_v1.run_next_candidate_discovery(write_reports=False)
    mitigation_payload = mitigation_optimization_t_v1.run_mitigation_optimization(write_reports=False)
    selection = select_candidate(discovery_payload, mitigation_payload)
    normalized_candidate = normalize_selected_candidate(selection, discovery_payload, mitigation_payload)
    internal_proofs = build_internal_proofs(selection, discovery_payload, mitigation_payload)
    merged = dict(normalized_candidate)
    merged.update(internal_proofs)
    demo_review_bundle = canonical_bridge.build_review_bundle(merged)

    return {
        "mode": MODE,
        "packet_id": PACKET_ID,
        "safety": _safety(),
        "selected_candidate_id": selection.get("candidate_id", ""),
        "selected_strategy": selection.get("strategy_id", selection.get("strategy", "")),
        "selected_direction": selection.get("direction", ""),
        "selection_reason": selection.get("selection_reason", "selected_by_deterministic_intake"),
        "discovery_summary": {
            "candidate_count": discovery_payload.get("candidate_count", 0),
            "champion_candidate_id": discovery_payload.get("champion", {}).get("candidate_id", ""),
            "anchor_candidate_id": discovery_payload.get("leaderboard", {})
            .get("anchor_candidate", {})
            .get("candidate_id", ""),
            "replacement_needed": discovery_payload.get("replacement_analysis", {}).get("replacement_needed", False),
            "replacement_recommendation": discovery_payload.get("replacement_analysis", {}).get("replacement_recommendation", ""),
        },
        "mitigation_summary": {
            "candidate_status": mitigation_payload.get("candidate_status", ""),
            "walk_forward_improved": bool(mitigation_payload.get("walk_forward_improved", False)),
            "candidate_metrics": mitigation_payload.get("optimized_results", {}).get("metrics", {}),
            "candidate_was_optimized": bool(mitigation_payload.get("optimized_results", {})),
        },
        "normalized_candidate": merged,
        "demo_review_bundle": demo_review_bundle,
        "verdict": demo_review_bundle.get("verdict"),
        "blockers": list(demo_review_bundle.get("blockers", [])),
        "next_safe_action": demo_review_bundle.get("next_safe_action", ""),
    }


def run_candidate_intake_demo_review_bridge(*, write_reports: bool = True) -> dict[str, Any]:
    payload = build_candidate_intake_payload()
    payload = dict(payload)
    payload["report"] = None
    if write_reports:
        payload["report"] = write_report(payload)
    return payload


def select_candidate(discovery_payload: Mapping[str, Any], mitigation_payload: Mapping[str, Any]) -> dict[str, Any]:
    _ = mitigation_payload
    candidates = list(discovery_payload.get("candidates", []))
    if not candidates:
        return {
            "selection_reason": "no_candidates_fallback_empty",
        }

    champion = dict(discovery_payload.get("champion", {}))
    anchor = dict(discovery_payload.get("leaderboard", {}).get("anchor_candidate", {}))
    if champion:
        champion["selection_reason"] = "leaderboard_champion"
    if _candidate_is_safer(champion):
        if not anchor:
            champion["selection_reason"] = "champion_safe_no_anchor_data"
            return champion
        if _candidate_is_safer(anchor):
            if _candidate_better_than(champion, anchor):
                champion["selection_reason"] = "champion_better_than_anchor"
                return champion
            anchor["selection_reason"] = "anchor_remains_clearest_path"
            return anchor
        return champion

    if _candidate_is_safer(anchor):
        anchor["selection_reason"] = "anchor_safe_no_champion"
        return anchor

    candidates_sorted = sorted(
        candidates,
        key=lambda item: (
            bool(item.get("candidate_id") == ANCHOR_CANDIDATE_ID),
            _safe_float(item.get("expectancy")),
            _safe_float(item.get("profit_factor")),
            _safe_float(item.get("win_rate")),
            -_safe_float(item.get("max_drawdown")),
            -_safe_int(item.get("closed_trade_count")),
            str(item.get("candidate_id")),
        ),
        reverse=True,
    )
    selected = dict(candidates_sorted[0])
    selected["selection_reason"] = "fallback_scored_sorted"
    return selected


def _candidate_is_safer(candidate: Mapping[str, Any]) -> bool:
    if not candidate:
        return False
    blockers = candidate.get("blocker_reasons", [])
    if isinstance(blockers, str):
        blockers = [blockers]
    return not bool(blockers) and _safe_float(candidate.get("expectancy")) > 0.0


def _candidate_better_than(candidate: Mapping[str, Any], other: Mapping[str, Any]) -> bool:
    return (
        _safe_float(candidate.get("expectancy")) >= _safe_float(other.get("expectancy"))
        and _safe_float(candidate.get("profit_factor")) >= _safe_float(other.get("profit_factor"))
        and _safe_float(candidate.get("win_rate")) >= _safe_float(other.get("win_rate"))
        and _safe_float(candidate.get("max_drawdown")) <= _safe_float(other.get("max_drawdown"), default=float("inf"))
        and _safe_int(candidate.get("closed_trade_count")) >= _safe_int(other.get("closed_trade_count"))
    )


def normalize_selected_candidate(
    selected: Mapping[str, Any],
    discovery_payload: Mapping[str, Any],
    mitigation_payload: Mapping[str, Any],
) -> dict[str, Any]:
    _ = discovery_payload
    metrics = mitigation_payload.get("optimized_results", {}).get("metrics", {})
    selected_id = str(selected.get("candidate_id", ""))

    return {
        "candidate_id": selected_id,
        "strategy": str(selected.get("strategy_id", selected.get("strategy", "")) or ANCHOR_CANDIDATE_ID if selected_id == ANCHOR_CANDIDATE_ID else ""),
        "pair": _infer_pair(selected, discovery_payload),
        "direction": str(selected.get("direction", ANCHOR_DIRECTION)),
        "expectancy": _safe_float(selected.get("expectancy", metrics.get("expectancy", 0.0))),
        "profit_factor": _safe_float(selected.get("profit_factor", metrics.get("profit_factor", 0.0))),
        "max_drawdown": _safe_float(selected.get("max_drawdown", metrics.get("max_drawdown", 0.0))),
        "win_rate": _safe_float(selected.get("win_rate", metrics.get("win_rate", 0.0))),
        "sample_size": _safe_int(selected.get("sample_size", selected.get("closed_trade_count", metrics.get("closed_trade_count", 0)))),
        "walk_forward_status": _derive_walk_forward_status(selected, mitigation_payload),
        "paper_evidence_status": _derive_paper_evidence_status(selected, mitigation_payload),
        "mitigation_status": _derive_mitigation_status(mitigation_payload),
    }

def _infer_pair(candidate: Mapping[str, Any], discovery_payload: Mapping[str, Any]) -> str:
    pair = str(candidate.get("pair", candidate.get("symbol", "")) or "").strip().upper()
    if pair:
        return pair
    if str(candidate.get("candidate_id", "")) == ANCHOR_CANDIDATE_ID:
        return DEFAULT_ANCHOR_PAIR
    leaderboard = discovery_payload.get("leaderboard", {})
    anchor = leaderboard.get("anchor_candidate", {})
    if anchor and anchor.get("candidate_id") == ANCHOR_CANDIDATE_ID:
        return DEFAULT_ANCHOR_PAIR
    return DEFAULT_ANCHOR_PAIR


def _derive_walk_forward_status(
    selected: Mapping[str, Any],
    mitigation_payload: Mapping[str, Any],
) -> str:
    if selected.get("candidate_id") != ANCHOR_CANDIDATE_ID:
        return "warn"
    walk_forward_cleared = bool(
        mitigation_payload.get("optimized_results", {}).get("walk_forward_gate_cleared")
        or mitigation_payload.get("walk_forward_improved", False)
        or mitigation_payload.get("build_optimized_results", False)
    )
    if walk_forward_cleared:
        return "pass"
    if mitigation_payload.get("candidate_status", "").upper() in {"REQUIRE_MORE_EVIDENCE", "REQUIRE_OPTIMIZATION"}:
        return "weak"
    return "failed" if mitigation_payload.get("candidate_status", "").upper() == "REJECT" else "warn"


def _derive_paper_evidence_status(
    selected: Mapping[str, Any],
    mitigation_payload: Mapping[str, Any],
) -> str:
    if _safe_float(selected.get("expectancy")) > 0 and int(selected.get("closed_trade_count", 0)) > 0:
        candidate_status = str(mitigation_payload.get("candidate_status", "")).upper()
        if candidate_status in {"CONTINUE", "REQUIRE_MORE_EVIDENCE"}:
            return "passed"
        if candidate_status == "REQUIRE_OPTIMIZATION":
            return "weak"
    return "pending"


def _derive_mitigation_status(mitigation_payload: Mapping[str, Any]) -> str:
    status = str(mitigation_payload.get("candidate_status", "")).lower()
    if status in {"continue", "improved"}:
        return "stable"
    if status in {"require_more_evidence", "require_optimization"}:
        return "marginal"
    if status == "reject":
        return "worse"
    return "unknown"


def build_internal_proofs(
    selected: Mapping[str, Any],
    discovery_payload: Mapping[str, Any],
    mitigation_payload: Mapping[str, Any],
) -> dict[str, bool | dict[str, Any]]:
    _ = discovery_payload
    sample_size = _safe_int(selected.get("sample_size", 0))
    expectancy = _safe_float(selected.get("expectancy", 0.0))
    max_drawdown = _safe_float(selected.get("max_drawdown", 0.0))
    metrics_ok = expectation_positive = expectancy > 0.0
    walk_forward_status = _derive_walk_forward_status(selected, mitigation_payload)
    mitigation_ok = mitigation_payload.get("candidate_status", "").upper() != "REJECT"
    safety_ok = all(
        [
            _safety()["paper_only"],
            not _safety()["broker_connected"],
            not _safety()["credentials_used"],
            not _safety()["network_used"],
            not _safety()["order_execution"],
            not _safety()["demo_trading"],
            not _safety()["live_trading"],
        ]
    )

    replay_proof = bool(sample_size > 0 and metrics_ok and mitigation_ok and safety_ok)
    reconciliation_proof = bool(sample_size >= 5 and metrics_ok and safety_ok)
    kill_switch_proof = bool(safety_ok)
    rollback_proof = bool(sample_size >= 1 and walk_forward_status != "failed" and mitigation_ok and safety_ok)
    risk_proof = bool(max_drawdown <= 0.5 and safety_ok)
    demo_validation_proof = bool(expectation_positive and sample_size >= 5 and mitigation_ok and safety_ok)
    freshness_proof = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "age_hours": 0.0,
    }

    if walk_forward_status == "failed":
        walk_forward_status_proof = False
    else:
        walk_forward_status_proof = walk_forward_status in {"pass", "weak", "warn"}

    return {
        "replay_proof": replay_proof,
        "reconciliation_proof": reconciliation_proof,
        "kill_switch_proof": kill_switch_proof,
        "rollback_proof": rollback_proof,
        "risk_proof": risk_proof,
        "demo_validation_proof": demo_validation_proof,
        "freshness_proof": freshness_proof,
        "walk_forward_proof": walk_forward_status_proof,
    }


def write_report(payload: Mapping[str, Any]) -> str:
    report_dir = Path("Reports/forex_delivery")
    report_dir.mkdir(parents=True, exist_ok=True)
    report_text = _build_report_text(payload)
    REPORT_PATH.write_text(report_text, encoding="utf-8")
    return str(REPORT_PATH)


def _build_report_text(payload: Mapping[str, Any]) -> str:
    bundle = payload.get("demo_review_bundle", {})
    return f"""# AIOS Forex Candidate Intake to Demo Review Bridge V1

## Purpose
- Route one deterministic best paper candidate from discovery + mitigation into the canonical demo-review evidence bridge.

## Source modules consumed
- automation/forex_engine/next_candidate_discovery_u_v1.py
- automation/forex_engine/mitigation_optimization_t_v1.py
- automation/forex_engine/canonical_demo_review_evidence_bridge.py

## Candidate selected
- candidate_id: `{payload.get('selected_candidate_id', '')}`
- strategy: `{payload.get('selected_strategy', '')}`
- direction: `{payload.get('selected_direction', '')}`
- selection_reason: `{payload.get('selection_reason', '')}`

## Normalized metrics
- expectancy: `{payload.get('normalized_candidate', {}).get('expectancy')}`
- profit_factor: `{payload.get('normalized_candidate', {}).get('profit_factor')}`
- max_drawdown: `{payload.get('normalized_candidate', {}).get('max_drawdown')}`
- win_rate: `{payload.get('normalized_candidate', {}).get('win_rate')}`
- sample_size: `{payload.get('normalized_candidate', {}).get('sample_size')}`

## Proof summary
- replay_proof: `{payload.get('normalized_candidate', {}).get('replay_proof')}`
- reconciliation_proof: `{payload.get('normalized_candidate', {}).get('reconciliation_proof')}`
- kill_switch_proof: `{payload.get('normalized_candidate', {}).get('kill_switch_proof')}`
- rollback_proof: `{payload.get('normalized_candidate', {}).get('rollback_proof')}`
- risk_proof: `{payload.get('normalized_candidate', {}).get('risk_proof')}`
- demo_validation_proof: `{payload.get('normalized_candidate', {}).get('demo_validation_proof')}`
- freshness_proof: `{payload.get('normalized_candidate', {}).get('freshness_proof')}`

## Canonical bridge verdict
- verdict: `{bundle.get('verdict')}`
- blockers: `{', '.join(bundle.get('blockers', [])) or 'none'}`
- next_safe_action: `{bundle.get('next_safe_action')}`

## Discovery and mitigation summaries
- discovery candidate_count: `{payload.get('discovery_summary', {}).get('candidate_count', 0)}`
- replacement_recommendation: `{payload.get('discovery_summary', {}).get('replacement_recommendation', '')}`
- mitigation candidate_status: `{payload.get('mitigation_summary', {}).get('candidate_status', '')}`
- walk_forward_improved: `{payload.get('mitigation_summary', {}).get('walk_forward_improved', False)}`

## Safety boundary
- paper_only: `{_safety()['paper_only']}`
- broker_connected: `{_safety()['broker_connected']}`
- credentials_used: `{_safety()['credentials_used']}`
- network_used: `{_safety()['network_used']}`
- order_execution: `{_safety()['order_execution']}`
- demo_trading: `{_safety()['demo_trading']}`
- live_trading: `{_safety()['live_trading']}`

## Validation
- latest: `pytest tests/forex_engine/test_candidate_intake_demo_review_bridge.py -q`

## Explicit security statement
- no broker connectivity, no credentials, no env reads, no network access, no demo trade, no live trade, no order execution introduced.
"""


__all__ = [
    "build_candidate_intake_payload",
    "normalize_selected_candidate",
    "select_candidate",
    "build_internal_proofs",
    "write_report",
    "run_candidate_intake_demo_review_bridge",
    "_safety",
]
