from __future__ import annotations

from typing import Any

from automation.forex_engine import local_fixture_catalog
from automation.forex_engine import paper_forward_runner
from automation.forex_engine import schema_contracts as schemas


ALLOWED_OOS_CLASSIFICATIONS = {"FAIL", "WATCHLIST", "PAPER_FORWARD_READY"}
DEFAULT_STARTING_BALANCE = paper_forward_runner.DEFAULT_STARTING_BALANCE


def build_oos_splits(fixture_ids: list[str] | None = None) -> dict[str, Any]:
    active_fixture_ids = list(fixture_ids or local_fixture_catalog.list_fixture_ids())
    if not active_fixture_ids:
        active_fixture_ids = []
    heldout_fixtures = _default_heldout(active_fixture_ids)
    train_like_fixtures = [fixture_id for fixture_id in active_fixture_ids if fixture_id not in heldout_fixtures]
    splits = {
        "schema": "AIOS_FOREX_OOS_SPLITS.v1",
        "mode": schemas.PAPER_ONLY,
        "fixture_ids": active_fixture_ids,
        "fixture_count": len(active_fixture_ids),
        "train_like_fixtures": train_like_fixtures,
        "heldout_fixtures": heldout_fixtures,
        "leave_one_regime_out": _leave_one_group_out(active_fixture_ids, "regime"),
        "leave_one_symbol_out": _leave_one_group_out(active_fixture_ids, "symbol"),
        "leave_one_timeframe_out": _leave_one_group_out(active_fixture_ids, "timeframe"),
        "local_only": True,
        "network_allowed": False,
        "broker_allowed": False,
        "live_ready": False,
        "protected_gate_required": True,
    }
    schemas.assert_no_live_permissions(splits)
    return splits


def run_out_of_sample_validation(fixture_ids: list[str] | None = None) -> dict[str, Any]:
    splits = build_oos_splits(fixture_ids)
    train_like_ids = list(splits["train_like_fixtures"])
    heldout_ids = list(splits["heldout_fixtures"])
    train_like = paper_forward_runner.run_multi_fixture_paper_forward(train_like_ids) if train_like_ids else _empty_multi()
    heldout = paper_forward_runner.run_multi_fixture_paper_forward(heldout_ids) if heldout_ids else _empty_multi()
    train_summary = paper_forward_runner.summarize_multi_fixture_paper_forward(train_like)
    heldout_summary = paper_forward_runner.summarize_multi_fixture_paper_forward(heldout)
    leave_regime = [
        _leave_one_result(item)
        for item in list(splits["leave_one_regime_out"])
    ]
    leave_symbol = [
        _leave_one_result(item)
        for item in list(splits["leave_one_symbol_out"])
    ]
    leave_timeframe = [
        _leave_one_result(item)
        for item in list(splits["leave_one_timeframe_out"])
    ]
    heldout_per_fixture = list(heldout_summary.get("per_fixture_results") or [])
    weakest_holdout, strongest_holdout = _ranked_holdouts(heldout_per_fixture)
    degradation_pct = _degradation_pct(train_summary, heldout_summary)
    result = {
        "schema": "AIOS_FOREX_OUT_OF_SAMPLE_VALIDATION.v1",
        "mode": schemas.PAPER_ONLY,
        "splits": splits,
        "fixture_count": int(splits["fixture_count"]),
        "heldout_count": len(heldout_ids),
        "train_like_count": len(train_like_ids),
        "train_like_result": train_like,
        "heldout_result": heldout,
        "train_like_summary": train_summary,
        "heldout_summary": heldout_summary,
        "heldout_pnl": float(heldout_summary.get("aggregate_pnl", 0.0)),
        "heldout_return_pct": _return_pct(float(heldout_summary.get("aggregate_pnl", 0.0))),
        "heldout_consistency_pct": float(heldout_summary.get("consistency_pct", 0.0)),
        "leave_one_regime_results": leave_regime,
        "leave_one_symbol_results": leave_symbol,
        "leave_one_timeframe_results": leave_timeframe,
        "weakest_holdout": weakest_holdout,
        "strongest_holdout": strongest_holdout,
        "degradation_pct": degradation_pct,
        "live_ready": False,
        "protected_gate_required": True,
        "safety": oos_boundary_summary(),
    }
    result["blockers"] = _oos_blockers(result)
    result["classification"] = classify_oos_result(result)
    result["next_safe_action"] = _oos_next_safe_action(result["classification"], result["blockers"])
    result["oos_summary"] = summarize_oos_validation(result)
    schemas.assert_no_live_permissions(result)
    return result


def summarize_oos_validation(result: dict[str, Any]) -> dict[str, Any]:
    payload = dict(result)
    summary = {
        "schema": "AIOS_FOREX_OUT_OF_SAMPLE_VALIDATION_SUMMARY.v1",
        "mode": payload.get("mode", schemas.PAPER_ONLY),
        "fixture_count": int(payload.get("fixture_count", 0)),
        "heldout_count": int(payload.get("heldout_count", 0)),
        "train_like_count": int(payload.get("train_like_count", 0)),
        "heldout_pnl": float(payload.get("heldout_pnl", 0.0)),
        "heldout_return_pct": float(payload.get("heldout_return_pct", 0.0)),
        "heldout_consistency_pct": float(payload.get("heldout_consistency_pct", 0.0)),
        "degradation_pct": float(payload.get("degradation_pct", 100.0)),
        "weakest_holdout": payload.get("weakest_holdout"),
        "strongest_holdout": payload.get("strongest_holdout"),
        "blockers": list(payload.get("blockers") or []),
        "live_ready": False,
        "protected_gate_required": True,
    }
    summary["classification"] = classify_oos_result(payload)
    summary["next_safe_action"] = _oos_next_safe_action(summary["classification"], summary["blockers"])
    schemas.assert_no_live_permissions(summary)
    return summary


def classify_oos_result(result: dict[str, Any]) -> str:
    payload = dict(result)
    if payload.get("classification") == "LIVE_READY" or payload.get("live_ready") is True:
        return "FAIL"
    if int(payload.get("heldout_count", 0)) <= 0:
        return "FAIL"
    if float(payload.get("heldout_pnl", 0.0)) <= 0.0:
        return "FAIL"
    if float(payload.get("heldout_consistency_pct", 0.0)) < 50.0:
        return "FAIL"
    blockers = list(payload.get("blockers") or [])
    if any("non_positive" in str(item) for item in blockers):
        return "FAIL"
    if blockers or float(payload.get("degradation_pct", 100.0)) > 35.0:
        return "WATCHLIST"
    return "PAPER_FORWARD_READY"


def oos_boundary_summary() -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_OOS_BOUNDARY.v1",
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


def _default_heldout(fixture_ids: list[str]) -> list[str]:
    preferred = [
        "EURUSD_15M_TREND_SAMPLE",
        "GBPUSD_5M_TREND_SAMPLE",
        "USDJPY_5M_RANGE_SAMPLE",
    ]
    heldout = [fixture_id for fixture_id in preferred if fixture_id in fixture_ids]
    if heldout:
        return heldout
    return [fixture_id for index, fixture_id in enumerate(fixture_ids) if index % 3 == 2]


def _leave_one_group_out(fixture_ids: list[str], field_name: str) -> list[dict[str, Any]]:
    groups: dict[str, list[str]] = {}
    for fixture_id in fixture_ids:
        fixture = local_fixture_catalog.get_fixture_by_id(fixture_id)
        value = _fixture_field(fixture_id, fixture, field_name)
        groups.setdefault(value, []).append(fixture_id)
    return [
        {
            "split_id": f"leave_one_{field_name}:{value}",
            "field": field_name,
            "heldout_value": value,
            "excluded_fixture_ids": excluded,
            "included_fixture_ids": [fixture_id for fixture_id in fixture_ids if fixture_id not in excluded],
        }
        for value, excluded in sorted(groups.items())
    ]


def _fixture_field(fixture_id: str, fixture: Any, field_name: str) -> str:
    if field_name == "regime":
        return local_fixture_catalog.fixture_regime(fixture_id)
    if field_name == "symbol":
        return str(fixture.symbol)
    if field_name == "timeframe":
        return str(fixture.timeframe)
    return "unknown"


def _leave_one_result(split: dict[str, Any]) -> dict[str, Any]:
    included = list(split.get("included_fixture_ids") or [])
    summary = paper_forward_runner.summarize_multi_fixture_paper_forward(
        paper_forward_runner.run_multi_fixture_paper_forward(included) if included else _empty_multi()
    )
    result = {
        "split_id": split["split_id"],
        "field": split["field"],
        "heldout_value": split["heldout_value"],
        "excluded_fixture_ids": list(split.get("excluded_fixture_ids") or []),
        "included_fixture_count": len(included),
        "aggregate_pnl": float(summary.get("aggregate_pnl", 0.0)),
        "consistency_pct": float(summary.get("consistency_pct", 0.0)),
        "classification": summary.get("classification", "FAIL"),
        "blockers": list(summary.get("blockers") or []),
        "live_ready": False,
        "protected_gate_required": True,
    }
    schemas.assert_no_live_permissions(result)
    return result


def _ranked_holdouts(per_fixture_results: list[dict[str, Any]]) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not per_fixture_results:
        return None, None
    ranked = sorted(
        (
            {
                "fixture_id": str(item.get("fixture_id")),
                "symbol": str(item.get("symbol")),
                "timeframe": str(item.get("timeframe")),
                "regime": str(item.get("regime")),
                "paper_pnl_usd": float(item.get("paper_pnl_usd", 0.0)),
            }
            for item in per_fixture_results
        ),
        key=lambda item: item["paper_pnl_usd"],
    )
    return ranked[0], ranked[-1]


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


def _oos_blockers(result: dict[str, Any]) -> list[str]:
    blockers = []
    if int(result.get("heldout_count", 0)) <= 0:
        blockers.append("oos_missing_heldout_fixtures")
    if float(result.get("heldout_pnl", 0.0)) <= 0.0:
        blockers.append("oos_non_positive_heldout_pnl")
    if float(result.get("heldout_consistency_pct", 0.0)) < 60.0:
        blockers.append("oos_heldout_consistency_below_policy")
    if float(result.get("degradation_pct", 100.0)) > 35.0:
        blockers.append("oos_degradation_exceeds_policy")
    for key in ("leave_one_regime_results", "leave_one_symbol_results", "leave_one_timeframe_results"):
        for item in list(result.get(key) or []):
            if item.get("classification") == "FAIL":
                blockers.append(f"{item.get('split_id')}:failed")
    return _unique(blockers)


def _oos_next_safe_action(classification: str, blockers: list[str]) -> str:
    if classification == "PAPER_FORWARD_READY":
        return "Combine OOS with stress evidence before any broker-paper sandbox readiness contract."
    if blockers:
        return "Resolve OOS degradation or holdout blockers before protected promotion."
    return "Collect stronger deterministic heldout evidence and rerun OOS validation."


def _empty_multi() -> dict[str, Any]:
    return {
        "schema": "AIOS_FOREX_MULTI_FIXTURE_PAPER_FORWARD.v1",
        "mode": schemas.PAPER_ONLY,
        "strategy_id": paper_forward_runner.DEFAULT_STRATEGY_ID,
        "fixture_ids": [],
        "per_fixture_results": [],
        "blockers": ["missing_fixture_ids"],
        "live_ready": False,
        "protected_gate_required": True,
        "safety": oos_boundary_summary(),
    }


def _unique(items: list[str]) -> list[str]:
    unique: list[str] = []
    for item in items:
        if item and item not in unique:
            unique.append(item)
    return unique
