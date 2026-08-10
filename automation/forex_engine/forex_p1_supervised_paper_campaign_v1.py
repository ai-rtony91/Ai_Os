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


@dataclass(frozen=True)
class StaleMarketDataWait:
    """A bounded stale-data cycle that produced no paper activity or evidence."""

    cycle_number: int
    maximum_cycles: int
    stale_streak: int
    maximum_stale_cycles: int


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


def _stale_wait_progress(
    wait: StaleMarketDataWait, state: Mapping[str, Any], stream: TextIO
) -> None:
    stream.write(
        f"CYCLE: {wait.cycle_number}/{wait.maximum_cycles}\n"
        "MARKET_DATA: STALE\n"
        "ACTION: WAIT_FOR_FRESH_MARKET_DATA\n"
        f"STALE_STREAK: {wait.stale_streak}/{wait.maximum_stale_cycles}\n"
        f"QUALIFYING: {state['accepted_qualifying_trades']}/30\n"
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
            stop_reason = "TARGEWФ‘PPТQ‚€њ™XZВ€ћN‚€Ш[™Y]HH™^
]\]ЬЉB€^Щ\ЭЬ]\][ЫЋ‚€ЭЬЬ™X\ЫЫ€H•РRUS‘ЧС“Ф—ХђSQФТQУђS‚€њ™XZВ€Y€\Ъ[њЭ[ЩJШ[™Y]KШ[\ZYЫ’[
N‚€ЭЬЬ™X\ЫЫ€HШ[™Y]Kњ™X\ЫЫ‚€њ™XZВ€Y€\Ъ[њЭ[ЩJШ[™Y]KШ[\ZYЫ•ШZ]
N‚€™XЫЬ™ИHЫШYЬ™XЫЬ™К]Л›YЩ\ЉB€Э]Kќ\]JЫY]љXЬК™XЫЬ™КJB€Э]VИXШЩ\YЬ]X[YћZ[™ЧЭY\И—HH[Љ™XЫЬ™КB€Э]VИњWЬЭ]\И—HHЬWЬЭ]\К™XЫЬ™КB€Э]VИќ\]YЭ]И—HHЭ]ЧЫ›ЭК
B€ЭЬљ]WЫЭ]]К]ЛЭ]JB€ЭШZ]Ь›ЩЬ™\ЬКШ[™Y]KЭ]KЭ]]
B€ЫЫќ[ќYB€Y€\Ъ[њЭ[ЩJШ[™Y]KЭ[SX\љЩ]]UШZ]
N‚€™XЫЬ™ИHЫШYЬ™XЫЬ™К]Л›YЩ\ЉB€Э]Kќ\]JЫY]љXЬК™XЫЬ™КJB€Э]VИXШЩ\YЬ]X[YћZ[™ЧЭY\И—HH[Љ™XЫЬ™КB€Э]VИњWЬЭ]\И—HHЬWЬЭ]\К™XЫЬ™КB€Э]VИќ\]YЭ]И—HHЭ]ЧЫ›ЭК
B€ЭЬљ]WЫЭ]]К]ЛЭ]JB€ЬЭ[WЭШZ]Ь›ЩЬ™\ЬКШ[™Y]KЭ]KЭ]]
B€ЫЫќ[ќYB€Y€›Э\Ъ[њЭ[ЩJШ[™Y]KX\[™КN‚€ЭЬЬ™X\ЫЫ€H“PS“Ф“QQСU’QSђСWФ‘R‘PХQ‚€Э]VИњ™Z™XЭYЬ™XЫЬ™И—H
ПHB€њ™XZВ€YWЪYHЭЉШ[™Y]K™Щ]
ќYWЪY‹€ЉJKњЭљ\

B€Y€YWЪY[™YWЪY[€ЩY[—Э\ЧЬќ[Ћ‚€ЭЬЬ™X\ЫЫ€H‘TPРUWХђQWТQФ‘R‘PХQ‚€Э]VИњ™Z™XЭYЬ™XЫЬ™И—H
ПHB€њ™XZВ€™X[^™YHШ[™Y]K™Щ]
њ™X[^™YЬЉB€ћN‚€љ[љ]WЬ™X[^™YH›Ш]
™X[^™Y
B€^Щ\
\Q\њ›Ь‹[YQ\њ›ЬЉN‚€љ[љ]WЬ™X[^™YH›Ш]
›[€ЉB€Y€›ЭX]љ\Щљ[љ]Jљ[љ]WЬ™X[^™Y
N‚€ЭЬЬ™X\ЫЫ€H“PS“Ф“QQСU’QSђСWФ‘R‘PХQ‚€Э]VИњ™Z™XЭYЬ™XЫЬ™И—H
ПHB€њ™XZВ‚€ИHШ[™Y]H™\™\Щ[ќИ[€[™XYKXЫЬЩY\\€YK€]\ИHЫ›B€И][H[њЪYHHШ[›ЫљXШ[Ы™KXШ[™Y]HШ\\™KЬ™\^H›Э[™\ћK‚€Э]VИXЭ]™WЬЬЪ][Ы€—HHИќYWЪYЋ€YWЪYЬ€њ[™[™ЛY]\›Z[љ\ЭXЛZYџB€]ЛШ[™Y]Kњ\™[ќ›ZЩ\Љ\™[ќПUќYK^\ЭЫЪПUќYJB€]ЛШ[™Y]KќЬљ]WЭ^
њЫЫ‹™[\КXЭ
Ш[™Y]JK[ЭЧЫ[ЏQ[ЩJK[ЫЩ[™ПHќ]‹NЉB€™\^HHќ[—ШШ\\™WЬ™\^J€]ЛШ[™Y]K]Л›YЩ\‹]Лњ™\^WЬЭ]K]Лњ™\^WЬ™\Ьќ€]Л™]™[ќЫЩЛ™\ЬЪ]ЬћWЬ›ЫЭ\™\ЬЪ]ЬћWЬ›ЫЭ€
B€Э]VИXЭ]™WЬЬЪ][Ы€—HH›Ы™B€Э]VИњ™Z™XЭYЬ™XЫЬ™И—H
ПH™\^VИњ™Z™XЭYЬ™XЫЬ™И—B€Y€™\^VИXШЩ\YЬ™XЫЬ™И—HOHN‚€™X\ЫЫњИHЬ™X\ЫЫ€›Ь€][H[€™\^VИњ™Z™XЭ[ЫњИ—H›Ь€™X\ЫЫ€[€][VИњ™X\ЫЫњИ—_B€ЭЬЬ™X\ЫЫ€H‘TPРUWХђQWТQФ‘R‘PХQ€Y€™\XШ]WЭYWЪY€[€™X\ЫЫњИ[ЩH‘U’QSђСWХђSQUSУ—СђRSQ‚€њ™XZВ‚€™XЫЬ™ИHЫШYЬ™XЫЬ™К]Л›YЩ\ЉB€XШЩ\YH™XЫЬ™ЦЛLWB€ЩY[—Э\ЧЬќ[‹Y
ЭЉXШЩ\YИќYWЪY—JJB€Y]љXЬИHЫY]љXЬК™XЫЬ™КB€™\Э[HВ€ќYWЫќ[X™\€Ћ€[Љ™XЫЬ™КK€ќYWЪYЋ€XШЩ\YИќYWЪY—K€™[ќћHЋ€XШЩ\YИ™[ќћWЬљXЩH—K€™^]Ћ€XШЩ\YИ™^]ЬљXЩH—K€њ™X[^™YЬ\\—ЬЋ€XШЩ\YИњ™X[^™YЬ—K€Э[][]]™WЬ\\—ЬЋ€Y]љXЬЦИ›™]Ь—K€ќЪ[—ЫЬ—ЫЬЬИЋ€•ТS€€Y€XШЩ\YИњ™X[^™YЬ—H€[ЩH
“ФФИ€Y€XШЩ\YИњ™X[^™YЬ—H[ЩH‘“UЉK€B€Э]Kќ\]JY]љXЬКB€Э]Kќ\]JВ€XШЩ\YЬ]X[YћZ[™ЧЭY\ИЋ€™\^VИњ]X[YћZ[™ЧЭYWШЫЭ[ќ—K€Э\њ™[ќЭYWЫќ[X™\€Ћ€[Љ™XЫЬ™КK€›\ЭЭYHЋ€™\Э[€ќYWЬ™\Э[ИЋ€КњЭ]VИќYWЬ™\Э[И—K™\Э[K€њWЬЭ]\ИЋ€™\^VИњWЬЭ]\ЧШYќ\€—K€њ™XYWЩ›Ь—Ь—Ь™]љY]ИЋ€™\^VИњ™XYWЩ›Ь—Ь—Ь™]љY]И—K€ќ\]YЭ]ИЋ€Э]ЧЫ›ЭК
K€JB€ЭЬљ]WЫЭ]]К]ЛЭ]JB€Ь›ЩЬ™\ЬКЭ]KЭ]]
B€Y€X^[][WЬЩ\ЬЪ[Ы—ЫЬЬИ\И›Э›Ы™H[™Э]VИ›™]Ь—HHXXњКX^[][WЬЩ\ЬЪ[Ы—ЫЬЬКN‚€ЭЬЬ™X\ЫЫ€H“PVSUSWФСTФТSУ—УФФЧТU‚‚€Э]VИШ[\ZYЫ—ЬЭ]\И—HHђУУTUH€Y€ЭЬЬ™X\ЫЫ€OH•T‘СUФ‘PPТQ€[ЩH”ХФQ‚€Э]VИњЭЬЬ™X\ЫЫ€—HHЭЬЬ™X\ЫЫ‚€Э]VИќ\]YЭ]И—HHЭ]ЧЫ›ЭК
B€Э]VИЫЫ\]YЭ]И—HHЭ]VИќ\]YЭ]И—B€Э]VИXЭ]™WЬЬЪ][Ы€—HH›Ы™B€ЭЬљ]WЫЭ]]К]ЛЭ]JB€]ЛШ[™Y]Kќ[›[љКZ\ЬЪ[™ЧЫЪПUќYJB€™]\›€Э]B