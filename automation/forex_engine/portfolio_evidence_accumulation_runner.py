"""Canonical paper-only evidence accumulation runner for strategy portfolio selection."""
from __future__ import annotations

from collections import Counter
from typing import Any
from collections.abc import Mapping, Sequence

from automation.forex_engine.strategy_portfolio_competition_runner import run_strategy_portfolio_competition

MODE = "PORTFOLIO_EVIDENCE_ACCUMULATION_RUNNER_ONLY"
DEFAULT_MIN_BATCHES = 3
DEFAULT_MIN_WINNER_CONSISTENCY = 0.67


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "portfolio_evidence_accumulation_runner_only": True,
        "broker_access": False,
        "credentials_access": False,
        "network_access": False,
        "live_trading_active": False,
        "demo_execution_active": False,
        "capital_allocation_modified": False,
    }


def _to_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lower = value.strip().lower()
        if lower in {"true", "1", "yes"}:
            return True
        if lower in {"false", "0", "no"}:
            return False
    return None


def _safe(value: Any) -> bool:
    safety = value if isinstance(value, Mapping) else {}
    if not isinstance(safety, Mapping):
        safety = {}
    if not _to_bool(safety.get("paper_only")):
        return False

    blocked_keys = (
        "broker_access",
        "credentials_access",
        "network_access",
        "live_trading_active",
        "demo_execution_active",
        "capital_allocation_modified",
    )
    for key in blocked_keys:
        if _to_bool(safety.get(key)) is True:
            return False
    return True


def _as_batches(raw_batches: Any) -> list[Any]:
    if raw_batches is None:
        return []
    if not isinstance(raw_batches, Sequence) or isinstance(raw_batches, (str, bytes)):
        return []
    return list(raw_batches)


def _extract_competitors(batch: Any) -> list[dict[str, Any]]:
    if isinstance(batch, Mapping):
        for key in ("strategy_competitors", "competitors", "strategy_results", "strategies"):
            if key in batch:
                entries = batch[key]
                if isinstance(entries, Sequence) and not isinstance(entries, (str, bytes)):
                    return [dict(item) for item in entries if isinstance(item, Mapping)]
                return []
    if isinstance(batch, Sequence) and not isinstance(batch, (str, bytes)):
        return [dict(item) for item in batch if isinstance(item, Mapping)]
    return []


def run_portfolio_evidence_accumulation_runner(
    *,
    evidence_batches: Any = None,
    competition_batches: Any = None,
    strategy_batches: Any = None,
    minimum_batches: int = DEFAULT_MIN_BATCHES,
    winner_consistency_threshold: float = DEFAULT_MIN_WINNER_CONSISTENCY,
) -> dict[str, Any]:
    # Select the first supported input. Keep deterministic priority for testability.
    configured_batches = (
        evidence_batches
        if evidence_batches is not None
        else strategy_batches
        if strategy_batches is not None
        else competition_batches
    )

    raw_batches = _as_batches(configured_batches)
    batches_evaluated = len(raw_batches)
    competition_results: list[dict[str, Any]] = []
    winner_counter: Counter[str] = Counter()
    winner_examples: dict[str, dict[str, Any]] = {}
    blocked_reasons: list[str] = []

    if batches_evaluated == 0:
        blocked_reasons.append("no_batches_provided")
        return {
            "accumulation_completed": False,
            "batches_evaluated": 0,
            "competition_results": [],
            "stable_winner": {},
            "winner_consistency_rate": 0.0,
            "portfolio_ready": False,
            "blocked_reasons": blocked_reasons,
            "next_safe_action": "provide_evidence_batches",
            "safety": _safety(),
            "mode": MODE,
        }

    for index, raw_batch in enumerate(raw_batches):
        competitors = _extract_competitors(raw_batch)
        competition = run_strategy_portfolio_competition(strategy_competitors=competitors)
        winner = dict(competition.get("winner", {}))
        result_entry = {
            "batch_index": index,
            "competition_completed": bool(competition.get("competition_completed")),
            "winner": winner,
            "winner_safe": bool(winner and _safe(winner.get("safety"))),
            "portfolio_ready": bool(competition.get("portfolio_ready")),
            "blocked_reasons": list(competition.get("blocked_reasons", [])),
            "competition": competition,
        }
        competition_results.append(result_entry)

        winner_name = str(winner.get("strategy_name", "")).strip()
        if winner and winner_name:
            if competition.get("portfolio_ready") and _safe(winner.get("safety")):
                winner_counter[winner_name] += 1
                winner_examples.setdefault(winner_name, winner)

        if result_entry["blocked_reasons"]:
            blocked_reasons.extend(result_entry["blocked_reasons"])

    competition_completed = all(item["competition_completed"] for item in competition_results)

    safe_strategies_merged = any(
        entry["winner_safe"] for entry in competition_results if isinstance(entry.get("winner"), Mapping)
    )

    if not safe_strategies_merged:
        blocked_reasons.append("no_safe_strategies_remain")

    winner_consistency_rate = 0.0
    stable_winner: dict[str, Any] = {}
    if winner_counter:
        most_common_wins = winner_counter.most_common()
        winner_consistency_rate = round(most_common_wins[0][1] / batches_evaluated, 4)
        stable_winner = dict(winner_examples.get(most_common_wins[0][0], {}))

    if batches_evaluated < max(1, int(minimum_batches)):
        blocked_reasons.append("insufficient_batches")

    if not winner_counter:
        blocked_reasons.append("no_stable_winner")

    if winner_counter and winner_consistency_rate < float(winner_consistency_threshold):
        blocked_reasons.append("winner_consistency_below_threshold")

    if winner_consistency_rate == 0.0 and batches_evaluated >= max(1, int(minimum_batches)):
        blocked_reasons.append("all_batches_failed")

    blocked_reasons = list(dict.fromkeys(str(reason) for reason in blocked_reasons if reason))

    portfolio_ready = bool(
        competition_completed
        and stable_winner
        and winner_counter
        and safe_strategies_merged
        and batches_evaluated >= max(1, int(minimum_batches))
        and winner_consistency_rate >= float(winner_consistency_threshold)
    )

    if portfolio_ready:
        next_safe_action = "start_portfolio_monitoring_and_risk_checks"
    elif not competition_completed:
        next_safe_action = "rerun_failed_batches"
    elif "no_safe_strategies_remain" in blocked_reasons:
        next_safe_action = "remove_unsafe_candidates_and_retry"
    elif "insufficient_batches" in blocked_reasons:
        next_safe_action = "collect_additional_evidence_batches"
    else:
        next_safe_action = "collect_more_stable_evidence"

    return {
        "accumulation_completed": bool(competition_results),
        "batches_evaluated": batches_evaluated,
        "competition_results": competition_results,
        "stable_winner": stable_winner,
        "winner_consistency_rate": winner_consistency_rate,
        "portfolio_ready": portfolio_ready,
        "blocked_reasons": blocked_reasons,
        "next_safe_action": next_safe_action,
        "safety": _safety(),
        "mode": MODE,
    }
