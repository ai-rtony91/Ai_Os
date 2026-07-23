"""Read-only extended Forex evidence campaign evaluator.

This module classifies genuine market-demo evidence into progressively stronger
trust tiers. It never calls a broker, places orders, reads credentials, moves
money, or authorizes live trading.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

SCHEMA = "aios.forex.extended_evidence_campaign.v1"
MODE = "READ_ONLY_EVIDENCE_AUDIT"

BLOCKED_LEDGER_MISSING = "BLOCKED_LEDGER_MISSING"
BLOCKED_LEDGER_INVALID = "BLOCKED_LEDGER_INVALID"
BLOCKED_NO_MARKET_DEMO_EVIDENCE = "BLOCKED_NO_MARKET_DEMO_EVIDENCE"
BLOCKED_SAFETY_VIOLATION = "BLOCKED_SAFETY_VIOLATION"
BLOCKED_STALE_EVIDENCE = "BLOCKED_STALE_EVIDENCE"
BLOCKED_METRICS_INCOMPLETE = "BLOCKED_METRICS_INCOMPLETE"
COLLECTING_MARKET_DEMO_EVIDENCE = "COLLECTING_MARKET_DEMO_EVIDENCE"
SYSTEM_MINIMUM_REACHED = "SYSTEM_MINIMUM_REACHED"
EARLY_CONFIDENCE_REACHED = "EARLY_CONFIDENCE_REACHED"
STRONG_CONFIDENCE_REACHED = "STRONG_CONFIDENCE_REACHED"
PRODUCTION_CANDIDATE_READY_FOR_OWNER_REVIEW = (
    "PRODUCTION_CANDIDATE_READY_FOR_OWNER_REVIEW"
)

MAX_EVIDENCE_AGE_DAYS = 14

SYNTHETIC_MARKERS = (
    "fixture",
    "mock",
    "synthetic",
    "paper_simulation",
    "paper signal",
    "paper_signal_execution_loop",
    "simulated",
)
MARKET_DEMO_MARKERS = (
    "oanda",
    "broker_demo",
    "broker demo",
    "practice",
    "market_demo",
    "market demo",
)

SAFETY_FALSE_FIELDS = (
    "live_trading_allowed",
    "live_order_execution_allowed",
    "live_capital_action_authorized",
    "money_movement_allowed",
    "bank_access_allowed",
)


@dataclass(frozen=True)
class Tier:
    name: str
    status: str
    minimum_market_trades: int
    minimum_days: int
    minimum_windows: int
    minimum_expectancy: float
    minimum_profit_factor: float
    maximum_drawdown_pct: float


TIERS: tuple[Tier, ...] = (
    Tier(
        name="SYSTEM_MINIMUM",
        status=SYSTEM_MINIMUM_REACHED,
        minimum_market_trades=30,
        minimum_days=5,
        minimum_windows=2,
        minimum_expectancy=0.0,
        minimum_profit_factor=1.10,
        maximum_drawdown_pct=10.0,
    ),
    Tier(
        name="EARLY_CONFIDENCE",
        status=EARLY_CONFIDENCE_REACHED,
        minimum_market_trades=100,
        minimum_days=20,
        minimum_windows=4,
        minimum_expectancy=0.0,
        minimum_profit_factor=1.15,
        maximum_drawdown_pct=8.0,
    ),
    Tier(
        name="STRONG_CONFIDENCE",
        status=STRONG_CONFIDENCE_REACHED,
        minimum_market_trades=300,
        minimum_days=45,
        minimum_windows=6,
        minimum_expectancy=0.0,
        minimum_profit_factor=1.20,
        maximum_drawdown_pct=7.0,
    ),
    Tier(
        name="PRODUCTION_CANDIDATE",
        status=PRODUCTION_CANDIDATE_READY_FOR_OWNER_REVIEW,
        minimum_market_trades=500,
        minimum_days=60,
        minimum_windows=8,
        minimum_expectancy=0.0,
        minimum_profit_factor=1.25,
        maximum_drawdown_pct=6.0,
    ),
)


def evaluate_extended_evidence_campaign(
    ledger_path: str | Path,
    *,
    as_of_date: date | None = None,
) -> dict[str, Any]:
    """Evaluate an AIOS demo evidence ledger without mutating it."""

    path = Path(ledger_path)
    if not path.exists():
        return _result(
            status=BLOCKED_LEDGER_MISSING,
            blockers=[f"ledger_missing:{path}"],
            summary=_empty_summary(),
            next_tier=TIERS[0],
        )

    try:
        entries = list(_read_jsonl(path))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return _result(
            status=BLOCKED_LEDGER_INVALID,
            blockers=[f"ledger_invalid:{type(exc).__name__}"],
            summary=_empty_summary(),
            next_tier=TIERS[0],
        )

    today = as_of_date or datetime.now(timezone.utc).date()
    real_entries = [
        entry for entry in entries if str(entry.get("record_type", "")).upper() == "REAL_DEMO_DAY"
    ]

    classified = [(_classify_entry(entry), entry) for entry in real_entries]
    market_entries = [entry for kind, entry in classified if kind == "MARKET_DEMO"]
    synthetic_entries = [entry for kind, entry in classified if kind == "FIXTURE_OR_SIMULATION"]
    unclassified_entries = [entry for kind, entry in classified if kind == "UNCLASSIFIED"]

    summary = _build_summary(
        real_entries=real_entries,
        market_entries=market_entries,
        synthetic_entries=synthetic_entries,
        unclassified_entries=unclassified_entries,
        today=today,
    )

    safety_blockers = _safety_blockers(market_entries)
    if safety_blockers:
        return _result(
            status=BLOCKED_SAFETY_VIOLATION,
            blockers=safety_blockers,
            summary=summary,
            next_tier=TIERS[0],
        )

    if not market_entries or summary["market_demo_trades"] <= 0:
        return _result(
            status=BLOCKED_NO_MARKET_DEMO_EVIDENCE,
            blockers=[
                "no_genuine_market_demo_trades",
                f"fixture_or_simulation_trades:{summary['fixture_or_simulation_trades']}",
            ],
            summary=summary,
            next_tier=TIERS[0],
        )

    if not summary["evidence_age_ok"]:
        return _result(
            status=BLOCKED_STALE_EVIDENCE,
            blockers=[
                f"latest_market_evidence_age_days:{summary['latest_market_evidence_age_days']}",
                f"maximum_allowed_age_days:{MAX_EVIDENCE_AGE_DAYS}",
            ],
            summary=summary,
            next_tier=TIERS[0],
        )

    if not summary["metrics_complete"]:
        return _result(
            status=BLOCKED_METRICS_INCOMPLETE,
            blockers=list(summary["metric_blockers"]),
            summary=summary,
            next_tier=TIERS[0],
        )

    achieved: Tier | None = None
    next_tier: Tier | None = None
    for tier in TIERS:
        if _tier_passes(tier, summary):
            achieved = tier
        elif next_tier is None:
            next_tier = tier

    if achieved is None:
        next_tier = next_tier or TIERS[0]
        return _result(
            status=COLLECTING_MARKET_DEMO_EVIDENCE,
            blockers=_tier_blockers(next_tier, summary),
            summary=summary,
            next_tier=next_tier,
            achieved_tier=None,
        )

    if next_tier is None:
        next_tier = TIERS[-1]

    return _result(
        status=achieved.status,
        blockers=[],
        summary=summary,
        next_tier=next_tier,
        achieved_tier=achieved,
    )


def _read_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8-sig") as handle:
        for line_number, raw in enumerate(handle, start=1):
            if not raw.strip():
                continue
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError(f"line_{line_number}_not_object")
            yield value


def _classify_entry(entry: Mapping[str, Any]) -> str:
    source_text = " ".join(
        str(entry.get(field, ""))
        for field in (
            "session_mode",
            "session_source",
            "strategy_name",
            "source_label",
            "evidence_source",
            "broker",
            "environment",
        )
    ).lower()

    if any(marker in source_text for marker in SYNTHETIC_MARKERS):
        return "FIXTURE_OR_SIMULATION"
    if any(marker in source_text for marker in MARKET_DEMO_MARKERS):
        return "MARKET_DEMO"
    return "UNCLASSIFIED"


def _build_summary(
    *,
    real_entries: Sequence[Mapping[str, Any]],
    market_entries: Sequence[Mapping[str, Any]],
    synthetic_entries: Sequence[Mapping[str, Any]],
    unclassified_entries: Sequence[Mapping[str, Any]],
    today: date,
) -> dict[str, Any]:
    market_trades = sum(_non_negative_int(entry.get("fills")) for entry in market_entries)
    synthetic_trades = sum(_non_negative_int(entry.get("fills")) for entry in synthetic_entries)
    unclassified_trades = sum(
        _non_negative_int(entry.get("fills")) for entry in unclassified_entries
    )

    market_days = sorted(
        {
            parsed
            for parsed in (_parse_date(entry.get("date")) for entry in market_entries)
            if parsed is not None
        }
    )
    latest_date = market_days[-1] if market_days else None
    age_days = (today - latest_date).days if latest_date else None

    market_windows = max(
        (_non_negative_int(entry.get("windows_toward_verdict")) for entry in market_entries),
        default=0,
    )

    trade_values: list[float] = []
    for entry in market_entries:
        rows = entry.get("trade_rows")
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, Mapping):
                    continue
                value = _as_float(
                    row.get("realized_pnl_usd", row.get("realized_paper_pl"))
                )
                if value is not None:
                    trade_values.append(value)

    metric_blockers: list[str] = []
    if len(trade_values) != market_trades:
        metric_blockers.append(
            f"trade_level_pnl_rows_incomplete:{len(trade_values)} != {market_trades}"
        )

    expectancy: float | None = None
    profit_factor: float | None = None
    if market_trades > 0 and len(trade_values) == market_trades:
        expectancy = round(sum(trade_values) / market_trades, 10)
        gross_profit = sum(value for value in trade_values if value > 0)
        gross_loss = abs(sum(value for value in trade_values if value < 0))
        if gross_loss > 0:
            profit_factor = round(gross_profit / gross_loss, 10)
        elif gross_profit > 0:
            profit_factor = 999.0
        else:
            profit_factor = 0.0

    drawdown_values = [
        value
        for value in (_as_float(entry.get("max_drawdown_pct")) for entry in market_entries)
        if value is not None
    ]
    max_drawdown = max(drawdown_values) if drawdown_values else None
    if max_drawdown is None:
        metric_blockers.append("max_drawdown_pct_missing")

    return {
        "real_demo_day_records": len(real_entries),
        "market_demo_records": len(market_entries),
        "fixture_or_simulation_records": len(synthetic_entries),
        "unclassified_records": len(unclassified_entries),
        "engineering_trades": market_trades + synthetic_trades + unclassified_trades,
        "market_demo_trades": market_trades,
        "fixture_or_simulation_trades": synthetic_trades,
        "unclassified_trades": unclassified_trades,
        "market_demo_days": len(market_days),
        "market_demo_windows": market_windows,
        "latest_market_evidence_date": latest_date.isoformat() if latest_date else None,
        "latest_market_evidence_age_days": age_days,
        "evidence_age_ok": age_days is not None and 0 <= age_days <= MAX_EVIDENCE_AGE_DAYS,
        "expectancy_per_trade": expectancy,
        "profit_factor": profit_factor,
        "max_drawdown_pct": max_drawdown,
        "metrics_complete": not metric_blockers,
        "metric_blockers": metric_blockers,
    }


def _safety_blockers(entries: Sequence[Mapping[str, Any]]) -> list[str]:
    blockers: list[str] = []
    for index, entry in enumerate(entries, start=1):
        for field in SAFETY_FALSE_FIELDS:
            if entry.get(field) is True:
                blockers.append(f"market_entry_{index}_{field}_true")
    return blockers


def _tier_passes(tier: Tier, summary: Mapping[str, Any]) -> bool:
    return not _tier_blockers(tier, summary)


def _tier_blockers(tier: Tier, summary: Mapping[str, Any]) -> list[str]:
    blockers: list[str] = []
    trades = int(summary.get("market_demo_trades") or 0)
    days = int(summary.get("market_demo_days") or 0)
    windows = int(summary.get("market_demo_windows") or 0)
    expectancy = _as_float(summary.get("expectancy_per_trade"))
    profit_factor = _as_float(summary.get("profit_factor"))
    drawdown = _as_float(summary.get("max_drawdown_pct"))

    if trades < tier.minimum_market_trades:
        blockers.append(
            f"market_demo_trades_below_{tier.name.lower()}:{trades} < {tier.minimum_market_trades}"
        )
    if days < tier.minimum_days:
        blockers.append(f"market_demo_days_below_{tier.name.lower()}:{days} < {tier.minimum_days}")
    if windows < tier.minimum_windows:
        blockers.append(
            f"market_demo_windows_below_{tier.name.lower()}:{windows} < {tier.minimum_windows}"
        )
    if expectancy is None or expectancy <= tier.minimum_expectancy:
        blockers.append(
            f"expectancy_not_above_{tier.minimum_expectancy}:{expectancy}"
        )
    if profit_factor is None or profit_factor < tier.minimum_profit_factor:
        blockers.append(
            f"profit_factor_below_{tier.minimum_profit_factor}:{profit_factor}"
        )
    if drawdown is None or drawdown > tier.maximum_drawdown_pct:
        blockers.append(
            f"max_drawdown_above_{tier.maximum_drawdown_pct}:{drawdown}"
        )
    return blockers


def _result(
    *,
    status: str,
    blockers: list[str],
    summary: Mapping[str, Any],
    next_tier: Tier,
    achieved_tier: Tier | None = None,
) -> dict[str, Any]:
    next_blockers = _tier_blockers(next_tier, summary) if summary.get("metrics_complete") else []
    return {
        "schema": SCHEMA,
        "mode": MODE,
        "status": status,
        "passed": achieved_tier is not None,
        "achieved_tier": achieved_tier.name if achieved_tier else "NONE",
        "next_target_tier": next_tier.name,
        "blockers": list(blockers),
        "next_target_blockers": next_blockers,
        "summary": dict(summary),
        "tier_thresholds": [
            {
                "name": tier.name,
                "minimum_market_trades": tier.minimum_market_trades,
                "minimum_days": tier.minimum_days,
                "minimum_windows": tier.minimum_windows,
                "minimum_expectancy": tier.minimum_expectancy,
                "minimum_profit_factor": tier.minimum_profit_factor,
                "maximum_drawdown_pct": tier.maximum_drawdown_pct,
            }
            for tier in TIERS
        ],
        "safety": {
            "read_only": True,
            "broker_calls_performed": False,
            "credential_access_performed": False,
            "orders_placed": False,
            "money_movement_performed": False,
            "automatic_order_execution_allowed": False,
            "live_trading_allowed": False,
            "owner_review_required_before_any_live_step": True,
        },
        "next_safe_action": _next_safe_action(status, next_tier),
    }


def _next_safe_action(status: str, next_tier: Tier) -> str:
    if status == BLOCKED_LEDGER_MISSING:
        return "Restore the governed demo evidence ledger, then rerun this read-only audit."
    if status == BLOCKED_LEDGER_INVALID:
        return "Repair the invalid JSONL evidence record without fabricating evidence."
    if status == BLOCKED_NO_MARKET_DEMO_EVIDENCE:
        return (
            "Collect fresh owner-supervised OANDA practice evidence; fixture and simulation trades "
            "do not count toward the market-demo trust tiers."
        )
    if status == BLOCKED_SAFETY_VIOLATION:
        return "Stop the campaign and investigate the safety violation before collecting more evidence."
    if status == BLOCKED_STALE_EVIDENCE:
        return "Collect fresh market-demo evidence; the latest accepted evidence is stale."
    if status == BLOCKED_METRICS_INCOMPLETE:
        return "Capture complete trade-level PnL and drawdown evidence for every accepted market-demo trade."
    if status == PRODUCTION_CANDIDATE_READY_FOR_OWNER_REVIEW:
        return (
            "Prepare an owner review packet. Keep live trading blocked until separate broker-verified "
            "micro-live approval and post-trade review."
        )
    return (
        f"Continue the governed market-demo campaign toward {next_tier.name}; "
        "do not fabricate, duplicate, or backdate evidence."
    )


def _empty_summary() -> dict[str, Any]:
    return {
        "real_demo_day_records": 0,
        "market_demo_records": 0,
        "fixture_or_simulation_records": 0,
        "unclassified_records": 0,
        "engineering_trades": 0,
        "market_demo_trades": 0,
        "fixture_or_simulation_trades": 0,
        "unclassified_trades": 0,
        "market_demo_days": 0,
        "market_demo_windows": 0,
        "latest_market_evidence_date": None,
        "latest_market_evidence_age_days": None,
        "evidence_age_ok": False,
        "expectancy_per_trade": None,
        "profit_factor": None,
        "max_drawdown_pct": None,
        "metrics_complete": False,
        "metric_blockers": ["no_market_demo_metrics"],
    }


def _parse_date(value: Any) -> date | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        return None


def _non_negative_int(value: Any) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError):
        return 0
    return max(0, parsed)


def _as_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", default=".")
    parser.add_argument(
        "--ledger",
        default="telemetry/forex/demo_proof_ledger.jsonl",
    )
    args = parser.parse_args(argv)
    ledger = Path(args.repo_root) / args.ledger
    result = evaluate_extended_evidence_campaign(ledger)
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
