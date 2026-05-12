from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from aios.modules.trader.execution_quality import build_execution_quality_metrics
from apps.trading_lab.trading_lab.tv_tp_bridge.aios_paper_validator import (
    validate_aios_paper_signal,
)
from apps.trading_lab.trading_lab.tv_tp_bridge.aios_signal_intake import (
    normalize_tradingview_payload,
)
from apps.trading_lab.trading_lab.tv_tp_bridge.traderspost_handoff_payload import (
    build_traderspost_handoff_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[4]
MOCK_DATA_ROOT = REPO_ROOT / "apps" / "trading_lab" / "mock-data" / "tv_tp_bridge"
TV_ALERT_EXAMPLE = MOCK_DATA_ROOT / "tradingview_alert.example.json"
PAPER_VALIDATION_EXAMPLE = MOCK_DATA_ROOT / "aios_paper_validation_result.example.json"
REPLAY_RESULT_EXAMPLE = MOCK_DATA_ROOT / "paper_route_replay_result.example.json"


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def build_paper_route_replay_result() -> dict[str, Any]:
    """Build a deterministic local paper replay result without external calls."""
    tv_alert = load_json(TV_ALERT_EXAMPLE)
    reference_validation = load_json(PAPER_VALIDATION_EXAMPLE)

    intake = normalize_tradingview_payload(
        tv_alert,
        received_time="2026-05-12T13:00:01Z",
    )
    validation = validate_aios_paper_signal(intake)
    handoff = build_traderspost_handoff_payload(intake, validation)

    expected_fill_price = float(tv_alert.get("price", 0.0))
    actual_fill_price = expected_fill_price
    spread_estimate = 0.0
    slippage_estimate = actual_fill_price - expected_fill_price
    fill_latency_ms = 0
    execution_record = {
        "paper_only": True,
        "expected_fill_price": expected_fill_price,
        "actual_paper_fill_price": actual_fill_price,
        "paper_slippage": slippage_estimate,
        "spread_estimate": spread_estimate,
        "fill_latency_ms": fill_latency_ms,
    }
    execution_quality = build_execution_quality_metrics([execution_record])

    paper_validation_status = validation.get(
        "validation_status",
        reference_validation.get("validation_status", "BLOCKED"),
    )
    blocked_reason = validation.get("blocked_reason") or "Live execution blocked; paper replay only."

    return {
        "replay_id": "PHASE_14_11_PAPER_ROUTE_REPLAY_001",
        "mode": "paper_only",
        "source": tv_alert.get("source", "TradingView"),
        "pair": intake.get("pair", "UNKNOWN"),
        "timeframe": intake.get("timeframe", "UNKNOWN"),
        "direction": intake.get("direction", "UNKNOWN"),
        "paper_validation_status": paper_validation_status,
        "traderspost_handoff_status": handoff.get("webhook_status", "NOT_SENT"),
        "broker_status": "NOT_CONNECTED",
        "live_execution_status": "BLOCKED",
        "expected_fill_price": expected_fill_price,
        "actual_fill_price": actual_fill_price,
        "spread_estimate": spread_estimate,
        "slippage_estimate": slippage_estimate,
        "fill_latency_ms": fill_latency_ms,
        "paper_result_status": "PAPER_REPLAY_READY",
        "execution_quality_score": execution_quality["execution_quality_score"],
        "scorecard_ready": paper_validation_status == "PAPER_ROUTE_READY",
        "blocked_reason": blocked_reason,
    }


def write_example_result(path: Path = REPLAY_RESULT_EXAMPLE) -> dict[str, Any]:
    result = build_paper_route_replay_result()
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


def main() -> None:
    print(json.dumps(write_example_result(), indent=2))


if __name__ == "__main__":
    main()
