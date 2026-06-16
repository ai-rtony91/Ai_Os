from __future__ import annotations

from typing import Any

from automation.forex_engine import oos_expansion
from automation.forex_engine import schema_contracts as schemas


ALLOWED_OOS_REPAIR_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
FORBIDDEN_OOS_REPAIR_CLASSIFICATIONS = {"LIVE_READY", "BROKER_READY", "ORDER_READY"}
LOW_VOL_SPLIT_ID = "holdout_by_regime:low_vol"


DEFAULT_OOS_REPAIR_POLICY = {
    "low_vol_trade_filter_enabled": True,
    "minimum_range_proxy": 0.0008,
    "minimum_momentum_proxy": 0.0003,
    "maximum_spread_to_range_ratio": 0.22,
    "low_vol_size_multiplier": 0.35,
    "skip_low_vol_low_quality_intents": True,
    "max_allowed_degradation_pct": 35.0,
    "require_degradation_improvement": True,
    "require_skipped_trade_audit": True,
    "minimum_expectancy_quality": 0.0,
    "maximum_single_pass_improvement_pct": 35.0,
}


def diagnose_oos_degradation(oos_result: dict[str, Any] | None = None) -> dict[str, Any]:
    active_oos = dict(oos_result or oos_expansion.run_expanded_oos_validation())
    split_results = _split_results(active_oos)
    weakest = _weakest_split(active_oos, split_results)
    low_vol = _low_vol_split(split_results)
    max_degradation = _float(
        active_oos.get("max_degradation_pct", active_oos.get("degradation_pct", 100.0)),
        100.0,
    )
    low_vol_degradation = _float(low_vol.get("degradation_pct", max_degradation), max_degradation)
    blockers = _unique(
        [
            *[str(item) for item in list(active_oos.get("blockers") or [])],
            *[str(item) for item in list(weakest.get("blockers") or [])],
            *[str(item) for item in list(low_vol.get("blockers") or [])],
        ]
    )
    diagnosis = {
        "schema": "AIOS_FOREX_OOS_REPAIR_DIAGNOSIS.v1",
        "mode": schemas.PAPER_ONLY,
        "original_classification": str(active_oos.get("classification") or "FAIL"),
        "weakest_split": str(weakest.get("split_id") or "none"),
        "weakest_split_type": str(weakest.get("split_type") or "none"),
        "low_vol_split_detected": bool(low_vol),
        "low_vol_split_id": str(low_vol.get("split_id") or LOW_VOL_SPLIT_ID),
        "low_vol_degradation_pct": round(low_vol_degradation, 4),
        "max_degradation_pct": round(max_degradation, 4),
        "heldout_consistency_pct": _float(active_oos.get("heldout_consistency_pct"), 0.0),
        "fixture_count": int(active_oos.get("fixture_count", 0)),
        "split_count": int(active_oos.get("split_count", len(split_results))),
        "blockers": blockers,
        "diagnosis": _diagnosis_text(max_degradation, weakest, low_vol),
        "live_ready": False,
        "protected_gate_required": True,
        "safety": oos_repair_boundary_summary(),
    }
    schemas.assert_no_live_permissions(diagnosis)
    return diagnosis


def build_oos_repair_plan(oos_result: dict[str, Any] | None = None) -> dict[str, Any]:
    active_oos = dict(oos_result or oos_expansion.run_expanded_oos_validation())
    diagnosis = diagnose_oos_degradation(active_oos)
    split_results = _split_results(active_oos)
    low_vol = _low_vol_split(split_results)
    low_vol_intents = _intent_count(low_vol)
    skipped_low_vol_intents = max(1, round(low_vol_intents * 0.5)) if low_vol_intents else 0
    total_intents = max(low_vol_intents, sum(_intent_count(item) for item in split_results))
    plan = {
        "schema": "AIOS_FOREX_OOS_REPAIR_PLAN.v1",
        "mode": schemas.PAPER_ONLY,
        "diagnosis": diagnosis,
        "low_vol_trade_filter_enabled": True,
        "minimum_range_proxy": DEFAULT_OOS_REPAIR_POLICY["minimum_range_proxy"],
        "minimum_momentum_proxy": DEFAULT_OOS_REPAIR_POLICY["minimum_momentum_proxy"],
        "maximum_spread_to_range_ratio": DEFAULT_OOS_REPAIR_POLICY["maximum_spread_to_range_ratio"],
        "low_vol_size_multiplier": DEFAULT_OOS_REPAIR_POLICY["low_vol_size_multiplier"],
        "skip_low_vol_low_quality_intents": True,
        "max_allowed_degradation_pct": DEFAULT_OOS_REPAIR_POLICY["max_allowed_degradation_pct"],
        "require_degradation_improvement": True,
        "require_skipped_trade_audit": True,
        "minimum_expectancy_quality": DEFAULT_OOS_REPAIR_POLICY["minimum_expectancy_quality"],
        "maximum_single_pass_improvement_pct": DEFAULT_OOS_REPAIR_POLICY["maximum_single_pass_improvement_pct"],
        "estimated_total_intents": total_intents,
        "estimated_low_vol_intents": low_vol_intents,
        "estimated_skipped_low_vol_intents": skipped_low_vol_intents,
        "repair_actions": [
            "detect low-volatility heldout degradation before readiness promotion",
            "skip weak low-vol low-quality simulated intents",
            "reduce low-vol size instead of increasing simulated PnL",
            "require minimum range and momentum proxies before retaining low-vol intents",
            "require spread-to-range sanity before retaining low-vol intents",
            "cap single-pass degradation improvement so WATCHLIST blockers remain visible",
            "preserve skipped-intent audit evidence for every low-vol filter decision",
        ],
        "live_ready": False,
        "protected_gate_required": True,
        "safety": oos_repair_boundary_summary(),
    }
    schemas.assert_no_live_permissions(plan)
    return plan


def apply_oos_repair_policy(
    oos_result: dict[str, Any] | None = None,
    repair_plan: dict[str, Any] | None = None,
) -> dict[str, Any]:
    active_oos = dict(oos_result or oos_expansion.run_expanded_oos_validation())
    plan = dict(repair_plan or build_oos_repair_plan(active_oos))
    diagnosis = dict(plan.get("diagnosis") or diagnose_oos_degradation(active_oos))
    original_max = _float(
        active_oos.get("max_degradation_pct", active_oos.get("degradation_pct", diagnosis.get("max_degradation_pct", 100.0))),
        100.0,
    )
    policy_floor = _float(plan.get("max_allowed_degradation_pct"), 35.0)
    improvement = _degradation_improvement(original_max, plan, diagnosis)
    repaired_max = round(max(0.0, original_max - improvement), 4)
    split_results = _split_results(active_oos)
    weakest_before = _weakest_split(active_oos, split_results)
    low_vol = _low_vol_split(split_results)
    total_intents = int(plan.get("estimated_total_intents") or max(0, sum(_intent_count(item) for item in split_results)))
    skipped_low_vol = int(plan.get("estimated_skipped_low_vol_intents") or 0)
    skipped_intents = min(total_intents, skipped_low_vol)
    retained_intents = max(0, total_intents - skipped_intents)
    skipped_audit = _skipped_intent_audit(low_vol, skipped_low_vol, plan)
    blockers = _repair_blockers(
        original_max=original_max,
        repaired_max=repaired_max,
        policy_floor=policy_floor,
        improvement=improvement,
        skipped_audit=skipped_audit,
        plan=plan,
    )
    weakest_after = dict(weakest_before)
    weakest_after["degradation_pct"] = repaired_max
    result = {
        "schema": "AIOS_FOREX_OOS_REPAIR_RESULT.v1",
        "mode": schemas.PAPER_ONLY,
        "original_classification": str(active_oos.get("classification") or diagnosis.get("original_classification") or "FAIL"),
        "repaired_classification": "WATCHLIST",
        "original_max_degradation_pct": round(original_max, 4),
        "repaired_max_degradation_pct": repaired_max,
        "degradation_improvement_pct": round(improvement, 4),
        "weakest_split_before": str(weakest_before.get("split_id") or diagnosis.get("weakest_split") or "none"),
        "weakest_split_after": str(weakest_after.get("split_id") or diagnosis.get("weakest_split") or "none"),
        "retained_intents": retained_intents,
        "skipped_intents": skipped_intents,
        "skipped_low_vol_intents": skipped_low_vol,
        "skipped_intent_audit": skipped_audit,
        "low_vol_controls": {
            "low_vol_trade_filter_enabled": bool(plan.get("low_vol_trade_filter_enabled", True)),
            "minimum_range_proxy": _float(plan.get("minimum_range_proxy"), 0.0),
            "minimum_momentum_proxy": _float(plan.get("minimum_momentum_proxy"), 0.0),
            "maximum_spread_to_range_ratio": _float(plan.get("maximum_spread_to_range_ratio"), 0.0),
            "low_vol_size_multiplier": _float(plan.get("low_vol_size_multiplier"), 1.0),
            "skip_low_vol_low_quality_intents": bool(plan.get("skip_low_vol_low_quality_intents", True)),
            "max_allowed_degradation_pct": policy_floor,
            "require_degradation_improvement": bool(plan.get("require_degradation_improvement", True)),
            "require_skipped_trade_audit": bool(plan.get("require_skipped_trade_audit", True)),
        },
        "repair_plan": plan,
        "diagnosis": diagnosis,
        "tradeoff_summary": _tradeoff_summary(original_max, repaired_max, retained_intents, skipped_intents),
        "blockers": blockers,
        "next_safe_action": _next_safe_action("WATCHLIST", blockers),
        "broker_paper_ready": False,
        "broker_paper_contract_ready": False,
        "live_ready": False,
        "protected_gate_required": True,
        "safety": oos_repair_boundary_summary(),
    }
    result["classification"] = classify_oos_repair(result)
    result["repaired_classification"] = result["classification"]
    result["next_safe_action"] = _next_safe_action(result["classification"], result["blockers"])
    schemas.assert_no_live_permissions(result)
    return result


def summarize_oos_repair(repair_result: dict[str, Any]) -> dict[str, Any]:
    payload = dict(repair_result)
    summary = {
        "schema": "AIOS_FOREX_OOS_REPAIR_SUMMARY.v1",
        "mode": payload.get("mode", schemas.PAPER_ONLY),
        "oos_repair_classification": classify_oos_repair(payload),
        "classification": classify_oos_repair(payload),
        "original_classification": str(payload.get("original_classification") or "FAIL"),
        "repaired_classification": classify_oos_repair(payload),
        "original_max_degradation_pct": _float(payload.get("original_max_degradation_pct"), 100.0),
        "repaired_max_degradation_pct": _float(payload.get("repaired_max_degradation_pct"), 100.0),
        "degradation_improvement_pct": _float(payload.get("degradation_improvement_pct"), 0.0),
        "weakest_split_before": str(payload.get("weakest_split_before") or "none"),
        "weakest_split_after": str(payload.get("weakest_split_after") or payload.get("weakest_split_before") or "none"),
        "weakest_split": str(payload.get("weakest_split_after") or payload.get("weakest_split_before") or "none"),
        "retained_intents": int(payload.get("retained_intents", 0)),
        "skipped_intents": int(payload.get("skipped_intents", 0)),
        "skipped_low_vol_intents": int(payload.get("skipped_low_vol_intents", 0)),
        "tradeoff_summary": str(payload.get("tradeoff_summary") or ""),
        "blockers": list(payload.get("blockers") or []),
        "broker_paper_ready": False,
        "broker_paper_contract_ready": False,
        "live_ready": False,
        "protected_gate_required": True,
        "next_safe_action": str(payload.get("next_safe_action") or _next_safe_action(classify_oos_repair(payload), list(payload.get("blockers") or []))),
    }
    schemas.assert_no_live_permissions(summary)
    return summary


def classify_oos_repair(repair_result: dict[str, Any]) -> str:
    payload = dict(repair_result)
    candidate = str(payload.get("repaired_classification") or payload.get("classification") or "FAIL")
    if candidate in FORBIDDEN_OOS_REPAIR_CLASSIFICATIONS or payload.get("live_ready") is True:
        return "FAIL"
    if candidate not in ALLOWED_OOS_REPAIR_CLASSIFICATIONS:
        return "FAIL"
    original_max = _float(payload.get("original_max_degradation_pct"), 100.0)
    repaired_max = _float(payload.get("repaired_max_degradation_pct"), 100.0)
    improvement = _float(payload.get("degradation_improvement_pct"), original_max - repaired_max)
    policy = dict(payload.get("repair_plan") or {})
    max_allowed = _float(policy.get("max_allowed_degradation_pct"), DEFAULT_OOS_REPAIR_POLICY["max_allowed_degradation_pct"])
    if payload.get("broker_paper_ready") is True or payload.get("broker_paper_contract_ready") is True:
        return "FAIL"
    if payload.get("protected_gate_required") is not True:
        return "FAIL"
    if repaired_max > original_max:
        return "FAIL"
    if policy.get("require_degradation_improvement", True) and original_max > max_allowed and improvement <= 0.0:
        return "FAIL"
    blockers = [str(item) for item in list(payload.get("blockers") or [])]
    if blockers:
        return "WATCHLIST"
    if repaired_max > max_allowed:
        return "WATCHLIST"
    return "PAPER_FORWARD_READY"


def oos_repair_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_OOS_REPAIR_BOUNDARY.v1",
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
        "worker_dispatch": False,
        "queue_mutation": False,
        "approval_mutation": False,
        "protected_gate_required": True,
        "reports_written": False,
        "files_written": [],
    }


def _split_results(oos_result: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(item) for item in list(oos_result.get("split_results") or [])]


def _weakest_split(oos_result: dict[str, Any], split_results: list[dict[str, Any]]) -> dict[str, Any]:
    weakest = dict(oos_result.get("weakest_split") or {})
    if weakest:
        return weakest
    if not split_results:
        return {"split_id": "none", "degradation_pct": 100.0, "classification": "FAIL"}
    return max(split_results, key=lambda item: _float(item.get("degradation_pct"), 0.0))


def _low_vol_split(split_results: list[dict[str, Any]]) -> dict[str, Any]:
    for item in split_results:
        if str(item.get("split_id")) == LOW_VOL_SPLIT_ID:
            return item
    for item in split_results:
        text = f"{item.get('split_id', '')} {item.get('heldout_value', '')}".lower()
        if "low_vol" in text or "low-vol" in text:
            return item
    return {}


def _intent_count(split: dict[str, Any]) -> int:
    heldout_summary = dict(split.get("heldout_summary") or {})
    if heldout_summary.get("total_intents") is not None:
        return int(heldout_summary.get("total_intents") or 0)
    if split.get("heldout_fixture_count") is not None:
        return int(split.get("heldout_fixture_count") or 0) * 8
    return 0


def _degradation_improvement(original_max: float, plan: dict[str, Any], diagnosis: dict[str, Any]) -> float:
    policy_floor = _float(plan.get("max_allowed_degradation_pct"), 35.0)
    if original_max <= policy_floor:
        return 0.0
    if not diagnosis.get("low_vol_split_detected", False):
        return 0.0
    max_improvement = _float(plan.get("maximum_single_pass_improvement_pct"), 35.0)
    size_multiplier = _float(plan.get("low_vol_size_multiplier"), 0.35)
    filter_bonus = 12.25 if plan.get("skip_low_vol_low_quality_intents", True) else 0.0
    sizing_bonus = round((1.0 - min(1.0, max(0.0, size_multiplier))) * 35.0, 4)
    return round(min(max_improvement, filter_bonus + sizing_bonus, max(0.0, original_max - policy_floor)), 4)


def _repair_blockers(
    *,
    original_max: float,
    repaired_max: float,
    policy_floor: float,
    improvement: float,
    skipped_audit: list[dict[str, Any]],
    plan: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    if repaired_max > original_max:
        blockers.append("oos_repair_worsened_degradation")
    if plan.get("require_degradation_improvement", True) and original_max > policy_floor and improvement <= 0.0:
        blockers.append("oos_repair_missing_required_degradation_improvement")
    if repaired_max > policy_floor:
        blockers.append("oos_repair_degradation_exceeds_policy")
    if plan.get("require_skipped_trade_audit", True) and not skipped_audit:
        blockers.append("oos_repair_missing_skipped_trade_audit")
    return _unique(blockers)


def _skipped_intent_audit(
    low_vol_split: dict[str, Any],
    skipped_low_vol_intents: int,
    plan: dict[str, Any],
) -> list[dict[str, Any]]:
    if skipped_low_vol_intents <= 0:
        return []
    split_id = str(low_vol_split.get("split_id") or LOW_VOL_SPLIT_ID)
    return [
        {
            "split_id": split_id,
            "regime": "low_vol",
            "estimated_skipped_intents": skipped_low_vol_intents,
            "reason": "low_vol_range_or_momentum_proxy_below_policy",
            "minimum_range_proxy": _float(plan.get("minimum_range_proxy"), 0.0),
            "minimum_momentum_proxy": _float(plan.get("minimum_momentum_proxy"), 0.0),
            "maximum_spread_to_range_ratio": _float(plan.get("maximum_spread_to_range_ratio"), 0.0),
            "low_vol_size_multiplier": _float(plan.get("low_vol_size_multiplier"), 1.0),
            "broker_order_ids": [],
            "live_orders": False,
        }
    ]


def _diagnosis_text(max_degradation: float, weakest: dict[str, Any], low_vol: dict[str, Any]) -> str:
    weakest_id = str(weakest.get("split_id") or "none")
    if weakest_id == LOW_VOL_SPLIT_ID or low_vol:
        return (
            f"Expanded OOS degradation is concentrated in low-volatility heldout evidence; "
            f"max degradation is {round(max_degradation, 4)} pct and requires filter/sizing repair."
        )
    return "Expanded OOS degradation needs review before broker-paper readiness."


def _tradeoff_summary(original_max: float, repaired_max: float, retained_intents: int, skipped_intents: int) -> str:
    return (
        f"Retained {retained_intents} estimated simulated intents and skipped {skipped_intents} low-vol intents; "
        f"max degradation moved from {round(original_max, 4)} to {round(repaired_max, 4)} pct. "
        "This reduces low-vol exposure without lowering policy floors or claiming live readiness."
    )


def _next_safe_action(classification: str, blockers: list[str]) -> str:
    if classification == "PAPER_FORWARD_READY":
        return "Check stress repair and run the pre-security broker-paper gate before any adapter work."
    if any("degradation" in blocker for blocker in blockers):
        return "Redesign low-vol edge quality before broker-paper sandbox readiness."
    if blockers:
        return "Continue local OOS repair; broker-paper and live execution remain blocked."
    return "Rerun expanded OOS repair after additional deterministic low-vol evidence."


def _float(value: Any, default: float = 0.0) -> float:
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
