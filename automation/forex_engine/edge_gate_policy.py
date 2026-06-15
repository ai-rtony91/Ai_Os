"""PAPER_ONLY edge gate policy. This never grants live readiness."""


FAIL = "FAIL"
WATCHLIST = "WATCHLIST"
PAPER_FORWARD_READY = "PAPER_FORWARD_READY"


DEFAULT_POLICY = {
    "minimum_trades": 20,
    "minimum_expectancy_r": 0.05,
    "minimum_profit_factor": 1.2,
    "max_drawdown_pct": 10.0,
    "max_losing_streak": 5,
    "minimum_consistent_windows_pct": 60.0,
}


def classify_edge_gate(metrics, walk_forward_summary=None, policy=None, cost_model_used=True):
    active_policy = dict(DEFAULT_POLICY)
    if policy:
        active_policy.update(policy)
    blockers = []
    total_trades = int(metrics.get("total_trades", 0))
    expectancy = float(metrics.get("expectancy_r", 0.0))
    profit_factor = metrics.get("profit_factor")
    max_drawdown_pct = float(metrics.get("max_drawdown_pct", 0.0))
    losing_streak = int(metrics.get("longest_losing_streak", 0))
    consistency_pct = 0.0
    if walk_forward_summary:
        consistency_pct = float(walk_forward_summary.get("consistent_windows_pct", 0.0))

    if not cost_model_used:
        blockers.append("cost_model_required")
    if total_trades < active_policy["minimum_trades"]:
        blockers.append("minimum_sample_size_not_met")
    if expectancy <= active_policy["minimum_expectancy_r"]:
        blockers.append("positive_expectancy_after_costs_not_met")
    if profit_factor is None or float(profit_factor) < active_policy["minimum_profit_factor"]:
        blockers.append("profit_factor_threshold_not_met")
    if max_drawdown_pct > active_policy["max_drawdown_pct"]:
        blockers.append("max_drawdown_cap_exceeded")
    if losing_streak > active_policy["max_losing_streak"]:
        blockers.append("losing_streak_cap_exceeded")
    if walk_forward_summary and consistency_pct < active_policy["minimum_consistent_windows_pct"]:
        blockers.append("walk_forward_consistency_not_met")

    if blockers:
        classification = FAIL if "minimum_sample_size_not_met" in blockers or "cost_model_required" in blockers else WATCHLIST
    else:
        classification = PAPER_FORWARD_READY

    return {
        "mode": "PAPER_ONLY",
        "classification": classification,
        "blockers": blockers,
        "policy": active_policy,
        "live_ready": False,
        "next_safe_action": _next_safe_action(classification),
        "safety_note": "No backtest-only result grants live approval.",
    }


def _next_safe_action(classification):
    if classification == PAPER_FORWARD_READY:
        return "Continue paper-forward research only; no live trading approval."
    if classification == WATCHLIST:
        return "Keep on watchlist and collect stronger out-of-sample paper evidence."
    return "Reject or revise the edge candidate before further paper research."
