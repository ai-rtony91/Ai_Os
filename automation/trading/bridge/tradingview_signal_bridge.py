"""Paper-only TradingView signal mock/intake bridge."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from aios.modules.trader.payloads.alert_payload import build_mock_alert_payload


def read_signal_fixture(fixture_path: Path) -> dict[str, Any]:
    """Read a local TradingView-style paper replay fixture."""
    return dict(__import__("json").loads(fixture_path.read_text(encoding="utf-8")))


def normalize_signal_to_mock_payload(fixture: dict[str, Any]) -> dict[str, Any]:
    """Convert a fixture into a paper-only mock intake payload."""
    symbol = str(fixture.get("symbol", "")).strip()
    timeframe = str(fixture.get("timeframe", "")).strip()
    permission = str(fixture.get("permission", "")).strip().lower()
    signal = str(fixture.get("signal", "")).strip().upper()
    confidence = float(fixture.get("confidence", 0.0))

    base_payload = build_mock_alert_payload(
        symbol=symbol,
        timeframe=timeframe,
        permission=permission,
        signal=signal,
        confidence=confidence,
        metadata={
            "fixture_signal_id": fixture.get("signal_id"),
            "generated_at": fixture.get("generated_at"),
            "source": fixture.get("source", "TradingViewMock"),
            "paper_fixture": True,
        },
    )

    normalized = dict(base_payload)
    normalized.update(
        {
            "source": fixture.get("source", "TradingViewMock"),
            "signal_id": fixture.get("signal_id"),
            "regime": fixture.get("regime", "trend_up"),
            "trend_score": fixture.get("trend_score", 0.0),
            "received_at": fixture.get("received_at", datetime.now(UTC).isoformat()),
            "paper_replay": True,
        },
    )
    return normalized

