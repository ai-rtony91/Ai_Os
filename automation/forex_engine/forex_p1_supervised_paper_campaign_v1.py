"""Bounded, sequential campaign adapter for canonical P1 paper evidence.

This module does not trade and does not fetch market data.  It accepts completed,
sanitized paper-trade candidates emitted by the existing long-run paper supervisor
and passes them, one at a time, through the canonical capture/replay boundary.
"""

from __future__ import annotations

import json
import math
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TextIO

from automation.forex_engine.forex_p1_supervised_paper_capture_replay_v1 import (
    run_capture_replay,
)
from automation.forex_engine.forex_profit_track_p1_strategy_evidence_v1 import (
    evaluate_strategy_evidence,
)
from automation.forex_engine.long_run_paper_supervisor import LONG_RUN_PAPER_MODE

VERSION = "forex_p1_supervised_paper_campaign_v1"
TARGET_QUALIFYING_TRADES = 30
MAX_OPEN_PAPER_POSITIONS = 1
PAPER_MODE = LONG_RUN_PAPER_MODE
LONG_RUN_LIMITS = {"max_session_trades": TARGET_QUALIFYING_TRADES}

SAFETY_FLAGS = {
    "broker_write_performed": False,
    "practice_order_performed": False,
    "live_trade_performed": False,
    "money_movement_performed": False,
    "credentials_persisted": False,
}


@dataclass(frozen=True)
class CampaignPaths:
    candidate: Path
    ledger: Path
    replay_state: Path
    replay_report: Path
    event_log: Path
    campaign_state: Path
    campaign_report: Path


@dataclass(frozen=True)
class CampaignHalt:
    """Fail-closed stop emitted by the canonical upstream paper supervisor."""

    reason: str


@dataclass(frozen=True)
class CampaignWait:
    """A bounded market cycle that produced no evidence and must continue."""

    cycle_number: int
    maximum_cycles: int


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_records(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    records = payload.get("records", []) if isinstance(payload, Mapping) else []
    return list(records) if isinstance(records, list) else []


def _metrics(records: list[Mapping[str, Any]]) -> dict[str, Any]:
    pnl = [float(record["realized_pl"]) for record in records]
    gross_profit = round(sum(value for value in pnl if value > 0), 8)
    gross_loss = round(abs(sum(value for value in pnl if value < 0)), 8)
    net_pl = round(sum(pnl), 8)
    profit_factor: float | str | None
    if gross_loss:
        profit_factor = round(gross_profit / gross_loss, 8)
    else:
        profit_factor = "INFINITE" if gross_profit else None
    equity = peak = maximum_drawdown = 0.0
    current_streak = maximum_streak = 0
    for value in pnl:
        equity += value
        peak = max(peak, equity)
        maximum_drawdown = max(maximum_drawdown, peak - equity)
        current_streak = current_streak + 1 if value < 0 else 0
        maximum_streak = max(maximum_streak, current_streak)
    return {
        "net_pl": net_pl,
        "gross_profit": gross_profit,
        "gross_loss": gross_loss,
        "profit_factor": profit_factor,
        "maximum_drawdown": round(maximum_drawdown, 8),
        "consecutive_losses": maximum_streak,
        "expectancy": round(net_pl / len(pnl), 8) if pnl else 0.0,
    }


def _p1_status(records: list[Mapping[str, Any]]) -> str:
    evaluation = evaluate_strategy_evidence([
        {
            "trade_id": record["trade_id"],
            "entry": record["entry_price"],
            "exit": record["exit_price"],
            "realized_pl": record["realized_pl"],
            "timestamp": record["exit_timestamp_utc"],
            "evidence_type": record["evidence_type"],
        }
        for record in records
    ])
    return str(evaluation["strategy_evidence_status"])


def _initial_state(started_utc: str) -> dict[str, Any]:
    return {
        "campaign_version": VERSION,
        "campaign_status": "RUNNING",
        "stop_reason": None,
        "target_qualifying_trades": TARGET_QUALIFYING_TRADES,
        "accepted_qualifying_trades": 0,
        "rejected_records": 0,
        "current_trade_number": 0,
        "active_position": None,
        "last_trade": None,
        "trade_results": [],
        **_metrics([]),
        "p1_status": "NO_EVIDENCE",
        "ready_for_p2_review": False,
        "started_utc": started_utc,
        "updated_utc": started_utc,
        "completed_utc": None,
        **SAFETY_FLAGS,
    }


def _write_outputs(paths: CampaignPaths, state: Mapping[str, Any]) -> None:
    paths.campaign_state.parent.mkdir(parents=True, exist_ok=True)
    paths.campaign_state.write_text(
        json.dumps(state, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    results = state["trade_results"]
    pnl_lines = [
        f"- {item['trade_id']}: {item['realized_paper_pl']} PAPER P/L"
        for item in results
    ] or ["- NONE"]
    report = [
        "# AIOS Forex P1 30-Trade Paper Campaign V1", "",
        f"- TARGET: {state['target_qualifying_trades']}",
        f"- ACCEPTED: {state['accepted_qualifying_trades']}",
        f"- REJECTED: {state['rejected_records']}",
        f"- CUMULATIVE_PAPER_PNL: {state['net_pl']}",
        f"- PROFIT_FACTOR: {state['profit_factor']}",
        f"- DRAWDOWN: {state['maximum_drawdown']}",
        f"- LOSS_STREAK: {state['consecutive_losses']}",
        f"- EXPECTANCY: {state['expectancy']}",
        f"- P1_STATUS: {state['p1_status']}",
        f"- STOP_REASON: {state['stop_reason']}",
        "- NEXT_ACTION: Supply a fresh legitimate paper signal in a new owner-started campaign." if state["stop_reason"] != "TARGET_REACHED" else "- NEXT_ACTION: Human owner may review P1 evidence; no promotion is automatic.",
        "", "## PAPER_PNL_BY_TRADE", "", *pnl_lines, "",
        "All results are local PAPER P/L. No broker order, live trade, or money movement occurred.", "",
    ]
    paths.campaign_report.write_text("\n".join(report), encoding="utf-8")


def _progress(state: Mapping[str, Any], stream: TextIO) -> None:
    last = state["last_trade"]
    stream.write(
        f"TRADE: {state['accepted_qualifying_trades']}/30\n"
        f"REALIZED PAPER P/L: {last['realized_paper_pl']}\n"
        f"CUMULATIVE PAPER P/L: {state['net_pl']}\n"
        f"PROFIT FACTOR: {state['profit_factor']}\n"
        f"MAX DRAWDOWN: {state['maximum_drawdown']}\n"
        f"LOSS STREAK: {state['consecutive_losses']}\n"
        f"QUALIFYING: {state['accepted_qualifying_trades']}/30\n"
        f"P1 STATUS: {state['p1_status']}\n"
    )


def _wait_progress(wait: CampaignWait, state: Mapping[str, Any], stream: TextIO) -> None:
    stream.write(
        f"CYCLE: {wait.cycle_number}/{wait.maximum_cycles}\n"
        "SIGNAL: NONE\n"
        "ACTION: WAIT_FOR_NEXT_CYCLE\n"
        f"QUALIFYING: {state['accepted_qualifying_trades']}/30\n"
        f"CUMULATIVE PAPER P/L: {state['net_pl']}\n"
        f"P1 STATUS: {state['p1_status']}\n"
    )


def run_campaign(
    candidates: Iterable[Mapping[str, Any]],
    paths: CampaignPaths,
    *,
    repository_root: Path,
    output: TextIO,
    kill_switch_active: bool = False,
    risk_halt_active: bool = False,
    maximum_session_loss: float | None = None,
) -> dict[str, Any]:
    """Capture up to 30 already-closed paper candidates, sequentially and fail closed."""
    started = _utc_now()
    state = _initial_state(started)
    stop_reason: str | None = None
    seen_this_run: set[str] = set()

    if kill_switch_active:
        stop_reason = "KILL_SWITCH_ACTIVE"
    elif risk_halt_active:
        stop_reason = "RISK_HALT"

    iterator = iter(candidates)
    while stop_reason is None:
        prior = _load_records(paths.ledger)
        if len(prior) >= TARGET_QUALIFYING_TRADES:
            stop_reason = "TARGET_REACHED"
            break
        try:
            candidate = next(iterator)
        except StopIteration:
            stop_reason = "WAITING_FOR_VALID_SIGNAL"
            break
        if isinstance(candidate, CampaignHalt):
            stop_reason = candidate.reason
            break
        if isinstance(candidate, CampaignWait):
            records = _load_records(paths.ledger)
            state.update(_metrics(records))
            state["accepted_qualifying_trades"] = len(records)
            state["p1_status"] = _p1_status(records)
            state["updated_utc"] = _utc_now()
            _write_outputs(paths, state)
            _wait_progress(candidate, state, output)
            continue
        if not isinstance(candidate, Mapping):
            stop_reason = "MALFORMED_EVIDENCE_REJECTED"
            state["rejected_records"] += 1
            break
        trade_id = str(candidate.get("trade_id", "")).strip()
        if trade_id and trade_id in seen_this_run:
            stop_reason = "DUPLICATE_TRADE_ID_REJECTED"
            state["rejected_records"] += 1
            break
        realized = candidate.get("realized_pl")
        try:
            finite_realized = float(realized)
        except (TypeError, ValueError):
            finite_realized = float("nan")
        if not math.isfinite(finite_realized):
            stop_reason = "MALFORMED_EVIDENCE_REJECTED"
            state["rejected_records"] += 1
            break

        # The candidate represents an already-closed paper trade. It is the only
        # item inside the canonical one-candidate capture/replay boundary.
        state["active_position"] = {"trade_id": trade_id or "pending-deterministic-id"}
        paths.candidate.parent.mkdir(parents=True, exist_ok=True)
        paths.candidate.write_text(json.dumps(dict(candidate), allow_nan=False), encoding="utf-8")
        replay = run_capture_replay(
            paths.candidate, paths.ledger, paths.replay_state, paths.replay_report,
            paths.event_log, repository_root=repository_root,
        )
        state["active_position"] = None
        state["rejected_records"] += replay["rejected_records"]
        if replay["accepted_records"] != 1:
            reasons = {reason for item in replay["rejections"] for reason in item["reasons"]}
            stop_reason = "DUPLICATE_TRADE_ID_REJECTED" if "duplicate_trade_id" in reasons else "EVIDENCE_VALIDATION_FAILED"
            break

        records = _load_records(paths.ledger)
        accepted = records[-1]
        seen_this_run.add(str(accepted["trade_id"]))
        metrics = _metrics(records)
        result = {
            "trade_number": len(records),
            "trade_id": accepted["trade_id"],
            "entry": accepted["entry_price"],
            "exit": accepted["exit_price"],
            "realized_paper_pl": accepted["realized_pl"],
            "cumulative_paper_pl": metrics["net_pl"],
            "win_or_loss": "WIN" if accepted["realized_pl"] > 0 else ("LOSS" if accepted["realized_pl"] < 0 else "FLAT"),
        }
        state.update(metrics)
        state.update({
            "accepted_qualifying_trades": replay["qualifying_trade_count"],
            "current_trade_number": len(records),
            "last_trade": result,
            "trade_results": [*state["trade_results"], result],
            "p1_status": replay["p1_status_after"],
            "ready_for_p2_review": replay["ready_for_p2_review"],
            "updated_utc": _utc_now(),
        })
        _write_outputs(paths, state)
        _progress(state, output)
        if maximum_session_loss is not None and state["net_pl"] <= -abs(maximum_session_loss):
            stop_reason = "MAXIMUM_SESSION_LOSS_HIT"

    state["campaign_status"] = "COMPLETE" if stop_reason == "TARGET_REACHED" else "STOPPED"
    state["stop_reason"] = stop_reason
    state["updated_utc"] = _utc_now()
    state["completed_utc"] = state["updated_utc"]
    state["active_position"] = None
    _write_outputs(paths, state)
    paths.candidate.unlink(missing_ok=True)
    return state
