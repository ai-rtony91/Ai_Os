from __future__ import annotations

import json
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from automation.forex_engine.forex_extended_evidence_campaign_v1 import (  # noqa: E402
    BLOCKED_LEDGER_INVALID,
    BLOCKED_LEDGER_MISSING,
    BLOCKED_METRICS_INCOMPLETE,
    BLOCKED_NO_MARKET_DEMO_EVIDENCE,
    BLOCKED_SAFETY_VIOLATION,
    BLOCKED_STALE_EVIDENCE,
    COLLECTING_MARKET_DEMO_EVIDENCE,
    EARLY_CONFIDENCE_REACHED,
    PRODUCTION_CANDIDATE_READY_FOR_OWNER_REVIEW,
    STRONG_CONFIDENCE_REACHED,
    SYSTEM_MINIMUM_REACHED,
    evaluate_extended_evidence_campaign,
)


TODAY = date(2026, 7, 23)


def _write(path: Path, rows: list[dict[str, object]]) -> Path:
    path.write_text(
        "\n".join(json.dumps(row, sort_keys=True) for row in rows) + "\n",
        encoding="utf-8",
    )
    return path


def _market_rows(
    *,
    trades: int,
    days: int,
    windows: int,
    wins: int | None = None,
    loss_size: float = -1.0,
    win_size: float = 1.5,
    max_drawdown_pct: float = 5.0,
    latest_age_days: int = 0,
) -> list[dict[str, object]]:
    wins = trades if wins is None else wins
    losses = trades - wins
    values = ([win_size] * wins) + ([loss_size] * losses)
    rows: list[dict[str, object]] = []
    base_date = TODAY - timedelta(days=latest_age_days + days - 1)
    cursor = 0
    for day_index in range(days):
        remaining_days = days - day_index
        remaining_trades = trades - cursor
        count = remaining_trades // remaining_days
        if remaining_trades % remaining_days:
            count += 1
        day_values = values[cursor : cursor + count]
        cursor += len(day_values)
        rows.append(
            {
                "schema": "aios.forex.demo_proof_ledger.v1",
                "record_type": "REAL_DEMO_DAY",
                "date": (base_date + timedelta(days=day_index)).isoformat(),
                "session_mode": "OANDA_PRACTICE",
                "session_source": "oanda_demo_post_trade_evidence",
                "strategy_name": "governed_market_demo_v1",
                "fills": len(day_values),
                "windows_toward_verdict": windows,
                "max_drawdown_pct": max_drawdown_pct,
                "trade_rows": [
                    {"realized_pnl_usd": value, "pair": "EUR_USD"} for value in day_values
                ],
                "live_trading_allowed": False,
                "live_order_execution_allowed": False,
                "live_capital_action_authorized": False,
                "money_movement_allowed": False,
                "bank_access_allowed": False,
            }
        )
    assert cursor == trades
    return rows


def test_missing_ledger_blocks(tmp_path: Path) -> None:
    result = evaluate_extended_evidence_campaign(
        tmp_path / "missing.jsonl", as_of_date=TODAY
    )
    assert result["status"] == BLOCKED_LEDGER_MISSING
    assert result["safety"]["live_trading_allowed"] is False


def test_invalid_ledger_blocks(tmp_path: Path) -> None:
    path = tmp_path / "ledger.jsonl"
    path.write_text("{not-json}\n", encoding="utf-8")
    result = evaluate_extended_evidence_campaign(path, as_of_date=TODAY)
    assert result["status"] == BLOCKED_LEDGER_INVALID


def test_fixture_trades_do_not_count_as_market_demo(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "ledger.jsonl",
        [
            {
                "record_type": "REAL_DEMO_DAY",
                "date": TODAY.isoformat(),
                "session_mode": "PAPER_SIMULATION",
                "session_source": "paper_signal_execution_loop",
                "strategy_name": "paper_fixture_expectancy_probe_v1",
                "fills": 100,
                "trade_rows": [{"realized_paper_pl": 1.0}] * 100,
                "max_drawdown_pct": 0.0,
            }
        ],
    )
    result = evaluate_extended_evidence_campaign(path, as_of_date=TODAY)
    assert result["status"] == BLOCKED_NO_MARKET_DEMO_EVIDENCE
    assert result["summary"]["engineering_trades"] == 100
    assert result["summary"]["market_demo_trades"] == 0
    assert result["summary"]["fixture_or_simulation_trades"] == 100


def test_incomplete_trade_metrics_block(tmp_path: Path) -> None:
    rows = _market_rows(trades=30, days=5, windows=2)
    rows[-1]["trade_rows"] = []
    path = _write(tmp_path / "ledger.jsonl", rows)
    result = evaluate_extended_evidence_campaign(path, as_of_date=TODAY)
    assert result["status"] == BLOCKED_METRICS_INCOMPLETE


def test_stale_market_evidence_blocks(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "ledger.jsonl",
        _market_rows(trades=30, days=5, windows=2, latest_age_days=15),
    )
    result = evaluate_extended_evidence_campaign(path, as_of_date=TODAY)
    assert result["status"] == BLOCKED_STALE_EVIDENCE


def test_safety_violation_blocks(tmp_path: Path) -> None:
    rows = _market_rows(trades=30, days=5, windows=2)
    rows[0]["money_movement_allowed"] = True
    path = _write(tmp_path / "ledger.jsonl", rows)
    result = evaluate_extended_evidence_campaign(path, as_of_date=TODAY)
    assert result["status"] == BLOCKED_SAFETY_VIOLATION


def test_below_first_tier_collects(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "ledger.jsonl",
        _market_rows(trades=29, days=5, windows=2),
    )
    result = evaluate_extended_evidence_campaign(path, as_of_date=TODAY)
    assert result["status"] == COLLECTING_MARKET_DEMO_EVIDENCE
    assert result["achieved_tier"] == "NONE"
    assert result["next_target_tier"] == "SYSTEM_MINIMUM"


@pytest.mark.parametrize(
    ("trades", "days", "windows", "wins", "drawdown", "expected"),
    [
        (30, 5, 2, 20, 9.0, SYSTEM_MINIMUM_REACHED),
        (100, 20, 4, 70, 7.0, EARLY_CONFIDENCE_REACHED),
        (300, 45, 6, 210, 6.5, STRONG_CONFIDENCE_REACHED),
        (500, 60, 8, 360, 5.5, PRODUCTION_CANDIDATE_READY_FOR_OWNER_REVIEW),
    ],
)
def test_tier_thresholds(
    tmp_path: Path,
    trades: int,
    days: int,
    windows: int,
    wins: int,
    drawdown: float,
    expected: str,
) -> None:
    path = _write(
        tmp_path / "ledger.jsonl",
        _market_rows(
            trades=trades,
            days=days,
            windows=windows,
            wins=wins,
            max_drawdown_pct=drawdown,
        ),
    )
    result = evaluate_extended_evidence_campaign(path, as_of_date=TODAY)
    assert result["status"] == expected
    assert result["passed"] is True
    assert result["safety"]["orders_placed"] is False
    assert result["safety"]["automatic_order_execution_allowed"] is False
    assert result["safety"]["live_trading_allowed"] is False


def test_low_profit_factor_prevents_tier(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "ledger.jsonl",
        _market_rows(
            trades=100,
            days=20,
            windows=4,
            wins=45,
            win_size=1.0,
            loss_size=-1.0,
        ),
    )
    result = evaluate_extended_evidence_campaign(path, as_of_date=TODAY)
    assert result["status"] == COLLECTING_MARKET_DEMO_EVIDENCE
    assert any("profit_factor" in blocker for blocker in result["blockers"])


def test_output_contains_no_live_or_profit_approval(tmp_path: Path) -> None:
    path = _write(
        tmp_path / "ledger.jsonl",
        _market_rows(trades=500, days=60, windows=8, wins=360),
    )
    result = evaluate_extended_evidence_campaign(path, as_of_date=TODAY)
    serialized = json.dumps(result, sort_keys=True).lower()
    for phrase in (
        "guaranteed profit",
        "approved for live",
        "safe to trade live",
        "live trading approved",
    ):
        assert phrase not in serialized
