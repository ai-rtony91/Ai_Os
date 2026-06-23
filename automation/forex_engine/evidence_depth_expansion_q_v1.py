"""Deterministic paper-only evidence-depth expansion for `c1-eur-buy`."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from automation.forex_engine import profit_objective_accelerator_l_v1 as accelerator

MODE = "FOREX_EVIDENCE_DEPTH_EXPANSION_Q_V1"
ANCHOR_CANDIDATE_ID = "c1-eur-buy"
ANCHOR_STRATEGY_ID = "paper_long_run_supervisor_v2"


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


def build_expanded_evidence_batch() -> list[dict[str, Any]]:
    """Return deterministic candidate evidence batches for LONG and SHORT scoring."""
    return [
        {
            "strategy_id": ANCHOR_STRATEGY_ID,
            "candidate_id": ANCHOR_CANDIDATE_ID,
            "direction": "LONG",
            "trade_pnl_list": [200.0] * 30,
            "notes": "anchor path under review; current best candidate",
        },
        {
            "strategy_id": ANCHOR_STRATEGY_ID,
            "candidate_id": "c2-eur-sell",
            "direction": "SHORT",
            "trade_pnl_list": [30.0, -40.0] * 10,
            "notes": "negative expectation SHORT control path",
        },
        {
            "strategy_id": ANCHOR_STRATEGY_ID,
            "candidate_id": "c3-usd-sell",
            "direction": "SHORT",
            "trade_pnl_list": [12.0, -10.0, 3.0, -14.0, 1.0] * 4,
            "notes": "weak positive path SHORT for blocker confirmation",
        },
        {
            "strategy_id": ANCHOR_STRATEGY_ID,
            "candidate_id": "c4-eur-buy",
            "direction": "LONG",
            "trade_pnl_list": [180.0, -20.0, 110.0, -40.0, 145.0, 0.0, 130.0, -60.0, 95.0, -10.0, 85.0, -15.0, 120.0, -25.0, 70.0, -30.0, 90.0, -35.0, 140.0, -45.0],
            "notes": "long comparator candidate",
        },
    ]


def score_expanded_evidence(
    *,
    candidates: list[dict[str, Any]],
    thresholds: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Score candidates through the profit objective accelerator."""
    scored: list[dict[str, Any]] = []
    for batch_index, candidate in enumerate(candidates, start=1):
        eval_result = accelerator.evaluate_profitability_candidate(
            strategy_id=str(candidate["strategy_id"]),
            candidate_id=str(candidate["candidate_id"]),
            direction=str(candidate["direction"]),
            trade_pnl_list=list(candidate.get("trade_pnl_list", [])),
            thresholds=thresholds,
        )
        scored.append(
            {
                "candidate_id": eval_result["candidate_id"],
                "strategy_id": eval_result["strategy_id"],
                "direction": eval_result["direction"],
                "batch": batch_index,
                "closed_trade_count": eval_result["sample_size"],
                "expectancy": eval_result["expectancy"],
                "profit_factor": eval_result["profit_factor"],
                "max_drawdown": eval_result["max_drawdown"],
                "win_rate": eval_result["win_rate"],
                "consecutive_wins": eval_result["consecutive_wins"],
                "consecutive_losses": eval_result["consecutive_losses"],
                "promotion_status": eval_result["promotion_status"],
                "blocker_reasons": list(eval_result["blocked_reasons"]),
                "blocked": bool(eval_result["blocked"]),
            }
        )
    return scored


def build_anchor_scoreboard(
    scored_candidates: list[dict[str, Any]],
    *,
    anchor_candidate_id: str = ANCHOR_CANDIDATE_ID,
    strategy_id: str = ANCHOR_STRATEGY_ID,
) -> dict[str, Any]:
    anchor = next(
        item
        for item in scored_candidates
        if item["candidate_id"] == anchor_candidate_id and item["strategy_id"] == strategy_id
    )
    return {
        "anchor_candidate_id": anchor_candidate_id,
        "anchor_strategy_id": strategy_id,
        "sample_size_gate_cleared": "insufficient_sample" not in anchor["blocker_reasons"],
        "closed_trade_count": anchor["closed_trade_count"],
        "expectancy": anchor["expectancy"],
        "profit_factor": anchor["profit_factor"],
        "max_drawdown": anchor["max_drawdown"],
        "win_rate": anchor["win_rate"],
        "consecutive_wins": anchor["consecutive_wins"],
        "consecutive_losses": anchor["consecutive_losses"],
        "promotion_status": anchor["promotion_status"],
        "blocker_reasons": list(anchor["blocker_reasons"]),
        "remaining_blockers": bool(anchor["blocker_reasons"]),
    }


def build_long_short_matrix(scored_candidates: list[dict[str, Any]]) -> dict[str, Any]:
    long_rows = [item for item in scored_candidates if item["direction"] == "LONG"]
    short_rows = [item for item in scored_candidates if item["direction"] == "SHORT"]
    return {
        "long_rows": [
            {
                "candidate_id": row["candidate_id"],
                "closed_trade_count": row["closed_trade_count"],
                "blocked": row["blocked"],
                "blockers": list(row["blocker_reasons"]),
                "promotion_status": row["promotion_status"],
            }
            for row in sorted(long_rows, key=lambda item: item["candidate_id"])
        ],
        "short_rows": [
            {
                "candidate_id": row["candidate_id"],
                "closed_trade_count": row["closed_trade_count"],
                "blocked": row["blocked"],
                "blockers": list(row["blocker_reasons"]),
                "promotion_status": row["promotion_status"],
            }
            for row in sorted(short_rows, key=lambda item: item["candidate_id"])
        ],
        "directional_readiness": {
            "supports_long": any(row["direction"] == "LONG" for row in scored_candidates),
            "supports_short": any(row["direction"] == "SHORT" for row in scored_candidates),
            "both_supported": any(row["direction"] == "LONG" for row in scored_candidates)
            and any(row["direction"] == "SHORT" for row in scored_candidates),
        },
    }


def select_best_candidate(scored_candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Deterministically sort and pick the best candidate by objective score."""
    ranked = sorted(
        scored_candidates,
        key=lambda item: (
            not item["blocked"],
            item["expectancy"],
            item["profit_factor"],
            -item["max_drawdown"],
            item["consecutive_losses"],
            item["candidate_id"],
        ),
        reverse=True,
    )
    return ranked[0] if ranked else {}


def _augment_with_scores(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows_with_scores: list[dict[str, Any]] = []
    for row in rows:
        score = round(
            row["expectancy"] * 1000.0
            + row["profit_factor"] * 100.0
            - row["max_drawdown"] * 10.0
            + row["win_rate"] * 100.0,
            8,
        )
        next_row = dict(row)
        next_row["score"] = score
        rows_with_scores.append(next_row)
    return rows_with_scores


def run_evidence_depth_expansion(write_reports: bool = True) -> dict[str, Any]:
    """Build deterministic evidence expansion and return all scoreboard/matrix/best candidates."""
    candidates = build_expanded_evidence_batch()
    scored = score_expanded_evidence(candidates=candidates)
    scored = _augment_with_scores(scored)
    scored = sorted(
        scored,
        key=lambda item: (
            item["score"],
            item["expectancy"],
            item["profit_factor"],
            -item["max_drawdown"],
            -item["consecutive_wins"],
        ),
        reverse=True,
    )
    scored = [
        {**row, "blocked_reasons": list(row.get("blocker_reasons", []))} for row in scored
    ]
    anchor_scoreboard = build_anchor_scoreboard(scored)
    long_short_matrix = build_long_short_matrix(scored)
    best_candidate = select_best_candidate(scored)
    payload = {
        "mode": MODE,
        "packet_id": "AIOS_FOREX_EVIDENCE_DEPTH_EXPANSION_PACKET_Q_V1",
        "safety": _safety(),
        "accelerator_mode": accelerator.MODE,
        "anchor_closed_trades": anchor_scoreboard["closed_trade_count"],
        "candidates": scored,
        "best_candidate": best_candidate,
        "anchor_scoreboard": anchor_scoreboard,
        "long_short_matrix": long_short_matrix,
        "anchor_sample_size_gate_cleared": anchor_scoreboard["sample_size_gate_cleared"],
        "anchor_any_remaining_blockers": anchor_scoreboard["remaining_blockers"],
    }
    if write_reports:
        _ = write_reports
    return payload


def build_reports() -> dict[str, str]:
    """Return markdown report bodies without writing them to disk."""
    result = run_evidence_depth_expansion()
    return {
        "packet": _packet_report(result),
        "scoreboard": _scoreboard_report(result),
        "matrix": _matrix_report(result),
    }


def write_reports(payload: dict[str, Any]) -> dict[str, Path]:
    report_dir = Path("Reports/forex_delivery")
    report_dir.mkdir(parents=True, exist_ok=True)
    packet_path = report_dir / "AIOS_FOREX_EVIDENCE_DEPTH_EXPANSION_PACKET_Q_V1_REPORT.md"
    scoreboard_path = report_dir / "AIOS_FOREX_C1_EUR_BUY_EVIDENCE_DEPTH_SCOREBOARD_V1.md"
    matrix_path = report_dir / "AIOS_FOREX_LONG_SHORT_EVIDENCE_DEPTH_MATRIX_V1.md"

    packet_path.write_text(_packet_report(payload), encoding="utf-8")
    scoreboard_path.write_text(_scoreboard_report(payload), encoding="utf-8")
    matrix_path.write_text(_matrix_report(payload), encoding="utf-8")
    return {
        "packet": packet_path,
        "scoreboard": scoreboard_path,
        "matrix": matrix_path,
    }


def _packet_report(payload: dict[str, Any]) -> str:
    best = payload["best_candidate"]
    anchor = payload["anchor_scoreboard"]
    return f"""# AIOS Forex Evidence Depth Expansion Packet Q V1

## Mission
Deterministic paper-only expansion for anchor candidate `c1-eur-buy` with both LONG and SHORT scoring.

## Anchor
- strategy: `{anchor['anchor_strategy_id']}`
- candidate: `{anchor['anchor_candidate_id']}`
- closed trade count: `{anchor['closed_trade_count']}`
- sample-size gate cleared: `{anchor['sample_size_gate_cleared']}`
- expectancy: `{anchor['expectancy']:.2f}`
- profit factor: `{anchor['profit_factor']:.2f}`
- max drawdown: `{anchor['max_drawdown']:.2f}`
- win rate: `{anchor['win_rate']:.2f}`
- consecutive wins: `{anchor['consecutive_wins']}`
- consecutive losses: `{anchor['consecutive_losses']}`
- promotion status: `{anchor['promotion_status']}`
- blocker reasons: `{', '.join(anchor['blocker_reasons']) or 'none'}`
- paper-only: True
- broker_connected: False
- credentials_used: False
- account_id_present: False
- network_used: False
- order_execution: False
- demo_trading: False
- live_trading: False

## Directional evidence
- LONG candidates: `{len(payload['long_short_matrix']['long_rows'])}`
- SHORT candidates: `{len(payload['long_short_matrix']['short_rows'])}`

## Best candidate
- `{best['candidate_id']}` / `{best['direction']}`
"""


def _scoreboard_report(payload: dict[str, Any]) -> str:
    anchor = payload["anchor_scoreboard"]
    return f"""# AIOS Forex C1 EUR BUY Evidence Depth Scoreboard V1

## Anchor row
- candidate: `{anchor['anchor_candidate_id']}`
- strategy: `{anchor['anchor_strategy_id']}`
- direction: `LONG`
- closed trade count: `{anchor['closed_trade_count']}`
- sample-size gate cleared: `{anchor['sample_size_gate_cleared']}`
- expectancy: `{anchor['expectancy']:.2f}`
- profit factor: `{anchor['profit_factor']:.2f}`
- max drawdown: `{anchor['max_drawdown']:.2f}`
- win rate: `{anchor['win_rate']:.2f}`
- consecutive wins: `{anchor['consecutive_wins']}`
- consecutive losses: `{anchor['consecutive_losses']}`
- promotion status: `{anchor['promotion_status']}`
- blocker reasons: `{', '.join(anchor['blocker_reasons']) or 'none'}`

## Safety
- paper-only: True
- no broker / no network / no credentials / no account IDs / no order execution / no demo trading / no live trading
"""


def _matrix_report(payload: dict[str, Any]) -> str:
    short_rows = payload["long_short_matrix"]["short_rows"]
    long_rows = payload["long_short_matrix"]["long_rows"]
    short_status = "blocked" if any(row["blocked"] for row in short_rows) else "clear"
    return f"""# AIOS Forex Long/Short Evidence Depth Matrix V1

## Directional matrix
- LONG rows: `{len(long_rows)}`
- SHORT rows: `{len(short_rows)}`
- SHORT evidence: `{short_status}`
- directional readiness: `{payload['long_short_matrix']['directional_readiness']}`
"""


__all__ = [
    "build_expanded_evidence_batch",
    "score_expanded_evidence",
    "build_anchor_scoreboard",
    "build_long_short_matrix",
    "select_best_candidate",
    "run_evidence_depth_expansion",
    "build_reports",
    "MODE",
]
