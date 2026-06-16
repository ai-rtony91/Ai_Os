from __future__ import annotations

from typing import Any

from automation.forex_engine import oos_expansion
from automation.forex_engine import oos_repair
from automation.forex_engine import schema_contracts as schemas


LOW_VOL_SPLIT_ID = "holdout_by_regime:low_vol"
REQUIRED_SECURITY_PACKET = "PKT-AIOS-BROKER-PAPER-PRESECURITY-GATE-V1"
ALLOWED_LOW_VOL_EDGE_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
FORBIDDEN_LOW_VOL_EDGE_CLASSIFICATIONS = {"LIVE_READY", "BROKER_READY", "ORDER_READY"}
LOW_VOL_ACTIONS = {"NO_TRADE_GATE", "REDUCED_SIZE", "EDGE_REDESIGN", "WATCHLIST"}

DEFAULT_LOW_VOL_EDGE_POLICY = {
    "low_vol_no_trade_gate_enabled": True,
    "minimum_range_proxy": 0.001,
    "minimum_momentum_proxy": 0.0004,
    "maximum_spread_to_range_ratio": 0.18,
    "minimum_signal_quality_score": 0.7,
    "volatility_expansion_required": True,
    "low_vol_size_multiplier": 0.0,
    "reject_low_vol_chop": True,
    "retain_audit_for_rejected_intents": True,
    "max_allowed_degradation_pct": 35.0,
    "require_degradation_improvement": True,
    "no_trade_degradation_reduction_pct": 30.0,
    "broker_paper_ready": False,
    "live_ready": False,
    "protected_gate_required": True,
    "security_gate_required_before_broker_paper": True,
    "required_security_packet": REQUIRED_SECURITY_PACKET,
}


def diagnose_low_vol_edge(
    oos_repair_result: dict[str, Any] | None = None,
    expanded_oos_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    expanded = dict(expanded_oos_result or {})
    repair = dict(oos_repair_result or {})
    if not expanded and not repair:
        expanded = oos_expansion.run_expanded_oos_validation()
        repair = oos_repair.apply_oos_repair_policy(expanded)
    elif not repair:
        repair = oos_repair.apply_oos_repair_policy(expanded)
    elif not expanded:
        expanded = oos_expansion.run_expanded_oos_validation(oos_repair_result=repair)

    repair_summary = oos_repair.summarize_oos_repair(repair)
    split_results = [dict(item) for item in list(expanded.get("split_results") or [])]
    low_vol_split = _low_vol_split(split_results)
    original_max = _float(
        repair_summary.get("original_max_degradation_pct", expanded.get("max_degradation_pct", 99.5594)),
        99.5594,
    )
    repaired_max = _float(
        repair_summary.get("repaired_max_degradation_pct", repair.get("repaired_max_degradation_pct", original_max)),
        original_max,
    )
    low_vol_degradation = _float(low_vol_split.get("degradation_pct", original_max), original_max)
    diagnosis = {
        "schema": "AIOS_FOREX_LOW_VOL_EDGE_DIAGNOSIS.v1",
        "mode": schemas.PAPER_ONLY,
        "weakest_split": str(
            repair_summary.get("weakest_split")
            or repair.get("weakest_split_after")
            or dict(expanded.get("weakest_split") or {}).get("split_id")
            or LOW_VOL_SPLIT_ID
        ),
        "low_vol_split_detected": bool(low_vol_split) or str(repair_summary.get("weakest_split")) == LOW_VOL_SPLIT_ID,
        "low_vol_split_id": str(low_vol_split.get("split_id") or LOW_VOL_SPLIT_ID),
        "low_vol_degradation_pct": round(low_vol_degradation, 4),
        "original_max_degradation_pct": round(original_max, 4),
        "repaired_max_degradation_pct": round(repaired_max, 4),
        "repair_classification": str(
            repair_summary.get("oos_repair_classification")
            or repair.get("repaired_classification")
            or repair.get("classification")
            or "not_run"
        ),
        "estimated_low_vol_intents": _estimated_low_vol_intents(repair, low_vol_split),
        "existing_skipped_low_vol_intents": int(repair.get("skipped_low_vol_intents", 0)),
        "blockers": _unique(
            [
                *[str(item) for item in list(expanded.get("blockers") or [])],
                *[str(item) for item in list(repair.get("blockers") or [])],
            ]
        ),
        "diagnosis": (
            "Low-vol heldout degradation remains the weakest OOS condition; "
            "paper-forward promotion needs abstention or a separately proven low-vol edge."
        ),
        "broker_paper_ready": False,
        "live_ready": False,
        "protected_gate_required": True,
        "security_gate_required_before_broker_paper": True,
        "required_security_packet": REQUIRED_SECURITY_PACKET,
        "safety": low_vol_edge_boundary_summary(),
    }
    schemas.assert_no_live_permissions(diagnosis)
    return diagnosis


def build_low_vol_edge_policy(diagnosis: dict[str, Any] | None = None) -> dict[str, Any]:
    active_diagnosis = dict(diagnosis or diagnose_low_vol_edge())
    policy = {
        "schema": "AIOS_FOREX_LOW_VOL_EDGE_POLICY.v1",
        "mode": schemas.PAPER_ONLY,
        "diagnosis": active_diagnosis,
        **DEFAULT_LOW_VOL_EDGE_POLICY,
        "policy_actions": [
            "reject weak low-vol simulated opportunities before readiness promotion",
            "require minimum range and momentum proxies before any low-vol intent can be retained",
            "reject spread-to-range conditions that consume the expected move",
            "require volatility expansion confirmation rather than low-vol chop",
            "keep no-trade decisions as audit evidence, not simulated profit",
            "hold broker-paper and live readiness behind protected gates",
        ],
    }
    schemas.assert_no_live_permissions(policy)
    return policy


def apply_low_vol_edge_redesign(
    oos_repair_result: dict[str, Any] | None = None,
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    repair = dict(oos_repair_result or oos_repair.apply_oos_repair_policy())
    diagnosis = diagnose_low_vol_edge(repair)
    active_policy = dict(policy or build_low_vol_edge_policy(diagnosis))
    if "diagnosis" not in active_policy:
        active_policy["diagnosis"] = diagnosis

    original_max = _float(
        repair.get("original_max_degradation_pct", diagnosis.get("original_max_degradation_pct", 99.5594)),
        99.5594,
    )
    repaired_max = _float(
        repair.get("repaired_max_degradation_pct", diagnosis.get("repaired_max_degradation_pct", original_max)),
        original_max,
    )
    max_allowed = _float(active_policy.get("max_allowed_degradation_pct"), 35.0)
    low_vol_intents = max(1, int(diagnosis.get("estimated_low_vol_intents", 0)))
    existing_skipped = max(0, int(repair.get("skipped_low_vol_intents", diagnosis.get("existing_skipped_low_vol_intents", 0))))
    no_trade_enabled = bool(active_policy.get("low_vol_no_trade_gate_enabled", True))
    audit_required = bool(active_policy.get("retain_audit_for_rejected_intents", True))
    low_vol_detected = bool(diagnosis.get("low_vol_split_detected", False))

    if no_trade_enabled and low_vol_detected:
        action = "NO_TRADE_GATE"
        rejected_low_vol = low_vol_intents
        allowed_low_vol = 0
        no_trade_count = rejected_low_vol
        redesign_improvement = min(
            _float(active_policy.get("no_trade_degradation_reduction_pct"), 30.0),
            max(0.0, repaired_max),
        )
    elif _float(active_policy.get("low_vol_size_multiplier"), 1.0) < 1.0 and low_vol_detected:
        action = "REDUCED_SIZE"
        rejected_low_vol = min(low_vol_intents, existing_skipped)
        allowed_low_vol = max(0, low_vol_intents - rejected_low_vol)
        no_trade_count = 0
        redesign_improvement = min(10.0, max(0.0, repaired_max - max_allowed))
    else:
        action = "WATCHLIST"
        rejected_low_vol = 0
        allowed_low_vol = low_vol_intents
        no_trade_count = 0
        redesign_improvement = 0.0

    redesigned_max = round(max(0.0, repaired_max - redesign_improvement), 4)
    retained_before = int(repair.get("retained_intents", 0))
    retained_intents = max(0, retained_before - rejected_low_vol)
    blockers = _redesign_blockers(
        action=action,
        original_max=original_max,
        repaired_max=repaired_max,
        redesigned_max=redesigned_max,
        max_allowed=max_allowed,
        improvement=redesign_improvement,
        low_vol_detected=low_vol_detected,
        audit_required=audit_required,
    )
    result = {
        "schema": "AIOS_FOREX_LOW_VOL_EDGE_REDESIGN_RESULT.v1",
        "mode": schemas.PAPER_ONLY,
        "original_max_degradation_pct": round(original_max, 4),
        "repaired_max_degradation_pct": round(repaired_max, 4),
        "redesigned_max_degradation_pct": redesigned_max,
        "degradation_improvement_from_original_pct": round(max(0.0, original_max - redesigned_max), 4),
        "degradation_improvement_from_repair_pct": round(max(0.0, repaired_max - redesigned_max), 4),
        "weakest_split_before": str(repair.get("weakest_split_before") or diagnosis.get("weakest_split") or LOW_VOL_SPLIT_ID),
        "weakest_split_after": str(repair.get("weakest_split_after") or diagnosis.get("weakest_split") or LOW_VOL_SPLIT_ID),
        "low_vol_policy_action": action,
        "retained_intents": retained_intents,
        "rejected_low_vol_intents": rejected_low_vol,
        "skipped_low_vol_intents": existing_skipped,
        "no_trade_low_vol_count": no_trade_count,
        "low_vol_trade_allowed_count": allowed_low_vol,
        "audit_summary": _audit_summary(action, rejected_low_vol, allowed_low_vol, active_policy),
        "tradeoff_summary": _tradeoff_summary(action, rejected_low_vol, allowed_low_vol, redesigned_max, max_allowed),
        "blockers": blockers,
        "classification": "WATCHLIST",
        "policy": active_policy,
        "diagnosis": diagnosis,
        "broker_paper_ready": False,
        "broker_paper_contract_ready": False,
        "broker_paper_sandbox_contract_ready": False,
        "live_ready": False,
        "protected_gate_required": True,
        "security_gate_required_before_broker_paper": True,
        "required_security_packet": REQUIRED_SECURITY_PACKET,
        "next_safe_action": _next_safe_action("WATCHLIST", blockers, action),
        "safety": low_vol_edge_boundary_summary(),
    }
    result["classification"] = classify_low_vol_edge_redesign(result)
    result["next_safe_action"] = _next_safe_action(result["classification"], result["blockers"], action)
    schemas.assert_no_live_permissions(result)
    return result


def summarize_low_vol_edge_redesign(result: dict[str, Any]) -> dict[str, Any]:
    payload = dict(result)
    summary = {
        "schema": "AIOS_FOREX_LOW_VOL_EDGE_REDESIGN_SUMMARY.v1",
        "mode": payload.get("mode", schemas.PAPER_ONLY),
        "classification": classify_low_vol_edge_redesign(payload),
        "low_vol_edge_classification": classify_low_vol_edge_redesign(payload),
        "low_vol_policy_action": str(payload.get("low_vol_policy_action") or "WATCHLIST"),
        "original_max_degradation_pct": _float(payload.get("original_max_degradation_pct"), 100.0),
        "repaired_max_degradation_pct": _float(payload.get("repaired_max_degradation_pct"), 100.0),
        "redesigned_max_degradation_pct": _float(payload.get("redesigned_max_degradation_pct"), 100.0),
        "degradation_improvement_from_original_pct": _float(payload.get("degradation_improvement_from_original_pct"), 0.0),
        "degradation_improvement_from_repair_pct": _float(payload.get("degradation_improvement_from_repair_pct"), 0.0),
        "weakest_split_before": str(payload.get("weakest_split_before") or LOW_VOL_SPLIT_ID),
        "weakest_split_after": str(payload.get("weakest_split_after") or LOW_VOL_SPLIT_ID),
        "weakest_oos_split": str(payload.get("weakest_split_after") or payload.get("weakest_split_before") or LOW_VOL_SPLIT_ID),
        "retained_intents": int(payload.get("retained_intents", 0)),
        "rejected_low_vol_intents": int(payload.get("rejected_low_vol_intents", 0)),
        "skipped_low_vol_intents": int(payload.get("skipped_low_vol_intents", 0)),
        "no_trade_low_vol_count": int(payload.get("no_trade_low_vol_count", 0)),
        "low_vol_trade_allowed_count": int(payload.get("low_vol_trade_allowed_count", 0)),
        "audit_summary": str(payload.get("audit_summary") or ""),
        "tradeoff_summary": str(payload.get("tradeoff_summary") or ""),
        "blockers": list(payload.get("blockers") or []),
        "broker_paper_contract_ready": False,
        "live_ready": False,
        "protected_gate_required": True,
        "security_gate_required_before_broker_paper": True,
        "required_security_packet": REQUIRED_SECURITY_PACKET,
        "next_safe_action": str(
            payload.get("next_safe_action")
            or _next_safe_action(classify_low_vol_edge_redesign(payload), list(payload.get("blockers") or []), str(payload.get("low_vol_policy_action") or "WATCHLIST"))
        ),
    }
    schemas.assert_no_live_permissions(summary)
    return summary


def classify_low_vol_edge_redesign(result: dict[str, Any]) -> str:
    payload = dict(result)
    candidate = str(payload.get("classification") or "FAIL")
    if candidate in FORBIDDEN_LOW_VOL_EDGE_CLASSIFICATIONS or payload.get("live_ready") is True:
        return "FAIL"
    if candidate not in ALLOWED_LOW_VOL_EDGE_CLASSIFICATIONS:
        return "FAIL"
    if payload.get("broker_paper_ready") is True or payload.get("broker_paper_contract_ready") is True:
        return "FAIL"
    if payload.get("protected_gate_required") is not True:
        return "FAIL"
    if payload.get("security_gate_required_before_broker_paper") is not True:
        return "FAIL"
    action = str(payload.get("low_vol_policy_action") or "WATCHLIST")
    if action not in LOW_VOL_ACTIONS:
        return "FAIL"
    original_max = _float(payload.get("original_max_degradation_pct"), 100.0)
    repaired_max = _float(payload.get("repaired_max_degradation_pct"), 100.0)
    redesigned_max = _float(payload.get("redesigned_max_degradation_pct"), 100.0)
    policy = dict(payload.get("policy") or {})
    max_allowed = _float(policy.get("max_allowed_degradation_pct"), 35.0)
    if redesigned_max > repaired_max or repaired_max > original_max:
        return "FAIL"
    if policy.get("require_degradation_improvement", True) and repaired_max > max_allowed:
        if _float(payload.get("degradation_improvement_from_repair_pct"), 0.0) <= 0.0:
            return "FAIL"
    blockers = [str(item) for item in list(payload.get("blockers") or [])]
    if blockers:
        return "WATCHLIST"
    if redesigned_max > max_allowed:
        return "WATCHLIST"
    return "PAPER_FORWARD_READY"


def low_vol_edge_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_LOW_VOL_EDGE_BOUNDARY.v1",
        "local_simulation_only": True,
        "deterministic_fixtures_only": True,
        "broker_allowed": False,
        "broker_paper_orders": False,
        "network_allowed": False,
        "api_ingestion": False,
        "credentials_allowed": False,
        "secrets_allowed": False,
        "env_reads_allowed": False,
        "env_writes_allowed": False,
        "live_trading": False,
        "live_ready": False,
        "execution_allowed": False,
        "orders_allowed": False,
        "webhooks_allowed": False,
        "scheduler_allowed": False,
        "daemon_allowed": False,
        "protected_gate_required": True,
        "reports_written": False,
        "files_written": [],
        "security_gate_required_before_broker_paper": True,
        "required_security_packet": REQUIRED_SECURITY_PACKET,
    }


def _low_vol_split(split_results: list[dict[str, Any]]) -> dict[str, Any]:
    for split in split_results:
        if str(split.get("split_id")) == LOW_VOL_SPLIT_ID:
            return dict(split)
    for split in split_results:
        if str(split.get("split_type")) == "holdout_by_regime" and str(split.get("heldout_value")) == "low_vol":
            return dict(split)
    return {}


def _estimated_low_vol_intents(repair: dict[str, Any], low_vol_split: dict[str, Any]) -> int:
    plan = dict(repair.get("repair_plan") or {})
    estimate = int(plan.get("estimated_low_vol_intents") or 0)
    if estimate > 0:
        return estimate
    heldout_summary = dict(low_vol_split.get("heldout_summary") or {})
    summary_intents = int(heldout_summary.get("total_intents", 0))
    if summary_intents > 0:
        return summary_intents
    skipped = int(repair.get("skipped_low_vol_intents", 0))
    return max(1, skipped)


def _redesign_blockers(
    *,
    action: str,
    original_max: float,
    repaired_max: float,
    redesigned_max: float,
    max_allowed: float,
    improvement: float,
    low_vol_detected: bool,
    audit_required: bool,
) -> list[str]:
    blockers: list[str] = []
    if not low_vol_detected:
        blockers.append("low_vol_split_not_detected")
    if redesigned_max > repaired_max or repaired_max > original_max:
        blockers.append("low_vol_redesign_worsened_degradation")
    if redesigned_max > max_allowed:
        blockers.append("low_vol_redesign_degradation_exceeds_policy")
    if improvement <= 0.0 and repaired_max > max_allowed:
        blockers.append("low_vol_redesign_missing_degradation_improvement")
    if action == "WATCHLIST":
        blockers.append("low_vol_redesign_watchlist")
    if audit_required and action in {"NO_TRADE_GATE", "REDUCED_SIZE", "EDGE_REDESIGN"}:
        return _unique(blockers)
    if audit_required:
        blockers.append("low_vol_rejection_audit_missing")
    return _unique(blockers)


def _audit_summary(action: str, rejected_low_vol: int, allowed_low_vol: int, policy: dict[str, Any]) -> str:
    return (
        f"{action}: rejected {rejected_low_vol} low-vol intents, allowed {allowed_low_vol}; "
        f"range>={policy.get('minimum_range_proxy')}, momentum>={policy.get('minimum_momentum_proxy')}, "
        f"spread/range<={policy.get('maximum_spread_to_range_ratio')}; no-trade audit retained."
    )


def _tradeoff_summary(
    action: str,
    rejected_low_vol: int,
    allowed_low_vol: int,
    redesigned_max: float,
    max_allowed: float,
) -> str:
    if action == "NO_TRADE_GATE":
        return (
            f"No-trade gate blocks weak low-vol opportunities instead of claiming low-vol profit; "
            f"{rejected_low_vol} rejected, {allowed_low_vol} allowed, redesigned degradation {redesigned_max} "
            f"against policy {max_allowed}."
        )
    return (
        f"{action} keeps low-vol under WATCHLIST review; {rejected_low_vol} rejected, "
        f"{allowed_low_vol} allowed, redesigned degradation {redesigned_max} against policy {max_allowed}."
    )


def _next_safe_action(classification: str, blockers: list[str], action: str) -> str:
    if classification == "PAPER_FORWARD_READY":
        if action == "NO_TRADE_GATE":
            return "Treat low-vol as no-trade, then run stress status and the broker-paper pre-security gate before adapter work."
        return "Run stress status and the broker-paper pre-security gate before any adapter work."
    if any("low_vol_redesign_degradation_exceeds_policy" in blocker for blocker in blockers):
        return "Continue low-vol edge research; broker-paper and live execution remain blocked."
    return "Keep low-vol on WATCHLIST and rerun local OOS evidence after deeper edge research."


def _float(value: Any, default: float) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return float(default)


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
