"""Failure regime analysis for deterministic walk-forward Packet R output."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from automation.forex_engine import walk_forward_depth_r_v1 as walk_forward_packet

MODE = "FOREX_FAILURE_REGIME_ANALYSIS_S_V1"
PACKET_ID = "AIOS_FOREX_FAILURE_REGIME_ANALYSIS_PACKET_S_V1"
REPORTS_DIR = Path("Reports/forex_delivery")
REPORT_PACKET = "AIOS_FOREX_FAILURE_REGIME_ANALYSIS_PACKET_S_V1_REPORT.md"
REPORT_SCOREBOARD = "AIOS_FOREX_C1_EUR_BUY_FAILURE_REGIME_SCOREBOARD_V1.md"
REPORT_MATRIX = "AIOS_FOREX_WALK_FORWARD_FAILURE_ROOT_CAUSE_MATRIX_V1.md"

ANCHOR_CANDIDATE_ID = "c1-eur-buy"
ANCHOR_STRATEGY_ID = "paper_long_run_supervisor_v2"


def _safety() -> dict[str, bool]:
    return {
        "paper_only": True,
        "broker_connected": False,
        "credentials_used": False,
        "network_used": False,
        "account_id_present": False,
        "order_execution": False,
        "demo_trading": False,
        "live_trading": False,
    }


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return default
    return parsed if parsed == parsed else default


def identify_root_causes(windows: list[dict[str, Any]]) -> dict[str, list[str]]:
    """Return row-level root causes keyed by window id."""
    causes: dict[str, list[str]] = {}
    for window in windows:
        row_id = str(window["window_id"])
        window_causes: list[str] = []
        if _safe_float(window.get("expectancy"), 0.0) <= 0.0:
            window_causes.append("expectancy")
        if _safe_float(window.get("profit_factor"), 0.0) < 1.25:
            window_causes.append("profit_factor")
        if _safe_float(window.get("max_drawdown"), 0.0) > 10.0:
            window_causes.append("drawdown")
        if _safe_float(window.get("win_rate"), 0.0) < 0.5:
            window_causes.append("win_rate")
        if int(window.get("consecutive_losses", 0)) >= 2:
            window_causes.append("consecutive_loss_profile")

        trade_pnls = window.get("trade_pnl_list")
        if isinstance(trade_pnls, list) and trade_pnls:
            abs_sum = sum(abs(_safe_float(item, 0.0)) for item in trade_pnls)
            if abs_sum > 0 and max(abs(_safe_float(item, 0.0)) for item in trade_pnls) / abs_sum >= 0.45:
                window_causes.append("trade_concentration")
        elif window_causes:
            window_causes.append("trade_concentration")

        if window_causes and not window.get("blocker_reasons") and not window.get("blocked"):
            window_causes = []
        causes[row_id] = window_causes
    return causes


def analyze_failure_regimes(payload: dict[str, Any] | None = None) -> dict[str, Any]:
    if payload is None:
        packet = walk_forward_packet.run_walk_forward_depth(write_reports=False)
    else:
        packet = dict(payload)

    scored_windows = list(packet.get("scored_windows", []))
    windows = packet.get("windows", [])
    trade_map = {str(window["window_id"]): window.get("trade_pnl_list", []) for window in windows if isinstance(window, dict)}

    enriched: list[dict[str, Any]] = []
    for row in scored_windows:
        row = dict(row)
        row["trade_pnl_list"] = list(trade_map.get(str(row["window_id"]), []))
        enriched.append(row)

    return {
        "mode": MODE,
        "packet_id": PACKET_ID,
        "walk_forward_packet_id": packet.get("packet_id", ""),
        "windows": enriched,
        "stability": packet.get("stability_scoreboard", {}),
        "best_candidate": packet.get("best_candidate", {}),
        "safety": _safety(),
    }


def classify_failure_patterns(
    scored_windows: list[dict[str, Any]],
    root_causes: dict[str, list[str]],
    *,
    failing_gate: str = "blocked",
) -> dict[str, Any]:
    failing_windows: list[str] = []
    for row in scored_windows:
        is_failing = row.get("blocked") if failing_gate == "blocked" else False
        if is_failing:
            failing_windows.append(row["window_id"])
        elif root_causes.get(str(row["window_id"])):
            failing_windows.append(row["window_id"])
    passing_windows = [row["window_id"] for row in scored_windows if row["window_id"] not in failing_windows]

    frequency: dict[str, int] = {}
    for row_id in failing_windows:
        for reason in root_causes.get(row_id, []):
            frequency[reason] = frequency.get(reason, 0) + 1

    systemic_failures = [reason for reason, count in sorted(frequency.items()) if count >= 2]
    isolated_failures = [reason for reason, count in sorted(frequency.items()) if count == 1]

    return {
        "failing_windows": failing_windows,
        "passing_windows": passing_windows,
        "root_causes": root_causes,
        "systemic_failures": systemic_failures,
        "isolated_failures": isolated_failures,
    }


def build_failure_matrix(analyzed: dict[str, Any], classification: dict[str, Any]) -> dict[str, Any]:
    return {
        "windows": [
            {
                "window_id": row["window_id"],
                "candidate_id": row["candidate_id"],
                "closed_trade_count": row["closed_trade_count"],
                "expectancy": row["expectancy"],
                "profit_factor": row["profit_factor"],
                "max_drawdown": row["max_drawdown"],
                "win_rate": row["win_rate"],
                "consecutive_losses": row["consecutive_losses"],
                "root_causes": classification["root_causes"].get(row["window_id"], []),
                "blocked": bool(row.get("blocked")),
            }
            for row in sorted(analyzed["windows"], key=lambda item: item["window_id"])
        ],
        "systemic_failures": classification["systemic_failures"],
        "isolated_failures": classification["isolated_failures"],
        "failing_windows": classification["failing_windows"],
        "passing_windows": classification["passing_windows"],
    }


def determine_candidate_verdict(
    classified: dict[str, Any],
    analyzed: dict[str, Any],
) -> tuple[str, int]:
    failing_count = len(classified["failing_windows"])
    total_count = len(analyzed["windows"])
    if total_count == 0:
        return "REQUIRE_MORE_EVIDENCE", 0

    if failing_count == 0:
        return "CONTINUE", 90

    pass_ratio = (total_count - failing_count) / total_count
    root_causes = set(classified["systemic_failures"])
    if failing_count == total_count:
        if root_causes.issuperset({"drawdown"}) or len(root_causes) >= 3:
            return "REJECT", 20
        return "REQUIRE_OPTIMIZATION", 55

    confidence = int(round((pass_ratio * 100) - (len(root_causes) * 10), 0))
    if "drawdown" in root_causes:
        confidence -= 15
    if confidence < 0:
        confidence = 0
    return ("REQUIRE_OPTIMIZATION", confidence)


def build_failure_scoreboard(
    analyzed: dict[str, Any],
    classified: dict[str, Any],
    verdict: str,
    confidence: int,
) -> dict[str, Any]:
    best_candidate = analyzed.get("best_candidate", {})
    best_is_anchor = best_candidate.get("candidate_id") == ANCHOR_CANDIDATE_ID

    return {
        "candidate_id": ANCHOR_CANDIDATE_ID,
        "strategy_id": ANCHOR_STRATEGY_ID,
        "windows_analyzed": len(analyzed["windows"]),
        "failing_windows": classified["failing_windows"],
        "passing_windows": classified["passing_windows"],
        "root_causes": classified["root_causes"],
        "systemic_failures": classified["systemic_failures"],
        "isolated_failures": classified["isolated_failures"],
        "verdict": verdict,
        "confidence_score": confidence,
        "best_candidate_still_viable": best_is_anchor and verdict in {"CONTINUE", "REQUIRE_OPTIMIZATION", "REQUIRE_MORE_EVIDENCE"},
        "best_candidate": best_candidate,
        "safety": _safety(),
    }


def run_failure_regime_analysis(*, write_reports: bool = True) -> dict[str, Any]:
    analyzed = analyze_failure_regimes()
    root_causes = identify_root_causes(analyzed["windows"])
    classified = classify_failure_patterns(analyzed["windows"], root_causes)
    verdict, confidence = determine_candidate_verdict(classified, analyzed)
    scoreboard = build_failure_scoreboard(analyzed, classified, verdict, confidence)
    matrix = build_failure_matrix(analyzed, classified)
    result = {
        "mode": MODE,
        "packet_id": PACKET_ID,
        "walk_forward_packet_id": analyzed["walk_forward_packet_id"],
        "safety": _safety(),
        "analyzed_windows": analyzed["windows"],
        "failure_summary": classified,
        "verdict": verdict,
        "confidence_score": confidence,
        "failure_scoreboard": scoreboard,
        "failure_matrix": matrix,
        "c1_eur_buy_best_candidate": analyzed.get("best_candidate", {}),
        "walk_forward_stability": analyzed.get("stability", {}),
    }
    if write_reports:
        result["report_paths"] = write_reports(result)
    return result


def write_reports(payload: dict[str, Any]) -> dict[str, Path]:
    report_dir = Path(REPORTS_DIR)
    report_dir.mkdir(parents=True, exist_ok=True)
    packet_path = report_dir / REPORT_PACKET
    scoreboard_path = report_dir / REPORT_SCOREBOARD
    matrix_path = report_dir / REPORT_MATRIX
    packet_path.write_text(_build_packet_report(payload), encoding="utf-8")
    scoreboard_path.write_text(_build_scoreboard_report(payload), encoding="utf-8")
    matrix_path.write_text(_build_matrix_report(payload), encoding="utf-8")
    return {
        "packet": packet_path,
        "scoreboard": scoreboard_path,
        "matrix": matrix_path,
    }


def _build_packet_report(payload: dict[str, Any]) -> str:
    scoreboard = payload["failure_scoreboard"]
    stability = payload["walk_forward_stability"]
    return f"""# AIOS Forex Failure-Regime Packet S V1

## Paper-only scope
- paper_only: True
- no broker connectivity
- no credentials
- no account IDs
- no network
- no order execution
- no demo trading
- no live trading

## Candidate under review
- candidate: `{scoreboard['candidate_id']}`
- strategy: `{scoreboard['strategy_id']}`
- verdict: `{payload['verdict']}`
- confidence_score: `{payload['confidence_score']}`
- best candidate viable: `{scoreboard['best_candidate_still_viable']}`

## Failure summary
- failing windows: `{', '.join(scoreboard['failing_windows']) or 'none'}`
- passing windows: `{', '.join(scoreboard['passing_windows']) or 'none'}`
- walk-forward windows: `{stability.get('total_windows', 0)}`
- walk-forward gate: `{stability.get('walk_forward_gate_cleared', False)}`
- root causes: `{scoreboard['root_causes']}`
"""


def _build_scoreboard_report(payload: dict[str, Any]) -> str:
    scoreboard = payload["failure_scoreboard"]
    return f"""# AIOS Forex C1 EUR BUY Failure Regime Scoreboard V1

## Candidate status
- verdict: `{scoreboard['verdict']}`
- confidence: `{scoreboard['confidence_score']}`
- candidate remains best: `{scoreboard['best_candidate_still_viable']}`

## Regime findings
- failing_windows: `{', '.join(scoreboard['failing_windows']) or 'none'}`
- passing_windows: `{', '.join(scoreboard['passing_windows']) or 'none'}`
- systemic_failures: `{', '.join(scoreboard['systemic_failures']) or 'none'}`
- isolated_failures: `{', '.join(scoreboard['isolated_failures']) or 'none'}`
- optimization_recommendation: `optimize expectancy and profit factor thresholds before retry`
"""


def _build_matrix_report(payload: dict[str, Any]) -> str:
    matrix = payload["failure_matrix"]
    return f"""# AIOS Forex Walk Forward Failure Root Cause Matrix V1

## Matrix
| window | candidate | trades | expectancy | profit factor | drawdown | win rate | consecutive losses | root causes | blocked |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
""" + "\n".join(
        f"| {row['window_id']} | {row['candidate_id']} | {row['closed_trade_count']} | {row['expectancy']:.2f} | "
        f"{row['profit_factor']:.2f} | {row['max_drawdown']:.2f} | {row['win_rate']:.2f} | {row['consecutive_losses']} | "
        f"{', '.join(row['root_causes']) or 'none'} | {row['blocked']} |"
        for row in matrix["windows"]
    ) + f"\n\n## Failure pattern\n- systemic_failures: `{', '.join(matrix['systemic_failures']) or 'none'}`\n- isolated_failures: `{', '.join(matrix['isolated_failures']) or 'none'}`"


__all__ = [
    "analyze_failure_regimes",
    "identify_root_causes",
    "classify_failure_patterns",
    "determine_candidate_verdict",
    "build_failure_scoreboard",
    "build_failure_matrix",
    "run_failure_regime_analysis",
]
