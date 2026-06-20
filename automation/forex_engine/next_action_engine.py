"""Canonical next-action selector for canonical forex paper spine transitions."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Union

NEXT_ACTION_MODE = "PAPER_ONLY"
NEXT_ACTION_ALLOWED = "allowed"
NEXT_ACTION_BLOCKED = "blocked"
NEXT_ACTION_REQUIRES_APPROVAL = "requires_approval"

NEXT_PACKET_BUCKETS = [
    "FOREX-EVIDENCE-LEDGER",
    "FOREX-SESSION-REPLAY",
    "AIOS-FOREX-DASHBOARD-TRUTH-WIRING",
    "FOREX-LONG-RUN-PAPER-SUPERVISOR",
    "AIOS-FOREX-SELF-IMPROVEMENT",
    "FOREX-DEMO-CONNECTOR-READONLY",
    "FOREX-DEMO-ORDER-MAPPING",
    "FOREX-DEMO-RECONCILIATION",
    "FOREX-PAPER-TO-DEMO-PROMOTION",
    "FOREX-DEMO-MULTI-TRADE-RUNNER",
    "FOREX-LIVE-READINESS-REVIEW",
    "FOREX-FIRST-LIVE-MICRO-TRADE-PROOF",
    "FOREX-LIVE-MULTI-TRADE-EXPANSION",
]

PROTECTED_TERMS = (
    "live",
    "broker",
    "credential",
    "credentials",
    "real order",
    "real_order",
    "order submit",
    "account id",
    "api key",
    "apikey",
    "oanda",
    "webhook",
)


def _to_bool(value: Any, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    return default


def _as_list(value: Any) -> List[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, set):
        return list(value)
    return [value]


def _contains_protected_term(values: Iterable[Any]) -> List[str]:
    matched: List[str] = []
    seen = set()
    for raw in values:
        text = str(raw).lower()
        for term in PROTECTED_TERMS:
            if term in text and term not in seen:
                seen.add(term)
                matched.append(term)
    return matched


def _safe_module_present(modules: Sequence[str], names: Sequence[str]) -> bool:
    module_set = {str(name).lower() for name in modules}
    return any(name.lower() in module_set for name in names)


def _safe_docs_present(docs: Sequence[str], names: Sequence[str]) -> bool:
    doc_set = {str(name).lower() for name in docs}
    return any(name.lower() in doc_set for name in names)


def _pick_missing_spine(repo_state: Mapping[str, Any]) -> Optional[str]:
    modules = _as_list(repo_state.get("modules"))
    docs = _as_list(repo_state.get("docs"))

    if not _safe_module_present(modules, ["evidence_ledger", "automation/forex_engine/evidence_ledger.py"]):
        return "FOREX-EVIDENCE-LEDGER"
    if not _safe_module_present(modules, ["session_replay", "automation/forex_engine/session_replay.py"]):
        return "FOREX-SESSION-REPLAY"
    if not _safe_docs_present(
        docs, ["AIOS_FOREX_DASHBOARD_TRUTH_WIRING.md", "AIOS_FOREX_DASHBOARD_TRUTH_WIRING"]
    ):
        return "AIOS-FOREX-DASHBOARD-TRUTH-WIRING"
    return None


def _is_demo_ready(evidence_summary: Mapping[str, Any]) -> bool:
    missing = _as_list(evidence_summary.get("missing_evidence_warnings"))
    if missing:
        return False
    sessions = evidence_summary.get("paper_session_count", evidence_summary.get("sessions", 0))
    trades = evidence_summary.get("paper_trade_count", evidence_summary.get("trades", 0))
    return bool(sessions and sessions >= 1 and trades and trades >= 1)


def _is_demo_eligible(evidence_summary: Mapping[str, Any]) -> bool:
    drawdown = evidence_summary.get("drawdown", 0) or 0
    return _is_demo_ready(evidence_summary) and drawdown >= 0


def recommend_next_action(
    repo_state: Optional[Mapping[str, Any]] = None,
    evidence_summary: Optional[Mapping[str, Any]] = None,
    completed_packets: Optional[Iterable[str]] = None,
    blockers: Optional[Iterable[str]] = None,
    requested_goal: Optional[str] = None,
    metadata: Optional[Mapping[str, Any]] = None,
) -> Dict[str, Any]:
    repo_state = dict(repo_state or {})
    evidence_summary = dict(evidence_summary or {})
    completed = {str(p).upper() for p in _as_list(completed_packets)}
    base_blockers = list(_as_list(blockers))
    requested = str(requested_goal or "")
    all_blocker_tokens: List[str] = []

    all_blocker_tokens.extend(base_blockers)
    if requested:
        all_blocker_tokens.append(requested)

    protected = _contains_protected_term(all_blocker_tokens)
    protected_action_detected = bool(protected)

    missing_prerequisites: List[str] = []

    if protected:
        # Always require explicit approval for protected actions.
        return {
            "allowed": False,
            "decision": NEXT_ACTION_REQUIRES_APPROVAL,
            "mode": NEXT_ACTION_MODE,
            "next_packet_bucket": "FOREX-LIVE-READINESS-REVIEW",
            "priority": 100,
            "reason": "protected_action_request_detected",
            "blockers": protected,
            "protected_action_detected": True,
            "approval_required": True,
            "approval_reason": "live_or_secret_or_broker_or_api_action_blocked_in_paper_orchestrator",
            "missing_prerequisites": [],
            "safe_to_auto_build": False,
            "no_live_action_stop": True,
            "evidence_used": {
                "requested_goal": requested or None,
                "blockers": list(base_blockers),
                "missing_spine": _pick_missing_spine(repo_state),
            },
            "recommended_validator_scope": "approval_and_safety_review",
            "safety": {
                "paper_only": True,
                "broker": False,
                "live_trading": False,
                "credentials": False,
                "real_orders": False,
                "network_access": False,
            },
            "next_safe_action": "REQUEST_APPROVAL_BEFORE_ANY_NON_PAPER_ACTION",
            "metadata": dict(metadata or {}),
        }

    missing_spine = _pick_missing_spine(repo_state)
    if missing_spine:
        missing_prerequisites.append(missing_spine)
        return {
            "allowed": False,
            "decision": NEXT_ACTION_BLOCKED,
            "mode": NEXT_ACTION_MODE,
            "next_packet_bucket": missing_spine,
            "priority": 95,
            "reason": "missing_spine_packet",
            "blockers": base_blockers,
            "protected_action_detected": False,
            "approval_required": False,
            "approval_reason": "",
            "missing_prerequisites": missing_prerequisites,
            "safe_to_auto_build": True,
            "no_live_action_stop": False,
            "evidence_used": {
                "repo_modules": _as_list(repo_state.get("modules")),
                "repo_docs": _as_list(repo_state.get("docs")),
                "missing_spine": missing_spine,
            },
            "recommended_validator_scope": "spine_validation",
            "safety": {
                "paper_only": True,
                "broker": False,
                "live_trading": False,
                "credentials": False,
                "real_orders": False,
                "network_access": False,
            },
            "next_safe_action": f"IMPLEMENT_{missing_spine}",
            "metadata": dict(metadata or {}),
        }

    if "FOREX-LONG-RUN-PAPER-SUPERVISOR" not in completed:
        return {
            "allowed": True,
            "decision": NEXT_ACTION_ALLOWED,
            "mode": NEXT_ACTION_MODE,
            "next_packet_bucket": "FOREX-LONG-RUN-PAPER-SUPERVISOR",
            "priority": 90,
            "reason": "paper_spine_present_without_long_run_supervisor",
            "blockers": base_blockers,
            "protected_action_detected": False,
            "approval_required": False,
            "approval_reason": "",
            "missing_prerequisites": [],
            "safe_to_auto_build": True,
            "no_live_action_stop": False,
            "evidence_used": {
                "completed_packets": sorted(completed),
                "evidence_summary": evidence_summary,
            },
            "recommended_validator_scope": "paper_supervisor_guardrails",
            "safety": {
                "paper_only": True,
                "broker": False,
                "live_trading": False,
                "credentials": False,
                "real_orders": False,
                "network_access": False,
            },
            "next_safe_action": "RUN_PAPER_LONG_FORM_VALIDATION_CYCLE",
            "metadata": dict(metadata or {}),
        }

    session_count = evidence_summary.get("paper_session_count", 0) or evidence_summary.get("sessions", 0) or 0
    trade_count = evidence_summary.get("paper_trade_count", 0) or evidence_summary.get("trades", 0) or 0

    if session_count < 1 or trade_count < 1 or not _is_demo_ready(evidence_summary):
        return {
            "allowed": True,
            "decision": NEXT_ACTION_ALLOWED,
            "mode": NEXT_ACTION_MODE,
            "next_packet_bucket": "FOREX-LONG-RUN-PAPER-SUPERVISOR",
            "priority": 80,
            "reason": "paper_evidence_volume_not_mature_for_demo",
            "blockers": base_blockers,
            "protected_action_detected": False,
            "approval_required": False,
            "approval_reason": "",
            "missing_prerequisites": [],
            "safe_to_auto_build": True,
            "no_live_action_stop": False,
            "evidence_used": {
                "evidence_summary": evidence_summary,
            },
            "recommended_validator_scope": "paper_supervisor_guardrails",
            "safety": {
                "paper_only": True,
                "broker": False,
                "live_trading": False,
                "credentials": False,
                "real_orders": False,
                "network_access": False,
            },
            "next_safe_action": "PUBLISH_MORE_PAPER_SESSION_EVIDENCE",
            "metadata": dict(metadata or {}),
        }

    if _is_demo_eligible(evidence_summary) and "FOREX-DEMO-CONNECTOR-READONLY" not in completed:
        return {
            "allowed": True,
            "decision": NEXT_ACTION_ALLOWED,
            "mode": NEXT_ACTION_MODE,
            "next_packet_bucket": "FOREX-DEMO-CONNECTOR-READONLY",
            "priority": 70,
            "reason": "paper_evidence_mature_ready_for_demo_connector_readonly",
            "blockers": base_blockers,
            "protected_action_detected": False,
            "approval_required": False,
            "approval_reason": "",
            "missing_prerequisites": [],
            "safe_to_auto_build": True,
            "no_live_action_stop": False,
            "evidence_used": {
                "evidence_summary": evidence_summary,
            },
            "recommended_validator_scope": "demo_connector_readonly_smoke",
            "safety": {
                "paper_only": True,
                "broker": False,
                "live_trading": False,
                "credentials": False,
                "real_orders": False,
                "network_access": False,
            },
            "next_safe_action": "RUN_DEMO_CONNECTOR_READONLY",
            "metadata": dict(metadata or {}),
        }

    if "FOREX-DEMO-CONNECTOR-READONLY" in completed and "FOREX-DEMO-ORDER-MAPPING" not in completed:
        return {
            "allowed": True,
            "decision": NEXT_ACTION_ALLOWED,
            "mode": NEXT_ACTION_MODE,
            "next_packet_bucket": "FOREX-DEMO-ORDER-MAPPING",
            "priority": 60,
            "reason": "demo_readonly_completed_mapping_missing",
            "blockers": base_blockers,
            "protected_action_detected": False,
            "approval_required": False,
            "approval_reason": "",
            "missing_prerequisites": [],
            "safe_to_auto_build": True,
            "no_live_action_stop": False,
            "evidence_used": {
                "completed_packets": sorted(completed),
            },
            "recommended_validator_scope": "demo_order_mapping_validation",
            "safety": {
                "paper_only": True,
                "broker": False,
                "live_trading": False,
                "credentials": False,
                "real_orders": False,
                "network_access": False,
            },
            "next_safe_action": "IMPLEMENT_DEMO_ORDER_MAPPING",
            "metadata": dict(metadata or {}),
        }

    if "FOREX-DEMO-ORDER-MAPPING" in completed and "FOREX-DEMO-RECONCILIATION" not in completed:
        return {
            "allowed": True,
            "decision": NEXT_ACTION_ALLOWED,
            "mode": NEXT_ACTION_MODE,
            "next_packet_bucket": "FOREX-DEMO-RECONCILIATION",
            "priority": 50,
            "reason": "demo_mapping_completed_reconciliation_missing",
            "blockers": base_blockers,
            "protected_action_detected": False,
            "approval_required": False,
            "approval_reason": "",
            "missing_prerequisites": [],
            "safe_to_auto_build": True,
            "no_live_action_stop": False,
            "evidence_used": {
                "completed_packets": sorted(completed),
            },
            "recommended_validator_scope": "demo_reconciliation_validation",
            "safety": {
                "paper_only": True,
                "broker": False,
                "live_trading": False,
                "credentials": False,
                "real_orders": False,
                "network_access": False,
            },
            "next_safe_action": "IMPLEMENT_DEMO_RECONCILIATION",
            "metadata": dict(metadata or {}),
        }

    if "FOREX-DEMO-RECONCILIATION" in completed and not _to_bool(evidence_summary.get("demo_ready")):
        return {
            "allowed": True,
            "decision": NEXT_ACTION_ALLOWED,
            "mode": NEXT_ACTION_MODE,
            "next_packet_bucket": "FOREX-PAPER-TO-DEMO-PROMOTION",
            "priority": 40,
            "reason": "demo_integration_incomplete_promotion_proofs_missing",
            "blockers": base_blockers,
            "protected_action_detected": False,
            "approval_required": False,
            "approval_reason": "",
            "missing_prerequisites": [],
            "safe_to_auto_build": True,
            "no_live_action_stop": False,
            "evidence_used": {
                "evidence_summary": evidence_summary,
                "completed_packets": sorted(completed),
            },
            "recommended_validator_scope": "paper_to_demo_promotion_review",
            "safety": {
                "paper_only": True,
                "broker": False,
                "live_trading": False,
                "credentials": False,
                "real_orders": False,
                "network_access": False,
            },
            "next_safe_action": "RUN_DEMO_PROMOTION_REVIEW",
            "metadata": dict(metadata or {}),
        }

    if "AIOS-FOREX-SELF-IMPROVEMENT" not in completed:
        return {
            "allowed": True,
            "decision": NEXT_ACTION_ALLOWED,
            "mode": NEXT_ACTION_MODE,
            "next_packet_bucket": "AIOS-FOREX-SELF-IMPROVEMENT",
            "priority": 30,
            "reason": "demo_pipeline_complete_recommend_continual_improvement",
            "blockers": base_blockers,
            "protected_action_detected": False,
            "approval_required": False,
            "approval_reason": "",
            "missing_prerequisites": [],
            "safe_to_auto_build": True,
            "no_live_action_stop": False,
            "evidence_used": {
                "completed_packets": sorted(completed),
                "evidence_summary": evidence_summary,
            },
            "recommended_validator_scope": "self_improvement_review",
            "safety": {
                "paper_only": True,
                "broker": False,
                "live_trading": False,
                "credentials": False,
                "real_orders": False,
                "network_access": False,
            },
            "next_safe_action": "START_SELF_IMPROVEMENT",
            "metadata": dict(metadata or {}),
        }

    return {
        "allowed": True,
        "decision": NEXT_ACTION_ALLOWED,
        "mode": NEXT_ACTION_MODE,
        "next_packet_bucket": "AIOS-FOREX-SELF-IMPROVEMENT",
        "priority": 10,
        "reason": "all_guardrails_met__self_improvement_cycle_continues",
        "blockers": base_blockers,
        "protected_action_detected": False,
        "approval_required": False,
        "approval_reason": "",
        "missing_prerequisites": [],
        "safe_to_auto_build": True,
        "no_live_action_stop": False,
        "evidence_used": {
            "evidence_summary": evidence_summary,
            "completed_packets": sorted(completed),
        },
        "recommended_validator_scope": "continuous_improvement_review",
        "safety": {
            "paper_only": True,
            "broker": False,
            "live_trading": False,
            "credentials": False,
            "real_orders": False,
            "network_access": False,
        },
        "next_safe_action": "CONTINUE_SELF_IMPROVEMENT",
        "metadata": dict(metadata or {}),
    }
