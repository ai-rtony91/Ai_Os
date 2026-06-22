"""Deterministic paper-only journey wrapper for candidate selection and review-chain orchestration."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from automation.forex_engine import candidate_intake_demo_review_bridge
from automation.forex_engine import review_chain_orchestrator
from automation.forex_engine import canonical_demo_review_evidence_bridge

MODE = "FOREX_REVIEW_CHAIN_END_TO_END_CANDIDATE_JOURNEY_V1"
PACKET_ID = "AIOS_FOREX_REVIEW_CHAIN_END_TO_END_CANDIDATE_JOURNEY_V1"
REPORT_PATH = Path("Reports/forex_delivery/AIOS_FOREX_REVIEW_CHAIN_END_TO_END_CANDIDATE_JOURNEY_V1_REPORT.md")

JOURNEY_REVIEW_READY = "JOURNEY_REVIEW_READY"
JOURNEY_INCOMPLETE = "JOURNEY_INCOMPLETE"
JOURNEY_REJECTED = "JOURNEY_REJECTED"
JOURNEY_BLOCKED = "JOURNEY_BLOCKED"


def _safe_get(mapping: dict[str, Any], aliases: Iterable[str], default: Any = "") -> Any:
    for alias in aliases:
        if alias in mapping:
            return mapping[alias]
    return default


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


def build_review_chain_state(candidate_payload: dict[str, Any]) -> dict[str, Any]:
    safety = _safe_get(candidate_payload, ("safety",), default=_safety())
    if not isinstance(safety, dict):
        safety = _safety()

    candidate_verdict = str(_safe_get(candidate_payload, ("verdict",), default=""))
    candidate_ready = candidate_verdict == canonical_demo_review_evidence_bridge.DEMO_REVIEW_READY
    state: dict[str, Any] = {
        "candidate_intake_demo_review": candidate_payload,
        "live_readiness_candidate": candidate_ready,
        "candidate_ready": candidate_ready,
        "human_live_review_ready": candidate_ready,
    }
    if bool(safety.get("broker_connected")):
        state["unsafe_broker_connection_detected"] = True
    if bool(safety.get("network_used")):
        state["unsafe_network_access_detected"] = True
    if bool(safety.get("credentials_used")):
        state["unsafe_credential_access_detected"] = True
    if bool(safety.get("account_id_present")):
        state["unsafe_account_identifier_access_detected"] = True
    if bool(safety.get("order_execution")):
        state["unsafe_order_execution_detected"] = True
    if bool(safety.get("demo_trading")):
        state["demo_trading_detected"] = True
    if bool(safety.get("live_trading")):
        state["live_trading_authorization_detected"] = True
    return state


def classify_final_verdict(
    candidate_payload: dict[str, Any],
    review_result: dict[str, Any],
) -> tuple[str, str, bool]:
    candidate_verdict = str(_safe_get(candidate_payload, ("verdict",), default="")).strip()
    review_status = str(_safe_get(review_result, ("review_chain_status",), default=""))
    safety_blocked = any(
        bool(_safe_get(review_result.get("safety", {}), key, default=False))
        for key in (
            "broker_connection_active",
            "network_access",
            "credentials_accessed",
            "account_identifiers_accessed",
            "order_execution_enabled",
            "live_trading_authorized",
            "execution_authority_granted",
            "capital_allocated",
        )
    )
    if safety_blocked:
        return JOURNEY_BLOCKED, review_result.get("next_safe_action", ""), False
    if review_status == review_chain_orchestrator.REVIEW_CHAIN_REVIEW_READY and candidate_verdict == canonical_demo_review_evidence_bridge.DEMO_REVIEW_READY:
        return JOURNEY_REVIEW_READY, review_result.get("next_safe_action", ""), True
    if review_status == review_chain_orchestrator.REVIEW_CHAIN_REJECTED:
        return JOURNEY_REJECTED, review_result.get("next_safe_action", ""), False
    if review_status == review_chain_orchestrator.REVIEW_CHAIN_BLOCKED:
        return JOURNEY_BLOCKED, review_result.get("next_safe_action", ""), False
    if review_status == review_chain_orchestrator.REVIEW_CHAIN_INCOMPLETE:
        return JOURNEY_INCOMPLETE, review_result.get("next_safe_action", ""), False
    return JOURNEY_INCOMPLETE, review_result.get("next_safe_action", ""), False


def run_review_chain_end_to_end_candidate_journey(*, write_reports: bool = True) -> dict[str, Any]:
    candidate_payload = candidate_intake_demo_review_bridge.run_candidate_intake_demo_review_bridge(write_reports=False)
    chain_state = build_review_chain_state(candidate_payload)
    review_result = review_chain_orchestrator.orchestrate_forex_review_chain(chain_state)

    candidate_verdict = str(candidate_payload.get("verdict", ""))
    final_verdict, final_next_safe_action, journey_completed = classify_final_verdict(
        candidate_payload,
        review_result,
    )

    result: dict[str, Any] = {
        "mode": MODE,
        "packet_id": PACKET_ID,
        "safety": {
            **_safety(),
            **candidate_payload.get("safety", {}),
            "live_trading_authorized": False,
        },
        "selected_candidate_id": str(candidate_payload.get("selected_candidate_id", "")),
        "selected_strategy": str(candidate_payload.get("selected_strategy", "")),
        "selected_direction": str(candidate_payload.get("selected_direction", "")),
        "candidate_selection_reason": str(candidate_payload.get("selection_reason", "")),
        "candidate_demo_review_verdict": candidate_verdict,
        "candidate_demo_review_blockers": list(candidate_payload.get("blockers", [])),
        "candidate_demo_review_next_safe_action": str(candidate_payload.get("next_safe_action", "")),
        "review_chain_status": str(review_result.get("review_chain_status", "")),
        "review_chain_blockers": list(review_result.get("blockers", [])),
        "review_chain_next_safe_action": str(review_result.get("next_safe_action", "")),
        "review_chain_required_next_packets": list(review_result.get("required_next_packets", [])),
        "human_live_review_ready": bool(review_result.get("human_live_review_ready", False)),
        "live_micro_trade_review_ready": bool(review_result.get("live_micro_trade_review_ready", False)),
        "live_trading_authorized": bool(review_result.get("live_trading_authorized", False)),
        "journey_completed": bool(journey_completed),
        "final_verdict": final_verdict,
        "final_next_safe_action": final_next_safe_action,
        "source_modules": [
            "automation/forex_engine/candidate_intake_demo_review_bridge.py",
            "automation/forex_engine/canonical_demo_review_evidence_bridge.py",
            "automation/forex_engine/review_chain_orchestrator.py",
        ],
    }

    if write_reports:
        result["report"] = write_report(result)
    else:
        result["report"] = None
    return result


def write_report(payload: dict[str, Any]) -> str:
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    report_text = _build_report_text(payload)
    REPORT_PATH.write_text(report_text, encoding="utf-8")
    return str(REPORT_PATH)


def _build_report_text(payload: dict[str, Any]) -> str:
    return f"""# AIOS Forex Review Chain End-to-End Candidate Journey V1

## Purpose
Produce one deterministic journey payload that runs candidate intake, canonical demo-review evidence consolidation, and review-chain orchestration.

## Files created
- `automation/forex_engine/review_chain_end_to_end_candidate_journey.py`
- `tests/forex_engine/test_review_chain_end_to_end_candidate_journey.py`
- `Reports/forex_delivery/AIOS_FOREX_REVIEW_CHAIN_END_TO_END_CANDIDATE_JOURNEY_V1_REPORT.md`

## Source modules consumed
- automation/forex_engine/candidate_intake_demo_review_bridge.py
- automation/forex_engine/canonical_demo_review_evidence_bridge.py
- automation/forex_engine/review_chain_orchestrator.py

## Journey flow
1. Run candidate intake bridge (paper-only, no reports).
2. Build a conservative review-chain state from candidate payload and safety flags.
3. Pass the state to review_chain_orchestrator.
4. Classify final journey verdict from candidate verdict + chain status.

## Selected candidate
- candidate_id: `{payload.get('selected_candidate_id', '')}`
- strategy: `{payload.get('selected_strategy', '')}`
- direction: `{payload.get('selected_direction', '')}`
- selection_reason: `{payload.get('candidate_selection_reason', '')}`

## Candidate verdict
- canonical verdict: `{payload.get('candidate_demo_review_verdict', '')}`
- blockers: `{', '.join(payload.get('candidate_demo_review_blockers', []) ) or 'none'}`
- next_safe_action: `{payload.get('candidate_demo_review_next_safe_action', '')}`

## Review-chain status
- status: `{payload.get('review_chain_status', '')}`
- blockers: `{', '.join(payload.get('review_chain_blockers', []) ) or 'none'}`
- next_safe_action: `{payload.get('review_chain_next_safe_action', '')}`

## Final journey verdict
- final_verdict: `{payload.get('final_verdict', '')}`
- final_next_safe_action: `{payload.get('final_next_safe_action', '')}`
- journey_completed: `{payload.get('journey_completed', False)}`

## Blockers
- review-chain blockers preserved: `{', '.join(payload.get('review_chain_blockers', []) ) or 'none'}`
- candidate blockers preserved: `{', '.join(payload.get('candidate_demo_review_blockers', []) ) or 'none'}`

## Safety boundary
- paper_only: `{payload.get('safety', {}).get('paper_only', False)}`
- broker_connected: `{payload.get('safety', {}).get('broker_connected', False)}`
- credentials_used: `{payload.get('safety', {}).get('credentials_used', False)}`
- network_used: `{payload.get('safety', {}).get('network_used', False)}`
- order_execution: `{payload.get('safety', {}).get('order_execution', False)}`
- demo_trading: `{payload.get('safety', {}).get('demo_trading', False)}`
- live_trading: `{payload.get('safety', {}).get('live_trading', False)}`

## Validation
- placeholder

## Explicit security statement
No broker connectivity, no credentials, no env reads, no network access, no demo trade, no live trade, no order execution introduced.
"""


__all__ = [
    "build_review_chain_state",
    "classify_final_verdict",
    "run_review_chain_end_to_end_candidate_journey",
    "write_report",
]

