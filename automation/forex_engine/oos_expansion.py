from __future__ import annotations

from typing import Any

from automation.forex_engine import local_fixture_catalog
from automation.forex_engine import out_of_sample_validator
from automation.forex_engine import paper_forward_runner
from automation.forex_engine import schema_contracts as schemas


ALLOWED_EXPANDED_OOS_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
FORBIDDEN_EXPANDED_OOS_CLASSIFICATIONS = {"LIVE_READY", "BROKER_READY", "ORDER_READY"}
DEFAULT_STARTING_BALANCE = paper_forward_runner.DEFAULT_STARTING_BALANCE

DEFAULT_EXPANDED_OOS_POLICY = {
    "minimum_heldout_consistency_pct": 70.0,
    "maximum_degradation_pct": 35.0,
    "minimum_split_count": 6,
    "minimum_fixture_count": 9,
    "require_symbol_holdout": True,
    "require_timeframe_holdout": True,
    "require_regime_holdout": True,
}


def build_expanded_oos_plan(fixture_ids: list[str] | None = None) -> dict[str, Any]:
    active_fixture_ids = _active_fixture_ids(fixture_ids)
    groups = {
        "regime": _group_fixture_ids(active_fixture_ids, "regime"),
        "symbol": _group_fixture_ids(active_fixture_ids, "symbol"),
        "timeframe": _group_fixture_ids(active_fixture_ids, "timeframe"),
    }
    splits: list[dict[str, Any]] = []

    for value, heldout_ids in groups["regime"].items():
        splits.append(_split("holdout_by_regime", value, heldout_ids, active_fixture_ids))
    for value, heldout_ids in groups["symbol"].items():
        splits.append(_split("holdout_by_symbol", value, heldout_ids, active_fixture_ids))
    for value, heldout_ids in groups["timeframe"].items():
        splits.append(_split("holdout_by_timeframe", value, heldout_ids, active_fixture_ids))
    for value, heldout_ids in groups["regime"].items():
        splits.append(_split("leave_one_regime_out", value, heldout_ids, active_fixture_ids))
    for value, heldout_ids in groups["symbol"].items():
        splits.append(_split("leave_one_symbol_out", value, heldout_ids, active_fixture_ids))
    for value, heldout_ids in groups["timeframe"].items():
        splits.append(_split("leave_one_timeframe_out", value, heldout_ids, active_fixture_ids))

    weak_ids = _weak_regime_fixture_ids(active_fixture_ids)
    if weak_ids:
        splits.append(_split("weak_regime_holdout", "weak_regimes", weak_ids, active_fixture_ids))
    stress_ids = _stress_repaired_holdout_fixture_ids(active_fixture_ids)
    if stress_ids:
        splits.append(_split("stress_repaired_holdout", "stress_repair_focus", stress_ids, active_fixture_ids))
    splits.extend(_rotating_train_test_windows(active_fixture_ids))

    split_types = _unique([str(item["split_type"]) for item in splits])
    plan = {
        "schema": "AIOS_FOREX_EXPANDED_OOS_PLAN.v1",
        "mode": schemas.PAPER_ONLY,
        "fixture_ids": active_fixture_ids,
        "fixture_count": len(active_fixture_ids),
        "split_count": len(splits),
        "split_types": split_types,
        "required_split_types": [
            "holdout_by_regime",
            "holdout_by_symbol",
            "holdout_by_timeframe",
            "leave_one_regime_out",
            "leave_one_symbol_out",
            "leave_one_timeframe_out",
            "weak_regime_holdout",
            "stress_repaired_holdout",
            "rotating_train_test_windows",
        ],
        "splits": splits,
        "policy": dict(DEFAULT_EXPANDED_OOS_POLICY),
        "local_only": True,
        "network_allowed": False,
        "broker_allowed": False,
        "live_ready": False,
        "protected_gate_required": True,
        "safety": oos_expansion_boundary_summary(),
    }
    schemas.assert_no_live_permissions(plan)
    return plan


def run_expanded_oos_validation(fixture_ids: list[str] | None = None) -> dict[str, Any]:
    plan = build_expanded_oos_plan(fixture_ids)
    policy = dict(plan["policy"])
    split_results = [_evaluate_split(split, policy) for split in list(plan["splits"])]
    base_oos = out_of_sample_validator.run_out_of_sample_validation(list(plan["fixture_ids"]))
    blockers = _expanded_oos_blockers(plan, split_results, policy)
    weakest_split, strongest_split = _ranked_splits(split_results)
    result = {
        "schema": "AIOS_FOREX_EXPANDED_OOS_VALIDATION.v1",
        "mode": schemas.PAPER_ONLY,
        "fixture_count": int(plan["fixture_count"]),
        "split_count": int(plan["split_count"]),
        "split_types": list(plan["split_types"]),
        "policy": policy,
        "plan": plan,
        "base_oos_validation": base_oos,
        "split_results": split_results,
        "heldout_consistency_pct": _average_consistency(split_results),
        "max_degradation_pct": _max_degradation(split_results),
        "degradation_pct": _max_degradation(split_results),
        "weakest_split": weakest_split,
        "strongest_split": strongest_split,
        "blockers": blockers,
        "broker_paper_contract_ready": False,
        "live_ready": False,
        "protected_gate_required": True,
        "safety": oos_expansion_boundary_summary(),
    }
    result["classification"] = classify_expanded_oos(result)
    result["next_safe_action"] = _next_safe_action(result["classification"], result["blockers"])
    result["expanded_oos_summary"] = summarize_expanded_oos(result)
    schemas.assert_no_live_permissions(result)
    return result


def summarize_expanded_oos(result: dict[str, Any]) -> dict[str, Any]:
    payload = dict(result)
    weakest = payload.get("weakest_split") or {}
    summary = {
        "schema": "AIOS_FOREX_EXPANDED_OOS_SUMMARY.v1",
        "mode": payload.get("mode", schemas.PAPER_ONLY),
        "fixture_count": int(payload.get("fixture_count", 0)),
        "split_count": int(payload.get("split_count", 0)),
        "heldout_consistency_pct": float(payload.get("heldout_consistency_pct", 0.0)),
        "max_degradation_pct": float(payload.get("max_degradation_pct", payload.get("degradation_pct", 100.0))),
        "degradation_pct": float(payload.get("degradation_pct", payload.get("max_degradation_pct", 100.0))),
        "weakest_split": weakest,
        "weakest_split_id": str(dict(weakest).get("split_id") or "none"),
        "classification": classify_expanded_oos(payload),
        "blockers": list(payload.get("blockers") or []),
        "broker_paper_contract_ready": bool(payload.get("broker_paper_contract_ready", False)),
        "live_ready": False,
        "protected_gate_required": True,
        "next_safe_action": payload.get("next_safe_action")
        or _next_safe_action(classify_expanded_oos(payload), list(payload.get("blockers") or [])),
    }
    schemas.assert_no_live_permissions(summary)
    return summary


def classify_expanded_oos(result: dict[str, Any]) -> str:
    payload = dict(result)
    candidate = str(payload.get("classification") or "")
    if candidate in FORBIDDEN_EXPANDED_OOS_CLASSIFICATIONS or payload.get("live_ready") is True:
        return "FAIL"
    if int(payload.get("fixture_count", 0)) < int(DEFAULT_EXPANDED_OOS_POLICY["minimum_fixture_count"]):
        return "FAIL"
    if int(payload.get("split_count", 0)) < int(DEFAULT_EXPANDED_OOS_POLICY["minimum_split_count"]):
        return "FAIL"
    split_results = [dict(item) for item in list(payload.get("split_results") or [])]
    if not split_results:
        return "FAIL"
    if any(str(item.get("classification")) in FORBIDDEN_EXPANDED_OOS_CLASSIFICATIONS for item in split_results):
        return "FAIL"
    if any(str(item.get("classification")) == "FAIL" for item in split_results):
        return "WATCHLIST"
    blockers = list(payload.get("blockers") or [])
    if blockers or any(str(item.get("classification")) == "WATCHLIST" for item in split_results):
        return "WATCHLIST"
    if float(payload.get("heldout_consistency_pct", 0.0)) < DEFAULT_EXPANDED_OOS_POLICY["minimum_heldout_consistency_pct"]:
        return "WATCHLIST"
    if float(payload.get("max_degradation_pct", payload.get("degradation_pct", 100.0))) > DEFAULT_EXPANDED_OOS_POLICY["maximum_degradation_pct"]:
        return "WATCHLIST"
    return "PAPER_FORWARD_READY"


def oos_expansion_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_EXPANDED_OOS_BOUNDARY.v1",
        "local_simulation_only": True,
        "deterministic_fixtures_only": True,
        "broker_allowed": False,
        "broker_paper_orders": False,
        "network_allowed": False,
        "csv_ingestion": False,
        "api_ingestion": False,
        "credentials_allowed": False,
        "secrets_allowed": False,
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
    }


def _active_fixture_ids(fixture_ids: list[str] | None) -> list[str]:
    available = local_fixture_catalog.list_fixture_ids()
    requested = list(fixture_ids or available)
    return [fixture_id for fixture_id in requested if fixture_id in available]


def _group_fixture_ids(fixture_ids: list[str], field_name: str) -> dict[str, list[str]]:
    groups: dict[str, list[str]] = {}
    for fixture_id in fixture_ids:
        fixture = local_fixture_catalog.get_fixture_by_id(fixture_id)
        if field_name == "regime":
            value = local_fixture_catalog.fixture_regime(fixture_id)
        elif field_name == "symbol":
            value = str(fixture.symbol)
        elif field_name == "timeframe":
            value = str(fixture.timeframe)
        else:
            value = "unknown"
        groups.setdefault(value, []).append(fixture_id)
    return dict(sorted(groups.items()))


def _split(split_type: str, heldout_value: str, heldout_ids: list[str], fixture_ids: list[str]) -> dict[str, Any]:
    active_heldout = [fixture_id for fixture_id in fixture_ids if fixture_id in set(heldout_ids)]
    train_ids = [fixture_id for fixture_id in fixture_ids if fixture_id not in active_heldout]
    return {
        "split_id": f"{split_type}:{heldout_value}",
        "split_type": split_type,
        "heldout_value": heldout_value,
        "train_fixture_ids": train_ids,
        "heldout_fixture_ids": active_heldout,
        "train_fixture_count": len(train_ids),
        "heldout_fixture_count": len(active_heldout),
        "live_ready": False,
        "protected_gate_required": True,
    }


def _rotating_train_test_windows(fixture_ids: list[str]) -> list[dict[str, Any]]:
    if not fixture_ids:
        return []
    windows: list[dict[str, Any]] = []
    window_count = min(3, max(1, len(fixture_ids)))
    for index in range(window_count):
        heldout = [
            fixture_id
            for fixture_index, fixture_id in enumerate(fixture_ids)
            if fixture_index % window_count == index
        ]
        if heldout:
            windows.append(_split("rotating_train_test_windows", f"window_{index + 1}", heldout, fixture_ids))
    return windows


def _weak_regime_fixture_ids(fixture_ids: list[str]) -> list[str]:
    weak_regimes = {"chop", "low_vol", "range", "volatile"}
    return [
        fixture_id
        for fixture_id in fixture_ids
        if local_fixture_catalog.fixture_regime(fixture_id) in weak_regimes
    ]


def _stress_repaired_holdout_fixture_ids(fixture_ids: list[str]) -> list[str]:
    focus_regimes = {"low_vol", "volatile", "range"}
    focused = [
        fixture_id
        for fixture_id in fixture_ids
        if local_fixture_catalog.fixture_regime(fixture_id) in focus_regimes
    ]
    return focused or _weak_regime_fixture_ids(fixture_ids)


def _evaluate_split(split: dict[str, Any], policy: dict[str, Any]) -> dict[str, Any]:
    train_ids = list(split.get("train_fixture_ids") or [])
    heldout_ids = list(split.get("heldout_fixture_ids") or [])
    train_summary = _multi_summary(train_ids)
    heldout_summary = _multi_summary(heldout_ids)
    heldout_pnl = float(heldout_summary.get("aggregate_pnl", 0.0))
    degradation_pct = _degradation_pct(train_summary, heldout_summary)
    blockers = _split_blockers(split, heldout_summary, degradation_pct, policy)
    result = {
        "split_id": str(split["split_id"]),
        "split_type": str(split["split_type"]),
        "train_fixture_count": len(train_ids),
        "heldout_fixture_count": len(heldout_ids),
        "heldout_pnl": round(heldout_pnl, 4),
        "heldout_return_pct": _return_pct(heldout_pnl),
        "heldout_consistency_pct": float(heldout_summary.get("consistency_pct", 0.0)),
        "degradation_pct": degradation_pct,
        "train_summary": train_summary,
        "heldout_summary": heldout_summary,
        "blockers": blockers,
        "live_ready": False,
        "protected_gate_required": True,
    }
    result["classification"] = _classify_split(result)
    schemas.assert_no_live_permissions(result)
    return result


def _multi_summary(fixture_ids: list[str]) -> dict[str, Any]:
    if not fixture_ids:
        return {
            "schema": "AIOS_FOREX_MULTI_FIXTURE_PAPER_FORWARD_SUMMARY.v1",
            "mode": schemas.PAPER_ONLY,
            "fixture_count": 0,
            "per_fixture_results": [],
            "total_intents": 0,
            "total_ledger_entries": 0,
            "aggregate_pnl": 0.0,
            "positive_fixture_count": 0,
            "negative_fixture_count": 0,
            "blocked_fixture_count": 0,
            "consistency_pct": 0.0,
            "classification": "FAIL",
            "blockers": ["missing_fixture_ids"],
            "live_ready": False,
            "protected_gate_required": True,
        }
    return paper_forward_runner.summarize_multi_fixture_paper_forward(
        paper_forward_runner.run_multi_fixture_paper_forward(fixture_ids)
    )


def _split_blockers(
    split: dict[str, Any],
    heldout_summary: dict[str, Any],
    degradation_pct: float,
    policy: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    split_type = str(split.get("split_type") or "")
    heldout_count = int(split.get("heldout_fixture_count", 0))
    if int(split.get("train_fixture_count", 0)) <= 0:
        blockers.append("expanded_oos_missing_train_fixtures")
    if heldout_count <= 0:
        blockers.append("expanded_oos_missing_heldout_fixtures")
    if float(heldout_summary.get("aggregate_pnl", 0.0)) <= 0.0:
        blockers.append("expanded_oos_non_positive_heldout_pnl")
    if float(heldout_summary.get("consistency_pct", 0.0)) < float(policy["minimum_heldout_consistency_pct"]):
        blockers.append("expanded_oos_heldout_consistency_below_policy")
    if degradation_pct > float(policy["maximum_degradation_pct"]):
        blockers.append("expanded_oos_degradation_exceeds_policy")
    if split_type == "weak_regime_holdout" and heldout_count < 3:
        blockers.append("expanded_oos_weak_regime_holdout_too_small")
    return _unique(blockers)


def _classify_split(result: dict[str, Any]) -> str:
    blockers = list(result.get("blockers") or [])
    if any("non_positive" in str(item) or "missing" in str(item) for item in blockers):
        return "FAIL"
    if blockers:
        return "WATCHLIST"
    return "PAPER_FORWARD_READY"


def _expanded_oos_blockers(
    plan: dict[str, Any],
    split_results: list[dict[str, Any]],
    policy: dict[str, Any],
) -> list[str]:
    blockers: list[str] = []
    split_types = set(str(item) for item in list(plan.get("split_types") or []))
    if int(plan.get("fixture_count", 0)) < int(policy["minimum_fixture_count"]):
        blockers.append("expanded_oos_fixture_count_below_policy")
    if int(plan.get("split_count", 0)) < int(policy["minimum_split_count"]):
        blockers.append("expanded_oos_split_count_below_policy")
    if policy.get("require_symbol_holdout") and "holdout_by_symbol" not in split_types:
        blockers.append("expanded_oos_missing_symbol_holdout")
    if policy.get("require_timeframe_holdout") and "holdout_by_timeframe" not in split_types:
        blockers.append("expanded_oos_missing_timeframe_holdout")
    if policy.get("require_regime_holdout") and "holdout_by_regime" not in split_types:
        blockers.append("expanded_oos_missing_regime_holdout")
    for item in split_results:
        if item.get("classification") == "FAIL":
            blockers.append(f"{item.get('split_id')}:failed")
        elif item.get("classification") == "WATCHLIST":
            blockers.append(f"{item.get('split_id')}:watchlist")
        blockers.extend([f"{item.get('split_id')}:{blocker}" for blocker in list(item.get("blockers") or [])])
    return _unique(blockers)


def _ranked_splits(split_results: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any]]:
    if not split_results:
        empty = {"split_id": "none", "heldout_pnl": 0.0, "classification": "FAIL"}
        return empty, empty
    ranked = sorted(
        (
            {
                "split_id": str(item.get("split_id")),
                "split_type": str(item.get("split_type")),
                "heldout_pnl": float(item.get("heldout_pnl", 0.0)),
                "heldout_consistency_pct": float(item.get("heldout_consistency_pct", 0.0)),
                "degradation_pct": float(item.get("degradation_pct", 0.0)),
                "classification": str(item.get("classification")),
            }
            for item in split_results
        ),
        key=lambda item: (
            _classification_rank(item["classification"]),
            item["heldout_pnl"],
            -item["degradation_pct"],
        ),
    )
    return ranked[0], ranked[-1]


def _classification_rank(classification: str) -> int:
    return {"FAIL": 0, "WATCHLIST": 1, "PAPER_FORWARD_READY": 2}.get(classification, 0)


def _average_consistency(split_results: list[dict[str, Any]]) -> float:
    if not split_results:
        return 0.0
    return round(
        sum(float(item.get("heldout_consistency_pct", 0.0)) for item in split_results) / len(split_results),
        4,
    )


def _max_degradation(split_results: list[dict[str, Any]]) -> float:
    if not split_results:
        return 100.0
    return round(max(float(item.get("degradation_pct", 0.0)) for item in split_results), 4)


def _degradation_pct(train_summary: dict[str, Any], heldout_summary: dict[str, Any]) -> float:
    train_count = max(1, int(train_summary.get("fixture_count", 0)))
    heldout_count = max(1, int(heldout_summary.get("fixture_count", 0)))
    train_avg = float(train_summary.get("aggregate_pnl", 0.0)) / train_count
    heldout_avg = float(heldout_summary.get("aggregate_pnl", 0.0)) / heldout_count
    if train_avg <= 0.0:
        return 100.0
    return round(max(0.0, ((train_avg - heldout_avg) / abs(train_avg)) * 100.0), 4)


def _return_pct(pnl: float) -> float:
    return round((float(pnl) / DEFAULT_STARTING_BALANCE) * 100.0, 4) if DEFAULT_STARTING_BALANCE else 0.0


def _next_safe_action(classification: str, blockers: list[str]) -> str:
    if classification == "PAPER_FORWARD_READY":
        return "Use expanded OOS evidence with stress repair before any protected broker-paper sandbox contract."
    if blockers:
        return "Repair expanded OOS holdout or degradation blockers before broker-paper sandbox readiness."
    return "Add stronger deterministic heldout fixtures and rerun expanded OOS validation."


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
