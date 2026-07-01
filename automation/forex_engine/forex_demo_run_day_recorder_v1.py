from __future__ import annotations

import json
import math
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


SCHEMA = "aios.forex.demo_proof_ledger.v1"
RECORD_TYPE_REAL_DEMO_DAY = "REAL_DEMO_DAY"
LEDGER_RELATIVE_PATH = Path("telemetry/forex/demo_proof_ledger.jsonl")

DEFAULT_BASELINE_EQUITY_USD = 1000.0
MINIMUM_TOTAL_TRADES = 30
MINIMUM_WALK_FORWARD_WINDOWS = 2
MINIMUM_EXPECTANCY = 0.5
MINIMUM_PROFIT_FACTOR = 2.0
MAXIMUM_EVIDENCE_AGE_DAYS = 14
DEFAULT_WINDOW_DAYS = 7

LEDGER_SAFE_DIRECTORY = Path("telemetry/forex")

LEDGER_NEVER_LIVE_FLAGS = {
    "bank_access_allowed": False,
    "broker_api_allowed": False,
    "close_trade_allowed": False,
    "credential_access_allowed": False,
    "live_capital_action_authorized": False,
    "live_order_execution_allowed": False,
    "live_trading_allowed": False,
    "money_movement_allowed": False,
    "order_placement_allowed": False,
}

SESSION_TRADE_ROW_FIELDS = (
    "pair",
    "side",
    "units",
    "entry_time",
    "exit_time",
    "duration",
    "entry_price",
    "exit_price",
    "realized_paper_pl",
    "exit_reason",
    "strategy",
    "risk_approved",
    "source_label",
    "freshness_utc",
    "evidence_status",
    "stop_loss_policy",
    "take_profit_policy",
    "trailing_stop_policy",
    "max_time_policy",
    "slippage_if_available",
    "secret_values_recorded",
    "private_identifiers_recorded",
    "raw_broker_payload_recorded",
)


def load_demo_ledger_entries(repo_root: Path) -> list[dict[str, Any]]:
    ledger_path = _safe_ledger_path(repo_root)
    return _read_jsonl_entries(ledger_path)


def summarize_demo_ledger(
    entries: Sequence[Mapping[str, Any]] | None,
    *,
    baseline_equity_usd: float = DEFAULT_BASELINE_EQUITY_USD,
    as_of_utc: str | datetime | date | None = None,
) -> dict[str, Any]:
    ledger_entries = [dict(entry) for entry in (entries or []) if isinstance(entry, Mapping)]
    real_entries = [entry for entry in ledger_entries if _record_type(entry) == RECORD_TYPE_REAL_DEMO_DAY]
    mock_entries = [entry for entry in ledger_entries if _record_type(entry) != RECORD_TYPE_REAL_DEMO_DAY]
    as_of_date = _coerce_date(as_of_utc) if as_of_utc is not None else _utc_date()

    trade_rows = _flatten_trade_rows(real_entries)
    if not trade_rows and real_entries:
        trade_rows = [_synthetic_trade_row(entry) for entry in real_entries]

    trade_count = sum(_entry_trade_count(entry, trade_rows) for entry in real_entries)
    realized_values = [_row_pnl(row) for row in trade_rows]
    total_realized_pnl = round(sum(realized_values), 2)
    wins = sum(1 for value in realized_values if value > 0)
    losses = sum(1 for value in realized_values if value < 0)
    breakeven = sum(1 for value in realized_values if value == 0)
    gross_profit = round(sum(value for value in realized_values if value > 0), 6)
    gross_loss = round(abs(sum(value for value in realized_values if value < 0)), 6)
    expectancy = round(total_realized_pnl / trade_count, 6) if trade_count else 0.0
    if gross_loss > 0:
        profit_factor = round(gross_profit / gross_loss, 6)
    else:
        profit_factor = 999.0 if gross_profit > 0 else 0.0
    win_rate_pct = round((wins / max(1, wins + losses)) * 100.0, 2) if (wins + losses) else 0.0

    cumulative_curve = _cumulative_equity_curve(trade_rows, baseline_equity_usd)
    max_drawdown_pct = _max_drawdown_pct(cumulative_curve, baseline_equity_usd)

    real_dates = sorted(_coerce_date(entry.get("date")) for entry in real_entries if entry.get("date"))
    latest_date = real_dates[-1] if real_dates else None
    oldest_date = real_dates[0] if real_dates else None
    evidence_age_days = (as_of_date - latest_date).days if latest_date is not None else None
    evidence_age_ok = evidence_age_days is not None and evidence_age_days <= MAXIMUM_EVIDENCE_AGE_DAYS
    windows = len({_window_key(item) for item in real_dates}) if real_dates else 0

    days_until_verdict_possible = _days_until_verdict_possible(
        trade_count=trade_count,
        day_count=len(real_entries),
        windows=windows,
        evidence_age_ok=evidence_age_ok,
    )
    verdict_status = _classify_verdict(
        real_demo_day_count=len(real_entries),
        trade_count=trade_count,
        windows=windows,
        evidence_age_ok=evidence_age_ok,
        expectancy=expectancy,
        profit_factor=profit_factor,
        max_drawdown_pct=max_drawdown_pct,
    )

    summary = {
        "schema": "aios.forex.demo_run_summary.v1",
        "ledger_line_count": len(ledger_entries),
        "real_demo_day_count": len(real_entries),
        "mock_entry_count": len(mock_entries),
        "mock_entries_superseded_by_real_run": len(mock_entries),
        "days_recorded_toward_verdict": len(real_entries),
        "trades_accumulated": trade_count,
        "windows": windows,
        "current_expectancy": expectancy,
        "current_profit_factor": profit_factor,
        "win_rate_pct": win_rate_pct,
        "wins": wins,
        "losses": losses,
        "breakeven": breakeven,
        "realized_pnl_usd": total_realized_pnl,
        "gross_profit_usd": gross_profit,
        "gross_loss_usd": gross_loss,
        "max_drawdown_pct": round(max_drawdown_pct, 4),
        "evidence_age_days": evidence_age_days,
        "evidence_age_ok": evidence_age_ok,
        "oldest_real_demo_day": oldest_date.isoformat() if oldest_date is not None else None,
        "latest_real_demo_day": latest_date.isoformat() if latest_date is not None else None,
        "days_until_verdict_possible": days_until_verdict_possible,
        "verdict_status": verdict_status,
        "verdict_blockers": _verdict_blockers(
            real_demo_day_count=len(real_entries),
            trade_count=trade_count,
            windows=windows,
            evidence_age_ok=evidence_age_ok,
            expectancy=expectancy,
            profit_factor=profit_factor,
            max_drawdown_pct=max_drawdown_pct,
        ),
        "thresholds": {
            "minimum_total_trades": MINIMUM_TOTAL_TRADES,
            "minimum_walk_forward_windows": MINIMUM_WALK_FORWARD_WINDOWS,
            "minimum_expectancy": MINIMUM_EXPECTANCY,
            "minimum_profit_factor": MINIMUM_PROFIT_FACTOR,
            "maximum_evidence_age_days": MAXIMUM_EVIDENCE_AGE_DAYS,
            "maximum_drawdown_pct": round(DEFAULT_BASELINE_EQUITY_USD * 0 + 15.0, 2),
        },
        "baseline_equity_usd": baseline_equity_usd,
    }
    return summary


def build_demo_verdict_snapshot(
    repo_root: Path,
    *,
    baseline_equity_usd: float = DEFAULT_BASELINE_EQUITY_USD,
    as_of_utc: str | datetime | date | None = None,
) -> dict[str, Any]:
    entries = load_demo_ledger_entries(repo_root)
    return summarize_demo_ledger(
        entries,
        baseline_equity_usd=baseline_equity_usd,
        as_of_utc=as_of_utc,
    )


def record_forex_demo_run_day(
    repo_root: Path,
    session_result: Mapping[str, Any],
    *,
    apply: bool = False,
    recorded_at_utc: str | datetime | None = None,
    session_date: str | date | None = None,
    baseline_equity_usd: float = DEFAULT_BASELINE_EQUITY_USD,
) -> dict[str, Any]:
    repo_root = repo_root.resolve()
    ledger_path = _safe_ledger_path(repo_root)
    existing_entries = _read_jsonl_entries(ledger_path)
    summary_before = summarize_demo_ledger(
        existing_entries,
        baseline_equity_usd=baseline_equity_usd,
        as_of_utc=recorded_at_utc,
    )

    recorded_at_dt = _coerce_datetime(recorded_at_utc) if recorded_at_utc is not None else _utc_now()
    session_day = _coerce_date(session_date) if session_date is not None else recorded_at_dt.date()
    session_day_text = session_day.isoformat()

    if any(
        _record_type(entry) == RECORD_TYPE_REAL_DEMO_DAY and str(entry.get("date")) == session_day_text
        for entry in existing_entries
    ):
        raise ValueError(f"duplicate_real_demo_day_entry:{session_day_text}")

    new_entry = _build_real_demo_day_entry(
        session_result,
        recorded_at_utc=recorded_at_dt,
        session_date=session_day,
        existing_entries=existing_entries,
        baseline_equity_usd=baseline_equity_usd,
    )
    hypothetical_entries = existing_entries + [new_entry]
    summary_after = summarize_demo_ledger(
        hypothetical_entries,
        baseline_equity_usd=baseline_equity_usd,
        as_of_utc=recorded_at_dt,
    )

    appended = False
    if apply:
        ledger_path.parent.mkdir(parents=True, exist_ok=True)
        with ledger_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(new_entry, sort_keys=True) + "\n")
        appended = True

    receipt = {
        "schema": "aios.forex.demo_run_day_recorder_receipt.v1",
        "mode": "APPLY" if apply else "DRY_RUN",
        "appended": appended,
        "append_requested": True,
        "ledger_path": str(LEDGER_RELATIVE_PATH).replace("\\", "/"),
        "session_date": session_day_text,
        "recorded_at_utc": _utc_datetime_text(recorded_at_dt),
        "session_mode": str(session_result.get("mode") or "PAPER_SIMULATION"),
        "session_source": "paper_signal_execution_loop",
        "session_summary": _session_summary(session_result, baseline_equity_usd=baseline_equity_usd),
        "new_entry": new_entry,
        "summary_before": summary_before,
        "summary_after": summary_after,
        "days_recorded_toward_verdict": summary_after["days_recorded_toward_verdict"],
        "trades_accumulated_toward_verdict": summary_after["trades_accumulated"],
        "windows_toward_verdict": summary_after["windows"],
        "real_demo_day_count_before": summary_before["real_demo_day_count"],
        "real_demo_day_count_after": summary_after["real_demo_day_count"],
        "mock_entries_superseded_by_real_run": summary_after["mock_entries_superseded_by_real_run"],
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "live_capital_action_authorized": False,
        "live_trading_allowed": False,
        "broker_api_allowed": False,
        "close_trade_allowed": False,
        "live_order_execution_allowed": False,
        "order_placement_allowed": False,
        "credential_access_allowed": False,
    }
    return receipt


def _build_real_demo_day_entry(
    session_result: Mapping[str, Any],
    *,
    recorded_at_utc: datetime,
    session_date: date,
    existing_entries: Sequence[Mapping[str, Any]],
    baseline_equity_usd: float,
) -> dict[str, Any]:
    trade_rows = _session_trade_rows(session_result)
    fills = _session_fill_count(session_result, trade_rows)
    wins, losses = _wins_losses(trade_rows, session_result)
    realized_pnl_usd = _session_realized_pnl(session_result, trade_rows)
    win_rate_pct = round((wins / max(1, wins + losses)) * 100.0, 2) if (wins + losses) else 0.0
    expectancy_per_trade = round(realized_pnl_usd / fills, 6) if fills else 0.0
    gross_profit = round(sum(value for value in (_row_pnl(row) for row in trade_rows) if value > 0), 6)
    gross_loss = round(abs(sum(value for value in (_row_pnl(row) for row in trade_rows) if value < 0)), 6)
    if gross_loss > 0:
        profit_factor = round(gross_profit / gross_loss, 6)
    else:
        profit_factor = 999.0 if gross_profit > 0 else 0.0

    hypothetical_entries = [
        *[dict(entry) for entry in existing_entries if isinstance(entry, Mapping)],
        {
            "schema": SCHEMA,
            "record_type": RECORD_TYPE_REAL_DEMO_DAY,
            "date": session_date.isoformat(),
            "recorded_at_utc": _utc_datetime_text(recorded_at_utc),
            "trade_rows": trade_rows,
            "fills": fills,
            "wins": wins,
            "losses": losses,
            "realized_pnl_usd": realized_pnl_usd,
        },
    ]
    summary = summarize_demo_ledger(
        hypothetical_entries,
        baseline_equity_usd=baseline_equity_usd,
        as_of_utc=recorded_at_utc,
    )

    entry = {
        "schema": SCHEMA,
        "record_type": RECORD_TYPE_REAL_DEMO_DAY,
        "date": session_date.isoformat(),
        "recorded_at_utc": _utc_datetime_text(recorded_at_utc),
        "session_mode": str(session_result.get("mode") or "PAPER_SIMULATION"),
        "session_source": "paper_signal_execution_loop",
        "strategy_name": _first_text(session_result, "strategy_name", default=""),
        "selected_pair": _first_text(session_result, "selected_pair", default=""),
        "signal_side": _first_text(session_result, "signal_side", default=""),
        "paper_entry_created": bool(session_result.get("paper_entry_created")),
        "paper_close_reconcile": bool(session_result.get("paper_close_reconcile")),
        "trading_history_row_written": bool(session_result.get("trading_history_row_written")),
        "fills": fills,
        "wins": wins,
        "losses": losses,
        "realized_pnl_usd": realized_pnl_usd,
        "win_rate_pct": win_rate_pct,
        "expectancy_per_trade": expectancy_per_trade,
        "profit_factor": profit_factor,
        "max_drawdown_pct": round(summary["max_drawdown_pct"], 4),
        "cumulative_realized_pnl_usd": summary["realized_pnl_usd"],
        "days_recorded_toward_verdict": summary["days_recorded_toward_verdict"],
        "trades_accumulated_toward_verdict": summary["trades_accumulated"],
        "windows_toward_verdict": summary["windows"],
        "evidence_age_days": summary["evidence_age_days"],
        "evidence_age_ok": summary["evidence_age_ok"],
        "trade_rows": trade_rows,
        **LEDGER_NEVER_LIVE_FLAGS,
    }
    return entry


def _session_summary(
    session_result: Mapping[str, Any],
    *,
    baseline_equity_usd: float,
) -> dict[str, Any]:
    trade_rows = _session_trade_rows(session_result)
    fills = _session_fill_count(session_result, trade_rows)
    wins, losses = _wins_losses(trade_rows, session_result)
    realized_pnl_usd = _session_realized_pnl(session_result, trade_rows)
    gross_profit = round(sum(value for value in (_row_pnl(row) for row in trade_rows) if value > 0), 6)
    gross_loss = round(abs(sum(value for value in (_row_pnl(row) for row in trade_rows) if value < 0)), 6)
    if gross_loss > 0:
        profit_factor = round(gross_profit / gross_loss, 6)
    else:
        profit_factor = 999.0 if gross_profit > 0 else 0.0
    win_rate_pct = round((wins / max(1, wins + losses)) * 100.0, 2) if (wins + losses) else 0.0
    return {
        "fills": fills,
        "wins": wins,
        "losses": losses,
        "realized_pnl_usd": realized_pnl_usd,
        "win_rate_pct": win_rate_pct,
        "expectancy_per_trade": round(realized_pnl_usd / fills, 6) if fills else 0.0,
        "profit_factor": profit_factor,
        "trade_rows_count": len(trade_rows),
        "money_movement_allowed": False,
        "bank_access_allowed": False,
        "live_capital_action_authorized": False,
        "live_trading_allowed": False,
        "broker_api_allowed": False,
        "order_placement_allowed": False,
        "credential_access_allowed": False,
        "baseline_equity_usd": baseline_equity_usd,
    }


def _classify_verdict(
    *,
    real_demo_day_count: int,
    trade_count: int,
    windows: int,
    evidence_age_ok: bool,
    expectancy: float,
    profit_factor: float,
    max_drawdown_pct: float,
) -> str:
    if real_demo_day_count == 0:
        return "EARNING"
    if not evidence_age_ok:
        return "FAILING_THRESHOLDS"
    if max_drawdown_pct > 15.0:
        return "FAILING_THRESHOLDS"
    if expectancy < MINIMUM_EXPECTANCY:
        return "FAILING_THRESHOLDS"
    if profit_factor < MINIMUM_PROFIT_FACTOR:
        return "FAILING_THRESHOLDS"
    if trade_count >= MINIMUM_TOTAL_TRADES and windows >= MINIMUM_WALK_FORWARD_WINDOWS:
        return "VERDICT_READY"
    return "EARNING"


def _verdict_blockers(
    *,
    real_demo_day_count: int,
    trade_count: int,
    windows: int,
    evidence_age_ok: bool,
    expectancy: float,
    profit_factor: float,
    max_drawdown_pct: float,
) -> list[str]:
    blockers: list[str] = []
    if real_demo_day_count == 0:
        blockers.append("no_real_demo_days_recorded")
        return blockers
    if not evidence_age_ok:
        blockers.append("evidence_age_exceeds_14_days")
    if max_drawdown_pct > 15.0:
        blockers.append(f"max_drawdown_pct_above_governor_threshold:{max_drawdown_pct:.4f}")
    if expectancy < MINIMUM_EXPECTANCY:
        blockers.append(f"expectancy_below_minimum:{expectancy:.6f}")
    if profit_factor < MINIMUM_PROFIT_FACTOR:
        blockers.append(f"profit_factor_below_minimum:{profit_factor:.6f}")
    if trade_count < MINIMUM_TOTAL_TRADES:
        blockers.append(
            f"trades_accumulated_below_minimum:{trade_count}<{MINIMUM_TOTAL_TRADES}"
        )
    if windows < MINIMUM_WALK_FORWARD_WINDOWS:
        blockers.append(
            f"walk_forward_windows_below_minimum:{windows}<{MINIMUM_WALK_FORWARD_WINDOWS}"
        )
    return blockers


def _days_until_verdict_possible(
    *,
    trade_count: int,
    day_count: int,
    windows: int,
    evidence_age_ok: bool,
) -> int:
    avg_trades_per_day = trade_count / day_count if day_count > 0 else 1.0
    if avg_trades_per_day <= 0:
        avg_trades_per_day = 1.0
    trades_remaining = max(0, MINIMUM_TOTAL_TRADES - trade_count)
    days_for_trades = math.ceil(trades_remaining / avg_trades_per_day)
    days_for_windows = max(0, MINIMUM_WALK_FORWARD_WINDOWS - windows) * DEFAULT_WINDOW_DAYS
    days_for_freshness = 0 if evidence_age_ok or day_count == 0 else 1
    return max(days_for_trades, days_for_windows, days_for_freshness)


def _cumulative_equity_curve(
    trade_rows: Sequence[Mapping[str, Any]],
    baseline_equity_usd: float,
) -> list[float]:
    equity = baseline_equity_usd
    curve: list[float] = []
    for row in trade_rows:
        equity = round(equity + _row_pnl(row), 6)
        curve.append(equity)
    return curve


def _max_drawdown_pct(curve: Sequence[float], baseline_equity_usd: float) -> float:
    if not curve:
        return 0.0
    peak = baseline_equity_usd
    max_drawdown = 0.0
    for equity in curve:
        if equity > peak:
            peak = equity
        drawdown = peak - equity
        if drawdown > max_drawdown:
            max_drawdown = drawdown
    if baseline_equity_usd <= 0:
        return 0.0
    return round((max_drawdown / baseline_equity_usd) * 100.0, 6)


def _flatten_trade_rows(entries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for entry in entries:
        rows.extend(_entry_trade_rows(entry))
    return rows


def _entry_trade_rows(entry: Mapping[str, Any]) -> list[dict[str, Any]]:
    if isinstance(entry.get("trade_rows"), Sequence) and not isinstance(
        entry.get("trade_rows"),
        (str, bytes, bytearray),
    ):
        rows: list[dict[str, Any]] = []
        for item in entry.get("trade_rows", []):
            if isinstance(item, Mapping):
                rows.append(_sanitize_trade_row(item))
        if rows:
            return rows
    if isinstance(entry.get("history_rows"), Sequence) and not isinstance(
        entry.get("history_rows"),
        (str, bytes, bytearray),
    ):
        rows = []
        for item in entry.get("history_rows", []):
            if isinstance(item, Mapping):
                rows.append(_sanitize_trade_row(item))
        if rows:
            return rows
    return []


def _sanitize_trade_row(row: Mapping[str, Any]) -> dict[str, Any]:
    return {field: row.get(field) for field in SESSION_TRADE_ROW_FIELDS if field in row}


def _synthetic_trade_row(entry: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "realized_paper_pl": _row_pnl(entry),
        "source_label": entry.get("session_source", "REAL_DEMO_DAY"),
    }


def _entry_trade_count(entry: Mapping[str, Any], trade_rows: Sequence[Mapping[str, Any]]) -> int:
    fills = _as_int(entry.get("fills"))
    if fills is not None and fills > 0:
        return fills
    trade_rows = _entry_trade_rows(entry)
    if trade_rows:
        return len(trade_rows)
    return 1 if _record_type(entry) == RECORD_TYPE_REAL_DEMO_DAY else 0


def _session_trade_rows(session_result: Mapping[str, Any]) -> list[dict[str, Any]]:
    candidate_paths = (
        ("trading_history", "history_rows"),
        ("history_rows",),
        ("trade_rows",),
        ("reconciliation", "history_rows"),
    )
    for path in candidate_paths:
        value: Any = session_result
        for key in path:
            if isinstance(value, Mapping):
                value = value.get(key)
            else:
                value = None
                break
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            rows = [_sanitize_trade_row(item) for item in value if isinstance(item, Mapping)]
            if rows:
                return rows
    return []


def _session_fill_count(session_result: Mapping[str, Any], trade_rows: Sequence[Mapping[str, Any]]) -> int:
    count = _as_int(session_result.get("fills"))
    if count is not None and count >= 0:
        return count
    if trade_rows:
        return len(trade_rows)
    return 1 if bool(session_result.get("paper_close_reconcile")) else 0


def _wins_losses(
    trade_rows: Sequence[Mapping[str, Any]],
    session_result: Mapping[str, Any],
) -> tuple[int, int]:
    if trade_rows:
        wins = sum(1 for row in trade_rows if _row_pnl(row) > 0)
        losses = sum(1 for row in trade_rows if _row_pnl(row) < 0)
        return wins, losses
    wins = _as_int(session_result.get("wins"))
    losses = _as_int(session_result.get("losses"))
    if wins is None:
        wins = 1 if _row_pnl(session_result) > 0 else 0
    if losses is None:
        losses = 1 if _row_pnl(session_result) < 0 else 0
    return wins, losses


def _session_realized_pnl(
    session_result: Mapping[str, Any],
    trade_rows: Sequence[Mapping[str, Any]],
) -> float:
    value = _as_float(
        session_result.get("realized_pnl_usd"),
        default=None,
    )
    if value is None:
        value = _as_float(session_result.get("realized_paper_pl"), default=None)
    if value is None and trade_rows:
        value = round(sum(_row_pnl(row) for row in trade_rows), 6)
    if value is None:
        value = 0.0
    return round(value, 2)


def _row_pnl(row: Mapping[str, Any]) -> float:
    for key in (
        "realized_paper_pl",
        "realized_pnl_usd",
        "net_pnl_usd",
        "realized_demo_pnl",
    ):
        value = row.get(key)
        parsed = _as_float(value, default=None)
        if parsed is not None:
            return parsed
    return 0.0


def _record_type(entry: Mapping[str, Any]) -> str:
    return str(entry.get("record_type") or "")


def _first_text(mapping: Mapping[str, Any], *keys: str, default: str = "") -> str:
    for key in keys:
        value = mapping.get(key)
        if value not in (None, ""):
            return str(value)
    return default


def _safe_ledger_path(repo_root: Path) -> Path:
    path = (repo_root / LEDGER_RELATIVE_PATH).resolve()
    safe_root = (repo_root / LEDGER_SAFE_DIRECTORY).resolve()
    if safe_root not in path.parents and path != safe_root:
        raise RuntimeError("ledger_path_outside_telemetry_forex")
    return path


def _read_jsonl_entries(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        parsed = json.loads(line)
        if isinstance(parsed, Mapping):
            entries.append(dict(parsed))
            continue
        raise ValueError(f"ledger_line_{line_number}_must_be_json_object")
    return entries


def _window_key(value: date) -> str:
    iso = value.isocalendar()
    return f"{iso.year:04d}-W{iso.week:02d}"


def _coerce_date(value: str | datetime | date) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    text = str(value).strip()
    if not text:
        raise ValueError("date_value_required")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return date.fromisoformat(text)
    return parsed.date()


def _coerce_datetime(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    text = str(value).strip()
    if not text:
        raise ValueError("datetime_value_required")
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def _utc_date() -> date:
    return _utc_now().date()


def _utc_datetime_text(value: datetime) -> str:
    return value.replace(microsecond=0).astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def _as_int(value: Any) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value) if value.is_integer() else None
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return None


def _as_float(value: Any, default: float | None) -> float | None:
    if value is None or isinstance(value, bool):
        return default
    if isinstance(value, (int, float)):
        return float(value)
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default
