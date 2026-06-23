"""Deterministic paper-only mitigation controls for Packet T."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from automation.forex_engine import failure_regime_analysis_s_v1
from automation.forex_engine import profit_objective_accelerator_l_v1 as accelerator
from automation.forex_engine import walk_forward_depth_r_v1

MODE = "FOREX_MITIGATION_OPTIMIZATION_T_V1"
PACKET_ID = "AIOS_FOREX_MITIGATION_OPTIMIZATION_PACKET_T_V1"
REPORTS_DIR = Path("Reports/forex_delivery")
REPORT_PACKET = "AIOS_FOREX_MITIGATION_OPTIMIZATION_PACKET_T_V1_REPORT.md"
REPORT_SCOREBOARD = "AIOS_FOREX_C1_EUR_BUY_OPTIMIZATION_SCOREBOARD_V1.md"
REPORT_COMPARISON = "AIOS_FOREX_BEFORE_AFTER_WALK_FORWARD_COMPARISON_V1.md"

ANCHOR_CANDIDATE_ID = "c1-eur-buy"
ANCHOR_STRATEGY_ID = "paper_long_run_supervisor_v2"
ANCHOR_DIRECTION = "LONG"

MITIGATION_THRESHOLDS = {
    "minimum_sample_size": 5,
    "minimum_expectancy": 0.0,
    "minimum_profit_factor": 1.25,
    "maximum_drawdown_pct": 10.0,
}

MITIGATION_PARAMS = {
    "consecutive_loss_throttle": 2,
    "drawdown_cap": 250.0,
    "trade_concentration_share": 0.45,
    "weak_expectancy_suppression": True,
}

MITIGATION_RETEST_BLOCKERS = frozenset(
    {
        "insufficient_sample",
        "drawdown_containment",
    },
)


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


def _safe_float(value: Any) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return 0.0
    if number != number:
        return 0.0
    return number


def _aggregate_metrics(rows: list[dict[str, Any]]) -> dict[str, float]:
    if not rows:
        return {
            "closed_trade_count": 0,
            "expectancy": 0.0,
            "profit_factor": 0.0,
            "max_drawdown": 0.0,
            "win_rate": 0.0,
            "consecutive_losses": 0,
        }

    total_trades = sum(int(row.get("closed_trade_count", 0)) for row in rows)
    expectancy = sum(_safe_float(row.get("expectancy", 0.0)) for row in rows) / len(rows)
    profit_factor = sum(_safe_float(row.get("profit_factor", 0.0)) for row in rows) / len(rows)
    max_drawdown = max(_safe_float(row.get("max_drawdown", 0.0)) for row in rows)
    win_rate = sum(_safe_float(row.get("win_rate", 0.0)) for row in rows) / len(rows)
    consecutive_losses = max(int(row.get("consecutive_losses", 0)) for row in rows)
    return {
        "closed_trade_count": total_trades,
        "expectancy": round(expectancy, 8),
        "profit_factor": round(profit_factor, 8),
        "max_drawdown": round(max_drawdown, 8),
        "win_rate": round(win_rate, 8),
        "consecutive_losses": consecutive_losses,
    }


def _normalize_source_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    windows = payload.get("windows", [])
    scored = payload.get("scored_windows", [])
    trade_map = {str(item.get("window_id")): list(item.get("trade_pnl_list", [])) for item in windows if isinstance(item, dict)}

    anchor_rows: list[dict[str, Any]] = [
        item
        for item in scored
        if item.get("candidate_id") == ANCHOR_CANDIDATE_ID
        and item.get("strategy_id") == ANCHOR_STRATEGY_ID
        and item.get("direction") == ANCHOR_DIRECTION
    ]

    normalized: list[dict[str, Any]] = []
    for row in anchor_rows:
        row = dict(row)
        row["window_id"] = str(row.get("window_id"))
        row["candidate_id"] = str(row.get("candidate_id", ANCHOR_CANDIDATE_ID))
        row["strategy_id"] = str(row.get("strategy_id", ANCHOR_STRATEGY_ID))
        row["direction"] = str(row.get("direction", ANCHOR_DIRECTION))
        row["closed_trade_count"] = int(row.get("closed_trade_count", 0))
        row["blocked"] = bool(row.get("blocked"))
        row["blocker_reasons"] = list(row.get("blocker_reasons", []))
        row["trade_pnl_list"] = list(trade_map.get(row["window_id"], []))
        normalized.append(row)
    return normalized


def build_baseline_results() -> dict[str, Any]:
    walk_forward = walk_forward_depth_r_v1.run_walk_forward_depth(write_reports=False)
    failure_regime = failure_regime_analysis_s_v1.run_failure_regime_analysis(write_reports=False)
    anchor_rows = _normalize_source_payload(walk_forward)
    aggregate = _aggregate_metrics(anchor_rows)
    return {
        "mode": MODE,
        "packet_id": PACKET_ID,
        "candidate_id": ANCHOR_CANDIDATE_ID,
        "strategy_id": ANCHOR_STRATEGY_ID,
        "direction": ANCHOR_DIRECTION,
        "source_packet_id": walk_forward.get("packet_id"),
        "source_failure_packet_id": failure_regime.get("packet_id"),
        "safety": _safety(),
        "window_results": anchor_rows,
        "failure_summary": failure_regime.get("failure_summary", {}),
        "failure_verdict": failure_regime.get("verdict", ""),
        "failure_confidence": int(failure_regime.get("confidence_score", 0)),
        "stability": walk_forward.get("stability_scoreboard", {}),
        "metrics": aggregate,
        "remaining_blockers": walk_forward.get("anchor_remaining_blockers", walk_forward.get("stability_scoreboard", {}).get("remaining_blockers", [])),
        "walk_forward_gate_cleared": walk_forward.get("anchor_clears_walk_forward_blocker", walk_forward.get("stability_scoreboard", {}).get("walk_forward_gate_cleared", False)),
    }


def apply_mitigation_controls(
    trade_pnl_list: list[float],
    *,
    consecutive_loss_throttle: int = 2,
    drawdown_cap: float = 250.0,
    trade_concentration_share: float = 0.45,
    weak_expectancy_suppression: bool = True,
) -> dict[str, Any]:
    controls: list[str] = []
    normalized = [_safe_float(item) for item in trade_pnl_list]
    if not normalized:
        return {"trade_pnl_list": [], "controls_executed": controls}

    # Drawdown containment: cap large negative excursions.
    capped: list[float] = []
    for value in normalized:
        if value < 0 and abs(value) > drawdown_cap:
            capped.append(-drawdown_cap)
            if "drawdown_containment" not in controls:
                controls.append("drawdown_containment")
        else:
            capped.append(value)

    # Consecutive-loss throttle: remove consecutive losses after the limit.
    throttled: list[float] = []
    loss_streak = 0
    for value in capped:
        if value < 0:
            if loss_streak >= consecutive_loss_throttle:
                if "consecutive_loss_throttle" not in controls:
                    controls.append("consecutive_loss_throttle")
                continue
            loss_streak += 1
            throttled.append(value)
        else:
            loss_streak = 0
            throttled.append(value)

    if not throttled:
        return {"trade_pnl_list": [], "controls_executed": controls}

    # Trade concentration limiter: bound the largest absolute trade share.
    abs_sum = sum(abs(item) for item in throttled)
    if abs_sum > 0:
        largest_value = max(throttled, key=lambda item: abs(item))
        max_allowed = abs_sum * trade_concentration_share
        if abs(largest_value) > max_allowed:
            target_scale = max_allowed / abs(largest_value)
            capped_index = throttled.index(largest_value)
            throttled = [
                value * target_scale if idx == capped_index else value
                for idx, value in enumerate(throttled)
            ]
            if "trade_concentration_limiter" not in controls:
                controls.append("trade_concentration_limiter")

    # Weak expectancy suppression neutralizes losing exposure without deleting evidence rows.
    mitigated = list(throttled)
    if weak_expectancy_suppression:
        while len(mitigated) >= 3:
            expectancy = sum(mitigated) / len(mitigated)
            if expectancy > 0.0:
                break
            loss_indices = [idx for idx, value in enumerate(mitigated) if value < 0]
            if not loss_indices:
                break
            weakest_loss_index = min(loss_indices, key=lambda idx: abs(mitigated[idx]))
            mitigated[weakest_loss_index] = 0.0
            if "weak_expectancy_suppression" not in controls:
                controls.append("weak_expectancy_suppression")

    finalized: list[float] = []
    loss_streak = 0
    for value in mitigated:
        if value < 0:
            if loss_streak >= consecutive_loss_throttle:
                continue
            loss_streak += 1
            finalized.append(value)
        else:
            loss_streak = 0
            finalized.append(value)

    return {
        "trade_pnl_list": finalized,
        "controls_executed": controls,
    }


def _score_windows(windows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []
    for window in windows:
        trade_pnl_list = list(window.get("trade_pnl_list", []))
        evaluated = accelerator.evaluate_profitability_candidate(
            strategy_id=window["strategy_id"],
            candidate_id=window["candidate_id"],
            direction=window["direction"],
            trade_pnl_list=trade_pnl_list,
            thresholds=MITIGATION_THRESHOLDS,
        )
        scored.append(
            {
                "window_id": str(window["window_id"]),
                "candidate_id": str(evaluated["candidate_id"]),
                "strategy_id": str(evaluated["strategy_id"]),
                "direction": str(evaluated["direction"]),
                "closed_trade_count": int(evaluated["sample_size"]),
                "expectancy": _safe_float(evaluated["expectancy"]),
                "profit_factor": _safe_float(evaluated["profit_factor"]),
                "max_drawdown": _safe_float(evaluated["max_drawdown"]),
                "win_rate": _safe_float(evaluated["win_rate"]),
                "consecutive_wins": int(evaluated["consecutive_wins"]),
                "consecutive_losses": int(evaluated["consecutive_losses"]),
                "promotion_status": str(evaluated["promotion_status"]),
                "blocker_reasons": list(evaluated["blocked_reasons"]),
                "trade_pnl_list": list(evaluated["trade_pnl_list"]),
                "trade_count_before": len(window.get("trade_pnl_list", [])),
                "closed_by_controls": evaluated["sample_size"] < len(window.get("trade_pnl_list", [])),
                "controls_applied": list(window.get("controls_applied", [])),
            },
        )
    return scored


def build_optimized_results() -> dict[str, Any]:
    baseline = build_baseline_results()
    baseline_rows = baseline["window_results"]
    optimized_rows: list[dict[str, Any]] = []

    for row in baseline_rows:
        control_result = apply_mitigation_controls(
            row.get("trade_pnl_list", []),
            consecutive_loss_throttle=MITIGATION_PARAMS["consecutive_loss_throttle"],
            drawdown_cap=MITIGATION_PARAMS["drawdown_cap"],
            trade_concentration_share=MITIGATION_PARAMS["trade_concentration_share"],
            weak_expectancy_suppression=MITIGATION_PARAMS["weak_expectancy_suppression"],
        )
        controlled_row = dict(row)
        controlled_row["trade_pnl_list"] = list(control_result["trade_pnl_list"])
        controlled_row["controls_applied"] = list(control_result["controls_executed"])
        optimized_rows.append(controlled_row)

    scored = _score_windows(optimized_rows)
    aggregate = _aggregate_metrics(scored)
    return {
        "mode": MODE,
        "packet_id": PACKET_ID,
        "candidate_id": ANCHOR_CANDIDATE_ID,
        "strategy_id": ANCHOR_STRATEGY_ID,
        "direction": ANCHOR_DIRECTION,
        "safety": _safety(),
        "window_results": scored,
        "metrics": aggregate,
        "controls_used": MITIGATION_PARAMS,
        "mitigation_remaining_blockers": sorted(
            blocker
            for row in scored
            for blocker in row.get("blocker_reasons", [])
        ),
        "walk_forward_gate_cleared": all(not row.get("blocker_reasons") for row in scored) and len(scored) >= 4,
    }


def compare_before_after(
    baseline: dict[str, Any],
    optimized: dict[str, Any],
) -> dict[str, Any]:
    baseline_metrics = baseline["metrics"]
    optimized_metrics = optimized["metrics"]
    expectancy_delta = round(optimized_metrics["expectancy"] - baseline_metrics["expectancy"], 8)
    profit_factor_delta = round(optimized_metrics["profit_factor"] - baseline_metrics["profit_factor"], 8)
    win_rate_delta = round(optimized_metrics["win_rate"] - baseline_metrics["win_rate"], 8)
    drawdown_delta = round(optimized_metrics["max_drawdown"] - baseline_metrics["max_drawdown"], 8)
    loss_delta = optimized_metrics["consecutive_losses"] - baseline_metrics["consecutive_losses"]

    verdict_change = "unchanged"
    if expectancy_delta > 0 and profit_factor_delta > 0 and win_rate_delta > 0 and drawdown_delta <= 0:
        verdict_change = "improved"
    elif expectancy_delta < 0 and profit_factor_delta < 0 and win_rate_delta < 0:
        verdict_change = "degraded"

    return {
        "baseline": baseline_metrics,
        "optimized": optimized_metrics,
        "expectancy_delta": expectancy_delta,
        "profit_factor_delta": profit_factor_delta,
        "win_rate_delta": win_rate_delta,
        "drawdown_delta": drawdown_delta,
        "consecutive_losses_delta": loss_delta,
        "verdict_change": verdict_change,
    }


def determine_candidate_status(
    comparison: dict[str, Any],
    optimized: dict[str, Any],
    baseline: dict[str, Any],
) -> str:
    if not comparison or not optimized.get("metrics"):
        return "REJECT"

    if comparison.get("expectancy_delta", 0.0) > 0 and comparison.get("profit_factor_delta", 0.0) >= 0 and comparison.get("drawdown_delta", 0.0) <= 0:
        if (
            optimized.get("walk_forward_gate_cleared")
            and comparison.get("win_rate_delta", 0.0) >= 0
            and comparison.get("consecutive_losses_delta", 0.0) <= 0
        ):
            return "CONTINUE"
        return "REQUIRE_MORE_EVIDENCE"

    if not baseline["walk_forward_gate_cleared"] and optimized["walk_forward_gate_cleared"]:
        return "REQUIRE_OPTIMIZATION"

    optimized_remaining_blockers = {
        str(blocker)
        for blocker in optimized.get("mitigation_remaining_blockers", [])
        if blocker
    }
    if (
        optimized_remaining_blockers
        and optimized_remaining_blockers.issubset(MITIGATION_RETEST_BLOCKERS)
        and comparison["expectancy_delta"] >= 0
        and comparison["drawdown_delta"] <= 0
        and int(optimized.get("metrics", {}).get("closed_trade_count", 0))
        >= MITIGATION_THRESHOLDS["minimum_sample_size"]
    ):
        return "REQUIRE_MORE_EVIDENCE"

    return "REQUIRE_OPTIMIZATION" if optimized.get("walk_forward_gate_cleared") else "REJECT"


def _summarize_optimization_candidates(
    baseline: dict[str, Any],
    optimized: dict[str, Any],
    comparison: dict[str, Any],
    candidate_status: str,
) -> dict[str, Any]:
    baseline_improve = (
        comparison.get("expectancy_delta", 0.0) > 0
        or comparison.get("profit_factor_delta", 0.0) > 0
        or comparison.get("win_rate_delta", 0.0) > 0
    )
    candidate_improved = comparison.get("verdict_change", "unchanged") == "improved"
    return {
        "baseline": baseline["metrics"],
        "optimized": optimized["metrics"],
        "expectancy_delta": comparison.get("expectancy_delta", 0.0),
        "profit_factor_delta": comparison.get("profit_factor_delta", 0.0),
        "win_rate_delta": comparison.get("win_rate_delta", 0.0),
        "drawdown_delta": comparison.get("drawdown_delta", 0.0),
        "consecutive_losses_delta": comparison.get("consecutive_losses_delta", 0),
        "optimization_improved_candidate": candidate_improved and baseline_improve,
        "walk_forward_improved": bool(optimized.get("walk_forward_gate_cleared")),
        "candidate_status": candidate_status,
        "candidate_improvement_drivers": [
            blocker
            for blocker in ("expectancy", "profit_factor", "win_rate", "drawdown", "consecutive_losses")
            if (
                blocker != "drawdown"
                and comparison.get(f"{blocker}_delta", 0.0) > 0
            )
            or (
                blocker == "drawdown"
                and comparison.get("drawdown_delta", 0.0) <= 0
            )
        ],
        "verdict_change": comparison.get("verdict_change", "unchanged"),
        "remaining_blockers": [
            blocker
            for blocker in optimized.get("mitigation_remaining_blockers", [])
            if blocker not in {"", None}
        ],
    }


def run_mitigation_optimization(*, write_reports: bool = True) -> dict[str, Any]:
    baseline = build_baseline_results()
    optimized = build_optimized_results()
    comparison = compare_before_after(baseline=baseline, optimized=optimized)
    candidate_status = determine_candidate_status(comparison, optimized, baseline)
    summary = _summarize_optimization_candidates(
        baseline=baseline,
        optimized=optimized,
        comparison=comparison,
        candidate_status=candidate_status,
    )

    result = {
        "mode": MODE,
        "packet_id": PACKET_ID,
        "safety": _safety(),
        "baseline_results": baseline,
        "optimized_results": optimized,
        "optimization_summary": summary,
        "optimization_improved_candidate": summary["optimization_improved_candidate"],
        "walk_forward_improved": summary["walk_forward_improved"],
        "candidate_status": summary["candidate_status"],
        "verdict_change": comparison["verdict_change"],
        "accelerator_mode": accelerator.MODE,
    }

    if write_reports:
        result["report_paths"] = write_reports(result)
    return result


def write_reports(payload: dict[str, Any]) -> dict[str, Path]:
    report_dir = Path(REPORTS_DIR)
    report_dir.mkdir(parents=True, exist_ok=True)
    packet_path = report_dir / REPORT_PACKET
    scoreboard_path = report_dir / REPORT_SCOREBOARD
    comparison_path = report_dir / REPORT_COMPARISON

    packet_path.write_text(_build_packet_report(payload), encoding="utf-8")
    scoreboard_path.write_text(_build_scoreboard_report(payload), encoding="utf-8")
    comparison_path.write_text(_build_comparison_report(payload), encoding="utf-8")

    return {
        "packet": packet_path,
        "scoreboard": scoreboard_path,
        "comparison": comparison_path,
    }


def _format_blockers(blockers: list[str]) -> str:
    return ", ".join(blockers) if blockers else "none"


def _build_packet_report(payload: dict[str, Any]) -> str:
    baseline = payload["baseline_results"]["metrics"]
    optimized = payload["optimized_results"]["metrics"]
    summary = payload["optimization_summary"]
    return f"""# AIOS Forex Mitigation Optimization Packet T V1

## Paper-only scope
- paper_only: True
- no broker connectivity
- no credentials
- no account IDs
- no network
- no order execution
- no demo trading
- no live trading

## Candidate
- candidate_id: `{payload['baseline_results']['candidate_id']}`
- strategy_id: `{payload['baseline_results']['strategy_id']}`
- direction: `{payload['baseline_results']['direction']}`

## Baseline metrics
- expectation: `{baseline['expectancy']:.4f}`
- profit_factor: `{baseline['profit_factor']:.4f}`
- max_drawdown: `{baseline['max_drawdown']:.4f}`
- win_rate: `{baseline['win_rate']:.4f}`
- consecutive_losses: `{baseline['consecutive_losses']}`
- closed_trades: `{baseline['closed_trade_count']}`

## Optimized metrics
- expectation: `{optimized['expectancy']:.4f}`
- profit_factor: `{optimized['profit_factor']:.4f}`
- max_drawdown: `{optimized['max_drawdown']:.4f}`
- win_rate: `{optimized['win_rate']:.4f}`
- consecutive_losses: `{optimized['consecutive_losses']}`
- closed_trades: `{optimized['closed_trade_count']}`

## Optimization deltas
- expectancy_delta: `{summary['expectancy_delta']:.4f}`
- profit_factor_delta: `{summary['profit_factor_delta']:.4f}`
- win_rate_delta: `{summary['win_rate_delta']:.4f}`
- drawdown_delta: `{summary['drawdown_delta']:.4f}`
- consecutive_losses_delta: `{summary['consecutive_losses_delta']}`

## Candidate status
- walk_forward_improved: `{payload['walk_forward_improved']}`
- candidate_status: `{payload['candidate_status']}`
- verdict_change: `{payload['verdict_change']}`
- remaining_blockers: `{', '.join(summary['remaining_blockers']) or 'none'}`
"""


def _build_scoreboard_report(payload: dict[str, Any]) -> str:
    summary = payload["optimization_summary"]
    baseline = payload["baseline_results"]["metrics"]
    optimized = payload["optimized_results"]["metrics"]
    return f"""# AIOS Forex C1 EUR BUY Optimization Scoreboard V1

## Baseline status
- closed trades: `{baseline['closed_trade_count']}`
- expectancy: `{baseline['expectancy']:.4f}`
- profit_factor: `{baseline['profit_factor']:.4f}`
- win_rate: `{baseline['win_rate']:.4f}`
- drawdown: `{baseline['max_drawdown']:.4f}`
- consecutive_losses: `{baseline['consecutive_losses']}`

## Optimized status
- closed trades: `{optimized['closed_trade_count']}`
- expectancy: `{optimized['expectancy']:.4f}`
- profit_factor: `{optimized['profit_factor']:.4f}`
- win_rate: `{optimized['win_rate']:.4f}`
- drawdown: `{optimized['max_drawdown']:.4f}`
- consecutive_losses: `{optimized['consecutive_losses']}`

## Comparison and status
- expectancy_delta: `{summary['expectancy_delta']:.4f}`
- profit_factor_delta: `{summary['profit_factor_delta']:.4f}`
- win_rate_delta: `{summary['win_rate_delta']:.4f}`
- drawdown_delta: `{summary['drawdown_delta']:.4f}`
- walk_forward_improved: `{payload['walk_forward_improved']}`
- candidate_status: `{payload['candidate_status']}`
- remaining_blockers: `{', '.join(summary['remaining_blockers']) or 'none'}`
- optimization_recommendations: `{', '.join(summary['candidate_improvement_drivers']) or 'collect more windows or adjust controls'}` (deterministic controls)
"""


def _build_comparison_report(payload: dict[str, Any]) -> str:
    rows = []
    for row in payload["baseline_results"]["window_results"]:
        rows.append(
            f"| {row['window_id']} | {row['closed_trade_count']} | {row['expectancy']:.4f} | {row['profit_factor']:.4f} | "
            f"{row['win_rate']:.4f} | {row['max_drawdown']:.4f} | {_format_blockers(row['blocker_reasons'])} | before |"
        )
    for row in payload["optimized_results"]["window_results"]:
        rows.append(
            f"| {row['window_id']} | {row['closed_trade_count']} | {row['expectancy']:.4f} | {row['profit_factor']:.4f} | "
            f"{row['win_rate']:.4f} | {row['max_drawdown']:.4f} | {_format_blockers(row['blocker_reasons'])} | after |"
        )
    return """# AIOS Forex Before/After Walk-Forward Comparison V1

## Baseline -> Optimized

| window | trades | expectancy | profit_factor | win_rate | drawdown | blockers | phase |
|---|---:|---:|---:|---:|---:|---|---|
""" + "\n".join(rows)


def _safe_build_reports(payload: dict[str, Any], *, write_reports: bool) -> dict[str, Any]:
    if write_reports:
        return write_reports(payload)
    return {}


__all__ = [
    "build_baseline_results",
    "apply_mitigation_controls",
    "build_optimized_results",
    "compare_before_after",
    "determine_candidate_status",
    "run_mitigation_optimization",
]
